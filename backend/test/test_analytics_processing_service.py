"""Unit tests for AnalyticsProcessingService."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.analytics_processing_service import AnalyticsProcessingService
from db.models.db_analytics import EventType, LearningStyleType, UserBehaviorData
from utils.analytics_utils import generate_analytics_id


class TestAnalyticsProcessingService:
    """Test cases for AnalyticsProcessingService."""
    
    @pytest.fixture
    def service(self):
        """Create AnalyticsProcessingService instance for testing."""
        return AnalyticsProcessingService()
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_umami_data(self):
        """Sample Umami analytics data for testing."""
        return [
            {
                "event_type": "page_view",
                "url": "/courses/123/chapters/456",
                "timestamp": datetime.now(timezone.utc),
                "session_id": "sess_123",
                "user_id": "user_456",
                "metadata": {
                    "content_type": "text",
                    "duration": 300
                }
            },
            {
                "event_type": "course_complete",
                "url": "/courses/123",
                "timestamp": datetime.now(timezone.utc),
                "session_id": "sess_123",
                "user_id": "user_456",
                "metadata": {
                    "score": 85,
                    "completion_time": 1800
                }
            }
        ]
    
    @pytest.fixture
    def sample_behavior_data(self):
        """Sample UserBehaviorData for testing."""
        return [
            UserBehaviorData(
                id=generate_analytics_id(),
                user_id="user_123",
                session_id="sess_456",
                event_type=EventType.PAGE_VIEW,
                page_url="/courses/1/chapters/1",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
                metadata={"content_type": "text"},
                duration_seconds=300
            ),
            UserBehaviorData(
                id=generate_analytics_id(),
                user_id="user_123",
                session_id="sess_456",
                event_type=EventType.CHAPTER_COMPLETE,
                page_url="/courses/1/chapters/1",
                timestamp=datetime.now(timezone.utc),
                metadata={"score": 90},
                duration_seconds=1800
            )
        ]
    
    def test_map_event_type(self, service):
        """Test event type mapping."""
        assert service._map_event_type("page_view") == EventType.PAGE_VIEW
        assert service._map_event_type("course_start") == EventType.COURSE_START
        assert service._map_event_type("unknown_event") == EventType.PAGE_VIEW  # Default
    
    def test_extract_course_info_from_url(self, service):
        """Test course and chapter ID extraction from URLs."""
        # Test course and chapter URL
        course_id, chapter_id = service._extract_course_info_from_url("/courses/123/chapters/456")
        assert course_id == 123
        assert chapter_id == 456
        
        # Test course only URL
        course_id, chapter_id = service._extract_course_info_from_url("/courses/789")
        assert course_id == 789
        assert chapter_id is None
        
        # Test invalid URL
        course_id, chapter_id = service._extract_course_info_from_url("/invalid/url")
        assert course_id is None
        assert chapter_id is None
    
    def test_analyze_learning_style_visual(self, service):
        """Test learning style analysis for visual learner."""
        behavior_data = [
            Mock(metadata={"content_type": "image"}),
            Mock(metadata={"content_type": "video"}),
            Mock(metadata={"content_type": "text"}),
        ]
        
        style, confidence = service._analyze_learning_style(behavior_data)
        assert style == LearningStyleType.VISUAL
        assert confidence > 0.5
    
    def test_analyze_learning_style_reading(self, service):
        """Test learning style analysis for reading learner."""
        behavior_data = [
            Mock(metadata={"content_type": "text"}),
            Mock(metadata={"content_type": "article"}),
            Mock(metadata={"content_type": "image"}),
        ]
        
        style, confidence = service._analyze_learning_style(behavior_data)
        assert style == LearningStyleType.READING
        assert confidence > 0.5
    
    def test_analyze_learning_style_insufficient_data(self, service):
        """Test learning style analysis with insufficient data."""
        behavior_data = [Mock(metadata=None)]
        
        style, confidence = service._analyze_learning_style(behavior_data)
        assert style == LearningStyleType.UNKNOWN
        assert confidence == 0.0
    
    def test_calculate_optimal_session_duration(self, service):
        """Test optimal session duration calculation."""
        now = datetime.now(timezone.utc)
        behavior_data = [
            Mock(session_id="sess1", timestamp=now),
            Mock(session_id="sess1", timestamp=now + timedelta(minutes=30)),
            Mock(session_id="sess2", timestamp=now),
            Mock(session_id="sess2", timestamp=now + timedelta(minutes=45)),
        ]
        
        duration = service._calculate_optimal_session_duration(behavior_data)
        assert duration is not None
        assert 30 <= duration <= 45  # Should be average of 30 and 45
    
    def test_analyze_preferred_learning_times(self, service):
        """Test preferred learning times analysis."""
        # Create behavior data with specific hours
        behavior_data = [
            Mock(timestamp=datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)),  # 9 AM
            Mock(timestamp=datetime(2024, 1, 1, 9, 30, tzinfo=timezone.utc)), # 9 AM
            Mock(timestamp=datetime(2024, 1, 1, 14, 0, tzinfo=timezone.utc)), # 2 PM
            Mock(timestamp=datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)), # 8 PM
        ]
        
        preferred_times = service._analyze_preferred_learning_times(behavior_data)
        assert preferred_times is not None
        assert 9 in preferred_times  # 9 AM should be preferred (appears twice)
    
    def test_calculate_attention_span(self, service):
        """Test attention span calculation."""
        now = datetime.now(timezone.utc)
        behavior_data = [
            Mock(session_id="sess1", timestamp=now),
            Mock(session_id="sess1", timestamp=now + timedelta(minutes=10)),
            Mock(session_id="sess1", timestamp=now + timedelta(minutes=20)),
        ]
        
        attention_span = service._calculate_attention_span(behavior_data)
        assert attention_span is not None
        assert attention_span == 15  # Average of 10 and 10 minute gaps
    
    def test_analyze_content_preferences(self, service):
        """Test content preferences analysis."""
        behavior_data = [
            Mock(metadata={"content_type": "video"}),
            Mock(metadata={"content_type": "video"}),
            Mock(metadata={"content_type": "text"}),
            Mock(metadata={"content_type": "interactive"}),
        ]
        
        preferences = service._analyze_content_preferences(behavior_data)
        assert preferences is not None
        assert "video" in preferences  # Should be top preference
    
    def test_analyze_difficulty_progression_insufficient_data(self, service):
        """Test difficulty progression with insufficient data."""
        behavior_data = [
            Mock(event_type=EventType.CHAPTER_COMPLETE, timestamp=datetime.now(timezone.utc))
        ]
        
        progression_rate = service._analyze_difficulty_progression(behavior_data)
        assert progression_rate is None
    
    def test_analyze_topic_performance(self, service):
        """Test topic performance analysis."""
        behavior_data = [
            Mock(
                event_type=EventType.CHAPTER_START,
                metadata={"topic": "mathematics"}
            ),
            Mock(
                event_type=EventType.CHAPTER_COMPLETE,
                metadata={"topic": "mathematics"}
            ),
            Mock(
                event_type=EventType.CHAPTER_START,
                metadata={"topic": "physics"}
            ),
            # No completion for physics - should be challenging
        ]
        
        strong_topics, challenging_topics = service._analyze_topic_performance(behavior_data)
        assert strong_topics is not None
        assert "mathematics" in strong_topics
        assert challenging_topics is not None
        assert "physics" in challenging_topics
    
    @pytest.mark.asyncio
    async def test_fetch_umami_data_missing_config(self, service):
        """Test Umami data fetching with missing configuration."""
        service.umami_api_url = None
        service.umami_api_token = None
        
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc)
        
        result = await service.fetch_umami_data(start_date, end_date)
        assert result == []
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_fetch_umami_data_success(self, mock_client, service):
        """Test successful Umami data fetching."""
        # Mock the HTTP client
        mock_response = Mock()
        mock_response.json.return_value = {
            "pageviews": [
                {
                    "url": "/test",
                    "created_at": 1640995200000,  # 2022-01-01 00:00:00 UTC
                    "session_id": "sess123",
                    "user_id": "user456"
                }
            ],
            "events": []
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        service.umami_api_url = "https://test-umami.com"
        service.umami_api_token = "test-token"
        service.umami_website_id = "test-website"
        
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc)
        
        result = await service.fetch_umami_data(start_date, end_date)
        
        assert len(result) == 1
        assert result[0]["event_type"] == "page_view"
        assert result[0]["url"] == "/test"
    
    @patch('backend.src.db.crud.analytics_crud.create_user_behavior_data')
    @patch('backend.src.db.crud.analytics_crud.get_user_behavior_data')
    def test_calculate_engagement_metrics(self, mock_get_behavior, mock_create_metrics, service, mock_db, sample_behavior_data):
        """Test engagement metrics calculation."""
        mock_get_behavior.return_value = sample_behavior_data
        mock_create_metrics.return_value = Mock()
        
        result = service.calculate_engagement_metrics(mock_db, "user_123", 24)
        
        assert mock_get_behavior.called
        assert mock_create_metrics.called
    
    @patch('backend.src.db.crud.analytics_crud.get_user_behavior_data')
    @patch('backend.src.db.crud.analytics_crud.get_learning_pattern_by_user')
    @patch('backend.src.db.crud.analytics_crud.create_learning_pattern')
    def test_identify_learning_patterns_new_user(self, mock_create_pattern, mock_get_pattern, mock_get_behavior, service, mock_db, sample_behavior_data):
        """Test learning pattern identification for new user."""
        mock_get_behavior.return_value = sample_behavior_data
        mock_get_pattern.return_value = None  # No existing pattern
        mock_create_pattern.return_value = Mock()
        
        result = service.identify_learning_patterns(mock_db, "user_123")
        
        assert mock_create_pattern.called
        assert result is not None
    
    @patch('backend.src.db.crud.analytics_crud.get_user_behavior_data')
    def test_identify_learning_patterns_insufficient_data(self, mock_get_behavior, service, mock_db):
        """Test learning pattern identification with insufficient data."""
        mock_get_behavior.return_value = []  # No behavior data
        
        result = service.identify_learning_patterns(mock_db, "user_123")
        
        assert result is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])