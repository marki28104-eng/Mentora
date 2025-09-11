"""Database models for the Mentora application."""

from .db_user import User
from .db_course import Course, Chapter, PracticeQuestion, CourseStatus
from .db_file import Document, Image
from .db_note import Note
from .db_chat import Chat
from .db_flashcard import FlashcardDeck, PDFChapter, Flashcard, FlashcardReview, ChapterSegmentationMode, FlashcardDifficulty
from .db_usage import Usage
from .db_analytics import (
    UserBehaviorData, 
    LearningPattern, 
    UserLearningProfile, 
    EngagementMetrics,
    EventType,
    LearningStyleType,
    DifficultyLevel
)

__all__ = [
    # User models
    "User",
    
    # Course models
    "Course",
    "Chapter", 
    "PracticeQuestion",
    "CourseStatus",
    
    # File models
    "Document",
    "Image",
    
    # Note models
    "Note",
    
    # Chat models
    "Chat",
    
    # Flashcard models
    "FlashcardDeck",
    "PDFChapter", 
    "Flashcard",
    "FlashcardReview",
    "ChapterSegmentationMode",
    "FlashcardDifficulty",
    
    # Usage models
    "Usage",
    
    # Analytics models
    "UserBehaviorData",
    "LearningPattern", 
    "UserLearningProfile",
    "EngagementMetrics",
    
    # Analytics enums
    "EventType",
    "LearningStyleType",
    "DifficultyLevel",
]