"""
Analytics Processing Service for handling Umami analytics data and learning pattern identification.

This service fetches data from Umami analytics, processes user behavior data,
calculates engagement metrics, and identifies learning patterns.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
import httpx
from sqlalchemy.orm import Session

from ..db.crud import analytics_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..utils.analytics_utils import (
    sanitize_url, sanitize_session_id, sanitize_user_id, sanitize_metadata,
    validate_engagement_score, validate_duration, validate_timestamp,
    calculate_engagement_score, generate_analytics_id
)
from ..config.settings import UMAMI_API_URL, UMAMI_API_TOKEN, UMAMI_WEBSITE_ID

logger = logging.getLogger(__name__)


class AnalyticsProcessingService:
    """Service for processing Umami analytics data and generating learning insights."""
    
    def __init__(self):
        self.umami_api_url = UMAMI_API_URL
        self.umami_api_token = UMAMI_API_TOKEN
        self.umami_website_id = UMAMI_WEBSITE_ID
        
    async def fetch_umami_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch analytics data from Umami API.
        
        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            event_type: Optional event type filter
            
        Returns:
            List of analytics events from Umami
        """
        if not self.umami_api_url or not self.umami_api_token:
            logger.warning("Umami API configuration missing")
            return []
        
        headers = {
            "Authorization": f"Bearer {self.umami_api_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "startAt": int(start_date.timestamp() * 1000),
            "endAt": int(end_date.timestamp() * 1000),
            "unit": "hour"
        }
        
        if event_type:
            params["event"] = event_type
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch page views
                pageviews_response = await client.get(
                    f"{self.umami_api_url}/api/websites/{self.umami_website_id}/pageviews",
                    headers=headers,
                    params=params
                )
                pageviews_response.raise_for_status()
                pageviews_data = pageviews_response.json()
                
                # Fetch events
                events_response = await client.get(
                    f"{self.umami_api_url}/api/websites/{self.umami_website_id}/events",
                    headers=headers,
                    params=params
                )
                events_response.raise_for_status()
                events_data = events_response.json()
                
                # Combine and normalize data
                analytics_data = []
                
                # Process pageviews
                for pageview in pageviews_data.get("pageviews", []):
                    analytics_data.append({
                        "event_type": "page_view",
                        "url": pageview.get("url", ""),
                        "timestamp": datetime.fromtimestamp(pageview.get("created_at", 0) / 1000, tz=timezone.utc),
                        "session_id": pageview.get("session_id", ""),
                        "user_id": pageview.get("user_id", ""),
                        "metadata": {
                            "referrer": pageview.get("referrer"),
                            "country": pageview.get("country"),
                            "device": pageview.get("device"),
                            "os": pageview.get("os"),
                            "browser": pageview.get("browser")
                        }
                    })
                
                # Process custom events
                for event in events_data.get("events", []):
                    analytics_data.append({
                        "event_type": event.get("event_name", "custom_event"),
                        "url": event.get("url", ""),
                        "timestamp": datetime.fromtimestamp(event.get("created_at", 0) / 1000, tz=timezone.utc),
                        "session_id": event.get("session_id", ""),
                        "user_id": event.get("user_id", ""),
                        "metadata": event.get("event_data", {})
                    })
                
                logger.info(f"Fetched {len(analytics_data)} analytics events from Umami")
                return analytics_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Umami data: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Umami data: {str(e)}")
            return []
    
    async def process_umami_data(self, db: Session, website_id: str) -> List[UserBehaviorData]:
        """
        Process Umami analytics data and store in database.
        
        Args:
            db: Database session
            website_id: Umami website ID
            
        Returns:
            List of processed UserBehaviorData records
        """
        # Fetch data for the last 24 hours
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(hours=24)
        
        umami_data = await self.fetch_umami_data(start_date, end_date)
        processed_records = []
        
        for event_data in umami_data:
            try:
                # Extract and validate data
                user_id = sanitize_user_id(event_data.get("user_id", "anonymous"))
                session_id = sanitize_session_id(event_data.get("session_id", "unknown"))
                page_url = sanitize_url(event_data.get("url", ""))
                timestamp = validate_timestamp(event_data.get("timestamp", datetime.now(timezone.utc)))
                
                # Map event type
                event_type_str = event_data.get("event_type", "page_view")
                event_type = self._map_event_type(event_type_str)
                
                # Extract course and chapter IDs from URL if available
                course_id, chapter_id = self._extract_course_info_from_url(page_url)
                
                # Sanitize metadata
                metadata = sanitize_metadata(event_data.get("metadata", {}))
                
                # Calculate duration if available
                duration_seconds = validate_duration(metadata.get("duration") if metadata else None)
                
                # Create behavior data record
                behavior_data = analytics_crud.create_user_behavior_data(
                    db=db,
                    user_id=user_id,
                    session_id=session_id,
                    event_type=event_type,
                    page_url=page_url,
                    timestamp=timestamp,
                    course_id=course_id,
                    chapter_id=chapter_id,
                    metadata=metadata,
                    duration_seconds=duration_seconds
                )
                
                processed_records.append(behavior_data)
                
            except Exception as e:
                logger.error(f"Error processing analytics event: {str(e)}")
                continue
        
        logger.info(f"Processed {len(processed_records)} analytics records")
        return processed_records
    
    def calculate_engagement_metrics(
        self, 
        db: Session, 
        user_id: str, 
        time_period_hours: int = 24
    ) -> EngagementMetrics:
        """
        Calculate engagement metrics for a user over a time period.
        
        Args:
            db: Database session
            user_id: User ID to calculate metrics for
            time_period_hours: Time period in hours to analyze
            
        Returns:
            EngagementMetrics record
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=time_period_hours)
        
        # Get user behavior data for the period
        behavior_data = analytics_crud.get_user_behavior_data(
            db=db,
            user_id=user_id,
            start_date=start_time,
            end_date=end_time
        )
        
        if not behavior_data:
            # Create empty metrics if no data
            return analytics_crud.create_engagement_metrics(
                db=db,
                user_id=user_id,
                time_period_start=start_time,
                time_period_end=end_time
            )
        
        # Calculate metrics
        total_time_spent = sum(
            (data.duration_seconds or 0) for data in behavior_data
        )
        
        interaction_count = len([
            data for data in behavior_data 
            if data.event_type in [EventType.CLICK, EventType.CONTENT_INTERACTION]
        ])
        
        page_views = len([
            data for data in behavior_data 
            if data.event_type == EventType.PAGE_VIEW
        ])
        
        # Calculate completion percentage based on course/chapter completion events
        completion_events = len([
            data for data in behavior_data 
            if data.event_type in [EventType.COURSE_COMPLETE, EventType.CHAPTER_COMPLETE]
        ])
        
        start_events = len([
            data for data in behavior_data 
            if data.event_type in [EventType.COURSE_START, EventType.CHAPTER_START]
        ])
        
        completion_percentage = completion_events / start_events if start_events > 0 else 0.0
        
        # Calculate engagement score
        engagement_score = calculate_engagement_score(
            time_spent=total_time_spent,
            interaction_count=interaction_count,
            page_views=page_views,
            completion_percentage=completion_percentage
        )
        
        # Calculate focus score (time spent vs session duration)
        unique_sessions = len(set(data.session_id for data in behavior_data))
        session_duration = time_period_hours * 3600  # Convert to seconds
        focus_score = min(1.0, total_time_spent / (session_duration * unique_sessions)) if unique_sessions > 0 else 0.0
        
        # Calculate progress velocity (content completed per time)
        progress_velocity = completion_events / time_period_hours if time_period_hours > 0 else 0.0
        
        # Create engagement metrics record
        return analytics_crud.create_engagement_metrics(
            db=db,
            user_id=user_id,
            time_period_start=start_time,
            time_period_end=end_time,
            total_time_spent=total_time_spent,
            interaction_count=interaction_count,
            page_views=page_views,
            completion_percentage=completion_percentage,
            engagement_score=engagement_score,
            focus_score=focus_score,
            progress_velocity=progress_velocity
        )
    
    def identify_learning_patterns(self, db: Session, user_id: str) -> Optional[LearningPattern]:
        """
        Identify learning patterns for a user based on their behavior data.
        
        Args:
            db: Database session
            user_id: User ID to analyze
            
        Returns:
            LearningPattern record or None if insufficient data
        """
        # Get behavior data for the last 30 days
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        behavior_data = analytics_crud.get_user_behavior_data(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        if len(behavior_data) < 10:  # Need minimum data points
            return None
        
        # Analyze learning style patterns
        learning_style, confidence = self._analyze_learning_style(behavior_data)
        
        # Analyze session patterns
        optimal_session_duration = self._calculate_optimal_session_duration(behavior_data)
        preferred_learning_times = self._analyze_preferred_learning_times(behavior_data)
        average_attention_span = self._calculate_attention_span(behavior_data)
        
        # Analyze content preferences
        preferred_content_types = self._analyze_content_preferences(behavior_data)
        
        # Analyze difficulty progression
        difficulty_progression_rate = self._analyze_difficulty_progression(behavior_data)
        
        # Analyze topic performance
        strong_topics, challenging_topics = self._analyze_topic_performance(behavior_data)
        
        # Create or update learning pattern
        existing_pattern = analytics_crud.get_learning_pattern_by_user(db, user_id)
        
        if existing_pattern:
            # Update existing pattern
            update_data = {
                "pattern_type": learning_style,
                "confidence_score": confidence,
                "preferred_content_types": preferred_content_types,
                "optimal_session_duration": optimal_session_duration,
                "difficulty_progression_rate": difficulty_progression_rate,
                "preferred_learning_times": preferred_learning_times,
                "average_attention_span": average_attention_span,
                "strong_topics": strong_topics,
                "challenging_topics": challenging_topics,
                "data_points_count": len(behavior_data)
            }
            return analytics_crud.update_learning_pattern(db, existing_pattern, update_data)
        else:
            # Create new pattern
            return analytics_crud.create_learning_pattern(
                db=db,
                user_id=user_id,
                pattern_type=learning_style,
                confidence_score=confidence,
                preferred_content_types=preferred_content_types,
                optimal_session_duration=optimal_session_duration,
                difficulty_progression_rate=difficulty_progression_rate,
                preferred_learning_times=preferred_learning_times,
                average_attention_span=average_attention_span,
                strong_topics=strong_topics,
                challenging_topics=challenging_topics,
                data_points_count=len(behavior_data)
            )
    
    def _map_event_type(self, event_type_str: str) -> EventType:
        """Map string event type to EventType enum."""
        event_mapping = {
            "page_view": EventType.PAGE_VIEW,
            "click": EventType.CLICK,
            "scroll": EventType.SCROLL,
            "time_spent": EventType.TIME_SPENT,
            "course_start": EventType.COURSE_START,
            "course_complete": EventType.COURSE_COMPLETE,
            "chapter_start": EventType.CHAPTER_START,
            "chapter_complete": EventType.CHAPTER_COMPLETE,
            "assessment_start": EventType.ASSESSMENT_START,
            "assessment_complete": EventType.ASSESSMENT_COMPLETE,
            "content_interaction": EventType.CONTENT_INTERACTION
        }
        return event_mapping.get(event_type_str.lower(), EventType.PAGE_VIEW)
    
    def _extract_course_info_from_url(self, url: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract course and chapter IDs from URL."""
        try:
            # Example URL patterns:
            # /courses/123/chapters/456
            # /courses/123
            parts = url.split('/')
            course_id = None
            chapter_id = None
            
            for i, part in enumerate(parts):
                if part == "courses" and i + 1 < len(parts):
                    try:
                        course_id = int(parts[i + 1])
                    except ValueError:
                        pass
                elif part == "chapters" and i + 1 < len(parts):
                    try:
                        chapter_id = int(parts[i + 1])
                    except ValueError:
                        pass
            
            return course_id, chapter_id
        except Exception:
            return None, None
    
    def _analyze_learning_style(self, behavior_data: List[UserBehaviorData]) -> Tuple[LearningStyleType, float]:
        """Analyze learning style based on behavior patterns."""
        # Simple heuristic-based analysis
        # In a real implementation, this would use more sophisticated ML algorithms
        
        visual_indicators = 0
        reading_indicators = 0
        interactive_indicators = 0
        
        for data in behavior_data:
            if data.metadata:
                content_type = data.metadata.get("content_type", "")
                if "image" in content_type or "video" in content_type:
                    visual_indicators += 1
                elif "text" in content_type or "article" in content_type:
                    reading_indicators += 1
                elif "interactive" in content_type or data.event_type == EventType.CONTENT_INTERACTION:
                    interactive_indicators += 1
        
        total_indicators = visual_indicators + reading_indicators + interactive_indicators
        if total_indicators == 0:
            return LearningStyleType.UNKNOWN, 0.0
        
        # Determine dominant style
        if visual_indicators > reading_indicators and visual_indicators > interactive_indicators:
            confidence = visual_indicators / total_indicators
            return LearningStyleType.VISUAL, confidence
        elif reading_indicators > interactive_indicators:
            confidence = reading_indicators / total_indicators
            return LearningStyleType.READING, confidence
        elif interactive_indicators > 0:
            confidence = interactive_indicators / total_indicators
            return LearningStyleType.KINESTHETIC, confidence
        else:
            return LearningStyleType.MIXED, 0.5
    
    def _calculate_optimal_session_duration(self, behavior_data: List[UserBehaviorData]) -> Optional[int]:
        """Calculate optimal session duration in minutes."""
        session_durations = {}
        
        for data in behavior_data:
            if data.session_id not in session_durations:
                session_durations[data.session_id] = []
            session_durations[data.session_id].append(data.timestamp)
        
        durations = []
        for session_id, timestamps in session_durations.items():
            if len(timestamps) > 1:
                timestamps.sort()
                duration = (timestamps[-1] - timestamps[0]).total_seconds() / 60  # Convert to minutes
                if 5 <= duration <= 240:  # Between 5 minutes and 4 hours
                    durations.append(duration)
        
        if durations:
            return int(sum(durations) / len(durations))
        return None
    
    def _analyze_preferred_learning_times(self, behavior_data: List[UserBehaviorData]) -> Optional[List[int]]:
        """Analyze preferred learning times (hours of day)."""
        hour_counts = {}
        
        for data in behavior_data:
            hour = data.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return None
        
        # Find hours with above-average activity
        avg_activity = sum(hour_counts.values()) / len(hour_counts)
        preferred_hours = [hour for hour, count in hour_counts.items() if count > avg_activity]
        
        return preferred_hours if preferred_hours else None
    
    def _calculate_attention_span(self, behavior_data: List[UserBehaviorData]) -> Optional[int]:
        """Calculate average attention span in minutes."""
        attention_spans = []
        
        # Group by session and calculate time between interactions
        sessions = {}
        for data in behavior_data:
            if data.session_id not in sessions:
                sessions[data.session_id] = []
            sessions[data.session_id].append(data.timestamp)
        
        for session_id, timestamps in sessions.items():
            if len(timestamps) > 1:
                timestamps.sort()
                # Calculate gaps between interactions
                for i in range(1, len(timestamps)):
                    gap = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
                    if gap <= 60:  # Only consider gaps up to 1 hour
                        attention_spans.append(gap)
        
        if attention_spans:
            return int(sum(attention_spans) / len(attention_spans))
        return None
    
    def _analyze_content_preferences(self, behavior_data: List[UserBehaviorData]) -> Optional[List[str]]:
        """Analyze preferred content types."""
        content_types = {}
        
        for data in behavior_data:
            if data.metadata and "content_type" in data.metadata:
                content_type = data.metadata["content_type"]
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        if not content_types:
            return None
        
        # Return top 3 content types
        sorted_types = sorted(content_types.items(), key=lambda x: x[1], reverse=True)
        return [content_type for content_type, _ in sorted_types[:3]]
    
    def _analyze_difficulty_progression(self, behavior_data: List[UserBehaviorData]) -> Optional[float]:
        """Analyze difficulty progression rate."""
        # Simple implementation - in practice, this would be more sophisticated
        completion_events = [
            data for data in behavior_data 
            if data.event_type in [EventType.CHAPTER_COMPLETE, EventType.ASSESSMENT_COMPLETE]
        ]
        
        if len(completion_events) < 2:
            return None
        
        # Calculate average time between completions
        completion_events.sort(key=lambda x: x.timestamp)
        time_diffs = []
        
        for i in range(1, len(completion_events)):
            diff = (completion_events[i].timestamp - completion_events[i-1].timestamp).total_seconds() / 3600
            time_diffs.append(diff)
        
        if time_diffs:
            avg_time = sum(time_diffs) / len(time_diffs)
            # Normalize to 0-1 scale (faster completion = higher progression rate)
            return max(0.0, min(1.0, 1.0 / (avg_time / 24)))  # 24 hours as baseline
        
        return 0.5  # Default moderate progression rate
    
    def _analyze_topic_performance(self, behavior_data: List[UserBehaviorData]) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """Analyze strong and challenging topics based on behavior."""
        # This is a simplified implementation
        # In practice, this would analyze completion rates, time spent, etc. by topic
        
        topic_performance = {}
        
        for data in behavior_data:
            if data.metadata and "topic" in data.metadata:
                topic = data.metadata["topic"]
                if topic not in topic_performance:
                    topic_performance[topic] = {"completions": 0, "attempts": 0}
                
                if data.event_type in [EventType.CHAPTER_COMPLETE, EventType.ASSESSMENT_COMPLETE]:
                    topic_performance[topic]["completions"] += 1
                elif data.event_type in [EventType.CHAPTER_START, EventType.ASSESSMENT_START]:
                    topic_performance[topic]["attempts"] += 1
        
        strong_topics = []
        challenging_topics = []
        
        for topic, performance in topic_performance.items():
            if performance["attempts"] > 0:
                success_rate = performance["completions"] / performance["attempts"]
                if success_rate >= 0.8:
                    strong_topics.append(topic)
                elif success_rate <= 0.4:
                    challenging_topics.append(topic)
        
        return (strong_topics if strong_topics else None, 
                challenging_topics if challenging_topics else None)