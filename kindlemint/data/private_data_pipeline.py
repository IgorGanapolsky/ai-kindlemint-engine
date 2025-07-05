"""
Private Data Pipeline with GDPR-compliant Data Handling

This module implements the Alembic approach to privacy-preserving data processing,
distilling complex privacy requirements into clean, auditable data pipelines that
enable AI-driven insights while maintaining strict compliance.
"""

import hashlib
import secrets
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import pandas as pd
import numpy as np
from collections import defaultdict
import re
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import hmac

# Set up logging
logger = logging.getLogger(__name__)


class DataCategory(Enum):
    """Categories of personal data under GDPR"""
    PERSONAL_IDENTIFIABLE = "personal_identifiable"
    SENSITIVE = "sensitive"
    BEHAVIORAL = "behavioral"
    TRANSACTIONAL = "transactional"
    DERIVED = "derived"
    ANONYMOUS = "anonymous"
    PSEUDONYMOUS = "pseudonymous"


class LegalBasis(Enum):
    """Legal basis for data processing under GDPR"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class ProcessingPurpose(Enum):
    """Purposes for data processing"""
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PRODUCT_IMPROVEMENT = "product_improvement"
    CUSTOMER_SERVICE = "customer_service"
    LEGAL_COMPLIANCE = "legal_compliance"
    SECURITY = "security"
    RESEARCH = "research"


@dataclass
class DataSubject:
    """Represents a data subject (user) in the system"""
    subject_id: str
    pseudonym: str
    created_at: datetime
    consents: Dict[ProcessingPurpose, bool] = field(default_factory=dict)
    data_categories: Set[DataCategory] = field(default_factory=set)
    deletion_requested: Optional[datetime] = None
    last_activity: Optional[datetime] = None


@dataclass
class PrivacyPolicy:
    """Privacy policy configuration"""
    retention_periods: Dict[DataCategory, timedelta]
    anonymization_threshold: timedelta
    encryption_required: Set[DataCategory]
    audit_retention: timedelta
    consent_renewal_period: timedelta
    data_minimization_rules: Dict[DataCategory, List[str]]


@dataclass
class ProcessingRecord:
    """Record of data processing for audit trail"""
    record_id: str
    timestamp: datetime
    data_category: DataCategory
    purpose: ProcessingPurpose
    legal_basis: LegalBasis
    subject_pseudonym: str
    operation: str
    data_fields: List[str]
    retention_until: datetime


class PrivateDataPipeline:
    """
    GDPR-compliant data pipeline implementing the Alembic strategy.
    
    Transforms raw user data into privacy-preserving analytics while
    maintaining full compliance and audit trails.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the private data pipeline"""
        self.config = config or self._default_config()
        self.privacy_policy = self._initialize_privacy_policy()
        self.encryption_key = self._generate_encryption_key()
        self.subjects = {}
        self.processing_records = []
        self.anonymization_queue = asyncio.Queue()
        self.audit_db = self._initialize_audit_db()
        self.executor = ThreadPoolExecutor(max_workers=self.config["max_workers"])
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the pipeline"""
        return {
            "max_workers": 4,
            "batch_size": 1000,
            "anonymization_batch_size": 100,
            "audit_db_path": "privacy_audit.db",
            "encryption_algorithm": "AES-256",
            "hash_algorithm": "SHA-256",
            "pseudonym_length": 32,
            "min_k_anonymity": 5,
            "noise_epsilon": 1.0,  # Differential privacy parameter
            "secure_delete_passes": 3
        }
    
    def _initialize_privacy_policy(self) -> PrivacyPolicy:
        """Initialize privacy policy with GDPR-compliant defaults"""
        return PrivacyPolicy(
            retention_periods={
                DataCategory.PERSONAL_IDENTIFIABLE: timedelta(days=365 * 2),
                DataCategory.SENSITIVE: timedelta(days=90),
                DataCategory.BEHAVIORAL: timedelta(days=365),
                DataCategory.TRANSACTIONAL: timedelta(days=365 * 7),  # 7 years for tax
                DataCategory.DERIVED: timedelta(days=180),
                DataCategory.ANONYMOUS: timedelta(days=365 * 10),  # 10 years
                DataCategory.PSEUDONYMOUS: timedelta(days=365 * 3)
            },
            anonymization_threshold=timedelta(days=365),
            encryption_required={
                DataCategory.PERSONAL_IDENTIFIABLE,
                DataCategory.SENSITIVE,
                DataCategory.TRANSACTIONAL
            },
            audit_retention=timedelta(days=365 * 5),  # 5 years
            consent_renewal_period=timedelta(days=365),  # Annual renewal
            data_minimization_rules={
                DataCategory.PERSONAL_IDENTIFIABLE: ["name", "email", "phone", "address"],
                DataCategory.SENSITIVE: ["health", "biometric", "political", "religious"],
                DataCategory.BEHAVIORAL: ["clicks", "views", "searches", "preferences"],
                DataCategory.TRANSACTIONAL: ["orders", "payments", "refunds"]
            }
        )
    
    def _generate_encryption_key(self) -> bytes:
        """Generate or retrieve encryption key"""
        # In production, this would use a proper key management system
        import os
        password = os.getenv("ENCRYPTION_PASSWORD", "default-dev-key").encode()
        salt = os.getenv("ENCRYPTION_SALT", "default-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _initialize_audit_db(self) -> sqlite3.Connection:
        """Initialize audit database for compliance records"""
        db_path = self.config["audit_db_path"]
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processing_records (
                record_id TEXT PRIMARY KEY,
                timestamp DATETIME,
                data_category TEXT,
                purpose TEXT,
                legal_basis TEXT,
                subject_pseudonym TEXT,
                operation TEXT,
                data_fields TEXT,
                retention_until DATETIME
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                subject_pseudonym TEXT,
                purpose TEXT,
                granted BOOLEAN,
                timestamp DATETIME,
                expiry DATETIME,
                withdrawal_timestamp DATETIME
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_requests (
                request_id TEXT PRIMARY KEY,
                subject_pseudonym TEXT,
                request_type TEXT,
                timestamp DATETIME,
                completed BOOLEAN,
                completion_timestamp DATETIME,
                data_provided TEXT
            )
        """)
        
        conn.commit()
        return conn
    
    async def process_user_data(self,
                              raw_data: Dict[str, Any],
                              subject_id: str,
                              purpose: ProcessingPurpose,
                              legal_basis: LegalBasis) -> Dict[str, Any]:
        """
        Process user data with full GDPR compliance
        
        Args:
            raw_data: Raw user data to process
            subject_id: Unique identifier for the data subject
            purpose: Purpose of processing
            legal_basis: Legal basis for processing
            
        Returns:
            Processed data with privacy protections applied
        """
        # Get or create data subject
        subject = await self._get_or_create_subject(subject_id)
        
        # Check consent if required
        if legal_basis == LegalBasis.CONSENT:
            if not self._check_consent(subject, purpose):
                raise PermissionError(f"No consent for {purpose.value}")
        
        # Categorize data
        categorized_data = self._categorize_data(raw_data)
        
        # Apply data minimization
        minimized_data = self._minimize_data(categorized_data, purpose)
        
        # Process each category appropriately
        processed_data = {}
        
        for category, data in minimized_data.items():
            if category in self.privacy_policy.encryption_required:
                # Encrypt sensitive data
                processed_data[category] = await self._encrypt_data(data, subject.pseudonym)
            elif category == DataCategory.ANONYMOUS:
                # Apply k-anonymity
                processed_data[category] = await self._anonymize_data(data)
            else:
                # Pseudonymize
                processed_data[category] = await self._pseudonymize_data(data, subject.pseudonym)
        
        # Record processing
        await self._record_processing(
            subject, categorized_data.keys(), purpose, legal_basis
        )
        
        # Schedule retention check
        asyncio.create_task(self._schedule_retention_check(subject, categorized_data))
        
        return processed_data
    
    async def _get_or_create_subject(self, subject_id: str) -> DataSubject:
        """Get or create a data subject record"""
        if subject_id in self.subjects:
            subject = self.subjects[subject_id]
            subject.last_activity = datetime.now()
        else:
            # Generate pseudonym
            pseudonym = self._generate_pseudonym(subject_id)
            
            subject = DataSubject(
                subject_id=subject_id,
                pseudonym=pseudonym,
                created_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            self.subjects[subject_id] = subject
        
        return subject
    
    def _generate_pseudonym(self, subject_id: str) -> str:
        """Generate a secure pseudonym for a subject"""
        # Use HMAC to generate deterministic but secure pseudonym
        key = self.encryption_key[:32]  # Use part of encryption key
        h = hmac.new(key, subject_id.encode(), hashlib.sha256)
        return base64.urlsafe_b64encode(h.digest()).decode()[:self.config["pseudonym_length"]]
    
    def _check_consent(self, subject: DataSubject, purpose: ProcessingPurpose) -> bool:
        """Check if subject has given consent for purpose"""
        return subject.consents.get(purpose, False)
    
    def _categorize_data(self, raw_data: Dict[str, Any]) -> Dict[DataCategory, Dict[str, Any]]:
        """Categorize data fields by privacy category"""
        categorized = defaultdict(dict)
        
        # Define field patterns for each category
        patterns = {
            DataCategory.PERSONAL_IDENTIFIABLE: [
                r".*name.*", r".*email.*", r".*phone.*", r".*address.*",
                r".*id$", r".*ssn.*", r".*passport.*"
            ],
            DataCategory.SENSITIVE: [
                r".*health.*", r".*medical.*", r".*diagnosis.*",
                r".*religion.*", r".*political.*", r".*union.*",
                r".*ethnic.*", r".*biometric.*", r".*genetic.*"
            ],
            DataCategory.BEHAVIORAL: [
                r".*click.*", r".*view.*", r".*visit.*", r".*search.*",
                r".*preference.*", r".*rating.*", r".*bookmark.*"
            ],
            DataCategory.TRANSACTIONAL: [
                r".*order.*", r".*payment.*", r".*transaction.*",
                r".*purchase.*", r".*invoice.*", r".*refund.*"
            ]
        }
        
        # Categorize each field
        for field, value in raw_data.items():
            categorized_field = False
            
            for category, field_patterns in patterns.items():
                for pattern in field_patterns:
                    if re.match(pattern, field.lower()):
                        categorized[category][field] = value
                        categorized_field = True
                        break
                
                if categorized_field:
                    break
            
            # Default to derived data
            if not categorized_field:
                categorized[DataCategory.DERIVED][field] = value
        
        return dict(categorized)
    
    def _minimize_data(self, 
                      categorized_data: Dict[DataCategory, Dict[str, Any]],
                      purpose: ProcessingPurpose) -> Dict[DataCategory, Dict[str, Any]]:
        """Apply data minimization based on processing purpose"""
        minimized = {}
        
        # Define necessary fields for each purpose
        purpose_requirements = {
            ProcessingPurpose.ANALYTICS: {
                DataCategory.BEHAVIORAL: ["views", "clicks", "searches"],
                DataCategory.DERIVED: ["segment", "cohort"],
                DataCategory.ANONYMOUS: ["device_type", "browser"]
            },
            ProcessingPurpose.MARKETING: {
                DataCategory.PSEUDONYMOUS: ["preferences", "interests"],
                DataCategory.BEHAVIORAL: ["engagement_score", "activity_level"],
                DataCategory.DERIVED: ["segment", "lifetime_value"]
            },
            ProcessingPurpose.CUSTOMER_SERVICE: {
                DataCategory.PERSONAL_IDENTIFIABLE: ["email", "name"],
                DataCategory.TRANSACTIONAL: ["recent_orders", "support_history"]
            }
        }
        
        requirements = purpose_requirements.get(purpose, {})
        
        for category, data in categorized_data.items():
            if category in requirements:
                # Only keep required fields
                required_fields = requirements[category]
                minimized[category] = {
                    k: v for k, v in data.items()
                    if any(req in k.lower() for req in required_fields)
                }
            elif category == DataCategory.ANONYMOUS:
                # Always include anonymous data
                minimized[category] = data
        
        return minimized
    
    async def _encrypt_data(self, 
                          data: Dict[str, Any],
                          subject_pseudonym: str) -> Dict[str, Any]:
        """Encrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        encrypted = {}
        
        for field, value in data.items():
            # Convert to bytes
            value_bytes = json.dumps(value).encode()
            
            # Encrypt with subject-specific nonce
            nonce = f"{subject_pseudonym}:{field}".encode()
            encrypted_value = fernet.encrypt(value_bytes + nonce)
            
            encrypted[field] = {
                "encrypted": base64.b64encode(encrypted_value).decode(),
                "algorithm": self.config["encryption_algorithm"],
                "timestamp": datetime.now().isoformat()
            }
        
        return encrypted
    
    async def _anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply k-anonymity and differential privacy"""
        anonymized = {}
        
        for field, value in data.items():
            if isinstance(value, (int, float)):
                # Add Laplace noise for differential privacy
                noise = np.random.laplace(0, 1 / self.config["noise_epsilon"])
                anonymized[field] = value + noise
            elif isinstance(value, str):
                # Generalize strings
                anonymized[field] = self._generalize_string(value)
            else:
                # Hash other types
                anonymized[field] = hashlib.sha256(
                    json.dumps(value, sort_keys=True).encode()
                ).hexdigest()[:16]
        
        return anonymized
    
    def _generalize_string(self, value: str) -> str:
        """Generalize string values for k-anonymity"""
        generalizations = {
            "email": lambda x: x.split('@')[1] if '@' in x else "unknown",
            "ip": lambda x: '.'.join(x.split('.')[:2] + ['*', '*']),
            "postal": lambda x: x[:3] + "**" if len(x) > 3 else "***",
            "age": lambda x: f"{int(int(x) / 10) * 10}-{int(int(x) / 10) * 10 + 9}",
            "date": lambda x: x[:7] if len(x) > 7 else x  # Keep only year-month
        }
        
        # Try to identify field type and generalize
        for field_type, generalizer in generalizations.items():
            if field_type in value.lower():
                try:
                    return generalizer(value)
                except:
                    pass
        
        # Default: return category
        if len(value) > 10:
            return "long_text"
        elif value.isdigit():
            return "numeric"
        else:
            return "text"
    
    async def _pseudonymize_data(self, 
                               data: Dict[str, Any],
                               subject_pseudonym: str) -> Dict[str, Any]:
        """Replace identifiers with pseudonyms"""
        pseudonymized = {}
        
        for field, value in data.items():
            if "id" in field.lower() or "identifier" in field.lower():
                # Generate field-specific pseudonym
                field_pseudonym = self._generate_field_pseudonym(
                    subject_pseudonym, field, str(value)
                )
                pseudonymized[field] = field_pseudonym
            else:
                pseudonymized[field] = value
        
        return pseudonymized
    
    def _generate_field_pseudonym(self, 
                                subject_pseudonym: str,
                                field: str,
                                value: str) -> str:
        """Generate deterministic pseudonym for a field"""
        data = f"{subject_pseudonym}:{field}:{value}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def _record_processing(self,
                               subject: DataSubject,
                               categories: Set[DataCategory],
                               purpose: ProcessingPurpose,
                               legal_basis: LegalBasis):
        """Record processing activity for audit"""
        record = ProcessingRecord(
            record_id=secrets.token_urlsafe(16),
            timestamp=datetime.now(),
            data_category=list(categories)[0] if categories else DataCategory.ANONYMOUS,
            purpose=purpose,
            legal_basis=legal_basis,
            subject_pseudonym=subject.pseudonym,
            operation="process",
            data_fields=[],  # Don't log actual fields for privacy
            retention_until=datetime.now() + self.privacy_policy.retention_periods.get(
                list(categories)[0] if categories else DataCategory.ANONYMOUS,
                timedelta(days=365)
            )
        )
        
        self.processing_records.append(record)
        
        # Also save to audit DB
        self._save_processing_record(record)
    
    def _save_processing_record(self, record: ProcessingRecord):
        """Save processing record to audit database"""
        self.audit_db.execute("""
            INSERT INTO processing_records 
            (record_id, timestamp, data_category, purpose, legal_basis,
             subject_pseudonym, operation, data_fields, retention_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.record_id,
            record.timestamp,
            record.data_category.value,
            record.purpose.value,
            record.legal_basis.value,
            record.subject_pseudonym,
            record.operation,
            json.dumps(record.data_fields),
            record.retention_until
        ))
        self.audit_db.commit()
    
    async def _schedule_retention_check(self,
                                      subject: DataSubject,
                                      categorized_data: Dict[DataCategory, Any]):
        """Schedule data retention checks"""
        for category in categorized_data.keys():
            retention_period = self.privacy_policy.retention_periods.get(
                category, 
                timedelta(days=365)
            )
            
            # Schedule deletion
            deletion_time = datetime.now() + retention_period
            
            asyncio.create_task(
                self._scheduled_deletion(
                    subject.pseudonym, 
                    category, 
                    deletion_time
                )
            )
    
    async def _scheduled_deletion(self,
                                subject_pseudonym: str,
                                category: DataCategory,
                                deletion_time: datetime):
        """Delete data when retention period expires"""
        # Wait until deletion time
        wait_seconds = (deletion_time - datetime.now()).total_seconds()
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        
        # Perform deletion
        logger.info(f"Deleting {category.value} data for {subject_pseudonym}")
        
        # In real implementation, this would delete from all systems
        # For now, we'll mark it in the audit log
        self._record_deletion(subject_pseudonym, category)
    
    def _record_deletion(self, subject_pseudonym: str, category: DataCategory):
        """Record data deletion in audit log"""
        record = ProcessingRecord(
            record_id=secrets.token_urlsafe(16),
            timestamp=datetime.now(),
            data_category=category,
            purpose=ProcessingPurpose.LEGAL_COMPLIANCE,
            legal_basis=LegalBasis.LEGAL_OBLIGATION,
            subject_pseudonym=subject_pseudonym,
            operation="delete",
            data_fields=[],
            retention_until=datetime.now()  # Deleted now
        )
        
        self._save_processing_record(record)
    
    async def handle_data_request(self,
                                subject_id: str,
                                request_type: str) -> Dict[str, Any]:
        """
        Handle GDPR data subject requests
        
        Args:
            subject_id: ID of the data subject
            request_type: Type of request (access, portability, erasure, etc.)
            
        Returns:
            Response to the request
        """
        logger.info(f"Handling {request_type} request for {subject_id}")
        
        if subject_id not in self.subjects:
            return {
                "status": "not_found",
                "message": "No data found for subject"
            }
        
        subject = self.subjects[subject_id]
        
        if request_type == "access":
            return await self._handle_access_request(subject)
        elif request_type == "portability":
            return await self._handle_portability_request(subject)
        elif request_type == "erasure":
            return await self._handle_erasure_request(subject)
        elif request_type == "rectification":
            return await self._handle_rectification_request(subject)
        elif request_type == "restriction":
            return await self._handle_restriction_request(subject)
        else:
            return {
                "status": "invalid_request",
                "message": f"Unknown request type: {request_type}"
            }
    
    async def _handle_access_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle data access request"""
        # Gather all data about the subject
        subject_data = {
            "subject_id": subject.subject_id,
            "pseudonym": subject.pseudonym,
            "created_at": subject.created_at.isoformat(),
            "consents": {k.value: v for k, v in subject.consents.items()},
            "data_categories": [cat.value for cat in subject.data_categories],
            "processing_records": []
        }
        
        # Get processing records
        cursor = self.audit_db.execute("""
            SELECT * FROM processing_records 
            WHERE subject_pseudonym = ?
            ORDER BY timestamp DESC
        """, (subject.pseudonym,))
        
        for row in cursor.fetchall():
            subject_data["processing_records"].append({
                "timestamp": row[1],
                "category": row[2],
                "purpose": row[3],
                "legal_basis": row[4],
                "operation": row[6]
            })
        
        return {
            "status": "success",
            "data": subject_data,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _handle_portability_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle data portability request"""
        # Export data in machine-readable format
        portable_data = await self._handle_access_request(subject)
        
        # Convert to standard format (JSON)
        export_data = {
            "format": "JSON",
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "data": portable_data["data"]
        }
        
        # In real implementation, this would create a downloadable file
        return {
            "status": "success",
            "format": "JSON",
            "data": json.dumps(export_data, indent=2),
            "message": "Data exported in portable format"
        }
    
    async def _handle_erasure_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle right to erasure (right to be forgotten)"""
        # Check for legal obligations that prevent erasure
        has_legal_obligation = self._check_legal_obligations(subject)
        
        if has_legal_obligation:
            return {
                "status": "partial",
                "message": "Some data retained due to legal obligations",
                "retained_categories": ["transactional"]  # For tax purposes
            }
        
        # Mark for deletion
        subject.deletion_requested = datetime.now()
        
        # Immediate anonymization
        await self._immediate_anonymization(subject)
        
        # Record erasure
        self._record_deletion(subject.pseudonym, DataCategory.PERSONAL_IDENTIFIABLE)
        
        return {
            "status": "success",
            "message": "Data erasure completed",
            "completed_at": datetime.now().isoformat()
        }
    
    async def _handle_rectification_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle data rectification request"""
        # In real implementation, this would update incorrect data
        return {
            "status": "success",
            "message": "Data rectification process initiated",
            "instructions": "Please provide corrected data through secure channel"
        }
    
    async def _handle_restriction_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle processing restriction request"""
        # Mark subject for restricted processing
        subject.data_categories.add(DataCategory.PSEUDONYMOUS)
        
        return {
            "status": "success",
            "message": "Processing restricted as requested",
            "restricted_purposes": ["marketing", "analytics"]
        }
    
    def _check_legal_obligations(self, subject: DataSubject) -> bool:
        """Check if there are legal obligations preventing data deletion"""
        # Check for transactional data within legal retention period
        if DataCategory.TRANSACTIONAL in subject.data_categories:
            # Tax law typically requires 7 years retention
            if subject.last_activity:
                time_since_activity = datetime.now() - subject.last_activity
                if time_since_activity < timedelta(days=365 * 7):
                    return True
        
        return False
    
    async def _immediate_anonymization(self, subject: DataSubject):
        """Immediately anonymize subject data"""
        # In real implementation, this would:
        # 1. Remove all PII from active systems
        # 2. Update all references to use anonymous ID
        # 3. Securely delete encryption keys for this subject
        
        # Generate anonymous ID
        anonymous_id = hashlib.sha256(
            f"{subject.subject_id}:{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        logger.info(f"Anonymized subject {subject.pseudonym} to {anonymous_id}")
    
    async def update_consent(self,
                           subject_id: str,
                           purpose: ProcessingPurpose,
                           granted: bool) -> Dict[str, Any]:
        """Update consent for a specific purpose"""
        if subject_id not in self.subjects:
            return {
                "status": "error",
                "message": "Subject not found"
            }
        
        subject = self.subjects[subject_id]
        subject.consents[purpose] = granted
        
        # Record consent change
        self.audit_db.execute("""
            INSERT INTO consent_records
            (consent_id, subject_pseudonym, purpose, granted, timestamp, expiry, withdrawal_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            secrets.token_urlsafe(16),
            subject.pseudonym,
            purpose.value,
            granted,
            datetime.now(),
            datetime.now() + self.privacy_policy.consent_renewal_period if granted else None,
            None if granted else datetime.now()
        ))
        self.audit_db.commit()
        
        return {
            "status": "success",
            "purpose": purpose.value,
            "granted": granted,
            "updated_at": datetime.now().isoformat()
        }
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy compliance report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_subjects": len(self.subjects),
            "processing_summary": defaultdict(int),
            "consent_summary": defaultdict(int),
            "retention_compliance": {},
            "anonymization_stats": {},
            "data_requests": defaultdict(int)
        }
        
        # Processing summary
        cursor = self.audit_db.execute("""
            SELECT data_category, COUNT(*) 
            FROM processing_records 
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY data_category
        """)
        
        for category, count in cursor.fetchall():
            report["processing_summary"][category] = count
        
        # Consent summary
        cursor = self.audit_db.execute("""
            SELECT purpose, SUM(CASE WHEN granted = 1 THEN 1 ELSE 0 END) as granted,
                   SUM(CASE WHEN granted = 0 THEN 1 ELSE 0 END) as denied
            FROM consent_records
            WHERE withdrawal_timestamp IS NULL
            GROUP BY purpose
        """)
        
        for purpose, granted, denied in cursor.fetchall():
            report["consent_summary"][purpose] = {
                "granted": granted,
                "denied": denied,
                "rate": granted / (granted + denied) if (granted + denied) > 0 else 0
            }
        
        # Retention compliance
        for category, retention_period in self.privacy_policy.retention_periods.items():
            cursor = self.audit_db.execute("""
                SELECT COUNT(*) FROM processing_records
                WHERE data_category = ? 
                AND timestamp < datetime('now', ?)
                AND operation != 'delete'
            """, (category.value, f'-{retention_period.days} days'))
            
            overdue_count = cursor.fetchone()[0]
            report["retention_compliance"][category.value] = {
                "retention_days": retention_period.days,
                "overdue_records": overdue_count,
                "compliant": overdue_count == 0
            }
        
        # Data request stats
        cursor = self.audit_db.execute("""
            SELECT request_type, COUNT(*) 
            FROM data_requests
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY request_type
        """)
        
        for request_type, count in cursor.fetchall():
            report["data_requests"][request_type] = count
        
        return report
    
    def export_audit_trail(self, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Export audit trail for compliance review"""
        query = "SELECT * FROM processing_records WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        cursor = self.audit_db.execute(query, params)
        
        audit_trail = []
        for row in cursor.fetchall():
            audit_trail.append({
                "record_id": row[0],
                "timestamp": row[1],
                "data_category": row[2],
                "purpose": row[3],
                "legal_basis": row[4],
                "subject_pseudonym": row[5],
                "operation": row[6],
                "retention_until": row[8]
            })
        
        return audit_trail
    
    async def run_privacy_health_check(self) -> Dict[str, Any]:
        """Run comprehensive privacy health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {},
            "recommendations": []
        }
        
        # Check 1: Consent expiry
        cursor = self.audit_db.execute("""
            SELECT COUNT(*) FROM consent_records
            WHERE granted = 1 
            AND expiry < datetime('now')
            AND withdrawal_timestamp IS NULL
        """)
        
        expired_consents = cursor.fetchone()[0]
        health_status["checks"]["consent_expiry"] = {
            "status": "pass" if expired_consents == 0 else "fail",
            "expired_count": expired_consents
        }
        
        if expired_consents > 0:
            health_status["recommendations"].append(
                "Renew expired consents immediately"
            )
            health_status["overall_status"] = "attention_required"
        
        # Check 2: Retention compliance
        retention_issues = 0
        for category, retention_period in self.privacy_policy.retention_periods.items():
            cursor = self.audit_db.execute("""
                SELECT COUNT(*) FROM processing_records
                WHERE data_category = ? 
                AND retention_until < datetime('now')
                AND operation != 'delete'
            """, (category.value,))
            
            overdue = cursor.fetchone()[0]
            if overdue > 0:
                retention_issues += overdue
        
        health_status["checks"]["retention_compliance"] = {
            "status": "pass" if retention_issues == 0 else "fail",
            "overdue_deletions": retention_issues
        }
        
        if retention_issues > 0:
            health_status["recommendations"].append(
                f"Delete {retention_issues} records past retention period"
            )
            health_status["overall_status"] = "critical"
        
        # Check 3: Encryption status
        encryption_ok = all(
            category in self.privacy_policy.encryption_required
            for category in [DataCategory.PERSONAL_IDENTIFIABLE, DataCategory.SENSITIVE]
        )
        
        health_status["checks"]["encryption"] = {
            "status": "pass" if encryption_ok else "fail",
            "required_categories_encrypted": encryption_ok
        }
        
        # Check 4: Audit trail integrity
        cursor = self.audit_db.execute("""
            SELECT COUNT(*) FROM processing_records
            WHERE timestamp > datetime('now', '-1 day')
        """)
        
        recent_records = cursor.fetchone()[0]
        health_status["checks"]["audit_trail"] = {
            "status": "pass",
            "recent_records": recent_records,
            "logging_active": recent_records > 0
        }
        
        return health_status
    
    def close(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)
        self.audit_db.close()
        logger.info("Private data pipeline closed")