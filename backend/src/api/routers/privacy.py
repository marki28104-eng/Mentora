"""
Privacy and data management API endpoints.

This module provides endpoints for GDPR compliance, user consent management,
data deletion, anonymization, and privacy reporting.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...services.privacy_service import PrivacyService
from ...services.auth_service import get_current_user
from ...db.models.db_user import User
from ..schemas.privacy import (
    ConsentPreferences, ConsentUpdate, ConsentStatus,
    DataDeletionRequest, DataDeletionResponse,
    DataExportRequest, DataExportResponse,
    PrivacyReport, AnonymizationRequest, AnonymizationResponse,
    RetentionPolicy, DataCleanupRequest, DataCleanupResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/privacy", tags=["privacy"])
privacy_service = PrivacyService()


@router.get("/consent/{user_id}", response_model=ConsentStatus)
async def get_user_consent(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user consent status for data collection and processing.
    
    Args:
        user_id: User ID to get consent for
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User consent status
    """
    # Check if user can access this data (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's consent data"
        )
    
    try:
        consent_status = privacy_service.check_user_consent(db, user_id)
        return ConsentStatus(
            user_id=user_id,
            **consent_status,
            last_updated=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error getting consent for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consent status"
        )


@router.put("/consent/{user_id}", response_model=ConsentStatus)
async def update_user_consent(
    user_id: str,
    consent_update: ConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user consent preferences.
    
    Args:
        user_id: User ID to update consent for
        consent_update: New consent preferences
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated consent status
    """
    # Check if user can update this data (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's consent"
        )
    
    try:
        # Convert to dict, excluding None values
        consent_data = {
            k: v for k, v in consent_update.model_dump().items() 
            if v is not None
        }
        
        success = privacy_service.update_user_consent(db, user_id, consent_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return updated consent status
        updated_consent = privacy_service.check_user_consent(db, user_id)
        return ConsentStatus(
            user_id=user_id,
            **updated_consent,
            last_updated=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating consent for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consent preferences"
        )


@router.post("/delete-data", response_model=DataDeletionResponse)
async def request_data_deletion(
    deletion_request: DataDeletionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request deletion of user data (GDPR right to be forgotten).
    
    Args:
        deletion_request: Data deletion request details
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Data deletion response
    """
    user_id = deletion_request.user_id
    
    # Check if user can delete this data (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user's data"
        )
    
    try:
        # Validate deletion type
        hard_delete = deletion_request.deletion_type == "hard_delete"
        
        # Process deletion in background for large datasets
        background_tasks.add_task(
            _process_data_deletion,
            db, user_id, hard_delete
        )
        
        return DataDeletionResponse(
            user_id=user_id,
            deletion_type=deletion_request.deletion_type,
            status="in_progress",
            deleted_records={},
            processed_at=datetime.now(timezone.utc),
            message="Data deletion request submitted and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error processing deletion request for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data deletion request"
        )


@router.get("/report/{user_id}", response_model=PrivacyReport)
async def get_privacy_report(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a privacy report showing what data is collected for a user.
    
    Args:
        user_id: User ID to generate report for
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Privacy report with data summary
    """
    # Check if user can access this data (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's privacy report"
        )
    
    try:
        report_data = privacy_service.generate_privacy_report(db, user_id)
        return PrivacyReport(**report_data)
        
    except Exception as e:
        logger.error(f"Error generating privacy report for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate privacy report"
        )


@router.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_user_data(
    anonymization_request: AnonymizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Anonymize user data while preserving aggregate analytics.
    
    Args:
        anonymization_request: Anonymization request details
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Anonymization response
    """
    user_id = anonymization_request.user_id
    
    # Check if user can anonymize this data (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to anonymize this user's data"
        )
    
    try:
        # Process anonymization in background
        background_tasks.add_task(
            _process_data_anonymization,
            db, user_id, anonymization_request.batch_size
        )
        
        return AnonymizationResponse(
            user_id=user_id,
            anonymized_records={},
            status="in_progress",
            processed_at=datetime.now(timezone.utc),
            message="Data anonymization request submitted and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error processing anonymization request for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process anonymization request"
        )


