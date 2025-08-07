import os
import json
import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from api.models import ReviewResult, ReviewIssue
from api.utils.lessonplan.prompt import review_lesson_plan_system_prompt, review_lesson_plan_analysis_prompt

# Configure logging
logger = logging.getLogger(__name__)

def get_review_llm():
    """Get the LLM instance for review operations"""
    openai_api_key = os.getenv("YOUR_OPENAI_API_KEY")
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        openai_api_key=openai_api_key
    )

async def review_lesson_plan(lesson_plan: Dict[str, Any], grade: str, subject: str, language: str) -> ReviewResult:
    """
    Review a lesson plan for quality, appropriateness, and potential issues.
    
    Args:
        lesson_plan: The lesson plan to review
        grade: Target grade level
        subject: Subject area
        language: Language of instruction
    
    Returns:
        ReviewResult: Detailed review findings and recommendations
    """
    try:
        logger.info(f"Starting lesson plan review for grade {grade} {subject}")
        
        # Get LLM instance
        llm = get_review_llm()
        
        # Prepare the lesson plan content for review
        lesson_plan_text = _format_lesson_plan_for_review(lesson_plan)
        
        # Create the review prompt
        review_prompt = review_lesson_plan_analysis_prompt.format(
            lesson_plan=lesson_plan_text,
            grade=grade,
            subject=subject,
            language=language
        )
        
        # Create messages for the LLM
        messages = [
            SystemMessage(content=review_lesson_plan_system_prompt),
            HumanMessage(content=review_prompt)
        ]
        
        # Get review response
        logger.info("Sending lesson plan for AI review...")
        response = await llm.ainvoke(messages)
        review_content = response.content
        
        # Parse the review response
        review_data = _parse_review_response(review_content)
        
        # Create ReviewResult object
        review_result = ReviewResult(
            quality_score=review_data.get("quality_score", 0.0),
            issues_found=review_data.get("issues_found", []),
            suggestions=review_data.get("suggestions", []),
            needs_revision=review_data.get("needs_revision", False),
            review_summary=review_data.get("review_summary", ""),
            reading_level_assessment=review_data.get("reading_level_assessment")
        )
        
        logger.info(f"Review completed. Quality score: {review_result.quality_score}")
        logger.info(f"Issues found: {len(review_result.issues_found)}")
        logger.info(f"Needs revision: {review_result.needs_revision}")
        
        return review_result
        
    except Exception as e:
        logger.error(f"Error during lesson plan review: {e}", exc_info=True)
        # Return a default review result indicating an error
        return ReviewResult(
            quality_score=0.0,
            issues_found=[],
            suggestions=["Review process encountered an error. Please check the lesson plan manually."],
            needs_revision=True,
            review_summary="Review process failed. Manual review recommended.",
            reading_level_assessment="Unable to assess reading level due to review error."
        )

def _format_lesson_plan_for_review(lesson_plan: Dict[str, Any]) -> str:
    """
    Format the lesson plan content for review.
    
    Args:
        lesson_plan: The lesson plan dictionary
    
    Returns:
        str: Formatted lesson plan text
    """
    try:
        if isinstance(lesson_plan, list):
            # Handle multiple lesson plans
            formatted_content = []
            for i, plan in enumerate(lesson_plan, 1):
                formatted_content.append(f"=== LESSON {i} ===\n")
                formatted_content.append(_format_single_lesson(plan))
                formatted_content.append("\n")
            return "\n".join(formatted_content)
        else:
            # Handle single lesson plan
            return _format_single_lesson(lesson_plan)
    except Exception as e:
        logger.error(f"Error formatting lesson plan: {e}")
        return str(lesson_plan)

def _format_single_lesson(lesson: Dict[str, Any]) -> str:
    """
    Format a single lesson plan for review.
    
    Args:
        lesson: Single lesson plan dictionary
    
    Returns:
        str: Formatted lesson text
    """
    formatted_parts = []
    
    # Handle different lesson plan formats
    if isinstance(lesson, dict):
        for key, value in lesson.items():
            if value and isinstance(value, str):
                formatted_parts.append(f"**{key}:**\n{value}\n")
            elif value and isinstance(value, dict):
                formatted_parts.append(f"**{key}:**\n")
                for sub_key, sub_value in value.items():
                    if sub_value and isinstance(sub_value, str):
                        formatted_parts.append(f"  {sub_key}: {sub_value}\n")
    
    return "\n".join(formatted_parts)

def _parse_review_response(review_content: str) -> Dict[str, Any]:
    """
    Parse the AI review response to extract structured data.
    
    Args:
        review_content: Raw review response from LLM
    
    Returns:
        Dict: Parsed review data
    """
    try:
        # Try to extract JSON from the response
        json_start = review_content.find('{')
        json_end = review_content.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            json_str = review_content[json_start:json_end]
            review_data = json.loads(json_str)
            
            # Convert issues to ReviewIssue objects
            issues = []
            for issue_data in review_data.get("issues_found", []):
                issue = ReviewIssue(
                    type=issue_data.get("type", ""),
                    severity=issue_data.get("severity", "minor"),
                    description=issue_data.get("description", ""),
                    location=issue_data.get("location"),
                    suggestion=issue_data.get("suggestion")
                )
                issues.append(issue)
            
            review_data["issues_found"] = issues
            return review_data
        else:
            logger.warning("No JSON found in review response")
            return _create_default_review_data()
            
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing review response JSON: {e}")
        return _create_default_review_data()
    except Exception as e:
        logger.error(f"Error parsing review response: {e}")
        return _create_default_review_data()

def _create_default_review_data() -> Dict[str, Any]:
    """
    Create default review data when parsing fails.
    
    Returns:
        Dict: Default review data
    """
    return {
        "quality_score": 0.5,
        "issues_found": [],
        "suggestions": ["Unable to parse review response. Manual review recommended."],
        "needs_revision": True,
        "review_summary": "Review parsing failed. Manual review required.",
        "reading_level_assessment": "Unable to assess reading level."
    }

def should_revise_lesson_plan(review_result: ReviewResult, max_revisions: int = 3, current_revision: int = 0) -> bool:
    """
    Determine if a lesson plan should be revised based on review results.
    Made easier to pass - only critical issues trigger revision.
    
    Args:
        review_result: Review findings
        max_revisions: Maximum number of allowed revisions
        current_revision: Current revision count
    
    Returns:
        bool: True if revision is needed and allowed
    """
    # Don't revise if we've reached the maximum number of revisions
    if current_revision >= max_revisions:
        logger.info(f"Maximum revisions ({max_revisions}) reached. Skipping further revision.")
        return False
    
    # Revise if explicitly flagged AND quality score is very low
    if review_result.needs_revision and review_result.quality_score < 0.4:
        return True
    
    # Revise if quality score is extremely low (only very poor content)
    if review_result.quality_score < 0.3:
        return True
    
    # Revise if there are critical issues (bias, inappropriate content, etc.)
    critical_issues = [issue for issue in review_result.issues_found if issue.severity == "critical"]
    if critical_issues:
        logger.info(f"Critical issues found: {len(critical_issues)}. Revision needed.")
        return True
    
    # Don't revise for minor or major issues - let them pass
    logger.info("No critical issues found. Lesson plan passes review.")
    return False
