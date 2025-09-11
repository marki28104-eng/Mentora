
from ..db.crud import courses_crud
from ..db.models import db_course as course_model
from ..api.schemas.course import CourseInfo
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..db.models.db_course import Course

from fastapi import HTTPException, status
from ..db.models.db_course import Chapter

from ..db.crud import usage_crud, chapters_crud
from .personalization_engine import PersonalizationEngine, AdaptedContent
from .learning_adaptation_service import LearningAdaptationService
from ..db.crud import analytics_crud
import logging

logger = logging.getLogger(__name__)



def get_user_courses(db: Session, user_id: str, skip: int = 0, limit: int = 200) -> List[CourseInfo]:
    """
    Get a list of courses for a specific user.
    This function retrieves courses that belong to the user identified by user_id,
    with pagination support using skip and limit parameters.
    """
    return courses_crud.get_courses_infos(db, user_id, skip, limit)

def get_public_courses(db: Session, skip: int = 0, limit: int = 100) -> List[CourseInfo]:
    """
    Get all public courses.
    """
    # The CRUD function `get_public_courses_infos` expects a user_id, but it's not used.
    # We can pass an empty string or any placeholder. This could be refactored later.
    return courses_crud.get_public_courses_infos(db, user_id="", skip=skip, limit=limit)

def get_completed_chapters_count(db: Session, course_id: int) -> int:
    """
    Get the count of completed chapters for a specific course.
    This function retrieves the number of chapters that have been marked as completed
    for the given course ID.
    """
    return chapters_crud.get_completed_chapters_count(db, course_id)


def get_course_by_id(db: Session, course_id: int, user_id: str) -> Optional[Course]:
    """
    Get a course by its ID for a specific user.
    Returns None if the course does not exist or does not belong to the user.
    """
    return courses_crud.get_courses_by_course_id_user_id(db, course_id, user_id)


async def verify_course_ownership(course_id: int, user_id: str, db: Session) -> Course:
    """
    Verify that a course belongs to the current user.
    Returns the course if valid, raises HTTPException if not found or unauthorized.
    """
    course = get_course_by_id(db, course_id, user_id)
    
    if not course:
        course = courses_crud.get_course_by_id(db, course_id)
        if course and course.is_public:
            return course

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    return course

def get_chapter_by_id(course_id: int, chapter_id: int, db: Session) -> Chapter:
    """
    Get a chapter by its ID within a specific course.
    Raises HTTPException if the chapter does not exist in the course.
    """

    # Get the chapter by course_id and chapter_id
    chapter = chapters_crud.get_chapter_by_course_id_and_chapter_id(db, course_id, chapter_id)
    # Log the chapter retrieval
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found in this course"
        )

    return chapter


async def get_personalized_chapter_content(
    db: Session, 
    user_id: str, 
    course_id: int, 
    chapter_id: int
) -> Dict[str, Any]:
    """
    Get chapter content adapted for the user's learning profile.
    
    Args:
        db: Database session
        user_id: User ID for personalization
        course_id: Course ID
        chapter_id: Chapter ID
        
    Returns:
        Dictionary with adapted chapter content and metadata
    """
    try:
        # Get the base chapter
        chapter = get_chapter_by_id(course_id, chapter_id, db)
        
        # Initialize personalization engine
        personalization_engine = PersonalizationEngine()
        
        # Get or generate user profile
        user_profile = await personalization_engine.generate_user_profile(db, user_id)
        
        if not user_profile:
            logger.info(f"No user profile available for {user_id}, returning default content")
            return {
                "chapter": chapter,
                "adaptations": {},
                "personalized": False,
                "pacing_adjustment": 1.0,
                "content_modifications": {}
            }
        
        # Adapt content based on user profile
        content_metadata = {
            "difficulty": 0.5,  # Default difficulty, could be stored in chapter metadata
            "content_type": "text",
            "topic": chapter.caption
        }
        
        adapted_content = await personalization_engine.adapt_content_difficulty(
            db=db,
            content_id=f"chapter_{chapter_id}",
            user_profile=user_profile,
            content_metadata=content_metadata
        )
        
        # Get pacing adjustment from learning adaptation service
        learning_adaptation = LearningAdaptationService()
        pacing_adjustment = await learning_adaptation.adjust_pacing(db, user_id, course_id)
        
        # Prepare personalized response
        personalized_content = {
            "chapter": chapter,
            "adaptations": {
                "difficulty_adjustment": {
                    "original": adapted_content.original_difficulty,
                    "adapted": adapted_content.adapted_difficulty,
                    "explanation_style": adapted_content.explanation_style
                },
                "pacing": {
                    "adjustment_factor": adapted_content.pacing_adjustment,
                    "recommended_time": int(chapter.time_minutes * adapted_content.pacing_adjustment),
                    "pacing_reason": pacing_adjustment.reason if pacing_adjustment else "Standard pacing"
                }
            },
            "personalized": True,
            "content_modifications": adapted_content.content_modifications,
            "learning_style": user_profile.learning_style.value if user_profile.learning_style else "unknown"
        }
        
        return personalized_content
        
    except Exception as e:
        logger.error(f"Error getting personalized chapter content: {str(e)}")
        # Fallback to regular chapter content
        chapter = get_chapter_by_id(course_id, chapter_id, db)
        return {
            "chapter": chapter,
            "adaptations": {},
            "personalized": False,
            "pacing_adjustment": 1.0,
            "content_modifications": {}
        }


