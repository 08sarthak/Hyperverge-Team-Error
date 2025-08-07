from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from api.models import DetailedLessonPlan, QuizAssignment
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from api.utils.lessonplan.rag.prompt_rag import generate_lesson_plan_points_rag_prompt, generate_lesson_plan_detailed_rag_prompt, generate_lesson_plan_detailed_rag_prompt_2, generate_quiz_assignment_rag_prompt
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_api_key = os.getenv("YOUR_OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=openai_api_key)

structured_llm = llm.with_structured_output(DetailedLessonPlan)
structured_llm_quiz_assignment = llm.with_structured_output(QuizAssignment)

from langchain_core.prompts import ChatPromptTemplate

async def generate_lesson_plan_points_rag(state):
    """Generates a lesson plan based on a PDF chapter."""

    system_message = SystemMessage(
        content=(generate_lesson_plan_points_rag_prompt)
    )
    
    messages = [system_message, HumanMessage(state["user_prompt"])]
    response = llm.generate([messages])
    
    lesson_plan = response.generations[0][0].text.strip()

    return lesson_plan

async def generate_lesson_plan_detailed_rag(modified_prompt, structured_output):
    """Generates a detailed lesson plan based on a PDF chapter."""

    if structured_output == True:
        prompt = ChatPromptTemplate.from_messages([("system", generate_lesson_plan_detailed_rag_prompt), ("human", "{input}")])
        
        response = prompt | structured_llm
        
        result = await response.ainvoke({"input": modified_prompt})
        if isinstance(result, BaseModel):
            return result.model_dump(mode="python")
        return result  
    else:
        system_message = SystemMessage(
            content=(generate_lesson_plan_detailed_rag_prompt_2)
        )
        
        messages = [system_message, HumanMessage(modified_prompt)]
        response = llm.generate([messages])
        
        lesson_plan = response.generations[0][0].text.strip()

        return lesson_plan

async def generate_quiz_assignment_rag(modified_prompt, structured_output):
    """Generates a quiz_assignment based on a lesson plan."""

    if structured_output == True:
        prompt = ChatPromptTemplate.from_messages([("system", generate_quiz_assignment_rag_prompt), ("human", "{input}")])
        
        response = prompt | structured_llm_quiz_assignment
        
        quiz_assignment = await response.ainvoke({"input": modified_prompt})

        return quiz_assignment
    else:
        system_message = SystemMessage(
            content=(generate_quiz_assignment_rag_prompt)
        )
        
        messages = [system_message, HumanMessage(modified_prompt)]
        response = llm.generate([messages])
        
        lesson_plan = response.generations[0][0].text.strip()

        return lesson_plan
