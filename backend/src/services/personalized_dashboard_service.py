"""
Personalized Dashboard Service for providing customized dashboard content.

This service integrates with the personalization engine and learning analytics
to provide personalized course recommendations, learning progress insights,
and adaptive content suggestions for the user dashboard.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from ..db.crud import courses_crud, analytics_crud
from ..db.models.db_course import Course
from ..db.models.db_analytics import UserLearningProfile
from .personalization_engine import PersonalizationEngine
from .learning_adaptation_service import LearningAdaptationService
from .course_service import get_personalized_course_recommendations

logger = logging.getLogger(__name__)


class PersonalizedDashboardService:
    """Service for generating personalized dashboard content."""
    
    def __init__(self):
        self.personalization_engine = PersonalizationEngine()
        self.learning_adaptation = LearningAdaptationService()
    
    async def get_dashboard_data(
        self,
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive personalized dashboard data for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with personalized dashboard content
        """
        try:
            # Get user's learning profile
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            
            # Get user's courses
            user_courses = courses_crud.get_courses_infos(db, user_id, skip=0, limit=50)
            
            # Generate personalized recommendations
            recommendations = await self._get_personalized_recommendations(
                db, user_id, user_profile, user_courses
            )
            
            # Get learning progress insights
            progress_insights = await self._get_learning_progress_insights(
                db, user_id, user_profile, user_courses
            )
            
            # Get adaptive learning suggestions
            learning_suggestions = await self._get_adaptive_learning_suggestions(
                db, user_id, user_profile
            )
            
            # Get personalized metrics
            personalized_metrics = await self._get_personalized_metrics(
                db, user_id, user_profile
            )
            
            # Get next learning actions
            next_actions = await self._get_next_learning_actions(
                db, user_id, user_courses
            )
            
            return {
                "user_profile": self._format_user_profile(user_profile),
                "recommendations": recommendations,
                "progress_insights": progress_insights,
                "learning_suggestions": learning_suggestions,
                "personalized_metrics": personalized_metrics,
                "next_actions": next_actions,
                "personalization_available": user_profile is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for user {user_id}: {str(e)}")
            return {
                "user_profile": None,
                "recommendations": [],
                "progress_insights": {},
                "learning_suggestions": [],
                "personalized_metrics": {},
                "next_actions": [],
                "personalization_available": False,
                "error": "Failed to load personalized content"
            }
    
    async def get_learning_path_recommendations(
        self,
        db: Session,
        user_id: str,
        current_course_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get personalized learning path recommendations.
        
        Args:
            db: Database session
            user_id: User ID
            current_course_id: Optional current course ID for context
            
        Returns:
            List of learning path recommendations
        """
        try:
            user_profile = analytics_crud.get_user_learning_profile(db, user_id)
            
            if not user_profile:
                return []
            
            # Determine topic based on current course or user interests
            topic = "general"
            if current_course_id:
                current_course = courses_crud.get_course_by_id(db, current_course_id)
                if current_course and current_course.title:
                    topic = current_course.title
            elif user_profile.strong_topics:
                topic = user_profile.strong_topics[0]
            
            # Get recommendations from personalization engine
            recommendations = await self.personalization_engine.recommend_learning_path(
                db=db,
                user_id=user_id,
                topic=topic,
                max_recommendations=5
            )
            
            # Format recommendations
            formatted_recommendations = []
            for rec in recommendations:
                formatted_recommendations.append({
                    "course_id": rec.course_id,
                    "title": rec.title,
                    "recommendation_score": rec.recommendation_score,
                    "reason": rec.reason,
                    "recommended_difficulty": rec.recommended_difficulty.value,
                    "estimated_completion_time": rec.estimated_completion_time,
                    "topic_match_score": rec.topic_match_score,
                    "learning_style_match": rec.learning_style_match,
                    "recommendation_type": "learning_path"
                })
            
            return formatted_recommendations
            
        except Exception as e:
            logger.error(f"Error getting learning path recommendations: {str(e)}")
            return []
    
    async def get_adaptive_content_suggestions(
        self,
        db: Session,
        user_id: str,
        struggling_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get adaptive content suggestions for struggling areas.
        
        Args:
            db: Database session
            user_id: User ID
            struggling_areas: List of areas where user is struggling
            
        Returns:
            List of adaptive content suggestions
        """
        try:
            suggestions = []
            
            for area in struggling_areas:
                # Get supplementary materials
                materials = await self.learning_adaptation.provide_supplementary_content(
                    db=db,
                    user_id=user_id,
                    topic=area,
                    max_recommendations=3
                )
                
                for material in materials:
                    suggestions.append({
                        "material_id": material.material_id,
                        "title": material.title,
                        "content_type": material.content_type,
                        "difficulty_level": material.difficulty_level.value,
                        "estimated_time": material.estimated_time,
                        "relevance_score": material.relevance_score,
                        "reason": material.reason,
                        "priority": material.priority,
                        "topic": area,
                        "suggestion_type": "supplementary_content"
                    })
            
            # Sort by priority and relevance
            suggestions.sort(key=lambda x: (x["priority"], -x["relevance_score"]))
            
            return suggestions[:10]  # Limit to top 10 suggestions
            
        except Exception as e:
            logger.error(f"Error getting adaptive content suggestions: {str(e)}")
            return []
    
    async def _get_personalized_recommendations(
        self,
        db: Session,
        user_id: str,
        user_profile: Optional[UserLearningProfile],
        user_courses: List[Any]
    ) -> List[Dict[str, Any]]:
        """Get personalized course recommendations."""
        
        if not user_profile:
            return []
        
        try:
            # Get topic-based recommendations
            topic_recommendations = await get_personalized_course_recommendations(
                db=db,
                user_id=user_id,
                topic=None,  # Will infer from user activity
                max_recommendations=5
            )
            
            # Add recommendation metadata
            for rec in topic_recommendations:
                rec["recommendation_type"] = "personalized"
                rec["confidence"] = min(1.0, rec["recommendation_score"] * 1.2)
            
            return topic_recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            return []
    
    async def _get_learning_progress_insights(
        self,
        db: Session,
        user_id: str,
        user_profile: Optional[UserLearningProfile],
        user_courses: List[Any]
    ) -> Dict[str, Any]:
        """Get learning progress insights."""
        
        insights = {
            "completion_trend": "stable",
            "learning_velocity": "average",
            "engagement_level": "moderate",
            "strength_areas": [],
            "improvement_areas": [],
            "learning_style_insights": {},
            "time_management_insights": {}
        }
        
        if not user_profile:
            return insights
        
        try:
            # Analyze completion trend
            if user_profile.completion_rate > 0.8:
                insights["completion_trend"] = "excellent"
            elif user_profile.completion_rate > 0.6:
                insights["completion_trend"] = "good"
            elif user_profile.completion_rate < 0.3:
                insights["completion_trend"] = "needs_improvement"
            
            # Analyze learning velocity
            if user_profile.consistency_score > 0.7:
                insights["learning_velocity"] = "fast"
            elif user_profile.consistency_score < 0.3:
                insights["learning_velocity"] = "slow"
            
            # Analyze engagement level
            if user_profile.engagement_score > 0.7:
                insights["engagement_level"] = "high"
            elif user_profile.engagement_score < 0.3:
                insights["engagement_level"] = "low"
            
            # Add strength and improvement areas
            if user_profile.strong_topics:
                insights["strength_areas"] = user_profile.strong_topics[:3]
            
            if user_profile.challenging_topics:
                insights["improvement_areas"] = user_profile.challenging_topics[:3]
            
            # Learning style insights
            if user_profile.learning_style:
                insights["learning_style_insights"] = {
                    "primary_style": user_profile.learning_style.value,
                    "recommendations": self._get_learning_style_recommendations(user_profile.learning_style.value)
                }
            
            # Time management insights
            if user_profile.attention_span:
                insights["time_management_insights"] = {
                    "optimal_session_length": user_profile.attention_span,
                    "recommendation": self._get_time_management_recommendation(user_profile.attention_span)
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning progress insights: {str(e)}")
            return insights
    
    async def _get_adaptive_learning_suggestions(
        self,
        db: Session,
        user_id: str,
        user_profile: Optional[UserLearningProfile]
    ) -> List[Dict[str, Any]]:
        """Get adaptive learning suggestions."""
        
        suggestions = []
        
        if not user_profile:
            return suggestions
        
        try:
            # Suggest based on completion rate
            if user_profile.completion_rate < 0.4:
                suggestions.append({
                    "type": "pacing_adjustment",
                    "title": "Consider Slower Pacing",
                    "description": "Your completion rate suggests you might benefit from a slower learning pace.",
                    "action": "adjust_pacing",
                    "priority": "high"
                })
            
            # Suggest based on engagement score
            if user_profile.engagement_score < 0.4:
                suggestions.append({
                    "type": "content_variety",
                    "title": "Try Different Content Types",
                    "description": "Exploring different content formats might increase your engagement.",
                    "action": "explore_content_types",
                    "priority": "medium"
                })
            
            # Suggest based on learning style
            if user_profile.learning_style:
                style_suggestion = self._get_learning_style_suggestion(user_profile.learning_style.value)
                if style_suggestion:
                    suggestions.append(style_suggestion)
            
            # Suggest based on challenging topics
            if user_profile.challenging_topics:
                suggestions.append({
                    "type": "supplementary_practice",
                    "title": "Additional Practice Available",
                    "description": f"Extra practice materials are available for {', '.join(user_profile.challenging_topics[:2])}.",
                    "action": "get_supplementary_content",
                    "priority": "medium",
                    "topics": user_profile.challenging_topics[:3]
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting adaptive learning suggestions: {str(e)}")
            return suggestions
    
    async def _get_personalized_metrics(
        self,
        db: Session,
        user_id: str,
        user_profile: Optional[UserLearningProfile]
    ) -> Dict[str, Any]:
        """Get personalized metrics for the dashboard."""
        
        metrics = {
            "learning_efficiency": 0.5,
            "consistency_score": 0.5,
            "challenge_readiness": 0.5,
            "engagement_trend": "stable",
            "personalized_goals": []
        }
        
        if not user_profile:
            return metrics
        
        try:
            # Calculate learning efficiency (completion rate * engagement)
            metrics["learning_efficiency"] = (
                user_profile.completion_rate * 0.7 + 
                user_profile.engagement_score * 0.3
            )
            
            # Use consistency score from profile
            metrics["consistency_score"] = user_profile.consistency_score
            
            # Calculate challenge readiness
            metrics["challenge_readiness"] = min(1.0, user_profile.challenge_preference)
            
            # Determine engagement trend (simplified)
            if user_profile.engagement_score > 0.7:
                metrics["engagement_trend"] = "improving"
            elif user_profile.engagement_score < 0.3:
                metrics["engagement_trend"] = "declining"
            
            # Generate personalized goals
            goals = []
            
            if user_profile.completion_rate < 0.6:
                goals.append({
                    "type": "completion",
                    "title": "Improve Course Completion",
                    "target": 0.8,
                    "current": user_profile.completion_rate,
                    "suggestion": "Focus on completing one chapter at a time"
                })
            
            if user_profile.consistency_score < 0.5:
                goals.append({
                    "type": "consistency",
                    "title": "Build Learning Consistency",
                    "target": 0.7,
                    "current": user_profile.consistency_score,
                    "suggestion": "Try to study for a few minutes each day"
                })
            
            if user_profile.engagement_score < 0.5:
                goals.append({
                    "type": "engagement",
                    "title": "Increase Learning Engagement",
                    "target": 0.7,
                    "current": user_profile.engagement_score,
                    "suggestion": "Explore interactive content and practice exercises"
                })
            
            metrics["personalized_goals"] = goals[:3]  # Limit to 3 goals
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting personalized metrics: {str(e)}")
            return metrics
    
    async def _get_next_learning_actions(
        self,
        db: Session,
        user_id: str,
        user_courses: List[Any]
    ) -> List[Dict[str, Any]]:
        """Get recommended next learning actions."""
        
        actions = []
        
        try:
            # Find incomplete courses
            incomplete_courses = [
                course for course in user_courses 
                if course.status != "CourseStatus.FINISHED" and course.status != "CourseStatus.COMPLETED"
            ]
            
            # Suggest continuing incomplete courses
            for course in incomplete_courses[:3]:  # Limit to 3 suggestions
                progress = 0
                if course.chapter_count and course.chapter_count > 0:
                    progress = (course.completed_chapter_count or 0) / course.chapter_count
                
                actions.append({
                    "type": "continue_course",
                    "title": f"Continue: {course.title}",
                    "description": f"You're {int(progress * 100)}% complete",
                    "course_id": course.course_id,
                    "progress": progress,
                    "priority": "high" if progress > 0.1 else "medium"
                })
            
            # Suggest creating new course if user has few courses
            if len(user_courses) < 3:
                actions.append({
                    "type": "create_course",
                    "title": "Create New Course",
                    "description": "Explore a new topic that interests you",
                    "priority": "low"
                })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting next learning actions: {str(e)}")
            return actions
    
    def _format_user_profile(self, user_profile: Optional[UserLearningProfile]) -> Optional[Dict[str, Any]]:
        """Format user profile for dashboard display."""
        
        if not user_profile:
            return None
        
        return {
            "learning_style": user_profile.learning_style.value if user_profile.learning_style else "unknown",
            "completion_rate": user_profile.completion_rate,
            "engagement_score": user_profile.engagement_score,
            "consistency_score": user_profile.consistency_score,
            "challenge_preference": user_profile.challenge_preference,
            "attention_span": user_profile.attention_span,
            "strong_topics": user_profile.strong_topics or [],
            "challenging_topics": user_profile.challenging_topics or [],
            "total_learning_time": user_profile.total_learning_time,
            "courses_completed": user_profile.courses_completed
        }
    
    def _get_learning_style_recommendations(self, learning_style: str) -> List[str]:
        """Get recommendations based on learning style."""
        
        recommendations = {
            "visual": [
                "Use diagrams and charts to understand concepts",
                "Watch video content when available",
                "Create mind maps for complex topics"
            ],
            "auditory": [
                "Listen to audio content or read aloud",
                "Discuss topics with others",
                "Use verbal repetition for memorization"
            ],
            "kinesthetic": [
                "Practice hands-on exercises",
                "Take breaks to move around",
                "Use interactive simulations when available"
            ],
            "reading": [
                "Take detailed notes while studying",
                "Read supplementary materials",
                "Summarize key concepts in writing"
            ]
        }
        
        return recommendations.get(learning_style, [])
    
    def _get_time_management_recommendation(self, attention_span: int) -> str:
        """Get time management recommendation based on attention span."""
        
        if attention_span < 20:
            return "Take frequent breaks (every 15-20 minutes) to maintain focus"
        elif attention_span < 45:
            return "Study in 30-45 minute sessions with short breaks"
        else:
            return "You can handle longer study sessions, but still take breaks every hour"
    
    def _get_learning_style_suggestion(self, learning_style: str) -> Optional[Dict[str, Any]]:
        """Get learning style-specific suggestion."""
        
        suggestions = {
            "visual": {
                "type": "learning_style_optimization",
                "title": "Optimize for Visual Learning",
                "description": "Look for courses with diagrams, charts, and visual content.",
                "action": "filter_visual_content",
                "priority": "low"
            },
            "kinesthetic": {
                "type": "learning_style_optimization",
                "title": "Find Interactive Content",
                "description": "Seek out hands-on exercises and interactive simulations.",
                "action": "filter_interactive_content",
                "priority": "low"
            },
            "auditory": {
                "type": "learning_style_optimization",
                "title": "Explore Audio Content",
                "description": "Look for courses with audio explanations and discussions.",
                "action": "filter_audio_content",
                "priority": "low"
            }
        }
        
        return suggestions.get(learning_style)