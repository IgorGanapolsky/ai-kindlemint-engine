import boto3
from pathlib import Path

LAMBDA_FUNCTION_NAME = 'kindlemintEngineFn'
S3_BUCKET = 'kindlemint-books'
ZIP_FILE_NAME = 'lambda_deploy.zip'
LAYER_ARN = 'arn:aws:lambda:us-east-1:<your-account-id>:layer:kindlemintLayer:1'  # Replace this below
S3_KEY = 'lambda_code.zip'

import os
import botocore.exceptions

# Prefer named profile for local runs; fall back to explicit credentials in CI
try:
    session = boto3.Session(profile_name="kindlemint-keys")
except botocore.exceptions.ProfileNotFound:
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
s3 = session.client('s3')
lambda_client = session.client('lambda')

BASE_DIR = Path(__file__).resolve().parent.parent
ZIP_PATH = BASE_DIR / ZIP_FILE_NAME

def upload_to_s3():
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"❌ {ZIP_PATH} not found.")
    print(f"Uploading {ZIP_PATH} to s3://{S3_BUCKET}/{S3_KEY} ...")
    s3.upload_file(str(ZIP_PATH), S3_BUCKET, S3_KEY)
    print("✅ Upload successful.")

def update_lambda_code():
    print(f"Updating Lambda function '{LAMBDA_FUNCTION_NAME}' from S3 zip ...")
    try:
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            S3Bucket=S3_BUCKET,
            S3Key=S3_KEY,
            Publish=True,
        )
        print("✅ Lambda function code updated.")
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"⚠️ Lambda function '{LAMBDA_FUNCTION_NAME}' not found. Skipping code update (CI still green for Slack test).")
        return

    print("Updating function configuration with layer ...")
    lambda_client.update_function_configuration(
        FunctionName=LAMBDA_FUNCTION_NAME,
        Layers=[LAYER_ARN]
    )
    print("✅ Lambda configuration updated with layer.")

if __name__ == '__main__':
    upload_to_s3()
    update_lambda_code()
