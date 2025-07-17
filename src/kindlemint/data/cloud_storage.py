#!/usr/bin/env python3
"""
Cloud Data Handling - Abstract Storage Layer
Supports both local and cloud (AWS S3) storage with environment-based configuration
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Configuration for data storage"""
    storage_type: str  # "local" or "s3"
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    local_path: Optional[str] = None
    use_cloud: bool = False


class DataStorageInterface(ABC):
    """Abstract interface for data storage operations"""
    
    @abstractmethod
    def save_data(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """Save data with key"""
        pass
    
    @abstractmethod
    def load_data(self, key: str) -> Optional[Any]:
        """Load data by key"""
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """List available keys"""
        pass
    
    @abstractmethod
    def delete_data(self, key: str) -> bool:
        """Delete data by key"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if data exists"""
        pass


class LocalStorage(DataStorageInterface):
    """Local file system storage implementation"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized local storage at {self.base_path}")
    
    def save_data(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """Save data to local file system"""
        try:
            file_path = self.base_path / f"{key}.json"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data with metadata
            save_data = {
                "data": data,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "key": key
            }
            
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            logger.info(f"Saved data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data {key}: {e}")
            return False
    
    def load_data(self, key: str) -> Optional[Any]:
        """Load data from local file system"""
        try:
            file_path = self.base_path / f"{key}.json"
            
            if not file_path.exists():
                logger.warning(f"Data file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                save_data = json.load(f)
            
            logger.info(f"Loaded data from {file_path}")
            return save_data["data"]
            
        except Exception as e:
            logger.error(f"Failed to load data {key}: {e}")
            return None
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List available keys in local storage, recursively, returning keys relative to base_path (no .json)"""
        try:
            keys = []
            self.base_path / prefix if prefix else self.base_path
            if prefix and not prefix.endswith("/"):
                prefix += "/"
            for file_path in self.base_path.rglob("*.json"):
                rel_path = file_path.relative_to(self.base_path)
                key = str(rel_path.with_suffix(""))  # Remove .json
                if not prefix or key.startswith(prefix):
                    keys.append(key)
            return keys
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []
    
    def delete_data(self, key: str) -> bool:
        """Delete data from local storage"""
        try:
            file_path = self.base_path / f"{key}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted data: {key}")
                return True
            else:
                logger.warning(f"Data not found for deletion: {key}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete data {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if data exists in local storage"""
        file_path = self.base_path / f"{key}.json"
        return file_path.exists()


class S3Storage(DataStorageInterface):
    """AWS S3 storage implementation"""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS S3 client"""
        try:
            import boto3
            self._client = boto3.client('s3', region_name=self.region)
            logger.info(f"Initialized S3 storage for bucket: {self.bucket_name}")
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def save_data(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """Save data to S3"""
        try:
            # Prepare data with metadata
            save_data = {
                "data": data,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "key": key
            }
            
            # Convert to JSON string
            json_data = json.dumps(save_data, default=str)
            
            # Upload to S3
            self._client.put_object(
                Bucket=self.bucket_name,
                Key=f"{key}.json",
                Body=json_data,
                ContentType='application/json'
            )
            
            logger.info(f"Saved data to S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data to S3 {key}: {e}")
            return False
    
    def load_data(self, key: str) -> Optional[Any]:
        """Load data from S3"""
        try:
            response = self._client.get_object(
                Bucket=self.bucket_name,
                Key=f"{key}.json"
            )
            
            json_data = response['Body'].read().decode('utf-8')
            save_data = json.loads(json_data)
            
            logger.info(f"Loaded data from S3: {key}")
            return save_data["data"]
            
        except Exception as e:
            logger.error(f"Failed to load data from S3 {key}: {e}")
            return None
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List available keys in S3"""
        try:
            response = self._client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            keys = []
            for obj in response.get('Contents', []):
                key = obj['Key'].replace('.json', '')  # Remove .json extension
                keys.append(key)
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to list S3 keys: {e}")
            return []
    
    def delete_data(self, key: str) -> bool:
        """Delete data from S3"""
        try:
            self._client.delete_object(
                Bucket=self.bucket_name,
                Key=f"{key}.json"
            )
            
            logger.info(f"Deleted data from S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete data from S3 {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if data exists in S3"""
        try:
            self._client.head_object(
                Bucket=self.bucket_name,
                Key=f"{key}.json"
            )
            return True
        except:
            return False


class DataManager:
    """Main data manager that abstracts storage operations"""
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or self._load_config()
        self.storage = self._initialize_storage()
        logger.info(f"Initialized DataManager with {self.config.storage_type} storage")
    
    def _load_config(self) -> StorageConfig:
        """Load configuration from environment variables"""
        storage_type = os.getenv("KINDLEMINT_STORAGE_TYPE", "local")
        use_cloud = os.getenv("KINDLEMINT_USE_CLOUD", "false").lower() == "true"
        
        if use_cloud or storage_type == "s3":
            return StorageConfig(
                storage_type="s3",
                bucket_name=os.getenv("KINDLEMINT_S3_BUCKET", "kindlemint-data"),
                region=os.getenv("KINDLEMINT_S3_REGION", "us-east-1"),
                use_cloud=True
            )
        else:
            return StorageConfig(
                storage_type="local",
                local_path=os.getenv("KINDLEMINT_LOCAL_PATH", "data"),
                use_cloud=False
            )
    
    def _initialize_storage(self) -> DataStorageInterface:
        """Initialize the appropriate storage backend"""
        if self.config.storage_type == "s3":
            return S3Storage(
                bucket_name=self.config.bucket_name,
                region=self.config.region
            )
        else:
            return LocalStorage(
                base_path=self.config.local_path
            )
    
    def save_book_data(self, book_id: str, data: Dict[str, Any]) -> bool:
        """Save book-specific data"""
        key = f"books/{book_id}/data"
        metadata = {
            "type": "book_data",
            "book_id": book_id,
            "version": "1.0"
        }
        return self.storage.save_data(key, data, metadata)
    
    def load_book_data(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Load book-specific data"""
        key = f"books/{book_id}/data"
        return self.storage.load_data(key)
    
    def save_analytics(self, analytics_type: str, data: Dict[str, Any]) -> bool:
        """Save analytics data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"analytics/{analytics_type}/{timestamp}"
        metadata = {
            "type": "analytics",
            "analytics_type": analytics_type,
            "timestamp": timestamp
        }
        return self.storage.save_data(key, data, metadata)
    
    def load_latest_analytics(self, analytics_type: str) -> Optional[Dict[str, Any]]:
        """Load the latest analytics data for a type"""
        keys = self.storage.list_keys(f"analytics/{analytics_type}/")
        logger.debug(f"[load_latest_analytics] Keys found: {keys}")
        if keys:
            # Filter keys that match the analytics type pattern
            filtered_keys = [k for k in keys if k.startswith(f"analytics/{analytics_type}/")]
            logger.debug(f"[load_latest_analytics] Filtered keys: {filtered_keys}")
            if filtered_keys:
                latest_key = sorted(filtered_keys)[-1]  # Get most recent
                logger.debug(f"[load_latest_analytics] Loading key: {latest_key}")
                return self.storage.load_data(latest_key)
        return None
    
    def save_market_data(self, market_id: str, data: Dict[str, Any]) -> bool:
        """Save market research data"""
        key = f"market_data/{market_id}"
        metadata = {
            "type": "market_data",
            "market_id": market_id
        }
        return self.storage.save_data(key, data, metadata)
    
    def list_books(self) -> List[str]:
        """List all book IDs"""
        keys = self.storage.list_keys("books/")
        book_ids = []
        for key in keys:
            if "/data" in key:
                book_id = key.split("/")[1]
                book_ids.append(book_id)
        return list(set(book_ids))  # Remove duplicates
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the current storage configuration"""
        return {
            "storage_type": self.config.storage_type,
            "use_cloud": self.config.use_cloud,
            "bucket_name": self.config.bucket_name,
            "region": self.config.region,
            "local_path": self.config.local_path,
            "total_keys": len(self.storage.list_keys())
        } 