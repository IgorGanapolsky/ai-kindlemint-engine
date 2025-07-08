# Cloud Data Migration Guide

## Overview

This guide outlines the migration from direct file I/O to the abstracted DataManager layer for cloud-ready data operations.

## Why Migrate?

- **Cloud Scalability**: Seamless transition from local to cloud storage
- **Data Consistency**: Centralized data management with metadata
- **Environment Flexibility**: Switch between local and cloud via environment variables
- **Better Error Handling**: Robust error handling and logging
- **Future-Proof**: Ready for AWS S3 and other cloud storage providers

## Migration Steps

### 1. Identify Scripts to Migrate

Scripts that need migration typically:
- Save/load JSON files directly
- Use `open()` with JSON operations
- Have hardcoded file paths
- Lack metadata tracking

### 2. Replace Direct File I/O

**Before (Direct File I/O):**
```python
# Loading data
with open("config.json", "r") as f:
    config = json.load(f)

# Saving data
with open("results.json", "w") as f:
    json.dump(data, f, indent=2)
```

**After (DataManager):**
```python
from kindlemint.data import DataManager

data_manager = DataManager()

# Loading data
config = data_manager.storage.load_data("config")

# Saving data
data_manager.storage.save_data("results", data, {
    "type": "results",
    "timestamp": datetime.now().isoformat()
})
```

### 3. Use Specialized Methods

**Book Data:**
```python
# Save book-specific data
data_manager.save_book_data("book_123", book_data)

# Load book data
book_data = data_manager.load_book_data("book_123")
```

**Analytics:**
```python
# Save analytics with timestamp
data_manager.save_analytics("daily_sales", sales_data)

# Load latest analytics
latest_sales = data_manager.load_latest_analytics("daily_sales")
```

**Market Data:**
```python
# Save market research
data_manager.save_market_data("sudoku_market_2025", market_data)
```

### 4. Environment Configuration

Set environment variables to control storage behavior:

```bash
# Local storage (default)
export KINDLEMINT_STORAGE_TYPE=local
export KINDLEMINT_LOCAL_PATH=data

# Cloud storage (AWS S3)
export KINDLEMINT_USE_CLOUD=true
export KINDLEMINT_STORAGE_TYPE=s3
export KINDLEMINT_S3_BUCKET=kindlemint-data
export KINDLEMINT_S3_REGION=us-east-1
```

## Migration Examples

### Batch Processor Migration

See `scripts/batch_processor_refactored.py` for a complete example of migrating the batch processor.

**Key Changes:**
- Replaced `_load_config()` with DataManager
- Replaced `_save_progress()` with DataManager
- Added book data persistence
- Added analytics tracking

### Daily Summary Generator Migration

**Before:**
```python
def save_summary(self, summary: Dict):
    json_path = self.reports_dir / f"summary_{date_str}.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
```

**After:**
```python
def save_summary(self, summary: Dict):
    date_str = summary["date"]
    self.data_manager.save_analytics("daily_summary", summary)
```

### Market Research Migration

**Before:**
```python
def save_insights(self, insights: Dict):
    filename = f"market_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = self.data_dir / filename
    with open(filepath, 'w') as f:
        json.dump(insights, f, indent=2)
```

**After:**
```python
def save_insights(self, insights: Dict):
    market_id = f"market_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    self.data_manager.save_market_data(market_id, insights)
```

## Testing Migration

### 1. Unit Tests

Test DataManager operations:
```python
def test_data_manager_operations():
    data_manager = DataManager()
    
    # Test save/load
    test_data = {"test": "data"}
    data_manager.storage.save_data("test_key", test_data)
    loaded_data = data_manager.storage.load_data("test_key")
    assert loaded_data == test_data
```

### 2. Integration Tests

Test with real scripts:
```python
def test_batch_processor_migration():
    processor = RefactoredBatchProcessor("test_config.json")
    # Test that data is saved/loaded correctly
```

### 3. Cloud Testing

Test S3 integration:
```bash
export KINDLEMINT_USE_CLOUD=true
export KINDLEMINT_S3_BUCKET=test-bucket
python scripts/test_cloud_storage.py
```

## Migration Checklist

- [ ] Identify all scripts using direct file I/O
- [ ] Replace `open()` calls with DataManager methods
- [ ] Add appropriate metadata to data operations
- [ ] Update error handling for DataManager operations
- [ ] Test local storage functionality
- [ ] Test cloud storage functionality (if applicable)
- [ ] Update documentation
- [ ] Update deployment scripts
- [ ] Monitor for any regressions

## Benefits After Migration

1. **Scalability**: Easy transition to cloud storage
2. **Reliability**: Better error handling and recovery
3. **Observability**: Metadata tracking for all data operations
4. **Maintainability**: Centralized data management
5. **Flexibility**: Environment-based configuration

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/kindlemint/data` is in Python path
2. **Storage Type Mismatch**: Check environment variables
3. **S3 Permissions**: Verify AWS credentials and bucket permissions
4. **Data Format**: Ensure data is JSON-serializable

### Debug Commands

```python
# Check storage configuration
info = data_manager.get_storage_info()
print(info)

# List available keys
keys = data_manager.storage.list_keys()
print(keys)

# Check if data exists
exists = data_manager.storage.exists("key")
print(exists)
```

## Next Steps

1. Complete migration of all production scripts
2. Set up cloud storage infrastructure
3. Implement data backup and recovery procedures
4. Add monitoring and alerting for data operations
5. Document cloud deployment procedures 