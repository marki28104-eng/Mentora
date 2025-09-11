"""
Tests for Advanced Analytics API endpoints.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.src.main import app
from backend.src.services.advanced_analytics_service import (
    PredictiveOutcome, CohortAnalysis, RealTimePersonalization
)
from backend.src.db.models.db_user import User


class TestAdvancedAnalyticsAPI:
    """Test cases for Advanced Analytics API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        return User(
            id="user_1",
            email="test@example.com",
            username="testuser",
            is_admin=False,
            is_active=True
        )
    
    @pytest.fixture
    def mock_admin_user(self):
        return User(
            id="admin_1",
            email="admin@example.com",
            username="admin",
            is_admin=True,
            is_active=True
        )
    
    @pytest.fixture
    def mock_prediction(self):
        return PredictiveOutcome(
            user_id="user_1",
            prediction_type="learning_outcome",
            predicted_value=0.8,
            confidence=0.7,
            factors={
                'engagement': 0.6,
                'difficulty_preference': 0.4,
                'session_frequency': 0.3
            },
            recommendations=[
                "Continue with current difficulty level",
                "Add more interactive elements"
            ]
        )
    
    @pytest.fixture
    def mock_cohort_analysis(self):
        return CohortAnalysis(
            cohort_name="visual_learners",
            cohort_size=25,
            time_period="2024-01 to 2024-03",
            retention_rates={
                'week_1': 0.9,
                'week_2': 0.8,
                'week_4': 0.7
            },
            engagement_trends={
                'month_1': 0.8,
                'month_2': 0.75,
                'month_3': 0.7
            },
            learning_patterns={
                'learning_styles_distribution': {'visual': 25},
                'avg_session_duration': 35.5,
                'avg_completion_rate': 0.78
            },
            performance_metrics={
                'avg_completion_rate': 0.78,
                'avg_engagement_score': 0.75,
                'high_performers_pct': 0.6
            }
        )
    
    @pytest.fixture
    def mock_personalization(self):
        return RealTimePersonalization(
            user_id="user_1",
            session_id="session_123",
            adjustments={
                'difficulty_increase': {
                    'increase_challenge': True,
                    'add_bonus_content': True,
                    'increase_difficulty_by': 0.1
                }
            },
            trigger_events=['fast_progress'],
            confidence=0.8
        )
    
    def test_initialize_advanced_analytics_success(self, client, mock_admin_user):
        """Test successful initialization of advanced analytics."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_admin_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.initialize_models') as mock_init:
                mock_init.return_value = {'status': 'success'}
                
                response = client.post("/advanced-analytics/initialize")
                
                assert response.status_code == 200
                data = response.json()
                assert data['message'] == "Advanced analytics initialization started"
                assert data['status'] == "processing"
    
    def test_initialize_advanced_analytics_non_admin(self, client, mock_user):
        """Test initialization with non-admin user."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            response = client.post("/advanced-analytics/initialize")
            
            assert response.status_code == 403
            assert "Admin access required" in response.json()['detail']
    
    def test_predict_learning_outcome_success(self, client, mock_user, mock_prediction):
        """Test successful learning outcome prediction."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.get_learning_outcome_prediction') as mock_predict:
                mock_predict.return_value = mock_prediction
                
                response = client.get("/advanced-analytics/predict-outcome/1")
                
                assert response.status_code == 200
                data = response.json()
                assert data['user_id'] == "user_1"
                assert data['prediction_type'] == "learning_outcome"
                assert data['predicted_value'] == 0.8
                assert data['confidence'] == 0.7
                assert 'factors' in data
                assert 'recommendations' in data
    
    def test_predict_learning_outcome_no_prediction(self, client, mock_user):
        """Test learning outcome prediction when no prediction available."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.get_learning_outcome_prediction') as mock_predict:
                mock_predict.return_value = None
                
                response = client.get("/advanced-analytics/predict-outcome/1")
                
                assert response.status_code == 200
                assert response.json() is None
    
    def test_get_cohort_analysis_success(self, client, mock_admin_user, mock_cohort_analysis):
        """Test successful cohort analysis."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_admin_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.analyze_cohorts') as mock_analyze:
                mock_analyze.return_value = [mock_cohort_analysis]
                
                response = client.get("/advanced-analytics/cohort-analysis?cohort_type=learning_style")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]['cohort_name'] == "visual_learners"
                assert data[0]['cohort_size'] == 25
                assert 'retention_rates' in data[0]
                assert 'engagement_trends' in data[0]
    
    def test_get_cohort_analysis_non_admin(self, client, mock_user):
        """Test cohort analysis with non-admin user."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            response = client.get("/advanced-analytics/cohort-analysis")
            
            assert response.status_code == 403
            assert "Admin access required" in response.json()['detail']
    
    def test_process_real_time_event_success(self, client, mock_user, mock_personalization):
        """Test successful real-time event processing."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.process_real_time_event') as mock_process:
                mock_process.return_value = mock_personalization
                
                event_request = {
                    "session_id": "session_123",
                    "event_data": {
                        "event_type": "content_interaction",
                        "interaction_type": "quiz_completion",
                        "score": 0.9,
                        "time_spent": 120
                    }
                }
                
                response = client.post("/advanced-analytics/real-time-event", json=event_request)
                
                assert response.status_code == 200
                data = response.json()
                assert data['user_id'] == "user_1"
                assert data['session_id'] == "session_123"
                assert 'adjustments' in data
                assert 'trigger_events' in data
                assert data['confidence'] == 0.8
    
    def test_process_real_time_event_no_adjustments(self, client, mock_user):
        """Test real-time event processing with no adjustments needed."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.process_real_time_event') as mock_process:
                mock_process.return_value = None
                
                event_request = {
                    "session_id": "session_123",
                    "event_data": {
                        "event_type": "page_view",
                        "page_url": "/courses/1"
                    }
                }
                
                response = client.post("/advanced-analytics/real-time-event", json=event_request)
                
                assert response.status_code == 200
                assert response.json() is None
    
    def test_process_real_time_event_invalid_data(self, client, mock_user):
        """Test real-time event processing with invalid event data."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            event_request = {
                "session_id": "session_123",
                "event_data": {
                    # Missing required event_type
                    "page_url": "/courses/1"
                }
            }
            
            response = client.post("/advanced-analytics/real-time-event", json=event_request)
            
            assert response.status_code == 422  # Validation error
    
    def test_process_real_time_event_pii_filtering(self, client, mock_user):
        """Test that PII is filtered from event data."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.process_real_time_event') as mock_process:
                mock_process.return_value = None
                
                event_request = {
                    "session_id": "session_123",
                    "event_data": {
                        "event_type": "content_interaction",
                        "email": "user@example.com",  # Should be filtered out
                        "name": "John Doe",  # Should be filtered out
                        "interaction_type": "quiz",  # Should be kept
                        "score": 0.8  # Should be kept
                    }
                }
                
                response = client.post("/advanced-analytics/real-time-event", json=event_request)
                
                # Should succeed but PII should be filtered
                assert response.status_code == 200
                
                # Check that the service was called with filtered data
                mock_process.assert_called_once()
                call_args = mock_process.call_args[1]
                event_data = call_args['event_data']
                
                assert 'email' not in event_data
                assert 'name' not in event_data
                assert 'event_type' in event_data
                assert 'interaction_type' in event_data
                assert 'score' in event_data
    
    def test_get_user_predictions(self, client, mock_user):
        """Test getting user predictions."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            response = client.get("/advanced-analytics/user-predictions")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            # Currently returns empty list as predictions are generated on-demand
            assert len(data) == 0
    
    def test_cleanup_sessions_success(self, client, mock_admin_user):
        """Test successful session cleanup."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_admin_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.cleanup_session_data') as mock_cleanup:
                response = client.post("/advanced-analytics/cleanup-sessions")
                
                assert response.status_code == 200
                data = response.json()
                assert data['message'] == "Session data cleanup completed"
                assert data['status'] == "success"
                mock_cleanup.assert_called_once()
    
    def test_cleanup_sessions_non_admin(self, client, mock_user):
        """Test session cleanup with non-admin user."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            response = client.post("/advanced-analytics/cleanup-sessions")
            
            assert response.status_code == 403
            assert "Admin access required" in response.json()['detail']
    
    def test_get_analytics_status(self, client, mock_user):
        """Test getting analytics status."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            response = client.get("/advanced-analytics/analytics-status")
            
            assert response.status_code == 200
            data = response.json()
            assert 'predictive_models' in data
            assert 'cohort_analysis' in data
            assert 'real_time_personalization' in data
            
            # Check structure
            assert 'completion_predictor' in data['predictive_models']
            assert 'available' in data['cohort_analysis']
            assert 'active_sessions' in data['real_time_personalization']
    
    def test_get_available_cohort_types(self, client, mock_user):
        """Test getting available cohort types."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            response = client.get("/advanced-analytics/cohort-types")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 4  # Should have 4 cohort types
            
            # Check structure
            for cohort_type in data:
                assert 'type' in cohort_type
                assert 'description' in cohort_type
            
            # Check specific types
            types = [ct['type'] for ct in data]
            assert 'registration_month' in types
            assert 'learning_style' in types
            assert 'difficulty_level' in types
            assert 'engagement_level' in types
    
    def test_api_error_handling(self, client, mock_user):
        """Test API error handling."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.get_learning_outcome_prediction') as mock_predict:
                mock_predict.side_effect = Exception("Database error")
                
                response = client.get("/advanced-analytics/predict-outcome/1")
                
                assert response.status_code == 500
                assert "Failed to generate prediction" in response.json()['detail']
    
    def test_cohort_analysis_error_handling(self, client, mock_admin_user):
        """Test cohort analysis error handling."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_admin_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.analyze_cohorts') as mock_analyze:
                mock_analyze.side_effect = Exception("Analysis error")
                
                response = client.get("/advanced-analytics/cohort-analysis")
                
                assert response.status_code == 500
                assert "Failed to perform cohort analysis" in response.json()['detail']
    
    def test_real_time_event_error_handling(self, client, mock_user):
        """Test real-time event processing error handling."""
        with patch('backend.src.core.security.get_current_user', return_value=mock_user):
            with patch('backend.src.api.routers.advanced_analytics.advanced_analytics_service.process_real_time_event') as mock_process:
                mock_process.side_effect = Exception("Processing error")
                
                event_request = {
                    "session_id": "session_123",
                    "event_data": {
                        "event_type": "content_interaction"
                    }
                }
                
                response = client.post("/advanced-analytics/real-time-event", json=event_request)
                
                assert response.status_code == 500
                assert "Failed to process real-time event" in response.json()['detail']


if __name__ == "__main__":
    pytest.main([__file__])