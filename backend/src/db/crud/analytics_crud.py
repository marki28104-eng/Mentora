"""CRUD operations for analytics data management."""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.sql import text

from ..models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, 
    EngagementMetrics, EventType, LearningStyleType, DifficultyLevel
)
from ...utils.analytics_utils import generate_analytics_id


# UserBehaviorData CRUD operations
def create_user_behavior_data(
    db: Session,
    user_id: str,
    session_id: str,
    event_type: EventType,
    page_url: str,
    timestamp: datetime,
    course_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    engagement_score: Optional[float] = None,
    duration_seconds: Optional[int] = None,
    is_anonymized: bool = False
) -> UserBehaviorData:
    """Create a new user behavior data record."""
    behavior_data = UserBehaviorData(
        id=generate_analytics_id(),
        user_id=user_id,
        session_id=session_id,
        event_type=event_type,
        page_url=page_url,
        course_id=course_id,
        chapter_id=chapter_id,
        timestamp=timestamp,
        metadata=metadata,
        engagement_score=engagement_score,
        duration_seconds=duration_seconds,
        is_anonymized=is_anonymized
    )
    db.add(behavior_data)
    db.commit()
    db.refresh(behavior_data)
    return behavior_data


def get_user_behavior_data(
    db: Session,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    course_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[UserBehaviorData]:
    """Retrieve user behavior data with optional filters."""
    query = db.query(UserBehaviorData)
    
    if user_id:
        query = query.filter(UserBehaviorData.user_id == user_id)
    if session_id:
        query = query.filter(UserBehaviorData.session_id == session_id)
    if event_type:
        query = query.filter(UserBehaviorData.event_type == event_type)
    if course_id:
        query = query.filter(UserBehaviorData.course_id == course_id)
    if chapter_id:
        query = query.filter(UserBehaviorData.chapter_id == chapter_id)
    if start_date:
        query = query.filter(UserBehaviorData.timestamp >= start_date)
    if end_date:
        query = query.filter(UserBehaviorData.timestamp <= end_date)
    
    return query.order_by(desc(UserBehaviorData.timestamp)).offset(offset).limit(limit).all()


def get_user_behavior_data_by_id(db: Session, behavior_id: str) -> Optional[UserBehaviorData]:
    """Retrieve user behavior data by ID."""
    return db.query(UserBehaviorData).filter(UserBehaviorData.id == behavior_id).first()


def delete_user_behavior_data(db: Session, user_id: str) -> int:
    """Delete all behavior data for a user (for GDPR compliance)."""
    deleted_count = db.query(UserBehaviorData).filter(UserBehaviorData.user_id == user_id).delete()
    db.commit()
    return deleted_count


def get_user_session_data(db: Session, user_id: str, session_id: str) -> List[UserBehaviorData]:
    """Get all behavior data for a specific user session."""
    return db.query(UserBehaviorData).filter(
        and_(
            UserBehaviorData.user_id == user_id,
            UserBehaviorData.session_id == session_id
        )
    ).order_by(asc(UserBehaviorData.timestamp)).all()


# LearningPattern CRUD operations
def create_learning_pattern(
    db: Session,
    user_id: str,
    pattern_type: LearningStyleType,
    confidence_score: float,
    preferred_content_types: Optional[List[str]] = None,
    optimal_session_duration: Optional[int] = None,
    difficulty_progression_rate: Optional[float] = None,
    preferred_learning_times: Optional[List[int]] = None,
    average_attention_span: Optional[int] = None,
    strong_topics: Optional[List[str]] = None,
    challenging_topics: Optional[List[str]] = None,
    data_points_count: int = 0
) -> LearningPattern:
    """Create a new learning pattern record."""
    pattern = LearningPattern(
        id=generate_analytics_id(),
        user_id=user_id,
        pattern_type=pattern_type,
        confidence_score=confidence_score,
        preferred_content_types=preferred_content_types,
        optimal_session_duration=optimal_session_duration,
        difficulty_progression_rate=difficulty_progression_rate,
        preferred_learning_times=preferred_learning_times,
        average_attention_span=average_attention_span,
        strong_topics=strong_topics,
        challenging_topics=challenging_topics,
        data_points_count=data_points_count
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern


def get_learning_pattern_by_user(db: Session, user_id: str) -> Optional[LearningPattern]:
    """Get the most recent learning pattern for a user."""
    return db.query(LearningPattern).filter(
        LearningPattern.user_id == user_id
    ).order_by(desc(LearningPattern.last_calculated)).first()


def get_learning_patterns_by_type(db: Session, pattern_type: LearningStyleType) -> List[LearningPattern]:
    """Get all learning patterns of a specific type."""
    return db.query(LearningPattern).filter(LearningPattern.pattern_type == pattern_type).all()


def update_learning_pattern(
    db: Session,
    pattern: LearningPattern,
    update_data: Dict[str, Any]
) -> LearningPattern:
    """Update an existing learning pattern."""
    for key, value in update_data.items():
        if hasattr(pattern, key):
            setattr(pattern, key, value)
    
    pattern.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pattern)
    return pattern


def delete_learning_patterns(db: Session, user_id: str) -> int:
    """Delete all learning patterns for a user."""
    deleted_count = db.query(LearningPattern).filter(LearningPattern.user_id == user_id).delete()
    db.commit()
    return deleted_count


# UserLearningProfile CRUD operations
def create_user_learning_profile(
    db: Session,
    profile_data,  # Can accept either dict or Pydantic model
    user_id: Optional[str] = None,
    learning_style: LearningStyleType = LearningStyleType.UNKNOWN,
    attention_span: Optional[int] = None,
    preferred_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
    completion_rate: float = 0.0,
    average_session_duration: Optional[int] = None,
    total_learning_time: int = 0,
    courses_completed: int = 0,
    engagement_score: float = 0.0,
    consistency_score: float = 0.0,
    challenge_preference: float = 0.5,
    strong_topics: Optional[List[str]] = None,
    challenging_topics: Optional[List[str]] = None,
    preferred_content_formats: Optional[List[str]] = None,
    current_difficulty_level: float = 0.5,
    adaptation_rate: float = 0.1
) -> UserLearningProfile:
    """Create a new user learning profile."""
    # Handle both Pydantic model and direct parameters
    if hasattr(profile_data, 'model_dump'):
        # It's a Pydantic model
        data = profile_data.model_dump()
        profile = UserLearningProfile(
            id=generate_analytics_id(),
            **data
        )
    elif isinstance(profile_data, dict):
        # It's a dictionary
        profile = UserLearningProfile(
            id=generate_analytics_id(),
            **profile_data
        )
    else:
        # Use individual parameters (backward compatibility)
        profile = UserLearningProfile(
            id=generate_analytics_id(),
            user_id=user_id or profile_data,
            learning_style=learning_style,
            attention_span=attention_span,
            preferred_difficulty=preferred_difficulty,
            completion_rate=completion_rate,
            average_session_duration=average_session_duration,
            total_learning_time=total_learning_time,
            courses_completed=courses_completed,
            engagement_score=engagement_score,
            consistency_score=consistency_score,
            challenge_preference=challenge_preference,
            strong_topics=strong_topics,
            challenging_topics=challenging_topics,
            preferred_content_formats=preferred_content_formats,
            current_difficulty_level=current_difficulty_level,
            adaptation_rate=adaptation_rate
        )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_user_learning_profile(db: Session, user_id: str) -> Optional[UserLearningProfile]:
    """Get the learning profile for a user."""
    return db.query(UserLearningProfile).filter(UserLearningProfile.user_id == user_id).first()


def update_user_learning_profile(
    db: Session,
    profile: UserLearningProfile,
    update_data: Dict[str, Any]
) -> UserLearningProfile:
    """Update an existing user learning profile."""
    for key, value in update_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    profile.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    return profile


def delete_user_learning_profile(db: Session, user_id: str) -> bool:
    """Delete the learning profile for a user."""
    deleted_count = db.query(UserLearningProfile).filter(UserLearningProfile.user_id == user_id).delete()
    db.commit()
    return deleted_count > 0


def get_all_user_learning_profiles(db: Session, limit: int = 1000) -> List[UserLearningProfile]:
    """Get all user learning profiles for collaborative filtering."""
    return db.query(UserLearningProfile).limit(limit).all()


# EngagementMetrics CRUD operations
def create_engagement_metrics(
    db: Session,
    user_id: str,
    time_period_start: datetime,
    time_period_end: datetime,
    course_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    total_time_spent: int = 0,
    interaction_count: int = 0,
    page_views: int = 0,
    completion_percentage: float = 0.0,
    engagement_score: float = 0.0,
    focus_score: float = 0.0,
    progress_velocity: float = 0.0,
    calculation_version: str = "1.0"
) -> EngagementMetrics:
    """Create new engagement metrics."""
    metrics = EngagementMetrics(
        id=generate_analytics_id(),
        user_id=user_id,
        course_id=course_id,
        chapter_id=chapter_id,
        time_period_start=time_period_start,
        time_period_end=time_period_end,
        total_time_spent=total_time_spent,
        interaction_count=interaction_count,
        page_views=page_views,
        completion_percentage=completion_percentage,
        engagement_score=engagement_score,
        focus_score=focus_score,
        progress_velocity=progress_velocity,
        calculation_version=calculation_version
    )
    db.add(metrics)
    db.commit()
    db.refresh(metrics)
    return metrics


def get_engagement_metrics(
    db: Session,
    user_id: Optional[str] = None,
    course_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[EngagementMetrics]:
    """Retrieve engagement metrics with optional filters."""
    query = db.query(EngagementMetrics)
    
    if user_id:
        query = query.filter(EngagementMetrics.user_id == user_id)
    if course_id:
        query = query.filter(EngagementMetrics.course_id == course_id)
    if chapter_id:
        query = query.filter(EngagementMetrics.chapter_id == chapter_id)
    if start_date:
        query = query.filter(EngagementMetrics.time_period_start >= start_date)
    if end_date:
        query = query.filter(EngagementMetrics.time_period_end <= end_date)
    
    return query.order_by(desc(EngagementMetrics.time_period_start)).offset(offset).limit(limit).all()


def get_user_engagement_summary(db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
    """Get engagement summary for a user over the last N days."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get aggregated metrics
    result = db.query(
        func.count(EngagementMetrics.id).label('total_sessions'),
        func.sum(EngagementMetrics.total_time_spent).label('total_time'),
        func.avg(EngagementMetrics.engagement_score).label('avg_engagement'),
        func.sum(EngagementMetrics.interaction_count).label('total_interactions'),
        func.sum(EngagementMetrics.page_views).label('total_page_views')
    ).filter(
        and_(
            EngagementMetrics.user_id == user_id,
            EngagementMetrics.time_period_start >= start_date,
            EngagementMetrics.time_period_end <= end_date
        )
    ).first()
    
    return {
        'total_sessions': result.total_sessions or 0,
        'total_time_spent': result.total_time or 0,
        'average_engagement_score': float(result.avg_engagement or 0.0),
        'total_interactions': result.total_interactions or 0,
        'total_page_views': result.total_page_views or 0,
        'period_days': days
    }


def delete_engagement_metrics(db: Session, user_id: str) -> int:
    """Delete all engagement metrics for a user."""
    deleted_count = db.query(EngagementMetrics).filter(EngagementMetrics.user_id == user_id).delete()
    db.commit()
    return deleted_count


# Analytics aggregation functions
def get_user_activity_timeline(
    db: Session, 
    user_id: str, 
    days: int = 30
) -> List[Dict[str, Any]]:
    """Get user activity timeline for the last N days."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Group by date and get daily activity
    result = db.query(
        func.date(UserBehaviorData.timestamp).label('activity_date'),
        func.count(UserBehaviorData.id).label('event_count'),
        func.count(func.distinct(UserBehaviorData.session_id)).label('session_count'),
        func.sum(UserBehaviorData.duration_seconds).label('total_duration')
    ).filter(
        and_(
            UserBehaviorData.user_id == user_id,
            UserBehaviorData.timestamp >= start_date,
            UserBehaviorData.timestamp <= end_date
        )
    ).group_by(
        func.date(UserBehaviorData.timestamp)
    ).order_by(
        func.date(UserBehaviorData.timestamp)
    ).all()
    
    return [
        {
            'date': row.activity_date,
            'event_count': row.event_count,
            'session_count': row.session_count,
            'total_duration': row.total_duration or 0
        }
        for row in result
    ]


def get_course_engagement_stats(db: Session, course_id: int) -> Dict[str, Any]:
    """Get engagement statistics for a specific course."""
    # Get basic stats
    result = db.query(
        func.count(func.distinct(UserBehaviorData.user_id)).label('unique_users'),
        func.count(UserBehaviorData.id).label('total_events'),
        func.avg(UserBehaviorData.engagement_score).label('avg_engagement'),
        func.sum(UserBehaviorData.duration_seconds).label('total_time')
    ).filter(UserBehaviorData.course_id == course_id).first()
    
    # Get completion stats
    completion_events = db.query(UserBehaviorData).filter(
        and_(
            UserBehaviorData.course_id == course_id,
            UserBehaviorData.event_type == EventType.COURSE_COMPLETE
        )
    ).count()
    
    return {
        'unique_users': result.unique_users or 0,
        'total_events': result.total_events or 0,
        'average_engagement_score': float(result.avg_engagement or 0.0),
        'total_time_spent': result.total_time or 0,
        'completion_count': completion_events,
        'completion_rate': completion_events / (result.unique_users or 1) if result.unique_users else 0.0
    }


def anonymize_user_analytics_data(db: Session, user_id: str) -> Dict[str, int]:
    """Anonymize all analytics data for a user (for privacy compliance)."""
    from ...utils.analytics_utils import anonymize_user_data
    
    # Get all behavior data for the user
    behavior_data = db.query(UserBehaviorData).filter(UserBehaviorData.user_id == user_id).all()
    
    anonymized_count = 0
    for data in behavior_data:
        if not data.is_anonymized:
            # Anonymize the user and session IDs
            anon_user_id, anon_session_id = anonymize_user_data(data.user_id, data.session_id)
            data.user_id = anon_user_id
            data.session_id = anon_session_id
            data.is_anonymized = True
            anonymized_count += 1
    
    db.commit()
    
    return {
        'anonymized_behavior_records': anonymized_count,
        'original_user_id': user_id
    }


# Additional CRUD operations for privacy compliance
def update_user_behavior_data(
    db: Session,
    behavior_data: UserBehaviorData,
    update_data: Dict[str, Any]
) -> UserBehaviorData:
    """Update an existing user behavior data record."""
    for key, value in update_data.items():
        if hasattr(behavior_data, key):
            setattr(behavior_data, key, value)
    
    db.commit()
    db.refresh(behavior_data)
    return behavior_data


def get_learning_patterns_by_user(db: Session, user_id: str) -> List[LearningPattern]:
    """Get all learning patterns for a user."""
    return db.query(LearningPattern).filter(LearningPattern.user_id == user_id).all()


def delete_user_learning_patterns(db: Session, user_id: str) -> int:
    """Delete all learning patterns for a user."""
    deleted_count = db.query(LearningPattern).filter(LearningPattern.user_id == user_id).delete()
    db.commit()
    return deleted_count


def get_user_engagement_metrics(db: Session, user_id: str) -> List[EngagementMetrics]:
    """Get all engagement metrics for a user."""
    return db.query(EngagementMetrics).filter(EngagementMetrics.user_id == user_id).all()


def delete_user_engagement_metrics(db: Session, user_id: str) -> int:
    """Delete all engagement metrics for a user."""
    deleted_count = db.query(EngagementMetrics).filter(EngagementMetrics.user_id == user_id).delete()
    db.commit()
    return deleted_count


def update_engagement_metrics(
    db: Session,
    metrics: EngagementMetrics,
    update_data: Dict[str, Any]
) -> EngagementMetrics:
    """Update existing engagement metrics."""
    for key, value in update_data.items():
        if hasattr(metrics, key):
            setattr(metrics, key, value)
    
    db.commit()
    db.refresh(metrics)
    return metrics


def count_user_behavior_data(db: Session, user_id: str) -> int:
    """Count total behavior data records for a user."""
    return db.query(UserBehaviorData).filter(UserBehaviorData.user_id == user_id).count()


def count_anonymized_behavior_data(db: Session, user_id: str) -> int:
    """Count anonymized behavior data records for a user."""
    return db.query(UserBehaviorData).filter(
        and_(
            UserBehaviorData.user_id == user_id,
            UserBehaviorData.is_anonymized == True
        )
    ).count()


def get_oldest_user_behavior_data(db: Session, user_id: str) -> Optional[UserBehaviorData]:
    """Get the oldest behavior data record for a user."""
    return db.query(UserBehaviorData).filter(
        UserBehaviorData.user_id == user_id
    ).order_by(asc(UserBehaviorData.created_at)).first()


def get_newest_user_behavior_data(db: Session, user_id: str) -> Optional[UserBehaviorData]:
    """Get the newest behavior data record for a user."""
    return db.query(UserBehaviorData).filter(
        UserBehaviorData.user_id == user_id
    ).order_by(desc(UserBehaviorData.created_at)).first()


def delete_behavior_data_before_date(db: Session, cutoff_date: datetime) -> int:
    """Delete behavior data older than the specified date."""
    deleted_count = db.query(UserBehaviorData).filter(
        and_(
            UserBehaviorData.created_at < cutoff_date,
            UserBehaviorData.is_anonymized == False  # Only delete non-anonymized old data
        )
    ).delete()
    db.commit()
    return deleted_count


def delete_engagement_metrics_before_date(db: Session, cutoff_date: datetime) -> int:
    """Delete engagement metrics older than the specified date."""
    deleted_count = db.query(EngagementMetrics).filter(
        EngagementMetrics.created_at < cutoff_date
    ).delete()
    db.commit()
    return deleted_count