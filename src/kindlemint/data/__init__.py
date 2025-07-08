"""
KindleMint Data Module

Implements GDPR-compliant data processing pipelines for the KindleMint engine.
"""

from .private_data_pipeline import (
    PrivateDataPipeline,
    DataCategory,
    LegalBasis,
    ProcessingPurpose,
    DataSubject,
    PrivacyPolicy,
    ProcessingRecord
)

__all__ = [
    "PrivateDataPipeline",
    "DataCategory",
    "LegalBasis",
    "ProcessingPurpose",
    "DataSubject",
    "PrivacyPolicy",
    "ProcessingRecord"
]