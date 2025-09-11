"""Tests for analytics monitoring service."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.analytics_monitoring_service import (
    AnalyticsMonitoringService,
    HealthStatus,
    HealthCheckResult,
    AlertConfig
)


class TestAnalyticsMonitoringService:
    """Test cases for AnalyticsMonitoringService."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create monitoring service instance."""
        return AnalyticsMonitoringService()
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock(spec=Session)
    
    @pytest.mark.asyncio
    async def test_umami_health_check_success(self, monitoring_service):
        """Test successful Umami health check."""
        # Mock Umami configuration
        monitoring_service.analytics_service.umami_api_url = "https://test-umami.com"
        monitoring_service.analytics_service.umami_api_token = "test-token"
        monitoring_service.analytics_service.umami_website_id = "test-website"
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"id": "test-website", "name": "Test Website"}
                ]
            }
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await monitoring_service.check_umami_integration_health()
            
            assert result.service == "umami_integration"
            assert result.status == HealthStatus.HEALTHY
            assert result.message == "Umami integration healthy"
            assert result.response_time_ms > 0
            assert result.details["website_found"] is True
    
    @pytest.mark.asyncio
    async def test_umami_health_check_missing_config(self, monitoring_service):
        """Test Umami health check with missing configuration."""
        # Clear Umami configuration
        monitoring_service.analytics_service.umami_api_url = None
        monitoring_service.analytics_service.umami_api_token = None
        
        result = await monitoring_service.check_umami_integration_health()
        
        assert result.service == "umami_integration"
        assert result.status == HealthStatus.WARNING
        assert result.message == "Umami configuration missing"
        assert result.details["configured"] is False
    
    @pytest.mark.asyncio
    async def test_umami_health_check_api_error(self, monitoring_service):
        """Test Umami health check with API error."""
        # Mock Umami configuration
        monitoring_service.analytics_service.umami_api_url = "https://test-umami.com"
        monitoring_service.analytics_service.umami_api_token = "test-token"
        
        with patch('httpx.AsyncClient') as mock_client:
            # Mock error response
            mock_response = Mock()
            mock_response.status_code = 401
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await monitoring_service.check_umami_integration_health()
            
            assert result.service == "umami_integration"
            assert result.status == HealthStatus.CRITICAL
            assert "401" in result.message
    
    @pytest.mark.asyncio
    async def test_analytics_processing_health_check(self, monitoring_service, mock_db):
        """Test analytics processing health check."""
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = []
            
            with patch.object(monitoring_service.analytics_service, 'calculate_engagement_metrics') as mock_calc:
                mock_calc.return_value = Mock()
                
                result = await monitoring_service.check_analytics_processing_health(mock_db)
                
                assert result.service == "analytics_processing"
                assert result.status == HealthStatus.HEALTHY
                assert result.message == "Analytics processing healthy"
                assert result.response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_personalization_engine_health_check(self, monitoring_service, mock_db):
        """Test personalization engine health check."""
        with patch.object(monitoring_service.personalization_engine, 'generate_user_profile') as mock_profile:
            mock_profile.return_value = Mock()
            
            with patch.object(monitoring_service.personalization_engine, 'recommend_courses') as mock_recommend:
                mock_recommend.return_value = [Mock(), Mock()]
                
                result = await monitoring_service.check_personalization_engine_health(mock_db)
                
                assert result.service == "personalization_engine"
                assert result.status == HealthStatus.HEALTHY
                assert result.message == "Personalization engine healthy"
                assert result.details["recommendations_count"] == 2
    
    @pytest.mark.asyncio
    async def test_database_health_check(self, monitoring_service, mock_db):
        """Test database health check."""
        # Mock successful database operations
        mock_db.execute.return_value.fetchone.return_value = (1,)
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = []
            
            result = await monitoring_service.check_database_health(mock_db)
            
            assert result.service == "database"
            assert result.status == HealthStatus.HEALTHY
            assert result.message == "Database connectivity healthy"
            assert result.details["connection_test"] is True
    
    @pytest.mark.asyncio
    async def test_get_analytics_metrics(self, monitoring_service, mock_db):
        """Test analytics metrics collection."""
        # Mock behavior data
        mock_behavior_data = [
            Mock(
                user_id=f"user_{i}",
                session_id=f"session_{i // 2}",
                engagement_score=0.5 + (i * 0.1)
            )
            for i in range(10)
        ]
        
        with patch('backend.src.db.crud.analytics_crud.get_user_behavior_data') as mock_get_behavior:
            mock_get_behavior.return_value = mock_behavior_data
            
            metrics = await monitoring_service.get_analytics_metrics(mock_db)
            
            assert "total_events_24h" in metrics
            assert "unique_users_24h" in metrics
            assert "unique_sessions_24h" in metrics
            assert "average_engagement_score" in metrics
            assert metrics["total_events_24h"] == 10
            assert metrics["unique_users_24h"] == 10
            assert metrics["unique_sessions_24h"] == 5
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self, monitoring_service):
        """Test comprehensive health check."""
        with patch.object(monitoring_service, 'check_umami_integration_health') as mock_umami:
            mock_umami.return_value = HealthCheckResult(
                service="umami_integration",
                status=HealthStatus.HEALTHY,
                message="Healthy",
                response_time_ms=100.0,
                timestamp=datetime.now(timezone.utc)
            )
            
            with patch.object(monitoring_service, 'check_analytics_processing_health') as mock_analytics:
                mock_analytics.return_value = HealthCheckResult(
                    service="analytics_processing",
                    status=HealthStatus.HEALTHY,
                    message="Healthy",
                    response_time_ms=200.0,
                    timestamp=datetime.now(timezone.utc)
                )
                
                with patch.object(monitoring_service, 'check_personalization_engine_health') as mock_personalization:
                    mock_personalization.return_value = HealthCheckResult(
                        service="personalization_engine",
                        status=HealthStatus.HEALTHY,
                        message="Healthy",
                        response_time_ms=150.0,
                        timestamp=datetime.now(timezone.utc)
                    )
                    
                    with patch.object(monitoring_service, 'check_database_health') as mock_database:
                        mock_database.return_value = HealthCheckResult(
                            service="database",
                            status=HealthStatus.HEALTHY,
                            message="Healthy",
                            response_time_ms=50.0,
                            timestamp=datetime.now(timezone.utc)
                        )
                        
                        with patch.object(monitoring_service, 'get_analytics_metrics') as mock_metrics:
                            mock_metrics.return_value = {
                                "total_events_24h": 100,
                                "error_rate": 0.01
                            }
                            
                            result = await monitoring_service.run_comprehensive_health_check()
                            
                            assert result["overall_status"] == "healthy"
                            assert len(result["services"]) == 4
                            assert "metrics" in result
                            assert "alerts" in result
    
    def test_alert_condition_checking(self, monitoring_service):
        """Test alert condition checking."""
        # Mock health results with high response time
        health_results = {
            "umami_integration": {
                "response_time_ms": 6000.0  # Exceeds 5000ms threshold
            },
            "analytics_processing": {
                "response_time_ms": 1000.0  # Within threshold
            }
        }
        
        metrics = {
            "error_rate": 0.02  # Within threshold
        }
        
        alerts = monitoring_service._check_alert_conditions(health_results, metrics)
        
        # Should trigger umami response time alert
        assert len(alerts) == 1
        assert alerts[0]["name"] == "umami_response_time"
        assert alerts[0]["current_value"] == 6000.0
    
    def test_compare_value_operations(self, monitoring_service):
        """Test value comparison operations."""
        assert monitoring_service._compare_value(10, 5, "gt") is True
        assert monitoring_service._compare_value(3, 5, "gt") is False
        assert monitoring_service._compare_value(3, 5, "lt") is True
        assert monitoring_service._compare_value(10, 5, "lt") is False
        assert monitoring_service._compare_value(5, 5, "eq") is True
        assert monitoring_service._compare_value(3, 5, "eq") is False
    
    @pytest.mark.asyncio
    async def test_alert_cooldown_mechanism(self, monitoring_service):
        """Test alert cooldown mechanism."""
        # Set up alert config with short cooldown for testing
        monitoring_service.alert_configs = [
            AlertConfig(
                name="test_alert",
                threshold=100.0,
                comparison="gt",
                cooldown_minutes=1  # 1 minute cooldown
            )
        ]
        
        # Trigger first alert
        health_results = {"test_service": {"response_time_ms": 150.0}}
        metrics = {}
        
        alerts1 = monitoring_service._check_alert_conditions(health_results, metrics)
        assert len(alerts1) == 0  # No matching service for test_alert
        
        # Test with umami alert (which exists in default config)
        health_results = {"umami_integration": {"response_time_ms": 6000.0}}
        alerts2 = monitoring_service._check_alert_conditions(health_results, metrics)
        assert len(alerts2) == 1
        
        # Immediately trigger again - should be blocked by cooldown
        alerts3 = monitoring_service._check_alert_conditions(health_results, metrics)
        assert len(alerts3) == 0  # Blocked by cooldown
    
    @pytest.mark.asyncio
    async def test_send_alert_notification(self, monitoring_service):
        """Test alert notification sending."""
        test_alert = {
            "name": "test_alert",
            "message": "Test alert message",
            "threshold": 100,
            "current_value": 150,
            "severity": "warning"
        }
        
        # Test successful notification
        result = await monitoring_service.send_alert_notification(test_alert)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_with_critical_status(self, monitoring_service):
        """Test health check when services are in critical status."""
        with patch.object(monitoring_service, 'check_umami_integration_health') as mock_umami:
            mock_umami.return_value = HealthCheckResult(
                service="umami_integration",
                status=HealthStatus.CRITICAL,
                message="API unavailable",
                response_time_ms=0.0,
                timestamp=datetime.now(timezone.utc)
            )
            
            with patch.object(monitoring_service, 'check_analytics_processing_health') as mock_analytics:
                mock_analytics.return_value = HealthCheckResult(
                    service="analytics_processing",
                    status=HealthStatus.WARNING,
                    message="Slow response",
                    response_time_ms=3000.0,
                    timestamp=datetime.now(timezone.utc)
                )
                
                with patch.object(monitoring_service, 'check_personalization_engine_health') as mock_personalization:
                    mock_personalization.return_value = HealthCheckResult(
                        service="personalization_engine",
                        status=HealthStatus.HEALTHY,
                        message="Healthy",
                        response_time_ms=150.0,
                        timestamp=datetime.now(timezone.utc)
                    )
                    
                    with patch.object(monitoring_service, 'check_database_health') as mock_database:
                        mock_database.return_value = HealthCheckResult(
                            service="database",
                            status=HealthStatus.HEALTHY,
                            message="Healthy",
                            response_time_ms=50.0,
                            timestamp=datetime.now(timezone.utc)
                        )
                        
                        with patch.object(monitoring_service, 'get_analytics_metrics') as mock_metrics:
                            mock_metrics.return_value = {"total_events_24h": 100}
                            
                            result = await monitoring_service.run_comprehensive_health_check()
                            
                            # Overall status should be critical due to umami critical status
                            assert result["overall_status"] == "critical"
                            assert result["services"]["umami_integration"]["status"] == "critical"
                            assert result["services"]["analytics_processing"]["status"] == "warning"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])