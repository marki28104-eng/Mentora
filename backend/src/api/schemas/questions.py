from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class QuestionResponse(BaseModel):
    """Schema for a practice question."""
    id: int
    type: str
    question: str
    answer_a: Optional[str] = None
    answer_b: Optional[str] = None
    answer_c: Optional[str] = None
    answer_d: Optional[str] = None
    correct_answer: str
    explanation: Optional[str] = None
    users_answer: Optional[str] = None
    points_received: Optional[int] = None
    feedback: Optional[str] = None


class AdaptiveQuestionResponse(BaseModel):
    """Schema for an adaptive question with personalization data."""
    question: QuestionResponse
    adaptations: Dict[str, Any]
    session_info: Dict[str, Any]


class AssessmentSessionResponse(BaseModel):
    """Schema for an adaptive assessment session."""
    session_id: str
    chapter_id: int
    total_questions: int
    difficulty_adjustments: Dict[str, Any]
    adaptive_features: bool


class SupplementaryMaterialResponse(BaseModel):
    """Schema for supplementary practice material."""
    material_id: str
    title: str
    content_type: str
    difficulty_level: str
    estimated_time: int
    relevance_score: float
    reason: str
    priority: int
    topic: str


class AssessmentFeedbackResponse(BaseModel):
    """Schema for assessment feedback."""
    question_id: int
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    time_taken: int
    performance_feedback: Dict[str, str]
    session_id: Optional[str] = None
    adaptive_adjustments: Optional[Dict[str, Any]] = None