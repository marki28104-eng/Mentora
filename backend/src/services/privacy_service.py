"""
Privacy Service for handling GDPR compliance, data anonymization, and user consent management.

This service ensures that all analytics data collection and processing complies with
privacy regulations including GDPR, CCPA, and other data protection laws.
"""

import asyncio
import logging
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..db.crud import analytics_crud
from ..db.crud import users_crud
from ..db.models.db_analytics import (
    UserBehaviorData, LearningPattern, UserLearningProfile, EngagementMetrics
)
from ..db.models.db_user import User
from ..utils.analytics_utils import generate_analytics_id

logger = logging.getLogger(__name__)


class PrivacyService:
    """Service for managing privacy compliance and data protection."""
    
    def __init__(self):
        self.anonymization_salt = self._get_or_create_salt()
        
    def _get_or_create_salt(self) -> str:
        """Get or create a salt for anonymization hashing."""
        # In production, this should be stored securely (e.g., environment variable or key management service)
        return secrets.token_hex(32)
    
    def anonymize_user_id(self, user_id: str) -> str:
        """
        Create an anonymized version of a user ID using one-way hashing.
        
        Args:
            user_id: Original user ID
            
        Returns:
            Anonymized user ID that cannot be reversed
        """
        # Use SHA-256 with salt for one-way anonymization
        combined = f"{user_id}:{self.anonymization_salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]  # Use first 16 chars
    
    def anonymize_session_id(self, session_id: str) -> str:
        """
        Create an anonymized version of a session ID.
        
        Args:
            session_id: Original session ID
            
        Returns:
            Anonymized session ID
        """
        combined = f"{session_id}:{self.anonymization_salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:12]  # Use first 12 chars
    
    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove any potentially identifying information from metadata.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Sanitized metadata with PII removed
        """
        if not metadata:
            return {}
        
        # List of keys that might contain PII
        pii_keys = {
            'email', 'phone', 'address', 'name', 'firstname', 'lastname',
            'ssn', 'social_security', 'credit_card', 'password', 'token',
            'ip_address', 'user_agent', 'fingerprint', 'device_id'
        }
        
        sanitized = {}
        for key, value in metadata.items():
            # Skip keys that might contain PII
            if any(pii_key in key.lower() for pii_key in pii_keys):
                continue
            
            # Sanitize string values
            if isinstance(value, str):
                # Remove potential identifiers and limit length
                sanitized_value = value.strip()[:500]  # Limit to 500 chars
                
                # Skip if it looks like an email, phone, or other identifier
                if '@' in sanitized_value or sanitized_value.isdigit():
                    continue
                    
                sanitized[key] = sanitized_value
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, dict)) and len(str(value)) < 1000:
                # Include simple collections if they're not too large
                sanitized[key] = value
        
        return sanitized
    
    async def anonymize_user_behavior_data(
        self, 
        db: Session, 
        user_id: str,
        batch_size: int = 1000
    ) -> int:
        """
        Anonymize all behavior data for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to anonymize data for
            batch_size: Number of records to process at once
            
        Returns:
            Number of records anonymized
        """
        total_anonymized = 0
        offset = 0
        
        while True:
            # Get batch of user behavior data
            behavior_data = analytics_crud.get_user_behavior_data(
                db=db,
                user_id=user_id,
                limit=batch_size,
                offset=offset
            )
            
            if not behavior_data:
                break
            
            for data in behavior_data:
                if not data.is_anonymized:
                    # Anonymize the data
                    anonymized_user_id = self.anonymize_user_id(data.user_id)
                    anonymized_session_id = self.anonymize_session_id(data.session_id)
                    sanitized_metadata = self.sanitize_metadata(data.metadata or {})
                    
                    # Update the record
                    analytics_crud.update_user_behavior_data(
                        db=db,
                        behavior_data=data,
                        update_data={
                            "user_id": anonymized_user_id,
                            "session_id": anonymized_session_id,
                            "metadata": sanitized_metadata,
                            "is_anonymized": True
                        }
                    )
                    total_anonymized += 1
            
            offset += batch_size
            
            # Break if we got fewer records than batch_size (end of data)
            if len(behavior_data) < batch_size:
                break
        
        logger.info(f"Anonymized {total_anonymized} behavior data records for user {user_id}")
        return total_anonymized
    
    async def delete_user_analytics_data(
        self, 
        db: Session, 
        user_id: str,
        hard_delete: bool = False
    ) -> Dict[str, int]:
        """
        Delete all analytics data for a user (GDPR right to be forgotten).
        
        Args:
            db: Database session
            user_id: User ID to delete data for
            hard_delete: If True, permanently delete. If False, anonymize instead.
            
        Returns:
            Dictionary with counts of deleted/anonymized records
        """
        deletion_counts = {
            "behavior_data": 0,
            "learning_patterns": 0,
            "learning_profiles": 0,
            "engagement_metrics": 0
        }
        
        try:
            if hard_delete:
                # Permanently delete all analytics data
                deletion_counts["behavior_data"] = analytics_crud.delete_user_behavior_data(db, user_id)
                deletion_counts["learning_patterns"] = analytics_crud.delete_user_learning_patterns(db, user_id)
                deletion_counts["learning_profiles"] = analytics_crud.delete_user_learning_profile(db, user_id)
                deletion_counts["engagement_metrics"] = analytics_crud.delete_user_engagement_metrics(db, user_id)
            else:
                # Anonymize data instead of deleting (preserves aggregate analytics)
                deletion_counts["behavior_data"] = await self.anonymize_user_behavior_data(db, user_id)
                
                # For learning patterns and profiles, we can anonymize the user_id
                learning_patterns = analytics_crud.get_learning_patterns_by_user(db, user_id)
                for pattern in learning_patterns:
                    analytics_crud.update_learning_pattern(
                        db, pattern, {"user_id": self.anonymize_user_id(user_id)}
                    )
                    deletion_counts["learning_patterns"] += 1
                
                learning_profile = analytics_crud.get_user_learning_profile(db, user_id)
                if learning_profile:
                    analytics_crud.update_user_learning_profile(
                        db, learning_profile, {"user_id": self.anonymize_user_id(user_id)}
                    )
                    deletion_counts["learning_profiles"] = 1
                
                engagement_metrics = analytics_crud.get_user_engagement_metrics(db, user_id)
                for metric in engagement_metrics:
                    analytics_crud.update_engagement_metrics(
                        db, metric, {"user_id": self.anonymize_user_id(user_id)}
                    )
                    deletion_counts["engagement_metrics"] += 1
            
            db.commit()
            logger.info(f"{'Deleted' if hard_delete else 'Anonymized'} analytics data for user {user_id}: {deletion_counts}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error {'deleting' if hard_delete else 'anonymizing'} analytics data for user {user_id}: {str(e)}")
            raise
        
        return deletion_counts
    
    def check_user_consent(self, db: Session, user_id: str) -> Dict[str, bool]:
        """
        Check user consent status for different types of data collection.
        
        Args:
            db: Database session
            user_id: User ID to check consent for
            
        Returns:
            Dictionary with consent status for different data types
        """
        user = users_crud.get_user_by_id(db, user_id)
        if not user:
            return {
                "analytics_collection": False,
                "personalization": False,
                "performance_tracking": False,
                "content_recommendations": False
            }
        
        # Check user preferences/settings for consent
        # This assumes the User model has consent fields - you may need to add these
        user_settings = getattr(user, 'settings', {}) or {}
        
        return {
            "analytics_collection": user_settings.get("analytics_consent", False),
            "personalization": user_settings.get("personalization_consent", False),
            "performance_tracking": user_settings.get("performance_consent", False),
            "content_recommendations": user_settings.get("recommendations_consent", False)
        }
    
    def update_user_consent(
        self, 
        db: Session, 
        user_id: str, 
        consent_data: Dict[str, bool]
    ) -> bool:
        """
        Update user consent preferences.
        
        Args:
            db: Database session
            user_id: User ID to update consent for
            consent_data: Dictionary with consent preferences
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = users_crud.get_user_by_id(db, user_id)
            if not user:
                return False
            
            # Update user settings with consent preferences
            current_settings = getattr(user, 'settings', {}) or {}
            current_settings.update({
                "analytics_consent": consent_data.get("analytics_collection", False),
                "personalization_consent": consent_data.get("personalization", False),
                "performance_consent": consent_data.get("performance_tracking", False),
                "recommendations_consent": consent_data.get("content_recommendations", False),
                "consent_updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Update user record
            users_crud.update_user(db, user, {"settings": current_settings})
            
            # If user revoked analytics consent, anonymize their existing data
            if not consent_data.get("analytics_collection", False):
                asyncio.create_task(self.anonymize_user_behavior_data(db, user_id))
            
            db.commit()
            logger.info(f"Updated consent preferences for user {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating consent for user {user_id}: {str(e)}")
            return False
    
    def get_data_retention_policy(self) -> Dict[str, int]:
        """
        Get data retention policy in days for different data types.
        
        Returns:
            Dictionary with retention periods in days
        """
        return {
            "behavior_data": 365,  # 1 year
            "learning_patterns": 730,  # 2 years
            "learning_profiles": 1095,  # 3 years
            "engagement_metrics": 365,  # 1 year
            "anonymized_data": -1  # Keep indefinitely
        }
    
    async def cleanup_expired_data(self, db: Session) -> Dict[str, int]:
        """
        Clean up expired data according to retention policy.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with counts of cleaned up records
        """
        retention_policy = self.get_data_retention_policy()
        cleanup_counts = {}
        
        try:
            # Clean up behavior data
            if retention_policy["behavior_data"] > 0:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_policy["behavior_data"])
                cleanup_counts["behavior_data"] = analytics_crud.delete_behavior_data_before_date(db, cutoff_date)
            
            # Clean up engagement metrics
            if retention_policy["engagement_metrics"] > 0:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_policy["engagement_metrics"])
                cleanup_counts["engagement_metrics"] = analytics_crud.delete_engagement_metrics_before_date(db, cutoff_date)
            
            # Learning patterns and profiles have longer retention periods
            # They are typically kept longer as they represent valuable learning insights
            
            db.commit()
            logger.info(f"Cleaned up expired data: {cleanup_counts}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up expired data: {str(e)}")
            raise
        
        return cleanup_counts
    
    def validate_data_collection_consent(self, db: Session, user_id: str, data_type: str) -> bool:
        """
        Validate that user has given consent for specific type of data collection.
        
        Args:
            db: Database session
            user_id: User ID to check
            data_type: Type of data being collected
            
        Returns:
            True if consent is given, False otherwise
        """
        consent_status = self.check_user_consent(db, user_id)
        
        consent_mapping = {
            "behavior_tracking": "analytics_collection",
            "learning_analytics": "personalization",
            "performance_metrics": "performance_tracking",
            "recommendations": "content_recommendations"
        }
        
        consent_key = consent_mapping.get(data_type, "analytics_collection")
        return consent_status.get(consent_key, False)
    
    def generate_privacy_report(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Generate a privacy report for a user showing what data is collected.
        
        Args:
            db: Database session
            user_id: User ID to generate report for
            
        Returns:
            Dictionary with privacy report data
        """
        try:
            # Get consent status
            consent_status = self.check_user_consent(db, user_id)
            
            # Get data counts
            behavior_data_count = analytics_crud.count_user_behavior_data(db, user_id)
            learning_patterns_count = len(analytics_crud.get_learning_patterns_by_user(db, user_id))
            
            learning_profile = analytics_crud.get_user_learning_profile(db, user_id)
            has_learning_profile = learning_profile is not None
            
            engagement_metrics_count = len(analytics_crud.get_user_engagement_metrics(db, user_id))
            
            # Get data age ranges
            oldest_data = analytics_crud.get_oldest_user_behavior_data(db, user_id)
            newest_data = analytics_crud.get_newest_user_behavior_data(db, user_id)
            
            return {
                "user_id": user_id,
                "consent_status": consent_status,
                "data_summary": {
                    "behavior_events": behavior_data_count,
                    "learning_patterns": learning_patterns_count,
                    "has_learning_profile": has_learning_profile,
                    "engagement_metrics": engagement_metrics_count
                },
                "data_age": {
                    "oldest_record": oldest_data.created_at if oldest_data else None,
                    "newest_record": newest_data.created_at if newest_data else None
                },
                "retention_policy": self.get_data_retention_policy(),
                "anonymization_status": {
                    "anonymized_records": analytics_crud.count_anonymized_behavior_data(db, user_id),
                    "total_records": behavior_data_count
                },
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error generating privacy report for user {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "error": "Unable to generate privacy report",
                "generated_at": datetime.now(timezone.utc)
            }