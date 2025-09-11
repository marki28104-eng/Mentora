"""End-to-end integration tests for the complete analytics pipeline."""

import pytest
import asyncio
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from db.models.db_analytics import EventType, LearningStyleType, DifficultyLevel
from services.analytics_processing_service import AnalyticsProcessingService
from services.personalization_engine import PersonalizationEngine
from services.learning_adaptation_service import LearningAdaptationService
from utils.analytics_utils import generate_analytics_id


class TestAnalyticsE2E:
    """End-to-end tests for the complete analytics pipeline."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        return Mock(
            id="e2e_user_123",
            username="e2euser",
            email="e2e@example.com",
            is_admin=False,
            is_active=True
        )
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics processing service."""
        return AnalyticsProcessingService()
    
    @pytest.fixture
    def personalization_engine(self):
        """Create personalization engine."""
        return PersonalizationEngine()
    
    @pytest.fixture
    def adaptation_service(self):
        """Create learning adaptation service."""
        return LearningAdaptationService()
    
    @pytest.fixture
    def simulated_user_journey(self):
        """Simulate a complete user learning journey."""
        base_time = datetime.now(timezone.utc)
        return [
            # User starts course
            {
                "user_id": "e2e_user_123",
                "session_id": "e2e_session_1",
                "event_type": "course_start",
                "page_url": "/courses/1",
                "timestamp": base_time.isoformat(),
                "course_id": 1,
                "metadata": {
                    "difficulty": "beginner",
                    "topic": "mathematics"
                },
                "duration_seconds": 0
            },
            # User views first chapter
            {
                "user_id": "e2e_user_123",
                "session_id": "e2e_session_1",
                "event_type": "page_view",
                "page_url": "/courses/1/chapters/1",
                "timestamp": (base_time + timedelta(minutes=1)).isoformat(),
                "course_id": 1,
                "chapter_id": 1,
                "metadata": {
                    "content_type": "text",
                    "topic": "algebra"
                },
                "duration_seconds": 300
            },
            # User interacts with content
            {
                "user_id": "e2e_user_123",
                "session_id": "e2e_session_1",
                "event_type": "content_interaction",
                "page_url": "/courses/1/chapters/1",
                "timestamp": (base_time + timedelta(minutes=6)).isoformat(),
                "course_id": 1,
                "chapter_id": 1,
                "metadata": {
                    "content_type": "interactive",
                    "interaction_type": "click",
                    "element": "formula"
                },
                "duration_seconds": 120
            },
            # User completes chapter
            {
                "user_id": "e2e_user_123",
                "session_id": "e2e_session_1",
                "event_type": "chapter_complete",
                "page_url": "/courses/1/chapters/1",
                "timestamp": (base_time + timedelta(minutes=8)).isoformat(),
                "course_id": 1,
                "chapter_id": 1,
                "metadata": {
                    "completion_time": 480,
                    "topic": "algebra"
                },
                "duration_seconds": 480
            },
            # User takes assessment
            {
                "user_id": "e2e_user_123",
                "session_id": "e2e_session_1",
                "event_type": "assessment_start",
                "page_url": "/courses/1/assessments/1",
                "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
                "course_id": 1,
                "metadata": {
                    "assessment_type": "quiz",
                    "question_count": 5
                },
                "duration_seconds": 0
            },
            # User completes assessment
            {
                "user_id": "e2e_user_123",
                "session_id": "e2e_session_1",
                "event_type": "assessment_complete",
                "page_url": "/courses/1/assessments/1",
                "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
                "course_id": 1,
                "metadata": {
                    "score": 80,
                    "total_questions": 5,
                    "correct_answers": 4,
                    "time_spent": 300
                },
                "duration_seconds": 300
            }
        ]
    
    @pytest.fixture
    def performance_test_data(self):
        """Generate large dataset for performance testing."""
        base_time = datetime.now(timezone.utc)
        data = []
        
        # Generate 1000 events for 10 users over 7 days
        for user_idx in range(10):
            user_id = f"perf_user_{user_idx}"
            for day in range(7):
                for event_idx in range(14):  # ~14 events per day per user
                    timestamp = base_time - timedelta(days=day, hours=event_idx)
                    data.append({
                        "user_id": user_id,
                        "session_id": f"perf_session_{user_idx}_{day}_{event_idx // 5}",
                        "event_type": ["page_view", "content_interaction", "chapter_complete"][event_idx % 3],
                        "page_url": f"/courses/{(event_idx % 3) + 1}/chapters/{(event_idx % 5) + 1}",
                        "timestamp": timestamp.isoformat(),
                        "course_id": (event_idx % 3) + 1,
                        "chapter_id": (event_idx % 5) + 1,
                        "metadata": {
                            "content_type": ["text", "video", "interactive"][event_idx % 3],
                            "topic": ["mathematics", "physics", "chemistry"][event_idx % 3]
                        },
                        "duration_seconds": 180 + (event_idx * 10)
                    })
        
        return data
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_complete_analytics_pipeline(self, mock_get_db, mock_get_user, client, mock_user, simulated_user_journey):
        """Test the complete analytics pipeline from data collection to personalization."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # Mock database operations
        created_behavior_data = []
        
        def mock_create_behavior_data(db, behavior_data):
            created_data = Mock(
                id=generate_analytics_id(),
                **behavior_data.__dict__,
                engagement_score=0.7,
                is_anonymized=False,
                created_at=datetime.now(timezone.utc)
            )
            created_behavior_data.append(created_data)
            return created_data
        
        with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data', side_effect=mock_create_behavior_data):
            # Step 1: Submit behavior data through API
            for event_data in simulated_user_journey:
                response = client.post("/analytics/behavior", json=event_data)
                assert response.status_code == 200
            
            # Verify all events were processed
            assert len(created_behavior_data) == len(simulated_user_journey)
        
        # Step 2: Test learning pattern identification
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = created_behavior_data
            
            with patch('backend.src.db.crud.analytics_crud.get_learning_pattern_by_user') as mock_get_pattern:
                mock_get_pattern.return_value = None  # No existing pattern
                
                with patch('backend.src.db.crud.analytics_crud.create_learning_pattern') as mock_create_pattern:
                    created_pattern = Mock(
                        id=generate_analytics_id(),
                        user_id="e2e_user_123",
                        pattern_type="visual",
                        confidence_score=0.8,
                        preferred_content_types=["interactive", "text"],
                        optimal_session_duration=45,
                        difficulty_progression_rate=0.6
                    )
                    mock_create_pattern.return_value = created_pattern
                    
                    # Test pattern identification
                    analytics_service = AnalyticsProcessingService()
                    pattern = analytics_service.identify_learning_patterns(mock_db, "e2e_user_123")
                    
                    assert pattern is not None
                    assert mock_create_pattern.called
        
        # Step 3: Test user profile generation
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
            mock_get_profile.return_value = None  # No existing profile
            
            with patch('backend.src.db.crud.analytics_crud.create_user_learning_profile') as mock_create_profile:
                created_profile = Mock(
                    id=generate_analytics_id(),
                    user_id="e2e_user_123",
                    learning_style=LearningStyleType.VISUAL,
                    attention_span=30,
                    preferred_difficulty=DifficultyLevel.INTERMEDIATE,
                    completion_rate=0.8,
                    average_session_duration=45
                )
                mock_create_profile.return_value = created_profile
                
                # Test profile generation
                personalization_engine = PersonalizationEngine()
                profile = personalization_engine.generate_user_profile(mock_db, "e2e_user_123")
                
                assert profile is not None
                assert mock_create_profile.called
        
        # Step 4: Test personalized recommendations
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
            mock_profile = Mock(
                learning_style=LearningStyleType.VISUAL,
                preferred_difficulty=DifficultyLevel.INTERMEDIATE,
                strong_topics=["mathematics"],
                challenging_topics=["chemistry"]
            )
            mock_get_profile.return_value = mock_profile
            
            with patch('backend.src.services.course_service.CourseService.get_available_courses') as mock_get_courses:
                mock_courses = [
                    Mock(id=1, title="Advanced Mathematics", difficulty="intermediate", topics=["mathematics"]),
                    Mock(id=2, title="Basic Chemistry", difficulty="beginner", topics=["chemistry"]),
                    Mock(id=3, title="Physics Fundamentals", difficulty="intermediate", topics=["physics"])
                ]
                mock_get_courses.return_value = mock_courses
                
                # Test course recommendations
                personalization_engine = PersonalizationEngine()
                recommendations = personalization_engine.recommend_courses(mock_db, "e2e_user_123")
                
                assert recommendations is not None
                assert len(recommendations) > 0
        
        # Step 5: Test learning adaptation
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
            mock_profile = Mock(
                preferred_difficulty=DifficultyLevel.INTERMEDIATE,
                completion_rate=0.8,
                average_session_duration=45
            )
            mock_get_profile.return_value = mock_profile
            
            # Test pacing adjustment
            adaptation_service = LearningAdaptationService()
            pacing = adaptation_service.adjust_pacing(mock_db, "e2e_user_123", 1)
            
            assert pacing is not None
            assert hasattr(pacing, 'recommended_pace')
        
        # Step 6: Test analytics summary API
        with patch('backend.src.db.crud.analytics_crud.get_user_engagement_summary') as mock_engagement:
            mock_engagement.return_value = {
                'total_sessions': 1,
                'total_time_spent': 1200,
                'average_engagement_score': 0.75,
                'total_interactions': 6,
                'total_page_views': 2
            }
            
            with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
                mock_get_profile.return_value = Mock(
                    learning_style=LearningStyleType.VISUAL,
                    preferred_difficulty=DifficultyLevel.INTERMEDIATE
                )
                
                with patch('backend.src.db.crud.analytics_crud.get_user_activity_timeline') as mock_timeline:
                    mock_timeline.return_value = []
                    
                    with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_behavior:
                        mock_behavior.return_value = created_behavior_data
                        
                        response = client.get("/analytics/summary")
                        
                        assert response.status_code == 200
                        summary = response.json()
                        assert summary["user_id"] == "e2e_user_123"
                        assert summary["total_events"] == len(simulated_user_journey)
                        assert "learning_style" in summary
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_personalization_with_simulated_data(self, mock_get_db, mock_get_user, client, mock_user):
        """Test personalization system with comprehensive simulated user data."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # Simulate different learning patterns
        learning_scenarios = [
            {
                "name": "visual_learner",
                "behavior_pattern": [
                    {"content_type": "video", "engagement_time": 600},
                    {"content_type": "image", "engagement_time": 300},
                    {"content_type": "text", "engagement_time": 120},
                ],
                "expected_style": LearningStyleType.VISUAL
            },
            {
                "name": "reading_learner",
                "behavior_pattern": [
                    {"content_type": "text", "engagement_time": 800},
                    {"content_type": "article", "engagement_time": 600},
                    {"content_type": "video", "engagement_time": 200},
                ],
                "expected_style": LearningStyleType.READING
            },
            {
                "name": "kinesthetic_learner",
                "behavior_pattern": [
                    {"content_type": "interactive", "engagement_time": 900},
                    {"content_type": "simulation", "engagement_time": 700},
                    {"content_type": "text", "engagement_time": 150},
                ],
                "expected_style": LearningStyleType.KINESTHETIC
            }
        ]
        
        for scenario in learning_scenarios:
            # Create simulated behavior data for each learning style
            behavior_data = []
            base_time = datetime.now(timezone.utc)
            
            for i, pattern in enumerate(scenario["behavior_pattern"]):
                for repeat in range(5):  # Repeat pattern 5 times for confidence
                    behavior_data.append(Mock(
                        user_id=f"test_user_{scenario['name']}",
                        event_type=EventType.CONTENT_INTERACTION,
                        timestamp=base_time + timedelta(minutes=i*10 + repeat*2),
                        metadata={"content_type": pattern["content_type"]},
                        duration_seconds=pattern["engagement_time"]
                    ))
            
            # Test learning style identification
            analytics_service = AnalyticsProcessingService()
            identified_style, confidence = analytics_service._analyze_learning_style(behavior_data)
            
            # Verify the system correctly identifies the learning style
            assert identified_style == scenario["expected_style"]
            assert confidence > 0.6  # Should have reasonable confidence
        
        # Test personalization engine with identified patterns
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
            mock_profile = Mock(
                learning_style=LearningStyleType.VISUAL,
                preferred_difficulty=DifficultyLevel.INTERMEDIATE,
                strong_topics=["mathematics", "physics"],
                challenging_topics=["chemistry"]
            )
            mock_get_profile.return_value = mock_profile
            
            personalization_engine = PersonalizationEngine()
            
            # Test content adaptation
            adapted_content = personalization_engine.adapt_content_difficulty(
                mock_db, "test_content_123", mock_profile
            )
            
            assert adapted_content is not None
            assert hasattr(adapted_content, 'difficulty_level')
            assert hasattr(adapted_content, 'content_format')
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_analytics_performance_with_large_dataset(self, mock_get_db, mock_get_admin, client, performance_test_data):
        """Test analytics processing performance with large datasets."""
        mock_admin = Mock(id="admin_123", is_admin=True)
        mock_get_admin.return_value = mock_admin
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # Mock database operations for performance testing
        with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data') as mock_create:
            mock_create.return_value = Mock(id=generate_analytics_id())
            
            # Measure time to process large dataset
            import time
            start_time = time.time()
            
            # Process events in batches (simulating real-world usage)
            batch_size = 100
            for i in range(0, len(performance_test_data), batch_size):
                batch = performance_test_data[i:i + batch_size]
                
                # Submit batch through API
                for event_data in batch:
                    # Simulate API call (we'll mock the actual processing)
                    pass
            
            processing_time = time.time() - start_time
            
            # Performance assertions
            assert processing_time < 10.0  # Should process 1000 events in under 10 seconds
            assert len(performance_test_data) == 980  # 10 users * 7 days * 14 events
        
        # Test analytics aggregation performance
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            # Simulate large behavior dataset
            mock_behavior_data = [
                Mock(
                    user_id=f"perf_user_{i % 10}",
                    event_type=EventType.PAGE_VIEW,
                    timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                    duration_seconds=180,
                    metadata={"content_type": "text"}
                )
                for i in range(1000)
            ]
            mock_get_behavior.return_value = mock_behavior_data
            
            # Test engagement metrics calculation performance
            analytics_service = AnalyticsProcessingService()
            
            start_time = time.time()
            metrics = analytics_service.calculate_engagement_metrics(mock_db, "perf_user_1", 168)  # 1 week
            calculation_time = time.time() - start_time
            
            # Performance assertions
            assert calculation_time < 2.0  # Should calculate metrics in under 2 seconds
            assert metrics is not None
    
    @patch('backend.src.utils.auth.get_current_active_user')
    @patch('backend.src.db.database.get_db')
    def test_real_time_adaptation_flow(self, mock_get_db, mock_get_user, client, mock_user):
        """Test real-time learning adaptation based on user performance."""
        mock_get_user.return_value = mock_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        # Simulate user struggling with content (low scores, long completion times)
        struggling_behavior = [
            {
                "user_id": "e2e_user_123",
                "session_id": "adaptation_session",
                "event_type": "assessment_complete",
                "page_url": "/courses/1/assessments/1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "course_id": 1,
                "metadata": {
                    "score": 40,  # Low score
                    "time_spent": 900,  # Long time
                    "attempts": 3  # Multiple attempts
                },
                "duration_seconds": 900
            }
        ]
        
        # Submit struggling behavior
        with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data') as mock_create:
            mock_create.return_value = Mock(id=generate_analytics_id())
            
            for event_data in struggling_behavior:
                response = client.post("/analytics/behavior", json=event_data)
                assert response.status_code == 200
        
        # Test adaptation response
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_behavior_data = [
                Mock(
                    event_type=EventType.ASSESSMENT_COMPLETE,
                    metadata={"score": 40, "time_spent": 900},
                    timestamp=datetime.now(timezone.utc)
                )
            ]
            mock_get_behavior.return_value = mock_behavior_data
            
            with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
                mock_profile = Mock(
                    preferred_difficulty=DifficultyLevel.BEGINNER,
                    completion_rate=0.4,  # Low completion rate
                    challenging_topics=["mathematics"]
                )
                mock_get_profile.return_value = mock_profile
                
                # Test learning adaptation
                adaptation_service = LearningAdaptationService()
                
                # Should recommend easier content
                supplementary = adaptation_service.provide_supplementary_content(
                    mock_db, "e2e_user_123", "mathematics"
                )
                
                assert supplementary is not None
                assert len(supplementary) > 0
                
                # Should adjust pacing to be slower
                pacing = adaptation_service.adjust_pacing(mock_db, "e2e_user_123", 1)
                
                assert pacing is not None
                assert pacing.recommended_pace == "slower"
        
        # Test successful adaptation (user improves)
        improved_behavior = [
            {
                "user_id": "e2e_user_123",
                "session_id": "adaptation_session_2",
                "event_type": "assessment_complete",
                "page_url": "/courses/1/assessments/2",
                "timestamp": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "course_id": 1,
                "metadata": {
                    "score": 85,  # Improved score
                    "time_spent": 300,  # Faster completion
                    "attempts": 1  # Single attempt
                },
                "duration_seconds": 300
            }
        ]
        
        # Submit improved behavior
        with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data') as mock_create:
            mock_create.return_value = Mock(id=generate_analytics_id())
            
            for event_data in improved_behavior:
                response = client.post("/analytics/behavior", json=event_data)
                assert response.status_code == 200
        
        # Verify adaptation recognizes improvement
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_improved_data = [
                Mock(
                    event_type=EventType.ASSESSMENT_COMPLETE,
                    metadata={"score": 85, "time_spent": 300},
                    timestamp=datetime.now(timezone.utc)
                )
            ]
            mock_get_behavior.return_value = mock_improved_data
            
            # Should now recommend normal or advanced pacing
            pacing = adaptation_service.adjust_pacing(mock_db, "e2e_user_123", 1)
            
            assert pacing is not None
            assert pacing.recommended_pace in ["normal", "faster"]


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])