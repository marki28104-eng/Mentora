"""
Adaptive Assessment Service for providing personalized quiz experiences.

This service integrates with the learning adaptation service to modify assessment
difficulty, provide real-time adjustments, and recommend supplementary practice.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from ..db.crud import questions_crud, analytics_crud
from ..db.models.db_course import PracticeQuestion, Chapter
from ..db.models.db_analytics import UserLearningProfile, DifficultyLevel
from .learning_adaptation_service import LearningAdaptationService, AssessmentModification
from .personalization_engine import PersonalizationEngine
from ..api.schemas.questions import QuestionResponse
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class AdaptiveQuestion:
    """Container for an adapted question with difficulty modifications."""
    
    def __init__(
        self,
        question: PracticeQuestion,
        original_difficulty: float,
        adapted_difficulty: float,
        time_adjustment: float,
        support_level: str,
        hints: List[str],
        modification_reason: str
    ):
        self.question = question
        self.original_difficulty = original_difficulty
        self.adapted_difficulty = adapted_difficulty
        self.time_adjustment = time_adjustment
        self.support_level = support_level
        self.hints = hints
        self.modification_reason = modification_reason


class AssessmentSession:
    """Container for an adaptive assessment session."""
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        chapter_id: int,
        questions: List[AdaptiveQuestion],
        difficulty_adjustments: Dict[str, Any],
        real_time_adaptation: bool = True
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.chapter_id = chapter_id
        self.questions = questions
        self.difficulty_adjustments = difficulty_adjustments
        self.real_time_adaptation = real_time_adaptation
        self.current_question_index = 0
        self.performance_history = []


class AdaptiveAssessmentService:
    """Service for providing adaptive assessment experiences."""
    
    def __init__(self):
        self.learning_adaptation = LearningAdaptationService()
        self.personalization_engine = PersonalizationEngine()
        
    async def create_adaptive_assessment(
        self,
        db: Session,
        user_id: str,
        chapter_id: int,
        assessment_type: str = "practice"
    ) -> Optional[AssessmentSession]:
        """
        Create an adaptive assessment session for a user and chapter.
        
        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID
            assessment_type: Type of assessment (practice, quiz, exam)
            
        Returns:
            AssessmentSession or None if creation fails
        """
        try:
            # Get base questions for the chapter
            base_questions = questions_crud.get_questions_by_chapter_id(db, chapter_id)
            
            if not base_questions:
                logger.info(f"No questions found for chapter {chapter_id}")
                return None
            
            # Get user's learning profile
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            
            # Create adaptive questions
            adaptive_questions = []
            
            for question in base_questions:
                adaptive_question = await self._adapt_question(
                    db=db,
                    question=question,
                    user_id=user_id,
                    user_profile=user_profile
                )
                adaptive_questions.append(adaptive_question)
            
            # Calculate overall difficulty adjustments
            difficulty_adjustments = await self._calculate_session_adjustments(
                db=db,
                user_id=user_id,
                chapter_id=chapter_id,
                user_profile=user_profile
            )
            
            # Create session
            session_id = f"assessment_{user_id}_{chapter_id}_{generate_analytics_id()}"
            
            session = AssessmentSession(
                session_id=session_id,
                user_id=user_id,
                chapter_id=chapter_id,
                questions=adaptive_questions,
                difficulty_adjustments=difficulty_adjustments,
                real_time_adaptation=True
            )
            
            logger.info(f"Created adaptive assessment session {session_id} with {len(adaptive_questions)} questions")
            return session
            
        except Exception as e:
            logger.error(f"Error creating adaptive assessment: {str(e)}")
            return None
    
    async def get_next_question(
        self,
        db: Session,
        session: AssessmentSession,
        previous_answer: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next question in an adaptive assessment with real-time adjustments.
        
        Args:
            db: Database session
            session: Assessment session
            previous_answer: Previous answer data for real-time adaptation
            
        Returns:
            Dictionary with question data and adaptations
        """
        try:
            # Process previous answer if provided
            if previous_answer:
                await self._process_answer_feedback(db, session, previous_answer)
            
            # Check if assessment is complete
            if session.current_question_index >= len(session.questions):
                return None
            
            # Get current question
            adaptive_question = session.questions[session.current_question_index]
            
            # Apply real-time adaptations if enabled
            if session.real_time_adaptation and session.performance_history:
                adaptive_question = await self._apply_real_time_adaptation(
                    db=db,
                    session=session,
                    question=adaptive_question
                )
            
            # Prepare question response
            question_data = {
                "question": {
                    "id": adaptive_question.question.id,
                    "type": adaptive_question.question.type,
                    "question": adaptive_question.question.question,
                    "answer_a": adaptive_question.question.answer_a,
                    "answer_b": adaptive_question.question.answer_b,
                    "answer_c": adaptive_question.question.answer_c,
                    "answer_d": adaptive_question.question.answer_d,
                    "correct_answer": adaptive_question.question.correct_answer,
                    "explanation": adaptive_question.question.explanation
                },
                "adaptations": {
                    "original_difficulty": adaptive_question.original_difficulty,
                    "adapted_difficulty": adaptive_question.adapted_difficulty,
                    "time_adjustment": adaptive_question.time_adjustment,
                    "support_level": adaptive_question.support_level,
                    "hints": adaptive_question.hints,
                    "modification_reason": adaptive_question.modification_reason
                },
                "session_info": {
                    "session_id": session.session_id,
                    "question_index": session.current_question_index + 1,
                    "total_questions": len(session.questions),
                    "progress": (session.current_question_index + 1) / len(session.questions)
                }
            }
            
            # Move to next question
            session.current_question_index += 1
            
            return question_data
            
        except Exception as e:
            logger.error(f"Error getting next question: {str(e)}")
            return None
    
    async def get_supplementary_practice(
        self,
        db: Session,
        user_id: str,
        chapter_id: int,
        struggling_topics: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get supplementary practice recommendations for struggling topics.
        
        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID
            struggling_topics: List of topics the user is struggling with
            
        Returns:
            List of supplementary practice recommendations
        """
        try:
            recommendations = []
            
            for topic in struggling_topics:
                # Get supplementary materials from learning adaptation service
                materials = await self.learning_adaptation.provide_supplementary_content(
                    db=db,
                    user_id=user_id,
                    topic=topic,
                    max_recommendations=3
                )
                
                for material in materials:
                    recommendations.append({
                        "material_id": material.material_id,
                        "title": material.title,
                        "content_type": material.content_type,
                        "difficulty_level": material.difficulty_level.value,
                        "estimated_time": material.estimated_time,
                        "relevance_score": material.relevance_score,
                        "reason": material.reason,
                        "priority": material.priority,
                        "topic": topic
                    })
            
            # Sort by priority and relevance
            recommendations.sort(key=lambda x: (x["priority"], -x["relevance_score"]))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting supplementary practice: {str(e)}")
            return []
    
    async def _adapt_question(
        self,
        db: Session,
        question: PracticeQuestion,
        user_id: str,
        user_profile: Optional[UserLearningProfile]
    ) -> AdaptiveQuestion:
        """Adapt a single question based on user profile."""
        
        # Default values
        original_difficulty = 0.5  # Default medium difficulty
        adapted_difficulty = original_difficulty
        time_adjustment = 1.0
        support_level = "standard"
        hints = []
        modification_reason = "No adaptation needed"
        
        if user_profile:
            # Get assessment modification from learning adaptation service
            assessment_modification = await self.learning_adaptation.modify_assessment_difficulty(
                db=db,
                user_id=user_id,
                assessment_id=f"question_{question.id}",
                assessment_metadata={"difficulty": original_difficulty}
            )
            
            if assessment_modification:
                adapted_difficulty = assessment_modification.modified_difficulty
                support_level = assessment_modification.support_level
                modification_reason = assessment_modification.modification_reason
                
                # Extract time adjustments
                if "time_multiplier" in assessment_modification.time_adjustments:
                    time_adjustment = assessment_modification.time_adjustments["time_multiplier"]
                
                # Generate hints based on question adjustments
                if "provide_hints" in assessment_modification.question_adjustments:
                    hints = self._generate_question_hints(question, user_profile)
        
        return AdaptiveQuestion(
            question=question,
            original_difficulty=original_difficulty,
            adapted_difficulty=adapted_difficulty,
            time_adjustment=time_adjustment,
            support_level=support_level,
            hints=hints,
            modification_reason=modification_reason
        )
    
    async def _calculate_session_adjustments(
        self,
        db: Session,
        user_id: str,
        chapter_id: int,
        user_profile: Optional[UserLearningProfile]
    ) -> Dict[str, Any]:
        """Calculate overall session-level adjustments."""
        
        adjustments = {
            "overall_difficulty_modifier": 1.0,
            "time_extension": 1.0,
            "support_features": [],
            "adaptive_features": []
        }
        
        if not user_profile:
            return adjustments
        
        # Adjust based on completion rate
        if user_profile.completion_rate < 0.4:
            adjustments["overall_difficulty_modifier"] = 0.8
            adjustments["time_extension"] = 1.3
            adjustments["support_features"].extend(["hints", "step_by_step", "examples"])
        elif user_profile.completion_rate > 0.8:
            adjustments["overall_difficulty_modifier"] = 1.2
            adjustments["adaptive_features"].extend(["bonus_questions", "advanced_concepts"])
        
        # Adjust based on learning style
        if user_profile.learning_style:
            style = user_profile.learning_style.value
            if style == "visual":
                adjustments["support_features"].extend(["diagrams", "visual_aids"])
            elif style == "kinesthetic":
                adjustments["support_features"].extend(["interactive_elements", "simulations"])
        
        # Adjust based on attention span
        if user_profile.attention_span and user_profile.attention_span < 20:
            adjustments["adaptive_features"].extend(["frequent_breaks", "shorter_sessions"])
        
        return adjustments
    
    async def _process_answer_feedback(
        self,
        db: Session,
        session: AssessmentSession,
        answer_data: Dict[str, Any]
    ) -> None:
        """Process answer feedback for real-time adaptation."""
        
        try:
            # Extract answer information
            question_id = answer_data.get("question_id")
            user_answer = answer_data.get("user_answer")
            time_taken = answer_data.get("time_taken", 0)
            is_correct = answer_data.get("is_correct", False)
            
            # Record performance
            performance_record = {
                "question_id": question_id,
                "user_answer": user_answer,
                "time_taken": time_taken,
                "is_correct": is_correct,
                "timestamp": datetime.now(timezone.utc)
            }
            
            session.performance_history.append(performance_record)
            
            # Analyze performance trend for real-time adaptation
            if len(session.performance_history) >= 3:
                recent_performance = session.performance_history[-3:]
                correct_count = sum(1 for p in recent_performance if p["is_correct"])
                
                # Update session difficulty adjustments based on performance
                if correct_count == 0:  # Struggling
                    session.difficulty_adjustments["overall_difficulty_modifier"] *= 0.9
                    session.difficulty_adjustments["time_extension"] *= 1.1
                elif correct_count == 3:  # Performing well
                    session.difficulty_adjustments["overall_difficulty_modifier"] *= 1.05
                    session.difficulty_adjustments["time_extension"] *= 0.95
            
        except Exception as e:
            logger.error(f"Error processing answer feedback: {str(e)}")
    
    async def _apply_real_time_adaptation(
        self,
        db: Session,
        session: AssessmentSession,
        question: AdaptiveQuestion
    ) -> AdaptiveQuestion:
        """Apply real-time adaptations based on current performance."""
        
        try:
            if not session.performance_history:
                return question
            
            # Calculate recent performance metrics
            recent_performance = session.performance_history[-3:] if len(session.performance_history) >= 3 else session.performance_history
            
            if not recent_performance:
                return question
            
            correct_rate = sum(1 for p in recent_performance if p["is_correct"]) / len(recent_performance)
            avg_time = sum(p["time_taken"] for p in recent_performance) / len(recent_performance)
            
            # Adjust difficulty based on performance
            difficulty_modifier = session.difficulty_adjustments["overall_difficulty_modifier"]
            
            if correct_rate < 0.3:  # Struggling significantly
                question.adapted_difficulty *= 0.8
                question.time_adjustment *= 1.2
                question.support_level = "high"
                question.hints.extend(["Take your time", "Review the concept if needed"])
                question.modification_reason = "Real-time adaptation: providing additional support"
                
            elif correct_rate > 0.8:  # Performing very well
                question.adapted_difficulty *= 1.1
                question.time_adjustment *= 0.9
                question.support_level = "minimal"
                question.modification_reason = "Real-time adaptation: increasing challenge"
            
            return question
            
        except Exception as e:
            logger.error(f"Error applying real-time adaptation: {str(e)}")
            return question
    
    def _generate_question_hints(
        self,
        question: PracticeQuestion,
        user_profile: UserLearningProfile
    ) -> List[str]:
        """Generate helpful hints for a question based on user profile."""
        
        hints = []
        
        # Generic hints based on question type
        if question.type == "MC":
            hints.append("Read all answer choices carefully before selecting")
            hints.append("Eliminate obviously incorrect answers first")
        elif question.type == "OT":
            hints.append("Take time to think through your answer")
            hints.append("Consider key concepts from the chapter")
        
        # Hints based on learning style
        if user_profile.learning_style:
            style = user_profile.learning_style.value
            if style == "visual":
                hints.append("Try to visualize the concept or draw a diagram")
            elif style == "kinesthetic":
                hints.append("Think about practical applications or examples")
            elif style == "auditory":
                hints.append("Try explaining the concept out loud to yourself")
        
        # Hints based on challenge preference
        if user_profile.challenge_preference < 0.4:
            hints.append("Don't worry if this seems difficult - take it step by step")
            hints.append("Focus on the main concept rather than complex details")
        
        return hints[:3]  # Limit to 3 hints maximum