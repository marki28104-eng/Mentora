"""Analytics monitoring and health check service."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import httpx
from sqlalchemy.orm import Session

from db.database import get_db
from db.crud import analytics_crud
from services.analytics_processing_service import AnalyticsProcessingService
from services.personalization_engine import PersonalizationEngine
from config.settings import get_settings

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result data class."""
    service: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class AlertConfig:
    """Alert configuration data class."""
    name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    enabled: bool = True
    cooldown_minutes: int = 15


class AnalyticsMonitoringService:
    """Service for monitoring analytics system health and performance."""
    
    def __init__(self):
        """Initialize monitoring service."""
        self.settings = get_settings()
        self.analytics_service = AnalyticsProcessingService()
        self.personalization_engine = PersonalizationEngine()
        self.alert_configs = self._load_alert_configs()
        self.last_alerts = {}  # Track last alert times for cooldown
    
    def _load_alert_configs(self) -> List[AlertConfig]:
        """Load alert configurations."""
        return [
            AlertConfig(
                name="umami_response_time",
                threshold=5000.0,  # 5 seconds
                comparison="gt"
            ),
            AlertConfig(
                name="analytics_processing_time",
                threshold=10000.0,  # 10 seconds
                comparison="gt"
            ),
            AlertConfig(
                name="personalization_response_time",
                threshold=2000.0,  # 2 seconds
                comparison="gt"
            ),
            AlertConfig(
                name="database_connection_failures",
                threshold=5.0,  # 5 failures
                comparison="gt"
            ),
            AlertConfig(
                name="analytics_data_processing_errors",
                threshold=10.0,  # 10 errors per hour
                comparison="gt"
            ),
            AlertConfig(
                name="umami_api_availability",
                threshold=0.95,  # 95% availability
                comparison="lt"
            )
        ]
    
    async def check_umami_integration_health(self) -> HealthCheckResult:
        """Check Umami integration health."""
        start_time = datetime.now()
        
        try:
            if not self.analytics_service.umami_api_url or not self.analytics_service.umami_api_token:
                return HealthCheckResult(
                    service="umami_integration",
                    status=HealthStatus.WARNING,
                    message="Umami configuration missing",
                    response_time_ms=0.0,
                    timestamp=start_time,
                    details={"configured": False}
                )
            
            # Test Umami API connectivity
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.get(
                        f"{self.analytics_service.umami_api_url}/api/websites",
                        headers={"Authorization": f"Bearer {self.analytics_service.umami_api_token}"}
                    )
                    
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    if response.status_code == 200:
                        websites = response.json()
                        website_found = any(
                            w.get("id") == self.analytics_service.umami_website_id 
                            for w in websites.get("data", [])
                        )
                        
                        if website_found:
                            status = HealthStatus.HEALTHY
                            message = "Umami integration healthy"
                        else:
                            status = HealthStatus.WARNING
                            message = "Website ID not found in Umami"
                        
                        return HealthCheckResult(
                            service="umami_integration",
                            status=status,
                            message=message,
                            response_time_ms=response_time,
                            timestamp=start_time,
                            details={
                                "status_code": response.status_code,
                                "website_count": len(websites.get("data", [])),
                                "website_found": website_found
                            }
                        )
                    else:
                        return HealthCheckResult(
                            service="umami_integration",
                            status=HealthStatus.CRITICAL,
                            message=f"Umami API returned status {response.status_code}",
                            response_time_ms=response_time,
                            timestamp=start_time,
                            details={"status_code": response.status_code}
                        )
                
                except httpx.TimeoutException:
                    return HealthCheckResult(
                        service="umami_integration",
                        status=HealthStatus.CRITICAL,
                        message="Umami API timeout",
                        response_time_ms=10000.0,
                        timestamp=start_time,
                        details={"error": "timeout"}
                    )
        
        except Exception as e:
            logger.error(f"Umami health check failed: {str(e)}")
            return HealthCheckResult(
                service="umami_integration",
                status=HealthStatus.CRITICAL,
                message=f"Umami health check error: {str(e)}",
                response_time_ms=0.0,
                timestamp=start_time,
                details={"error": str(e)}
            )
    
    async def check_analytics_processing_health(self, db: Session) -> HealthCheckResult:
        """Check analytics processing service health."""
        start_time = datetime.now()
        
        try:
            # Test analytics processing with sample data
            test_user_id = "health_check_user"
            
            # Check if we can fetch user behavior data
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=test_user_id,
                limit=10
            )
            
            # Test engagement metrics calculation
            metrics = self.analytics_service.calculate_engagement_metrics(
                db=db,
                user_id=test_user_id,
                hours=24
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                service="analytics_processing",
                status=HealthStatus.HEALTHY,
                message="Analytics processing healthy",
                response_time_ms=response_time,
                timestamp=start_time,
                details={
                    "behavior_data_count": len(behavior_data),
                    "metrics_calculated": metrics is not None
                }
            )
        
        except Exception as e:
            logger.error(f"Analytics processing health check failed: {str(e)}")
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                service="analytics_processing",
                status=HealthStatus.CRITICAL,
                message=f"Analytics processing error: {str(e)}",
                response_time_ms=response_time,
                timestamp=start_time,
                details={"error": str(e)}
            )
    
    async def check_personalization_engine_health(self, db: Session) -> HealthCheckResult:
        """Check personalization engine health."""
        start_time = datetime.now()
        
        try:
            # Test personalization engine with sample data
            test_user_id = "health_check_user"
            
            # Test user profile generation
            profile = self.personalization_engine.generate_user_profile(
                db=db,
                user_id=test_user_id
            )
            
            # Test course recommendations
            recommendations = self.personalization_engine.recommend_courses(
                db=db,
                user_id=test_user_id,
                limit=5
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                service="personalization_engine",
                status=HealthStatus.HEALTHY,
                message="Personalization engine healthy",
                response_time_ms=response_time,
                timestamp=start_time,
                details={
                    "profile_generated": profile is not None,
                    "recommendations_count": len(recommendations) if recommendations else 0
                }
            )
        
        except Exception as e:
            logger.error(f"Personalization engine health check failed: {str(e)}")
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                service="personalization_engine",
                status=HealthStatus.CRITICAL,
                message=f"Personalization engine error: {str(e)}",
                response_time_ms=response_time,
                timestamp=start_time,
                details={"error": str(e)}
            )
    
    async def check_database_health(self, db: Session) -> HealthCheckResult:
        """Check database connectivity and performance."""
        start_time = datetime.now()
        
        try:
            # Test basic database connectivity
            result = db.execute("SELECT 1").fetchone()
            
            # Test analytics tables accessibility
            recent_behavior = analytics_crud.get_user_behavior_data(
                db=db,
                user_id="test",
                limit=1
            )
            
            # Test write capability (if needed)
            # This would be a lightweight test write/delete operation
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                service="database",
                status=HealthStatus.HEALTHY,
                message="Database connectivity healthy",
                response_time_ms=response_time,
                timestamp=start_time,
                details={
                    "connection_test": result is not None,
                    "analytics_tables_accessible": True
                }
            )
        
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                service="database",
                status=HealthStatus.CRITICAL,
                message=f"Database error: {str(e)}",
                response_time_ms=response_time,
                timestamp=start_time,
                details={"error": str(e)}
            )
    
    async def get_analytics_metrics(self, db: Session) -> Dict[str, Any]:
        """Get analytics system performance metrics."""
        try:
            # Get recent analytics activity
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            
            # Count recent behavior data entries
            recent_events = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=None,  # All users
                start_date=start_time,
                end_date=end_time,
                limit=10000
            )
            
            # Calculate processing metrics
            total_events = len(recent_events)
            unique_users = len(set(event.user_id for event in recent_events))
            unique_sessions = len(set(event.session_id for event in recent_events))
            
            # Calculate average engagement score
            engagement_scores = [
                event.engagement_score for event in recent_events 
                if event.engagement_score is not None
            ]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            # Get error rates (this would require error logging)
            error_rate = 0.0  # Placeholder - implement based on error logging system
            
            return {
                "total_events_24h": total_events,
                "unique_users_24h": unique_users,
                "unique_sessions_24h": unique_sessions,
                "average_engagement_score": avg_engagement,
                "events_per_hour": total_events / 24,
                "error_rate": error_rate,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to get analytics metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check of all analytics components."""
        db = next(get_db())
        
        try:
            # Run all health checks concurrently
            health_checks = await asyncio.gather(
                self.check_umami_integration_health(),
                self.check_analytics_processing_health(db),
                self.check_personalization_engine_health(db),
                self.check_database_health(db),
                return_exceptions=True
            )
            
            # Process results
            results = {}
            overall_status = HealthStatus.HEALTHY
            
            for check in health_checks:
                if isinstance(check, Exception):
                    logger.error(f"Health check failed with exception: {str(check)}")
                    continue
                
                results[check.service] = {
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "timestamp": check.timestamp.isoformat(),
                    "details": check.details
                }
                
                # Determine overall status
                if check.status == HealthStatus.CRITICAL:
                    overall_status = HealthStatus.CRITICAL
                elif check.status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                    overall_status = HealthStatus.WARNING
            
            # Get performance metrics
            metrics = await self.get_analytics_metrics(db)
            
            # Check for alert conditions
            alerts = self._check_alert_conditions(results, metrics)
            
            return {
                "overall_status": overall_status.value,
                "services": results,
                "metrics": metrics,
                "alerts": alerts,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        finally:
            db.close()
    
    def _check_alert_conditions(self, health_results: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions based on health results and metrics."""
        alerts = []
        current_time = datetime.now(timezone.utc)
        
        for config in self.alert_configs:
            if not config.enabled:
                continue
            
            # Check cooldown
            last_alert_time = self.last_alerts.get(config.name)
            if last_alert_time and (current_time - last_alert_time).total_seconds() < config.cooldown_minutes * 60:
                continue
            
            alert_triggered = False
            alert_value = None
            
            # Check different alert conditions
            if config.name == "umami_response_time":
                umami_result = health_results.get("umami_integration", {})
                response_time = umami_result.get("response_time_ms", 0)
                if self._compare_value(response_time, config.threshold, config.comparison):
                    alert_triggered = True
                    alert_value = response_time
            
            elif config.name == "analytics_processing_time":
                analytics_result = health_results.get("analytics_processing", {})
                response_time = analytics_result.get("response_time_ms", 0)
                if self._compare_value(response_time, config.threshold, config.comparison):
                    alert_triggered = True
                    alert_value = response_time
            
            elif config.name == "personalization_response_time":
                personalization_result = health_results.get("personalization_engine", {})
                response_time = personalization_result.get("response_time_ms", 0)
                if self._compare_value(response_time, config.threshold, config.comparison):
                    alert_triggered = True
                    alert_value = response_time
            
            elif config.name == "analytics_data_processing_errors":
                error_rate = metrics.get("error_rate", 0)
                if self._compare_value(error_rate, config.threshold, config.comparison):
                    alert_triggered = True
                    alert_value = error_rate
            
            if alert_triggered:
                alerts.append({
                    "name": config.name,
                    "message": f"Alert: {config.name} threshold exceeded",
                    "threshold": config.threshold,
                    "current_value": alert_value,
                    "severity": "critical" if config.comparison == "gt" and alert_value > config.threshold * 2 else "warning",
                    "timestamp": current_time.isoformat()
                })
                
                # Update last alert time
                self.last_alerts[config.name] = current_time
                
                # Log alert
                logger.warning(f"Analytics alert triggered: {config.name} = {alert_value}, threshold = {config.threshold}")
        
        return alerts
    
    def _compare_value(self, value: float, threshold: float, comparison: str) -> bool:
        """Compare value against threshold using specified comparison."""
        if comparison == "gt":
            return value > threshold
        elif comparison == "lt":
            return value < threshold
        elif comparison == "eq":
            return value == threshold
        return False
    
    async def send_alert_notification(self, alert: Dict[str, Any]) -> bool:
        """Send alert notification (placeholder for integration with notification system)."""
        try:
            # This would integrate with your notification system
            # For now, just log the alert
            logger.critical(f"ANALYTICS ALERT: {alert['message']} - Value: {alert['current_value']}, Threshold: {alert['threshold']}")
            
            # In a real implementation, you might:
            # - Send email notifications
            # - Post to Slack/Discord
            # - Send to monitoring systems like PagerDuty
            # - Store in alert database
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to send alert notification: {str(e)}")
            return False