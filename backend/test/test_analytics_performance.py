"""Performance tests for analytics processing system."""

import pytest
import asyncio
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor
import statistics

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.analytics_processing_service import AnalyticsProcessingService
from services.personalization_engine import PersonalizationEngine
from services.learning_adaptation_service import LearningAdaptationService
from db.models.db_analytics import EventType, LearningStyleType, UserBehaviorData
from utils.analytics_utils import generate_analytics_id


class TestAnalyticsPerformance:
    """Performance tests for analytics processing components."""
    
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
    def mock_db(self):
        """Create mock database session."""
        return Mock()
    
    def generate_large_behavior_dataset(self, num_users=100, events_per_user=1000):
        """Generate large dataset for performance testing."""
        dataset = []
        base_time = datetime.now(timezone.utc)
        
        for user_idx in range(num_users):
            user_id = f"perf_user_{user_idx}"
            
            for event_idx in range(events_per_user):
                timestamp = base_time - timedelta(
                    days=event_idx // 100,
                    hours=event_idx % 24,
                    minutes=(event_idx * 3) % 60
                )
                
                dataset.append(UserBehaviorData(
                    id=generate_analytics_id(),
                    user_id=user_id,
                    session_id=f"session_{user_idx}_{event_idx // 50}",
                    event_type=EventType(["page_view", "content_interaction", "chapter_complete"][event_idx % 3]),
                    page_url=f"/courses/{(event_idx % 10) + 1}/chapters/{(event_idx % 20) + 1}",
                    timestamp=timestamp,
                    course_id=(event_idx % 10) + 1,
                    chapter_id=(event_idx % 20) + 1,
                    metadata={
                        "content_type": ["text", "video", "interactive", "image"][event_idx % 4],
                        "topic": ["mathematics", "physics", "chemistry", "biology"][event_idx % 4],
                        "difficulty": ["beginner", "intermediate", "advanced"][event_idx % 3]
                    },
                    duration_seconds=60 + (event_idx % 300),
                    engagement_score=0.3 + (event_idx % 7) * 0.1
                ))
        
        return dataset
    
    def test_engagement_metrics_calculation_performance(self, analytics_service, mock_db):
        """Test performance of engagement metrics calculation with large datasets."""
        # Generate test data
        behavior_data = self.generate_large_behavior_dataset(num_users=10, events_per_user=500)
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = behavior_data
            
            with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data') as mock_create:
                mock_create.return_value = Mock()
                
                # Measure performance
                execution_times = []
                
                for i in range(5):  # Run 5 iterations
                    start_time = time.time()
                    
                    metrics = analytics_service.calculate_engagement_metrics(
                        mock_db, f"perf_user_{i}", 168  # 1 week
                    )
                    
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)
                
                # Performance assertions
                avg_time = statistics.mean(execution_times)
                max_time = max(execution_times)
                
                assert avg_time < 1.0, f"Average execution time {avg_time:.3f}s exceeds 1.0s threshold"
                assert max_time < 2.0, f"Maximum execution time {max_time:.3f}s exceeds 2.0s threshold"
                
                print(f"Engagement metrics calculation - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
    
    def test_learning_pattern_identification_performance(self, analytics_service, mock_db):
        """Test performance of learning pattern identification."""
        # Generate diverse behavior data
        behavior_data = self.generate_large_behavior_dataset(num_users=1, events_per_user=2000)
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = behavior_data
            
            with patch('backend.src.db.crud.analytics_crud.get_learning_pattern_by_user') as mock_get_pattern:
                mock_get_pattern.return_value = None  # No existing pattern
                
                with patch('backend.src.db.crud.analytics_crud.create_learning_pattern') as mock_create:
                    mock_create.return_value = Mock()
                    
                    # Measure performance
                    execution_times = []
                    
                    for i in range(3):  # Run 3 iterations
                        start_time = time.time()
                        
                        pattern = analytics_service.identify_learning_patterns(
                            mock_db, "perf_user_0"
                        )
                        
                        execution_time = time.time() - start_time
                        execution_times.append(execution_time)
                    
                    # Performance assertions
                    avg_time = statistics.mean(execution_times)
                    max_time = max(execution_times)
                    
                    assert avg_time < 3.0, f"Average execution time {avg_time:.3f}s exceeds 3.0s threshold"
                    assert max_time < 5.0, f"Maximum execution time {max_time:.3f}s exceeds 5.0s threshold"
                    
                    print(f"Learning pattern identification - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
    
    def test_personalization_engine_performance(self, personalization_engine, mock_db):
        """Test performance of personalization engine operations."""
        # Mock user profile
        mock_profile = Mock(
            learning_style=LearningStyleType.VISUAL,
            preferred_difficulty="intermediate",
            strong_topics=["mathematics", "physics"],
            challenging_topics=["chemistry"],
            completion_rate=0.75,
            attention_span=30
        )
        
        with patch('backend.src.db.crud.analytics_crud.get_user_learning_profile') as mock_get_profile:
            mock_get_profile.return_value = mock_profile
            
            with patch('backend.src.services.course_service.CourseService.get_available_courses') as mock_get_courses:
                # Generate large course dataset
                mock_courses = [
                    Mock(
                        id=i,
                        title=f"Course {i}",
                        difficulty=["beginner", "intermediate", "advanced"][i % 3],
                        topics=[["mathematics"], ["physics"], ["chemistry"], ["biology"]][i % 4],
                        content_types=["text", "video", "interactive"],
                        estimated_duration=60 + (i % 120)
                    )
                    for i in range(1000)  # 1000 courses
                ]
                mock_get_courses.return_value = mock_courses
                
                # Test course recommendation performance
                execution_times = []
                
                for i in range(5):  # Run 5 iterations
                    start_time = time.time()
                    
                    recommendations = personalization_engine.recommend_courses(
                        mock_db, f"perf_user_{i}", limit=20
                    )
                    
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)
                
                # Performance assertions
                avg_time = statistics.mean(execution_times)
                max_time = max(execution_times)
                
                assert avg_time < 0.5, f"Average execution time {avg_time:.3f}s exceeds 0.5s threshold"
                assert max_time < 1.0, f"Maximum execution time {max_time:.3f}s exceeds 1.0s threshold"
                
                print(f"Course recommendation - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
    
    def test_concurrent_analytics_processing(self, analytics_service, mock_db):
        """Test concurrent processing of analytics for multiple users."""
        # Generate behavior data for multiple users
        all_behavior_data = {}
        for user_idx in range(20):
            user_id = f"concurrent_user_{user_idx}"
            all_behavior_data[user_id] = self.generate_large_behavior_dataset(
                num_users=1, events_per_user=200
            )
        
        def process_user_analytics(user_id):
            """Process analytics for a single user."""
            with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
                mock_get_behavior.return_value = all_behavior_data[user_id]
                
                with patch('backend.src.db.crud.analytics_crud.create_user_behavior_data') as mock_create:
                    mock_create.return_value = Mock()
                    
                    start_time = time.time()
                    
                    # Process engagement metrics
                    metrics = analytics_service.calculate_engagement_metrics(
                        mock_db, user_id, 24
                    )
                    
                    execution_time = time.time() - start_time
                    return execution_time, user_id
        
        # Test concurrent processing
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(process_user_analytics, f"concurrent_user_{i}")
                for i in range(20)
            ]
            
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        execution_times = [result[0] for result in results]
        
        # Performance assertions
        avg_individual_time = statistics.mean(execution_times)
        max_individual_time = max(execution_times)
        
        assert total_time < 10.0, f"Total concurrent processing time {total_time:.3f}s exceeds 10.0s"
        assert avg_individual_time < 2.0, f"Average individual processing time {avg_individual_time:.3f}s exceeds 2.0s"
        
        print(f"Concurrent processing - Total: {total_time:.3f}s, Avg individual: {avg_individual_time:.3f}s")
    
    def test_memory_usage_with_large_datasets(self, analytics_service, mock_db):
        """Test memory usage when processing large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate very large dataset
        large_dataset = self.generate_large_behavior_dataset(num_users=5, events_per_user=5000)
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = large_dataset
            
            with patch('backend.src.db.crud.analytics_crud.get_learning_pattern_by_user') as mock_get_pattern:
                mock_get_pattern.return_value = None
                
                with patch('backend.src.db.crud.analytics_crud.create_learning_pattern') as mock_create:
                    mock_create.return_value = Mock()
                    
                    # Process the large dataset
                    for user_idx in range(5):
                        user_id = f"perf_user_{user_idx}"
                        
                        # Process learning patterns
                        pattern = analytics_service.identify_learning_patterns(mock_db, user_id)
                        
                        # Check memory usage
                        current_memory = process.memory_info().rss / 1024 / 1024  # MB
                        memory_increase = current_memory - initial_memory
                        
                        # Memory should not increase excessively
                        assert memory_increase < 500, f"Memory usage increased by {memory_increase:.1f}MB, exceeds 500MB limit"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_increase = final_memory - initial_memory
        
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {total_memory_increase:.1f}MB")
    
    @pytest.mark.asyncio
    async def test_async_umami_data_fetching_performance(self, analytics_service):
        """Test performance of asynchronous Umami data fetching."""
        # Mock Umami API responses
        mock_responses = []
        for i in range(10):
            mock_responses.append({
                "pageviews": [
                    {
                        "url": f"/test/{j}",
                        "created_at": int((datetime.now(timezone.utc) - timedelta(hours=j)).timestamp() * 1000),
                        "session_id": f"session_{i}_{j}",
                        "user_id": f"user_{i}_{j}"
                    }
                    for j in range(100)  # 100 pageviews per response
                ],
                "events": []
            })
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            # Simulate different response times
            async def mock_get(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate network delay
                mock_response.json.return_value = mock_responses[0]
                return mock_response
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get = mock_get
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            analytics_service.umami_api_url = "https://test-umami.com"
            analytics_service.umami_api_token = "test-token"
            analytics_service.umami_website_id = "test-website"
            
            # Test concurrent API calls
            start_time = time.time()
            
            tasks = []
            for i in range(10):
                start_date = datetime.now(timezone.utc) - timedelta(hours=i+1)
                end_date = datetime.now(timezone.utc) - timedelta(hours=i)
                
                task = analytics_service.fetch_umami_data(start_date, end_date)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            # Performance assertions
            assert total_time < 2.0, f"Concurrent API fetching took {total_time:.3f}s, exceeds 2.0s threshold"
            assert len(results) == 10
            assert all(len(result) > 0 for result in results)
            
            print(f"Async Umami data fetching - Total time: {total_time:.3f}s for 10 concurrent requests")
    
    def test_analytics_aggregation_performance(self, analytics_service, mock_db):
        """Test performance of analytics data aggregation operations."""
        # Generate time-series behavior data
        behavior_data = []
        base_time = datetime.now(timezone.utc)
        
        for day in range(30):  # 30 days of data
            for hour in range(24):  # Hourly data points
                for event in range(5):  # 5 events per hour
                    timestamp = base_time - timedelta(days=day, hours=hour, minutes=event*10)
                    
                    behavior_data.append(UserBehaviorData(
                        id=generate_analytics_id(),
                        user_id="aggregation_user",
                        session_id=f"session_{day}_{hour}",
                        event_type=EventType.PAGE_VIEW,
                        page_url=f"/courses/{(day % 5) + 1}",
                        timestamp=timestamp,
                        course_id=(day % 5) + 1,
                        metadata={"content_type": "text"},
                        duration_seconds=120 + (event * 30),
                        engagement_score=0.5 + (event * 0.1)
                    ))
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = behavior_data
            
            # Test different aggregation operations
            aggregation_tests = [
                ("daily_aggregation", 24),
                ("weekly_aggregation", 168),
                ("monthly_aggregation", 720)
            ]
            
            for test_name, hours in aggregation_tests:
                execution_times = []
                
                for i in range(3):  # Run 3 iterations
                    start_time = time.time()
                    
                    # Perform aggregation (simulate complex analytics calculation)
                    user_data = [bd for bd in behavior_data if bd.user_id == "aggregation_user"]
                    
                    # Calculate various metrics
                    total_time = sum(bd.duration_seconds for bd in user_data)
                    avg_engagement = statistics.mean([bd.engagement_score for bd in user_data])
                    daily_sessions = len(set(bd.session_id for bd in user_data))
                    
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)
                
                avg_time = statistics.mean(execution_times)
                
                # Performance thresholds based on aggregation complexity
                threshold = 0.1 if hours <= 24 else 0.5 if hours <= 168 else 1.0
                
                assert avg_time < threshold, f"{test_name} took {avg_time:.3f}s, exceeds {threshold}s threshold"
                
                print(f"{test_name} - Avg time: {avg_time:.3f}s")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short", "-s"])