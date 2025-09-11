"""
Unit tests for CourseRecommendationService.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.course_recommendation_service import (
    CourseRecommendationService, CourseRecommendation
)
from db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from db.models.db_course import Course, Chapter


class TestCourseRecommendationService:
    """Test cases for CourseRecommendationService."""
    
    @pytest.fixture
    def service(self):
        """Create CourseRecommendationService instance."""
        return CourseRecommendationService()
    
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
    def sample_courses(self):
        """Create sample courses."""
        return [
            Course(
                id=1,
                title="Python Programming Fundamentals",
                description="Learn the basics of Python programming language",
                difficulty="beginner"
            ),
            Course(
                id=2,
                title="Advanced Data Science with Python",
                description="Master advanced data science techniques using Python",
                difficulty="advanced"
            ),
            Course(
                id=3,
                title="Web Development with JavaScript",
                description="Build modern web applications using JavaScript",
                difficulty="intermediate"
            ),
            Course(
                id=4,
                title="Machine Learning Basics",
                description="Introduction to machine learning concepts and algorithms",
                difficulty="intermediate"
            )
        ]
    
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
                user_id="user_456",
                session_id="session_2",
                event_type=EventType.COURSE_COMPLETE,
                page_url="/courses/2",
                course_id=2,
                timestamp=now - timedelta(hours=1),
                duration_seconds=7200,
                engagement_score=0.9
            ),
            UserBehaviorData(
                id="behavior_3",
                user_id="user_789",
                session_id="session_3",
                event_type=EventType.COURSE_START,
                page_url="/courses/3",
                course_id=3,
                timestamp=now,
                duration_seconds=1800,
                engagement_score=0.7
            )
        ]
    
    @pytest.fixture
    def sample_user_profiles(self):
        """Create sample user profiles for similarity testing."""
        return [
            UserLearningProfile(
                id="profile_2",
                user_id="user_456",
                learning_style=LearningStyleType.VISUAL,  # Same as user_123
                completion_rate=0.8,  # Similar to user_123
                engagement_score=0.75,
                challenge_preference=0.65,
                current_difficulty_level=0.65,
                last_updated=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            ),
            UserLearningProfile(
                id="profile_3",
                user_id="user_789",
                learning_style=LearningStyleType.AUDITORY,  # Different from user_123
                completion_rate=0.4,  # Different from user_123
                engagement_score=0.5,
                challenge_preference=0.3,
                current_difficulty_level=0.3,
                last_updated=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
        ]
    
    @pytest.mark.asyncio
    async def test_get_course_recommendations_successful(
        self, service, mock_db, sample_user_profile, sample_courses
    ):
        """Test successful course recommendation generation."""
        with patch('services.course_recommendation_service.analytics_crud') as mock_crud:
            # Mock database calls
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            mock_crud.get_user_behavior_data.return_value = []
            
            # Mock course queries
            mock_db.query.return_value.all.return_value = sample_courses
            
            # Mock internal methods
            service._get_completed_courses = Mock(return_value=[])
            service._calculate_content_based_score = AsyncMock(return_value=0.8)
            service._calculate_collaborative_score = AsyncMock(return_value=0.6)
            service._calculate_popularity_score = AsyncMock(return_value=0.7)
            service._get_similar_users = AsyncMock(return_value=["user_456"])
            
            result = await service.get_course_recommendations(
                mock_db, "user_123", max_recommendations=3
            )
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) <= 3
            
            for recommendation in result:
                assert isinstance(recommendation, CourseRecommendation)
                assert recommendation.course_id in [1, 2, 3, 4]
                assert 0.0 <= recommendation.recommendation_score <= 1.0
                assert recommendation.reason is not None
                assert len(recommendation.reason) > 0
    
    @pytest.mark.asyncio
    async def test_get_course_recommendations_no_profile(
        self, service, mock_db, sample_courses
    ):
        """Test course recommendations without user profile."""
        with patch('services.course_recommendation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = None
            
            # Mock default recommendations
            service._get_default_recommendations = AsyncMock(return_value=[
                CourseRecommendation(
                    course_id=1,
                    title="Default Course",
                    description="Default description",
                    recommendation_score=0.5,
                    content_based_score=0.0,
                    collaborative_score=0.0,
                    popularity_score=0.5,
                    difficulty_match_score=0.0,
                    learning_style_match_score=0.0,
                    reason="Popular course for new learners",
                    recommended_difficulty=DifficultyLevel.BEGINNER,
                    estimated_completion_time=120
                )
            ])
            
            result = await service.get_course_recommendations(mock_db, "user_123")
            
            # Should return default recommendations
            assert len(result) > 0
            assert result[0].reason == "Popular course for new learners"
    
    @pytest.mark.asyncio
    async def test_get_course_recommendations_with_topic_filter(
        self, service, mock_db, sample_user_profile, sample_courses
    ):
        """Test course recommendations with topic filter."""
        with patch('services.course_recommendation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_learning_profile.return_value = sample_user_profile
            
            # Filter courses by topic
            python_courses = [c for c in sample_courses if "python" in c.title.lower()]
            mock_db.query.return_value.filter.return_value.all.return_value = python_courses
            
            service._get_completed_courses = Mock(return_value=[])
            service._calculate_content_based_score = AsyncMock(return_value=0.9)  # High score for topic match
            service._calculate_collaborative_score = AsyncMock(return_value=0.5)
            service._calculate_popularity_score = AsyncMock(return_value=0.6)
            service._get_similar_users = AsyncMock(return_value=[])
            
            result = await service.get_course_recommendations(
                mock_db, "user_123", topic_filter="python"
            )
            
            # Should return Python-related courses
            assert len(result) > 0
            for recommendation in result:
                assert "python" in recommendation.title.lower()
    
    @pytest.mark.asyncio
    async def test_get_similar_courses(self, service, mock_db, sample_courses):
        """Test getting similar courses."""
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = sample_courses[0]
        mock_db.query.return_value.filter.return_value.all.return_value = sample_courses[1:]
        
        result = await service.get_similar_courses(mock_db, 1, max_recommendations=2)
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) <= 2
        
        for recommendation in result:
            assert isinstance(recommendation, CourseRecommendation)
            assert recommendation.course_id != 1  # Should not include the reference course
            assert recommendation.recommendation_score > 0.0
    
    @pytest.mark.asyncio
    async def test_get_similar_courses_no_reference(self, service, mock_db):
        """Test getting similar courses when reference course doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = await service.get_similar_courses(mock_db, 999)
        
        # Should return empty list
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_trending_courses(
        self, service, mock_db, sample_courses, sample_behavior_data
    ):
        """Test getting trending courses."""
        with patch('services.course_recommendation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_behavior_data.return_value = sample_behavior_data
            
            # Mock course queries for each course in behavior data
            def mock_course_query(course_id):
                return next((c for c in sample_courses if c.id == course_id), None)
            
            mock_db.query.return_value.filter.return_value.first.side_effect = lambda: mock_course_query(1)
            
            result = await service.get_trending_courses(mock_db, max_recommendations=3)
            
            # Verify result
            assert isinstance(result, list)
            
            for recommendation in result:
                assert isinstance(recommendation, CourseRecommendation)
                assert "trending" in recommendation.reason.lower()
                assert recommendation.popularity_score > 0
    
    def test_calculate_difficulty_match_score(self, service, sample_user_profile):
        """Test difficulty match score calculation."""
        # Test course with intermediate difficulty
        course = Course(id=1, title="Test Course", difficulty="intermediate")
        
        score = service._calculate_difficulty_match_score(course, sample_user_profile)
        
        # Should return a reasonable match score
        assert 0.0 <= score <= 1.0
        # Intermediate course should match well with intermediate user level
        assert score > 0.5
    
    def test_calculate_learning_style_match_score_visual(self, service, sample_user_profile):
        """Test learning style match for visual learner."""
        course = Course(id=1, title="Test Course")
        
        score = service._calculate_learning_style_match_score(course, sample_user_profile)
        
        # Visual learner should get high score
        assert score >= 0.7
    
    def test_calculate_learning_style_match_score_reading(self, service):
        """Test learning style match for reading learner."""
        reading_profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            learning_style=LearningStyleType.READING,
            current_difficulty_level=0.5,
            completion_rate=0.7,
            engagement_score=0.7,
            challenge_preference=0.5,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        course = Course(id=1, title="Test Course")
        
        score = service._calculate_learning_style_match_score(course, reading_profile)
        
        # Reading learner should get very high score (most courses have text)
        assert score >= 0.8
    
    def test_calculate_topic_relevance_exact_match(self, service):
        """Test topic relevance with exact match."""
        course = Course(
            id=1,
            title="Python Programming Fundamentals",
            description="Learn Python programming"
        )
        
        score = service._calculate_topic_relevance(course, "Python")
        
        # Should get high score for exact match
        assert score >= 0.7
    
    def test_calculate_topic_relevance_partial_match(self, service):
        """Test topic relevance with partial match."""
        course = Course(
            id=1,
            title="Programming with Multiple Languages",
            description="Learn various programming languages"
        )
        
        score = service._calculate_topic_relevance(course, "Programming Languages")
        
        # Should get moderate score for partial match
        assert score > 0.0
        assert score < 1.0
    
    def test_calculate_topic_relevance_no_match(self, service):
        """Test topic relevance with no match."""
        course = Course(
            id=1,
            title="Cooking Basics",
            description="Learn to cook delicious meals"
        )
        
        score = service._calculate_topic_relevance(course, "Programming")
        
        # Should get very low or zero score
        assert score <= 0.1
    
    def test_calculate_user_similarity_identical_users(self, service, sample_user_profile):
        """Test user similarity calculation for identical profiles."""
        # Create identical profile
        identical_profile = UserLearningProfile(
            id="profile_2",
            user_id="user_456",
            learning_style=sample_user_profile.learning_style,
            completion_rate=sample_user_profile.completion_rate,
            engagement_score=sample_user_profile.engagement_score,
            challenge_preference=sample_user_profile.challenge_preference,
            current_difficulty_level=sample_user_profile.current_difficulty_level,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        similarity = service._calculate_user_similarity(sample_user_profile, identical_profile)
        
        # Should be very high similarity
        assert similarity >= 0.9
    
    def test_calculate_user_similarity_different_users(self, service, sample_user_profile):
        """Test user similarity calculation for different profiles."""
        different_profile = UserLearningProfile(
            id="profile_2",
            user_id="user_456",
            learning_style=LearningStyleType.AUDITORY,  # Different
            completion_rate=0.2,  # Very different
            engagement_score=0.3,  # Very different
            challenge_preference=0.1,  # Very different
            current_difficulty_level=0.2,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        similarity = service._calculate_user_similarity(sample_user_profile, different_profile)
        
        # Should be low similarity
        assert similarity <= 0.5
    
    def test_calculate_course_similarity_identical_courses(self, service):
        """Test course similarity for identical courses."""
        course1 = Course(
            id=1,
            title="Python Programming",
            description="Learn Python programming language"
        )
        course2 = Course(
            id=2,
            title="Python Programming",
            description="Learn Python programming language"
        )
        
        similarity = service._calculate_course_similarity(course1, course2)
        
        # Should be very high similarity
        assert similarity >= 0.8
    
    def test_calculate_course_similarity_related_courses(self, service):
        """Test course similarity for related courses."""
        course1 = Course(
            id=1,
            title="Python Programming Basics",
            description="Introduction to Python programming"
        )
        course2 = Course(
            id=2,
            title="Advanced Python Programming",
            description="Advanced Python programming techniques"
        )
        
        similarity = service._calculate_course_similarity(course1, course2)
        
        # Should have moderate similarity (both about Python programming)
        assert 0.3 <= similarity <= 0.8
    
    def test_calculate_course_similarity_unrelated_courses(self, service):
        """Test course similarity for unrelated courses."""
        course1 = Course(
            id=1,
            title="Python Programming",
            description="Learn Python programming language"
        )
        course2 = Course(
            id=2,
            title="Cooking Basics",
            description="Learn to cook delicious meals"
        )
        
        similarity = service._calculate_course_similarity(course1, course2)
        
        # Should have very low similarity
        assert similarity <= 0.2
    
    def test_extract_course_tags(self, service):
        """Test course tag extraction."""
        course = Course(
            id=1,
            title="Python Programming Fundamentals",
            description="Learn the basics of Python programming language and data structures"
        )
        
        tags = service._extract_course_tags(course)
        
        # Should extract relevant tags
        assert isinstance(tags, list)
        assert len(tags) > 0
        
        # Should include words from title and description
        tag_text = " ".join(tags)
        assert "python" in tag_text
        assert "programming" in tag_text
    
    def test_generate_recommendation_reason_content_based(self, service):
        """Test recommendation reason generation for content-based recommendation."""
        course = Course(id=1, title="Test Course")
        
        reason = service._generate_recommendation_reason(
            course,
            content_score=0.9,  # High content score
            collaborative_score=0.3,
            popularity_score=0.4,
            difficulty_score=0.6,
            style_score=0.5
        )
        
        # Should mention content match
        assert "interests" in reason.lower() or "match" in reason.lower()
    
    def test_generate_recommendation_reason_collaborative(self, service):
        """Test recommendation reason generation for collaborative recommendation."""
        course = Course(id=1, title="Test Course")
        
        reason = service._generate_recommendation_reason(
            course,
            content_score=0.4,
            collaborative_score=0.8,  # High collaborative score
            popularity_score=0.3,
            difficulty_score=0.5,
            style_score=0.4
        )
        
        # Should mention similar learners
        assert "similar" in reason.lower() or "learners" in reason.lower()
    
    def test_generate_recommendation_reason_popularity(self, service):
        """Test recommendation reason generation for popularity-based recommendation."""
        course = Course(id=1, title="Test Course")
        
        reason = service._generate_recommendation_reason(
            course,
            content_score=0.3,
            collaborative_score=0.2,
            popularity_score=0.9,  # High popularity score
            difficulty_score=0.4,
            style_score=0.3
        )
        
        # Should mention popularity
        assert "popular" in reason.lower()
    
    def test_determine_recommended_difficulty_beginner(self, service):
        """Test difficulty determination for beginner user."""
        beginner_profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            current_difficulty_level=0.2,  # Low level
            completion_rate=0.5,
            engagement_score=0.6,
            challenge_preference=0.3,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        course = Course(id=1, title="Test Course")
        
        difficulty = service._determine_recommended_difficulty(course, beginner_profile)
        
        assert difficulty == DifficultyLevel.BEGINNER
    
    def test_determine_recommended_difficulty_advanced(self, service):
        """Test difficulty determination for advanced user."""
        advanced_profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            current_difficulty_level=0.8,  # High level
            completion_rate=0.9,
            engagement_score=0.9,
            challenge_preference=0.8,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        course = Course(id=1, title="Test Course")
        
        difficulty = service._determine_recommended_difficulty(course, advanced_profile)
        
        assert difficulty == DifficultyLevel.ADVANCED
    
    def test_estimate_completion_time_fast_learner(self, service):
        """Test completion time estimation for fast learner."""
        fast_profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            completion_rate=0.9,  # High completion rate
            average_session_duration=90,
            current_difficulty_level=0.7,
            engagement_score=0.8,
            challenge_preference=0.6,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        course = Course(id=1, title="Test Course")
        
        time = service._estimate_completion_time(course, fast_profile)
        
        # Should be less than base time for fast learners
        assert time < 120  # Less than default 2 hours
        assert time > 0
    
    def test_estimate_completion_time_slow_learner(self, service):
        """Test completion time estimation for slow learner."""
        slow_profile = UserLearningProfile(
            id="profile_1",
            user_id="user_123",
            completion_rate=0.3,  # Low completion rate
            average_session_duration=30,
            current_difficulty_level=0.3,
            engagement_score=0.4,
            challenge_preference=0.2,
            last_updated=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        course = Course(id=1, title="Test Course")
        
        time = service._estimate_completion_time(course, slow_profile)
        
        # Should be more than base time for slow learners
        assert time > 120  # More than default 2 hours
    
    @pytest.mark.asyncio
    async def test_find_similar_users(self, service, mock_db, sample_user_profile, sample_user_profiles):
        """Test finding similar users."""
        with patch('services.course_recommendation_service.analytics_crud') as mock_crud:
            mock_crud.get_all_user_learning_profiles.return_value = sample_user_profiles
            
            similar_users = await service._find_similar_users(mock_db, "user_123", sample_user_profile)
            
            # Should find similar users
            assert isinstance(similar_users, list)
            
            # Should not include the user themselves
            user_ids = [user_id for user_id, similarity in similar_users]
            assert "user_123" not in user_ids
            
            # Should include similarity scores
            for user_id, similarity in similar_users:
                assert isinstance(user_id, str)
                assert 0.0 <= similarity <= 1.0
    
    def test_get_completed_courses(self, service, mock_db):
        """Test getting completed courses for a user."""
        completed_behavior = [
            UserBehaviorData(
                id="behavior_1",
                user_id="user_123",
                event_type=EventType.COURSE_COMPLETE,
                course_id=1,
                timestamp=datetime.now(timezone.utc)
            ),
            UserBehaviorData(
                id="behavior_2",
                user_id="user_123",
                event_type=EventType.COURSE_COMPLETE,
                course_id=2,
                timestamp=datetime.now(timezone.utc)
            )
        ]
        
        with patch('services.course_recommendation_service.analytics_crud') as mock_crud:
            mock_crud.get_user_behavior_data.return_value = completed_behavior
            
            completed_courses = service._get_completed_courses(mock_db, "user_123")
            
            # Should return list of completed course IDs
            assert isinstance(completed_courses, list)
            assert 1 in completed_courses
            assert 2 in completed_courses