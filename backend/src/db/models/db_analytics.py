"""Analytics data models for user behavior tracking and learning patterns."""

import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime, ForeignKey, 
    Float, JSON, Index, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class EventType(enum.Enum):
    """Types of user interaction events."""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    TIME_SPENT = "time_spent"
    COURSE_START = "course_start"
    COURSE_COMPLETE = "course_complete"
    CHAPTER_START = "chapter_start"
    CHAPTER_COMPLETE = "chapter_complete"
    ASSESSMENT_START = "assessment_start"
    ASSESSMENT_COMPLETE = "assessment_complete"
    CONTENT_INTERACTION = "content_interaction"


class LearningStyleType(enum.Enum):
    """Types of learning styles identified from user behavior."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class DifficultyLevel(enum.Enum):
    """Difficulty levels for content and user preferences."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserBehaviorData(Base):
    """Model for storing user interaction and behavior data from Umami analytics."""
    
    __tablename__ = "user_behavior_data"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    page_url = Column(String(2000), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Event-specific metadata stored as JSON
    event_metadata = Column(JSON, nullable=True)
    
    # Calculated engagement metrics
    engagement_score = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Privacy and data management
    is_anonymized = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    course = relationship("Course")
    chapter = relationship("Chapter")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_user_behavior_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_user_behavior_session_timestamp', 'session_id', 'timestamp'),
        Index('ix_user_behavior_course_event', 'course_id', 'event_type'),
    )


class LearningPattern(Base):
    """Model for storing identified learning patterns and preferences."""
    
    __tablename__ = "learning_patterns"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    pattern_type = Column(Enum(LearningStyleType), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Learning preferences derived from behavior
    preferred_content_types = Column(JSON, nullable=True)  # List of content types
    optimal_session_duration = Column(Integer, nullable=True)  # minutes
    difficulty_progression_rate = Column(Float, nullable=True)  # rate of difficulty increase
    
    # Time-based patterns
    preferred_learning_times = Column(JSON, nullable=True)  # hours of day
    average_attention_span = Column(Integer, nullable=True)  # minutes
    
    # Performance patterns
    strong_topics = Column(JSON, nullable=True)  # List of topic areas
    challenging_topics = Column(JSON, nullable=True)  # List of topic areas
    
    # Metadata
    data_points_count = Column(Integer, nullable=False, default=0)
    last_calculated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_learning_pattern_user_type', 'user_id', 'pattern_type'),
        Index('ix_learning_pattern_confidence', 'confidence_score'),
    )


class UserLearningProfile(Base):
    """Model for comprehensive user learning profile based on analytics and patterns."""
    
    __tablename__ = "user_learning_profiles"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Primary learning characteristics
    learning_style = Column(Enum(LearningStyleType), nullable=False, default=LearningStyleType.UNKNOWN)
    attention_span = Column(Integer, nullable=True)  # minutes
    preferred_difficulty = Column(Enum(DifficultyLevel), nullable=False, default=DifficultyLevel.BEGINNER)
    
    # Performance metrics
    completion_rate = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    average_session_duration = Column(Integer, nullable=True)  # minutes
    total_learning_time = Column(Integer, nullable=False, default=0)  # minutes
    courses_completed = Column(Integer, nullable=False, default=0)
    
    # Engagement metrics
    engagement_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    consistency_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    challenge_preference = Column(Float, nullable=False, default=0.5)  # 0.0 (easy) to 1.0 (hard)
    
    # Learning preferences
    strong_topics = Column(JSON, nullable=True)  # List of topic areas
    challenging_topics = Column(JSON, nullable=True)  # List of topic areas
    preferred_content_formats = Column(JSON, nullable=True)  # List of content formats
    
    # Adaptive learning parameters
    current_difficulty_level = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    adaptation_rate = Column(Float, nullable=False, default=0.1)  # how quickly to adapt
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_user_profile_learning_style', 'learning_style'),
        Index('ix_user_profile_difficulty', 'preferred_difficulty'),
        Index('ix_user_profile_engagement', 'engagement_score'),
    )


class EngagementMetrics(Base):
    """Model for storing calculated engagement metrics for users and content."""
    
    __tablename__ = "engagement_metrics"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    
    # Time-based metrics
    time_period_start = Column(DateTime(timezone=True), nullable=False)
    time_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Engagement calculations
    total_time_spent = Column(Integer, nullable=False, default=0)  # seconds
    interaction_count = Column(Integer, nullable=False, default=0)
    page_views = Column(Integer, nullable=False, default=0)
    completion_percentage = Column(Float, nullable=False, default=0.0)
    
    # Calculated scores
    engagement_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    focus_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    progress_velocity = Column(Float, nullable=False, default=0.0)  # content per time
    
    # Metadata
    calculation_version = Column(String(10), nullable=False, default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    course = relationship("Course")
    chapter = relationship("Chapter")
    
    # Indexes
    __table_args__ = (
        Index('ix_engagement_user_period', 'user_id', 'time_period_start', 'time_period_end'),
        Index('ix_engagement_course_period', 'course_id', 'time_period_start', 'time_period_end'),
        Index('ix_engagement_score', 'engagement_score'),
    )