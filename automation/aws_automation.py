"""
Complete AWS Automation System for Passive Income KDP Business
Handles book generation, KDP upload, and distribution automatically
"""
import boto3
import os
import json
import time
import schedule
from datetime import datetime
import zipfile
import paramiko
import requests
from botocore.exceptions import ClientError

class PassiveIncomeAutomation:
    """Complete automation system for KDP passive income business"""
    
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        self.events = boto3.client('events')
        self.ses = boto3.client('ses')
        self.bucket_name = 'ai-kindlemint-automation'
        
    def setup_aws_infrastructure(self):
        """Set up complete AWS infrastructure for automation"""
        print("Setting up AWS automation infrastructure...")
        
        # 1. Create S3 bucket for book storage
        self._create_s3_bucket()
        
        # 2. Create Lambda function for book generation
        self._create_lambda_function()
        
        # 3. Set up CloudWatch Events for scheduling
        self._setup_daily_schedule()
        
        # 4. Configure SES for email notifications
        self._setup_email_notifications()
        
        print("✓ AWS infrastructure ready for passive income automation")
    
    def _create_s3_bucket(self):
        """Create S3 bucket for storing generated books"""
        try:
            self.s3.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
            )
            
            # Enable versioning for book history
            self.s3.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            print(f"✓ S3 bucket created: {self.bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print(f"✓ S3 bucket already exists: {self.bucket_name}")
            else:
                print(f"✗ S3 bucket creation failed: {e}")
    
    def _create_lambda_function(self):
        """Create Lambda function for automated book generation"""
        
        # Package the entire mission control system
        lambda_code = self._package_lambda_code()
        
        function_config = {
            'FunctionName': 'ai-kindlemint-generator',
            'Runtime': 'python3.11',
            'Role': 'arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role',
            'Handler': 'lambda_handler.main',
            'Code': {'ZipFile': lambda_code},
            'Description': 'Automated AI book generation for KDP',
            'Timeout': 900,  # 15 minutes
            'MemorySize': 1024,
            'Environment': {
                'Variables': {
                    'S3_BUCKET': self.bucket_name,
                    'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY'),
                    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
                    'KDP_EMAIL': os.environ.get('KDP_EMAIL'),
                    'KDP_PASSWORD': os.environ.get('KDP_PASSWORD')
                }
            }
        }
        
        try:
            self.lambda_client.create_function(**function_config)
            print("✓ Lambda function created for automated book generation")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                # Update existing function
                self.lambda_client.update_function_code(
                    FunctionName='ai-kindlemint-generator',
                    ZipFile=lambda_code
                )
                print("✓ Lambda function updated")
    
    def _package_lambda_code(self):
        """Package the mission control system for Lambda deployment"""
        import io
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all necessary files
            files_to_package = [
                'mission_control.py',
                'config.py',
                'agents/cto_agent.py',
                'agents/cmo_agent.py',
                'agents/cfo_agent.py',
                'utils/file_manager.py',
                'utils/logger.py',
                'utils/emailer.py',
                'scripts/publish_to_kdp.py',
                'scripts/convert_kpf_to_docx.py'
            ]
            
            for file_path in files_to_package:
                if os.path.exists(file_path):
                    zipf.write(file_path)
            
            # Add Lambda handler
            lambda_handler_code = self._generate_lambda_handler()
            zipf.writestr('lambda_handler.py', lambda_handler_code)
        
        return zip_buffer.getvalue()
    
    def _generate_lambda_handler(self):
        """Generate Lambda handler code"""
        return '''
import json
import boto3
import os
import random
from mission_control import MissionControl

def main(event, context):
    """Lambda handler for automated book generation"""
    
    # Generate random book topic or use provided topic
    topics = [
        "Space Adventure Puzzles for Kids",
        "Underwater Mystery Quest", 
        "Jungle Explorer Challenges",
        "Castle Secret Riddles",
        "Robot Friend Adventures",
        "Magic Forest Puzzles",
        "Pirate Treasure Hunt",
        "Dinosaur Discovery Quest"
    ]
    
    topic = event.get('topic', random.choice(topics))
    
    # Initialize Mission Control
    mc = MissionControl()
    
    # Generate complete book
    results = mc.execute_full_mission(topic)
    
    # Upload to S3
    s3 = boto3.client('s3')
    bucket = os.environ['S3_BUCKET']
    
    # Upload generated files
    for file_path in results.get('files_created', []):
        if os.path.exists(file_path):
            s3.upload_file(file_path, bucket, f"books/{os.path.basename(file_path)}")
    
    # Trigger KDP upload if configured
    if os.environ.get('AUTO_PUBLISH') == 'true':
        from scripts.publish_to_kdp import publish_to_kdp
        publish_to_kdp(results['book_file'])
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Book generated successfully',
            'topic': topic,
            'files_created': len(results.get('files_created', []))
        })
    }
'''
    
    def _setup_daily_schedule(self):
        """Set up CloudWatch Events for daily book generation"""
        rule_name = 'daily-book-generation'
        
        # Create rule for daily execution at 6 AM UTC
        self.events.put_rule(
            Name=rule_name,
            ScheduleExpression='cron(0 6 * * ? *)',  # Daily at 6 AM UTC
            Description='Daily automated book generation',
            State='ENABLED'
        )
        
        # Add Lambda function as target
        self.events.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    'Id': '1',
                    'Arn': f'arn:aws:lambda:us-west-2:YOUR_ACCOUNT:function:ai-kindlemint-generator'
                }
            ]
        )
        
        print("✓ Daily automation schedule configured")
    
    def _setup_email_notifications(self):
        """Configure SES for automated email notifications"""
        try:
            # Verify email address for SES
            email = os.environ.get('GMAIL_USER')
            if email:
                self.ses.verify_email_identity(EmailAddress=email)
                print(f"✓ Email notifications configured for {email}")
        except ClientError as e:
            print(f"⚠ Email setup requires manual SES verification: {e}")

def main():
    """Main deployment function"""
    automation = PassiveIncomeAutomation()
    automation.setup_aws_infrastructure()
    
    print("\n🎉 PASSIVE INCOME SYSTEM CONFIGURED!")
    print("📈 Your AI KindleMint business infrastructure is ready")
    print("💤 Books will generate automatically daily at 6 AM UTC")
    print("📊 Files stored in S3 bucket: ai-kindlemint-automation")

if __name__ == '__main__':
    main()