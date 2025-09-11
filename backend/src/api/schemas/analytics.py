"""Pydantic schemas for analytics data validation and sanitization."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class EventTypeSchema(str, Enum):
    """Event types for user behavior tracking."""
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


class LearningStyleSchema(str, Enum):
    """Learning style types."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class DifficultyLevelSchema(str, Enum):
    """Difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserBehaviorDataBase(BaseModel):
    """Base schema for user behavior data."""
    user_id: str = Field(..., min_length=1, max_length=50)
    session_id: str = Field(..., min_length=1, max_length=100)
    event_type: EventTypeSchema
    page_url: str = Field(..., min_length=1, max_length=2000)
    course_id: Optional[int] = Field(None, ge=1)
    chapter_id: Optional[int] = Field(None, ge=1)
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[int] = Field(None, ge=0)

    @field_validator('page_url')
    @classmethod
    def validate_page_url(cls, v: str) -> str:
        """Sanitize and validate page URL."""
        # Remove any potential XSS or injection attempts
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Page URL cannot be empty")
        return sanitized

    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate and sanitize metadata to ensure no PII is included."""
        if v is None:
            return v
        
        # List of keys that might contain PII - reject if found
        pii_keys = {
            'email', 'phone', 'address', 'name', 'firstname', 'lastname',
            'ssn', 'social_security', 'credit_card', 'password', 'token'
        }
        
        sanitized = {}
        for key, value in v.items():
            # Check if key might contain PII
            if any(pii_key in key.lower() for pii_key in pii_keys):
                continue  # Skip PII fields
            
            # Limit string values to prevent abuse
            if isinstance(value, str) and len(value) > 1000:
                value = value[:1000]
            
            # Only allow basic types
            if isinstance(value, (str, int, float, bool, list, dict)):
                sanitized[key] = value
        
        return sanitized


class UserBehaviorDataCreate(UserBehaviorDataBase):
    """Schema for creating user behavior data."""
    pass


