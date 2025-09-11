"""
Tests for privacy API endpoints including GDPR compliance,
consent management, and data deletion functionality.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from backend.src.main import app
from backend.src.db.models.db_user import User


class TestPrivacyAPI:
    """Test cases for privacy API endpoints."""
    
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
    
    def test_get_user_consent_success(self, client, mock_user, auth_headers):
        """Test successful retrieval of user consent."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            # Mock consent status
            mock_service.check_user_consent.return_value = {
                "analytics_collection": True,
                "personalization": False,
                "performance_tracking": True,
                "content_recommendations": False
            }
            
            response = client.get(
                f"/privacy/consent/{mock_user.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["analytics_collection"] is True
            assert data["personalization"] is False
    
    def test_get_user_consent_forbidden(self, client, mock_user, auth_headers):
        """Test forbidden access to another user's consent."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            # Try to access another user's consent
            other_user_id = "other_user_456"
            response = client.get(
                f"/privacy/consent/{other_user_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_user_consent_admin_access(self, client, mock_admin_user, auth_headers):
        """Test admin can access any user's consent."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_admin_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            mock_service.check_user_consent.return_value = {
                "analytics_collection": False,
                "personalization": False,
                "performance_tracking": False,
                "content_recommendations": False
            }
            
            other_user_id = "other_user_456"
            response = client.get(
                f"/privacy/consent/{other_user_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == other_user_id
    
    def test_update_user_consent_success(self, client, mock_user, auth_headers):
        """Test successful consent update."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            # Mock successful update
            mock_service.update_user_consent.return_value = True
            mock_service.check_user_consent.return_value = {
                "analytics_collection": True,
                "personalization": True,
                "performance_tracking": False,
                "content_recommendations": True
            }
            
            consent_update = {
                "analytics_collection": True,
                "personalization": True,
                "content_recommendations": True
            }
            
            response = client.put(
                f"/privacy/consent/{mock_user.id}",
                json=consent_update,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["analytics_collection"] is True
            assert data["personalization"] is True
    
    def test_update_user_consent_user_not_found(self, client, mock_user, auth_headers):
        """Test consent update for non-existent user."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            # Mock user not found
            mock_service.update_user_consent.return_value = False
            
            consent_update = {"analytics_collection": True}
            
            response = client.put(
                f"/privacy/consent/{mock_user.id}",
                json=consent_update,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_request_data_deletion_success(self, client, mock_user, auth_headers):
        """Test successful data deletion request."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            deletion_request = {
                "user_id": mock_user.id,
                "deletion_type": "anonymize",
                "reason": "User requested data removal",
                "confirm_deletion": True
            }
            
            response = client.post(
                "/privacy/delete-data",
                json=deletion_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["deletion_type"] == "anonymize"
            assert data["status"] == "in_progress"
    
    def test_request_data_deletion_forbidden(self, client, mock_user, auth_headers):
        """Test forbidden data deletion for another user."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            deletion_request = {
                "user_id": "other_user_456",
                "deletion_type": "hard_delete",
                "confirm_deletion": True
            }
            
            response = client.post(
                "/privacy/delete-data",
                json=deletion_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_request_data_deletion_invalid_confirmation(self, client, mock_user, auth_headers):
        """Test data deletion without confirmation."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            deletion_request = {
                "user_id": mock_user.id,
                "deletion_type": "anonymize",
                "confirm_deletion": False  # Invalid
            }
            
            response = client.post(
                "/privacy/delete-data",
                json=deletion_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_privacy_report_success(self, client, mock_user, auth_headers):
        """Test successful privacy report generation."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            # Mock privacy report
            mock_report = {
                "user_id": mock_user.id,
                "consent_status": {
                    "analytics_collection": True,
                    "personalization": False,
                    "performance_tracking": True,
                    "content_recommendations": False
                },
                "data_summary": {
                    "behavior_events": 150,
                    "learning_patterns": 3,
                    "has_learning_profile": True,
                    "engagement_metrics": 12
                },
                "data_age": {
                    "oldest_record": datetime.now(timezone.utc),
                    "newest_record": datetime.now(timezone.utc)
                },
                "retention_policy": {
                    "behavior_data": 365,
                    "learning_patterns": 730,
                    "learning_profiles": 1095,
                    "engagement_metrics": 365,
                    "anonymized_data": -1
                },
                "anonymization_status": {
                    "anonymized_records": 10,
                    "total_records": 150
                },
                "generated_at": datetime.now(timezone.utc)
            }
            
            mock_service.generate_privacy_report.return_value = mock_report
            
            response = client.get(
                f"/privacy/report/{mock_user.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["data_summary"]["behavior_events"] == 150
            assert data["consent_status"]["analytics_collection"] is True
    
    def test_anonymize_user_data_success(self, client, mock_user, auth_headers):
        """Test successful data anonymization request."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            anonymization_request = {
                "user_id": mock_user.id,
                "data_types": ["behavior_data"],
                "batch_size": 500
            }
            
            response = client.post(
                "/privacy/anonymize",
                json=anonymization_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["status"] == "in_progress"
    
    def test_get_retention_policy(self, client, mock_user, auth_headers):
        """Test retrieval of retention policy."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            mock_policy = {
                "behavior_data": 365,
                "learning_patterns": 730,
                "learning_profiles": 1095,
                "engagement_metrics": 365,
                "anonymized_data": -1
            }
            
            mock_service.get_data_retention_policy.return_value = mock_policy
            
            response = client.get(
                "/privacy/retention-policy",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["behavior_data"] == 365
            assert data["anonymized_data"] == -1
    
    def test_cleanup_expired_data_admin_only(self, client, mock_user, auth_headers):
        """Test that only admins can trigger data cleanup."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            cleanup_request = {
                "dry_run": True,
                "force_cleanup": False
            }
            
            response = client.post(
                "/privacy/cleanup-expired-data",
                json=cleanup_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_cleanup_expired_data_admin_success(self, client, mock_admin_user, auth_headers):
        """Test successful data cleanup by admin."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_admin_user):
            
            cleanup_request = {
                "dry_run": True,
                "force_cleanup": False
            }
            
            response = client.post(
                "/privacy/cleanup-expired-data",
                json=cleanup_request,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["dry_run"] is True
            assert "cleanup_counts" in data
    
    def test_validate_consent_success(self, client, mock_user, auth_headers):
        """Test successful consent validation."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            mock_service.validate_data_collection_consent.return_value = True
            
            response = client.get(
                f"/privacy/validate-consent/{mock_user.id}/behavior_tracking",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["user_id"] == mock_user.id
            assert data["data_type"] == "behavior_tracking"
            assert data["has_consent"] is True
    
    def test_validate_consent_forbidden(self, client, mock_user, auth_headers):
        """Test forbidden consent validation for another user."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            other_user_id = "other_user_456"
            response = client.get(
                f"/privacy/validate-consent/{other_user_id}/behavior_tracking",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPrivacyAPIValidation:
    """Test input validation for privacy API endpoints."""
    
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
    
    def test_consent_update_validation(self, client, mock_user, auth_headers):
        """Test validation of consent update data."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            # Test invalid consent data
            invalid_updates = [
                {"invalid_field": True},  # Unknown field
                {"analytics_collection": "yes"},  # Wrong type
                {},  # Empty update
            ]
            
            for invalid_update in invalid_updates:
                response = client.put(
                    f"/privacy/consent/{mock_user.id}",
                    json=invalid_update,
                    headers=auth_headers
                )
                
                # Should either succeed (empty update) or fail validation
                assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_deletion_request_validation(self, client, mock_user, auth_headers):
        """Test validation of deletion request data."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            # Test invalid deletion requests
            invalid_requests = [
                {
                    "user_id": "",  # Empty user ID
                    "deletion_type": "anonymize",
                    "confirm_deletion": True
                },
                {
                    "user_id": mock_user.id,
                    "deletion_type": "invalid_type",  # Invalid deletion type
                    "confirm_deletion": True
                },
                {
                    "user_id": mock_user.id,
                    "deletion_type": "anonymize",
                    "confirm_deletion": False  # Must confirm
                }
            ]
            
            for invalid_request in invalid_requests:
                response = client.post(
                    "/privacy/delete-data",
                    json=invalid_request,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_anonymization_request_validation(self, client, mock_user, auth_headers):
        """Test validation of anonymization request data."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user):
            
            # Test invalid anonymization requests
            invalid_requests = [
                {
                    "user_id": "",  # Empty user ID
                    "batch_size": 1000
                },
                {
                    "user_id": mock_user.id,
                    "batch_size": 50  # Too small
                },
                {
                    "user_id": mock_user.id,
                    "batch_size": 20000  # Too large
                }
            ]
            
            for invalid_request in invalid_requests:
                response = client.post(
                    "/privacy/anonymize",
                    json=invalid_request,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPrivacyAPIErrorHandling:
    """Test error handling in privacy API endpoints."""
    
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
    
    def test_consent_service_error(self, client, mock_user, auth_headers):
        """Test handling of service errors in consent endpoints."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            # Mock service error
            mock_service.check_user_consent.side_effect = Exception("Database error")
            
            response = client.get(
                f"/privacy/consent/{mock_user.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_privacy_report_service_error(self, client, mock_user, auth_headers):
        """Test handling of service errors in privacy report."""
        with patch('backend.src.api.routers.privacy.get_current_user', return_value=mock_user), \
             patch('backend.src.api.routers.privacy.privacy_service') as mock_service:
            
            # Mock service error
            mock_service.generate_privacy_report.side_effect = Exception("Report generation failed")
            
            response = client.get(
                f"/privacy/report/{mock_user.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR