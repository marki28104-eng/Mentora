"""
Advanced Analytics API endpoints for predictive analytics, cohort analysis, and real-time personalization.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...services.advanced_analytics_service import AdvancedAnalyticsService
from ...core.security import get_current_user
from ...db.models.db_user import User
from ...api.schemas.analytics import (
    PredictiveOutcomeResponse, CohortAnalysisResponse, 
    RealTimePersonalizationResponse, RealTimeEventRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-analytics", tags=["advanced-analytics"])

# Initialize service
advanced_analytics_service = AdvancedAnalyticsService()


@router.post("/initialize", response_model=Dict[str, Any])
async def initialize_advanced_analytics(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize advanced analytics models.
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Run initialization in background
        background_tasks.add_task(
            advanced_analytics_service.initialize_models, db
        )
        
        return {
            "message": "Advanced analytics initialization started",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error initializing advanced analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize advanced analytics")


@router.get("/predict-outcome/{course_id}", response_model=Optional[PredictiveOutcomeResponse])
async def predict_learning_outcome(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get predictive analytics for learning outcomes for a specific course.
    """
    try:
        prediction = await advanced_analytics_service.get_learning_outcome_prediction(
            db=db,
            user_id=current_user.id,
            course_id=course_id
        )
        
        if not prediction:
            return None
        
        return PredictiveOutcomeResponse(
            user_id=prediction.user_id,
            prediction_type=prediction.prediction_type,
            predicted_value=prediction.predicted_value,
            confidence=prediction.confidence,
            factors=prediction.factors,
            recommendations=prediction.recommendations,
            created_at=prediction.created_at
        )
        
    except Exception as e:
        logger.error(f"Error predicting learning outcome: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate prediction")


@router.get("/cohort-analysis", response_model=List[CohortAnalysisResponse])
async def get_cohort_analysis(
    cohort_type: str = "registration_month",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get cohort analysis for learning pattern identification.
    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        cohort_analyses = await advanced_analytics_service.analyze_cohorts(
            db=db,
            cohort_type=cohort_type
        )
        
        return [
            CohortAnalysisResponse(
                cohort_name=analysis.cohort_name,
                cohort_size=analysis.cohort_size,
                time_period=analysis.time_period,
                retention_rates=analysis.retention_rates,
                engagement_trends=analysis.engagement_trends,
                learning_patterns=analysis.learning_patterns,
                performance_metrics=analysis.performance_metrics,
                created_at=analysis.created_at
            )
            for analysis in cohort_analyses
        ]
        
    except Exception as e:
        logger.error(f"Error performing cohort analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform cohort analysis")


@router.post("/real-time-event", response_model=Optional[RealTimePersonalizationResponse])
async def process_real_time_event(
    event_request: RealTimeEventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process real-time learning event and get personalization adjustments.
    """
    try:
        personalization = await advanced_analytics_service.process_real_time_event(
            db=db,
            user_id=current_user.id,
            session_id=event_request.session_id,
            event_data=event_request.event_data
        )
        
        if not personalization:
            return None
        
        return RealTimePersonalizationResponse(
            user_id=personalization.user_id,
            session_id=personalization.session_id,
            adjustments=personalization.adjustments,
            trigger_events=personalization.trigger_events,
            confidence=personalization.confidence,
            created_at=personalization.created_at
        )
        
    except Exception as e:
        logger.error(f"Error processing real-time event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process real-time event")


@router.get("/user-predictions", response_model=List[PredictiveOutcomeResponse])
async def get_user_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all available predictions for the current user.
    """
    try:
        # This would typically fetch stored predictions from database
        # For now, we'll return an empty list as predictions are generated on-demand
        return []
        
    except Exception as e:
        logger.error(f"Error fetching user predictions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch predictions")


@router.post("/cleanup-sessions")
async def cleanup_session_data(
    current_user: User = Depends(get_current_user)
):
    """
    Clean up old session data (admin only).
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        advanced_analytics_service.cleanup_session_data()
        
        return {
            "message": "Session data cleanup completed",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up session data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup session data")


@router.get("/analytics-status", response_model=Dict[str, Any])
async def get_analytics_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get status of advanced analytics models and services.
    """
    try:
        status = {
            "predictive_models": {
                "completion_predictor": advanced_analytics_service.predictive_engine.is_trained,
                "last_trained": advanced_analytics_service.predictive_engine.completion_predictor.__dict__.get('last_trained')
            },
            "cohort_analysis": {
                "available": True,
                "supported_cohort_types": [
                    "registration_month",
                    "learning_style", 
                    "difficulty_level",
                    "engagement_level"
                ]
            },
            "real_time_personalization": {
                "active_sessions": len(advanced_analytics_service.realtime_engine.session_data),
                "adjustment_thresholds": advanced_analytics_service.realtime_engine.adjustment_thresholds
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting analytics status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics status")


@router.get("/cohort-types", response_model=List[Dict[str, str]])
async def get_available_cohort_types(
    current_user: User = Depends(get_current_user)
):
    """
    Get available cohort analysis types.
    """
    cohort_types = [
        {
            "type": "registration_month",
            "description": "Group users by registration month"
        },
        {
            "type": "learning_style", 
            "description": "Group users by identified learning style"
        },
        {
            "type": "difficulty_level",
            "description": "Group users by preferred difficulty level"
        },
        {
            "type": "engagement_level",
            "description": "Group users by engagement score (high/medium/low)"
        }
    ]
    
    return cohort_types