"""
Learning Adaptation Service for adjusting pacing, content, and assessments based on user performance.

This service provides real-time adaptation of learning experiences by analyzing user
performance patterns and adjusting content delivery, pacing, and assessment difficulty.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..db.crud import analytics_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..db.models.db_course import Course, Chapter
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class PacingAdjustment:
    """Container for pacing adjustment recommendations."""
    
    def __init__(
        self,
        user_id: str,
        course_id: int,
        current_pace: float,
        recommended_pace: float,
        adjustment_factor: float,
        reason: str,
        confidence: float,
        next_review_date: datetime
    ):
        self.user_id = user_id
        self.course_id = course_id
        self.current_pace = current_pace
        self.recommended_pace = recommended_pace
        self.adjustment_factor = adjustment_factor
        self.reason = reason
        self.confidence = confidence
        self.next_review_date = next_review_date


class SupplementaryMaterial:
    """Container for supplementary content recommendations."""
    
    def __init__(
        self,
        material_id: str,
        title: str,
        content_type: str,
        difficulty_level: DifficultyLevel,
        estimated_time: int,
        relevance_score: float,
        reason: str,
        priority: int
    ):
        self.material_id = material_id
        self.title = title
        self.content_type = content_type
        self.difficulty_level = difficulty_level
        self.estimated_time = estimated_time
        self.relevance_score = relevance_score
        self.reason = reason
        self.priority = priority


class AssessmentModification:
    """Container for assessment difficulty modifications."""
    
    def __init__(
        self,
        assessment_id: str,
        original_difficulty: float,
        modified_difficulty: float,
        question_adjustments: Dict[str, Any],
        time_adjustments: Dict[str, Any],
        support_level: str,
        modification_reason: str
    ):
        self.assessment_id = assessment_id
        self.original_difficulty = original_difficulty
        self.modified_difficulty = modified_difficulty
        self.question_adjustments = question_adjustments
        self.time_adjustments = time_adjustments
        self.support_level = support_level
        self.modification_reason = modification_reason


class LearningAdaptationService:
    """Service for adapting learning experiences based on user performance."""
    
    def __init__(self):
        self.performance_window_days = 7  # Days to look back for performance analysis
        self.min_data_points = 3  # Minimum interactions needed for adaptation
        self.adaptation_confidence_threshold = 0.6  # Minimum confidence for adaptations
        
    async def adjust_pacing(
        self, 
        db: Session, 
        user_id: str, 
        course_id: int
    ) -> Optional[PacingAdjustment]:
        """
        Analyze user performance and recommend pacing adjustments.
        
        Args:
            db: Database session
            user_id: User ID to analyze
            course_id: Course ID to adjust pacing for
            
        Returns:
            PacingAdjustment or None if insufficient data
        """
        try:
            # Get user's learning profile
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if not user_profile:
                logger.info(f"No learning profile found for user {user_id}")
                return None
            
            # Get recent behavior data for the course
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=self.performance_window_days)
            
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=user_id,
                course_id=course_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if len(behavior_data) < self.min_data_points:
                logger.info(f"Insufficient behavior data for pacing adjustment: {len(behavior_data)}")
                return None
            
            # Analyze current performance patterns
            performance_metrics = self._analyze_performance_patterns(behavior_data)
            
            # Calculate current pace
            current_pace = self._calculate_current_pace(behavior_data, course_id, db)
            
            # Determine recommended pace adjustment
            recommended_pace, adjustment_factor, reason, confidence = self._calculate_pace_adjustment(
                performance_metrics, user_profile, current_pace
            )
            
            if confidence < self.adaptation_confidence_threshold:
                logger.info(f"Low confidence for pacing adjustment: {confidence}")
                return None
            
            # Calculate next review date
            next_review_date = end_date + timedelta(days=3)  # Review again in 3 days
            
            return PacingAdjustment(
                user_id=user_id,
                course_id=course_id,
                current_pace=current_pace,
                recommended_pace=recommended_pace,
                adjustment_factor=adjustment_factor,
                reason=reason,
                confidence=confidence,
                next_review_date=next_review_date
            )
            
        except Exception as e:
            logger.error(f"Error adjusting pacing for user {user_id}, course {course_id}: {str(e)}")
            return None
    
    async def provide_supplementary_content(
        self, 
        db: Session, 
        user_id: str, 
        topic: str,
        max_recommendations: int = 5
    ) -> List[SupplementaryMaterial]:
        """
        Recommend supplementary content based on user's learning gaps.
        
        Args:
            db: Database session
            user_id: User ID to provide recommendations for
            topic: Topic area to focus on
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of SupplementaryMaterial recommendations
        """
        try:
            # Get user's learning profile and patterns
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            learning_pattern = analytics_crud.get_learning_pattern_by_user(db, user_id)
            
            if not user_profile:
                logger.info(f"No learning profile found for user {user_id}")
                return []
            
            # Analyze learning gaps and struggles
            learning_gaps = self._identify_learning_gaps(db, user_id, topic)
            
            if not learning_gaps:
                logger.info(f"No learning gaps identified for user {user_id} in topic {topic}")
                return []
            
            # Generate supplementary material recommendations
            recommendations = []
            
            for gap in learning_gaps:
                materials = self._generate_supplementary_materials(
                    gap, user_profile, learning_pattern
                )
                recommendations.extend(materials)
            
            # Sort by relevance and priority
            recommendations.sort(key=lambda x: (x.priority, -x.relevance_score))
            
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error providing supplementary content for user {user_id}: {str(e)}")
            return []
    
    async def modify_assessment_difficulty(
        self, 
        db: Session, 
        user_id: str, 
        assessment_id: str,
        assessment_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AssessmentModification]:
        """
        Modify assessment difficulty based on user's current performance level.
        
        Args:
            db: Database session
            user_id: User ID to modify assessment for
            assessment_id: Assessment ID to modify
            assessment_metadata: Optional metadata about the assessment
            
        Returns:
            AssessmentModification or None if no modification needed
        """
        try:
            # Get user's learning profile
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if not user_profile:
                logger.info(f"No learning profile found for user {user_id}")
                return None
            
            # Get recent assessment performance
            recent_performance = self._get_recent_assessment_performance(db, user_id)
            
            # Get original assessment difficulty
            original_difficulty = 0.5  # Default
            if assessment_metadata and "difficulty" in assessment_metadata:
                original_difficulty = float(assessment_metadata["difficulty"])
            
            # Calculate modified difficulty
            modified_difficulty, modification_reason = self._calculate_assessment_difficulty(
                original_difficulty, user_profile, recent_performance
            )
            
            # Generate question adjustments
            question_adjustments = self._generate_question_adjustments(
                user_profile, original_difficulty, modified_difficulty
            )
            
            # Generate time adjustments
            time_adjustments = self._generate_time_adjustments(
                user_profile, recent_performance
            )
            
            # Determine support level
            support_level = self._determine_support_level(user_profile, recent_performance)
            
            # Only return modification if there's a significant change
            if abs(modified_difficulty - original_difficulty) < 0.1:
                return None  # No significant modification needed
            
            return AssessmentModification(
                assessment_id=assessment_id,
                original_difficulty=original_difficulty,
                modified_difficulty=modified_difficulty,
                question_adjustments=question_adjustments,
                time_adjustments=time_adjustments,
                support_level=support_level,
                modification_reason=modification_reason
            )
            
        except Exception as e:
            logger.error(f"Error modifying assessment {assessment_id} for user {user_id}: {str(e)}")
            return None
    
    def _analyze_performance_patterns(self, behavior_data: List[UserBehaviorData]) -> Dict[str, float]:
        """Analyze user performance patterns from behavior data."""
        
        metrics = {
            "completion_rate": 0.0,
            "average_time_per_activity": 0.0,
            "engagement_trend": 0.0,
            "struggle_indicators": 0.0,
            "consistency_score": 0.0
        }
        
        if not behavior_data:
            return metrics
        
        # Calculate completion rate
        start_events = len([d for d in behavior_data if d.event_type in [
            EventType.CHAPTER_START, EventType.ASSESSMENT_START
        ]])
        complete_events = len([d for d in behavior_data if d.event_type in [
            EventType.CHAPTER_COMPLETE, EventType.ASSESSMENT_COMPLETE
        ]])
        
        if start_events > 0:
            metrics["completion_rate"] = complete_events / start_events
        
        # Calculate average time per activity
        durations = [d.duration_seconds for d in behavior_data if d.duration_seconds]
        if durations:
            metrics["average_time_per_activity"] = sum(durations) / len(durations)
        
        # Calculate engagement trend (improvement over time)
        engagement_scores = [(d.timestamp, d.engagement_score) for d in behavior_data 
                           if d.engagement_score is not None]
        
        if len(engagement_scores) >= 2:
            engagement_scores.sort(key=lambda x: x[0])  # Sort by timestamp
            first_half = engagement_scores[:len(engagement_scores)//2]
            second_half = engagement_scores[len(engagement_scores)//2:]
            
            first_avg = sum(score for _, score in first_half) / len(first_half)
            second_avg = sum(score for _, score in second_half) / len(second_half)
            
            metrics["engagement_trend"] = second_avg - first_avg
        
        # Calculate struggle indicators (long times, low engagement)
        struggle_count = 0
        for data in behavior_data:
            if (data.duration_seconds and data.duration_seconds > 3600) or \
               (data.engagement_score and data.engagement_score < 0.3):
                struggle_count += 1
        
        metrics["struggle_indicators"] = struggle_count / len(behavior_data)
        
        # Calculate consistency (regular activity)
        daily_activity = {}
        for data in behavior_data:
            day = data.timestamp.date()
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
        if len(daily_activity) > 1:
            activities = list(daily_activity.values())
            mean_activity = sum(activities) / len(activities)
            if mean_activity > 0:
                variance = sum((x - mean_activity) ** 2 for x in activities) / len(activities)
                cv = (variance ** 0.5) / mean_activity
                metrics["consistency_score"] = max(0.0, 1.0 - cv)
        
        return metrics
    
    def _calculate_current_pace(
        self, 
        behavior_data: List[UserBehaviorData], 
        course_id: int, 
        db: Session
    ) -> float:
        """Calculate user's current learning pace for the course."""
        
        # Get course chapters to calculate expected pace
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return 1.0  # Default pace
            
            chapters = db.query(Chapter).filter(Chapter.course_id == course_id).count()
            if chapters == 0:
                return 1.0
            
            # Calculate chapters completed in the time period
            completed_chapters = len(set(
                d.chapter_id for d in behavior_data 
                if d.event_type == EventType.CHAPTER_COMPLETE and d.chapter_id
            ))
            
            # Calculate time span
            if len(behavior_data) < 2:
                return 1.0
            
            timestamps = [d.timestamp for d in behavior_data]
            time_span_days = (max(timestamps) - min(timestamps)).days + 1
            
            # Calculate pace (chapters per day)
            if time_span_days > 0:
                current_pace = completed_chapters / time_span_days
                # Normalize to expected pace (assume 1 chapter per 2 days as baseline)
                expected_pace = 0.5
                return current_pace / expected_pace if expected_pace > 0 else 1.0
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error calculating current pace: {str(e)}")
            return 1.0
    
    def _calculate_pace_adjustment(
        self, 
        performance_metrics: Dict[str, float], 
        user_profile: UserLearningProfile,
        current_pace: float
    ) -> Tuple[float, float, str, float]:
        """Calculate recommended pace adjustment."""
        
        # Base recommendation on performance metrics
        completion_rate = performance_metrics["completion_rate"]
        engagement_trend = performance_metrics["engagement_trend"]
        struggle_indicators = performance_metrics["struggle_indicators"]
        consistency_score = performance_metrics["consistency_score"]
        
        # Calculate adjustment factor
        adjustment_factor = 1.0
        reasons = []
        
        # Adjust based on completion rate
        if completion_rate > 0.8:
            adjustment_factor *= 1.2  # Speed up for high performers
            reasons.append("high completion rate")
        elif completion_rate < 0.4:
            adjustment_factor *= 0.8  # Slow down for struggling learners
            reasons.append("low completion rate")
        
        # Adjust based on engagement trend
        if engagement_trend > 0.1:
            adjustment_factor *= 1.1  # Speed up if engagement is improving
            reasons.append("improving engagement")
        elif engagement_trend < -0.1:
            adjustment_factor *= 0.9  # Slow down if engagement is declining
            reasons.append("declining engagement")
        
        # Adjust based on struggle indicators
        if struggle_indicators > 0.3:
            adjustment_factor *= 0.8  # Slow down if showing struggle
            reasons.append("signs of difficulty")
        
        # Adjust based on consistency
        if consistency_score > 0.7:
            adjustment_factor *= 1.05  # Slightly faster for consistent learners
            reasons.append("consistent learning pattern")
        elif consistency_score < 0.3:
            adjustment_factor *= 0.95  # Slightly slower for inconsistent learners
            reasons.append("inconsistent learning pattern")
        
        # Consider user profile factors
        if user_profile.challenge_preference > 0.7:
            adjustment_factor *= 1.1  # Faster for those who like challenges
            reasons.append("prefers challenges")
        elif user_profile.challenge_preference < 0.3:
            adjustment_factor *= 0.9  # Slower for those who prefer easier content
            reasons.append("prefers easier pace")
        
        # Calculate recommended pace
        recommended_pace = current_pace * adjustment_factor
        
        # Generate reason string
        reason = f"Recommended based on: {', '.join(reasons)}" if reasons else "Maintaining current pace"
        
        # Calculate confidence based on data quality
        confidence = min(1.0, (
            (1.0 if completion_rate > 0 else 0.0) * 0.3 +
            (1.0 if abs(engagement_trend) > 0.05 else 0.5) * 0.3 +
            (1.0 if consistency_score > 0.5 else 0.5) * 0.2 +
            (1.0 if user_profile.engagement_score > 0.5 else 0.5) * 0.2
        ))
        
        return recommended_pace, adjustment_factor, reason, confidence
    
    def _identify_learning_gaps(
        self, 
        db: Session, 
        user_id: str, 
        topic: str
    ) -> List[Dict[str, Any]]:
        """Identify learning gaps for a user in a specific topic."""
        
        gaps = []
        
        try:
            # Get user's challenging topics from learning profile
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if user_profile and user_profile.challenging_topics:
                for challenging_topic in user_profile.challenging_topics:
                    if topic.lower() in challenging_topic.lower() or challenging_topic.lower() in topic.lower():
                        gaps.append({
                            "topic": challenging_topic,
                            "gap_type": "challenging_topic",
                            "severity": "high",
                            "evidence": "identified from learning patterns"
                        })
            
            # Analyze recent poor performance in assessments
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=14)  # Last 2 weeks
            
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Look for incomplete assessments or chapters
            incomplete_assessments = [
                d for d in behavior_data 
                if d.event_type == EventType.ASSESSMENT_START
            ]
            
            completed_assessments = [
                d for d in behavior_data 
                if d.event_type == EventType.ASSESSMENT_COMPLETE
            ]
            
            if len(incomplete_assessments) > len(completed_assessments):
                gaps.append({
                    "topic": topic,
                    "gap_type": "assessment_completion",
                    "severity": "medium",
                    "evidence": f"{len(incomplete_assessments) - len(completed_assessments)} incomplete assessments"
                })
            
            # Look for excessive time spent on content
            long_duration_events = [
                d for d in behavior_data 
                if d.duration_seconds and d.duration_seconds > 3600  # More than 1 hour
            ]
            
            if len(long_duration_events) > len(behavior_data) * 0.3:  # More than 30% of events
                gaps.append({
                    "topic": topic,
                    "gap_type": "time_management",
                    "severity": "medium",
                    "evidence": "excessive time spent on content"
                })
            
        except Exception as e:
            logger.error(f"Error identifying learning gaps: {str(e)}")
        
        return gaps
    
    def _generate_supplementary_materials(
        self, 
        gap: Dict[str, Any], 
        user_profile: UserLearningProfile,
        learning_pattern: Optional[LearningPattern]
    ) -> List[SupplementaryMaterial]:
        """Generate supplementary material recommendations for a learning gap."""
        
        materials = []
        gap_type = gap["gap_type"]
        topic = gap["topic"]
        severity = gap["severity"]
        
        # Determine priority based on severity
        priority = {"high": 1, "medium": 2, "low": 3}.get(severity, 3)
        
        # Generate materials based on gap type and learning style
        if gap_type == "challenging_topic":
            # Provide foundational materials
            materials.extend([
                SupplementaryMaterial(
                    material_id=f"foundation_{topic}_{generate_analytics_id()}",
                    title=f"Foundations of {topic}",
                    content_type="tutorial",
                    difficulty_level=DifficultyLevel.BEGINNER,
                    estimated_time=30,
                    relevance_score=0.9,
                    reason="Strengthen foundational understanding",
                    priority=priority
                ),
                SupplementaryMaterial(
                    material_id=f"practice_{topic}_{generate_analytics_id()}",
                    title=f"Practice Exercises: {topic}",
                    content_type="exercises",
                    difficulty_level=DifficultyLevel.BEGINNER,
                    estimated_time=45,
                    relevance_score=0.8,
                    reason="Build confidence through practice",
                    priority=priority
                )
            ])
        
        elif gap_type == "assessment_completion":
            # Provide assessment preparation materials
            materials.append(
                SupplementaryMaterial(
                    material_id=f"assessment_prep_{topic}_{generate_analytics_id()}",
                    title=f"Assessment Preparation: {topic}",
                    content_type="study_guide",
                    difficulty_level=user_profile.preferred_difficulty,
                    estimated_time=20,
                    relevance_score=0.85,
                    reason="Improve assessment completion rate",
                    priority=priority
                )
            )
        
        elif gap_type == "time_management":
            # Provide structured learning materials
            materials.append(
                SupplementaryMaterial(
                    material_id=f"structured_{topic}_{generate_analytics_id()}",
                    title=f"Structured Learning Path: {topic}",
                    content_type="guided_path",
                    difficulty_level=user_profile.preferred_difficulty,
                    estimated_time=user_profile.attention_span or 30,
                    relevance_score=0.75,
                    reason="Improve learning efficiency",
                    priority=priority
                )
            )
        
        # Adapt materials based on learning style
        if user_profile.learning_style == LearningStyleType.VISUAL:
            for material in materials:
                if material.content_type == "tutorial":
                    material.content_type = "video_tutorial"
                    material.title = f"Visual Guide: {material.title}"
        
        elif user_profile.learning_style == LearningStyleType.KINESTHETIC:
            for material in materials:
                if material.content_type == "exercises":
                    material.content_type = "interactive_exercises"
                    material.title = f"Interactive {material.title}"
        
        return materials
    
    def _get_recent_assessment_performance(
        self, 
        db: Session, 
        user_id: str
    ) -> Dict[str, float]:
        """Get user's recent assessment performance metrics."""
        
        performance = {
            "average_score": 0.5,
            "completion_rate": 0.5,
            "average_time_ratio": 1.0,
            "trend": 0.0
        }
        
        try:
            # Get recent assessment events
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=14)
            
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            assessment_starts = [
                d for d in behavior_data 
                if d.event_type == EventType.ASSESSMENT_START
            ]
            
            assessment_completes = [
                d for d in behavior_data 
                if d.event_type == EventType.ASSESSMENT_COMPLETE
            ]
            
            if assessment_starts:
                performance["completion_rate"] = len(assessment_completes) / len(assessment_starts)
            
            # Calculate average engagement as proxy for performance
            if assessment_completes:
                engagement_scores = [
                    d.engagement_score for d in assessment_completes 
                    if d.engagement_score is not None
                ]
                if engagement_scores:
                    performance["average_score"] = sum(engagement_scores) / len(engagement_scores)
            
            # Calculate trend (improvement over time)
            if len(assessment_completes) >= 4:
                assessment_completes.sort(key=lambda x: x.timestamp)
                first_half = assessment_completes[:len(assessment_completes)//2]
                second_half = assessment_completes[len(assessment_completes)//2:]
                
                first_avg = sum(d.engagement_score or 0.5 for d in first_half) / len(first_half)
                second_avg = sum(d.engagement_score or 0.5 for d in second_half) / len(second_half)
                
                performance["trend"] = second_avg - first_avg
            
        except Exception as e:
            logger.error(f"Error getting assessment performance: {str(e)}")
        
        return performance
    
    def _calculate_assessment_difficulty(
        self, 
        original_difficulty: float, 
        user_profile: UserLearningProfile,
        recent_performance: Dict[str, float]
    ) -> Tuple[float, str]:
        """Calculate modified assessment difficulty."""
        
        modified_difficulty = original_difficulty
        reasons = []
        
        # Adjust based on recent performance
        avg_score = recent_performance["average_score"]
        completion_rate = recent_performance["completion_rate"]
        trend = recent_performance["trend"]
        
        # Performance-based adjustments
        if avg_score > 0.8 and completion_rate > 0.8:
            modified_difficulty = min(0.9, original_difficulty + 0.1)
            reasons.append("strong recent performance")
        elif avg_score < 0.4 or completion_rate < 0.5:
            modified_difficulty = max(0.1, original_difficulty - 0.15)
            reasons.append("struggling with assessments")
        
        # Trend-based adjustments
        if trend > 0.1:
            modified_difficulty = min(0.9, modified_difficulty + 0.05)
            reasons.append("improving performance")
        elif trend < -0.1:
            modified_difficulty = max(0.1, modified_difficulty - 0.1)
            reasons.append("declining performance")
        
        # Profile-based adjustments
        if user_profile.challenge_preference > 0.7:
            modified_difficulty = min(0.9, modified_difficulty + 0.05)
            reasons.append("prefers challenges")
        elif user_profile.challenge_preference < 0.3:
            modified_difficulty = max(0.1, modified_difficulty - 0.05)
            reasons.append("prefers easier content")
        
        reason = f"Adjusted based on: {', '.join(reasons)}" if reasons else "No adjustment needed"
        
        return modified_difficulty, reason
    
    def _generate_question_adjustments(
        self, 
        user_profile: UserLearningProfile, 
        original_difficulty: float,
        modified_difficulty: float
    ) -> Dict[str, Any]:
        """Generate question-level adjustments for assessments."""
        
        adjustments = {}
        
        difficulty_change = modified_difficulty - original_difficulty
        
        if difficulty_change > 0.1:  # Making it harder
            adjustments.update({
                "add_complex_scenarios": True,
                "reduce_hints": True,
                "add_multi_step_problems": True,
                "increase_analysis_questions": True
            })
        elif difficulty_change < -0.1:  # Making it easier
            adjustments.update({
                "add_hints": True,
                "break_down_complex_questions": True,
                "add_multiple_choice": True,
                "provide_examples": True
            })
        
        # Learning style adjustments
        if user_profile.learning_style == LearningStyleType.VISUAL:
            adjustments.update({
                "add_diagrams": True,
                "use_visual_questions": True,
                "include_charts": True
            })
        elif user_profile.learning_style == LearningStyleType.KINESTHETIC:
            adjustments.update({
                "add_practical_scenarios": True,
                "include_hands_on_problems": True,
                "use_real_world_examples": True
            })
        
        return adjustments
    
    def _generate_time_adjustments(
        self, 
        user_profile: UserLearningProfile,
        recent_performance: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate time-related adjustments for assessments."""
        
        adjustments = {
            "time_multiplier": 1.0,
            "allow_breaks": False,
            "provide_time_warnings": False
        }
        
        # Adjust based on attention span
        if user_profile.attention_span and user_profile.attention_span < 30:
            adjustments.update({
                "time_multiplier": 1.2,
                "allow_breaks": True,
                "provide_time_warnings": True
            })
        
        # Adjust based on recent performance
        completion_rate = recent_performance["completion_rate"]
        if completion_rate < 0.6:
            adjustments["time_multiplier"] = max(1.0, adjustments["time_multiplier"] * 1.3)
            adjustments["provide_time_warnings"] = True
        
        return adjustments
    
    def _determine_support_level(
        self, 
        user_profile: UserLearningProfile,
        recent_performance: Dict[str, float]
    ) -> str:
        """Determine level of support to provide during assessment."""
        
        avg_score = recent_performance["average_score"]
        completion_rate = recent_performance["completion_rate"]
        
        if avg_score < 0.4 or completion_rate < 0.5:
            return "high"  # Provide hints, examples, guidance
        elif avg_score < 0.6 or completion_rate < 0.7:
            return "medium"  # Provide some hints and encouragement
        else:
            return "low"  # Minimal support, let them work independently