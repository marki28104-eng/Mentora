"""
Analytics API endpoints for user behavior tracking and learning insights.

This module provides REST API endpoints for:
- Collecting user behavior data
- Retrieving analytics insights
- Managing learning patterns and profiles
- Privacy-compliant data operations
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import db_user as user_model
from ...db.crud import analytics_crud
from ...services.analytics_processing_service import AnalyticsProcessingService
from ...utils import auth
from ..schemas.analytics import (
    UserBehaviorDataCreate, UserBehaviorData, 
    LearningPatternCreate, LearningPattern, LearningPatternUpdate,
    UserLearningProfileCreate, UserLearningProfile, UserLearningProfileUpdate,
    EngagementMetricsCreate, EngagementMetrics,
    AnalyticsQuery, AnalyticsSummary,
    EventTypeSchema, LearningStyleSchema, DifficultyLevelSchema
)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

# Initialize analytics processing service
analytics_service = AnalyticsProcessingService()


@router.post("/behavior", 
             response_model=UserBehaviorData,
             summary="Record user behavior data")
async def create_behavior_data(
    behavior_data: UserBehaviorDataCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Record user behavior data for analytics tracking.
    
    This endpoint allows the frontend to submit user interaction data
    for analytics processing while ensuring privacy compliance.
    """
    try:
        # Validate that the user can only submit their own data
        if behavior_data.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot submit behavior data for other users"
            )
        
        # Create behavior data record
        return analytics_crud.create_user_behavior_data(
            db=db,
            user_id=behavior_data.user_id,
            session_id=behavior_data.session_id,
            event_type=behavior_data.event_type,
            page_url=behavior_data.page_url,
            timestamp=behavior_data.timestamp,
            course_id=behavior_data.course_id,
            chapter_id=behavior_data.chapter_id,
            metadata=behavior_data.metadata,
            duration_seconds=behavior_data.duration_seconds
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error recording behavior data: {str(e)}"
        )


@router.get("/behavior",
            response_model=List[UserBehaviorData],
            summary="Get user behavior data")
async def get_behavior_data(
    query: AnalyticsQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve user behavior data with optional filtering.
    
    Users can only access their own data unless they are admin users.
    """
    # Check permissions
    if query.user_id and query.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' behavior data"
        )
    
    # Use current user's ID if not specified or not admin
    user_id = query.user_id if current_user.is_admin else current_user.id
    
    return analytics_crud.get_user_behavior_data(
        db=db,
        user_id=user_id,
        event_type=query.event_type,
        course_id=query.course_id,
        chapter_id=query.chapter_id,
        start_date=query.start_date,
        end_date=query.end_date,
        limit=query.limit,
        offset=query.offset
    )


@router.get("/behavior/{behavior_id}",
            response_model=UserBehaviorData,
            summary="Get specific behavior data record")
async def get_behavior_data_by_id(
    behavior_id: str,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Retrieve a specific behavior data record by ID."""
    behavior_data = analytics_crud.get_user_behavior_data_by_id(db, behavior_id)
    
    if not behavior_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behavior data not found"
        )
    
    # Check permissions
    if behavior_data.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' behavior data"
        )
    
    return behavior_data


@router.get("/learning-patterns",
            response_model=Optional[LearningPattern],
            summary="Get user learning patterns")
