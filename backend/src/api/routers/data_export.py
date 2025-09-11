"""
Data Export and Management API endpoints.

This module provides endpoints for exporting analytics data, managing data exports,
and providing aggregated analytics dashboards for course creators and administrators.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...services.data_export_service import DataExportService
from ...services.auth_service import get_current_user
from ...db.models.db_user import User
from ..schemas.privacy import (
    DataExportRequest, DataExportResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-export", tags=["data-export"])
export_service = DataExportService()


@router.post("/request", response_model=DataExportResponse)
async def request_data_export(
    export_request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request export of user analytics data.
    
    Args:
        export_request: Data export request details
        background_tasks: Background task handler
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Data export response with download information
    """
    user_id = export_request.user_id
    
    # Check if user can export this data (admin or own data)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this user's data"
        )
    
    try:
        # Process export in background for large datasets
        background_tasks.add_task(
            _process_data_export,
            db, export_request, current_user.id
        )
        
        return DataExportResponse(
            user_id=user_id,
            export_id="pending",  # Will be generated in background task
            status="in_progress",
            created_at=datetime.now(timezone.utc),
            message="Data export request submitted and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error processing export request for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data export request"
        )


@router.get("/download/{export_id}")
async def download_export_file(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download exported data file.
    
    Args:
        export_id: Export ID to download
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        File download response
    """
    # In a real implementation, you would:
    # 1. Validate export_id exists and belongs to user
    # 2. Check if file hasn't expired
    # 3. Return the actual file
    
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File download not yet implemented"
    )


@router.get("/course-analytics/{course_id}")
async def get_course_analytics(
    course_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated analytics for a specific course (course creators only).
    
    Args:
        course_id: Course ID to get analytics for
        days: Number of days to analyze
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Aggregated course analytics
    """
    try:
        analytics_data = export_service.get_aggregated_analytics_for_course_creator(
            db=db,
            creator_user_id=current_user.id,
            course_id=course_id,
            days=days
        )
        
        return {
            "course_id": course_id,
            "analytics": analytics_data,
            "generated_at": datetime.now(timezone.utc)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting course analytics for course {course_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course analytics"
        )


@router.get("/creator-analytics")
async def get_creator_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated analytics for all courses by the current user.
    
    Args:
        days: Number of days to analyze
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Aggregated analytics for all user's courses
    """
    try:
        analytics_data = export_service.get_aggregated_analytics_for_course_creator(
            db=db,
            creator_user_id=current_user.id,
            course_id=None,  # All courses
            days=days
        )
        
        return {
            "creator_id": current_user.id,
            "analytics": analytics_data,
            "generated_at": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting creator analytics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve creator analytics"
        )


@router.get("/admin-dashboard")
async def get_admin_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get admin analytics dashboard (admin only).
    
    Args:
        days: Number of days to analyze
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Admin dashboard analytics
    """
    # Only admins can access admin dashboard
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access the admin dashboard"
        )
    
    try:
        dashboard_data = export_service.get_admin_analytics_dashboard(
            db=db,
            days=days
        )
        
        return {
            "dashboard": dashboard_data,
            "generated_at": datetime.now(timezone.utc),
            "generated_by": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin dashboard"
        )


@router.get("/export-status/{export_id}")
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a data export request.
    
    Args:
        export_id: Export ID to check status for
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Export status information
    """
    # In a real implementation, you would:
    # 1. Look up export status in database
    # 2. Return current status, progress, etc.
    
    # For now, return a placeholder response
    return {
        "export_id": export_id,
        "status": "completed",
        "progress": 100,
        "message": "Export completed successfully",
        "download_available": True,
        "expires_at": datetime.now(timezone.utc)
    }


@router.delete("/export/{export_id}")
async def delete_export_file(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an exported data file.
    
    Args:
        export_id: Export ID to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    # In a real implementation, you would:
    # 1. Validate export belongs to user
    # 2. Delete the file from storage
    # 3. Update database record
    
    return {
        "export_id": export_id,
        "deleted": True,
        "deleted_at": datetime.now(timezone.utc)
    }


@router.get("/analytics-summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of available analytics data for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Analytics data summary
    """
    try:
        # Get basic counts of user's analytics data
        from ...db.crud import analytics_crud
        
        behavior_count = analytics_crud.count_user_behavior_data(db, current_user.id)
        learning_patterns = analytics_crud.get_learning_patterns_by_user(db, current_user.id)
        learning_profile = analytics_crud.get_user_learning_profile(db, current_user.id)
        engagement_metrics = analytics_crud.get_user_engagement_metrics(db, current_user.id)
        
        return {
            "user_id": current_user.id,
            "data_summary": {
                "behavior_events": behavior_count,
                "learning_patterns": len(learning_patterns),
                "has_learning_profile": learning_profile is not None,
                "engagement_metrics": len(engagement_metrics)
            },
            "available_exports": [
                "behavior_data",
                "learning_patterns", 
                "learning_profile",
                "engagement_metrics"
            ],
            "export_formats": ["json", "csv"],
            "generated_at": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics summary for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics summary"
        )


# Background task functions
async def _process_data_export(
    db: Session, 
    export_request: DataExportRequest, 
    requesting_user_id: str
):
    """Background task to process data export."""
    try:
        export_result = await export_service.export_user_data(
            db=db,
            user_id=export_request.user_id,
            data_types=export_request.data_types,
            format=export_request.format,
            include_metadata=export_request.include_metadata
        )
        
        logger.info(f"Completed data export for user {export_request.user_id}: {export_result['export_id']}")
        
        # In a real implementation, you would:
        # 1. Store export metadata in database
        # 2. Send notification to user when ready
        # 3. Set up file cleanup after expiry
        
    except Exception as e:
        logger.error(f"Failed to export data for user {export_request.user_id}: {str(e)}")


@router.get("/course-engagement-trends/{course_id}")
async def get_course_engagement_trends(
    course_id: int,
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get engagement trends for a specific course over time.
    
    Args:
        course_id: Course ID to analyze
        days: Number of days to analyze
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Course engagement trends data
    """
    try:
        # Verify user owns the course
        from ...db.crud import courses_crud
        course = courses_crud.get_course_by_id(db, course_id)
        if not course or course.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Course not found or not owned by user"
            )
        
        # Get engagement trends (simplified implementation)
        from ...db.crud import analytics_crud
        from datetime import timedelta
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get daily engagement data
        daily_engagement = analytics_crud.get_user_activity_timeline(
            db=db, 
            user_id=current_user.id,  # This should be modified to get all users for the course
            days=days
        )
        
        return {
            "course_id": course_id,
            "course_title": course.title if hasattr(course, 'title') else f"Course {course_id}",
            "engagement_trends": daily_engagement,
            "time_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "generated_at": datetime.now(timezone.utc)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting engagement trends for course {course_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve engagement trends"
        )