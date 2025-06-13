#!/bin/bash
set -e

# -----------------------------
# Config
# -----------------------------
S3_BUCKET="kindlemint-books"
PROFILE="kindlemint-keys"
PYTHON_VERSION="python3.11"
ARCH="x86_64"

# -----------------------------
# Helpers
# -----------------------------
function clean_layer() {
  rm -rf lambda_layer
  mkdir -p lambda_layer/python
}

function prune_layer() {
  find lambda_layer/python -type d -name "__pycache__" -exec rm -rf {} +
  find lambda_layer/python -type f -name "*.pyc" -delete
  find lambda_layer/python -type d -name "tests" -exec rm -rf {} +
  rm -rf lambda_layer/python/botocore/data || true
}

function zip_and_upload() {
  local name=$1
  local zip_file="layer_${name}.zip"
  echo "Zipping layer: $zip_file"
  cd lambda_layer
  zip -r9 "../$zip_file" . > /dev/null
  cd ..
  echo "Uploading $zip_file to s3://$S3_BUCKET/$zip_file ..."
  aws s3 cp "$zip_file" "s3://$S3_BUCKET/$zip_file" --profile "$PROFILE"
  echo "✅ Done: $name layer"
}

# -----------------------------
# Layer 1: openai
# -----------------------------
clean_layer
pip install openai --no-cache-dir --upgrade --target lambda_layer/python
prune_layer
zip_and_upload "openai"

# -----------------------------
# Layer 2: boto3 + dateutil
# -----------------------------
clean_layer
pip install boto3 python-dateutil --no-cache-dir --upgrade --target lambda_layer/python
prune_layer
zip_and_upload "boto3"

# -----------------------------
# Optional Layer 3: ALL DEPS (fallback)
# -----------------------------
clean_layer
pip install openai boto3 python-dateutil --no-cache-dir --upgrade --target lambda_layer/python
prune_layer
zip_and_upload "deps"