async def get_learning_patterns(
    user_id: Optional[str] = Query(None, description="User ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve learning patterns for a user.
    
    Users can only access their own patterns unless they are admin users.
    """
    # Check permissions
    if user_id and user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' learning patterns"
        )
    
    # Use current user's ID if not specified or not admin
    target_user_id = user_id if current_user.is_admin else current_user.id
    
    return analytics_crud.get_learning_pattern_by_user(db, target_user_id)


@router.post("/learning-patterns",
             response_model=LearningPattern,
             summary="Create learning pattern")
async def create_learning_pattern(
    pattern_data: LearningPatternCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Create a new learning pattern record."""
    # Validate that the user can only create their own patterns
    if pattern_data.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create learning patterns for other users"
        )
    
    return analytics_crud.create_learning_pattern(
        db=db,
        user_id=pattern_data.user_id,
        pattern_type=pattern_data.pattern_type,
        confidence_score=pattern_data.confidence_score,
        preferred_content_types=pattern_data.preferred_content_types,
        optimal_session_duration=pattern_data.optimal_session_duration,
        difficulty_progression_rate=pattern_data.difficulty_progression_rate,
        preferred_learning_times=pattern_data.preferred_learning_times,
        average_attention_span=pattern_data.average_attention_span,
        strong_topics=pattern_data.strong_topics,
        challenging_topics=pattern_data.challenging_topics
    )


@router.put("/learning-patterns/{user_id}",
            response_model=LearningPattern,
            summary="Update learning pattern")
async def update_learning_pattern(
    user_id: str,
    pattern_update: LearningPatternUpdate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Update an existing learning pattern."""
    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' learning patterns"
        )
    
    pattern = analytics_crud.get_learning_pattern_by_user(db, user_id)
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning pattern not found"
        )
    
    update_data = pattern_update.model_dump(exclude_unset=True)
    return analytics_crud.update_learning_pattern(db, pattern, update_data)


@router.get("/learning-profile",
            response_model=Optional[UserLearningProfile],
            summary="Get user learning profile")
async def get_learning_profile(
    user_id: Optional[str] = Query(None, description="User ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve learning profile for a user.
    
    Users can only access their own profile unless they are admin users.
    """
    # Check permissions
    if user_id and user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' learning profile"
        )
    
    # Use current user's ID if not specified or not admin
    target_user_id = user_id if current_user.is_admin else current_user.id
    
    return analytics_crud.get_user_learning_profile(db, target_user_id)


@router.post("/learning-profile",
             response_model=UserLearningProfile,
             summary="Create learning profile")
async def create_learning_profile(
    profile_data: UserLearningProfileCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Create a new learning profile."""
    # Validate that the user can only create their own profile
    if profile_data.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create learning profile for other users"
        )
    
    # Check if profile already exists
    existing_profile = analytics_crud.get_user_learning_profile(db, profile_data.user_id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Learning profile already exists for this user"
        )
    
    return analytics_crud.create_user_learning_profile(
        db=db,
        user_id=profile_data.user_id,
        learning_style=profile_data.learning_style,
        attention_span=profile_data.attention_span,
        preferred_difficulty=profile_data.preferred_difficulty,
        completion_rate=profile_data.completion_rate,
        average_session_duration=profile_data.average_session_duration,
        total_learning_time=profile_data.total_learning_time,
        courses_completed=profile_data.courses_completed,
        engagement_score=profile_data.engagement_score,
        consistency_score=profile_data.consistency_score,
        challenge_preference=profile_data.challenge_preference,
        strong_topics=profile_data.strong_topics,
        challenging_topics=profile_data.challenging_topics,
        preferred_content_formats=profile_data.preferred_content_formats,
        current_difficulty_level=profile_data.current_difficulty_level,
        adaptation_rate=profile_data.adaptation_rate
    )


@router.put("/learning-profile/{user_id}",
            response_model=UserLearningProfile,
            summary="Update learning profile")
async def update_learning_profile(
    user_id: str,
    profile_update: UserLearningProfileUpdate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Update an existing learning profile."""
    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' learning profile"
        )
    
    profile = analytics_crud.get_user_learning_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning profile not found"
        )
    
    update_data = profile_update.model_dump(exclude_unset=True)
    return analytics_crud.update_user_learning_profile(db, profile, update_data)


@router.get("/engagement-metrics",
            response_model=List[EngagementMetrics],
            summary="Get engagement metrics")
