from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class CourseRequest(BaseModel):
    """Request schema for creating a course session."""
    query: str = Field(..., description="What the user wants to learn")
    time_hours: int = Field(..., description="Time investment in hours")
    document_ids: List[int] = Field(default=[], description="Document IDs")
    picture_ids: List[int] = Field(default=[], description="Picture IDs")
    language: str = Field(..., description="Language")
    difficulty: str = Field(..., description="Difficulty")


class Chapter(BaseModel):
    """Schema for a chapter in the course."""
    id: int  # Add this line to include the database ID
    index: int
    caption: str
    summary: str
    content: str
    time_minutes: int
    is_completed: bool = False  # Also useful for the frontend
    image_url: Optional[str] = None  # Optional image URL for the chapter

    class Config:
        from_attributes = True  # For Pydantic v2 (replaces orm_mode = True)


class CourseInfo(BaseModel):
    """Schema for a list of courses."""
    course_id: int
    total_time_hours: int
    status: str
    # Information from the agent
    title: Optional[str] = None
    description: Optional[str] = None
    chapter_count: Optional[int] = None
    image_url: Optional[str] = None
    completed_chapter_count: Optional[int] = None
    user_name: Optional[str] = None
    is_public: Optional[bool] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For Pydantic v2 (replaces orm_mode = True)


class UpdateCoursePublicStatusRequest(BaseModel):
    """Schema for updating the public status of a course."""
    is_public: bool


class PersonalizationData(BaseModel):
    """Schema for personalization data in chapter responses."""
    is_personalized: bool
    adaptations: Dict[str, Any] = {}
    content_modifications: Dict[str, Any] = {}
    learning_style: str = "unknown"


class PersonalizedChapter(BaseModel):
    """Schema for a personalized chapter response."""
    id: int
    index: int
    caption: str
    summary: str
    content: str
    time_minutes: int
    is_completed: bool = False
    image_url: Optional[str] = None
    personalization: PersonalizationData

    class Config:
        from_attributes = True


class CourseRecommendation(BaseModel):
    """Schema for course recommendations."""
    course_id: int
    title: str
    recommendation_score: float
    reason: str
    recommended_difficulty: str
    estimated_completion_time: int
    topic_match_score: float
    learning_style_match: float


class PacingData(BaseModel):
    """Schema for adaptive pacing data."""
    has_adjustment: bool
    current_pace: float
    recommended_pace: float
    adjustment_factor: float
    reason: str
    confidence: Optional[float] = None
    next_review_date: Optional[str] = None
