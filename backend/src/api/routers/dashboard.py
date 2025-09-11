"""
Dashboard API routes for personalized dashboard content.

This module provides endpoints for retrieving personalized dashboard data,
including course recommendations, learning insights, and adaptive suggestions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ...db.database import get_db
from ...db.models.db_user import User
from ...utils.auth import get_current_active_user
from ...services.personalized_dashboard_service import PersonalizedDashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

# Initialize personalized dashboard service
dashboard_service = PersonalizedDashboardService()


@router.get("/personalized")
async def get_personalized_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive personalized dashboard data for the current user.
    
    Returns:
        Dictionary with personalized recommendations, insights, and metrics
    """
    dashboard_data = await dashboard_service.get_dashboard_data(
        db=db,
        user_id=str(current_user.id)
    )
    
    return {
        "user_id": current_user.id,
        "dashboard_data": dashboard_data,
        "generated_at": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }


@router.get("/recommendations/learning-path")
async def get_learning_path_recommendations(
    course_id: Optional[int] = None,
    max_recommendations: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized learning path recommendations.
    
    Args:
        course_id: Optional current course ID for context
        max_recommendations: Maximum number of recommendations to return
        
    Returns:
        List of personalized learning path recommendations
    """
    recommendations = await dashboard_service.get_learning_path_recommendations(
        db=db,
        user_id=str(current_user.id),
        current_course_id=course_id
    )
    
    return {
        "user_id": current_user.id,
        "context_course_id": course_id,
        "recommendations": recommendations[:max_recommendations],
        "total_count": len(recommendations)
    }


@router.post("/suggestions/adaptive-content")
async def get_adaptive_content_suggestions(
    struggling_areas: List[str],
    max_suggestions: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get adaptive content suggestions for areas where the user is struggling.
    
    Args:
        struggling_areas: List of topics/areas where user needs help
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        List of adaptive content suggestions
    """
    if not struggling_areas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one struggling area must be provided"
        )
    
    suggestions = await dashboard_service.get_adaptive_content_suggestions(
        db=db,
        user_id=str(current_user.id),
        struggling_areas=struggling_areas
    )
    
    return {
        "user_id": current_user.id,
        "struggling_areas": struggling_areas,
        "suggestions": suggestions[:max_suggestions],
        "total_count": len(suggestions)
    }


@router.get("/insights/learning-progress")
async def get_learning_progress_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed learning progress insights for the current user.
    
    Returns:
        Dictionary with learning progress analysis and insights
    """
    dashboard_data = await dashboard_service.get_dashboard_data(
        db=db,
        user_id=str(current_user.id)
    )
    
    return {
        "user_id": current_user.id,
        "progress_insights": dashboard_data.get("progress_insights", {}),
        "personalized_metrics": dashboard_data.get("personalized_metrics", {}),
        "learning_suggestions": dashboard_data.get("learning_suggestions", []),
        "has_profile": dashboard_data.get("personalization_available", False)
    }


@router.get("/actions/next-steps")
async def get_next_learning_actions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recommended next learning actions for the current user.
    
    Returns:
        List of recommended actions to take next
    """
    dashboard_data = await dashboard_service.get_dashboard_data(
        db=db,
        user_id=str(current_user.id)
    )
    
    return {
        "user_id": current_user.id,
        "next_actions": dashboard_data.get("next_actions", []),
        "action_count": len(dashboard_data.get("next_actions", []))
    }


@router.get("/profile/learning-style")
async def get_learning_style_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get learning style information and recommendations for the current user.
    
    Returns:
        Learning style profile and personalized recommendations
    """
    dashboard_data = await dashboard_service.get_dashboard_data(
        db=db,
        user_id=str(current_user.id)
    )
    
    user_profile = dashboard_data.get("user_profile")
    progress_insights = dashboard_data.get("progress_insights", {})
    
    if not user_profile:
        return {
            "user_id": current_user.id,
            "has_profile": False,
            "message": "Learning profile not yet available. Complete more learning activities to generate insights."
        }
    
    return {
        "user_id": current_user.id,
        "has_profile": True,
        "learning_style": user_profile.get("learning_style", "unknown"),
        "learning_style_insights": progress_insights.get("learning_style_insights", {}),
        "attention_span": user_profile.get("attention_span"),
        "time_management_insights": progress_insights.get("time_management_insights", {}),
        "challenge_preference": user_profile.get("challenge_preference", 0.5),
        "strong_topics": user_profile.get("strong_topics", []),
        "challenging_topics": user_profile.get("challenging_topics", [])
    }


@router.get("/metrics/personalized")
async def get_personalized_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized learning metrics for dashboard display.
    
    Returns:
        Personalized metrics and goals for the user
    """
    dashboard_data = await dashboard_service.get_dashboard_data(
        db=db,
        user_id=str(current_user.id)
    )
    
    return {
        "user_id": current_user.id,
        "metrics": dashboard_data.get("personalized_metrics", {}),
        "has_personalization": dashboard_data.get("personalization_available", False)
    }