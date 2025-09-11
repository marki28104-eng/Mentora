"""
Course Recommendation Service for providing personalized course suggestions.

This service implements advanced recommendation algorithms including collaborative filtering
and content-based filtering to suggest relevant courses based on user learning patterns.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from collections import defaultdict
import math

from ..db.crud import analytics_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..db.models.db_course import Course, Chapter
from ..db.models.db_user import User
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class CourseRecommendation:
    """Enhanced course recommendation with detailed scoring."""
    
    def __init__(
        self,
        course_id: int,
        title: str,
        description: str,
        recommendation_score: float,
        content_based_score: float,
        collaborative_score: float,
        popularity_score: float,
        difficulty_match_score: float,
        learning_style_match_score: float,
        reason: str,
        recommended_difficulty: DifficultyLevel,
        estimated_completion_time: int,
        similar_users: List[str] = None,
        tags: List[str] = None
    ):
        self.course_id = course_id
        self.title = title
        self.description = description
        self.recommendation_score = recommendation_score
        self.content_based_score = content_based_score
        self.collaborative_score = collaborative_score
        self.popularity_score = popularity_score
        self.difficulty_match_score = difficulty_match_score
        self.learning_style_match_score = learning_style_match_score
        self.reason = reason
        self.recommended_difficulty = recommended_difficulty
        self.estimated_completion_time = estimated_completion_time
        self.similar_users = similar_users or []
        self.tags = tags or []


class CourseRecommendationService:
    """Service for generating personalized course recommendations."""
    
    def __init__(self):
        self.min_users_for_collaborative = 5  # Minimum users needed for collaborative filtering
        self.similarity_threshold = 0.3  # Minimum similarity for user-based recommendations
        self.popularity_weight = 0.2  # Weight for popularity in final score
        self.content_weight = 0.4  # Weight for content-based filtering
        self.collaborative_weight = 0.3  # Weight for collaborative filtering
        self.difficulty_weight = 0.1  # Weight for difficulty matching
        
    async def get_course_recommendations(
        self,
        db: Session,
        user_id: str,
        max_recommendations: int = 10,
        include_completed: bool = False,
        topic_filter: Optional[str] = None
    ) -> List[CourseRecommendation]:
        """
        Get personalized course recommendations for a user.
        
        Args:
            db: Database session
            user_id: User ID to generate recommendations for
            max_recommendations: Maximum number of recommendations
            include_completed: Whether to include already completed courses
            topic_filter: Optional topic to filter recommendations
            
        Returns:
            List of CourseRecommendation objects
        """
        try:
            # Get user profile and learning patterns
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            if not user_profile:
                logger.info(f"No user profile found for {user_id}, using default recommendations")
                return await self._get_default_recommendations(db, max_recommendations, topic_filter)
            
            # Get available courses
            courses = self._get_available_courses(db, user_id, include_completed, topic_filter)
            if not courses:
                return []
            
            # Calculate different recommendation scores
            recommendations = []
            
            for course in courses:
                # Content-based filtering score
                content_score = await self._calculate_content_based_score(
                    db, course, user_profile, topic_filter
                )
                
                # Collaborative filtering score
                collaborative_score = await self._calculate_collaborative_score(
                    db, course, user_id, user_profile
                )
                
                # Popularity score
                popularity_score = await self._calculate_popularity_score(db, course)
                
                # Difficulty match score
                difficulty_score = self._calculate_difficulty_match_score(course, user_profile)
                
                # Learning style match score
                style_score = self._calculate_learning_style_match_score(course, user_profile)
                
                # Calculate final recommendation score
                final_score = (
                    content_score * self.content_weight +
                    collaborative_score * self.collaborative_weight +
                    popularity_score * self.popularity_weight +
                    difficulty_score * self.difficulty_weight
                )
                
                # Generate recommendation reason
                reason = self._generate_recommendation_reason(
                    course, content_score, collaborative_score, popularity_score, 
                    difficulty_score, style_score
                )
                
                # Determine recommended difficulty
                recommended_difficulty = self._determine_recommended_difficulty(
                    course, user_profile
                )
                
                # Estimate completion time
                estimated_time = self._estimate_completion_time(course, user_profile)
                
                # Get similar users for transparency
                similar_users = await self._get_similar_users(db, user_id, course.id)
                
                # Extract course tags/topics
                tags = self._extract_course_tags(course)
                
                recommendation = CourseRecommendation(
                    course_id=course.id,
                    title=course.title,
                    description=course.description or "",
                    recommendation_score=final_score,
                    content_based_score=content_score,
                    collaborative_score=collaborative_score,
                    popularity_score=popularity_score,
                    difficulty_match_score=difficulty_score,
                    learning_style_match_score=style_score,
                    reason=reason,
                    recommended_difficulty=recommended_difficulty,
                    estimated_completion_time=estimated_time,
                    similar_users=similar_users,
                    tags=tags
                )
                
                recommendations.append(recommendation)
            
            # Sort by recommendation score and return top results
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating course recommendations for {user_id}: {str(e)}")
            return []
    
    async def get_similar_courses(
        self,
        db: Session,
        course_id: int,
        max_recommendations: int = 5
    ) -> List[CourseRecommendation]:
        """
        Get courses similar to a given course.
        
        Args:
            db: Database session
            course_id: Course ID to find similar courses for
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of similar CourseRecommendation objects
        """
        try:
            # Get the reference course
            reference_course = db.query(Course).filter(Course.id == course_id).first()
            if not reference_course:
                return []
            
            # Get all other courses
            other_courses = db.query(Course).filter(Course.id != course_id).all()
            
            recommendations = []
            
            for course in other_courses:
                # Calculate similarity based on content
                similarity_score = self._calculate_course_similarity(reference_course, course)
                
                if similarity_score > 0.3:  # Minimum similarity threshold
                    recommendation = CourseRecommendation(
                        course_id=course.id,
                        title=course.title,
                        description=course.description or "",
                        recommendation_score=similarity_score,
                        content_based_score=similarity_score,
                        collaborative_score=0.0,
                        popularity_score=0.0,
                        difficulty_match_score=0.0,
                        learning_style_match_score=0.0,
                        reason=f"Similar to {reference_course.title}",
                        recommended_difficulty=DifficultyLevel.INTERMEDIATE,
                        estimated_completion_time=120,  # Default estimate
                        tags=self._extract_course_tags(course)
                    )
                    
                    recommendations.append(recommendation)
            
            # Sort by similarity and return top results
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error finding similar courses for {course_id}: {str(e)}")
            return []
    
    async def get_trending_courses(
        self,
        db: Session,
        max_recommendations: int = 10,
        time_window_days: int = 30
    ) -> List[CourseRecommendation]:
        """
        Get currently trending courses based on recent activity.
        
        Args:
            db: Database session
            max_recommendations: Maximum number of recommendations
            time_window_days: Time window for calculating trends
            
        Returns:
            List of trending CourseRecommendation objects
        """
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=time_window_days)
            
            # Get recent course activity
            recent_activity = analytics_crud.get_user_behavior_data(
                db=db,
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            # Count activity per course
            course_activity = defaultdict(int)
            course_users = defaultdict(set)
            
            for activity in recent_activity:
                if activity.course_id:
                    course_activity[activity.course_id] += 1
                    course_users[activity.course_id].add(activity.user_id)
            
            # Calculate trending scores
            trending_courses = []
            
            for course_id, activity_count in course_activity.items():
                course = db.query(Course).filter(Course.id == course_id).first()
                if not course:
                    continue
                
                unique_users = len(course_users[course_id])
                
                # Calculate trending score (activity + unique users)
                trending_score = (activity_count * 0.7) + (unique_users * 0.3)
                
                recommendation = CourseRecommendation(
                    course_id=course.id,
                    title=course.title,
                    description=course.description or "",
                    recommendation_score=trending_score,
                    content_based_score=0.0,
                    collaborative_score=0.0,
                    popularity_score=trending_score,
                    difficulty_match_score=0.0,
                    learning_style_match_score=0.0,
                    reason=f"Trending with {unique_users} active learners",
                    recommended_difficulty=DifficultyLevel.INTERMEDIATE,
                    estimated_completion_time=120,
                    tags=self._extract_course_tags(course)
                )
                
                trending_courses.append(recommendation)
            
            # Sort by trending score and return top results
            trending_courses.sort(key=lambda x: x.recommendation_score, reverse=True)
            return trending_courses[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting trending courses: {str(e)}")
            return []
    
    async def _get_default_recommendations(
        self,
        db: Session,
        max_recommendations: int,
        topic_filter: Optional[str] = None
    ) -> List[CourseRecommendation]:
        """Get default recommendations for users without profiles."""
        
        try:
            # Get popular courses as default
            query = db.query(Course)
            
            if topic_filter:
                query = query.filter(
                    or_(
                        Course.title.ilike(f"%{topic_filter}%"),
                        Course.description.ilike(f"%{topic_filter}%")
                    )
                )
            
            courses = query.limit(max_recommendations).all()
            
            recommendations = []
            
            for course in courses:
                recommendation = CourseRecommendation(
                    course_id=course.id,
                    title=course.title,
                    description=course.description or "",
                    recommendation_score=0.5,  # Default score
                    content_based_score=0.0,
                    collaborative_score=0.0,
                    popularity_score=0.5,
                    difficulty_match_score=0.0,
                    learning_style_match_score=0.0,
                    reason="Popular course for new learners",
                    recommended_difficulty=DifficultyLevel.BEGINNER,
                    estimated_completion_time=120,
                    tags=self._extract_course_tags(course)
                )
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting default recommendations: {str(e)}")
            return []
    
    def _get_available_courses(
        self,
        db: Session,
        user_id: str,
        include_completed: bool,
        topic_filter: Optional[str] = None
    ) -> List[Course]:
        """Get available courses for recommendation."""
        
        try:
            query = db.query(Course)
            
            # Filter by topic if specified
            if topic_filter:
                query = query.filter(
                    or_(
                        Course.title.ilike(f"%{topic_filter}%"),
                        Course.description.ilike(f"%{topic_filter}%")
                    )
                )
            
            courses = query.all()
            
            if not include_completed:
                # Filter out completed courses
                completed_courses = self._get_completed_courses(db, user_id)
                courses = [c for c in courses if c.id not in completed_courses]
            
            return courses
            
        except Exception as e:
            logger.error(f"Error getting available courses: {str(e)}")
            return []
    
    def _get_completed_courses(self, db: Session, user_id: str) -> List[int]:
        """Get list of course IDs completed by user."""
        
        try:
            completed_events = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=user_id,
                event_type=EventType.COURSE_COMPLETE,
                limit=1000
            )
            
            return list(set(
                event.course_id for event in completed_events 
                if event.course_id is not None
            ))
            
        except Exception as e:
            logger.error(f"Error getting completed courses: {str(e)}")
            return []
    
    async def _calculate_content_based_score(
        self,
        db: Session,
        course: Course,
        user_profile: UserLearningProfile,
        topic_filter: Optional[str] = None
    ) -> float:
        """Calculate content-based filtering score."""
        
        score = 0.0
        
        try:
            # Topic relevance
            if topic_filter:
                topic_score = self._calculate_topic_relevance(course, topic_filter)
                score += topic_score * 0.4
            
            # Learning style match
            style_score = self._calculate_learning_style_match_score(course, user_profile)
            score += style_score * 0.3
            
            # Difficulty appropriateness
            difficulty_score = self._calculate_difficulty_match_score(course, user_profile)
            score += difficulty_score * 0.3
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating content-based score: {str(e)}")
            return 0.0
    
    async def _calculate_collaborative_score(
        self,
        db: Session,
        course: Course,
        user_id: str,
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate collaborative filtering score."""
        
        try:
            # Find similar users
            similar_users = await self._find_similar_users(db, user_id, user_profile)
            
            if len(similar_users) < self.min_users_for_collaborative:
                return 0.0  # Not enough data for collaborative filtering
            
            # Check how many similar users took this course
            course_takers = 0
            total_similar_users = len(similar_users)
            
            for similar_user_id, similarity in similar_users:
                user_courses = self._get_completed_courses(db, similar_user_id)
                if course.id in user_courses:
                    course_takers += 1
            
            # Calculate collaborative score
            if total_similar_users > 0:
                collaborative_score = course_takers / total_similar_users
                return collaborative_score
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating collaborative score: {str(e)}")
            return 0.0
    
    async def _calculate_popularity_score(self, db: Session, course: Course) -> float:
        """Calculate course popularity score."""
        
        try:
            # Count recent enrollments/starts
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=90)  # Last 3 months
            
            course_starts = analytics_crud.get_user_behavior_data(
                db=db,
                course_id=course.id,
                event_type=EventType.COURSE_START,
                start_date=start_date,
                end_date=end_date
            )
            
            # Normalize popularity (assuming max 100 starts is very popular)
            popularity = len(course_starts) / 100.0
            return min(1.0, popularity)
            
        except Exception as e:
            logger.error(f"Error calculating popularity score: {str(e)}")
            return 0.0
    
    def _calculate_difficulty_match_score(
        self,
        course: Course,
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate how well course difficulty matches user level."""
        
        try:
            # Get course difficulty (would be stored in course metadata)
            course_difficulty = 0.5  # Default to intermediate
            if hasattr(course, 'difficulty'):
                difficulty_map = {
                    'beginner': 0.3,
                    'intermediate': 0.5,
                    'advanced': 0.8
                }
                course_difficulty = difficulty_map.get(course.difficulty.lower(), 0.5)
            
            # Compare with user's current level
            user_level = user_profile.current_difficulty_level
            
            # Calculate match score (closer = higher score)
            diff = abs(course_difficulty - user_level)
            match_score = 1.0 - diff
            
            return max(0.0, match_score)
            
        except Exception as e:
            logger.error(f"Error calculating difficulty match: {str(e)}")
            return 0.5
    
    def _calculate_learning_style_match_score(
        self,
        course: Course,
        user_profile: UserLearningProfile
    ) -> float:
        """Calculate learning style compatibility score."""
        
        try:
            # This would analyze course content types, format, etc.
            # For now, return a moderate score based on learning style
            
            if user_profile.learning_style == LearningStyleType.VISUAL:
                # Check if course has visual elements (would be in metadata)
                return 0.8  # Assume most courses have some visual elements
            elif user_profile.learning_style == LearningStyleType.AUDITORY:
                return 0.6  # Moderate match for most courses
            elif user_profile.learning_style == LearningStyleType.KINESTHETIC:
                return 0.7  # Good match for interactive courses
            elif user_profile.learning_style == LearningStyleType.READING:
                return 0.9  # Most courses have text content
            else:
                return 0.5  # Unknown learning style
                
        except Exception as e:
            logger.error(f"Error calculating learning style match: {str(e)}")
            return 0.5
    
    def _calculate_topic_relevance(self, course: Course, topic: str) -> float:
        """Calculate topic relevance score."""
        
        try:
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
            
        except Exception as e:
            logger.error(f"Error calculating topic relevance: {str(e)}")
            return 0.0
    
    async def _find_similar_users(
        self,
        db: Session,
        user_id: str,
        user_profile: UserLearningProfile
    ) -> List[Tuple[str, float]]:
        """Find users similar to the given user."""
        
        try:
            # Get all user profiles
            all_profiles = analytics_crud.get_all_user_learning_profiles(db)
            
            similar_users = []
            
            for profile in all_profiles:
                if profile.user_id == user_id:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_user_similarity(user_profile, profile)
                
                if similarity >= self.similarity_threshold:
                    similar_users.append((profile.user_id, similarity))
            
            # Sort by similarity
            similar_users.sort(key=lambda x: x[1], reverse=True)
            
            return similar_users[:20]  # Return top 20 similar users
            
        except Exception as e:
            logger.error(f"Error finding similar users: {str(e)}")
            return []
    
    def _calculate_user_similarity(
        self,
        user1_profile: UserLearningProfile,
        user2_profile: UserLearningProfile
    ) -> float:
        """Calculate similarity between two user profiles."""
        
        try:
            similarity_factors = []
            
            # Learning style similarity
            if user1_profile.learning_style == user2_profile.learning_style:
                similarity_factors.append(1.0)
            else:
                similarity_factors.append(0.0)
            
            # Completion rate similarity
            completion_diff = abs(user1_profile.completion_rate - user2_profile.completion_rate)
            completion_sim = 1.0 - completion_diff
            similarity_factors.append(completion_sim)
            
            # Engagement score similarity
            engagement_diff = abs(user1_profile.engagement_score - user2_profile.engagement_score)
            engagement_sim = 1.0 - engagement_diff
            similarity_factors.append(engagement_sim)
            
            # Challenge preference similarity
            challenge_diff = abs(user1_profile.challenge_preference - user2_profile.challenge_preference)
            challenge_sim = 1.0 - challenge_diff
            similarity_factors.append(challenge_sim)
            
            # Calculate weighted average
            weights = [0.3, 0.25, 0.25, 0.2]  # Learning style has highest weight
            weighted_similarity = sum(
                factor * weight for factor, weight in zip(similarity_factors, weights)
            )
            
            return weighted_similarity
            
        except Exception as e:
            logger.error(f"Error calculating user similarity: {str(e)}")
            return 0.0
    
    def _calculate_course_similarity(self, course1: Course, course2: Course) -> float:
        """Calculate similarity between two courses."""
        
        try:
            # Simple text-based similarity
            title1_words = set(course1.title.lower().split())
            title2_words = set(course2.title.lower().split())
            
            desc1_words = set((course1.description or "").lower().split())
            desc2_words = set((course2.description or "").lower().split())
            
            # Calculate Jaccard similarity for titles
            title_intersection = len(title1_words & title2_words)
            title_union = len(title1_words | title2_words)
            title_similarity = title_intersection / title_union if title_union > 0 else 0.0
            
            # Calculate Jaccard similarity for descriptions
            desc_intersection = len(desc1_words & desc2_words)
            desc_union = len(desc1_words | desc2_words)
            desc_similarity = desc_intersection / desc_union if desc_union > 0 else 0.0
            
            # Weighted combination
            overall_similarity = (title_similarity * 0.7) + (desc_similarity * 0.3)
            
            return overall_similarity
            
        except Exception as e:
            logger.error(f"Error calculating course similarity: {str(e)}")
            return 0.0
    
    async def _get_similar_users(
        self,
        db: Session,
        user_id: str,
        course_id: int
    ) -> List[str]:
        """Get users similar to the given user who took the course."""
        
        try:
            # Get users who took this course
            # Get users who started the course
            course_starts = analytics_crud.get_user_behavior_data(
                db=db,
                course_id=course_id,
                event_type=EventType.COURSE_START
            )
            
            # Get users who completed the course
            course_completes = analytics_crud.get_user_behavior_data(
                db=db,
                course_id=course_id,
                event_type=EventType.COURSE_COMPLETE
            )
            
            # Combine the behavior data
            course_behavior = course_starts + course_completes
            
            course_users = list(set(
                behavior.user_id for behavior in course_behavior
                if behavior.user_id != user_id
            ))
            
            return course_users[:5]  # Return up to 5 similar users
            
        except Exception as e:
            logger.error(f"Error getting similar users: {str(e)}")
            return []
    
    def _extract_course_tags(self, course: Course) -> List[str]:
        """Extract tags/topics from course."""
        
        try:
            tags = []
            
            # Extract from title
            title_words = [
                word.strip().lower() for word in course.title.split()
                if len(word) > 3  # Skip short words
            ]
            tags.extend(title_words)
            
            # Extract from description (first few words)
            if course.description:
                desc_words = [
                    word.strip().lower() for word in course.description.split()[:10]
                    if len(word) > 3
                ]
                tags.extend(desc_words)
            
            # Remove duplicates and return
            return list(set(tags))
            
        except Exception as e:
            logger.error(f"Error extracting course tags: {str(e)}")
            return []
    
    def _generate_recommendation_reason(
        self,
        course: Course,
        content_score: float,
        collaborative_score: float,
        popularity_score: float,
        difficulty_score: float,
        style_score: float
    ) -> str:
        """Generate human-readable recommendation reason."""
        
        reasons = []
        
        # Determine primary reason based on highest score
        scores = {
            "content": content_score,
            "collaborative": collaborative_score,
            "popularity": popularity_score,
            "difficulty": difficulty_score,
            "style": style_score
        }
        
        primary_reason = max(scores, key=scores.get)
        
        if primary_reason == "content" and content_score > 0.7:
            reasons.append("Matches your learning interests")
        elif primary_reason == "collaborative" and collaborative_score > 0.6:
            reasons.append("Recommended by similar learners")
        elif primary_reason == "popularity" and popularity_score > 0.5:
            reasons.append("Popular among recent learners")
        elif primary_reason == "difficulty" and difficulty_score > 0.7:
            reasons.append("Appropriate for your skill level")
        elif primary_reason == "style" and style_score > 0.7:
            reasons.append("Matches your learning style")
        else:
            reasons.append("Good overall match for your profile")
        
        # Add secondary reasons
        if difficulty_score > 0.8:
            reasons.append("perfect difficulty level")
        elif style_score > 0.8:
            reasons.append("excellent learning style match")
        
        return ". ".join(reasons).capitalize()
    
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
        
        # Adjust based on user's learning patterns
        if user_profile.average_session_duration:
            # Consider user's typical session length
            sessions_needed = max(1, base_time // user_profile.average_session_duration)
            
            # Adjust for completion rate
            if user_profile.completion_rate > 0.7:
                adjusted_time = base_time * 0.9  # Faster for high performers
            elif user_profile.completion_rate < 0.4:
                adjusted_time = base_time * 1.3  # Slower for struggling learners
            else:
                adjusted_time = base_time
            
            return int(adjusted_time)
        
        return base_time