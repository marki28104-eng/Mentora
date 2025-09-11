"""Integration tests for Analytics API endpoints."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from db.models.db_analytics import EventType, LearningStyleType, DifficultyLevel
from utils.analytics_utils import generate_analytics_id


class TestAnalyticsAPI:
    """Test cases for Analytics API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        return Mock(
            id="test_user_123",
            username="testuser",
            email="test@example.com",
            is_admin=False,
            is_active=True
        )
    
    @pytest.fixture
    def mock_admin_user(self):
        """Create mock admin user for testing."""
        return Mock(
            id="admin_user_123",
            username="adminuser",
            email="admin@example.com",
            is_admin=True,
            is_active=True
        )
    
    @pytest.fixture
    def sample_behavior_data(self):
        """Sample behavior data for testing."""
        return {
            "user_id": "test_user_123",
            "session_id": "sess_456",
            "event_type": "page_view",
            "page_url": "/courses/1/chapters/1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "course_id": 1,
            "chapter_id": 1,
            "metadata": {
                "content_type": "text",
                "duration": 300
            },
            "duration_seconds": 300
        }
    
    @pytest.fixture
    def sample_learning_pattern(self):
        """Sample learning pattern for testing."""
        return {
            "user_id": "test_user_123",
            "pattern_type": "visual",
            "confidence_score": 0.8,
            "preferred_content_types": ["video", "image"],
            "optimal_session_duration": 45,
            "difficulty_progression_rate": 0.6,
            "preferred_learning_times": [9, 14, 20],
            "average_attention_span": 30,
            "strong_topics": ["mathematics", "physics"],
            "challenging_topics": ["chemistry"]
        }
    
    @pytest.fixture
    def sample_learning_profile(self):
        """Sample learning profile for testing."""
        return {
            "user_id": "test_user_123",
            "learning_style": "visual",
            "attention_span": 30,
            "preferred_difficulty": "intermediate",
            "completion_rate": 0.85,
            "average_session_duration": 45,
            "total_learning_time": 1200,
            "courses_completed": 5,
            "engagement_score": 0.75,
            "consistency_score": 0.8,
            "challenge_preference": 0.6,
            "strong_topics": ["mathematics"],
            "challenging_topics": ["chemistry"],
            "preferred_content_formats": ["video", "interactive"],
            "current_difficulty_level": 0.7,
            "adaptation_rate": 0.15
        }
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_create_behavior_data_success(self, mock_get_db, mock_get_user, client, mock_user, sample_behavior_data):
        """Test successful behavior data creation."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data') as mock_create:
            mock_create.return_value = Mock(
                id=generate_analytics_id(),
                **sample_behavior_data,
                engagement_score=0.7,
                is_anonymized=False,
                created_at=datetime.now(timezone.utc)
            )
            
            response = client.post("/analytics/behavior", json=sample_behavior_data)
            
            assert response.status_code == 200
            assert mock_create.called
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_create_behavior_data_forbidden(self, mock_get_db, mock_get_user, client, mock_user, sample_behavior_data):
        """Test behavior data creation with wrong user ID."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # Try to create data for different user
        sample_behavior_data["user_id"] = "different_user"
        
        response = client.post("/analytics/behavior", json=sample_behavior_data)
        
        assert response.status_code == 403
        assert "Cannot submit behavior data for other users" in response.json()["detail"]
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_get_behavior_data_success(self, mock_get_db, mock_get_user, client, mock_user):
        """Test successful behavior data retrieval."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get:
            mock_get.return_value = []
            
            response = client.get("/analytics/behavior")
            
            assert response.status_code == 200
            assert mock_get.called
            # Verify it was called with current user's ID
            mock_get.assert_called_with(
                db=mock_db,
                user_id=mock_user.id,
                event_type=None,
                course_id=None,
                chapter_id=None,
                start_date=None,
                end_date=None,
                limit=100,
                offset=0
            )
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_get_behavior_data_admin_access(self, mock_get_db, mock_get_user, client, mock_admin_user):
        """Test admin user can access other users' data."""
        mock_get_user.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get:
            mock_get.return_value = []
            
            response = client.get("/analytics/behavior?user_id=other_user")
            
            assert response.status_code == 200
            assert mock_get.called
            # Verify it was called with the specified user ID
            args, kwargs = mock_get.call_args
            assert kwargs['user_id'] == 'other_user'
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_get_behavior_data_forbidden_other_user(self, mock_get_db, mock_get_user, client, mock_user):
        """Test regular user cannot access other users' data."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        response = client.get("/analytics/behavior?user_id=other_user")
        
        assert response.status_code == 403
        assert "Cannot access other users' behavior data" in response.json()["detail"]
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_create_learning_pattern_success(self, mock_get_db, mock_get_user, client, mock_user, sample_learning_pattern):
        """Test successful learning pattern creation."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.create_learning_pattern') as mock_create:
            mock_create.return_value = Mock(
                id=generate_analytics_id(),
                **sample_learning_pattern,
                data_points_count=50,
                last_calculated=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            response = client.post("/analytics/learning-patterns", json=sample_learning_pattern)
            
            assert response.status_code == 200
            assert mock_create.called
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_get_learning_profile_success(self, mock_get_db, mock_get_user, client, mock_user):
        """Test successful learning profile retrieval."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get:
            mock_get.return_value = None  # No profile exists
            
            response = client.get("/analytics/learning-profile")
            
            assert response.status_code == 200
            assert mock_get.called
            assert mock_get.call_args[0][1] == mock_user.id  # Called with current user ID
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_create_learning_profile_success(self, mock_get_db, mock_get_user, client, mock_user, sample_learning_profile):
        """Test successful learning profile creation."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_existing:
            mock_get_existing.return_value = None  # No existing profile
            
            with patch('backend.src.db.crud.analytics_crud.create_user_learning_profile') as mock_create:
                mock_create.return_value = Mock(
                    id=generate_analytics_id(),
                    **sample_learning_profile,
                    last_updated=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc)
                )
                
                response = client.post("/analytics/learning-profile", json=sample_learning_profile)
                
                assert response.status_code == 200
                assert mock_create.called
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_create_learning_profile_already_exists(self, mock_get_db, mock_get_user, client, mock_user, sample_learning_profile):
        """Test learning profile creation when profile already exists."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_existing:
            mock_get_existing.return_value = Mock()  # Profile exists
            
            response = client.post("/analytics/learning-profile", json=sample_learning_profile)
            
            assert response.status_code == 400
            assert "Learning profile already exists" in response.json()["detail"]
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_get_analytics_summary_success(self, mock_get_db, mock_get_user, client, mock_user):
        """Test successful analytics summary retrieval."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_user_engagement_summary') as mock_engagement:
            mock_engagement.return_value = {
                'total_sessions': 10,
                'total_time_spent': 3600,
                'average_engagement_score': 0.75,
                'total_interactions': 50,
                'total_page_views': 100
            }
            
            with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_profile:
                mock_profile.return_value = Mock(
                    learning_style=LearningStyleType.VISUAL,
                    preferred_difficulty=DifficultyLevel.INTERMEDIATE
                )
                
                with patch('backend.src.db.crud.analytics_crud.get_user_activity_timeline') as mock_timeline:
                    mock_timeline.return_value = []
                    
                    with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_behavior:
                        mock_behavior.return_value = []
                        
                        response = client.get("/analytics/summary")
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert data["user_id"] == mock_user.id
                        assert "total_events" in data
                        assert "learning_style" in data
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_process_umami_data_admin_only(self, mock_get_db, mock_get_admin, client, mock_admin_user):
        """Test Umami data processing is admin-only."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        response = client.post("/analytics/process-umami-data?website_id=test_website")
        
        assert response.status_code == 200
        assert "processing started" in response.json()["message"]
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_delete_user_analytics_data_success(self, mock_get_db, mock_get_user, client, mock_user):
        """Test successful user analytics data deletion."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.delete_user_behavior_data') as mock_delete_behavior:
            mock_delete_behavior.return_value = 5
            
            with patch('backend.src.db.crud.analytics_crud.delete_learning_patterns') as mock_delete_patterns:
                mock_delete_patterns.return_value = 1
                
                with patch('backend.src.db.crud.analytics_crud.delete_user_learning_profile') as mock_delete_profile:
                    mock_delete_profile.return_value = True
                    
                    with patch('backend.src.db.crud.analytics_crud.delete_engagement_metrics') as mock_delete_metrics:
                        mock_delete_metrics.return_value = 3
                        
                        response = client.delete(f"/analytics/user-data/{mock_user.id}")
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert "deleted successfully" in data["message"]
                        assert data["details"]["behavior_records_deleted"] == 5
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_anonymize_user_analytics_data_success(self, mock_get_db, mock_get_user, client, mock_user):
        """Test successful user analytics data anonymization."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.anonymize_user_analytics_data') as mock_anonymize:
            mock_anonymize.return_value = {
                'anonymized_behavior_records': 5,
                'original_user_id': mock_user.id
            }
            
            response = client.delete(f"/analytics/user-data/{mock_user.id}?anonymize_only=true")
            
            assert response.status_code == 200
            data = response.json()
            assert "anonymized successfully" in data["message"]
            assert data["details"]["anonymized_behavior_records"] == 5
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_get_course_engagement_stats_success(self, mock_get_db, mock_get_user, client, mock_user):
        """Test successful course engagement statistics retrieval."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.db.crud.analytics_crud.get_course_engagement_stats') as mock_get_stats:
            mock_get_stats.return_value = {
                'unique_users': 25,
                'total_events': 150,
                'average_engagement_score': 0.72,
                'total_time_spent': 7200,
                'completion_count': 20,
                'completion_rate': 0.8
            }
            
            response = client.get("/analytics/course-stats/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["unique_users"] == 25
            assert data["completion_rate"] == 0.8


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])