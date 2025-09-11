"""Pydantic schemas for privacy and data management operations."""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ConsentPreferences(BaseModel):
    """Schema for user consent preferences."""
    analytics_collection: bool = Field(False, description="Consent for analytics data collection")
    personalization: bool = Field(False, description="Consent for personalization features")
    performance_tracking: bool = Field(False, description="Consent for performance tracking")
    content_recommendations: bool = Field(False, description="Consent for content recommendations")


class ConsentUpdate(BaseModel):
    """Schema for updating user consent preferences."""
    analytics_collection: Optional[bool] = None
    personalization: Optional[bool] = None
    performance_tracking: Optional[bool] = None
    content_recommendations: Optional[bool] = None


class ConsentStatus(ConsentPreferences):
    """Schema for consent status response."""
    user_id: str
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DataDeletionRequest(BaseModel):
    """Schema for data deletion requests."""
    user_id: str = Field(..., min_length=1, max_length=50)
    deletion_type: str = Field(..., regex="^(hard_delete|anonymize)$")
    reason: Optional[str] = Field(None, max_length=500)
    confirm_deletion: bool = Field(..., description="User must confirm deletion")

    @field_validator('confirm_deletion')
    @classmethod
    def validate_confirmation(cls, v: bool) -> bool:
        """Ensure user has confirmed the deletion."""
        if not v:
            raise ValueError("User must confirm deletion request")
        return v


class DataDeletionResponse(BaseModel):
    """Schema for data deletion response."""
    user_id: str
    deletion_type: str
    status: str  # "completed", "failed", "in_progress"
    deleted_records: Dict[str, int]
    processed_at: datetime
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DataExportRequest(BaseModel):
    """Schema for data export requests."""
    user_id: str = Field(..., min_length=1, max_length=50)
    data_types: List[str] = Field(
        default=["behavior_data", "learning_patterns", "learning_profile", "engagement_metrics"],
        description="Types of data to export"
    )
    format: str = Field("json", regex="^(json|csv)$")
    include_metadata: bool = Field(True, description="Include metadata in export")

    @field_validator('data_types')
    @classmethod
    def validate_data_types(cls, v: List[str]) -> List[str]:
        """Validate data types are supported."""
        valid_types = {
            "behavior_data", "learning_patterns", "learning_profile", 
            "engagement_metrics", "consent_history"
        }
        
        for data_type in v:
            if data_type not in valid_types:
                raise ValueError(f"Unsupported data type: {data_type}")
        
        return v


class DataExportResponse(BaseModel):
    """Schema for data export response."""
    user_id: str
    export_id: str
    status: str  # "completed", "failed", "in_progress"
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    file_size: Optional[int] = None
    created_at: datetime
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PrivacyReport(BaseModel):
    """Schema for privacy report response."""
    user_id: str
    consent_status: ConsentPreferences
    data_summary: Dict[str, Any]
    data_age: Dict[str, Optional[datetime]]
    retention_policy: Dict[str, int]
    anonymization_status: Dict[str, int]
    generated_at: datetime
    error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AnonymizationRequest(BaseModel):
    """Schema for data anonymization requests."""
    user_id: str = Field(..., min_length=1, max_length=50)
    data_types: List[str] = Field(
        default=["behavior_data"],
        description="Types of data to anonymize"
    )
    batch_size: int = Field(1000, ge=100, le=10000, description="Batch size for processing")


class AnonymizationResponse(BaseModel):
    """Schema for anonymization response."""
    user_id: str
    anonymized_records: Dict[str, int]
    status: str  # "completed", "failed", "in_progress"
    processed_at: datetime
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RetentionPolicyUpdate(BaseModel):
    """Schema for updating data retention policies."""
    behavior_data_days: Optional[int] = Field(None, ge=1, le=3650)  # Max 10 years
    learning_patterns_days: Optional[int] = Field(None, ge=1, le=3650)
    learning_profiles_days: Optional[int] = Field(None, ge=1, le=3650)
    engagement_metrics_days: Optional[int] = Field(None, ge=1, le=3650)


class RetentionPolicy(BaseModel):
    """Schema for retention policy response."""
    behavior_data: int  # days
    learning_patterns: int  # days
    learning_profiles: int  # days
    engagement_metrics: int  # days
    anonymized_data: int  # -1 for indefinite
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DataCleanupRequest(BaseModel):
    """Schema for data cleanup requests."""
    dry_run: bool = Field(True, description="If true, only report what would be deleted")
    force_cleanup: bool = Field(False, description="Force cleanup even if recent")


class DataCleanupResponse(BaseModel):
    """Schema for data cleanup response."""
    cleanup_counts: Dict[str, int]
    dry_run: bool
    processed_at: datetime
    next_cleanup_date: Optional[datetime] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PrivacyAuditLog(BaseModel):
    """Schema for privacy audit log entries."""
    id: str
    user_id: str
    action: str  # "consent_update", "data_deletion", "data_export", "anonymization"
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    status: str  # "success", "failed", "pending"

    model_config = ConfigDict(from_attributes=True)


class PrivacySettings(BaseModel):
    """Schema for privacy settings configuration."""
    auto_anonymize_after_days: int = Field(365, ge=30, le=3650)
    require_explicit_consent: bool = Field(True)
    allow_data_export: bool = Field(True)
    retention_policy_enforcement: bool = Field(True)
    audit_log_retention_days: int = Field(2555, ge=365, le=3650)  # 7 years default


class PrivacySettingsUpdate(BaseModel):
    """Schema for updating privacy settings."""
    auto_anonymize_after_days: Optional[int] = Field(None, ge=30, le=3650)
    require_explicit_consent: Optional[bool] = None
    allow_data_export: Optional[bool] = None
    retention_policy_enforcement: Optional[bool] = None
    audit_log_retention_days: Optional[int] = Field(None, ge=365, le=3650)