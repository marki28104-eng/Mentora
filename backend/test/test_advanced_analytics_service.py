"""
Tests for Advanced Analytics Service.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from backend.src.services.advanced_analytics_service import (
    AdvancedAnalyticsService, PredictiveAnalyticsEngine, 
    CohortAnalysisEngine, RealTimePersonalizationEngine,
    PredictiveOutcome, CohortAnalysis, RealTimePersonalization
)
from backend.src.db.models.db_analytics import (
    UserLearningProfile, UserBehaviorData, LearningPattern,
    LearningStyleType, DifficultyLevel, EventType
)


class TestPredictiveAnalyticsEngine:
    """Test cases for PredictiveAnalyticsEngine."""
    
    @pytest.fixture
    def engine(self):
        return PredictiveAnalyticsEngine()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user_profile(self):
        return UserLearningProfile(
            id="profile_1",
            user_id="user_1",
            learning_style=LearningStyleType.VISUAL,
            attention_span=30,
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            completion_rate=0.75,
            average_session_duration=45,
            total_learning_time=1200,
            courses_completed=5,
            engagement_score=0.8,
            consistency_score=0.7,
            challenge_preference=0.6,
            current_difficulty_level=0.7,
            adaptation_rate=0.1,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
    
    @pytest.fixture
    def sample_behavior_data(self):
        return [
            UserBehaviorData(
                id="behavior_1",
                user_id="user_1",
                session_id="session_1",
                event_type=EventType.PAGE_VIEW,
                page_url="/courses/1/chapters/1",
                course_id=1,
                chapter_id=1,
                timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
                duration_seconds=300,
                metadata={"content_type": "video"},
                engagement_score=0.8,
                is_anonymized=False,
                created_at=datetime.now(timezone.utc)
            ),
            UserBehaviorData(
                id="behavior_2",
                user_id="user_1",
                session_id="session_1",
                event_type=EventType.CONTENT_INTERACTION,
                page_url="/courses/1/chapters/1",
                course_id=1,
                chapter_id=1,
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=30),
                duration_seconds=120,
                metadata={"interaction_type": "quiz"},
                engagement_score=0.9,
                is_anonymized=False,
                created_at=datetime.now(timezone.utc)
            )
        ]
    
    @pytest.mark.asyncio
    async def test_train_predictive_models_insufficient_data(self, engine, mock_db):
        """Test training with insufficient data."""
        with patch.object(engine, '_prepare_predictive_training_data', return_value=AsyncMock()):
            engine._prepare_predictive_training_data.return_value = []
            
            result = await engine.train_predictive_models(mock_db)
            
            assert 'error' in result
            assert 'Insufficient training data' in result['error']
    
    @pytest.mark.asyncio
    async def test_predict_learning_outcome_not_trained(self, engine, mock_db):
        """Test prediction when models are not trained."""
        result = await engine.predict_learning_outcome(mock_db, "user_1", 1)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_predict_learning_outcome_no_profile(self, engine, mock_db):
        """Test prediction when user has no profile."""
        engine.is_trained = True
        
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile', return_value=None):
            result = await engine.predict_learning_outcome(mock_db, "user_1", 1)
            
            assert result is None
    
    def test_analyze_session_patterns_empty_data(self, engine):
        """Test session pattern analysis with empty data."""
        result = engine._analyze_session_patterns([])
        
        assert result == {}
    
    def test_analyze_session_patterns_with_data(self, engine, sample_behavior_data):
        """Test session pattern analysis with sample data."""
        result = engine._analyze_session_patterns(sample_behavior_data)
        
        assert 'initial_engagement' in result
        assert 'session_frequency' in result
        assert 'preferred_time' in result
        assert isinstance(result['initial_engagement'], float)
        assert 0 <= result['initial_engagement'] <= 1
    
    def test_encode_learning_style(self, engine):
        """Test learning style encoding."""
        assert engine._encode_learning_style(LearningStyleType.VISUAL) == 0.0
        assert engine._encode_learning_style(LearningStyleType.AUDITORY) == 0.25
        assert engine._encode_learning_style(LearningStyleType.KINESTHETIC) == 0.5
        assert engine._encode_learning_style(LearningStyleType.READING) == 0.75
        assert engine._encode_learning_style(LearningStyleType.MIXED) == 0.5
        assert engine._encode_learning_style(LearningStyleType.UNKNOWN) == 0.5
    
    def test_generate_outcome_recommendations(self, engine):
        """Test recommendation generation based on predictions."""
        factors = {
            'session_frequency': 0.3,
            'difficulty_preference': 0.25,
            'engagement': 0.2
        }
        
        recommendations = engine._generate_outcome_recommendations(
            completion_pred=0.4,
            success_prob=0.5,
            engagement_pred=0.3,
            factors=factors
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        assert all(isinstance(rec, str) for rec in recommendations)


class TestCohortAnalysisEngine:
    """Test cases for CohortAnalysisEngine."""
    
    @pytest.fixture
    def engine(self):
        return CohortAnalysisEngine()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user_profiles(self):
        return [
            UserLearningProfile(
                id="profile_1",
                user_id="user_1",
                learning_style=LearningStyleType.VISUAL,
                preferred_difficulty=DifficultyLevel.BEGINNER,
                engagement_score=0.8,
                completion_rate=0.7,
                created_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc)
            ),
            UserLearningProfile(
                id="profile_2",
                user_id="user_2",
                learning_style=LearningStyleType.AUDITORY,
                preferred_difficulty=DifficultyLevel.INTERMEDIATE,
                engagement_score=0.6,
                completion_rate=0.5,
                created_at=datetime(2024, 1, 20, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc)
            ),
            UserLearningProfile(
                id="profile_3",
                user_id="user_3",
                learning_style=LearningStyleType.VISUAL,
                preferred_difficulty=DifficultyLevel.ADVANCED,
                engagement_score=0.9,
                completion_rate=0.9,
                created_at=datetime(2024, 2, 5, tzinfo=timezone.utc),
                last_updated=datetime.now(timezone.utc)
            )
        ]
    
    def test_create_cohorts_by_registration_month(self, engine, sample_user_profiles):
        """Test cohort creation by registration month."""
        cohorts = engine._create_cohorts(sample_user_profiles, "registration_month")
        
        assert "2024-01" in cohorts
        assert "2024-02" in cohorts
        assert len(cohorts["2024-01"]) == 2
        assert len(cohorts["2024-02"]) == 1
    
    def test_create_cohorts_by_learning_style(self, engine, sample_user_profiles):
        """Test cohort creation by learning style."""
        cohorts = engine._create_cohorts(sample_user_profiles, "learning_style")
        
        assert "visual" in cohorts
        assert "auditory" in cohorts
        assert len(cohorts["visual"]) == 2
        assert len(cohorts["auditory"]) == 1
    
    def test_create_cohorts_by_difficulty_level(self, engine, sample_user_profiles):
        """Test cohort creation by difficulty level."""
        cohorts = engine._create_cohorts(sample_user_profiles, "difficulty_level")
        
        assert "beginner" in cohorts
        assert "intermediate" in cohorts
        assert "advanced" in cohorts
        assert len(cohorts["beginner"]) == 1
        assert len(cohorts["intermediate"]) == 1
        assert len(cohorts["advanced"]) == 1
    
    def test_create_cohorts_by_engagement_level(self, engine, sample_user_profiles):
        """Test cohort creation by engagement level."""
        cohorts = engine._create_cohorts(sample_user_profiles, "engagement_level")
        
        assert "high_engagement" in cohorts
        assert "medium_engagement" in cohorts
        assert len(cohorts["high_engagement"]) == 2  # 0.8 and 0.9
        assert len(cohorts["medium_engagement"]) == 1  # 0.6
    
    def test_calculate_cohort_performance(self, engine, sample_user_profiles):
        """Test cohort performance calculation."""
        performance = engine._calculate_cohort_performance(sample_user_profiles)
        
        assert 'avg_completion_rate' in performance
        assert 'avg_engagement_score' in performance
        assert 'high_performers_pct' in performance
        assert 'low_performers_pct' in performance
        
        # Check calculated values
        expected_avg_completion = (0.7 + 0.5 + 0.9) / 3
        assert abs(performance['avg_completion_rate'] - expected_avg_completion) < 0.01
    
    def test_identify_cohort_characteristics(self, engine, sample_user_profiles):
        """Test cohort characteristic identification."""
        characteristics = engine._identify_cohort_characteristics(sample_user_profiles)
        
        assert isinstance(characteristics, list)
        assert all(isinstance(char, str) for char in characteristics)
        
        # Should identify high engagement cohort (2/3 users have > 0.7 engagement)
        assert any("High engagement" in char for char in characteristics)


class TestRealTimePersonalizationEngine:
    """Test cases for RealTimePersonalizationEngine."""
    
    @pytest.fixture
    def engine(self):
        return RealTimePersonalizationEngine()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user_profile(self):
        return UserLearningProfile(
            id="profile_1",
            user_id="user_1",
            learning_style=LearningStyleType.VISUAL,
            attention_span=20,  # Short attention span
            preferred_difficulty=DifficultyLevel.INTERMEDIATE,
            completion_rate=0.75,
            engagement_score=0.8,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
    
    @pytest.mark.asyncio
    async def test_monitor_learning_session_new_session(self, engine, mock_db):
        """Test monitoring a new learning session."""
        event_data = {
            'event_type': 'page_view',
            'content_type': 'video',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        result = await engine.monitor_learning_session(
            mock_db, "user_1", "session_1", event_data
        )
        
        # First event shouldn't trigger adjustments
        assert result is None
        assert "session_1" in engine.session_data
        assert engine.session_data["session_1"]["user_id"] == "user_1"
    
    def test_analyze_current_session_empty(self, engine):
        """Test session analysis with no events."""
        session = {
            'user_id': 'user_1',
            'start_time': datetime.now(timezone.utc),
            'events': []
        }
        
        result = engine._analyze_current_session(session)
        
        assert result == {}
    
    def test_analyze_current_session_with_events(self, engine):
        """Test session analysis with events."""
        now = datetime.now(timezone.utc)
        session = {
            'user_id': 'user_1',
            'start_time': now - timedelta(minutes=10),
            'events': [
                {
                    'timestamp': now - timedelta(minutes=2),
                    'event_type': 'content_interaction',
                    'data': {}
                },
                {
                    'timestamp': now - timedelta(minutes=1),
                    'event_type': 'click',
                    'data': {}
                }
            ]
        }
        
        result = engine._analyze_current_session(session)
        
        assert 'session_duration' in result
        assert 'recent_interaction_rate' in result
        assert 'attention_score' in result
        assert result['session_duration'] == 10.0
        assert result['total_events'] == 2
    
    def test_determine_real_time_adjustments_low_engagement(self, engine, mock_db, sample_user_profile):
        """Test adjustments for low engagement."""
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile', return_value=sample_user_profile):
            session_analysis = {
                'recent_interaction_rate': 0.2,  # Below threshold
                'session_duration': 30,
                'struggle_indicators': 0,
                'success_indicators': 0,
                'attention_score': 0.8
            }
            
            result = engine._determine_real_time_adjustments(
                mock_db, "user_1", session_analysis
            )
            
            assert 'engagement_boost' in result['adjustments']
            assert 'low_engagement' in result['triggers']
            assert result['confidence'] > 0
    
    def test_determine_real_time_adjustments_high_struggle(self, engine, mock_db, sample_user_profile):
        """Test adjustments for high struggle indicators."""
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile', return_value=sample_user_profile):
            session_analysis = {
                'recent_interaction_rate': 0.5,
                'session_duration': 20,
                'struggle_indicators': 3,  # Above threshold
                'success_indicators': 0,
                'attention_score': 0.6
            }
            
            result = engine._determine_real_time_adjustments(
                mock_db, "user_1", session_analysis
            )
            
            assert 'difficulty_reduction' in result['adjustments']
            assert 'high_struggle' in result['triggers']
            assert result['adjustments']['difficulty_reduction']['provide_hints'] is True
    
    def test_determine_real_time_adjustments_fast_progress(self, engine, mock_db, sample_user_profile):
        """Test adjustments for fast progress."""
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile', return_value=sample_user_profile):
            session_analysis = {
                'recent_interaction_rate': 0.8,
                'session_duration': 15,
                'struggle_indicators': 0,
                'success_indicators': 4,  # Above threshold
                'attention_score': 0.9
            }
            
            result = engine._determine_real_time_adjustments(
                mock_db, "user_1", session_analysis
            )
            
            assert 'difficulty_increase' in result['adjustments']
            assert 'fast_progress' in result['triggers']
            assert result['adjustments']['difficulty_increase']['increase_challenge'] is True
    
    def test_determine_real_time_adjustments_attention_span_exceeded(self, engine, mock_db, sample_user_profile):
        """Test adjustments when attention span is exceeded."""
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile', return_value=sample_user_profile):
            session_analysis = {
                'recent_interaction_rate': 0.5,
                'session_duration': 25,  # Exceeds user's 20-minute attention span
                'struggle_indicators': 0,
                'success_indicators': 0,
                'attention_score': 0.6
            }
            
            result = engine._determine_real_time_adjustments(
                mock_db, "user_1", session_analysis
            )
            
            assert 'pacing_adjustment' in result['adjustments']
            assert 'attention_span_exceeded' in result['triggers']
            assert result['adjustments']['pacing_adjustment']['suggest_break'] is True
    
    def test_cleanup_old_sessions(self, engine):
        """Test cleanup of old session data."""
        # Add some test sessions
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        engine.session_data = {
            'old_session': {'start_time': old_time, 'user_id': 'user1'},
            'recent_session': {'start_time': recent_time, 'user_id': 'user2'}
        }
        
        engine.cleanup_old_sessions(hours_old=24)
        
        assert 'old_session' not in engine.session_data
        assert 'recent_session' in engine.session_data


class TestAdvancedAnalyticsService:
    """Test cases for AdvancedAnalyticsService."""
    
    @pytest.fixture
    def service(self):
        return AdvancedAnalyticsService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.mark.asyncio
    async def test_initialize_models(self, service, mock_db):
        """Test model initialization."""
        with patch.object(service.predictive_engine, 'train_predictive_models') as mock_train:
            mock_train.return_value = {'status': 'success'}
            
            result = await service.initialize_models(mock_db)
            
            assert 'predictive_models' in result
            assert result['status'] == 'initialized'
            mock_train.assert_called_once_with(mock_db)
    
    @pytest.mark.asyncio
    async def test_get_learning_outcome_prediction(self, service, mock_db):
        """Test getting learning outcome prediction."""
        mock_prediction = PredictiveOutcome(
            user_id="user_1",
            prediction_type="learning_outcome",
            predicted_value=0.8,
            confidence=0.7,
            factors={'engagement': 0.5},
            recommendations=['Study more']
        )
        
        with patch.object(service.predictive_engine, 'predict_learning_outcome', return_value=mock_prediction):
            result = await service.get_learning_outcome_prediction(mock_db, "user_1", 1)
            
            assert result == mock_prediction
    
    @pytest.mark.asyncio
    async def test_analyze_cohorts(self, service, mock_db):
        """Test cohort analysis."""
        mock_analysis = CohortAnalysis(
            cohort_name="test_cohort",
            cohort_size=10,
            time_period="2024-01",
            retention_rates={'week_1': 0.8},
            engagement_trends={'month_1': 0.7},
            learning_patterns={'visual': 0.6},
            performance_metrics={'avg_completion': 0.75}
        )
        
        with patch.object(service.cohort_engine, 'analyze_user_cohorts', return_value=[mock_analysis]):
            result = await service.analyze_cohorts(mock_db)
            
            assert len(result) == 1
            assert result[0] == mock_analysis
    
    @pytest.mark.asyncio
    async def test_process_real_time_event(self, service, mock_db):
        """Test real-time event processing."""
        mock_personalization = RealTimePersonalization(
            user_id="user_1",
            session_id="session_1",
            adjustments={'difficulty': 'increase'},
            trigger_events=['fast_progress'],
            confidence=0.8
        )
        
        event_data = {'event_type': 'content_interaction'}
        
        with patch.object(service.realtime_engine, 'monitor_learning_session', return_value=mock_personalization):
            result = await service.process_real_time_event(
                mock_db, "user_1", "session_1", event_data
            )
            
            assert result == mock_personalization
    
    def test_cleanup_session_data(self, service):
        """Test session data cleanup."""
        with patch.object(service.realtime_engine, 'cleanup_old_sessions') as mock_cleanup:
            service.cleanup_session_data()
            
            mock_cleanup.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])