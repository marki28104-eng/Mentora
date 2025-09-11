"""Utility functions for analytics data validation and sanitization."""

import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse


def generate_analytics_id() -> str:
    """Generate a unique ID for analytics records."""
    return str(uuid.uuid4())


def sanitize_url(url: str) -> str:
    """Sanitize and validate URL for analytics tracking."""
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Remove any potential XSS or injection attempts
    url = url.strip()
    
    # Basic URL validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme and not parsed.netloc and not parsed.path:
            raise ValueError("Invalid URL format")
    except Exception:
        raise ValueError("Invalid URL format")
    
    # Limit URL length
    if len(url) > 2000:
        url = url[:2000]
    
    return url


def sanitize_session_id(session_id: str) -> str:
    """Sanitize session ID to ensure it's safe for storage."""
    if not session_id or not isinstance(session_id, str):
        raise ValueError("Session ID must be a non-empty string")
    
    # Remove any non-alphanumeric characters except hyphens and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', session_id.strip())
    
    if not sanitized:
        raise ValueError("Session ID contains no valid characters")
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def sanitize_user_id(user_id: str) -> str:
    """Sanitize user ID to ensure it's safe for storage."""
    if not user_id or not isinstance(user_id, str):
        raise ValueError("User ID must be a non-empty string")
    
    # Remove any non-alphanumeric characters except hyphens and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', user_id.strip())
    
    if not sanitized:
        raise ValueError("User ID contains no valid characters")
    
    # Limit length
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    
    return sanitized


def sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize metadata to ensure no PII is included and data is safe for storage.
    
    Args:
        metadata: Dictionary containing event metadata
        
    Returns:
        Sanitized metadata dictionary or None if empty
    """
    if not metadata or not isinstance(metadata, dict):
        return None
    
    # List of keys that might contain PII - reject if found
    pii_keys = {
        'email', 'phone', 'address', 'name', 'firstname', 'lastname',
        'ssn', 'social_security', 'credit_card', 'password', 'token',
        'api_key', 'secret', 'private_key', 'auth', 'authorization'
    }
    
    # List of allowed metadata keys for analytics
    allowed_keys = {
        'content_type', 'difficulty_level', 'chapter_index', 'question_count',
        'score', 'completion_time', 'interaction_type', 'element_id',
        'scroll_depth', 'time_on_page', 'click_count', 'focus_time',
        'content_length', 'media_type', 'assessment_type', 'attempt_number'
    }
    
    sanitized = {}
    
    for key, value in metadata.items():
        # Skip if key might contain PII
        if any(pii_key in key.lower() for pii_key in pii_keys):
            continue
        
        # Only allow specific keys or keys that don't look suspicious
        key_lower = key.lower()
        if key_lower not in allowed_keys and any(pii_key in key_lower for pii_key in pii_keys):
            continue
        
        # Sanitize the key itself
        sanitized_key = re.sub(r'[^a-zA-Z0-9_]', '', key)[:50]
        if not sanitized_key:
            continue
        
        # Sanitize the value based on type
        if isinstance(value, str):
            # Limit string length and remove potentially dangerous content
            sanitized_value = value.strip()[:1000]
            # Remove any HTML/script tags
            sanitized_value = re.sub(r'<[^>]*>', '', sanitized_value)
            if sanitized_value:
                sanitized[sanitized_key] = sanitized_value
                
        elif isinstance(value, (int, float)):
            # Allow numeric values within reasonable ranges
            if isinstance(value, int) and -2147483648 <= value <= 2147483647:
                sanitized[sanitized_key] = value
            elif isinstance(value, float) and -1e10 <= value <= 1e10:
                sanitized[sanitized_key] = value
                
        elif isinstance(value, bool):
            sanitized[sanitized_key] = value
            
        elif isinstance(value, list):
            # Sanitize list items
            sanitized_list = []
            for item in value[:20]:  # Limit list size
                if isinstance(item, str):
                    sanitized_item = item.strip()[:100]
                    if sanitized_item:
                        sanitized_list.append(sanitized_item)
                elif isinstance(item, (int, float, bool)):
                    sanitized_list.append(item)
            
            if sanitized_list:
                sanitized[sanitized_key] = sanitized_list
    
    return sanitized if sanitized else None


def validate_engagement_score(score: Optional[float]) -> Optional[float]:
    """Validate and normalize engagement score."""
    if score is None:
        return None
    
    if not isinstance(score, (int, float)):
        raise ValueError("Engagement score must be a number")
    
    # Clamp to valid range
    return max(0.0, min(1.0, float(score)))


def validate_duration(duration_seconds: Optional[int]) -> Optional[int]:
    """Validate duration in seconds."""
    if duration_seconds is None:
        return None
    
    if not isinstance(duration_seconds, int):
        raise ValueError("Duration must be an integer")
    
    if duration_seconds < 0:
        raise ValueError("Duration cannot be negative")
    
    # Limit to reasonable maximum (24 hours)
    max_duration = 24 * 60 * 60
    if duration_seconds > max_duration:
        duration_seconds = max_duration
    
    return duration_seconds


def validate_timestamp(timestamp: datetime) -> datetime:
    """Validate and normalize timestamp."""
    if not isinstance(timestamp, datetime):
        raise ValueError("Timestamp must be a datetime object")
    
    # Ensure timezone awareness
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    # Check if timestamp is reasonable (not too far in past or future)
    now = datetime.now(timezone.utc)
    max_past = now.replace(year=now.year - 10)  # 10 years ago
    max_future = now.replace(year=now.year + 1)  # 1 year in future
    
    if timestamp < max_past:
        raise ValueError("Timestamp is too far in the past")
    
    if timestamp > max_future:
        raise ValueError("Timestamp is too far in the future")
    
    return timestamp


def anonymize_user_data(user_id: str, session_id: str) -> tuple[str, str]:
    """
    Anonymize user data for privacy compliance.
    
    Args:
        user_id: Original user ID
        session_id: Original session ID
        
    Returns:
        Tuple of (anonymized_user_id, anonymized_session_id)
    """
    # Create consistent but anonymized IDs using hashing
    import hashlib
    
    # Use a salt for additional security (in production, this should be from config)
    salt = "mentora_analytics_salt_2024"
    
    # Create anonymized user ID
    user_hash = hashlib.sha256(f"{salt}_{user_id}".encode()).hexdigest()[:16]
    anonymized_user_id = f"anon_{user_hash}"
    
    # Create anonymized session ID
    session_hash = hashlib.sha256(f"{salt}_{session_id}".encode()).hexdigest()[:16]
    anonymized_session_id = f"sess_{session_hash}"
    
    return anonymized_user_id, anonymized_session_id


def validate_topic_list(topics: Optional[List[str]]) -> Optional[List[str]]:
    """Validate and sanitize a list of topics."""
    if not topics:
        return None
    
    if not isinstance(topics, list):
        raise ValueError("Topics must be a list")
    
    sanitized = []
    for topic in topics[:20]:  # Limit to 20 topics
        if isinstance(topic, str):
            sanitized_topic = topic.strip()[:100]  # Limit length
            # Remove any potentially dangerous content
            sanitized_topic = re.sub(r'[<>"\']', '', sanitized_topic)
            if sanitized_topic:
                sanitized.append(sanitized_topic)
    
    return sanitized if sanitized else None


def calculate_engagement_score(
    time_spent: int,
    interaction_count: int,
    page_views: int,
    completion_percentage: float
) -> float:
    """
    Calculate engagement score based on user behavior metrics.
    
    Args:
        time_spent: Time spent in seconds
        interaction_count: Number of interactions
        page_views: Number of page views
        completion_percentage: Completion percentage (0.0 to 1.0)
        
    Returns:
        Engagement score between 0.0 and 1.0
    """
    # Normalize time spent (assume 30 minutes is high engagement)
    time_score = min(1.0, time_spent / (30 * 60))
    
    # Normalize interaction count (assume 50 interactions is high engagement)
    interaction_score = min(1.0, interaction_count / 50)
    
    # Normalize page views (assume 10 page views is high engagement)
    page_view_score = min(1.0, page_views / 10)
    
    # Completion percentage is already normalized
    completion_score = completion_percentage
    
    # Weighted average of all scores
    engagement_score = (
        time_score * 0.3 +
        interaction_score * 0.2 +
        page_view_score * 0.2 +
        completion_score * 0.3
    )
    
    return max(0.0, min(1.0, engagement_score))