async def get_engagement_metrics(
    user_id: Optional[str] = Query(None, description="User ID (admin only)"),
    course_id: Optional[int] = Query(None, description="Course ID"),
    chapter_id: Optional[int] = Query(None, description="Chapter ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve engagement metrics with optional filtering.
    
    Users can only access their own metrics unless they are admin users.
    """
    # Check permissions
    if user_id and user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' engagement metrics"
        )
    
    # Use current user's ID if not specified or not admin
    target_user_id = user_id if current_user.is_admin else current_user.id
    
    return analytics_crud.get_engagement_metrics(
        db=db,
        user_id=target_user_id,
        course_id=course_id,
        chapter_id=chapter_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )


@router.post("/engagement-metrics",
             response_model=EngagementMetrics,
             summary="Create engagement metrics")
async def create_engagement_metrics(
    metrics_data: EngagementMetricsCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Create new engagement metrics record."""
    # Validate that the user can only create their own metrics
    if metrics_data.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create engagement metrics for other users"
        )
    
    return analytics_crud.create_engagement_metrics(
        db=db,
        user_id=metrics_data.user_id,
        time_period_start=metrics_data.time_period_start,
        time_period_end=metrics_data.time_period_end,
        course_id=metrics_data.course_id,
        chapter_id=metrics_data.chapter_id,
        total_time_spent=metrics_data.total_time_spent,
        interaction_count=metrics_data.interaction_count,
        page_views=metrics_data.page_views,
        completion_percentage=metrics_data.completion_percentage,
        engagement_score=metrics_data.engagement_score,
        focus_score=metrics_data.focus_score,
        progress_velocity=metrics_data.progress_velocity
    )


@router.get("/summary",
            response_model=AnalyticsSummary,
            summary="Get analytics summary")
async def get_analytics_summary(
    user_id: Optional[str] = Query(None, description="User ID (admin only)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Get a comprehensive analytics summary for a user.
    
    Includes engagement metrics, learning patterns, and activity summary.
    """
    # Check permissions
    if user_id and user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' analytics summary"
        )
    
    # Use current user's ID if not specified or not admin
    target_user_id = user_id if current_user.is_admin else current_user.id
    
    # Get engagement summary
    engagement_summary = analytics_crud.get_user_engagement_summary(db, target_user_id, days)
    
    # Get learning profile
    learning_profile = analytics_crud.get_user_learning_profile(db, target_user_id)
    
    # Get activity timeline
    activity_timeline = analytics_crud.get_user_activity_timeline(db, target_user_id, days)
    
    # Calculate unique courses accessed
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    behavior_data = analytics_crud.get_user_behavior_data(
        db=db,
        user_id=target_user_id,
        start_date=start_date,
        end_date=end_date,
        limit=1000
    )
    
    unique_courses = len(set(
        data.course_id for data in behavior_data 
        if data.course_id is not None
    ))
    
    chapters_completed = len([
        data for data in behavior_data 
        if data.event_type.value == "chapter_complete"
    ])
    
    last_activity = max(
        (data.timestamp for data in behavior_data),
        default=None
    )
    
    return AnalyticsSummary(
        user_id=target_user_id,
        total_events=engagement_summary['total_sessions'],
        total_time_spent=engagement_summary['total_time_spent'],
        unique_sessions=engagement_summary['total_sessions'],
        courses_accessed=unique_courses,
        chapters_completed=chapters_completed,
        average_engagement_score=engagement_summary['average_engagement_score'],
        learning_style=learning_profile.learning_style if learning_profile else None,
        preferred_difficulty=learning_profile.preferred_difficulty if learning_profile else None,
        last_activity=last_activity
    )


@router.post("/process-umami-data",
             summary="Process Umami analytics data",
             dependencies=[Depends(auth.get_current_admin_user)])
async def process_umami_data(
    background_tasks: BackgroundTasks,
    website_id: str = Query(..., description="Umami website ID"),
    db: Session = Depends(get_db)
):
    """
    Process Umami analytics data in the background.
    
    This endpoint is only accessible by admin users and triggers
    the processing of analytics data from Umami.
    """
    async def process_data():
        try:
            await analytics_service.process_umami_data(db, website_id)
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logging.error(f"Error processing Umami data: {str(e)}")
    
    background_tasks.add_task(process_data)
    
    return {"message": "Umami data processing started in background"}


@router.post("/calculate-engagement/{user_id}",
             response_model=EngagementMetrics,
             summary="Calculate engagement metrics")
async def calculate_engagement_metrics(
    user_id: str,
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Calculate and store engagement metrics for a user."""
    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot calculate engagement metrics for other users"
        )
    
    return analytics_service.calculate_engagement_metrics(db, user_id, hours)


@router.post("/identify-patterns/{user_id}",
             response_model=Optional[LearningPattern],
             summary="Identify learning patterns")
async def identify_learning_patterns(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """Identify and store learning patterns for a user."""
    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot identify learning patterns for other users"
        )
    
    return analytics_service.identify_learning_patterns(db, user_id)


@router.delete("/user-data/{user_id}",
               summary="Delete user analytics data",
               response_model=Dict[str, Any])
async def delete_user_analytics_data(
    user_id: str,
    anonymize_only: bool = Query(False, description="Anonymize instead of delete"),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Delete or anonymize all analytics data for a user (GDPR compliance).
    
    Users can delete their own data, admins can delete any user's data.
    """
    # Check permissions
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' analytics data"
        )
    
    if anonymize_only:
        # Anonymize the data instead of deleting
        result = analytics_crud.anonymize_user_analytics_data(db, user_id)
        return {
            "message": "User analytics data anonymized successfully",
            "details": result
        }
    else:
        # Delete all analytics data
        behavior_deleted = analytics_crud.delete_user_behavior_data(db, user_id)
        patterns_deleted = analytics_crud.delete_learning_patterns(db, user_id)
        profile_deleted = analytics_crud.delete_user_learning_profile(db, user_id)
        metrics_deleted = analytics_crud.delete_engagement_metrics(db, user_id)
        
        return {
            "message": "User analytics data deleted successfully",
            "details": {
                "behavior_records_deleted": behavior_deleted,
                "learning_patterns_deleted": patterns_deleted,
                "profile_deleted": profile_deleted,
                "engagement_metrics_deleted": metrics_deleted
            }
        }


@router.get("/course-stats/{course_id}",
            response_model=Dict[str, Any],
            summary="Get course engagement statistics")
async def get_course_engagement_stats(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(auth.get_current_active_user)
):
    """
    Get engagement statistics for a specific course.
    
    Only accessible by course creators and admin users.
    """
    # TODO: Add course ownership check
    # For now, allow all authenticated users to access course stats
    
    return analytics_crud.get_course_engagement_stats(db, course_id)