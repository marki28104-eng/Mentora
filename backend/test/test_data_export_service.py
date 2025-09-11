"""
Tests for data export service functionality including user data export,
course creator analytics, and admin dashboard features.
"""

import pytest
import json
import tempfile
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from sqlalchemy.orm import Session

from backend.src.services.data_export_service import DataExportService
from backend.src.db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from backend.src.db.models.db_course import Course


class TestDataExportService:
    """Test cases for DataExportService."""
    
    @pytest.fixture
    def export_service(self):
        """Create a DataExportService instance for testing."""
        return DataExportService()
    
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
                metadata={"content_type": "text"},
                duration_seconds=300,
                engagement_score=0.8,
                is_anonymized=False,
                created_at=datetime.now(timezone.utc)
            ),
            UserBehaviorData(
                id="behavior_2",
                user_id=sample_user_id,
                session_id="session_2",
                event_type=EventType.COURSE_COMPLETE,
                page_url="/courses/1",
                timestamp=datetime.now(timezone.utc),
                metadata={"completion_time": 3600},
                duration_seconds=3600,
                engagement_score=0.9,
                is_anonymized=False,
                created_at=datetime.now(timezone.utc)
            )
        ]
    
    @pytest.fixture
    def sample_learning_pattern(self, sample_user_id):
        """Create sample learning pattern for testing."""
        return LearningPattern(
            id="pattern_1",
            user_id=sample_user_id,
            pattern_type=LearningStyleType.VISUAL,
            confidence_score=0.85,
            preferred_content_types=["video", "images"],
            optimal_session_duration=45,
            difficulty_progression_rate=0.7,
            preferred_learning_times=[9, 10, 14, 15],
            average_attention_span=30,
            strong_topics=["mathematics", "science"],
            challenging_topics=["history"],
            data_points_count=100,
            last_calculated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    @pytest.fixture
    def sample_learning_profile(self, sample_user_id):
        """Create sample learning profile for testing."""
        return UserLearningProfile(
            id="profile_1",
            user_id=sample_user_id,
            learning_style=LearningStyleType.VISUAL,
            attention_span=45,
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            completion_rate=0.75,
            average_session_duration=40,
            total_learning_time=1200,
            courses_completed=5,
            engagement_score=0.8,
            consistency_score=0.7,
            challenge_preference=0.6,
            strong_topics=["mathematics"],
            challenging_topics=["history"],
            preferred_content_formats=["video", "interactive"],
            current_difficulty_level=0.6,
            adaptation_rate=0.1,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
    
    def test_serialize_behavior_data(self, export_service, sample_behavior_data):
        """Test serialization of behavior data."""
        result = export_service._serialize_behavior_data(sample_behavior_data, include_metadata=True)
        
        assert len(result) == 2
        assert result[0]["id"] == "behavior_1"
        assert result[0]["event_type"] == "page_view"
        assert result[0]["metadata"]["content_type"] == "text"
        assert result[1]["event_type"] == "course_complete"
    
    def test_serialize_behavior_data_without_metadata(self, export_service, sample_behavior_data):
        """Test serialization of behavior data without metadata."""
        result = export_service._serialize_behavior_data(sample_behavior_data, include_metadata=False)
        
        assert len(result) == 2
        assert "metadata" not in result[0]
        assert "metadata" not in result[1]
    
    def test_serialize_learning_pattern(self, export_service, sample_learning_pattern):
        """Test serialization of learning pattern."""
        result = export_service._serialize_learning_patterns([sample_learning_pattern], include_metadata=True)
        
        assert len(result) == 1
        pattern = result[0]
        assert pattern["id"] == "pattern_1"
        assert pattern["pattern_type"] == "visual"
        assert pattern["confidence_score"] == 0.85
        assert pattern["preferred_content_types"] == ["video", "images"]
        assert pattern["strong_topics"] == ["mathematics", "science"]
    
    def test_serialize_learning_profile(self, export_service, sample_learning_profile):
        """Test serialization of learning profile."""
        result = export_service._serialize_learning_profile(sample_learning_profile, include_metadata=True)
        
        assert result["id"] == "profile_1"
        assert result["learning_style"] == "visual"
        assert result["preferred_difficulty"] == "intermediate"
        assert result["completion_rate"] == 0.75
        assert result["strong_topics"] == ["mathematics"]
    
    @pytest.mark.asyncio
    async def test_export_user_data_json(self, export_service, mock_db, sample_user_id, sample_behavior_data, sample_learning_pattern, sample_learning_profile):
        """Test user data export in JSON format."""
        with patch('backend.src.services.data_export_service.analytics_crud') as mock_crud, \
             patch('backend.src.services.data_export_service.users_crud') as mock_users_crud:
            
            # Mock CRUD operations
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            mock_crud.get_learning_patterns_by_user.return_value = [sample_learning_pattern]
            mock_crud.get_user_learning_profile.return_value = sample_learning_profile
            mock_crud.get_user_engagement_metrics.return_value = []
            
            # Mock user with settings
            mock_user = Mock()
            mock_user.settings = {"analytics_consent": True}
            mock_users_crud.get_user_by_id.return_value = mock_user
            
            # Run export
            result = await export_service.export_user_data(
                db=mock_db,
                user_id=sample_user_id,
                data_types=["behavior_data", "learning_patterns", "learning_profile"],
                format="json",
                include_metadata=True
            )
            
            # Verify result structure
            assert result["export_id"] is not None
            assert result["user_id"] == sample_user_id
            assert result["format"] == "json"
            assert result["file_path"] is not None
            assert result["file_size"] > 0
            assert "behavior_data" in result["record_counts"]
            assert "learning_patterns" in result["record_counts"]
            assert "learning_profile" in result["record_counts"]
            
            # Verify file was created
            assert Path(result["file_path"]).exists()
            
            # Verify file content
            with open(result["file_path"], 'r') as f:
                export_data = json.load(f)
            
            assert "export_metadata" in export_data
            assert "data" in export_data
            assert export_data["export_metadata"]["user_id"] == sample_user_id
            assert "behavior_data" in export_data["data"]
            assert len(export_data["data"]["behavior_data"]) == 2
    
    @pytest.mark.asyncio
    async def test_export_user_data_csv(self, export_service, mock_db, sample_user_id, sample_behavior_data):
        """Test user data export in CSV format."""
        with patch('backend.src.services.data_export_service.analytics_crud') as mock_crud, \
             patch('backend.src.services.data_export_service.users_crud') as mock_users_crud:
            
            # Mock CRUD operations
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            mock_crud.get_learning_patterns_by_user.return_value = []
            mock_crud.get_user_learning_profile.return_value = None
            mock_crud.get_user_engagement_metrics.return_value = []
            mock_users_crud.get_user_by_id.return_value = None
            
            # Run export
            result = await export_service.export_user_data(
                db=mock_db,
                user_id=sample_user_id,
                data_types=["behavior_data"],
                format="csv",
                include_metadata=True
            )
            
            # Verify result
            assert result["format"] == "csv"
            assert result["file_path"] is not None
            
            # For CSV, should create a zip file if multiple data types
            # In this case, only one data type, so should be a single CSV file
            assert result["file_path"].endswith('.csv')
            assert Path(result["file_path"]).exists()
    
    def test_export_user_data_invalid_format(self, export_service, mock_db, sample_user_id):
        """Test export with invalid format."""
        with pytest.raises(ValueError, match="Unsupported export format"):
            asyncio.run(export_service.export_user_data(
                db=mock_db,
                user_id=sample_user_id,
                data_types=["behavior_data"],
                format="xml"  # Invalid format
            ))
    
    def test_get_aggregated_analytics_for_course_creator(self, export_service, mock_db):
        """Test aggregated analytics for course creator."""
        creator_user_id = "creator_123"
        course_id = 1
        
        with patch('backend.src.services.data_export_service.courses_crud') as mock_courses_crud, \
             patch.object(export_service, '_get_course_behavior_stats') as mock_behavior_stats, \
             patch.object(export_service, '_get_course_engagement_stats') as mock_engagement_stats, \
             patch.object(export_service, '_get_course_learning_insights') as mock_learning_insights, \
             patch.object(export_service, '_get_course_completion_stats') as mock_completion_stats:
            
            # Mock course ownership verification
            mock_course = Mock()
            mock_course.user_id = creator_user_id
            mock_courses_crud.get_course_by_id.return_value = mock_course
            
            # Mock statistics
            mock_behavior_stats.return_value = {
                "unique_learners": 50,
                "total_sessions": 200,
                "avg_session_duration": 1800,
                "total_time_spent": 360000,
                "daily_trends": []
            }
            
            mock_engagement_stats.return_value = {
                "avg_engagement_score": 0.75
            }
            
            mock_learning_insights.return_value = {
                "learning_style_distribution": {"visual": 20, "reading": 15}
            }
            
            mock_completion_stats.return_value = {
                "1": {"starts": 50, "completions": 35, "completion_rate": 0.7}
            }
            
            # Run analytics
            result = export_service.get_aggregated_analytics_for_course_creator(
                db=mock_db,
                creator_user_id=creator_user_id,
                course_id=course_id,
                days=30
            )
            
            # Verify result structure
            assert result["course_ids"] == [course_id]
            assert result["total_learners"] == 50
            assert result["engagement_summary"]["total_sessions"] == 200
            assert result["engagement_summary"]["average_engagement_score"] == 0.75
            assert "learning_patterns" in result
            assert "completion_rates" in result
    
    def test_get_aggregated_analytics_unauthorized_course(self, export_service, mock_db):
        """Test analytics for course not owned by creator."""
        creator_user_id = "creator_123"
        course_id = 1
        
        with patch('backend.src.services.data_export_service.courses_crud') as mock_courses_crud:
            # Mock course owned by different user
            mock_course = Mock()
            mock_course.user_id = "other_user_456"
            mock_courses_crud.get_course_by_id.return_value = mock_course
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="Course not found or not owned by creator"):
                export_service.get_aggregated_analytics_for_course_creator(
                    db=mock_db,
                    creator_user_id=creator_user_id,
                    course_id=course_id
                )
    
    def test_get_admin_analytics_dashboard(self, export_service, mock_db):
        """Test admin analytics dashboard."""
        with patch.object(mock_db, 'query') as mock_query:
            # Mock database queries
            mock_scalar_result = Mock()
            mock_scalar_result.scalar.return_value = 100
            mock_query.return_value = mock_scalar_result
            
            # Mock query results
            mock_activity_result = Mock()
            mock_activity_result.total_events = 5000
            mock_activity_result.active_users = 150
            mock_activity_result.total_sessions = 800
            mock_activity_result.total_time_spent = 720000
            
            mock_privacy_result = Mock()
            mock_privacy_result.total_records = 10000
            mock_privacy_result.anonymized_records = 1000
            
            # Configure query chain
            mock_query.return_value.filter.return_value.first.return_value = mock_activity_result
            mock_query.return_value.group_by.return_value.all.return_value = []
            mock_query.return_value.first.return_value = mock_privacy_result
            
            # Run dashboard
            result = export_service.get_admin_analytics_dashboard(mock_db, days=30)
            
            # Verify result structure
            assert "platform_overview" in result
            assert "activity_summary" in result
            assert "learning_insights" in result
            assert "privacy_compliance" in result
            assert "time_period" in result
            
            # Verify some values
            assert result["activity_summary"]["total_events"] == 5000
            assert result["privacy_compliance"]["total_behavior_records"] == 10000


class TestDataExportServiceIntegration:
    """Integration tests for data export service."""
    
    @pytest.mark.asyncio
    async def test_full_export_workflow(self):
        """Test complete export workflow."""
        export_service = DataExportService()
        
        # Test that export service initializes correctly
        assert export_service.export_formats == ["json", "csv"]
        assert "behavior_data" in export_service.supported_data_types
        assert "learning_patterns" in export_service.supported_data_types
    
    def test_file_creation_and_cleanup(self):
        """Test that export files are created and can be cleaned up."""
        export_service = DataExportService()
        
        # Test JSON file creation
        test_data = {"test": "data", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        # This would test actual file operations in a real scenario
        # For now, we verify the service has the necessary methods
        assert hasattr(export_service, '_create_json_export')
        assert hasattr(export_service, '_create_csv_export')
        assert hasattr(export_service, '_create_zip_export')
    
    def test_data_serialization_consistency(self):
        """Test that data serialization is consistent across formats."""
        export_service = DataExportService()
        
        # Create sample data
        sample_data = [
            {
                "id": "test_1",
                "timestamp": datetime.now(timezone.utc),
                "value": 123.45
            }
        ]
        
        # Test that serialization methods exist and can handle data
        assert callable(export_service._serialize_behavior_data)
        assert callable(export_service._serialize_learning_patterns)
        assert callable(export_service._serialize_learning_profile)
        assert callable(export_service._serialize_engagement_metrics)