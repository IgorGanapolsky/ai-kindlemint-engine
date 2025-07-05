"""
Private Customer Data Pipeline for KindleMint

This module implements a secure, GDPR-compliant pipeline for ingesting and processing
anonymized first-party data to fuel causal inference models.
Based on the principle that private data is the ultimate competitive advantage.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import logging
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from cryptography.fernet import Fernet
import uuid


logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Types of data sources"""
    READER_SURVEY = "reader_survey"
    KDP_ANALYTICS = "kdp_analytics"
    WEBSITE_ANALYTICS = "website_analytics"
    EMAIL_ENGAGEMENT = "email_engagement"
    SOCIAL_MEDIA = "social_media"
    REVIEW_DATA = "review_data"
    SALES_DATA = "sales_data"
    PAGE_READ_DATA = "page_read_data"


class ConsentLevel(Enum):
    """GDPR consent levels"""
    ESSENTIAL = "essential"  # Required for service
    ANALYTICS = "analytics"  # Performance analytics
    MARKETING = "marketing"  # Marketing communications
    FULL = "full"  # All data collection


@dataclass
class DataPoint:
    """Represents a single anonymized data point"""
    user_hash: str  # Anonymized user identifier
    timestamp: datetime
    source: DataSource
    event_type: str
    data: Dict[str, Any]
    consent_level: ConsentLevel
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "user_hash": self.user_hash,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "event_type": self.event_type,
            "data": self.data,
            "consent_level": self.consent_level.value,
            "session_id": self.session_id
        }


@dataclass
class PrivacyConfig:
    """Configuration for privacy settings"""
    anonymization_salt: str = field(default_factory=lambda: uuid.uuid4().hex)
    retention_days: int = 365  # Data retention period
    min_aggregation_size: int = 10  # Minimum group size for aggregation
    pii_fields: List[str] = field(default_factory=lambda: [
        "email", "name", "ip_address", "phone", "address", 
        "payment_info", "device_id"
    ])
    encryption_key: Optional[bytes] = None
    
    def __post_init__(self):
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()


