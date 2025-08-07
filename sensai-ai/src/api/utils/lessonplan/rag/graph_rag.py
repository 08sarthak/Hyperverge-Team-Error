from langgraph.graph import StateGraph, START, END
from api.models import (
    RagLessonPlanStateWithReview, ReviewResult
)
from api.utils.lessonplan.prompt import quiz_assigment_prompt_mod
from api.utils.lessonplan.rag.prompt_rag import generate_lesson_plan_detailed_rag_prompt, generate_lesson_plan_points_rag_prompt, generate_lesson_plan_detailed_rag_prompt_2, generate_quiz_assignment_rag_prompt
from api.utils.lessonplan.rag.agent_rag import generate_lesson_plan_points_rag, generate_lesson_plan_detailed_rag, generate_quiz_assignment_rag
from api.utils.lessonplan.rag.fetchlink import fetch_resources
from api.utils.lessonplan.review_agent import review_lesson_plan, should_revise_lesson_plan
import re



pre_final_generated_content={}
final_generated_content={}
temp_generated_content={}


def graph_struct():
    # print("Building rag lesson plan  graph...")
    builder = StateGraph(RagLessonPlanStateWithReview)

    async def generate_user_prompt(state : RagLessonPlanStateWithReview):
        #file = await helper.return_file(state)
        #print("FILE :",file)
        #content = await helper.extract_pdf_text(file)
        #print("CONTENT :",content)
        user_prompt = f"""Generate lesson plan for :-
                        grade: {state['grade']}
                        subject: {state["subject"]}
                        chapter_number: {state['chapter_number']} 
                        chapter_name: {state['chapter_name']}
                        number_of_lectures: {state['number_of_lecture']}
                        duratione_of_each_lecture: {state['duration_of_lecture']}
                        class strength: {state['class_strength']}
                        content: {state['content']}
                        topic: {state['topic']}
                        """ 
        state["user_prompt"]=user_prompt
        #state["content"]=content
        return state
    

    async def points_lesson_plan_generator(state : RagLessonPlanStateWithReview):
        # print("GENERATING LESSON PLAN IN PONTS")
        lesson_plan =await generate_lesson_plan_points_rag(state)
        # print("LESSON PLAN in POINTS GENERATED")
        temp_generated_content["lesson_plan_points"] = lesson_plan
        blocked_lesson_plan = temp_generated_content["lesson_plan_points"].split("=====")


    async def detailed_lesson_plan_generator(state: RagLessonPlanStateWithReview):
        # print("LESSON PLAN", temp_generated_content["lesson_plan_points"])
        #print("PDF CONTENT:", state["pdf_content"])
        block_no = state["number_of_lecture"]
        content = temp_generated_content["lesson_plan_points"]
        # Split the content by '====='
        sections = content.split("=====")
        # print("A")
        # Trim whitespace from each section and remove empty elements
        sections = [section.strip() for section in sections if section.strip()]
        topics = []
        
        for section in sections:
            matches = re.findall(r"Topic\s*:\s*(.*?)\n", section)
            if matches:
                topics.append([match.strip() for match in matches])

        # print(sections)
        # print("Topics",topics)
        # print("B")
        # if "lesson_plan" not in final_generated_content:
        #     final_generated_content["lesson_plan"] = ""
        # print("C")
        
        # Check if this is a revision and preserve structured output format
        is_revision = state.get("revision_count", 0) > 0
        
        if state["structured_output"] == True:
            final_generated_content["lesson_plan"] = []
        else:
            final_generated_content["lesson_plan"] = ""
            
        for block in range(1, block_no + 1):
            # print(f"Generating content for class {block}/{block_no}...")
            # print("BLOCK",block)
            state["current_class"] = block
            # print("STATE",state)
            modified_prompt = f"""
                                current_class: {block}
                                total_classes: {block_no}
                                class_strength: {state['class_strength']}
                                number_of_lectures: {state['number_of_lecture']}
                                duration_of_each_lecture: {state['duration_of_lecture']}
                                lesson_plan_in_points: {sections[block-1]}
                                content: {state['content']}
                                Generate output in language: {state['language']}
                                """
            # print("Modified PROMPT",modified_prompt)
        
            
            lesson_plan = await generate_lesson_plan_detailed_rag(modified_prompt,state["structured_output"])
            # print("LESSON PLAN TYPE",type(lesson_plan))
            #lesson_plan = json.loads(str(lesson_plan))
            # print("AFTER LESSON PLAN",lesson_plan)
            if topics != []:
                web_resources = await fetch_resources(state,topics[block-1])
            else:
                web_resources = await fetch_resources(state,"")

            # print("LESSON PLAN GENERATED",lesson_plan)

            if state["quiz"] or state["assignment"]:
                quiz_assignment = await quiz_assignment_generator(state,block,block_no,lesson_plan)
            else:
                quiz_assignment = None

            if state["structured_output"] == True:
                # For structured output, add web resources and quiz/assignment as separate fields
                if isinstance(lesson_plan, dict):
                    if web_resources:
                        lesson_plan["Web_Resources"] = [web_resources]
                    if quiz_assignment:
                        lesson_plan["Quiz_/_Assignment"] = [quiz_assignment]
                    if isinstance(final_generated_content["lesson_plan"], list):
                        final_generated_content["lesson_plan"].append(lesson_plan)
                else:
                    # Fallback if lesson_plan is not a dict
                    if isinstance(final_generated_content["lesson_plan"], list):
                        final_generated_content["lesson_plan"].append(lesson_plan)
            else:
                # For non-structured output, concatenate as strings
                if quiz_assignment:
                    lesson_plan = f"{lesson_plan}\n\n{quiz_assignment}"
                if web_resources:
                    lesson_plan = f"{lesson_plan}\n\n{web_resources}"
                
                if final_generated_content["lesson_plan"] == "":
                    final_generated_content["lesson_plan"] = lesson_plan
                else:
                    final_generated_content["lesson_plan"] = f"{final_generated_content['lesson_plan']}\n\n{lesson_plan}"

        # Store the generated lesson plan in state for review
        # Preserve the original format for review while keeping structured output intact
        if isinstance(final_generated_content["lesson_plan"], str):
            state["lesson_plan"] = {"content": final_generated_content["lesson_plan"]}
        else:
            # For structured output (list), convert to string for review but keep original in final_generated_content
            state["lesson_plan"] = {"content": str(final_generated_content["lesson_plan"])}
        state["revision_count"] = state.get("revision_count", 0)
        state["review_completed"] = False  # Initialize review status
        
        return state

    async def review_lesson_plan_node(state: RagLessonPlanStateWithReview):
        """Review the generated lesson plan for quality and appropriateness"""
        try:
            # Check if review has already been done for this lesson plan
            if state.get("review_completed", False):
                print("=== REVIEW ALREADY COMPLETED - SKIPPING ===")
                return state
            
            print("=== REVIEWING LESSON PLAN ===")
            
            # Ensure lesson_plan is not None before reviewing
            lesson_plan = state.get("lesson_plan")
            if lesson_plan is None:
                print("No lesson plan to review - skipping review")
                state["review_completed"] = True
                return state
            
            # Review the lesson plan
            review_result = await review_lesson_plan(
                lesson_plan=lesson_plan,
                grade=state["grade"],
                subject=state["subject"],
                language=state["language"]
            )
            
            # Store review results in state
            state["review_results"] = review_result
            state["needs_revision"] = review_result.needs_revision
            state["review_completed"] = True  # Mark review as completed
            
            print(f"Review completed. Quality score: {review_result.quality_score}")
            print(f"Issues found: {len(review_result.issues_found)}")
            print(f"Needs revision: {review_result.needs_revision}")
            
            return state
            
        except Exception as e:
            print(f"Error in review node: {e}")
            # Create a default review result
            state["review_results"] = ReviewResult(
                quality_score=0.5,
                issues_found=[],
                suggestions=["Review process encountered an error"],
                needs_revision=False,
                review_summary="Review failed, but lesson plan generated successfully",
                reading_level_assessment="Unable to assess"
            )
            state["needs_revision"] = False
            state["review_completed"] = True  # Mark review as completed even on error
            return state

    async def quiz_assignment_generator(state: RagLessonPlanStateWithReview,block,block_no,lesson_plan):

        quiz_assign_modified_prompt = quiz_assigment_prompt_mod(state)

        if quiz_assign_modified_prompt == None:
            return None
        
        else:
            modified_prompt_quiz_assignment = f"""
                        current_class: {block}
                        total_classes: {block_no}
                        class_strength: {state['class_strength']}
                        number_of_lectures: {state['number_of_lecture']}
                        duration_of_each_lecture: {state['duration_of_lecture']}
                        Generate output in language: {state['language']}
                        {quiz_assign_modified_prompt}
                        lesson_plan: {lesson_plan}
                        """

            content = await generate_quiz_assignment_rag(modified_prompt_quiz_assignment,state["structured_output"])
            return content

    def should_revise_decision(state: RagLessonPlanStateWithReview):
        """Determine if the lesson plan needs revision based on review results"""
        # If review has already been completed, always approve (no more revisions)
        if state.get("review_completed", False):
            print("Review already completed - approving final output")
            return "approve"
        
        review_results = state.get("review_results")
        if not review_results:
            return "approve"  # No review results, approve by default
        
        # Check if we should revise
        should_revise = should_revise_lesson_plan(
            review_result=review_results,
            max_revisions=1,  # Only allow one revision
            current_revision=state.get("revision_count", 0)
        )
        
        if should_revise:
            # Increment revision count
            state["revision_count"] = state.get("revision_count", 0) + 1
            print(f"Revision needed. Revision count: {state['revision_count']}")
            return "revise"
        else:
            print("No revision needed - approving")
            return "approve"

    builder.add_node("prompt", generate_user_prompt)
    builder.add_node("points", points_lesson_plan_generator)
    builder.add_node("detailed_lesson_plan", detailed_lesson_plan_generator)
    builder.add_node("review_lesson_plan", review_lesson_plan_node)

    builder.add_edge(START, "prompt")
    builder.add_edge("prompt", "points")
    builder.add_edge("points", "detailed_lesson_plan")
    builder.add_edge("detailed_lesson_plan", "review_lesson_plan")
    
    # Add conditional edge based on review results
    builder.add_conditional_edges(
        "review_lesson_plan",
        should_revise_decision,
        {
            "revise": "detailed_lesson_plan",  # Loop back for revision
            "approve": END  # Final output
        }
    )

    lesson_plan_graph = builder.compile()
    return lesson_plan_graph

lesson_plan_graph = graph_struct()



async def run_graph_rag(state:RagLessonPlanStateWithReview):
    #result=[]
    global final_generated_content,pre_final_generated_content,temp_generated_content

    pre_final_generated_content.clear()
    final_generated_content.clear()
    temp_generated_content.clear()

    try:
        #state = models.LessonPlanState(grade=request.grade, subject=request.subject,chapter_number=request.chapter_number,chapter_name=request.chapter_name, number_of_lecture=request.number_of_lecture,duration_of_lecture=request.duration_of_lecture, class_strength=request.class_strength, language=request.language, user_prompt="",content="", current_class=0)
        #print("B")
        output = await lesson_plan_graph.ainvoke(state)
        #print("E")
        #result.append(final_generated_content["lesson_plan"])

        return final_generated_content["lesson_plan"]
    except Exception as e:
        return {"error": str(e)}
