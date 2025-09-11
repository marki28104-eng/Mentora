"""
Personalization Engine Service for generating user learning profiles and adapting content.

This service analyzes user behavior data and learning patterns to create personalized
learning experiences, adapt content difficulty, and recommend learning paths.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..db.crud import analytics_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..db.models.db_course import Course, Chapter
from ..api.schemas.analytics import (
    UserLearningProfileCreate, UserLearningProfileUpdate,
    DifficultyLevelSchema, LearningStyleSchema
)
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class AdaptedContent:
    """Container for adapted content based on user profile."""
    
    def __init__(
        self,
        content_id: str,
        original_difficulty: float,
        adapted_difficulty: float,
        content_modifications: Dict[str, Any],
        explanation_style: str,
        pacing_adjustment: float
    ):
        self.content_id = content_id
        self.original_difficulty = original_difficulty
        self.adapted_difficulty = adapted_difficulty
        self.content_modifications = content_modifications
        self.explanation_style = explanation_style
        self.pacing_adjustment = pacing_adjustment


class CourseRecommendation:
    """Container for course recommendations."""
    
    def __init__(
        self,
        course_id: int,
        title: str,
        recommendation_score: float,
        reason: str,
        recommended_difficulty: DifficultyLevel,
        estimated_completion_time: int,
        topic_match_score: float,
        learning_style_match: float
    ):
        self.course_id = course_id
        self.title = title
        self.recommendation_score = recommendation_score
        self.reason = reason
        self.recommended_difficulty = recommended_difficulty
        self.estimated_completion_time = estimated_completion_time
        self.topic_match_score = topic_match_score
        self.learning_style_match = learning_style_match


class PersonalizationEngine:
    """Service for generating personalized learning experiences."""
    
    def __init__(self):
        self.min_data_points = 5  # Minimum behavior data points needed for personalization
        self.confidence_threshold = 0.6  # Minimum confidence for pattern-based decisions
        
    async def generate_user_profile(self, db: Session, user_id: str) -> Optional[UserLearningProfile]:
        """
        Generate or update a comprehensive user learning profile.
        
        Args:
            db: Database session
            user_id: User ID to generate profile for
            
        Returns:
            UserLearningProfile or None if insufficient data
        """
        try:
            # Get existing profile if it exists
            existing_profile = analytics_crud.get_user_learning_profile(db, user_id)
            
            # Get user's learning patterns
            learning_pattern = analytics_crud.get_learning_pattern_by_user(db, user_id)
            
            # Get recent engagement metrics (last 30 days)
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=30)
            
            engagement_metrics = analytics_crud.get_engagement_metrics(
                db=db,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get user behavior data for analysis
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                limit=500
            )
            
            if len(behavior_data) < self.min_data_points:
                logger.info(f"Insufficient data points for user {user_id}: {len(behavior_data)}")
                return existing_profile  # Return existing profile or None
            
            # Calculate profile metrics
            profile_data = self._calculate_profile_metrics(
                behavior_data, learning_pattern, engagement_metrics
            )
            
            if existing_profile:
                # Update existing profile
                update_data = UserLearningProfileUpdate(**profile_data)
                return analytics_crud.update_user_learning_profile(db, existing_profile, update_data.model_dump(exclude_unset=True))
            else:
                # Create new profile
                profile_create = UserLearningProfileCreate(user_id=user_id, **profile_data)
                return analytics_crud.create_user_learning_profile(db, profile_create)
                
        except Exception as e:
            logger.error(f"Error generating user profile for {user_id}: {str(e)}")
            return None
    
    async def adapt_content_difficulty(
        self, 
        db: Session,
        content_id: str, 
        user_profile: UserLearningProfile,
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> AdaptedContent:
        """
        Adapt content difficulty based on user learning profile.
        
        Args:
            db: Database session
            content_id: ID of the content to adapt
            user_profile: User's learning profile
            content_metadata: Optional metadata about the content
            
        Returns:
            AdaptedContent with difficulty adjustments
        """
        try:
            # Get content's original difficulty (default to 0.5 if not specified)
            original_difficulty = 0.5
            if content_metadata and "difficulty" in content_metadata:
                original_difficulty = float(content_metadata["difficulty"])
            
            # Calculate adapted difficulty based on user profile
            adapted_difficulty = self._calculate_adapted_difficulty(
                original_difficulty, user_profile
            )
            
            # Determine content modifications based on learning style
            content_modifications = self._generate_content_modifications(
                user_profile, content_metadata
            )
            
            # Determine explanation style
            explanation_style = self._determine_explanation_style(user_profile)
            
            # Calculate pacing adjustment
            pacing_adjustment = self._calculate_pacing_adjustment(user_profile)
            
            return AdaptedContent(
                content_id=content_id,
                original_difficulty=original_difficulty,
                adapted_difficulty=adapted_difficulty,
                content_modifications=content_modifications,
                explanation_style=explanation_style,
                pacing_adjustment=pacing_adjustment
            )
            
        except Exception as e:
            logger.error(f"Error adapting content {content_id}: {str(e)}")
            # Return default adaptation on error
            return AdaptedContent(
                content_id=content_id,
                original_difficulty=0.5,
                adapted_difficulty=0.5,
                content_modifications={},
                explanation_style="balanced",
                pacing_adjustment=1.0
            )
    
    async def recommend_learning_path(
        self, 
        db: Session,
        user_id: str, 
        topic: str,
        max_recommendations: int = 5
    ) -> List[CourseRecommendation]:
        """
        Recommend learning path based on user profile and topic interest.
        
        Args:
            db: Database session
            user_id: User ID to generate recommendations for
            topic: Topic of interest
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of CourseRecommendation objects
        """
        try:
            # Get user profile
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if not user_profile:
                # Generate profile if it doesn't exist
                user_profile = await self.generate_user_profile(db, user_id)
                if not user_profile:
                    return []  # Can't recommend without profile
            
            # Get available courses related to the topic
            courses = self._get_courses_by_topic(db, topic)
            
            if not courses:
                logger.info(f"No courses found for topic: {topic}")
                return []
            
            # Score and rank courses
            recommendations = []
            
            for course in courses:
                recommendation_score = self._calculate_course_recommendation_score(
                    course, user_profile, topic
                )
                
                if recommendation_score > 0.3:  # Minimum threshold
                    # Determine recommended difficulty for this user
                    recommended_difficulty = self._determine_recommended_difficulty(
                        course, user_profile
                    )
                    
                    # Estimate completion time
                    estimated_time = self._estimate_completion_time(
                        course, user_profile
                    )
                    
                    # Generate recommendation reason
                    reason = self._generate_recommendation_reason(
                        course, user_profile, recommendation_score
                    )
                    
                    # Calculate component scores for transparency
                    topic_match_score = self._calculate_topic_match_score(course, topic)
                    learning_style_match = self._calculate_learning_style_match(
                        course, user_profile
                    )
                    
                    recommendation = CourseRecommendation(
                        course_id=course.id,
                        title=course.title,
                        recommendation_score=recommendation_score,
                        reason=reason,
                        recommended_difficulty=recommended_difficulty,
                        estimated_completion_time=estimated_time,
                        topic_match_score=topic_match_score,
                        learning_style_match=learning_style_match
                    )
                    
                    recommendations.append(recommendation)
            
            # Sort by recommendation score and return top results
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating learning path recommendations: {str(e)}")
            return []
    
    def _calculate_profile_metrics(
        self,
        behavior_data: List[UserBehaviorData],
        learning_pattern: Optional[LearningPattern],
        engagement_metrics: List[EngagementMetrics]
    ) -> Dict[str, Any]:
        """Calculate metrics for user learning profile."""
        
        # Calculate completion rate
        completion_events = len([
            data for data in behavior_data 
            if data.event_type in [EventType.COURSE_COMPLETE, EventType.CHAPTER_COMPLETE]
        ])
        start_events = len([
            data for data in behavior_data 
            if data.event_type in [EventType.COURSE_START, EventType.CHAPTER_START]
        ])
        completion_rate = completion_events / start_events if start_events > 0 else 0.0
        
        # Calculate average session duration
        session_durations = {}
        for data in behavior_data:
            if data.session_id not in session_durations:
                session_durations[data.session_id] = []
            session_durations[data.session_id].append(data.timestamp)
        
        avg_session_duration = None
        if session_durations:
            durations = []
            for session_id, timestamps in session_durations.items():
                if len(timestamps) > 1:
                    timestamps.sort()
                    duration = (timestamps[-1] - timestamps[0]).total_seconds() / 60
                    if 5 <= duration <= 240:  # 5 minutes to 4 hours
                        durations.append(duration)
            
            if durations:
                avg_session_duration = int(sum(durations) / len(durations))
        
        # Calculate total learning time
        total_learning_time = sum(
            (data.duration_seconds or 0) for data in behavior_data
        ) // 60  # Convert to minutes
        
        # Count completed courses
        courses_completed = len(set(
            data.course_id for data in behavior_data 
            if data.event_type == EventType.COURSE_COMPLETE and data.course_id
        ))
        
        # Calculate engagement score
        engagement_score = 0.0
        if engagement_metrics:
            engagement_score = sum(m.engagement_score for m in engagement_metrics) / len(engagement_metrics)
        
        # Calculate consistency score (based on regular learning activity)
        consistency_score = self._calculate_consistency_score(behavior_data)
        
        # Determine learning style and difficulty preference
        learning_style = LearningStyleType.UNKNOWN
        preferred_difficulty = DifficultyLevel.BEGINNER
        attention_span = None
        strong_topics = None
        challenging_topics = None
        
        if learning_pattern and learning_pattern.confidence_score >= self.confidence_threshold:
            learning_style = learning_pattern.pattern_type
            attention_span = learning_pattern.average_attention_span
            strong_topics = learning_pattern.strong_topics
            challenging_topics = learning_pattern.challenging_topics
        
        # Determine preferred difficulty based on performance
        if completion_rate >= 0.8:
            preferred_difficulty = DifficultyLevel.ADVANCED
        elif completion_rate >= 0.6:
            preferred_difficulty = DifficultyLevel.INTERMEDIATE
        
        # Calculate challenge preference (0.0 = prefers easy, 1.0 = prefers hard)
        challenge_preference = min(1.0, completion_rate + (engagement_score * 0.3))
        
        # Calculate current difficulty level
        current_difficulty_level = min(1.0, (completion_rate * 0.7) + (engagement_score * 0.3))
        
        return {
            "learning_style": learning_style,
            "attention_span": attention_span,
            "preferred_difficulty": preferred_difficulty,
            "completion_rate": completion_rate,
            "average_session_duration": avg_session_duration,
            "total_learning_time": total_learning_time,
            "courses_completed": courses_completed,
            "engagement_score": engagement_score,
            "consistency_score": consistency_score,
            "challenge_preference": challenge_preference,
            "strong_topics": strong_topics,
            "challenging_topics": challenging_topics,
            "current_difficulty_level": current_difficulty_level,
            "adaptation_rate": 0.1  # Default adaptation rate
        }
    
    def _calculate_consistency_score(self, behavior_data: List[UserBehaviorData]) -> float:
        """Calculate consistency score based on learning activity patterns."""
        if len(behavior_data) < 7:  # Need at least a week of data
            return 0.0
        
        # Group activities by day
        daily_activity = {}
        for data in behavior_data:
            day = data.timestamp.date()
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
        if len(daily_activity) < 3:  # Need at least 3 days of activity
            return 0.0
        
        # Calculate coefficient of variation (lower = more consistent)
        activities = list(daily_activity.values())
        mean_activity = sum(activities) / len(activities)
        
        if mean_activity == 0:
            return 0.0
        
        variance = sum((x - mean_activity) ** 2 for x in activities) / len(activities)
        std_dev = variance ** 0.5
        cv = std_dev / mean_activity
        
        # Convert to consistency score (0-1, higher = more consistent)
        consistency_score = max(0.0, 1.0 - (cv / 2.0))
        return min(1.0, consistency_score)
    
    def _calculate_adapted_difficulty(
        self, 
        original_difficulty: float, 
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate adapted difficulty based on user profile."""
        
        # Base adaptation on current difficulty level and challenge preference
        target_difficulty = (
            user_profile.current_difficulty_level * 0.7 +
            user_profile.challenge_preference * 0.3
        )
        
        # Apply adaptation rate to gradually move toward target
        adaptation_rate = user_profile.adaptation_rate
        adapted_difficulty = (
            original_difficulty * (1 - adaptation_rate) +
            target_difficulty * adaptation_rate
        )
        
        # Ensure difficulty stays within reasonable bounds
        return max(0.1, min(0.9, adapted_difficulty))
    
    def _generate_content_modifications(
        self, 
        user_profile: UserLearningProfile,
        content_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate content modifications based on learning style."""
        
        modifications = {}
        
        # Modifications based on learning style
        if user_profile.learning_style == LearningStyleType.VISUAL:
            modifications.update({
                "include_diagrams": True,
                "include_charts": True,
                "visual_examples": True,
                "color_coding": True
            })
        elif user_profile.learning_style == LearningStyleType.AUDITORY:
            modifications.update({
                "include_audio": True,
                "verbal_explanations": True,
                "discussion_prompts": True
            })
        elif user_profile.learning_style == LearningStyleType.KINESTHETIC:
            modifications.update({
                "interactive_elements": True,
                "hands_on_exercises": True,
                "practical_examples": True,
                "step_by_step_guidance": True
            })
        elif user_profile.learning_style == LearningStyleType.READING:
            modifications.update({
                "detailed_text": True,
                "comprehensive_explanations": True,
                "reference_materials": True,
                "written_examples": True
            })
        
        # Modifications based on attention span
        if user_profile.attention_span and user_profile.attention_span < 20:
            modifications.update({
                "break_into_chunks": True,
                "frequent_checkpoints": True,
                "shorter_sections": True
            })
        elif user_profile.attention_span and user_profile.attention_span > 60:
            modifications.update({
                "longer_sections": True,
                "deep_dive_content": True,
                "comprehensive_coverage": True
            })
        
        # Modifications based on challenge preference
        if user_profile.challenge_preference > 0.7:
            modifications.update({
                "advanced_examples": True,
                "challenging_exercises": True,
                "bonus_content": True
            })
        elif user_profile.challenge_preference < 0.3:
            modifications.update({
                "simplified_explanations": True,
                "basic_examples": True,
                "guided_practice": True
            })
        
        return modifications
    
    def _determine_explanation_style(self, user_profile: UserLearningProfile) -> str:
        """Determine explanation style based on user profile."""
        
        if user_profile.learning_style == LearningStyleType.VISUAL:
            return "visual"
        elif user_profile.learning_style == LearningStyleType.AUDITORY:
            return "conversational"
        elif user_profile.learning_style == LearningStyleType.KINESTHETIC:
            return "practical"
        elif user_profile.learning_style == LearningStyleType.READING:
            return "detailed"
        else:
            return "balanced"
    
    def _calculate_pacing_adjustment(self, user_profile: UserLearningProfile) -> float:
        """Calculate pacing adjustment factor."""
        
        # Base pacing on completion rate and engagement
        base_pacing = 1.0
        
        # Adjust based on completion rate
        if user_profile.completion_rate > 0.8:
            base_pacing *= 1.2  # Speed up for high performers
        elif user_profile.completion_rate < 0.4:
            base_pacing *= 0.8  # Slow down for struggling learners
        
        # Adjust based on engagement score
        if user_profile.engagement_score > 0.7:
            base_pacing *= 1.1  # Slightly faster for engaged learners
        elif user_profile.engagement_score < 0.3:
            base_pacing *= 0.9  # Slightly slower for disengaged learners
        
        # Adjust based on attention span
        if user_profile.attention_span:
            if user_profile.attention_span < 20:
                base_pacing *= 0.9  # Slower for short attention spans
            elif user_profile.attention_span > 60:
                base_pacing *= 1.1  # Faster for long attention spans
        
        return max(0.5, min(2.0, base_pacing))  # Keep within reasonable bounds
    
    def _get_courses_by_topic(self, db: Session, topic: str) -> List[Course]:
        """Get courses related to a specific topic."""
        try:
            # Simple text search in course titles and descriptions
            # In a real implementation, this would use more sophisticated search/tagging
            courses = db.query(Course).filter(
                or_(
                    Course.title.ilike(f"%{topic}%"),
                    Course.description.ilike(f"%{topic}%")
                )
            ).limit(20).all()
            
            return courses
        except Exception as e:
            logger.error(f"Error fetching courses by topic {topic}: {str(e)}")
            return []
    
    def _calculate_course_recommendation_score(
        self, 
        course: Course, 
        user_profile: UserLearningProfile, 
        topic: str
    ) -> float:
        """Calculate recommendation score for a course."""
        
        score = 0.0
        
        # Topic relevance (40% of score)
        topic_score = self._calculate_topic_match_score(course, topic)
        score += topic_score * 0.4
        
        # Learning style match (25% of score)
        style_score = self._calculate_learning_style_match(course, user_profile)
        score += style_score * 0.25
        
        # Difficulty appropriateness (20% of score)
        difficulty_score = self._calculate_difficulty_match_score(course, user_profile)
        score += difficulty_score * 0.2
        
        # User's topic strength/weakness (15% of score)
        topic_performance_score = self._calculate_topic_performance_score(
            course, user_profile
        )
        score += topic_performance_score * 0.15
        
        return min(1.0, max(0.0, score))
    
    def _calculate_topic_match_score(self, course: Course, topic: str) -> float:
        """Calculate how well a course matches the requested topic."""
        
        # Simple keyword matching - in practice, this would use NLP/embeddings
        topic_lower = topic.lower()
        title_lower = course.title.lower()
        desc_lower = (course.description or "").lower()
        
        score = 0.0
        
        # Exact match in title
        if topic_lower in title_lower:
            score += 0.8
        
        # Partial match in title
        topic_words = topic_lower.split()
        title_words = title_lower.split()
        matching_words = len(set(topic_words) & set(title_words))
        if matching_words > 0:
            score += (matching_words / len(topic_words)) * 0.4
        
        # Match in description
        if topic_lower in desc_lower:
            score += 0.3
        
        return min(1.0, score)
    
    def _calculate_learning_style_match(
        self, 
        course: Course, 
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate how well a course matches the user's learning style."""
        
        # This would analyze course content types, format, etc.
        # For now, return a default score
        return 0.7  # Default moderate match
    
    def _calculate_difficulty_match_score(
        self, 
        course: Course, 
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate how well course difficulty matches user's level."""
        
        # Get course difficulty (would be stored in course metadata)
        # For now, assume intermediate difficulty
        course_difficulty = 0.5  # Default to intermediate
        
        # Compare with user's preferred difficulty level
        user_difficulty = user_profile.current_difficulty_level
        
        # Calculate match score (closer = higher score)
        diff = abs(course_difficulty - user_difficulty)
        score = 1.0 - diff
        
        return max(0.0, score)
    
    def _calculate_topic_performance_score(
        self, 
        course: Course, 
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate score based on user's performance in related topics."""
        
        # Check if course topic is in user's strong or challenging topics
        course_topic = course.title.lower()  # Simplified topic extraction
        
        if user_profile.strong_topics:
            for strong_topic in user_profile.strong_topics:
                if strong_topic.lower() in course_topic:
                    return 0.8  # High score for strong topics
        
        if user_profile.challenging_topics:
            for challenging_topic in user_profile.challenging_topics:
                if challenging_topic.lower() in course_topic:
                    return 0.9  # Even higher score for improvement opportunities
        
        return 0.5  # Neutral score for unknown topics
    
    def _determine_recommended_difficulty(
        self, 
        course: Course, 
        user_profile: UserLearningProfile
    ) -> DifficultyLevel:
        """Determine recommended difficulty level for the user."""
        
        if user_profile.current_difficulty_level >= 0.7:
            return DifficultyLevel.ADVANCED
        elif user_profile.current_difficulty_level >= 0.4:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _estimate_completion_time(
        self, 
        course: Course, 
        user_profile: UserLearningProfile
    ) -> int:
        """Estimate completion time in minutes for the user."""
        
        # Base estimate (would come from course metadata)
        base_time = 120  # Default 2 hours
        
        # Adjust based on user's average session duration and pacing
        if user_profile.average_session_duration:
            # Estimate number of sessions needed
            sessions_needed = base_time / user_profile.average_session_duration
            
            # Adjust for user's completion rate (lower rate = more time needed)
            if user_profile.completion_rate > 0:
                adjusted_time = base_time / user_profile.completion_rate
            else:
                adjusted_time = base_time * 1.5  # Add 50% for new users
            
            return int(min(adjusted_time, base_time * 3))  # Cap at 3x base time
        
        return base_time
    
    def _generate_recommendation_reason(
        self, 
        course: Course, 
        user_profile: UserLearningProfile, 
        score: float
    ) -> str:
        """Generate human-readable reason for recommendation."""
        
        reasons = []
        
        if score > 0.8:
            reasons.append("Excellent match for your learning profile")
        elif score > 0.6:
            reasons.append("Good match for your interests and skill level")
        else:
            reasons.append("Suitable for expanding your knowledge")
        
        if user_profile.learning_style != LearningStyleType.UNKNOWN:
            style_name = user_profile.learning_style.value
            reasons.append(f"Designed for {style_name} learners")
        
        if user_profile.completion_rate > 0.7:
            reasons.append("Matches your high performance level")
        elif user_profile.completion_rate < 0.4:
            reasons.append("Structured to support steady progress")
        
        return ". ".join(reasons)