"""Tests for monitoring API endpoints."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from services.analytics_monitoring_service import HealthStatus, HealthCheckResult


class TestMonitoringAPI:
    """Test cases for monitoring API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_admin_user(self):
        """Create mock admin user."""
        return Mock(
            id="admin_123",
            username="admin",
            email="admin@example.com",
            is_admin=True,
            is_active=True
        )
    
    @pytest.fixture
    def mock_regular_user(self):
        """Create mock regular user."""
        return Mock(
            id="user_123",
            username="user",
            email="user@example.com",
            is_admin=False,
            is_active=True
        )
    
    @pytest.fixture
    def mock_health_status(self):
        """Create mock comprehensive health status."""
        return {
            "overall_status": "healthy",
            "services": {
                "umami_integration": {
                    "status": "healthy",
                    "message": "Umami integration healthy",
                    "response_time_ms": 150.0,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "details": {"website_found": True}
                },
                "analytics_processing": {
                    "status": "healthy",
                    "message": "Analytics processing healthy",
                    "response_time_ms": 200.0,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "details": {"behavior_data_count": 100}
                }
            },
            "metrics": {
                "total_events_24h": 1000,
                "unique_users_24h": 50,
                "error_rate": 0.01
            },
            "alerts": [],
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_get_analytics_health_status_success(self, mock_get_db, mock_get_admin, client, mock_admin_user, mock_health_status):
        """Test successful analytics health status retrieval."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.return_value = mock_health_status
            
            response = client.get("/monitoring/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["overall_status"] == "healthy"
            assert len(data["data"]["services"]) == 2
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    def test_get_analytics_health_status_admin_required(self, mock_get_admin, client, mock_regular_user):
        """Test that health status endpoint requires admin access."""
        # This would typically raise an HTTPException for non-admin users
        # The exact implementation depends on your auth system
        mock_get_admin.side_effect = Exception("Admin required")
        
        response = client.get("/monitoring/health")
        
        # Should return error due to admin requirement
        assert response.status_code in [401, 403, 500]
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    def test_get_umami_health_status_success(self, mock_get_admin, client, mock_admin_user):
        """Test successful Umami health status retrieval."""
        mock_get_admin.return_value = mock_admin_user
        
        mock_health_result = HealthCheckResult(
            service="umami_integration",
            status=HealthStatus.HEALTHY,
            message="Umami integration healthy",
            response_time_ms=150.0,
            timestamp=datetime.now(timezone.utc),
            details={"website_found": True}
        )
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.check_umami_integration_health') as mock_check:
            mock_check.return_value = mock_health_result
            
            response = client.get("/monitoring/health/umami")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["service"] == "umami_integration"
            assert data["data"]["status"] == "healthy"
            assert data["data"]["details"]["website_found"] is True
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_get_analytics_processing_health_success(self, mock_get_db, mock_get_admin, client, mock_admin_user):
        """Test successful analytics processing health retrieval."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        mock_health_result = HealthCheckResult(
            service="analytics_processing",
            status=HealthStatus.HEALTHY,
            message="Analytics processing healthy",
            response_time_ms=200.0,
            timestamp=datetime.now(timezone.utc),
            details={"behavior_data_count": 100}
        )
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.check_analytics_processing_health') as mock_check:
            mock_check.return_value = mock_health_result
            
            response = client.get("/monitoring/health/analytics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["service"] == "analytics_processing"
            assert data["data"]["status"] == "healthy"
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_get_personalization_health_success(self, mock_get_db, mock_get_admin, client, mock_admin_user):
        """Test successful personalization engine health retrieval."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        mock_health_result = HealthCheckResult(
            service="personalization_engine",
            status=HealthStatus.HEALTHY,
            message="Personalization engine healthy",
            response_time_ms=180.0,
            timestamp=datetime.now(timezone.utc),
            details={"recommendations_count": 5}
        )
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.check_personalization_engine_health') as mock_check:
            mock_check.return_value = mock_health_result
            
            response = client.get("/monitoring/health/personalization")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["service"] == "personalization_engine"
            assert data["data"]["status"] == "healthy"
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_get_database_health_success(self, mock_get_db, mock_get_admin, client, mock_admin_user):
        """Test successful database health retrieval."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        mock_health_result = HealthCheckResult(
            service="database",
            status=HealthStatus.HEALTHY,
            message="Database connectivity healthy",
            response_time_ms=50.0,
            timestamp=datetime.now(timezone.utc),
            details={"connection_test": True}
        )
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.check_database_health') as mock_check:
            mock_check.return_value = mock_health_result
            
            response = client.get("/monitoring/health/database")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["service"] == "database"
            assert data["data"]["status"] == "healthy"
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_get_analytics_metrics_success(self, mock_get_db, mock_get_admin, client, mock_admin_user):
        """Test successful analytics metrics retrieval."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        mock_metrics = {
            "total_events_24h": 1000,
            "unique_users_24h": 50,
            "unique_sessions_24h": 75,
            "average_engagement_score": 0.75,
            "events_per_hour": 41.67,
            "error_rate": 0.01,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.get_analytics_metrics') as mock_get_metrics:
            mock_get_metrics.return_value = mock_metrics
            
            response = client.get("/monitoring/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["total_events_24h"] == 1000
            assert data["data"]["unique_users_24h"] == 50
            assert data["data"]["error_rate"] == 0.01
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    @patch('backend.src.db.database.get_db')
    def test_get_active_alerts_success(self, mock_get_db, mock_get_admin, client, mock_admin_user):
        """Test successful active alerts retrieval."""
        mock_get_admin.return_value = mock_admin_user
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        
        mock_health_status = {
            "alerts": [
                {
                    "name": "umami_response_time",
                    "message": "Alert: umami_response_time threshold exceeded",
                    "threshold": 5000.0,
                    "current_value": 6000.0,
                    "severity": "warning",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ],
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.return_value = mock_health_status
            
            response = client.get("/monitoring/alerts")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["alert_count"] == 1
            assert len(data["data"]["active_alerts"]) == 1
            assert data["data"]["active_alerts"][0]["name"] == "umami_response_time"
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    def test_test_alert_system_success(self, mock_get_admin, client, mock_admin_user):
        """Test successful alert system testing."""
        mock_get_admin.return_value = mock_admin_user
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.send_alert_notification') as mock_send_alert:
            mock_send_alert.return_value = True
            
            response = client.post("/monitoring/alerts/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["message"] == "Test alert sent successfully"
            assert "data" in data
    
    def test_get_monitoring_status_public_access(self, client):
        """Test public monitoring status endpoint."""
        mock_health_status = {
            "overall_status": "healthy",
            "services": {
                "umami_integration": {"status": "healthy"},
                "analytics_processing": {"status": "healthy"}
            },
            "alerts": [],
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.return_value = mock_health_status
            
            response = client.get("/monitoring/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["system_status"] == "healthy"
            assert data["data"]["services_count"] == 2
            assert data["data"]["alerts_count"] == 0
    
    def test_get_monitoring_status_error_handling(self, client):
        """Test monitoring status endpoint error handling."""
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.side_effect = Exception("Monitoring system error")
            
            response = client.get("/monitoring/status")
            
            assert response.status_code == 200  # Should not fail, just return error status
            data = response.json()
            assert data["status"] == "error"
            assert data["data"]["system_status"] == "unknown"
            assert "error" in data["data"]
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    def test_get_health_summary_success(self, mock_get_admin, client, mock_admin_user, mock_health_status):
        """Test successful health summary retrieval."""
        mock_get_admin.return_value = mock_admin_user
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.return_value = mock_health_status
            
            response = client.get("/monitoring/health/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["overall_status"] == "healthy"
            assert len(data["data"]["services"]) == 2
            assert data["data"]["total_alerts"] == 0
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    def test_health_check_with_critical_status(self, mock_get_admin, client, mock_admin_user):
        """Test health check when system is in critical status."""
        mock_get_admin.return_value = mock_admin_user
        
        critical_health_status = {
            "overall_status": "critical",
            "services": {
                "umami_integration": {
                    "status": "critical",
                    "message": "Umami API unavailable",
                    "response_time_ms": 0.0,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "details": {"error": "Connection timeout"}
                }
            },
            "metrics": {"total_events_24h": 0},
            "alerts": [
                {
                    "name": "umami_api_availability",
                    "message": "Umami API is unavailable",
                    "severity": "critical"
                }
            ],
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.return_value = critical_health_status
            
            response = client.get("/monitoring/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["overall_status"] == "critical"
            assert len(data["data"]["alerts"]) == 1
    
    @patch('backend.src.utils.auth.get_current_admin_user')
    def test_monitoring_endpoint_error_handling(self, mock_get_admin, client, mock_admin_user):
        """Test monitoring endpoint error handling."""
        mock_get_admin.return_value = mock_admin_user
        
        with patch('backend.src.services.analytics_monitoring_service.AnalyticsMonitoringService.run_comprehensive_health_check') as mock_health_check:
            mock_health_check.side_effect = Exception("Service unavailable")
            
            response = client.get("/monitoring/health")
            
            assert response.status_code == 500
            data = response.json()
            assert "Health check failed" in data["detail"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])