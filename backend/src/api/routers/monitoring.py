"""API endpoints for analytics monitoring and health checks."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from db.database import get_db
from utils.auth import get_current_admin_user
from db.models.db_user import User
from services.analytics_monitoring_service import AnalyticsMonitoringService, HealthStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health", response_model=Dict[str, Any])
async def get_analytics_health_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get comprehensive health status of analytics system.
    
    Admin-only endpoint that returns detailed health information
    about all analytics components.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        health_status = await monitoring_service.run_comprehensive_health_check()
        
        return {
            "status": "success",
            "data": health_status
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/health/umami", response_model=Dict[str, Any])
async def get_umami_health_status(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get Umami integration health status.
    
    Admin-only endpoint for checking Umami API connectivity
    and configuration.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        health_result = await monitoring_service.check_umami_integration_health()
        
        return {
            "status": "success",
            "data": {
                "service": health_result.service,
                "status": health_result.status.value,
                "message": health_result.message,
                "response_time_ms": health_result.response_time_ms,
                "timestamp": health_result.timestamp.isoformat(),
                "details": health_result.details
            }
        }
    
    except Exception as e:
        logger.error(f"Umami health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Umami health check failed: {str(e)}"
        )


@router.get("/health/analytics", response_model=Dict[str, Any])
async def get_analytics_processing_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get analytics processing service health status.
    
    Admin-only endpoint for checking analytics processing
    performance and functionality.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        health_result = await monitoring_service.check_analytics_processing_health(db)
        
        return {
            "status": "success",
            "data": {
                "service": health_result.service,
                "status": health_result.status.value,
                "message": health_result.message,
                "response_time_ms": health_result.response_time_ms,
                "timestamp": health_result.timestamp.isoformat(),
                "details": health_result.details
            }
        }
    
    except Exception as e:
        logger.error(f"Analytics processing health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analytics processing health check failed: {str(e)}"
        )


@router.get("/health/personalization", response_model=Dict[str, Any])
async def get_personalization_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get personalization engine health status.
    
    Admin-only endpoint for checking personalization engine
    performance and functionality.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        health_result = await monitoring_service.check_personalization_engine_health(db)
        
        return {
            "status": "success",
            "data": {
                "service": health_result.service,
                "status": health_result.status.value,
                "message": health_result.message,
                "response_time_ms": health_result.response_time_ms,
                "timestamp": health_result.timestamp.isoformat(),
                "details": health_result.details
            }
        }
    
    except Exception as e:
        logger.error(f"Personalization engine health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Personalization engine health check failed: {str(e)}"
        )


@router.get("/health/database", response_model=Dict[str, Any])
async def get_database_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get database connectivity health status.
    
    Admin-only endpoint for checking database connectivity
    and analytics table accessibility.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        health_result = await monitoring_service.check_database_health(db)
        
        return {
            "status": "success",
            "data": {
                "service": health_result.service,
                "status": health_result.status.value,
                "message": health_result.message,
                "response_time_ms": health_result.response_time_ms,
                "timestamp": health_result.timestamp.isoformat(),
                "details": health_result.details
            }
        }
    
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_analytics_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get analytics system performance metrics.
    
    Admin-only endpoint that returns detailed performance
    metrics for the analytics system.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        metrics = await monitoring_service.get_analytics_metrics(db)
        
        return {
            "status": "success",
            "data": metrics
        }
    
    except Exception as e:
        logger.error(f"Failed to get analytics metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics metrics: {str(e)}"
        )


@router.get("/alerts", response_model=Dict[str, Any])
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get active alerts for the analytics system.
    
    Admin-only endpoint that returns current alerts
    and their status.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        
        # Run health check to get current alerts
        health_status = await monitoring_service.run_comprehensive_health_check()
        alerts = health_status.get("alerts", [])
        
        return {
            "status": "success",
            "data": {
                "active_alerts": alerts,
                "alert_count": len(alerts),
                "timestamp": health_status.get("timestamp")
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.post("/alerts/test", response_model=Dict[str, Any])
async def test_alert_system(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Test the alert system by sending a test alert.
    
    Admin-only endpoint for testing alert notifications.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        
        # Create test alert
        test_alert = {
            "name": "test_alert",
            "message": "Test alert from monitoring system",
            "threshold": 100,
            "current_value": 150,
            "severity": "warning",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Send alert notification in background
        background_tasks.add_task(
            monitoring_service.send_alert_notification,
            test_alert
        )
        
        return {
            "status": "success",
            "message": "Test alert sent successfully",
            "data": test_alert
        }
    
    except Exception as e:
        logger.error(f"Failed to send test alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test alert: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_monitoring_status():
    """
    Get basic monitoring system status.
    
    Public endpoint that returns basic system status
    without sensitive details.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        
        # Run basic health checks
        health_status = await monitoring_service.run_comprehensive_health_check()
        overall_status = health_status.get("overall_status", "unknown")
        
        # Return simplified status
        return {
            "status": "success",
            "data": {
                "system_status": overall_status,
                "services_count": len(health_status.get("services", {})),
                "alerts_count": len(health_status.get("alerts", [])),
                "timestamp": health_status.get("timestamp")
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {str(e)}")
        return {
            "status": "error",
            "data": {
                "system_status": "unknown",
                "error": "Monitoring system unavailable"
            }
        }


@router.get("/health/summary", response_model=Dict[str, Any])
async def get_health_summary(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get summarized health status of all services.
    
    Admin-only endpoint that returns a quick overview
    of all service health statuses.
    """
    try:
        monitoring_service = AnalyticsMonitoringService()
        health_status = await monitoring_service.run_comprehensive_health_check()
        
        services = health_status.get("services", {})
        summary = {}
        
        for service_name, service_data in services.items():
            summary[service_name] = {
                "status": service_data.get("status"),
                "response_time_ms": service_data.get("response_time_ms"),
                "message": service_data.get("message")
            }
        
        return {
            "status": "success",
            "data": {
                "overall_status": health_status.get("overall_status"),
                "services": summary,
                "total_alerts": len(health_status.get("alerts", [])),
                "timestamp": health_status.get("timestamp")
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get health summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health summary: {str(e)}"
        )