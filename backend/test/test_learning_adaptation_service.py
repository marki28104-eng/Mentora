"""
Unit tests for LearningAdaptationService.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.learning_adaptation_service import (
    LearningAdaptationService, PacingAdjustment, SupplementaryMaterial, AssessmentModification
)
from db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from db.models.db_course import Course, Chapter


class TestLearningAdaptationService:
    """Test cases for LearningAdaptationService."""
    
    @pytest.fixture
    def service(self):
        """Create LearningAdaptationService instance."""
        return LearningAdaptationService()
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user_profile(self):
        """Create sample user learning profile."""
        return UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.VISUAL,
            attention_span=45,
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            completion_rate=0.75,
            average_session_duration=60,
            total_learning_time=1200,
            courses_completed=3,
            engagement_score=0.8,
            consistency_score=0.7,
            challenge_preference=0.6,
            strong_topics=["mathematics", "programming"],
            challenging_topics=["statistics"],
            current_difficulty_level=0.6,
            adaptation_rate=0.1,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
    
    @pytest.fixture
    def sample_behavior_data(self):
        """Create sample behavior data for pacing analysis."""
        now = datetime.now(timezone.utc)
        return [
            UserBehaviorData(
                id="behavior_1",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.CHAPTER_START,
                page_url="/courses/1/chapters/1",
                course_id=1,
                chapter_id=1,
                timestamp=now - timedelta(hours=4),
                duration_seconds=1800,
                engagement_score=0.8
            ),
            UserBehaviorData(
                id="behavior_2",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.CHAPTER_COMPLETE,
                page_url="/courses/1/chapters/1",
                course_id=1,
                chapter_id=1,
                timestamp=now - timedelta(hours=3),
                duration_seconds=1800,
                engagement_score=0.9
            ),
            UserBehaviorData(
                id="behavior_3",
                user_id="user_123",
                session_id="session_2",
                event_type=EventType.CHAPTER_START,
                page_url="/courses/1/chapters/2",
                course_id=1,
                chapter_id=2,
                timestamp=now - timedelta(hours=2),
                duration_seconds=2400,
                engagement_score=0.7
            ),
            UserBehaviorData(
                id="behavior_4",
                user_id="user_123",
                session_id="session_2",
                event_type=EventType.CHAPTER_COMPLETE,
                page_url="/courses/1/chapters/2",
                course_id=1,
                chapter_id=2,
                timestamp=now - timedelta(hours=1),
                duration_seconds=2400,
                engagement_score=0.85
            )
        ]
    
    @pytest.fixture
    def sample_assessment_behavior_data(self):
        """Create sample behavior data for assessment analysis."""
        now = datetime.now(timezone.utc)
        return [
            UserBehaviorData(
                id="assessment_1",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.ASSESSMENT_START,
                page_url="/assessments/1",
                assessment_id="assessment_1",
                timestamp=now - timedelta(hours=2),
                duration_seconds=1200,
                engagement_score=0.8
            ),
            UserBehaviorData(
                id="assessment_2",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.ASSESSMENT_COMPLETE,
                page_url="/assessments/1",
                assessment_id="assessment_1",
                timestamp=now - timedelta(hours=1),
                duration_seconds=1200,
                engagement_score=0.9
            ),
            UserBehaviorData(
                id="assessment_3",
                user_id="user_123",
                session_id="session_2",
                event_type=EventType.ASSESSMENT_START,
                page_url="/assessments/2",
                assessment_id="assessment_2",
                timestamp=now - timedelta(minutes=30),
                duration_seconds=1800,
                engagement_score=0.6
            )
        ]
    
    @pytest.fixture
    def sample_learning_pattern(self):
        """Create sample learning pattern."""
        return LearningPattern(
            id="pattern_1",
            user_id="user_123",
            pattern_type=LearningStyleType.VISUAL,
            confidence_score=0.8,
            preferred_content_types=["video", "diagram"],
            optimal_session_duration=60,
            difficulty_progression_rate=0.7,
            preferred_learning_times=[9, 10, 14, 15],
            average_attention_span=45,
            strong_topics=["mathematics", "programming"],
            challenging_topics=["statistics"],
            data_points_count=50,
            last_calculated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    @pytest.fixture
    def sample_course(self):
        """Create sample course."""
        return Course(
            id=1,
            title="Python Programming",
            description="Learn Python programming fundamentals",
            difficulty="intermediate"
        )
    
    @pytest.fixture
    def sample_chapters(self):
        """Create sample chapters."""
        return [
            Chapter(id=1, course_id=1, title="Introduction", order_index=1),
            Chapter(id=2, course_id=1, title="Variables", order_index=2),
            Chapter(id=3, course_id=1, title="Functions", order_index=3)
        ]
    
    @pytest.mark.asyncio
    async def test_adjust_pacing_successful(
        self, service, mock_db, sample_user_profile, sample_behavior_data, sample_course, sample_chapters
    ):
        """Test successful pacing adjustment."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            # Mock database calls
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            
            # Mock course and chapter queries
            mock_db.query.return_value.filter.return_value.first.return_value = sample_course
            mock_db.query.return_value.filter.return_value.count.return_value = len(sample_chapters)
            
            # Test pacing adjustment
            result = await service.adjust_pacing(mock_db, "user_123", 1)
            
            # Verify result
            assert isinstance(result, PacingAdjustment)
            assert result.user_id == "user_123"
            assert result.course_id == 1
            assert result.current_pace > 0
            assert result.recommended_pace > 0
            assert result.confidence >= service.adaptation_confidence_threshold
            assert isinstance(result.reason, str)
            assert len(result.reason) > 0
    
    @pytest.mark.asyncio
    async def test_adjust_pacing_no_profile(self, service, mock_db):
        """Test pacing adjustment without user profile."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = None
            
            result = await service.adjust_pacing(mock_db, "user_123", 1)
            
            # Should return None without profile
            assert result is None
    
    @pytest.mark.asyncio
    async def test_adjust_pacing_insufficient_data(self, service, mock_db, sample_user_profile):
        """Test pacing adjustment with insufficient behavior data."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_user_behavior_data.return_value = []  # No behavior data
            
            result = await service.adjust_pacing(mock_db, "user_123", 1)
            
            # Should return None with insufficient data
            assert result is None
    
    @pytest.mark.asyncio
    async def test_adjust_pacing_low_confidence(self, service, mock_db, sample_user_profile):
        """Test pacing adjustment with low confidence."""
        # Create minimal behavior data that would result in low confidence
        minimal_data = [
            UserBehaviorData(
                id="behavior_1",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.PAGE_VIEW,
                page_url="/courses/1",
                course_id=1,
                timestamp=datetime.now(timezone.utc),
                duration_seconds=300,
                engagement_score=0.5
            )
        ] * 3  # Minimal data points
        
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_user_behavior_data.return_value = minimal_data
            
            # Mock course query
            mock_db.query.return_value.filter.return_value.first.return_value = sample_course
            mock_db.query.return_value.filter.return_value.count.return_value = 3
            
            result = await service.adjust_pacing(mock_db, "user_123", 1)
            
            # May return None due to low confidence
            if result is not None:
                assert result.confidence >= service.adaptation_confidence_threshold
    
    @pytest.mark.asyncio
    async def test_provide_supplementary_content_successful(
        self, service, mock_db, sample_user_profile, sample_learning_pattern
    ):
        """Test successful supplementary content provision."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_learning_pattern_by_user.return_value = sample_learning_pattern
            mock_crud.get_user_behavior_data.return_value = []  # Will create gaps based on profile
            
            result = await service.provide_supplementary_content(
                mock_db, "user_123", "statistics", max_recommendations=3
            )
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) <= 3
            
            for material in result:
                assert isinstance(material, SupplementaryMaterial)
                assert material.material_id is not None
                assert material.title is not None
                assert material.content_type is not None
                assert isinstance(material.difficulty_level, DifficultyLevel)
                assert material.estimated_time > 0
                assert 0.0 <= material.relevance_score <= 1.0
                assert material.reason is not None
                assert material.priority > 0
    
    @pytest.mark.asyncio
    async def test_provide_supplementary_content_no_profile(self, service, mock_db):
        """Test supplementary content provision without user profile."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = None
            
            result = await service.provide_supplementary_content(mock_db, "user_123", "statistics")
            
            # Should return empty list without profile
            assert result == []
    
    @pytest.mark.asyncio
    async def test_provide_supplementary_content_no_gaps(
        self, service, mock_db, sample_user_profile, sample_learning_pattern
    ):
        """Test supplementary content provision when no learning gaps identified."""
        # Create profile without challenging topics
        profile_no_gaps = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.VISUAL,
            attention_span=45,
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            completion_rate=0.9,  # High completion rate
            engagement_score=0.9,  # High engagement
            consistency_score=0.8,
            challenge_preference=0.6,
            strong_topics=["mathematics", "programming"],
            challenging_topics=[],  # No challenging topics
            current_difficulty_level=0.7,
            adaptation_rate=0.1,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = profile_no_gaps
            mock_crud.get_learning_pattern_by_user.return_value = sample_learning_pattern
            mock_crud.get_user_behavior_data.return_value = []
            
            result = await service.provide_supplementary_content(mock_db, "user_123", "mathematics")
            
            # Should return empty list when no gaps identified
            assert result == []
    
    @pytest.mark.asyncio
    async def test_modify_assessment_difficulty_successful(
        self, service, mock_db, sample_user_profile, sample_assessment_behavior_data
    ):
        """Test successful assessment difficulty modification."""
        assessment_metadata = {"difficulty": 0.7, "time_limit": 3600}
        
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_user_behavior_data.return_value = sample_assessment_behavior_data
            
            result = await service.modify_assessment_difficulty(
                mock_db, "user_123", "assessment_123", assessment_metadata
            )
            
            # Verify result (may be None if no significant modification needed)
            if result is not None:
                assert isinstance(result, AssessmentModification)
                assert result.assessment_id == "assessment_123"
                assert result.original_difficulty == 0.7
                assert 0.0 <= result.modified_difficulty <= 1.0
                assert isinstance(result.question_adjustments, dict)
                assert isinstance(result.time_adjustments, dict)
                assert result.support_level in ["low", "medium", "high"]
                assert result.modification_reason is not None
    
    @pytest.mark.asyncio
    async def test_modify_assessment_difficulty_no_profile(self, service, mock_db):
        """Test assessment modification without user profile."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = None
            
            result = await service.modify_assessment_difficulty(
                mock_db, "user_123", "assessment_123"
            )
            
            # Should return None without profile
            assert result is None
    
    @pytest.mark.asyncio
    async def test_modify_assessment_difficulty_no_significant_change(
        self, service, mock_db, sample_assessment_behavior_data
    ):
        """Test assessment modification when no significant change is needed."""
        # Create profile that would result in minimal difficulty change
        stable_profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.READING,
            attention_span=60,
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            completion_rate=0.7,  # Moderate performance
            engagement_score=0.7,
            consistency_score=0.7,
            challenge_preference=0.5,  # Neutral challenge preference
            current_difficulty_level=0.5,
            adaptation_rate=0.1,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = stable_profile
            mock_crud.get_user_behavior_data.return_value = sample_assessment_behavior_data
            
            result = await service.modify_assessment_difficulty(
                mock_db, "user_123", "assessment_123", {"difficulty": 0.5}
            )
            
            # Should return None when no significant modification needed
            assert result is None
    
    def test_analyze_performance_patterns(self, service, sample_behavior_data):
        """Test performance pattern analysis."""
        metrics = service._analyze_performance_patterns(sample_behavior_data)
        
        # Verify metrics structure
        assert isinstance(metrics, dict)
        assert "completion_rate" in metrics
        assert "average_time_per_activity" in metrics
        assert "engagement_trend" in metrics
        assert "struggle_indicators" in metrics
        assert "consistency_score" in metrics
        
        # Verify metric values
        assert 0.0 <= metrics["completion_rate"] <= 1.0
        assert metrics["average_time_per_activity"] >= 0
        assert 0.0 <= metrics["struggle_indicators"] <= 1.0
        assert 0.0 <= metrics["consistency_score"] <= 1.0
    
    def test_analyze_performance_patterns_empty_data(self, service):
        """Test performance pattern analysis with empty data."""
        metrics = service._analyze_performance_patterns([])
        
        # Should return default metrics
        assert metrics["completion_rate"] == 0.0
        assert metrics["average_time_per_activity"] == 0.0
        assert metrics["engagement_trend"] == 0.0
        assert metrics["struggle_indicators"] == 0.0
        assert metrics["consistency_score"] == 0.0
    
    def test_calculate_current_pace(self, service, sample_behavior_data, mock_db, sample_course):
        """Test current pace calculation."""
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = sample_course
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        
        pace = service._calculate_current_pace(sample_behavior_data, 1, mock_db)
        
        # Should return a positive pace value
        assert pace > 0.0
        assert isinstance(pace, float)
    
    def test_calculate_current_pace_no_course(self, service, sample_behavior_data, mock_db):
        """Test current pace calculation when course not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        pace = service._calculate_current_pace(sample_behavior_data, 999, mock_db)
        
        # Should return default pace
        assert pace == 1.0
    
    def test_calculate_pace_adjustment(self, service, sample_user_profile):
        """Test pace adjustment calculation."""
        performance_metrics = {
            "completion_rate": 0.8,
            "engagement_trend": 0.1,
            "struggle_indicators": 0.2,
            "consistency_score": 0.7
        }
        
        recommended_pace, adjustment_factor, reason, confidence = service._calculate_pace_adjustment(
            performance_metrics, sample_user_profile, 1.0
        )
        
        # Verify results
        assert recommended_pace > 0
        assert adjustment_factor > 0
        assert isinstance(reason, str)
        assert len(reason) > 0
        assert 0.0 <= confidence <= 1.0
    
    def test_identify_learning_gaps_challenging_topics(
        self, service, mock_db, sample_user_profile, sample_learning_pattern
    ):
        """Test learning gap identification for challenging topics."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_user_behavior_data.return_value = []
            
            gaps = service._identify_learning_gaps(mock_db, "user_123", "statistics")
            
            # Should identify statistics as challenging topic
            assert len(gaps) > 0
            challenging_gap = next((g for g in gaps if g["gap_type"] == "challenging_topic"), None)
            assert challenging_gap is not None
            assert "statistics" in challenging_gap["topic"].lower()
    
    def test_generate_supplementary_materials_challenging_topic(
        self, service, sample_user_profile, sample_learning_pattern
    ):
        """Test supplementary material generation for challenging topics."""
        gap = {
            "topic": "statistics",
            "gap_type": "challenging_topic",
            "severity": "high",
            "evidence": "identified from learning patterns"
        }
        
        materials = service._generate_supplementary_materials(
            gap, sample_user_profile, sample_learning_pattern
        )
        
        # Should generate appropriate materials
        assert len(materials) > 0
        
        for material in materials:
            assert isinstance(material, SupplementaryMaterial)
            assert "statistics" in material.title.lower()
            assert material.difficulty_level == DifficultyLevel.BEGINNER  # For challenging topics
            assert material.priority == 1  # High priority for high severity
    
    def test_generate_supplementary_materials_visual_learner(
        self, service, sample_user_profile, sample_learning_pattern
    ):
        """Test supplementary material adaptation for visual learners."""
        gap = {
            "topic": "mathematics",
            "gap_type": "challenging_topic",
            "severity": "medium",
            "evidence": "test"
        }
        
        materials = service._generate_supplementary_materials(
            gap, sample_user_profile, sample_learning_pattern
        )
        
        # Check for visual adaptations
        tutorial_materials = [m for m in materials if "tutorial" in m.content_type.lower()]
        if tutorial_materials:
            # Should be adapted to video for visual learners
            assert any("video" in m.content_type.lower() for m in tutorial_materials)
    
    def test_get_recent_assessment_performance(self, service, mock_db, sample_assessment_behavior_data):
        """Test recent assessment performance calculation."""
        with patch('services.learning_adaptation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_behavior_data.return_value = sample_assessment_behavior_data
            
            performance = service._get_recent_assessment_performance(mock_db, "user_123")
            
            # Verify performance metrics
            assert isinstance(performance, dict)
            assert "average_score" in performance
            assert "completion_rate" in performance
            assert "average_time_ratio" in performance
            assert "trend" in performance
            
            # Check value ranges
            assert 0.0 <= performance["average_score"] <= 1.0
            assert 0.0 <= performance["completion_rate"] <= 1.0
            assert performance["average_time_ratio"] > 0
    
    def test_calculate_assessment_difficulty_high_performer(self, service, sample_user_profile):
        """Test assessment difficulty calculation for high performer."""
        high_performance = {
            "average_score": 0.9,
            "completion_rate": 0.9,
            "average_time_ratio": 0.8,
            "trend": 0.1
        }
        
        modified_difficulty, reason = service._calculate_assessment_difficulty(
            0.5, sample_user_profile, high_performance
        )
        
        # Should increase difficulty for high performers
        assert modified_difficulty > 0.5
        assert "strong recent performance" in reason.lower()
    
    def test_calculate_assessment_difficulty_struggling_learner(self, service, sample_user_profile):
        """Test assessment difficulty calculation for struggling learner."""
        poor_performance = {
            "average_score": 0.3,
            "completion_rate": 0.4,
            "average_time_ratio": 1.5,
            "trend": -0.1
        }
        
        modified_difficulty, reason = service._calculate_assessment_difficulty(
            0.5, sample_user_profile, poor_performance
        )
        
        # Should decrease difficulty for struggling learners
        assert modified_difficulty < 0.5
        assert "struggling" in reason.lower()
    
    def test_generate_question_adjustments_increase_difficulty(self, service, sample_user_profile):
        """Test question adjustments for increased difficulty."""
        adjustments = service._generate_question_adjustments(
            sample_user_profile, 0.5, 0.7  # Increasing difficulty
        )
        
        # Should include harder question features
        assert adjustments.get("add_complex_scenarios") is True
        assert adjustments.get("reduce_hints") is True
        assert adjustments.get("add_multi_step_problems") is True
    
    def test_generate_question_adjustments_decrease_difficulty(self, service, sample_user_profile):
        """Test question adjustments for decreased difficulty."""
        adjustments = service._generate_question_adjustments(
            sample_user_profile, 0.5, 0.3  # Decreasing difficulty
        )
        
        # Should include easier question features
        assert adjustments.get("add_hints") is True
        assert adjustments.get("break_down_complex_questions") is True
        assert adjustments.get("add_multiple_choice") is True
    
    def test_generate_question_adjustments_visual_learner(self, service, sample_user_profile):
        """Test question adjustments for visual learner."""
        adjustments = service._generate_question_adjustments(
            sample_user_profile, 0.5, 0.5  # No difficulty change
        )
        
        # Should include visual elements
        assert adjustments.get("add_diagrams") is True
        assert adjustments.get("use_visual_questions") is True
        assert adjustments.get("include_charts") is True
    
    def test_generate_time_adjustments_short_attention_span(self, service):
        """Test time adjustments for short attention span."""
        profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.READING,
            attention_span=20,  # Short attention span
            preferred_difficulty=DifficultyLevel.BEGINNER,
            completion_rate=0.5,
            engagement_score=0.6,
            consistency_score=0.5,
            challenge_preference=0.4,
            current_difficulty_level=0.4,
            adaptation_rate=0.1,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        performance = {"completion_rate": 0.7}
        
        adjustments = service._generate_time_adjustments(profile, performance)
        
        # Should provide more time and support
        assert adjustments["time_multiplier"] > 1.0
        assert adjustments["allow_breaks"] is True
        assert adjustments["provide_time_warnings"] is True
    
    def test_generate_time_adjustments_low_completion_rate(self, service, sample_user_profile):
        """Test time adjustments for low completion rate."""
        poor_performance = {"completion_rate": 0.4}
        
        adjustments = service._generate_time_adjustments(sample_user_profile, poor_performance)
        
        # Should provide more time
        assert adjustments["time_multiplier"] > 1.0
        assert adjustments["provide_time_warnings"] is True
    
    def test_determine_support_level_struggling_learner(self, service, sample_user_profile):
        """Test support level determination for struggling learner."""
        poor_performance = {
            "average_score": 0.3,
            "completion_rate": 0.4
        }
        
        support_level = service._determine_support_level(sample_user_profile, poor_performance)
        
        # Should provide high support
        assert support_level == "high"
    
    def test_determine_support_level_high_performer(self, service, sample_user_profile):
        """Test support level determination for high performer."""
        good_performance = {
            "average_score": 0.8,
            "completion_rate": 0.9
        }
        
        support_level = service._determine_support_level(sample_user_profile, good_performance)
        
        # Should provide low support
        assert support_level == "low"
    
    def test_determine_support_level_moderate_performer(self, service, sample_user_profile):
        """Test support level determination for moderate performer."""
        moderate_performance = {
            "average_score": 0.6,
            "completion_rate": 0.65
        }
        
        support_level = service._determine_support_level(sample_user_profile, moderate_performance)
        
        # Should provide medium support
        assert support_level == "medium"