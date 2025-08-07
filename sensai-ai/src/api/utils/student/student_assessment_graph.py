from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph.message import add_messages
from api.models import StudentAssessmentState
from api.utils.student.student_assessment_agent import get_llm, get_system_message, extract_assessment_data, is_assessment_complete
from api.utils.student.student_lesson_agent import generate_student_lesson_plan
from pymongo import MongoClient
from bson import ObjectId
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
import asyncio
from typing import Any, Dict, Optional, Annotated, List, cast
from typing_extensions import TypedDict
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ── Graph state for student assessment conversation ──
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    thread_id: Optional[str]
    content: Optional[Dict[str, Any]]
    assessment_data: Optional[Dict[str, Any]]
    student_profile: Optional[Dict[str, Any]]
    is_complete: bool
    lesson_plan: Optional[Any]
    error: Optional[Dict[str, Any]]

# Global variables for MongoDB and graph management
student_assessment_graph = None
cp_cm = None

def get_mongodb_collection():
    """Get MongoDB collection for student assessments"""
    try:
        MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/?appName=hyperverge-checkpointer")
        MONGODB_DB = os.getenv("MONGODB_DB", "langgraph_hyperverge")
        MONGODB_COLL = os.getenv("MONGODB_STUDENT_COLL", "Hyperverge")
        
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLL]
        return collection, client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None, None

def build_graph(checkpointer: MongoDBSaver):
    """Build the student assessment graph structure"""
    logger.info("Building student assessment graph...")
    llm = get_llm()

    # Fetch content from database
    def fetch_content(state: State):
        logger.info("=== FETCH CONTENT NODE ===")
        thread_id = state.get("thread_id")
        
        if not thread_id:
            logger.error("Thread ID not provided")
            return {
                "error": {"status_code": 400, "detail": "Thread ID not provided"}
            }
        
        # Fetch content from database
        collection, client = get_mongodb_collection()
        content = None
        
        if collection is not None:
            try:
                document = collection.find_one({"thread_id": thread_id})
                
                if document:
                    content = document.get("content")
                    logger.info(f"Content found in database: {content is not None}")
                else:
                    logger.error(f"No content found for thread ID: {thread_id}")
                    return {
                        "error": {"status_code": 404, "detail": f"No content found for thread ID: {thread_id}"}
                    }
            except Exception as e:
                logger.error(f"Error fetching from MongoDB: {e}")
                return {
                    "error": {"status_code": 500, "detail": f"Database error: {str(e)}"}
                }
            finally:
                if client is not None:
                    client.close()
        else:
            logger.error("Database not available")
            return {
                "error": {"status_code": 500, "detail": "Database not available"}
            }
        
        if content is None:
            logger.error("Content is None")
            return {
                "error": {"status_code": 404, "detail": f"No content found for thread ID: {thread_id}"}
            }
        
        logger.info(f"Content fetched successfully: {content.get('subject', 'Unknown')} - {content.get('chapter_name', 'Unknown')}")
        return {"content": content}

    # Bootstrap the conversation
    def bootstrap(state: State):
        logger.info("=== BOOTSTRAP NODE ===")
        content = state.get("content")
        
        if not content:
            logger.error("No content available for bootstrap")
            return {
                "error": {"status_code": 400, "detail": "No content available"}
            }
        
        # Create system message
        system_message = get_system_message(content)
        
        # Create initial messages
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content="Hello! I'm ready to start my assessment. Please begin by asking me some questions to understand my current knowledge and learning needs.")
        ]
        
        logger.info("Bootstrap completed successfully")
        return {"messages": messages}

    # Call the LLM
    def call_model(state: State):
        logger.info("=== CALL MODEL NODE ===")
        messages = state.get("messages", [])
        
        if not messages:
            logger.error("No messages to process")
            return {
                "error": {"status_code": 400, "detail": "No messages to process"}
            }
        
        try:
            response = llm.invoke(messages)
            logger.info(f"LLM response generated: {len(str(response.content))} characters")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return {
                "error": {"status_code": 500, "detail": f"LLM error: {str(e)}"}
            }

    # Process assessment data
    def process_assessment(state: State):
        logger.info("=== PROCESS ASSESSMENT NODE ===")
        messages = state.get("messages", [])
        content = state.get("content")
        
        if not messages:
            logger.error("No messages to process for assessment")
            return {
                "error": {"status_code": 400, "detail": "No messages to process"}
            }
        
        try:
            # Extract assessment data from the conversation
            assessment_data = extract_assessment_data(messages, content)
            
            # Check if assessment is complete
            is_complete = is_assessment_complete(assessment_data)
            
            logger.info(f"Assessment processed: complete={is_complete}")
            return {
                "assessment_data": assessment_data,
                "is_complete": is_complete
            }
        except Exception as e:
            logger.error(f"Error processing assessment: {e}")
            return {
                "error": {"status_code": 500, "detail": f"Assessment processing error: {str(e)}"}
            }

    # Generate lesson plan
    def generate_lesson_plan(state: State):
        logger.info("=== GENERATE LESSON PLAN NODE ===")
        assessment_data = state.get("assessment_data")
        content = state.get("content")
        messages = state.get("messages", [])
        
        if not assessment_data:
            logger.error("No assessment data available for lesson plan generation")
            return {
                "error": {"status_code": 400, "detail": "No assessment data available"}
            }
        
        try:
            # Generate personalized lesson plan
            lesson_plan = generate_student_lesson_plan(assessment_data, content, messages)
            
            logger.info("Lesson plan generated successfully")
            return {"lesson_plan": lesson_plan}
        except Exception as e:
            logger.error(f"Error generating lesson plan: {e}")
            return {
                "error": {"status_code": 500, "detail": f"Lesson plan generation error: {str(e)}"}
            }

    # Handle fetch content errors
    def handle_fetch_content(state: State):
        logger.info("=== HANDLE FETCH CONTENT ERROR ===")
        error = state.get("error")
        logger.error(f"Fetch content error: {error}")
        return {"error": error}

    # Determine if we should continue
    def should_continue(state: State):
        logger.info("=== SHOULD CONTINUE NODE ===")
        
        # Check for errors
        if state.get("error"):
            logger.info("Error detected, ending conversation")
            return "end"
        
        # Check if assessment is complete
        if state.get("is_complete", False):
            logger.info("Assessment complete, generating lesson plan")
            return "generate_lesson_plan"
        
        # Continue the conversation
        logger.info("Continuing assessment conversation")
        return "continue"

    # Build the graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("fetch_content", fetch_content)
    workflow.add_node("bootstrap", bootstrap)
    workflow.add_node("call_model", call_model)
    workflow.add_node("process_assessment", process_assessment)
    workflow.add_node("generate_lesson_plan", generate_lesson_plan)
    workflow.add_node("handle_fetch_content", handle_fetch_content)
    
    # Add edges
    workflow.add_edge(START, "fetch_content")
    workflow.add_conditional_edges(
        "fetch_content",
        should_continue,
        {
            "continue": "bootstrap",
            "end": "handle_fetch_content"
        }
    )
    workflow.add_edge("bootstrap", "call_model")
    workflow.add_edge("call_model", "process_assessment")
    workflow.add_conditional_edges(
        "process_assessment",
        should_continue,
        {
            "continue": "call_model",
            "generate_lesson_plan": "generate_lesson_plan",
            "end": END
        }
    )
    workflow.add_edge("generate_lesson_plan", END)
    workflow.add_edge("handle_fetch_content", END)
    
    # Set entry point
    workflow.set_entry_point("fetch_content")
    
    # Compile with checkpointer
    graph = workflow.compile(checkpointer=checkpointer)
    
    logger.info("Student assessment graph built successfully")
    return graph