class UserBehaviorData(UserBehaviorDataBase):
    """Schema for user behavior data response."""
    id: str
    engagement_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_anonymized: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningPatternBase(BaseModel):
    """Base schema for learning patterns."""
    user_id: str = Field(..., min_length=1, max_length=50)
    pattern_type: LearningStyleSchema
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    preferred_content_types: Optional[List[str]] = None
    optimal_session_duration: Optional[int] = Field(None, ge=1, le=480)  # max 8 hours
    difficulty_progression_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    preferred_learning_times: Optional[List[int]] = None  # hours 0-23
    average_attention_span: Optional[int] = Field(None, ge=1, le=240)  # max 4 hours
    strong_topics: Optional[List[str]] = None
    challenging_topics: Optional[List[str]] = None

    @field_validator('preferred_learning_times')
    @classmethod
    def validate_learning_times(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validate learning times are valid hours."""
        if v is None:
            return v
        
        for hour in v:
            if not 0 <= hour <= 23:
                raise ValueError("Learning times must be hours between 0 and 23")
        
        return v

    @field_validator('preferred_content_types', 'strong_topics', 'challenging_topics')
    @classmethod
    def validate_topic_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and sanitize topic lists."""
        if v is None:
            return v
        
        # Limit list size and string lengths
        sanitized = []
        for item in v[:20]:  # Max 20 items
            if isinstance(item, str) and len(item.strip()) > 0:
                sanitized.append(item.strip()[:100])  # Max 100 chars per item
        
        return sanitized if sanitized else None


class LearningPatternCreate(LearningPatternBase):
    """Schema for creating learning patterns."""
    pass


class LearningPatternUpdate(BaseModel):
    """Schema for updating learning patterns."""
    pattern_type: Optional[LearningStyleSchema] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    preferred_content_types: Optional[List[str]] = None
    optimal_session_duration: Optional[int] = Field(None, ge=1, le=480)
    difficulty_progression_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    preferred_learning_times: Optional[List[int]] = None
    average_attention_span: Optional[int] = Field(None, ge=1, le=240)
    strong_topics: Optional[List[str]] = None
    challenging_topics: Optional[List[str]] = None


class LearningPattern(LearningPatternBase):
    """Schema for learning pattern response."""
    id: str
    data_points_count: int
    last_calculated: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLearningProfileBase(BaseModel):
    """Base schema for user learning profiles."""
    user_id: str = Field(..., min_length=1, max_length=50)
    learning_style: LearningStyleSchema = LearningStyleSchema.UNKNOWN
    attention_span: Optional[int] = Field(None, ge=1, le=240)  # minutes
    preferred_difficulty: DifficultyLevelSchema = DifficultyLevelSchema.BEGINNER
    completion_rate: float = Field(0.0, ge=0.0, le=1.0)
    average_session_duration: Optional[int] = Field(None, ge=1, le=480)  # minutes
    total_learning_time: int = Field(0, ge=0)  # minutes
    courses_completed: int = Field(0, ge=0)
    engagement_score: float = Field(0.0, ge=0.0, le=1.0)
    consistency_score: float = Field(0.0, ge=0.0, le=1.0)
    challenge_preference: float = Field(0.5, ge=0.0, le=1.0)
    strong_topics: Optional[List[str]] = None
    challenging_topics: Optional[List[str]] = None
    preferred_content_formats: Optional[List[str]] = None
    current_difficulty_level: float = Field(0.5, ge=0.0, le=1.0)
    adaptation_rate: float = Field(0.1, ge=0.0, le=1.0)


class UserLearningProfileCreate(UserLearningProfileBase):
    """Schema for creating user learning profiles."""
    pass


class UserLearningProfileUpdate(BaseModel):
    """Schema for updating user learning profiles."""
    learning_style: Optional[LearningStyleSchema] = None
    attention_span: Optional[int] = Field(None, ge=1, le=240)
    preferred_difficulty: Optional[DifficultyLevelSchema] = None
    completion_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    average_session_duration: Optional[int] = Field(None, ge=1, le=480)
    total_learning_time: Optional[int] = Field(None, ge=0)
    courses_completed: Optional[int] = Field(None, ge=0)
    engagement_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    consistency_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    challenge_preference: Optional[float] = Field(None, ge=0.0, le=1.0)
    strong_topics: Optional[List[str]] = None
    challenging_topics: Optional[List[str]] = None
    preferred_content_formats: Optional[List[str]] = None
    current_difficulty_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    adaptation_rate: Optional[float] = Field(None, ge=0.0, le=1.0)


class UserLearningProfile(UserLearningProfileBase):
    """Schema for user learning profile response."""
    id: str
    last_updated: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EngagementMetricsBase(BaseModel):
    """Base schema for engagement metrics."""
    user_id: str = Field(..., min_length=1, max_length=50)
    course_id: Optional[int] = Field(None, ge=1)
    chapter_id: Optional[int] = Field(None, ge=1)
    time_period_start: datetime
    time_period_end: datetime
    total_time_spent: int = Field(0, ge=0)  # seconds
    interaction_count: int = Field(0, ge=0)
    page_views: int = Field(0, ge=0)
    completion_percentage: float = Field(0.0, ge=0.0, le=1.0)
    engagement_score: float = Field(0.0, ge=0.0, le=1.0)
    focus_score: float = Field(0.0, ge=0.0, le=1.0)
    progress_velocity: float = Field(0.0, ge=0.0)

    @field_validator('time_period_end')
    @classmethod
    def validate_time_period(cls, v: datetime, info) -> datetime:
        """Validate that end time is after start time."""
        if 'time_period_start' in info.data and v <= info.data['time_period_start']:
            raise ValueError("End time must be after start time")
        return v


class EngagementMetricsCreate(EngagementMetricsBase):
    """Schema for creating engagement metrics."""
    pass


class EngagementMetrics(EngagementMetricsBase):
    """Schema for engagement metrics response."""
    id: str
    calculation_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyticsQuery(BaseModel):
    """Schema for analytics query parameters."""
    user_id: Optional[str] = Field(None, min_length=1, max_length=50)
    course_id: Optional[int] = Field(None, ge=1)
    chapter_id: Optional[int] = Field(None, ge=1)
    event_type: Optional[EventTypeSchema] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate that end date is after start date."""
        if v is not None and 'start_date' in info.data and info.data['start_date'] is not None:
            if v <= info.data['start_date']:
                raise ValueError("End date must be after start date")
        return v


class AnalyticsSummary(BaseModel):
    """Schema for analytics summary response."""
    user_id: str
    total_events: int
    total_time_spent: int  # seconds
    unique_sessions: int
    courses_accessed: int
    chapters_completed: int
    average_engagement_score: float
    learning_style: Optional[LearningStyleSchema] = None
    preferred_difficulty: Optional[DifficultyLevelSchema] = None
    last_activity: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Advanced Analytics Schemas

class PredictiveOutcomeResponse(BaseModel):
    """Schema for predictive analytics outcome response."""
    user_id: str
    prediction_type: str
    predicted_value: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    factors: Dict[str, float]
    recommendations: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CohortAnalysisResponse(BaseModel):
    """Schema for cohort analysis response."""
    cohort_name: str
    cohort_size: int = Field(..., ge=1)
    time_period: str
    retention_rates: Dict[str, float]
    engagement_trends: Dict[str, float]
    learning_patterns: Dict[str, Any]
    performance_metrics: Dict[str, float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RealTimePersonalizationResponse(BaseModel):
    """Schema for real-time personalization response."""
    user_id: str
    session_id: str
    adjustments: Dict[str, Any]
    trigger_events: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RealTimeEventRequest(BaseModel):
    """Schema for real-time event processing request."""
    session_id: str = Field(..., min_length=1, max_length=100)
    event_data: Dict[str, Any]

    @field_validator('event_data')
    @classmethod
    def validate_event_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize event data."""
        # Ensure required fields
        if 'event_type' not in v:
            raise ValueError("event_type is required in event_data")
        
        # Sanitize data similar to metadata validation
        pii_keys = {
            'email', 'phone', 'address', 'name', 'firstname', 'lastname',
            'ssn', 'social_security', 'credit_card', 'password', 'token'
        }
        
        sanitized = {}
        for key, value in v.items():
            # Check if key might contain PII
            if any(pii_key in key.lower() for pii_key in pii_keys):
                continue  # Skip PII fields
            
            # Limit string values to prevent abuse
            if isinstance(value, str) and len(value) > 1000:
                value = value[:1000]
            
            # Only allow basic types
            if isinstance(value, (str, int, float, bool, list, dict)):
                sanitized[key] = value
        
        return sanitized

    model_config = ConfigDict(from_attributes=True)