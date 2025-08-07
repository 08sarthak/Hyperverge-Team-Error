from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional
import json

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

def get_llm():
    """Get the LLM instance for student lesson plan generation"""
    openai_api_key = os.getenv("YOUR_OPENAI_API_KEY")
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=openai_api_key
    )

def generate_student_lesson_plan(assessment_data: Dict[str, Any], content: Dict[str, Any], messages: List) -> Dict[str, Any]:
    """Generate a personalized lesson plan based on student assessment"""
    
    try:
        llm = get_llm()
        
        # Extract key information
        subject = assessment_data.get("subject", content.get("subject", "Unknown"))
        chapter = assessment_data.get("chapter", content.get("chapter_name", "Unknown"))
        grade = assessment_data.get("grade", content.get("grade", "Unknown"))
        knowledge_level = assessment_data.get("knowledge_level", "unknown")
        learning_style = assessment_data.get("learning_style", "unknown")
        confidence_level = assessment_data.get("confidence_level", "unknown")
        strengths = assessment_data.get("strengths", [])
        weaknesses = assessment_data.get("weaknesses", [])
        learning_preferences = assessment_data.get("learning_preferences", [])
        study_habits = assessment_data.get("study_habits", "unknown")
        motivation_level = assessment_data.get("motivation_level", "unknown")
        preferred_pace = assessment_data.get("preferred_pace", "unknown")
        
        # Build content context
        content_summary = content.get("summary", "")
        content_data = content.get("data", [])
        
        context_info = ""
        if content_data:
            context_info = "\n\nContent Context:\n"
            for i, item in enumerate(content_data[:3], 1):  # Limit to first 3 items
                if isinstance(item, dict):
                    title = item.get("title", f"Section {i}")
                    content_text = item.get("content", "")
                    if content_text:
                        context_info += f"\n{i}. {title}:\n{content_text[:300]}...\n"
        
        # Create the lesson plan generation prompt
        prompt = f"""Based on the student assessment data, generate a personalized lesson plan for {subject} - {chapter} (Grade {grade}).

Student Assessment Summary:
- Knowledge Level: {knowledge_level}
- Learning Style: {learning_style}
- Confidence Level: {confidence_level}
- Key Strengths: {', '.join(strengths) if strengths else 'Not specified'}
- Areas for Improvement: {', '.join(weaknesses) if weaknesses else 'Not specified'}
- Learning Preferences: {', '.join(learning_preferences) if learning_preferences else 'Not specified'}
- Study Habits: {study_habits}
- Motivation Level: {motivation_level}
- Preferred Pace: {preferred_pace}

Content Information:
- Subject: {subject}
- Chapter: {chapter}
- Grade Level: {grade}
{context_info}

Please generate a comprehensive, personalized lesson plan that includes:

1. **Learning Objectives** - Tailored to the student's knowledge level and learning goals
2. **Teaching Strategy** - Adapted to their learning style and preferences
3. **Content Breakdown** - Organized based on their preferred pace and confidence level
4. **Interactive Activities** - Designed for their learning style and engagement level
5. **Assessment Methods** - Appropriate for their confidence and knowledge level
6. **Study Materials** - Recommended based on their learning preferences
7. **Progress Tracking** - Methods to monitor their learning progress
8. **Motivational Elements** - Strategies to maintain their motivation level
9. **Support Resources** - Additional help for areas where they need improvement
10. **Personalized Tips** - Specific advice based on their assessment profile

Guidelines:
- Focus on their strengths while providing support for weaknesses
- Use teaching methods that match their learning style
- Adjust the pace to their comfort level
- Include activities that build their confidence
- Provide clear, step-by-step instructions
- Include both theoretical and practical components
- Make it engaging and interactive
- Include regular checkpoints for progress assessment

Return the lesson plan as a structured JSON object with these sections:
{{
    "lesson_title": "string",
    "learning_objectives": ["list", "of", "objectives"],
    "teaching_strategy": "string",
    "content_breakdown": [
        {{
            "section": "string",
            "duration": "string",
            "activities": ["list", "of", "activities"],
            "materials": ["list", "of", "materials"]
        }}
    ],
    "interactive_activities": ["list", "of", "activities"],
    "assessment_methods": ["list", "of", "methods"],
    "study_materials": ["list", "of", "materials"],
    "progress_tracking": ["list", "of", "methods"],
    "motivational_elements": ["list", "of", "elements"],
    "support_resources": ["list", "of", "resources"],
    "personalized_tips": ["list", "of", "tips"],
    "estimated_duration": "string",
    "difficulty_level": "string",
    "success_criteria": ["list", "of", "criteria"]
}}"""

        # Generate the lesson plan
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the response
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                lesson_plan = json.loads(json_match.group())
                
                # Add metadata
                lesson_plan["metadata"] = {
                    "generated_from_assessment": True,
                    "student_profile": {
                        "knowledge_level": knowledge_level,
                        "learning_style": learning_style,
                        "confidence_level": confidence_level,
                        "strengths": strengths,
                        "weaknesses": weaknesses,
                        "learning_preferences": learning_preferences,
                        "study_habits": study_habits,
                        "motivation_level": motivation_level,
                        "preferred_pace": preferred_pace
                    },
                    "content_info": {
                        "subject": subject,
                        "chapter": chapter,
                        "grade": grade,
                        "content_available": bool(content_data)
                    }
                }
                
                return lesson_plan
            else:
                # Fallback: return a structured response
                return {
                    "lesson_title": f"Personalized Lesson Plan for {subject} - {chapter}",
                    "learning_objectives": ["Understand key concepts", "Apply knowledge practically", "Build confidence in the subject"],
                    "teaching_strategy": "Adaptive approach based on student's learning style and preferences",
                    "content_breakdown": [
                        {
                            "section": "Introduction and Review",
                            "duration": "15-20 minutes",
                            "activities": ["Discussion", "Quick assessment"],
                            "materials": ["Textbook", "Notes"]
                        }
                    ],
                    "interactive_activities": ["Group discussions", "Hands-on exercises", "Visual presentations"],
                    "assessment_methods": ["Formative assessments", "Self-evaluation", "Progress checks"],
                    "study_materials": ["Textbook", "Online resources", "Practice worksheets"],
                    "progress_tracking": ["Regular quizzes", "Learning journals", "Progress meetings"],
                    "motivational_elements": ["Achievement badges", "Progress celebrations", "Positive reinforcement"],
                    "support_resources": ["Tutoring sessions", "Online help", "Study groups"],
                    "personalized_tips": [
                        f"Focus on your strengths in {', '.join(strengths) if strengths else 'the subject'}",
                        f"Use {learning_style} learning methods to enhance understanding",
                        "Take regular breaks to maintain focus and motivation"
                    ],
                    "estimated_duration": "2-3 hours",
                    "difficulty_level": knowledge_level,
                    "success_criteria": ["Complete all activities", "Demonstrate understanding", "Show improvement in weak areas"],
                    "metadata": {
                        "generated_from_assessment": True,
                        "fallback_response": True,
                        "raw_response": response.content
                    }
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse lesson plan JSON, using fallback")
            return {
                "lesson_title": f"Personalized Lesson Plan for {subject} - {chapter}",
                "error": "Failed to parse lesson plan",
                "raw_response": response.content,
                "metadata": {
                    "generated_from_assessment": True,
                    "parse_error": True
                }
            }
            
    except Exception as e:
        logger.error(f"Error generating student lesson plan: {e}")
        return {
            "lesson_title": f"Personalized Lesson Plan for {subject} - {chapter}",
            "error": f"Error generating lesson plan: {str(e)}",
            "metadata": {
                "generated_from_assessment": True,
                "generation_error": True
            }
        }
