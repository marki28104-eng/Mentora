"""
Tests for privacy service functionality including GDPR compliance,
data anonymization, and user consent management.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from backend.src.services.privacy_service import PrivacyService
from backend.src.db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from backend.src.db.models.db_user import User


class TestPrivacyService:
    """Test cases for PrivacyService."""
    
    @pytest.fixture
    def privacy_service(self):
        """Create a PrivacyService instance for testing."""
        return PrivacyService()
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return "test_user_123"
    
    @pytest.fixture
    def sample_behavior_data(self, sample_user_id):
        """Create sample behavior data for testing."""
        return [
            UserBehaviorData(
                id="behavior_1",
                user_id=sample_user_id,
                session_id="session_1",
                event_type=EventType.PAGE_VIEW,
                page_url="/courses/1/chapters/1",
                timestamp=datetime.now(timezone.utc),
                metadata={"content_type": "text", "user_agent": "Mozilla/5.0"},
                is_anonymized=False
            ),
            UserBehaviorData(
                id="behavior_2",
                user_id=sample_user_id,
                session_id="session_2",
                event_type=EventType.COURSE_COMPLETE,
                page_url="/courses/1",
                timestamp=datetime.now(timezone.utc),
                metadata={"completion_time": 3600, "email": "test@example.com"},
                is_anonymized=False
            )
        ]
    
    def test_anonymize_user_id(self, privacy_service, sample_user_id):
        """Test user ID anonymization."""
        anonymized_id = privacy_service.anonymize_user_id(sample_user_id)
        
        # Should return a string
        assert isinstance(anonymized_id, str)
        
        # Should be different from original
        assert anonymized_id != sample_user_id
        
        # Should be consistent (same input = same output)
        assert privacy_service.anonymize_user_id(sample_user_id) == anonymized_id
        
        # Should be 16 characters long
        assert len(anonymized_id) == 16
    
    def test_anonymize_session_id(self, privacy_service):
        """Test session ID anonymization."""
        session_id = "session_123"
        anonymized_session = privacy_service.anonymize_session_id(session_id)
        
        # Should return a string
        assert isinstance(anonymized_session, str)
        
        # Should be different from original
        assert anonymized_session != session_id
        
        # Should be consistent
        assert privacy_service.anonymize_session_id(session_id) == anonymized_session
        
        # Should be 12 characters long
        assert len(anonymized_session) == 12
    
    def test_sanitize_metadata_removes_pii(self, privacy_service):
        """Test that metadata sanitization removes PII."""
        metadata = {
            "content_type": "text",
            "duration": 300,
            "email": "user@example.com",  # Should be removed
            "phone": "123-456-7890",      # Should be removed
            "user_agent": "Mozilla/5.0",  # Should be removed (contains identifying info)
            "topic": "mathematics",
            "difficulty": "intermediate"
        }
        
        sanitized = privacy_service.sanitize_metadata(metadata)
        
        # Should keep safe fields
        assert "content_type" in sanitized
        assert "duration" in sanitized
        assert "topic" in sanitized
        assert "difficulty" in sanitized
        
        # Should remove PII fields
        assert "email" not in sanitized
        assert "phone" not in sanitized
        assert "user_agent" not in sanitized
    
    def test_sanitize_metadata_limits_string_length(self, privacy_service):
        """Test that metadata sanitization limits string lengths."""
        long_string = "x" * 1000
        metadata = {
            "description": long_string,
            "short_field": "normal"
        }
        
        sanitized = privacy_service.sanitize_metadata(metadata)
        
        # Should limit long strings to 500 characters
        assert len(sanitized["description"]) == 500
        assert sanitized["short_field"] == "normal"
    
    def test_sanitize_metadata_handles_none(self, privacy_service):
        """Test that metadata sanitization handles None input."""
        result = privacy_service.sanitize_metadata(None)
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_anonymize_user_behavior_data(self, privacy_service, mock_db, sample_user_id, sample_behavior_data):
        """Test anonymization of user behavior data."""
        # Mock the CRUD operations
        with patch('backend.src.services.privacy_service.analytics_crud') as mock_crud:
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            mock_crud.update_user_behavior_data.return_value = None
            
            # Run anonymization
            result = await privacy_service.anonymize_user_behavior_data(mock_db, sample_user_id)
            
            # Should return count of anonymized records
            assert result == 2
            
            # Should have called update for each non-anonymized record
            assert mock_crud.update_user_behavior_data.call_count == 2
    
    @pytest.mark.asyncio
    async def test_delete_user_analytics_data_hard_delete(self, privacy_service, mock_db, sample_user_id):
        """Test hard deletion of user analytics data."""
        with patch('backend.src.services.privacy_service.analytics_crud') as mock_crud:
            # Mock deletion counts
            mock_crud.delete_user_behavior_data.return_value = 10
            mock_crud.delete_user_learning_patterns.return_value = 2
            mock_crud.delete_user_learning_profile.return_value = 1
            mock_crud.delete_user_engagement_metrics.return_value = 5
            
            # Run hard deletion
            result = await privacy_service.delete_user_analytics_data(mock_db, sample_user_id, hard_delete=True)
            
            # Should return deletion counts
            expected = {
                "behavior_data": 10,
                "learning_patterns": 2,
                "learning_profiles": 1,
                "engagement_metrics": 5
            }
            assert result == expected
            
            # Should have called hard delete methods
            mock_crud.delete_user_behavior_data.assert_called_once_with(mock_db, sample_user_id)
            mock_crud.delete_user_learning_patterns.assert_called_once_with(mock_db, sample_user_id)
    
    @pytest.mark.asyncio
    async def test_delete_user_analytics_data_anonymize(self, privacy_service, mock_db, sample_user_id):
        """Test anonymization instead of hard deletion."""
        with patch('backend.src.services.privacy_service.analytics_crud') as mock_crud:
            # Mock anonymization
            mock_crud.get_user_behavior_data.return_value = []
            mock_crud.get_learning_patterns_by_user.return_value = []
            mock_crud.get_user_learning_profile.return_value = None
            mock_crud.get_user_engagement_metrics.return_value = []
            
            # Run soft deletion (anonymization)
            result = await privacy_service.delete_user_analytics_data(mock_db, sample_user_id, hard_delete=False)
            
            # Should return anonymization counts
            assert "behavior_data" in result
            assert "learning_patterns" in result
            assert "learning_profiles" in result
            assert "engagement_metrics" in result
    
    def test_check_user_consent_existing_user(self, privacy_service, mock_db, sample_user_id):
        """Test checking consent for existing user."""
        # Mock user with consent settings
        mock_user = Mock()
        mock_user.settings = {
            "analytics_consent": True,
            "personalization_consent": False,
            "performance_consent": True,
            "recommendations_consent": True
        }
        
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud:
            mock_users_crud.get_user.return_value = mock_user
            
            result = privacy_service.check_user_consent(mock_db, sample_user_id)
            
            expected = {
                "analytics_collection": True,
                "personalization": False,
                "performance_tracking": True,
                "content_recommendations": True
            }
            assert result == expected
    
    def test_check_user_consent_nonexistent_user(self, privacy_service, mock_db, sample_user_id):
        """Test checking consent for non-existent user."""
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud:
            mock_users_crud.get_user.return_value = None
            
            result = privacy_service.check_user_consent(mock_db, sample_user_id)
            
            # Should return all False for non-existent user
            expected = {
                "analytics_collection": False,
                "personalization": False,
                "performance_tracking": False,
                "content_recommendations": False
            }
            assert result == expected
    
    def test_update_user_consent_success(self, privacy_service, mock_db, sample_user_id):
        """Test successful consent update."""
        mock_user = Mock()
        mock_user.settings = {}
        
        consent_data = {
            "analytics_collection": True,
            "personalization": True
        }
        
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud:
            mock_users_crud.get_user.return_value = mock_user
            mock_users_crud.update_user.return_value = mock_user
            
            result = privacy_service.update_user_consent(mock_db, sample_user_id, consent_data)
            
            assert result is True
            mock_users_crud.update_user.assert_called_once()
    
    def test_update_user_consent_nonexistent_user(self, privacy_service, mock_db, sample_user_id):
        """Test consent update for non-existent user."""
        consent_data = {"analytics_collection": True}
        
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud:
            mock_users_crud.get_user.return_value = None
            
            result = privacy_service.update_user_consent(mock_db, sample_user_id, consent_data)
            
            assert result is False
    
    def test_get_data_retention_policy(self, privacy_service):
        """Test getting data retention policy."""
        policy = privacy_service.get_data_retention_policy()
        
        # Should return expected policy structure
        expected_keys = {
            "behavior_data", "learning_patterns", 
            "learning_profiles", "engagement_metrics", "anonymized_data"
        }
        assert set(policy.keys()) == expected_keys
        
        # Should have reasonable retention periods
        assert policy["behavior_data"] > 0
        assert policy["learning_patterns"] > 0
        assert policy["anonymized_data"] == -1  # Indefinite
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_data(self, privacy_service, mock_db):
        """Test cleanup of expired data."""
        with patch('backend.src.services.privacy_service.analytics_crud') as mock_crud:
            mock_crud.delete_behavior_data_before_date.return_value = 50
            mock_crud.delete_engagement_metrics_before_date.return_value = 25
            
            result = await privacy_service.cleanup_expired_data(mock_db)
            
            # Should return cleanup counts
            assert "behavior_data" in result
            assert "engagement_metrics" in result
            assert result["behavior_data"] == 50
            assert result["engagement_metrics"] == 25
    
    def test_validate_data_collection_consent(self, privacy_service, mock_db, sample_user_id):
        """Test validation of data collection consent."""
        mock_user = Mock()
        mock_user.settings = {
            "analytics_consent": True,
            "personalization_consent": False
        }
        
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud:
            mock_users_crud.get_user.return_value = mock_user
            
            # Test valid consent
            assert privacy_service.validate_data_collection_consent(
                mock_db, sample_user_id, "behavior_tracking"
            ) is True
            
            # Test invalid consent
            assert privacy_service.validate_data_collection_consent(
                mock_db, sample_user_id, "learning_analytics"
            ) is False
    
    def test_generate_privacy_report(self, privacy_service, mock_db, sample_user_id):
        """Test generation of privacy report."""
        # Mock consent status
        mock_user = Mock()
        mock_user.settings = {"analytics_consent": True}
        
        # Mock data counts
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud, \
             patch('backend.src.services.privacy_service.analytics_crud') as mock_crud:
            
            mock_users_crud.get_user.return_value = mock_user
            mock_crud.count_user_behavior_data.return_value = 100
            mock_crud.get_learning_patterns_by_user.return_value = [Mock(), Mock()]
            mock_crud.get_user_learning_profile.return_value = Mock()
            mock_crud.get_user_engagement_metrics.return_value = [Mock()]
            mock_crud.get_oldest_user_behavior_data.return_value = Mock(
                created_at=datetime.now(timezone.utc) - timedelta(days=30)
            )
            mock_crud.get_newest_user_behavior_data.return_value = Mock(
                created_at=datetime.now(timezone.utc)
            )
            mock_crud.count_anonymized_behavior_data.return_value = 10
            
            result = privacy_service.generate_privacy_report(mock_db, sample_user_id)
            
            # Should return comprehensive report
            assert result["user_id"] == sample_user_id
            assert "consent_status" in result
            assert "data_summary" in result
            assert "data_age" in result
            assert "retention_policy" in result
            assert "anonymization_status" in result
            assert "generated_at" in result
            
            # Check data summary
            assert result["data_summary"]["behavior_events"] == 100
            assert result["data_summary"]["learning_patterns"] == 2
            assert result["data_summary"]["has_learning_profile"] is True
            assert result["data_summary"]["engagement_metrics"] == 1
    
    def test_generate_privacy_report_error_handling(self, privacy_service, mock_db, sample_user_id):
        """Test privacy report generation with errors."""
        with patch('backend.src.services.privacy_service.users_crud') as mock_users_crud:
            # Simulate an error
            mock_users_crud.get_user.side_effect = Exception("Database error")
            
            result = privacy_service.generate_privacy_report(mock_db, sample_user_id)
            
            # Should return error report
            assert result["user_id"] == sample_user_id
            assert "error" in result
            assert result["error"] == "Unable to generate privacy report"


class TestPrivacyServiceIntegration:
    """Integration tests for privacy service with real database operations."""
    
    @pytest.mark.asyncio
    async def test_full_anonymization_workflow(self):
        """Test complete anonymization workflow."""
        # This would require a test database setup
        # For now, we'll test the logic flow
        privacy_service = PrivacyService()
        
        # Test that anonymization methods work together
        user_id = "test_user"
        session_id = "test_session"
        
        anon_user = privacy_service.anonymize_user_id(user_id)
        anon_session = privacy_service.anonymize_session_id(session_id)
        
        # Should produce consistent results
        assert anon_user == privacy_service.anonymize_user_id(user_id)
        assert anon_session == privacy_service.anonymize_session_id(session_id)
        
        # Should be different from originals
        assert anon_user != user_id
        assert anon_session != session_id
    
    def test_metadata_sanitization_comprehensive(self):
        """Test comprehensive metadata sanitization."""
        privacy_service = PrivacyService()
        
        # Test various PII scenarios
        test_cases = [
            # Email addresses
            {"user_email": "test@example.com", "safe_field": "value"},
            # Phone numbers
            {"phone_number": "123-456-7890", "safe_field": "value"},
            # Names
            {"first_name": "John", "last_name": "Doe", "safe_field": "value"},
            # Mixed safe and unsafe
            {"content_type": "video", "email": "user@test.com", "duration": 300},
            # Long strings
            {"description": "x" * 2000, "short": "ok"},
            # Nested structures (should be preserved if small)
            {"metadata": {"type": "quiz", "score": 85}, "safe": True}
        ]
        
        for metadata in test_cases:
            sanitized = privacy_service.sanitize_metadata(metadata)
            
            # Should not contain PII keys
            pii_keys = {'email', 'phone', 'name', 'firstname', 'lastname'}
            for key in sanitized.keys():
                assert not any(pii_key in key.lower() for pii_key in pii_keys)
            
            # Should preserve safe fields
            if "safe_field" in metadata:
                assert sanitized.get("safe_field") == "value"
            if "content_type" in metadata:
                assert sanitized.get("content_type") == metadata["content_type"]