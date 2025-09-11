"""
Data Export Service for analytics data management and GDPR compliance.

This service provides functionality to export user analytics data in various formats,
create admin dashboards for data management, and provide aggregated analytics for course creators.
"""

import json
import csv
import logging
import tempfile
import zipfile
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..db.crud import analytics_crud, users_crud, courses_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics,
    EventType, LearningStyleType, DifficultyLevel
)
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class DataExportService:
    """Service for exporting and managing analytics data."""
    
    def __init__(self):
        self.export_formats = ["json", "csv"]
        self.supported_data_types = [
            "behavior_data", "learning_patterns", "learning_profile", 
            "engagement_metrics", "consent_history"
        ]
    
    async def export_user_data(
        self,
        db: Session,
        user_id: str,
        data_types: List[str],
        format: str = "json",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export all analytics data for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to export data for
            data_types: List of data types to include in export
            format: Export format (json or csv)
            include_metadata: Whether to include metadata in export
            
        Returns:
            Dictionary with export information and file paths
        """
        if format not in self.export_formats:
            raise ValueError(f"Unsupported export format: {format}")
        
        export_id = generate_analytics_id()
        export_data = {}
        file_paths = []
        
        try:
            # Export behavior data
            if "behavior_data" in data_types:
                behavior_data = analytics_crud.get_user_behavior_data(
                    db=db, user_id=user_id, limit=10000
                )
                export_data["behavior_data"] = self._serialize_behavior_data(
                    behavior_data, include_metadata
                )
            
            # Export learning patterns
            if "learning_patterns" in data_types:
                learning_patterns = analytics_crud.get_learning_patterns_by_user(db, user_id)
                export_data["learning_patterns"] = self._serialize_learning_patterns(
                    learning_patterns, include_metadata
                )
            
            # Export learning profile
            if "learning_profile" in data_types:
                learning_profile = analytics_crud.get_user_learning_profile(db, user_id)
                if learning_profile:
                    export_data["learning_profile"] = self._serialize_learning_profile(
                        learning_profile, include_metadata
                    )
            
            # Export engagement metrics
            if "engagement_metrics" in data_types:
                engagement_metrics = analytics_crud.get_user_engagement_metrics(db, user_id)
                export_data["engagement_metrics"] = self._serialize_engagement_metrics(
                    engagement_metrics, include_metadata
                )
            
            # Export consent history (if available)
            if "consent_history" in data_types:
                user = users_crud.get_user_by_id(db, user_id)
                if user and user.settings:
                    export_data["consent_history"] = {
                        "current_consent": user.settings,
                        "last_updated": user.settings.get("consent_updated_at")
                    }
            
            # Create export files
            if format == "json":
                file_path = await self._create_json_export(export_id, user_id, export_data)
                file_paths.append(file_path)
            elif format == "csv":
                csv_files = await self._create_csv_export(export_id, user_id, export_data)
                file_paths.extend(csv_files)
            
            # Create zip file if multiple files
            if len(file_paths) > 1:
                zip_path = await self._create_zip_export(export_id, user_id, file_paths)
                final_path = zip_path
            else:
                final_path = file_paths[0] if file_paths else None
            
            return {
                "export_id": export_id,
                "user_id": user_id,
                "format": format,
                "data_types": data_types,
                "file_path": final_path,
                "file_size": Path(final_path).stat().st_size if final_path else 0,
                "record_counts": {
                    data_type: len(data) if isinstance(data, list) else 1
                    for data_type, data in export_data.items()
                },
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7)  # 7 day expiry
            }
            
        except Exception as e:
            logger.error(f"Error exporting data for user {user_id}: {str(e)}")
            raise
    
    def _serialize_behavior_data(
        self, 
        behavior_data: List[UserBehaviorData], 
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """Serialize behavior data for export."""
        serialized = []
        
        for data in behavior_data:
            item = {
                "id": data.id,
                "event_type": data.event_type.value if data.event_type else None,
                "page_url": data.page_url,
                "course_id": data.course_id,
                "chapter_id": data.chapter_id,
                "timestamp": data.timestamp.isoformat() if data.timestamp else None,
                "duration_seconds": data.duration_seconds,
                "engagement_score": data.engagement_score,
                "is_anonymized": data.is_anonymized,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            
            if include_metadata and data.metadata:
                item["metadata"] = data.metadata
            
            serialized.append(item)
        
        return serialized
    
    def _serialize_learning_patterns(
        self, 
        learning_patterns: List[LearningPattern], 
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """Serialize learning patterns for export."""
        serialized = []
        
        for pattern in learning_patterns:
            item = {
                "id": pattern.id,
                "pattern_type": pattern.pattern_type.value if pattern.pattern_type else None,
                "confidence_score": pattern.confidence_score,
                "preferred_content_types": pattern.preferred_content_types,
                "optimal_session_duration": pattern.optimal_session_duration,
                "difficulty_progression_rate": pattern.difficulty_progression_rate,
                "preferred_learning_times": pattern.preferred_learning_times,
                "average_attention_span": pattern.average_attention_span,
                "strong_topics": pattern.strong_topics,
                "challenging_topics": pattern.challenging_topics,
                "data_points_count": pattern.data_points_count,
                "last_calculated": pattern.last_calculated.isoformat() if pattern.last_calculated else None,
                "created_at": pattern.created_at.isoformat() if pattern.created_at else None,
                "updated_at": pattern.updated_at.isoformat() if pattern.updated_at else None
            }
            
            serialized.append(item)
        
        return serialized
    
    def _serialize_learning_profile(
        self, 
        learning_profile: UserLearningProfile, 
        include_metadata: bool
    ) -> Dict[str, Any]:
        """Serialize learning profile for export."""
        return {
            "id": learning_profile.id,
            "learning_style": learning_profile.learning_style.value if learning_profile.learning_style else None,
            "attention_span": learning_profile.attention_span,
            "preferred_difficulty": learning_profile.preferred_difficulty.value if learning_profile.preferred_difficulty else None,
            "completion_rate": learning_profile.completion_rate,
            "average_session_duration": learning_profile.average_session_duration,
            "total_learning_time": learning_profile.total_learning_time,
            "courses_completed": learning_profile.courses_completed,
            "engagement_score": learning_profile.engagement_score,
            "consistency_score": learning_profile.consistency_score,
            "challenge_preference": learning_profile.challenge_preference,
            "strong_topics": learning_profile.strong_topics,
            "challenging_topics": learning_profile.challenging_topics,
            "preferred_content_formats": learning_profile.preferred_content_formats,
            "current_difficulty_level": learning_profile.current_difficulty_level,
            "adaptation_rate": learning_profile.adaptation_rate,
            "last_updated": learning_profile.last_updated.isoformat() if learning_profile.last_updated else None,
            "created_at": learning_profile.created_at.isoformat() if learning_profile.created_at else None
        }
    
    def _serialize_engagement_metrics(
        self, 
        engagement_metrics: List[EngagementMetrics], 
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """Serialize engagement metrics for export."""
        serialized = []
        
        for metrics in engagement_metrics:
            item = {
                "id": metrics.id,
                "course_id": metrics.course_id,
                "chapter_id": metrics.chapter_id,
                "time_period_start": metrics.time_period_start.isoformat() if metrics.time_period_start else None,
                "time_period_end": metrics.time_period_end.isoformat() if metrics.time_period_end else None,
                "total_time_spent": metrics.total_time_spent,
                "interaction_count": metrics.interaction_count,
                "page_views": metrics.page_views,
                "completion_percentage": metrics.completion_percentage,
                "engagement_score": metrics.engagement_score,
                "focus_score": metrics.focus_score,
                "progress_velocity": metrics.progress_velocity,
                "calculation_version": metrics.calculation_version,
                "created_at": metrics.created_at.isoformat() if metrics.created_at else None
            }
            
            serialized.append(item)
        
        return serialized
    
    async def _create_json_export(
        self, 
        export_id: str, 
        user_id: str, 
        export_data: Dict[str, Any]
    ) -> str:
        """Create JSON export file."""
        filename = f"user_data_export_{user_id}_{export_id}.json"
        file_path = Path(tempfile.gettempdir()) / filename
        
        export_package = {
            "export_metadata": {
                "export_id": export_id,
                "user_id": user_id,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "format": "json",
                "data_types": list(export_data.keys())
            },
            "data": export_data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_package, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    async def _create_csv_export(
        self, 
        export_id: str, 
        user_id: str, 
        export_data: Dict[str, Any]
    ) -> List[str]:
        """Create CSV export files."""
        file_paths = []
        
        for data_type, data in export_data.items():
            if not data:
                continue
            
            filename = f"user_{data_type}_{user_id}_{export_id}.csv"
            file_path = Path(tempfile.gettempdir()) / filename
            
            if isinstance(data, list) and data:
                # Write list data to CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            elif isinstance(data, dict):
                # Write single record to CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writeheader()
                    writer.writerow(data)
            
            file_paths.append(str(file_path))
        
        return file_paths
    
    async def _create_zip_export(
        self, 
        export_id: str, 
        user_id: str, 
        file_paths: List[str]
    ) -> str:
        """Create ZIP file containing all export files."""
        zip_filename = f"user_data_export_{user_id}_{export_id}.zip"
        zip_path = Path(tempfile.gettempdir()) / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                zipf.write(file_path, Path(file_path).name)
        
        return str(zip_path)
    
    def get_aggregated_analytics_for_course_creator(
        self,
        db: Session,
        creator_user_id: str,
        course_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get aggregated analytics data for course creators.
        
        Args:
            db: Database session
            creator_user_id: User ID of the course creator
            course_id: Optional specific course ID
            days: Number of days to analyze
            
        Returns:
            Aggregated analytics data
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get courses by creator
        if course_id:
            # Verify creator owns the course
            course = courses_crud.get_course_by_id(db, course_id)
            if not course or course.user_id != creator_user_id:
                raise ValueError("Course not found or not owned by creator")
            course_ids = [course_id]
        else:
            # Get all courses by creator
            creator_courses = courses_crud.get_courses_by_user_id(db, creator_user_id)
            course_ids = [course.id for course in creator_courses]
        
        if not course_ids:
            return {
                "course_ids": [],
                "total_learners": 0,
                "engagement_summary": {},
                "learning_patterns": {},
                "completion_rates": {},
                "time_period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
            }
        
        # Get aggregated behavior data
        behavior_stats = self._get_course_behavior_stats(db, course_ids, start_date, end_date)
        
        # Get engagement metrics
        engagement_stats = self._get_course_engagement_stats(db, course_ids, start_date, end_date)
        
        # Get learning pattern insights
        learning_insights = self._get_course_learning_insights(db, course_ids)
        
        # Get completion rates
        completion_stats = self._get_course_completion_stats(db, course_ids, start_date, end_date)
        
        return {
            "course_ids": course_ids,
            "total_learners": behavior_stats.get("unique_learners", 0),
            "engagement_summary": {
                "total_sessions": behavior_stats.get("total_sessions", 0),
                "average_session_duration": behavior_stats.get("avg_session_duration", 0),
                "total_time_spent": behavior_stats.get("total_time_spent", 0),
                "average_engagement_score": engagement_stats.get("avg_engagement_score", 0.0)
            },
            "learning_patterns": learning_insights,
            "completion_rates": completion_stats,
            "behavior_trends": behavior_stats.get("daily_trends", []),
            "time_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }
    
    def _get_course_behavior_stats(
        self,
        db: Session,
        course_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get behavior statistics for courses."""
        # Get basic stats
        result = db.query(
            func.count(func.distinct(UserBehaviorData.user_id)).label('unique_learners'),
            func.count(func.distinct(UserBehaviorData.session_id)).label('total_sessions'),
            func.sum(UserBehaviorData.duration_seconds).label('total_time_spent'),
            func.avg(UserBehaviorData.duration_seconds).label('avg_session_duration')
        ).filter(
            and_(
                UserBehaviorData.course_id.in_(course_ids),
                UserBehaviorData.timestamp >= start_date,
                UserBehaviorData.timestamp <= end_date
            )
        ).first()
        
        # Get daily trends
        daily_trends = db.query(
            func.date(UserBehaviorData.timestamp).label('date'),
            func.count(func.distinct(UserBehaviorData.user_id)).label('unique_users'),
            func.count(UserBehaviorData.id).label('total_events')
        ).filter(
            and_(
                UserBehaviorData.course_id.in_(course_ids),
                UserBehaviorData.timestamp >= start_date,
                UserBehaviorData.timestamp <= end_date
            )
        ).group_by(
            func.date(UserBehaviorData.timestamp)
        ).order_by(
            func.date(UserBehaviorData.timestamp)
        ).all()
        
        return {
            "unique_learners": result.unique_learners or 0,
            "total_sessions": result.total_sessions or 0,
            "total_time_spent": result.total_time_spent or 0,
            "avg_session_duration": float(result.avg_session_duration or 0),
            "daily_trends": [
                {
                    "date": trend.date.isoformat() if trend.date else None,
                    "unique_users": trend.unique_users,
                    "total_events": trend.total_events
                }
                for trend in daily_trends
            ]
        }
    
    def _get_course_engagement_stats(
        self,
        db: Session,
        course_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get engagement statistics for courses."""
        result = db.query(
            func.avg(EngagementMetrics.engagement_score).label('avg_engagement_score'),
            func.avg(EngagementMetrics.focus_score).label('avg_focus_score'),
            func.avg(EngagementMetrics.completion_percentage).label('avg_completion_percentage')
        ).filter(
            and_(
                EngagementMetrics.course_id.in_(course_ids),
                EngagementMetrics.time_period_start >= start_date,
                EngagementMetrics.time_period_end <= end_date
            )
        ).first()
        
        return {
            "avg_engagement_score": float(result.avg_engagement_score or 0.0),
            "avg_focus_score": float(result.avg_focus_score or 0.0),
            "avg_completion_percentage": float(result.avg_completion_percentage or 0.0)
        }
    
    def _get_course_learning_insights(
        self,
        db: Session,
        course_ids: List[int]
    ) -> Dict[str, Any]:
        """Get learning pattern insights for courses."""
        # Get users who have engaged with these courses
        course_users = db.query(
            func.distinct(UserBehaviorData.user_id)
        ).filter(
            UserBehaviorData.course_id.in_(course_ids)
        ).subquery()
        
        # Get learning style distribution
        learning_styles = db.query(
            UserLearningProfile.learning_style,
            func.count(UserLearningProfile.id).label('count')
        ).filter(
            UserLearningProfile.user_id.in_(course_users)
        ).group_by(
            UserLearningProfile.learning_style
        ).all()
        
        # Get difficulty preferences
        difficulty_prefs = db.query(
            UserLearningProfile.preferred_difficulty,
            func.count(UserLearningProfile.id).label('count')
        ).filter(
            UserLearningProfile.user_id.in_(course_users)
        ).group_by(
            UserLearningProfile.preferred_difficulty
        ).all()
        
        return {
            "learning_style_distribution": {
                style.learning_style.value if style.learning_style else "unknown": style.count
                for style in learning_styles
            },
            "difficulty_preference_distribution": {
                pref.preferred_difficulty.value if pref.preferred_difficulty else "unknown": pref.count
                for pref in difficulty_prefs
            }
        }
    
    def _get_course_completion_stats(
        self,
        db: Session,
        course_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get completion statistics for courses."""
        completion_stats = {}
        
        for course_id in course_ids:
            # Get course starts and completions
            course_starts = db.query(UserBehaviorData).filter(
                and_(
                    UserBehaviorData.course_id == course_id,
                    UserBehaviorData.event_type == EventType.COURSE_START,
                    UserBehaviorData.timestamp >= start_date,
                    UserBehaviorData.timestamp <= end_date
                )
            ).count()
            
            course_completions = db.query(UserBehaviorData).filter(
                and_(
                    UserBehaviorData.course_id == course_id,
                    UserBehaviorData.event_type == EventType.COURSE_COMPLETE,
                    UserBehaviorData.timestamp >= start_date,
                    UserBehaviorData.timestamp <= end_date
                )
            ).count()
            
            completion_rate = (course_completions / course_starts) if course_starts > 0 else 0.0
            
            completion_stats[str(course_id)] = {
                "starts": course_starts,
                "completions": course_completions,
                "completion_rate": completion_rate
            }
        
        return completion_stats
    
    def get_admin_analytics_dashboard(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get aggregated analytics dashboard for administrators.
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            Admin dashboard analytics data
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Overall platform statistics
        total_users = db.query(func.count(func.distinct(UserBehaviorData.user_id))).scalar() or 0
        total_courses = db.query(func.count(func.distinct(UserBehaviorData.course_id))).scalar() or 0
        
        # Activity statistics
        activity_stats = db.query(
            func.count(UserBehaviorData.id).label('total_events'),
            func.count(func.distinct(UserBehaviorData.user_id)).label('active_users'),
            func.count(func.distinct(UserBehaviorData.session_id)).label('total_sessions'),
            func.sum(UserBehaviorData.duration_seconds).label('total_time_spent')
        ).filter(
            and_(
                UserBehaviorData.timestamp >= start_date,
                UserBehaviorData.timestamp <= end_date
            )
        ).first()
        
        # Learning style distribution
        learning_styles = db.query(
            UserLearningProfile.learning_style,
            func.count(UserLearningProfile.id).label('count')
        ).group_by(
            UserLearningProfile.learning_style
        ).all()
        
        # Privacy compliance statistics
        privacy_stats = db.query(
            func.count(UserBehaviorData.id).label('total_records'),
            func.sum(func.case([(UserBehaviorData.is_anonymized == True, 1)], else_=0)).label('anonymized_records')
        ).first()
        
        return {
            "platform_overview": {
                "total_users": total_users,
                "total_courses": total_courses,
                "active_users_period": activity_stats.active_users or 0,
                "total_sessions_period": activity_stats.total_sessions or 0
            },
            "activity_summary": {
                "total_events": activity_stats.total_events or 0,
                "total_time_spent_hours": (activity_stats.total_time_spent or 0) / 3600,
                "average_session_duration": (
                    (activity_stats.total_time_spent or 0) / (activity_stats.total_sessions or 1)
                ) / 60  # Convert to minutes
            },
            "learning_insights": {
                "learning_style_distribution": {
                    style.learning_style.value if style.learning_style else "unknown": style.count
                    for style in learning_styles
                }
            },
            "privacy_compliance": {
                "total_behavior_records": privacy_stats.total_records or 0,
                "anonymized_records": privacy_stats.anonymized_records or 0,
                "anonymization_rate": (
                    (privacy_stats.anonymized_records or 0) / (privacy_stats.total_records or 1)
                ) * 100
            },
            "time_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }