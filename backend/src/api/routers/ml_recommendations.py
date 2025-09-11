"""
API endpoints for ML-based recommendations and A/B testing.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ...db.database import get_db
from ...services.ml_recommendation_service import MLRecommendationService
from ...services.personalization_engine import PersonalizationEngine
from ...db.crud import analytics_crud
from ...db.models.db_course import Course
from ...core.security import get_current_user
from ...api.schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml-recommendations", tags=["ML Recommendations"])

# Initialize services
ml_service = MLRecommendationService()
personalization_engine = PersonalizationEngine()


class MLRecommendationRequest(BaseModel):
    """Request model for ML recommendations."""
    topic: Optional[str] = None
    max_recommendations: int = Field(default=5, ge=1, le=20)
    include_difficulty_prediction: bool = True
    include_cluster_info: bool = False


class MLRecommendationResponse(BaseModel):
    """Response model for ML recommendations."""
    course_id: int
    title: str
    ml_score: float
    optimal_difficulty: Optional[float] = None
    user_cluster: Optional[int] = None
    confidence: float
    reason: str
    recommendation_id: str


class ABTestRequest(BaseModel):
    """Request model for creating A/B tests."""
    test_name: str
    variants: List[str]
    traffic_split: List[float]
    success_metric: str
    duration_days: int = Field(default=14, ge=1, le=90)


class ABTestAssignmentResponse(BaseModel):
    """Response model for A/B test assignment."""
    test_name: str
    variant: str
    user_id: str


class FeedbackRequest(BaseModel):
    """Request model for collecting feedback."""
    recommendation_id: str
    action: Optional[str] = None  # For implicit feedback
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)  # For explicit feedback
    context: Dict[str, Any] = Field(default_factory=dict)


class ModelTrainingResponse(BaseModel):
    """Response model for model training results."""
    status: str
    results: Dict[str, Any]
    training_data_size: int
    timestamp: datetime


@router.get("/recommendations", response_model=List[MLRecommendationResponse])
async def get_ml_recommendations(
    request: MLRecommendationRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ML-based course recommendations for the current user.
    
    This endpoint uses trained machine learning models to provide
    personalized course recommendations based on user behavior patterns.
    """
    try:
        # Get course candidates
        if request.topic:
            # Get courses related to the topic
            courses = db.query(Course).filter(
                Course.title.ilike(f"%{request.topic}%")
            ).limit(50).all()
        else:
            # Get all available courses
            courses = db.query(Course).limit(50).all()
        
        if not courses:
            return []
        
        # Get ML recommendations
        ml_recommendations = await ml_service.get_ml_recommendations(
            db=db,
            user_id=str(current_user.id),
            course_candidates=courses,
            max_recommendations=request.max_recommendations
        )
        
        # Convert to response format
        recommendations = []
        for rec in ml_recommendations:
            recommendation_id = f"ml_{current_user.id}_{rec['course_id']}_{int(datetime.now().timestamp())}"
            
            response = MLRecommendationResponse(
                course_id=rec['course_id'],
                title=rec['title'],
                ml_score=rec['ml_score'],
                confidence=rec['confidence'],
                reason=rec['reason'],
                recommendation_id=recommendation_id
            )
            
            if request.include_difficulty_prediction:
                response.optimal_difficulty = rec.get('optimal_difficulty')
            
            if request.include_cluster_info:
                response.user_cluster = rec.get('user_cluster')
            
            recommendations.append(response)
        
        logger.info(f"Generated {len(recommendations)} ML recommendations for user {current_user.id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting ML recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate ML recommendations")


@router.post("/train-models", response_model=ModelTrainingResponse)
async def train_ml_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Train ML recommendation models using available user behavior data.
    
    This endpoint triggers training of all ML models including:
    - Course recommendation model
    - Difficulty prediction model  
    - User clustering model
    
    Requires admin privileges.
    """
    # Check if user is admin (simplified check)
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        # Train models
        results = await ml_service.train_models(db)
        
        if 'error' in results:
            raise HTTPException(status_code=400, detail=results['error'])
        
        # Count training data size
        training_data = await ml_service._prepare_training_data(db)
        training_data_size = len(training_data)
        
        response = ModelTrainingResponse(
            status="success",
            results=results,
            training_data_size=training_data_size,
            timestamp=datetime.now(timezone.utc)
        )
        
        logger.info(f"Successfully trained ML models with {training_data_size} data points")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training ML models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to train ML models")


@router.post("/ab-tests", response_model=Dict[str, Any])
async def create_ab_test(
    request: ABTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new A/B test for personalization strategies.
    
    Requires admin privileges.
    """
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        test_config = ml_service.ab_testing.create_ab_test(
            test_name=request.test_name,
            variants=request.variants,
            traffic_split=request.traffic_split,
            success_metric=request.success_metric,
            duration_days=request.duration_days
        )
        
        logger.info(f"Created A/B test '{request.test_name}' with variants {request.variants}")
        return test_config
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating A/B test: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create A/B test")