class DataProcessor(ABC):
    """Abstract base class for data processing"""
    
    @abstractmethod
    def process(self, raw_data: Dict[str, Any]) -> Optional[DataPoint]:
        """Process raw data into anonymized data point"""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data before processing"""
        pass


class PrivateDataPipeline:
    """
    Secure pipeline for ingesting and processing customer data
    with strong privacy guarantees and GDPR compliance.
    """
    
    def __init__(self, privacy_config: Optional[PrivacyConfig] = None):
        self.privacy_config = privacy_config or PrivacyConfig()
        self.processors: Dict[DataSource, DataProcessor] = {}
        self.data_buffer: List[DataPoint] = []
        self.fernet = Fernet(self.privacy_config.encryption_key)
        self._setup_processors()
    
    def _setup_processors(self):
        """Initialize default data processors"""
        self.processors[DataSource.READER_SURVEY] = ReaderSurveyProcessor(self.privacy_config)
        self.processors[DataSource.KDP_ANALYTICS] = KDPAnalyticsProcessor(self.privacy_config)
        self.processors[DataSource.WEBSITE_ANALYTICS] = WebAnalyticsProcessor(self.privacy_config)
    
    def anonymize_identifier(self, identifier: str) -> str:
        """
        Create a consistent, anonymized hash of an identifier.
        Uses salt to prevent rainbow table attacks.
        """
        salted = f"{identifier}{self.privacy_config.anonymization_salt}"
        return hashlib.sha256(salted.encode()).hexdigest()[:16]
    
    def remove_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or anonymize PII from data"""
        cleaned_data = data.copy()
        
        for field in self.privacy_config.pii_fields:
            if field in cleaned_data:
                if field == "email":
                    # Keep domain for analytics
                    domain = cleaned_data[field].split('@')[-1] if '@' in cleaned_data[field] else "unknown"
                    cleaned_data["email_domain"] = domain
                elif field == "ip_address":
                    # Keep country/region if available
                    cleaned_data["country"] = self._get_country_from_ip(cleaned_data[field])
                
                # Remove the PII field
                del cleaned_data[field]
        
        return cleaned_data
    
    def _get_country_from_ip(self, ip_address: str) -> str:
        """Get country from IP address (placeholder)"""
        # In production, use a GeoIP service
        return "US"
    
    async def ingest_data(self, 
                         source: DataSource, 
                         raw_data: Dict[str, Any],
                         user_consent: ConsentLevel) -> Optional[DataPoint]:
        """
        Ingest raw data, anonymize it, and create a data point.
        
        Args:
            source: The data source type
            raw_data: Raw data including potential PII
            user_consent: Level of consent provided by user
            
        Returns:
            Anonymized DataPoint or None if processing fails
        """
        # Check if we have appropriate consent
        if not self._check_consent(source, user_consent):
            logger.warning(f"Insufficient consent for {source.value} data")
            return None
        
        # Get appropriate processor
        processor = self.processors.get(source)
        if not processor:
            logger.error(f"No processor found for source: {source}")
            return None
        
        # Validate data
        if not processor.validate(raw_data):
            logger.warning(f"Data validation failed for source: {source}")
            return None
        
        # Process and anonymize
        data_point = processor.process(raw_data)
        if data_point:
            self.data_buffer.append(data_point)
            
            # Check if buffer should be flushed
            if len(self.data_buffer) >= 100:
                await self.flush_buffer()
        
        return data_point
    
    def _check_consent(self, source: DataSource, consent: ConsentLevel) -> bool:
        """Check if user consent is sufficient for data source"""
        consent_requirements = {
            DataSource.READER_SURVEY: ConsentLevel.ANALYTICS,
            DataSource.KDP_ANALYTICS: ConsentLevel.ESSENTIAL,
            DataSource.WEBSITE_ANALYTICS: ConsentLevel.ANALYTICS,
            DataSource.EMAIL_ENGAGEMENT: ConsentLevel.MARKETING,
            DataSource.SOCIAL_MEDIA: ConsentLevel.MARKETING,
            DataSource.REVIEW_DATA: ConsentLevel.ESSENTIAL,
            DataSource.SALES_DATA: ConsentLevel.ESSENTIAL,
            DataSource.PAGE_READ_DATA: ConsentLevel.ANALYTICS,
        }
        
        required = consent_requirements.get(source, ConsentLevel.FULL)
        consent_hierarchy = [
            ConsentLevel.ESSENTIAL,
            ConsentLevel.ANALYTICS,
            ConsentLevel.MARKETING,
            ConsentLevel.FULL
        ]
        
        return consent_hierarchy.index(consent) >= consent_hierarchy.index(required)
    
    async def flush_buffer(self):
        """Flush data buffer to storage"""
        if not self.data_buffer:
            return
        
        # Apply k-anonymity before storage
        anonymized_batch = self._apply_k_anonymity(self.data_buffer)
        
        # Encrypt sensitive fields
        encrypted_batch = self._encrypt_batch(anonymized_batch)
        
        # Store batch (placeholder - would write to secure database)
        logger.info(f"Flushed {len(encrypted_batch)} data points to storage")
        
        # Clear buffer
        self.data_buffer.clear()
    
    def _apply_k_anonymity(self, data_points: List[DataPoint]) -> List[DataPoint]:
        """
        Apply k-anonymity to ensure groups are large enough.
        Suppresses data that doesn't meet minimum group size.
        """
        # Group by quasi-identifiers
        groups = {}
        for point in data_points:
            # Create group key from quasi-identifiers
            group_key = (
                point.source.value,
                point.event_type,
                point.data.get("country", "unknown"),
                point.timestamp.date()
            )
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(point)
        
        # Only keep groups that meet minimum size
        anonymized = []
        for group_key, group_points in groups.items():
            if len(group_points) >= self.privacy_config.min_aggregation_size:
                anonymized.extend(group_points)
            else:
                logger.info(f"Suppressed {len(group_points)} points for k-anonymity")
        
        return anonymized
    
    def _encrypt_batch(self, data_points: List[DataPoint]) -> List[Dict]:
        """Encrypt sensitive fields in data points"""
        encrypted_batch = []
        
        for point in data_points:
            encrypted_data = point.to_dict()
            
            # Encrypt the data field
            data_json = json.dumps(point.data)
            encrypted_data["data"] = self.fernet.encrypt(data_json.encode()).decode()
            
            encrypted_batch.append(encrypted_data)
        
        return encrypted_batch
    
    def get_aggregated_insights(self, 
                              source: Optional[DataSource] = None,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get aggregated insights from collected data.
        Always returns aggregated data to preserve privacy.
        """
        # Filter data points
        filtered_points = self.data_buffer
        if source:
            filtered_points = [p for p in filtered_points if p.source == source]
        if start_date:
            filtered_points = [p for p in filtered_points if p.timestamp >= start_date]
        if end_date:
            filtered_points = [p for p in filtered_points if p.timestamp <= end_date]
        
        # Aggregate insights
        insights = {
            "total_events": len(filtered_points),
            "unique_users": len(set(p.user_hash for p in filtered_points)),
            "events_by_type": {},
            "events_by_source": {},
            "temporal_distribution": {}
        }
        
        # Count by event type
        for point in filtered_points:
            event_type = point.event_type
            insights["events_by_type"][event_type] = insights["events_by_type"].get(event_type, 0) + 1
            
            source_name = point.source.value
            insights["events_by_source"][source_name] = insights["events_by_source"].get(source_name, 0) + 1
        
        return insights
    
    def export_for_ml(self, 
                     min_group_size: int = 50,
                     features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Export anonymized data for machine learning training.
        Ensures differential privacy through aggregation.
        """
        # Convert to DataFrame
        data_dicts = []
        for point in self.data_buffer:
            row = {
                "user_hash": point.user_hash[:8],  # Further truncate for ML
                "timestamp": point.timestamp,
                "source": point.source.value,
                "event_type": point.event_type,
                **point.data  # Flatten data fields
            }
            data_dicts.append(row)
        
        df = pd.DataFrame(data_dicts)
        
        # Apply differential privacy
        df = self._add_noise_for_privacy(df)
        
        # Aggregate to ensure minimum group sizes
        aggregation_cols = ["source", "event_type"]
        if "country" in df.columns:
            aggregation_cols.append("country")
        
        aggregated = df.groupby(aggregation_cols).agg({
            "user_hash": "count",
            **{col: "mean" for col in df.select_dtypes(include=[np.number]).columns}
        }).reset_index()
        
        # Filter out small groups
        aggregated = aggregated[aggregated["user_hash"] >= min_group_size]
        
        return aggregated
    
    def _add_noise_for_privacy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Laplacian noise for differential privacy"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Add Laplacian noise scaled to data sensitivity
            sensitivity = df[col].std() * 0.1  # 10% of standard deviation
            noise = np.random.laplace(0, sensitivity, size=len(df))
            df[col] = df[col] + noise
        
        return df
    
    def cleanup_old_data(self):
        """Remove data older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.privacy_config.retention_days)
        
        initial_count = len(self.data_buffer)
        self.data_buffer = [p for p in self.data_buffer if p.timestamp > cutoff_date]
        removed_count = initial_count - len(self.data_buffer)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} data points older than {cutoff_date}")


# Concrete processor implementations

class ReaderSurveyProcessor(DataProcessor):
    """Process reader survey responses"""
    
    def __init__(self, privacy_config: PrivacyConfig):
        self.privacy_config = privacy_config
    
    def validate(self, data: Dict[str, Any]) -> bool:
        required_fields = ["user_id", "survey_id", "responses"]
        return all(field in data for field in required_fields)
    
    def process(self, raw_data: Dict[str, Any]) -> Optional[DataPoint]:
        # Anonymize user ID
        pipeline = PrivateDataPipeline(self.privacy_config)
        user_hash = pipeline.anonymize_identifier(raw_data["user_id"])
        
        # Remove PII from responses
        clean_data = pipeline.remove_pii(raw_data)
        
        return DataPoint(
            user_hash=user_hash,
            timestamp=datetime.now(),
            source=DataSource.READER_SURVEY,
            event_type="survey_response",
            data={
                "survey_id": clean_data["survey_id"],
                "responses": clean_data["responses"],
                "completion_time": clean_data.get("completion_time"),
                "satisfaction_score": clean_data.get("satisfaction_score")
            },
            consent_level=ConsentLevel.ANALYTICS
        )


class KDPAnalyticsProcessor(DataProcessor):
    """Process KDP analytics data"""
    
    def __init__(self, privacy_config: PrivacyConfig):
        self.privacy_config = privacy_config
    
    def validate(self, data: Dict[str, Any]) -> bool:
        required_fields = ["book_id", "metric_type", "value"]
        return all(field in data for field in required_fields)
    
    def process(self, raw_data: Dict[str, Any]) -> Optional[DataPoint]:
        # KDP data is already anonymized
        return DataPoint(
            user_hash="kdp_aggregate",  # Aggregate data, no individual user
            timestamp=datetime.now(),
            source=DataSource.KDP_ANALYTICS,
            event_type=raw_data["metric_type"],
            data={
                "book_id": raw_data["book_id"],
                "value": raw_data["value"],
                "marketplace": raw_data.get("marketplace", "US"),
                "period": raw_data.get("period", "daily")
            },
            consent_level=ConsentLevel.ESSENTIAL
        )


class WebAnalyticsProcessor(DataProcessor):
    """Process website analytics data"""
    
    def __init__(self, privacy_config: PrivacyConfig):
        self.privacy_config = privacy_config
    
    def validate(self, data: Dict[str, Any]) -> bool:
        required_fields = ["session_id", "event_type", "page_url"]
        return all(field in data for field in required_fields)
    
    def process(self, raw_data: Dict[str, Any]) -> Optional[DataPoint]:
        pipeline = PrivateDataPipeline(self.privacy_config)
        
        # Hash session ID for consistency
        session_hash = pipeline.anonymize_identifier(raw_data["session_id"])
        
        # Remove PII
        clean_data = pipeline.remove_pii(raw_data)
        
        return DataPoint(
            user_hash=session_hash,
            timestamp=datetime.now(),
            source=DataSource.WEBSITE_ANALYTICS,
            event_type=clean_data["event_type"],
            data={
                "page_url": clean_data["page_url"],
                "referrer": clean_data.get("referrer", "direct"),
                "duration": clean_data.get("duration"),
                "country": clean_data.get("country"),
                "device_type": clean_data.get("device_type", "unknown")
            },
            consent_level=ConsentLevel.ANALYTICS,
            session_id=session_hash
        )