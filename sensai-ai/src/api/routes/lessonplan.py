from fastapi import Depends, APIRouter, File, UploadFile
from api.models import (
    LessonPlanRequest, LessonPlanRequestfromTopic, LessonPlanAutoRequest,
    LessonPlanStateWithReview, RagLessonPlanStateWithReview
)
from typing import Optional, Dict, Any

router = APIRouter()


@router.get("/")
async def read_root():
    return {"message": "Welcome to the Lesson Plan API!"}

@router.post("/Lesson_Plan")
async def generate_lesson_plan(
    request: LessonPlanRequest = Depends()
):
    allowed_lang = ["english","hindi"]
    #print("1")
    try:
        # Import the actual content and helper functions
        from api.utils.lessonplan import content
        import api.helper.lessonplan.api_helper as helper
        
        extracted_content = await content.content_from_db(request)
        json_data = helper.get_json_data(request)
        chapter_name_fromdb = helper.get_chapter_name_from_number(json_data, request.Chapter_Number)

        if (extracted_content is not None and 'data' in extracted_content and extracted_content['data'] != []) and (request.Language.lower() in allowed_lang):
            # Create state with review functionality
            state = LessonPlanStateWithReview(
                board=request.Board,
                grade=request.Grade, 
                subject=request.Subject,
                chapter_number=request.Chapter_Number,
                chapter_name=chapter_name_fromdb, 
                number_of_lecture=request.Number_of_Lecture,
                duration_of_lecture=request.Duration_of_Lecture, 
                class_strength=request.Class_Strength, 
                language=request.Language,
                quiz=request.Quiz,
                assignment=request.Assignment, 
                user_prompt="",
                content=str(extracted_content), 
                current_class=0,
                structured_output=request.Structured_Output,
                lesson_plan=None,
                review_results=None,
                needs_revision=False,
                revision_count=0,
                review_completed=False
            )
            #print("AAAA" , state)
            from api.utils.lessonplan.graph import run_graph
            lesson_content = await run_graph(state)

        else:
            lesson_content = "Please Enter Valid Details" 

        # if isinstance(lesson_content, list):
        #     for lesson in lesson_content:
        #         lesson["chapter_name"] = chapter_name_fromdb
        
        # Prepare response with review data
        response_data = {
            "status": "success",
            "message": "Lesson Plan Generated and Reviewed Successfully",
            "data": lesson_content
        }
        
        # Add review information if available
        if hasattr(state, 'review_results') and state.get("review_results"):
            review_results = state.get("review_results")
            if review_results:
                response_data["review_data"] = {
                    "quality_score": review_results.quality_score,
                    "issues_found": [
                        {
                            "type": issue.type,
                            "severity": issue.severity,
                            "description": issue.description,
                            "location": issue.location,
                            "suggestion": issue.suggestion
                        } for issue in review_results.issues_found
                    ],
                    "suggestions": review_results.suggestions,
                    "review_summary": review_results.review_summary,
                    "reading_level_assessment": review_results.reading_level_assessment,
                    "revision_count": state.get("revision_count", 0)
                }
                
        return response_data
    except Exception as e: 
        return f"Error {e}"

@router.post("/Lesson_Plan_from_Topic")
async def generate_lesson_plan_from_topic_rag(
    request: LessonPlanRequestfromTopic = Depends(),
    file: Optional[UploadFile] = File(None)
):
    # print("1")
    
    try:
        if file is None:
            context = "AI has to rely on its own knowledge base to generate lesson plans for given topics"
        else:
            #extracted_content = await content.content_from_pdf(file)
            # print("Extracted Content:",extracted_content)
            # print(type(extracted_content))
            
            # print("2")
            # topic = model.LessonPlanRequestfromTopic["topic"]
            
            # context = await extract_chunks(extracted_text=extracted_content, topic=topic)
            
            # print("/nRelevant context: ", context)

            state = RagLessonPlanStateWithReview(
                board=request.Board,
                grade=request.Grade, 
                subject=request.Subject,
                chapter_number="",
                chapter_name=request.Topic, 
                number_of_lecture=request.Number_of_Lecture,
                duration_of_lecture=request.Duration_of_Lecture, 
                class_strength=request.Class_Strength, 
                language=request.Language,
                quiz=request.Quiz,
                assignment=request.Assignment, 
                user_prompt="",
                content=" ", 
                current_class=0,
                structured_output=request.Structured_Output, 
                topic=request.Topic,
                lesson_plan=None,
                review_results=None,
                needs_revision=False,
                revision_count=0,
                review_completed=False
            )
            topic = state['topic']
            #context = await extract_chunks(extracted_text=extracted_content, topic=topic)
            ###
            from api.utils.lessonplan import content
            import api.helper.lessonplan.api_helper as helper
            
            vectorstor_id = await content.upload_pdf_to_vs(file)
            context = await helper.get_relevant_chunks(topic,vectorstor_id)
        
        # print("/nRelevant context: ", context)
        if context is not None:
            state['content'] = context
        # print("3")
        from api.utils.lessonplan.rag.graph_rag import run_graph_rag
        lesson_content = await run_graph_rag(state)

        # if isinstance(lesson_content, list):
        #     for lesson in lesson_content:
        #         lesson["chapter_name"] = chapter_name_fromdb
        # print("0")
        
        # Prepare response with review data
        response_data = {
            "status": "success",
            "message": "Lesson Plan Generated and Reviewed Successfully",
            "data": lesson_content
        }
        
        # Add review information if available
        if hasattr(state, 'review_results') and state.get("review_results"):
            review_results = state.get("review_results")
            if review_results:
                response_data["review_data"] = {
                    "quality_score": review_results.quality_score,
                    "issues_found": [
                        {
                            "type": issue.type,
                            "severity": issue.severity,
                            "description": issue.description,
                            "location": issue.location,
                            "suggestion": issue.suggestion
                        } for issue in review_results.issues_found
                    ],
                    "suggestions": review_results.suggestions,
                    "review_summary": review_results.review_summary,
                    "reading_level_assessment": review_results.reading_level_assessment,
                    "revision_count": state.get("revision_count", 0)
                }
                
        return response_data
    except Exception as e: 
        return f"Error {e}"

