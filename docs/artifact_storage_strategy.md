# Artifact Storage Strategy for KindleMint Engine

## Current State
- Git LFS is configured to track PDFs and images in `output/` and `published_archive/` directories
- This approach has limitations:
  - Increases repository size over time
  - LFS storage costs can become significant
  - Not ideal for temporary or intermediate files

## Recommended Strategy

### 1. Immediate Actions
- **Remove output/ from Git tracking** - These are generated files that shouldn't be in version control
- **Keep only final production files** in `published_archive/` with LFS
- **Add output/ to .gitignore**

### 2. External Storage Options

#### Option A: AWS S3 (Recommended)
```python
# Example integration
import boto3

class ArtifactStorage:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'kindlemint-artifacts'

    def upload_book(self, book_path, book_id):
        key = f"books/{book_id}/interior.pdf"
        self.s3.upload_file(book_path, self.bucket, key)
        return f"s3://{self.bucket}/{key}"
```

**Benefits:**
- Cost-effective for large files
- Integrates with AWS Lambda deployment
- Supports lifecycle policies for automatic cleanup
- Direct integration with KDP automation

#### Option B: Google Cloud Storage
- Similar to S3 but integrates better if using Google services
- Slightly cheaper for infrequent access

#### Option C: Cloudflare R2
- S3-compatible API
- No egress fees
- Good for frequently accessed files

### 3. Implementation Plan

1. **Set up S3 bucket** with appropriate permissions
2. **Create IAM role** for secure access
3. **Implement ArtifactStorage class** in `scripts/artifact_storage.py`
4. **Update book generation scripts** to use external storage
5. **Clean up existing LFS files** after migration

### 4. Directory Structure

```
kindlemint-engine/
├── books/                    # Metadata only (JSON files)
│   └── active_production/
├── published_archive/        # Final KDP-ready files (keep in LFS)
│   └── volume_X/
├── temp/                     # Local temporary files (gitignored)
└── scripts/                  # Code only
```

### 5. Retention Policy

- **Temporary files**: Delete after 24 hours
- **Failed attempts**: Keep for 7 days for debugging
- **Published books**: Archive indefinitely in S3 Glacier
- **QA reports**: Keep for 30 days

### 6. Cost Estimates

- **S3 Standard**: ~$0.023/GB/month
- **S3 Glacier**: ~$0.004/GB/month (for archives)
- **Git LFS**: $5/month for 50GB (current approach)

For 100 books/month at 10MB each:
- S3: ~$0.23/month
- LFS: Would exceed free tier quickly

### 7. Migration Steps

```bash
# 1. Remove output from Git
git rm -r --cached output/
echo "output/" >> .gitignore

# 2. Remove old LFS files
git lfs untrack "output/**/*.pdf"
git lfs untrack "output/**/*.png"

# 3. Update .gitattributes
# Keep only published_archive/ in LFS

# 4. Clean up repository
git gc --aggressive --prune=now
```

## Conclusion

Moving to external artifact storage will:
- Reduce repository size and complexity
- Lower storage costs
- Improve CI/CD performance
- Enable better artifact lifecycle management

The recommended approach is to use AWS S3 for all generated artifacts, keeping only code and essential production files in Git.