def initialize_graph():
    """Initialize the student assessment graph"""
    global student_assessment_graph, cp_cm
    
    try:
        logger.info("Initializing student assessment graph...")
        
        # MongoDB connection settings
        MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/?appName=hyperverge-checkpointer")
        MONGODB_DB = os.getenv("MONGODB_DB", "langgraph_hyperverge")
        MONGODB_COLL = os.getenv("MONGODB_STUDENT_COLL", "Hyperverge")
        
        # Create MongoDB checkpointer
        cp_cm = MongoDBSaver(
            connection_string=MONGODB_URI,
            database=MONGODB_DB,
            collection=MONGODB_COLL
        )
        
        # Build the graph
        student_assessment_graph = build_graph(cp_cm)
        
        logger.info("Student assessment graph initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize student assessment graph: {e}")
        return False

def cleanup_graph():
    """Cleanup the student assessment graph"""
    global student_assessment_graph, cp_cm
    
    try:
        logger.info("Cleaning up student assessment graph...")
        
        if cp_cm is not None:
            # Close MongoDB connection
            if hasattr(cp_cm, 'client'):
                cp_cm.client.close()
        
        student_assessment_graph = None
        cp_cm = None
        
        logger.info("Student assessment graph cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning up student assessment graph: {e}")

async def run_student_assessment_turn(thread_id: str, user_message: str, graph=None):
    """Run a single turn of the student assessment conversation"""
    logger.info(f"=== RUNNING STUDENT ASSESSMENT TURN ===")
    logger.info(f"Thread ID: {thread_id}")
    logger.info(f"User message: {user_message}")
    
    try:
        # Use global graph if none provided
        if graph is None:
            graph = student_assessment_graph
        
        if graph is None:
            logger.error("No graph available")
            return {
                "status": "error",
                "message": "Assessment system not initialized"
            }
        
        # Create configuration for the thread
        config = {"configurable": {"thread_id": thread_id}}
        
        # Add user message to the conversation
        def add_user_message(state):
            logger.info("Adding user message to conversation")
            return {"messages": [HumanMessage(content=user_message)]}
        
        # Run the graph
        try:
            # Use asyncio to run the synchronous graph
            def _run_sync():
                return graph.invoke(
                    {"messages": [HumanMessage(content=user_message)]},
                    config=config
                )
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _run_sync)
            
            logger.info("Assessment turn completed successfully")
            
            # Extract the response
            messages = result.get("messages", [])
            ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
            
            if ai_messages:
                latest_response = ai_messages[-1].content
            else:
                latest_response = "I'm processing your response. Please wait a moment."
            
            return {
                "status": "success",
                "response": latest_response,
                "assessment_complete": result.get("is_complete", False),
                "has_lesson_plan": result.get("lesson_plan") is not None,
                "assessment_data": result.get("assessment_data"),
                "lesson_plan": result.get("lesson_plan")
            }
            
        except Exception as e:
            logger.error(f"Error running assessment turn: {e}")
            return {
                "status": "error",
                "message": f"Error processing assessment: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Error in run_student_assessment_turn: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

# Initialize the graph when module is imported
if __name__ != "__main__":
    initialize_graph()
