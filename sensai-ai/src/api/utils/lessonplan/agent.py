from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from api.models import DetailedLessonPlan, QuizAssignment
import logging
from dotenv import load_dotenv
from api.utils.lessonplan.prompt import generate_lesson_plan_points_prompt, generate_lesson_plan_detailed_prompt, generate_lesson_plan_detailed_prompt_2, generate_quiz_assignment_prompt
from pydantic import BaseModel
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_api_key = os.getenv("YOUR_OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4.1", temperature=0.7, api_key=openai_api_key)

llm_json = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.2,
    api_key=openai_api_key,
    model_kwargs={"response_format": {"type": "json_object"}},
)

structured_llm = llm_json.with_structured_output(
    DetailedLessonPlan,
    strict=True
)

structured_llm_quiz_assignment = llm.with_structured_output(QuizAssignment)

from langchain_core.prompts import ChatPromptTemplate

async def generate_lesson_plan_points(state):
    """Generates a lesson plan based on a PDF chapter."""

    system_message = SystemMessage(
        content=(generate_lesson_plan_points_prompt)
    )
    
    messages = [system_message, HumanMessage(state["user_prompt"])]
    response = llm.generate([messages])
    
    lesson_plan = response.generations[0][0].text.strip()

    return lesson_plan

async def generate_lesson_plan_detailed(modified_prompt: str, structured_output: bool):
    """
    Generates a detailed lesson plan.
    Returns a plain dict that matches the old TypedDict shape.
    """
    if structured_output:
        prompt = ChatPromptTemplate.from_messages(
            [("system", generate_lesson_plan_detailed_prompt),
             ("human", "{input}")]
        )
        chain = prompt | structured_llm
        result = chain.invoke({"input": modified_prompt})

        # Convert Pydantic -> dict
        if isinstance(result, BaseModel):
            return result.model_dump(mode="python")
        return result
    else:
        system_msg = SystemMessage(content=generate_lesson_plan_detailed_prompt_2)
        messages = [system_msg, HumanMessage(modified_prompt)]
        resp = llm.generate([messages])
        return resp.generations[0][0].text.strip()

async def generate_quiz_assignment(modified_prompt, structured_output):
    """Generates a quiz_assignment based on a lesson plan."""

    if structured_output == True:
        prompt = ChatPromptTemplate.from_messages([("system", generate_quiz_assignment_prompt), ("human", "{input}")])
        
        response = prompt | structured_llm_quiz_assignment
        
        quiz_assignment = await response.ainvoke({"input": modified_prompt})

        return quiz_assignment
    else:
        system_message = SystemMessage(
            content=(generate_quiz_assignment_prompt)
        )
        
        messages = [system_message, HumanMessage(modified_prompt)]
        response = llm.generate([messages])
        
        lesson_plan = response.generations[0][0].text.strip()

        return lesson_plan
