"""
Data management module for KindleMint Engine
Handles data storage, retrieval, and cloud integration
"""

from .cloud_storage import (
    DataManager,
    StorageConfig,
    DataStorageInterface,
    LocalStorage,
    S3Storage
)

__all__ = [
    'DataManager',
    'StorageConfig', 
    'DataStorageInterface',
    'LocalStorage',
    'S3Storage'
]