async def get_personalized_course_recommendations(
    db: Session, 
    user_id: str, 
    topic: Optional[str] = None,
    max_recommendations: int = 5
) -> List[Dict[str, Any]]:
    """
    Get personalized course recommendations for a user.
    
    Args:
        db: Database session
        user_id: User ID for personalization
        topic: Optional topic to focus recommendations on
        max_recommendations: Maximum number of recommendations
        
    Returns:
        List of personalized course recommendations
    """
    try:
        personalization_engine = PersonalizationEngine()
        
        # If no topic specified, try to infer from user's recent activity
        if not topic:
            # Get user's recent courses to infer interests
            recent_courses = courses_crud.get_courses_infos(db, user_id, skip=0, limit=5)
            if recent_courses:
                # Use the most recent course title as topic
                topic = recent_courses[0].title or "general"
            else:
                topic = "general"
        
        # Get recommendations from personalization engine
        recommendations = await personalization_engine.recommend_learning_path(
            db=db,
            user_id=user_id,
            topic=topic,
            max_recommendations=max_recommendations
        )
        
        # Convert to response format
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append({
                "course_id": rec.course_id,
                "title": rec.title,
                "recommendation_score": rec.recommendation_score,
                "reason": rec.reason,
                "recommended_difficulty": rec.recommended_difficulty.value,
                "estimated_completion_time": rec.estimated_completion_time,
                "topic_match_score": rec.topic_match_score,
                "learning_style_match": rec.learning_style_match
            })
        
        return formatted_recommendations
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {str(e)}")
        return []


async def get_adaptive_course_pacing(
    db: Session, 
    user_id: str, 
    course_id: int
) -> Dict[str, Any]:
    """
    Get adaptive pacing recommendations for a course.
    
    Args:
        db: Database session
        user_id: User ID
        course_id: Course ID
        
    Returns:
        Dictionary with pacing recommendations
    """
    try:
        learning_adaptation = LearningAdaptationService()
        
        pacing_adjustment = await learning_adaptation.adjust_pacing(db, user_id, course_id)
        
        if not pacing_adjustment:
            return {
                "has_adjustment": False,
                "current_pace": 1.0,
                "recommended_pace": 1.0,
                "adjustment_factor": 1.0,
                "reason": "Insufficient data for pacing adjustment"
            }
        
        return {
            "has_adjustment": True,
            "current_pace": pacing_adjustment.current_pace,
            "recommended_pace": pacing_adjustment.recommended_pace,
            "adjustment_factor": pacing_adjustment.adjustment_factor,
            "reason": pacing_adjustment.reason,
            "confidence": pacing_adjustment.confidence,
            "next_review_date": pacing_adjustment.next_review_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting adaptive pacing: {str(e)}")
        return {
            "has_adjustment": False,
            "current_pace": 1.0,
            "recommended_pace": 1.0,
            "adjustment_factor": 1.0,
            "reason": "Error calculating pacing adjustment"
        }

