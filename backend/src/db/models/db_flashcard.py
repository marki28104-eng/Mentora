"""Flashcard models for spaced repetition learning system."""

import enum
from datetime import datetime, timedelta
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime, ForeignKey, 
    Float, JSON, Index, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ChapterSegmentationMode(enum.Enum):
    """Modes for segmenting PDF chapters."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    PAGE_BASED = "page_based"


class FlashcardDifficulty(enum.Enum):
    """Difficulty levels for flashcards."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class FlashcardDeck(Base):
    """Model for flashcard decks."""
    
    __tablename__ = "flashcard_decks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    source_pdf_id = Column(Integer, nullable=True)  # Reference to uploaded PDF
    segmentation_mode = Column(Enum(ChapterSegmentationMode), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    course = relationship("Course")
    flashcards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")
    pdf_chapters = relationship("PDFChapter", back_populates="deck", cascade="all, delete-orphan")


class PDFChapter(Base):
    """Model for PDF chapters extracted from documents."""
    
    __tablename__ = "pdf_chapters"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"), nullable=False, index=True)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    detection_confidence = Column(Float, nullable=False, default=0.0)
    detection_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    deck = relationship("FlashcardDeck", back_populates="pdf_chapters")
    flashcards = relationship("Flashcard", back_populates="pdf_chapter")


class Flashcard(Base):
    """Model for individual flashcards with spaced repetition data."""
    
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"), nullable=False, index=True)
    pdf_chapter_id = Column(Integer, ForeignKey("pdf_chapters.id"), nullable=True, index=True)
    
    # Card content
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    difficulty = Column(Enum(FlashcardDifficulty), nullable=False, default=FlashcardDifficulty.MEDIUM)
    source_slide_numbers = Column(String(100), nullable=True)  # e.g., "5-7,12"
    auto_generated = Column(Boolean, nullable=False, default=False)
    
    # Spaced repetition algorithm data
    ease_factor = Column(Float, nullable=False, default=2.5)  # SM-2 algorithm
    interval_days = Column(Integer, nullable=False, default=1)
    repetitions = Column(Integer, nullable=False, default=0)
    next_review_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Review statistics
    times_reviewed = Column(Integer, nullable=False, default=0)
    times_correct = Column(Integer, nullable=False, default=0)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Card management
    is_suspended = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    deck = relationship("FlashcardDeck", back_populates="flashcards")
    pdf_chapter = relationship("PDFChapter", back_populates="flashcards")
    reviews = relationship("FlashcardReview", back_populates="flashcard", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_flashcard_next_review', 'next_review_date'),
        Index('ix_flashcard_deck_suspended', 'deck_id', 'is_suspended'),
    )


class FlashcardReview(Base):
    """Model for tracking flashcard review sessions and responses."""
    
    __tablename__ = "flashcard_reviews"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    
    # Review data
    response_quality = Column(Integer, nullable=False)  # 1=Hard, 3=Normal, 5=Easy
    response_time_seconds = Column(Float, nullable=True)
    
    # Previous state (for analytics)
    previous_ease_factor = Column(Float, nullable=True)
    previous_interval_days = Column(Integer, nullable=True)
    previous_repetitions = Column(Integer, nullable=True)
    
    # Timestamp
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    flashcard = relationship("Flashcard", back_populates="reviews")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_flashcard_review_user_date', 'user_id', 'reviewed_at'),
        Index('ix_flashcard_review_card_date', 'flashcard_id', 'reviewed_at'),
    )