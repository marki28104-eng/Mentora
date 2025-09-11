"""
Unit tests for PersonalizationEngine service.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from backend.src.services.personalization_engine import (
    PersonalizationEngine, AdaptedContent, CourseRecommendation
)
from backend.src.db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from backend.src.db.models.db_course import Course
from backend.src.api.schemas.analytics import UserLearningProfileCreate


class TestPersonalizationEngine:
    """Test cases for PersonalizationEngine service."""
    
    @pytest.fixture
    def engine(self):
        """Create PersonalizationEngine instance."""
        return PersonalizationEngine()
    
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
        """Create sample behavior data."""
        now = datetime.now(timezone.utc)
        return [
            UserBehaviorData(
                id="behavior_1",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.COURSE_START,
                page_url="/courses/1",
                course_id=1,
                timestamp=now - timedelta(hours=2),
                duration_seconds=3600,
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
                timestamp=now - timedelta(hours=1),
                duration_seconds=1800,
                engagement_score=0.9
            ),
            UserBehaviorData(
                id="behavior_3",
                user_id="user_123",
                session_id="session_2",
                event_type=EventType.COURSE_COMPLETE,
                page_url="/courses/1",
                course_id=1,
                timestamp=now,
                duration_seconds=600,
                engagement_score=0.85
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
    def sample_engagement_metrics(self):
        """Create sample engagement metrics."""
        now = datetime.now(timezone.utc)
        return [
            EngagementMetrics(
                id="engagement_1",
                user_id="user_123",
                course_id=1,
                time_period_start=now - timedelta(hours=24),
                time_period_end=now,
                total_time_spent=7200,
                interaction_count=45,
                page_views=12,
                completion_percentage=0.8,
                engagement_score=0.85,
                focus_score=0.7,
                progress_velocity=0.5,
                calculation_version="1.0",
                created_at=now
            )
        ]
    
    @pytest.fixture
    def sample_courses(self):
        """Create sample courses."""
        return [
            Course(
                id=1,
                title="Advanced Python Programming",
                description="Learn advanced Python concepts and techniques",
                difficulty="intermediate"
            ),
            Course(
                id=2,
                title="Data Science with Python",
                description="Introduction to data science using Python",
                difficulty="beginner"
            ),
            Course(
                id=3,
                title="Machine Learning Fundamentals",
                description="Basic concepts of machine learning",
                difficulty="intermediate"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_generate_user_profile_new_user(
        self, engine, mock_db, sample_behavior_data, sample_learning_pattern, sample_engagement_metrics
    ):
        """Test generating profile for new user."""
        with patch('backend.src.services.personalization_engine.analytics_crud') as mock_crud:
            # Mock database calls
            mock_crud.get_user_learning_profile.return_value = None  # No existing profile
            mock_crud.get_learning_pattern_by_user.return_value = sample_learning_pattern
            mock_crud.get_engagement_metrics.return_value = sample_engagement_metrics
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            mock_crud.create_user_learning_profile.return_value = Mock()
            
            # Test profile generation
            result = await engine.generate_user_profile(mock_db, "user_123")
            
            # Verify profile was created
            assert result is not None
            mock_crud.create_user_learning_profile.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_user_profile_insufficient_data(self, engine, mock_db):
        """Test profile generation with insufficient data."""
        with patch('backend.src.services.personalization_engine.analytics_crud') as mock_crud:
            # Mock insufficient behavior data
            mock_crud.get_user_learning_profile.return_value = None
            mock_crud.get_learning_pattern_by_user.return_value = None
            mock_crud.get_engagement_metrics.return_value = []
            mock_crud.get_user_behavior_data.return_value = []  # No data
            
            # Test profile generation
            result = await engine.generate_user_profile(mock_db, "user_123")
            
            # Should return None for insufficient data
            assert result is None
            mock_crud.create_user_learning_profile.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_generate_user_profile_update_existing(
        self, engine, mock_db, sample_user_profile, sample_behavior_data, 
        sample_learning_pattern, sample_engagement_metrics
    ):
        """Test updating existing user profile."""
        with patch('backend.src.services.personalization_engine.analytics_crud') as mock_crud:
            # Mock existing profile
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_learning_pattern_by_user.return_value = sample_learning_pattern
            mock_crud.get_engagement_metrics.return_value = sample_engagement_metrics
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            mock_crud.update_user_learning_profile.return_value = sample_user_profile
            
            # Test profile update
            result = await engine.generate_user_profile(mock_db, "user_123")
            
            # Verify profile was updated
            assert result is not None
            mock_crud.update_user_learning_profile.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_adapt_content_difficulty(self, engine, mock_db, sample_user_profile):
        """Test content difficulty adaptation."""
        content_metadata = {"difficulty": 0.7, "content_type": "video"}
        
        result = await engine.adapt_content_difficulty(
            mock_db, "content_123", sample_user_profile, content_metadata
        )
        
        # Verify adaptation result
        assert isinstance(result, AdaptedContent)
        assert result.content_id == "content_123"
        assert result.original_difficulty == 0.7
        assert 0.0 <= result.adapted_difficulty <= 1.0
        assert result.explanation_style == "visual"  # Based on user's learning style
        assert result.pacing_adjustment > 0.0
    
    @pytest.mark.asyncio
    async def test_adapt_content_difficulty_visual_learner(self, engine, mock_db, sample_user_profile):
        """Test content adaptation for visual learner."""
        result = await engine.adapt_content_difficulty(
            mock_db, "content_123", sample_user_profile
        )
        
        # Check visual learner modifications
        modifications = result.content_modifications
        assert modifications.get("include_diagrams") is True
        assert modifications.get("include_charts") is True
        assert modifications.get("visual_examples") is True
        assert result.explanation_style == "visual"
    
    @pytest.mark.asyncio
    async def test_adapt_content_difficulty_short_attention_span(self, engine, mock_db):
        """Test content adaptation for short attention span."""
        # Create profile with short attention span
        profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.READING,
            attention_span=15,  # Short attention span
            preferred_difficulty=DifficultyLevel.BEGINNER,
            completion_rate=0.5,
            engagement_score=0.6,
            consistency_score=0.5,
            challenge_preference=0.3,
            current_difficulty_level=0.3,
            adaptation_rate=0.1,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        result = await engine.adapt_content_difficulty(mock_db, "content_123", profile)
        
        # Check short attention span modifications
        modifications = result.content_modifications
        assert modifications.get("break_into_chunks") is True
        assert modifications.get("frequent_checkpoints") is True
        assert modifications.get("shorter_sections") is True
    
    @pytest.mark.asyncio
    async def test_recommend_learning_path(
        self, engine, mock_db, sample_user_profile, sample_courses
    ):
        """Test learning path recommendation."""
        with patch('backend.src.services.personalization_engine.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            
            # Mock course search
            with patch.object(engine, '_get_courses_by_topic', return_value=sample_courses):
                result = await engine.recommend_learning_path(
                    mock_db, "user_123", "python", max_recommendations=3
                )
            
            # Verify recommendations
            assert isinstance(result, list)
            assert len(result) <= 3
            
            for recommendation in result:
                assert isinstance(recommendation, CourseRecommendation)
                assert recommendation.recommendation_score > 0.0
                assert recommendation.course_id in [1, 2, 3]
                assert recommendation.reason is not None
    
    @pytest.mark.asyncio
    async def test_recommend_learning_path_no_profile(self, engine, mock_db, sample_courses):
        """Test learning path recommendation without existing profile."""
        with patch('backend.src.services.personalization_engine.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = None
            
            # Mock profile generation failure
            with patch.object(engine, 'generate_user_profile', return_value=None):
                result = await engine.recommend_learning_path(
                    mock_db, "user_123", "python"
                )
            
            # Should return empty list without profile
            assert result == []
    
    def test_calculate_profile_metrics(
        self, engine, sample_behavior_data, sample_learning_pattern, sample_engagement_metrics
    ):
        """Test profile metrics calculation."""
        metrics = engine._calculate_profile_metrics(
            sample_behavior_data, sample_learning_pattern, sample_engagement_metrics
        )
        
        # Verify calculated metrics
        assert isinstance(metrics, dict)
        assert "completion_rate" in metrics
        assert "engagement_score" in metrics
        assert "consistency_score" in metrics
        assert "learning_style" in metrics
        assert "preferred_difficulty" in metrics
        
        # Check specific values
        assert 0.0 <= metrics["completion_rate"] <= 1.0
        assert 0.0 <= metrics["engagement_score"] <= 1.0
        assert metrics["learning_style"] == LearningStyleType.VISUAL
        assert metrics["courses_completed"] >= 0
    
    def test_calculate_consistency_score_insufficient_data(self, engine):
        """Test consistency score with insufficient data."""
        # Test with less than 7 data points
        behavior_data = [
            UserBehaviorData(
                id=f"behavior_{i}",
                user_id="user_123",
                session_id="session_1",
                event_type=EventType.PAGE_VIEW,
                page_url="/test",
                timestamp=datetime.now(timezone.utc),
                engagement_score=0.5
            ) for i in range(3)
        ]
        
        score = engine._calculate_consistency_score(behavior_data)
        assert score == 0.0
    
    def test_calculate_consistency_score_consistent_learner(self, engine):
        """Test consistency score for consistent learner."""
        # Create data with consistent daily activity
        base_date = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        behavior_data = []
        
        for day in range(7):  # 7 days of data
            for activity in range(5):  # 5 activities per day (consistent)
                behavior_data.append(
                    UserBehaviorData(
                        id=f"behavior_{day}_{activity}",
                        user_id="user_123",
                        session_id=f"session_{day}",
                        event_type=EventType.PAGE_VIEW,
                        page_url="/test",
                        timestamp=base_date - timedelta(days=day, minutes=activity*10),
                        engagement_score=0.5
                    )
                )
        
        score = engine._calculate_consistency_score(behavior_data)
        assert score > 0.8  # Should be high for consistent activity
    
    def test_calculate_adapted_difficulty(self, engine, sample_user_profile):
        """Test difficulty adaptation calculation."""
        original_difficulty = 0.5
        adapted = engine._calculate_adapted_difficulty(original_difficulty, sample_user_profile)
        
        # Should be within valid range
        assert 0.1 <= adapted <= 0.9
        
        # Should be influenced by user profile
        assert adapted != original_difficulty  # Should be adapted
    
    def test_generate_content_modifications_visual_learner(self, engine, sample_user_profile):
        """Test content modifications for visual learner."""
        modifications = engine._generate_content_modifications(sample_user_profile, None)
        
        # Visual learner should get visual modifications
        assert modifications.get("include_diagrams") is True
        assert modifications.get("include_charts") is True
        assert modifications.get("visual_examples") is True
        assert modifications.get("color_coding") is True
    
    def test_generate_content_modifications_kinesthetic_learner(self, engine):
        """Test content modifications for kinesthetic learner."""
        profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.KINESTHETIC,
            attention_span=30,
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
        
        modifications = engine._generate_content_modifications(profile, None)
        
        # Kinesthetic learner should get interactive modifications
        assert modifications.get("interactive_elements") is True
        assert modifications.get("hands_on_exercises") is True
        assert modifications.get("practical_examples") is True
        assert modifications.get("step_by_step_guidance") is True
    
    def test_determine_explanation_style(self, engine, sample_user_profile):
        """Test explanation style determination."""
        style = engine._determine_explanation_style(sample_user_profile)
        assert style == "visual"  # Based on visual learning style
    
    def test_calculate_pacing_adjustment(self, engine, sample_user_profile):
        """Test pacing adjustment calculation."""
        pacing = engine._calculate_pacing_adjustment(sample_user_profile)
        
        # Should be within reasonable bounds
        assert 0.5 <= pacing <= 2.0
        
        # High completion rate should increase pacing
        assert pacing > 1.0  # sample_user_profile has high completion rate
    
    def test_calculate_topic_match_score(self, engine):
        """Test topic matching score calculation."""
        course = Course(
            id=1,
            title="Python Programming Fundamentals",
            description="Learn the basics of Python programming language"
        )
        
        # Exact match
        score = engine._calculate_topic_match_score(course, "Python")
        assert score > 0.5
        
        # Partial match
        score = engine._calculate_topic_match_score(course, "Programming")
        assert score > 0.0
        
        # No match
        score = engine._calculate_topic_match_score(course, "Mathematics")
        assert score >= 0.0
    
    def test_calculate_difficulty_match_score(self, engine, sample_user_profile):
        """Test difficulty matching score calculation."""
        course = Course(id=1, title="Test Course", description="Test")
        
        score = engine._calculate_difficulty_match_score(course, sample_user_profile)
        
        # Should return a valid score
        assert 0.0 <= score <= 1.0
    
    def test_estimate_completion_time(self, engine, sample_user_profile):
        """Test completion time estimation."""
        course = Course(id=1, title="Test Course", description="Test")
        
        time = engine._estimate_completion_time(course, sample_user_profile)
        
        # Should return reasonable time estimate
        assert time > 0
        assert isinstance(time, int)
    
    def test_generate_recommendation_reason(self, engine, sample_user_profile):
        """Test recommendation reason generation."""
        course = Course(id=1, title="Test Course", description="Test")
        
        reason = engine._generate_recommendation_reason(course, sample_user_profile, 0.8)
        
        # Should return non-empty string
        assert isinstance(reason, str)
        assert len(reason) > 0
        assert "visual learners" in reason.lower()  # Should mention learning style