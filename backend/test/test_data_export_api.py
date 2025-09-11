"""
Tests for data export API endpoints including user data export,
course analytics, and admin dashboard functionality.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from backend.src.main import app
from backend.src.db.models.db_user import User
from backend.src.db.models.db_course import Course


class TestDataExportAPI:
    """Test cases for data export API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock(spec=User)
        user.id = "test_user_123"
        user.is_admin = False
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock admin user for testing."""
        user = Mock(spec=User)
        user.id = "admin_user_123"
        user.is_admin = True
        return user
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers."""
        return {"Authorization": "Bearer test_token"}
    
    def test_request_data_export_success(self, client, mock_user, auth_headers):
        """Test successful data export request."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            export_request = {
                "user_id": mock_user.id,
                "data_types": ["behavior_data", "learning_patterns"],
                "format": "json",
                "include_metadata": True
            }
            
            response = client.post(
                "/data-export/request",
                json=export_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["status"] == "in_progress"
    
    def test_request_data_export_forbidden(self, client, mock_user, auth_headers):
        """Test forbidden data export for another user."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            export_request = {
                "user_id": "other_user_456",
                "data_types": ["behavior_data"],
                "format": "json",
                "include_metadata": True
            }
            
            response = client.post(
                "/data-export/request",
                json=export_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_request_data_export_admin_access(self, client, mock_admin_user, auth_headers):
        """Test admin can export any user's data."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_admin_user):
            
            export_request = {
                "user_id": "other_user_456",
                "data_types": ["behavior_data"],
                "format": "json",
                "include_metadata": True
            }
            
            response = client.post(
                "/data-export/request",
                json=export_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_get_course_analytics_success(self, client, mock_user, auth_headers):
        """Test successful course analytics retrieval."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.export_service') as mock_service:
            
            # Mock analytics data
            mock_analytics = {
                "course_ids": [1],
                "total_learners": 25,
                "engagement_summary": {
                    "total_sessions": 100,
                    "average_session_duration": 1800,
                    "total_time_spent": 180000,
                    "average_engagement_score": 0.75
                },
                "learning_patterns": {
                    "learning_style_distribution": {"visual": 15, "reading": 10}
                },
                "completion_rates": {
                    "1": {"starts": 25, "completions": 20, "completion_rate": 0.8}
                },
                "time_period": {
                    "start": datetime.now(timezone.utc).isoformat(),
                    "end": datetime.now(timezone.utc).isoformat(),
                    "days": 30
                }
            }
            
            mock_service.get_aggregated_analytics_for_course_creator.return_value = mock_analytics
            
            response = client.get(
                "/data-export/course-analytics/1?days=30",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["course_id"] == 1
            assert data["analytics"]["total_learners"] == 25
            assert data["analytics"]["engagement_summary"]["total_sessions"] == 100
    
    def test_get_course_analytics_unauthorized(self, client, mock_user, auth_headers):
        """Test unauthorized course analytics access."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.export_service') as mock_service:
            
            # Mock service raising ValueError for unauthorized access
            mock_service.get_aggregated_analytics_for_course_creator.side_effect = ValueError(
                "Course not found or not owned by creator"
            )
            
            response = client.get(
                "/data-export/course-analytics/999",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_creator_analytics_success(self, client, mock_user, auth_headers):
        """Test successful creator analytics retrieval."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.export_service') as mock_service:
            
            # Mock analytics data for all creator's courses
            mock_analytics = {
                "course_ids": [1, 2, 3],
                "total_learners": 75,
                "engagement_summary": {
                    "total_sessions": 300,
                    "average_session_duration": 1800,
                    "total_time_spent": 540000,
                    "average_engagement_score": 0.78
                },
                "learning_patterns": {},
                "completion_rates": {},
                "time_period": {
                    "start": datetime.now(timezone.utc).isoformat(),
                    "end": datetime.now(timezone.utc).isoformat(),
                    "days": 30
                }
            }
            
            mock_service.get_aggregated_analytics_for_course_creator.return_value = mock_analytics
            
            response = client.get(
                "/data-export/creator-analytics?days=30",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["creator_id"] == mock_user.id
            assert data["analytics"]["total_learners"] == 75
            assert len(data["analytics"]["course_ids"]) == 3
    
    def test_get_admin_dashboard_success(self, client, mock_admin_user, auth_headers):
        """Test successful admin dashboard retrieval."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_admin_user), \
             patch('backend.src.api.routers.data_export.export_service') as mock_service:
            
            # Mock admin dashboard data
            mock_dashboard = {
                "platform_overview": {
                    "total_users": 500,
                    "total_courses": 150,
                    "active_users_period": 200,
                    "total_sessions_period": 1000
                },
                "activity_summary": {
                    "total_events": 25000,
                    "total_time_spent_hours": 5000,
                    "average_session_duration": 30
                },
                "learning_insights": {
                    "learning_style_distribution": {
                        "visual": 200,
                        "reading": 150,
                        "kinesthetic": 100,
                        "mixed": 50
                    }
                },
                "privacy_compliance": {
                    "total_behavior_records": 50000,
                    "anonymized_records": 5000,
                    "anonymization_rate": 10.0
                },
                "time_period": {
                    "start": datetime.now(timezone.utc).isoformat(),
                    "end": datetime.now(timezone.utc).isoformat(),
                    "days": 30
                }
            }
            
            mock_service.get_admin_analytics_dashboard.return_value = mock_dashboard
            
            response = client.get(
                "/data-export/admin-dashboard?days=30",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["dashboard"]["platform_overview"]["total_users"] == 500
            assert data["dashboard"]["privacy_compliance"]["anonymization_rate"] == 10.0
            assert data["generated_by"] == mock_admin_user.id
    
    def test_get_admin_dashboard_forbidden(self, client, mock_user, auth_headers):
        """Test forbidden admin dashboard access for non-admin."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            response = client.get(
                "/data-export/admin-dashboard",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_export_status(self, client, mock_user, auth_headers):
        """Test export status retrieval."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            export_id = "test_export_123"
            response = client.get(
                f"/data-export/export-status/{export_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["export_id"] == export_id
            assert "status" in data
            assert "progress" in data
    
    def test_delete_export_file(self, client, mock_user, auth_headers):
        """Test export file deletion."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            export_id = "test_export_123"
            response = client.delete(
                f"/data-export/export/{export_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["export_id"] == export_id
            assert data["deleted"] is True
    
    def test_get_analytics_summary_success(self, client, mock_user, auth_headers):
        """Test successful analytics summary retrieval."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.analytics_crud') as mock_crud:
            
            # Mock CRUD operations
            mock_crud.count_user_behavior_data.return_value = 150
            mock_crud.get_learning_patterns_by_user.return_value = [Mock(), Mock()]
            mock_crud.get_user_learning_profile.return_value = Mock()
            mock_crud.get_user_engagement_metrics.return_value = [Mock(), Mock(), Mock()]
            
            response = client.get(
                "/data-export/analytics-summary",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["data_summary"]["behavior_events"] == 150
            assert data["data_summary"]["learning_patterns"] == 2
            assert data["data_summary"]["has_learning_profile"] is True
            assert data["data_summary"]["engagement_metrics"] == 3
            assert "available_exports" in data
            assert "export_formats" in data
    
    def test_get_course_engagement_trends_success(self, client, mock_user, auth_headers):
        """Test successful course engagement trends retrieval."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.courses_crud') as mock_courses_crud, \
             patch('backend.src.api.routers.data_export.analytics_crud') as mock_analytics_crud:
            
            # Mock course ownership verification
            mock_course = Mock()
            mock_course.user_id = mock_user.id
            mock_course.title = "Test Course"
            mock_courses_crud.get_course_by_id.return_value = mock_course
            
            # Mock engagement trends data
            mock_trends = [
                {
                    "date": "2023-01-01",
                    "event_count": 50,
                    "session_count": 10,
                    "total_duration": 3600
                },
                {
                    "date": "2023-01-02",
                    "event_count": 75,
                    "session_count": 15,
                    "total_duration": 5400
                }
            ]
            mock_analytics_crud.get_user_activity_timeline.return_value = mock_trends
            
            response = client.get(
                "/data-export/course-engagement-trends/1?days=30",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["course_id"] == 1
            assert data["course_title"] == "Test Course"
            assert len(data["engagement_trends"]) == 2
            assert data["time_period"]["days"] == 30
    
    def test_get_course_engagement_trends_unauthorized(self, client, mock_user, auth_headers):
        """Test unauthorized course engagement trends access."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.courses_crud') as mock_courses_crud:
            
            # Mock course owned by different user
            mock_course = Mock()
            mock_course.user_id = "other_user_456"
            mock_courses_crud.get_course_by_id.return_value = mock_course
            
            response = client.get(
                "/data-export/course-engagement-trends/1",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_download_export_file_not_implemented(self, client, mock_user, auth_headers):
        """Test download export file endpoint (not yet implemented)."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            export_id = "test_export_123"
            response = client.get(
                f"/data-export/download/{export_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED


class TestDataExportAPIValidation:
    """Test input validation for data export API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock(spec=User)
        user.id = "test_user_123"
        user.is_admin = False
        return user
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers."""
        return {"Authorization": "Bearer test_token"}
    
    def test_export_request_validation(self, client, mock_user, auth_headers):
        """Test validation of export request data."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user):
            
            # Test invalid export requests
            invalid_requests = [
                {
                    "user_id": "",  # Empty user ID
                    "data_types": ["behavior_data"],
                    "format": "json"
                },
                {
                    "user_id": mock_user.id,
                    "data_types": [],  # Empty data types
                    "format": "json"
                },
                {
                    "user_id": mock_user.id,
                    "data_types": ["invalid_type"],  # Invalid data type
                    "format": "json"
                },
                {
                    "user_id": mock_user.id,
                    "data_types": ["behavior_data"],
                    "format": "xml"  # Invalid format
                }
            ]
            
            for invalid_request in invalid_requests:
                response = client.post(
                    "/data-export/request",
                    json=invalid_request,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_query_parameter_validation(self, client, mock_user, auth_headers):
        """Test validation of query parameters."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.export_service') as mock_service:
            
            mock_service.get_aggregated_analytics_for_course_creator.return_value = {}
            
            # Test invalid days parameter
            invalid_days = [0, -1, 400]  # Below minimum, negative, above maximum
            
            for days in invalid_days:
                response = client.get(
                    f"/data-export/course-analytics/1?days={days}",
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDataExportAPIErrorHandling:
    """Test error handling in data export API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock(spec=User)
        user.id = "test_user_123"
        user.is_admin = False
        return user
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers."""
        return {"Authorization": "Bearer test_token"}
    
    def test_export_service_error(self, client, mock_user, auth_headers):
        """Test handling of export service errors."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.export_service') as mock_service:
            
            # Mock service error
            mock_service.get_aggregated_analytics_for_course_creator.side_effect = Exception("Service error")
            
            response = client.get(
                "/data-export/course-analytics/1",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_analytics_crud_error(self, client, mock_user, auth_headers):
        """Test handling of analytics CRUD errors."""
        with patch('backend.src.api.routers.data_export.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.data_export.analytics_crud') as mock_crud:
            
            # Mock CRUD error
            mock_crud.count_user_behavior_data.side_effect = Exception("Database error")
            
            response = client.get(
                "/data-export/analytics-summary",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR