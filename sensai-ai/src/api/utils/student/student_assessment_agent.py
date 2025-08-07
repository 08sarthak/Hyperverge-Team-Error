from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
import logging
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional
import json
import re

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

def get_llm():
    """Get the LLM instance for student assessment"""
    openai_api_key = os.getenv("YOUR_OPENAI_API_KEY")
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=openai_api_key
    )

def get_system_message(content: Dict[str, Any]) -> str:
    """Generate system message for student assessment"""
    
    subject = content.get("subject", "Unknown")
    chapter_name = content.get("chapter_name", "Unknown")
    grade = content.get("grade", "Unknown")
    board = content.get("board", "Unknown")
    language = content.get("language", "english")
    
    # Get content summary if available
    content_summary = content.get("summary", "")
    content_data = content.get("data", [])
    
    # Build context from content data
    context_info = ""
    if content_data:
        context_info = "\n\nContent Context:\n"
        for i, item in enumerate(content_data[:5], 1):  # Limit to first 5 items
            if isinstance(item, dict):
                title = item.get("title", f"Section {i}")
                content_text = item.get("content", "")
                if content_text:
                    context_info += f"\n{i}. {title}:\n{content_text[:500]}...\n"
    
    system_message = f"""You are an expert educational AI assistant conducting a personalized student assessment for {subject} - {chapter_name} (Grade {grade}, {board}).

Your role is to:
1. **Conduct a comprehensive assessment** to understand the student's current knowledge, learning style, strengths, and areas for improvement
2. **Ask targeted questions** to evaluate their understanding of the subject matter
3. **Identify learning gaps** and areas where they need support
4. **Assess their learning preferences** and study habits
5. **Determine their confidence level** with the material

Assessment Guidelines:
- Ask 3-5 focused questions to understand their current knowledge
- Evaluate their learning style (visual, auditory, kinesthetic, etc.)
- Assess their confidence level and motivation
- Identify specific areas where they struggle or excel
- Understand their preferred learning pace and methods
- Ask about their study habits and time management

Content Information:
- Subject: {subject}
- Chapter: {chapter_name}
- Grade Level: {grade}
- Board: {board}
- Language: {language}
{context_info}

Assessment Process:
1. Start with general questions about their familiarity with the topic
2. Ask specific questions about key concepts from the content
3. Evaluate their learning preferences and study habits
4. Assess their confidence and motivation levels
5. Determine their preferred learning pace and methods

Important Notes:
- Be encouraging and supportive throughout the assessment
- Ask one question at a time to avoid overwhelming the student
- Listen carefully to their responses and ask follow-up questions when needed
- Keep track of their responses to build a comprehensive profile
- When you have enough information (after 3-5 exchanges), indicate that the assessment is complete

Response Format:
- Ask clear, specific questions
- Be conversational and encouraging
- Provide brief explanations when needed
- Keep responses concise but informative
- End with a clear next step or question

Remember: Your goal is to create a personalized learning experience by understanding the student's unique needs and preferences."""

    return system_message

def extract_assessment_data(messages: List[BaseMessage], content: Dict[str, Any]) -> Dict[str, Any]:
    """Extract assessment data from the conversation"""
    
    assessment_data = {
        "subject": content.get("subject", "Unknown"),
        "chapter": content.get("chapter_name", "Unknown"),
        "grade": content.get("grade", "Unknown"),
        "board": content.get("board", "Unknown"),
        "language": content.get("language", "english"),
        "knowledge_level": "unknown",
        "learning_style": "unknown",
        "confidence_level": "unknown",
        "strengths": [],
        "weaknesses": [],
        "learning_preferences": [],
        "study_habits": "unknown",
        "motivation_level": "unknown",
        "preferred_pace": "unknown",
        "conversation_summary": "",
        "assessment_questions": [],
        "student_responses": []
    }
    
    # Extract conversation summary
    conversation_text = ""
    for message in messages:
        if hasattr(message, 'content'):
            conversation_text += f"{type(message).__name__}: {message.content}\n"
    
    assessment_data["conversation_summary"] = conversation_text
    
    # Analyze the conversation to extract insights
    try:
        # Use LLM to analyze the conversation
        llm = get_llm()
        
        analysis_prompt = f"""Analyze this student assessment conversation and extract key insights:

Conversation:
{conversation_text}

Content Context:
Subject: {content.get('subject', 'Unknown')}
Chapter: {content.get('chapter_name', 'Unknown')}
Grade: {content.get('grade', 'Unknown')}

Please extract the following information from the conversation:
1. Knowledge Level (beginner, intermediate, advanced, unknown)
2. Learning Style (visual, auditory, kinesthetic, reading/writing, mixed, unknown)
3. Confidence Level (low, medium, high, unknown)
4. Key Strengths (list specific areas where student shows competence)
5. Areas for Improvement (list specific areas where student needs help)
6. Learning Preferences (list preferred learning methods)
7. Study Habits (describe student's study approach)
8. Motivation Level (low, medium, high, unknown)
9. Preferred Learning Pace (slow, moderate, fast, unknown)

Return the analysis as a JSON object with these fields:
{{
    "knowledge_level": "string",
    "learning_style": "string", 
    "confidence_level": "string",
    "strengths": ["list", "of", "strengths"],
    "weaknesses": ["list", "of", "weaknesses"],
    "learning_preferences": ["list", "of", "preferences"],
    "study_habits": "string",
    "motivation_level": "string",
    "preferred_pace": "string"
}}"""

        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse the response
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                # Update assessment data with extracted insights
                assessment_data.update({
                    "knowledge_level": analysis.get("knowledge_level", "unknown"),
                    "learning_style": analysis.get("learning_style", "unknown"),
                    "confidence_level": analysis.get("confidence_level", "unknown"),
                    "strengths": analysis.get("strengths", []),
                    "weaknesses": analysis.get("weaknesses", []),
                    "learning_preferences": analysis.get("learning_preferences", []),
                    "study_habits": analysis.get("study_habits", "unknown"),
                    "motivation_level": analysis.get("motivation_level", "unknown"),
                    "preferred_pace": analysis.get("preferred_pace", "unknown")
                })
        except json.JSONDecodeError:
            logger.warning("Failed to parse assessment analysis JSON")
            
    except Exception as e:
        logger.error(f"Error analyzing assessment conversation: {e}")
    
    return assessment_data

def is_assessment_complete(assessment_data: Dict[str, Any]) -> bool:
    """Determine if the assessment is complete"""
    
    # Check if we have sufficient information
    required_fields = [
        "knowledge_level",
        "learning_style", 
        "confidence_level",
        "strengths",
        "weaknesses"
    ]
    
    # Count how many fields have meaningful data
    meaningful_fields = 0
    for field in required_fields:
        value = assessment_data.get(field, "unknown")
        if value != "unknown" and value:
            if isinstance(value, list) and len(value) > 0:
                meaningful_fields += 1
            elif isinstance(value, str) and value.strip():
                meaningful_fields += 1
    
    # Assessment is complete if we have at least 3 meaningful fields
    # and we have some conversation history
    conversation_summary = assessment_data.get("conversation_summary", "")
    has_conversation = len(conversation_summary.strip()) > 100
    
    return meaningful_fields >= 3 and has_conversation