@router.get("/retention-policy", response_model=RetentionPolicy)
async def get_retention_policy(
    current_user: User = Depends(get_current_user)
):
    """
    Get current data retention policy.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current retention policy
    """
    try:
        policy = privacy_service.get_data_retention_policy()
        return RetentionPolicy(
            behavior_data=policy["behavior_data"],
            learning_patterns=policy["learning_patterns"],
            learning_profiles=policy["learning_profiles"],
            engagement_metrics=policy["engagement_metrics"],
            anonymized_data=policy["anonymized_data"],
            last_updated=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error getting retention policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve retention policy"
        )


@router.post("/cleanup-expired-data", response_model=DataCleanupResponse)
async def cleanup_expired_data(
    cleanup_request: DataCleanupRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clean up expired data according to retention policy (admin only).
    
    Args:
        cleanup_request: Cleanup request parameters
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cleanup response
    """
    # Only admins can trigger data cleanup
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can trigger data cleanup"
        )
    
    try:
        if cleanup_request.dry_run:
            # For dry run, calculate what would be deleted without actually deleting
            # This is a simplified implementation - in practice, you'd calculate counts
            cleanup_counts = {
                "behavior_data": 0,
                "engagement_metrics": 0,
                "estimated_only": True
            }
        else:
            # Process actual cleanup in background
            background_tasks.add_task(
                _process_data_cleanup,
                db
            )
            cleanup_counts = {}
        
        return DataCleanupResponse(
            cleanup_counts=cleanup_counts,
            dry_run=cleanup_request.dry_run,
            processed_at=datetime.now(timezone.utc),
            message="Data cleanup completed" if cleanup_request.dry_run else "Data cleanup started"
        )
        
    except Exception as e:
        logger.error(f"Error processing data cleanup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data cleanup"
        )


# Background task functions
async def _process_data_deletion(db: Session, user_id: str, hard_delete: bool):
    """Background task to process data deletion."""
    try:
        deletion_counts = await privacy_service.delete_user_analytics_data(
            db, user_id, hard_delete
        )
        logger.info(f"Completed data deletion for user {user_id}: {deletion_counts}")
    except Exception as e:
        logger.error(f"Failed to delete data for user {user_id}: {str(e)}")


async def _process_data_anonymization(db: Session, user_id: str, batch_size: int):
    """Background task to process data anonymization."""
    try:
        anonymized_count = await privacy_service.anonymize_user_behavior_data(
            db, user_id, batch_size
        )
        logger.info(f"Completed data anonymization for user {user_id}: {anonymized_count} records")
    except Exception as e:
        logger.error(f"Failed to anonymize data for user {user_id}: {str(e)}")


async def _process_data_cleanup(db: Session):
    """Background task to process expired data cleanup."""
    try:
        cleanup_counts = await privacy_service.cleanup_expired_data(db)
        logger.info(f"Completed data cleanup: {cleanup_counts}")
    except Exception as e:
        logger.error(f"Failed to cleanup expired data: {str(e)}")


@router.get("/validate-consent/{user_id}/{data_type}")
async def validate_data_collection_consent(
    user_id: str,
    data_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate that user has given consent for specific type of data collection.
    
    Args:
        user_id: User ID to check
        data_type: Type of data being collected
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Consent validation result
    """
    # Check if user can validate this consent (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to validate this user's consent"
        )
    
    try:
        has_consent = privacy_service.validate_data_collection_consent(db, user_id, data_type)
        return {
            "user_id": user_id,
            "data_type": data_type,
            "has_consent": has_consent,
            "checked_at": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error validating consent for user {user_id}, data type {data_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate consent"
        )