@router.post("/Lesson_Plan_auto")
async def generate_lesson_plan_auto(
    req: LessonPlanAutoRequest = Depends(),
    file:    Optional[UploadFile]  = File(None)
):
    # print("File:", file)
    try:
        if req.Chapter_Number is not None:
            # --- build the exact model expected by the first handler --------------
            lp_req = LessonPlanRequest(
                Board               = req.Board,
                Grade               = req.Grade,
                Subject             = req.Subject,
                Chapter_Number      = req.Chapter_Number,
                Number_of_Lecture   = req.Number_of_Lecture,
                Duration_of_Lecture = req.Duration_of_Lecture,
                Class_Strength      = req.Class_Strength,
                Language            = req.Language,
                Quiz                = req.Quiz,
                Assignment          = req.Assignment,
                Structured_Output   = req.Structured_Output,
            )
            response_dict = await generate_lesson_plan(request=lp_req)  # ← direct call

        elif req.Topic is not None or file is not None:
            # --- build the model for the second handler ---------------------------
            lp_topic_req = LessonPlanRequestfromTopic(
                Board               = req.Board,
                Grade               = req.Grade,
                Subject             = req.Subject,
                Topic               = req.Topic or "",          # empty if only file
                Number_of_Lecture   = req.Number_of_Lecture,
                Duration_of_Lecture = req.Duration_of_Lecture,
                Class_Strength      = req.Class_Strength,
                Language            = req.Language,
                Quiz                = req.Quiz,
                Assignment          = req.Assignment,
                Structured_Output   = req.Structured_Output,
            )
            response_dict = await generate_lesson_plan_from_topic_rag(
                request = lp_topic_req,
                file    = file,
            )

        return response_dict
    except Exception as e: 
        return f"Error {e}"

@router.post("/review_lesson_plan")
async def review_existing_lesson_plan(
    lesson_plan: Dict[str, Any],
    grade: str,
    subject: str,
    language: str = "english"
):
    """
    Review an existing lesson plan for quality, appropriateness, and potential issues.
    
    This endpoint allows you to review lesson plans that were generated elsewhere
    or to re-review previously generated lesson plans.
    """
    try:
        # from app.utils.review_agent import review_lesson_plan
        
        # Review the lesson plan
        # review_result = await review_lesson_plan(
        #     lesson_plan=lesson_plan,
        #     grade=grade,
        #     subject=subject,
        #     language=language
        # )
        
        # Placeholder review result
        review_result = None
        
        # Prepare response
        response_data = {
            "status": "success",
            "message": "Lesson Plan Review Completed",
            "review_data": {
                "quality_score": 0.8,
                "issues_found": [],
                "suggestions": [],
                "review_summary": "Review would be performed here",
                "reading_level_assessment": "Appropriate for grade level",
                "needs_revision": False
            }
        }
        
        return response_data
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Review failed: {str(e)}"
        }

@router.post("/review_lesson_plan_from_topic")
async def review_existing_lesson_plan_from_topic(
    lesson_plan: Dict[str, Any],
    grade: str,
    subject: str,
    topic: str,
    language: str = "english"
):
    """
    Review an existing lesson plan from topic for quality, appropriateness, and potential issues.
    
    This endpoint allows you to review lesson plans that were generated from topics
    or to re-review previously generated lesson plans.
    """
    try:
        # from app.utils.review_agent import review_lesson_plan
        
        # Review the lesson plan
        # review_result = await review_lesson_plan(
        #     lesson_plan=lesson_plan,
        #     grade=grade,
        #     subject=subject,
        #     language=language
        # )
        
        # Placeholder review result
        review_result = None
        
        # Prepare response
        response_data = {
            "status": "success",
            "message": "Lesson Plan Review Completed",
            "topic": topic,
            "review_data": {
                "quality_score": 0.8,
                "issues_found": [],
                "suggestions": [],
                "review_summary": "Review would be performed here",
                "reading_level_assessment": "Appropriate for grade level",
                "needs_revision": False
            }
        }
        
        return response_data
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Review failed: {str(e)}"
        }