@router.get("/ab-tests/{test_name}/assignment", response_model=ABTestAssignmentResponse)
async def get_ab_test_assignment(
    test_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get A/B test variant assignment for the current user.
    """
    try:
        variant = ml_service.ab_testing.assign_user_to_variant(
            test_name=test_name,
            user_id=str(current_user.id)
        )
        
        if variant is None:
            raise HTTPException(status_code=404, detail="A/B test not found or inactive")
        
        response = ABTestAssignmentResponse(
            test_name=test_name,
            variant=variant,
            user_id=str(current_user.id)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A/B test assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get A/B test assignment")


@router.get("/ab-tests/{test_name}/results", response_model=Dict[str, Any])
async def get_ab_test_results(
    test_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get results for an A/B test.
    
    Requires admin privileges.
    """
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        results = ml_service.ab_testing.get_test_results(test_name)
        
        if results is None:
            raise HTTPException(status_code=404, detail="A/B test not found")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting A/B test results: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get A/B test results")


@router.post("/feedback")
async def collect_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Collect user feedback on recommendations for model improvement.
    
    Supports both implicit feedback (user actions) and explicit feedback (ratings).
    """
    try:
        if request.action:
            # Collect implicit feedback
            ml_service.feedback_loop.collect_implicit_feedback(
                user_id=str(current_user.id),
                recommendation_id=request.recommendation_id,
                action=request.action,
                context=request.context
            )
        elif request.rating is not None:
            # Collect explicit feedback
            ml_service.feedback_loop.collect_explicit_feedback(
                user_id=str(current_user.id),
                recommendation_id=request.recommendation_id,
                rating=request.rating,
                context=request.context
            )
        else:
            raise HTTPException(status_code=400, detail="Either action or rating must be provided")
        
        return {"status": "success", "message": "Feedback collected"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error collecting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect feedback")


@router.post("/ab-tests/{test_name}/conversion")
async def record_conversion(
    test_name: str,
    metric_value: float = Body(default=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a conversion event for A/B test analysis.
    """
    try:
        ml_service.ab_testing.record_conversion(
            test_name=test_name,
            user_id=str(current_user.id),
            metric_value=metric_value
        )
        
        return {"status": "success", "message": "Conversion recorded"}
        
    except Exception as e:
        logger.error(f"Error recording conversion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record conversion")


@router.get("/model-performance", response_model=Dict[str, Any])
async def get_model_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for ML recommendation models.
    
    Requires admin privileges.
    """
    # Check if user is admin
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        # Get feedback-based performance metrics
        performance_metrics = ml_service.feedback_loop.get_model_performance_metrics()
        
        # Add model training status
        model_status = {
            'course_recommendation_trained': ml_service.course_model.is_trained,
            'difficulty_prediction_trained': ml_service.difficulty_model.is_trained,
            'user_clustering_trained': ml_service.clustering_model.is_trained,
            'course_model_last_trained': ml_service.course_model.last_trained,
            'difficulty_model_last_trained': ml_service.difficulty_model.last_trained,
            'clustering_model_last_trained': ml_service.clustering_model.last_trained
        }
        
        return {
            'performance_metrics': performance_metrics,
            'model_status': model_status,
            'timestamp': datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model performance")


@router.get("/user-cluster")
async def get_user_cluster(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the user's cluster assignment for personalization insights.
    """
    try:
        if not ml_service.clustering_model.is_trained:
            raise HTTPException(status_code=400, detail="User clustering model not trained")
        
        # Get user profile
        user_profile = analytics_crud.get_user_learning_profile(db, str(current_user.id))
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user cluster
        user_features = ml_service._prepare_user_features(user_profile)
        user_cluster = ml_service.clustering_model.predict_cluster([user_features])
        
        return {
            'user_id': current_user.id,
            'cluster': int(user_cluster),
            'cluster_description': f"Learning pattern cluster {user_cluster}",
            'timestamp': datetime.now(timezone.utc)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user cluster: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user cluster")