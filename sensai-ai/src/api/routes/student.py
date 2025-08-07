from fastapi import APIRouter, HTTPException
from api.models import (
    StudentAssessmentRequest, StudentLessonPlanRequest
)
from api.utils.lessonplan import content
import api.helper.lessonplan.api_helper as helper
from api.utils.student.student_assessment_graph import run_student_assessment_turn, student_assessment_graph, get_mongodb_collection
import uuid
from typing import Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Welcome to the Student Lesson Plan API!"}

@router.post("/assessment")
async def start_student_assessment(
    request: StudentAssessmentRequest
):
    """Initialize student assessment session - validate inputs and extract content"""
    logger.info(f"=== STARTING STUDENT ASSESSMENT ===")
    logger.info(f"Request: {request}")
    
    allowed_lang = ["english", "hindi"]
    
    try:
        # Normalize input parameters to handle case sensitivity
        normalized_request = StudentAssessmentRequest(
            Board=request.Board.lower(),
            Grade=request.Grade,
            Subject=request.Subject.lower(),
            Chapter_Number=request.Chapter_Number,
            Number_of_Lecture=request.Number_of_Lecture,
            Duration_of_Lecture=request.Duration_of_Lecture,
            Language=request.Language.lower(),
            Quiz=request.Quiz,
            Assignment=request.Assignment,
            Structured_Output=request.Structured_Output
        )
        
        logger.info(f"Normalized request: {normalized_request}")
        
        # Validate language
        if normalized_request.Language not in allowed_lang:
            logger.error(f"Invalid language: {normalized_request.Language}")
            return {
                "status": "error",
                "message": f"Language '{normalized_request.Language}' is not supported. Supported languages: {', '.join(allowed_lang)}"
            }
        
        # Extract content from database
        logger.info("Extracting content from database...")
        lesson_plan_request = normalized_request.to_lesson_plan_request()
        extracted_content = await content.content_from_db(lesson_plan_request)
        logger.info(f"Extracted content: {extracted_content is not None}")
        
        # Get JSON data and chapter name
        json_data = helper.get_json_data(lesson_plan_request)
        chapter_name_fromdb = helper.get_chapter_name_from_number(json_data, request.Chapter_Number)
        logger.info(f"Chapter name from DB: {chapter_name_fromdb}")
        
        # Generate unique thread ID
        thread_id = str(uuid.uuid4())
        logger.info(f"Generated thread_id: {thread_id}")
        
        # Determine content context
        if (extracted_content and 'data' in extracted_content and extracted_content['data'] != [] and 
            json_data and chapter_name_fromdb and chapter_name_fromdb != f"Chapter number {request.Chapter_Number} not found."):
            # Content exists - use it
            logger.info("Using database content")
            content_obj = {
                "board": normalized_request.Board,
                "grade": normalized_request.Grade,
                "subject": normalized_request.Subject,
                "chapter_number": normalized_request.Chapter_Number,
                "chapter_name": chapter_name_fromdb,
                "number_of_lecture": normalized_request.Number_of_Lecture,
                "duration_of_lecture": normalized_request.Duration_of_Lecture,
                "language": normalized_request.Language,
                "quiz": normalized_request.Quiz,
                "assignment": normalized_request.Assignment,
                "data": extracted_content.get('data', []),
                "summary": extracted_content.get('summary', ''),
                "context_type": "database_content"
            }
        else:
            # No content found - use fallback
            logger.info("Using AI knowledge fallback")
            content_obj = {
                "board": normalized_request.Board,
                "grade": normalized_request.Grade,
                "subject": normalized_request.Subject,
                "chapter_number": normalized_request.Chapter_Number,
                "chapter_name": f"Chapter {request.Chapter_Number}",
                "number_of_lecture": normalized_request.Number_of_Lecture,
                "duration_of_lecture": normalized_request.Duration_of_Lecture,
                "language": normalized_request.Language,
                "quiz": normalized_request.Quiz,
                "assignment": normalized_request.Assignment,
                "data": [],
                "summary": "AI needs to rely on its own knowledge as context",
                "context_type": "ai_knowledge"
            }
        
        # Store the content object in the database for later use
        # This will be retrieved in the continue route
        try:
            logger.info("Storing content in database...")
            logger.info(f"Content to store: {content_obj}")
            
            collection, client = get_mongodb_collection()
            if collection is not None:
                # Store content in database
                document = {
                    "thread_id": thread_id,
                    "content": content_obj,
                    "created_at": datetime.utcnow()
                }
                collection.insert_one(document)
                logger.info("Content stored successfully in database")
            else:
                logger.error("Database collection not available")
        except Exception as e:
            logger.error(f"Failed to store content in database: {e}")
            # If database not ready, we'll handle it in the continue route
            pass
        
        logger.info(f"=== ASSESSMENT INITIALIZED SUCCESSFULLY ===")
        return {
            "status": "success",
            "message": "Assessment session initialized successfully. Use the thread_id to continue with the assessment.",
            "thread_id": thread_id,
            "content_available": content_obj["context_type"] == "database_content"
        }
            
    except Exception as e:
        logger.error(f"Error in start_student_assessment: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@router.post("/assessment/continue")
async def continue_student_assessment(
    request: StudentLessonPlanRequest
):
    """Continue student assessment conversation"""
    logger.info(f"=== CONTINUING STUDENT ASSESSMENT ===")
    logger.info(f"Thread ID: {request.thread_id}")
    logger.info(f"Message: {request.message}")
    
    try:
        if not request.thread_id:
            logger.error("Thread ID is required")
            raise HTTPException(status_code=400, detail="Thread ID is required")
        
        if not request.message:
            logger.error("Message is required")
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info("Calling run_student_assessment_turn...")
        
        # Check if graph is available
        if student_assessment_graph is None:
            logger.error("Student assessment graph is not initialized")
            return {
                "status": "error",
                "message": "Assessment system is not ready. Please try again."
            }
        
        # Continue assessment conversation
        result = await run_student_assessment_turn(
            thread_id=request.thread_id,
            user_message=request.message,
            graph=None  # Will use the global graph
        )
        
        logger.info(f"Assessment turn result: {result}")
        
        return {
            "status": "success",
            "message": "Assessment continued successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in continue_student_assessment: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@router.get("/assessment/{thread_id}/status")
async def get_assessment_status(thread_id: str):
    """Get the current status of a student assessment"""
    logger.info(f"=== GETTING ASSESSMENT STATUS ===")
    logger.info(f"Thread ID: {thread_id}")
    
    try:
        if student_assessment_graph is None:
            logger.error("Assessment graph not initialized")
            raise HTTPException(status_code=500, detail="Assessment graph not initialized")
        
        # Get the current state from the graph
        cfg = {"configurable": {"thread_id": thread_id}}
        
        try:
            state = student_assessment_graph.get_state(cfg).values
            logger.info(f"Current state: {state}")
            
            return {
                "status": "success",
                "thread_id": thread_id,
                "assessment_complete": state.get("is_complete", False),
                "has_lesson_plan": state.get("lesson_plan") is not None,
                "current_state": {
                    "assessment_data": state.get("assessment_data"),
                    "student_profile": state.get("student_profile"),
                    "error": state.get("error")
                }
            }
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return {
                "status": "success",
                "thread_id": thread_id,
                "assessment_complete": False,
                "has_lesson_plan": False,
                "current_state": None
            }
            
    except Exception as e:
        logger.error(f"Error in get_assessment_status: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@router.get("/assessment/{thread_id}/debug")
async def debug_assessment_state(thread_id: str):
    """Debug endpoint to get detailed assessment state information"""
    logger.info(f"=== DEBUG ASSESSMENT STATE ===")
    logger.info(f"Thread ID: {thread_id}")
    
    try:
        if student_assessment_graph is None:
            logger.error("Assessment graph not initialized")
            raise HTTPException(status_code=500, detail="Assessment graph not initialized")
        
        # Get the current state from the graph
        cfg = {"configurable": {"thread_id": thread_id}}
        
        try:
            state = student_assessment_graph.get_state(cfg).values
            logger.info(f"Debug state: {state}")
            
            # Get message details
            messages = state.get("messages", [])
            message_details = []
            for i, msg in enumerate(messages):
                msg_detail = {
                    "index": i,
                    "type": type(msg).__name__,
                    "content_length": len(str(msg.content)) if hasattr(msg, 'content') else 0,
                    "content_preview": str(msg.content)[:100] if hasattr(msg, 'content') else "No content"
                }
                message_details.append(msg_detail)
            
            return {
                "status": "success",
                "thread_id": thread_id,
                "debug_info": {
                    "state_keys": list(state.keys()),
                    "is_complete": state.get("is_complete", False),
                    "has_content": state.get("content") is not None,
                    "has_assessment_data": state.get("assessment_data") is not None,
                    "has_student_profile": state.get("student_profile") is not None,
                    "has_lesson_plan": state.get("lesson_plan") is not None,
                    "has_error": state.get("error") is not None,
                    "message_count": len(messages),
                    "message_details": message_details,
                    "content_info": {
                        "subject": state.get("content", {}).get("subject") if state.get("content") else None,
                        "chapter_name": state.get("content", {}).get("chapter_name") if state.get("content") else None,
                        "context_type": state.get("content", {}).get("context_type") if state.get("content") else None
                    } if state.get("content") else None,
                    "assessment_data": state.get("assessment_data"),
                    "student_profile": state.get("student_profile"),
                    "error": state.get("error")
                }
            }
        except Exception as e:
            logger.error(f"Error getting debug state: {e}", exc_info=True)
            return {
                "status": "error",
                "thread_id": thread_id,
                "error": f"Error getting state: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Error in debug_assessment_state: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }
