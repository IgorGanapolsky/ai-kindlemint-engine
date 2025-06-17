"""V3 Zero-Touch Publishing Engine - Containerized KDP Publisher Task"""
import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

# Add the parent directory to the Python path
sys.path.insert(0, '/app')

from kindlemint.publisher.kdp_agent import KDPPublisher
from kindlemint.notifications.slack_notifier import SlackNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KDPPublisherTask:
    """Containerized KDP publishing task for AWS Fargate execution."""
    
    def __init__(self):
        """Initialize the KDP publisher task."""
        self.s3_client = boto3.client('s3')
        self.slack_notifier = SlackNotifier()
        
        # Get environment variables
        self.kdp_email = os.getenv('KDP_EMAIL')
        self.kdp_password = os.getenv('KDP_PASSWORD')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not self.kdp_email or not self.kdp_password:
            raise ValueError("KDP_EMAIL and KDP_PASSWORD environment variables must be set")
    
    async def execute_publishing_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete KDP publishing workflow.
        
        Args:
            task_input: Dictionary containing:
                - book_id: Unique book identifier
                - s3_bucket: S3 bucket containing assets
                - manuscript_key: S3 key for .docx manuscript
                - cover_key: S3 key for .jpg cover
                - metadata: Book metadata (title, description, etc.)
                
        Returns:
            Dictionary with publishing results
        """
        try:
            book_id = task_input['book_id']
            s3_bucket = task_input['s3_bucket']
            manuscript_key = task_input['manuscript_key']
            cover_key = task_input['cover_key']
            metadata = task_input['metadata']
            
            logger.info(f"🚀 Starting KDP publishing for book {book_id}")
            
            # Download assets from S3
            local_assets = await self._download_assets(s3_bucket, manuscript_key, cover_key, book_id)
            
            # Initialize KDP publisher
            publisher = KDPPublisher(
                email=self.kdp_email,
                password=self.kdp_password,
                headless=True  # Always headless in container
            )
            
            # Publish to KDP
            publishing_result = await publisher.publish_book(
                title=metadata['title'],
                subtitle=metadata.get('subtitle', ''),
                description=metadata['description'],
                keywords=metadata.get('keywords', []),
                categories=metadata.get('categories', []),
                manuscript_path=local_assets['manuscript_path'],
                cover_path=local_assets['cover_path'],
                price=metadata.get('price', 2.99),
                author=metadata.get('author', 'Igor Ganapolsky')
            )
            
            # Clean up local files
            self._cleanup_local_files(local_assets)
            
            # Send success notification
            await self._send_success_notification(book_id, metadata['title'], publishing_result)
            
            logger.info(f"✅ Successfully published book {book_id} to KDP")
            
            return {
                'status': 'success',
                'book_id': book_id,
                'kdp_url': publishing_result.get('book_url', ''),
                'publication_time': publishing_result.get('timestamp', ''),
                'message': 'Book successfully published to Amazon KDP'
            }
            
        except Exception as e:
            logger.error(f"❌ Error publishing book {book_id}: {str(e)}")
            
            # Send failure notification
            await self._send_failure_notification(book_id, str(e))
            
            return {
                'status': 'error',
                'book_id': book_id,
                'error': str(e),
                'message': 'Failed to publish book to KDP'
            }
    
    async def _download_assets(self, bucket: str, manuscript_key: str, cover_key: str, book_id: str) -> Dict[str, str]:
        """Download book assets from S3 to local storage."""
        try:
            logger.info(f"📥 Downloading assets from S3 bucket: {bucket}")
            
            # Create local directory
            local_dir = Path(f"/tmp/{book_id}")
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Download manuscript
            manuscript_path = local_dir / "manuscript.docx"
            self.s3_client.download_file(bucket, manuscript_key, str(manuscript_path))
            logger.info(f"Downloaded manuscript: {manuscript_key}")
            
            # Download cover
            cover_path = local_dir / "cover.jpg"
            self.s3_client.download_file(bucket, cover_key, str(cover_path))
            logger.info(f"Downloaded cover: {cover_key}")
            
            return {
                'manuscript_path': str(manuscript_path),
                'cover_path': str(cover_path),
                'local_dir': str(local_dir)
            }
            
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            raise Exception(f"Failed to download assets from S3: {str(e)}")
    
    def _cleanup_local_files(self, local_assets: Dict[str, str]):
        """Clean up local files after publishing."""
        try:
            import shutil
            local_dir = local_assets['local_dir']
            if os.path.exists(local_dir):
                shutil.rmtree(local_dir)
                logger.info(f"Cleaned up local directory: {local_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup local files: {e}")
    
    async def _send_success_notification(self, book_id: str, title: str, result: Dict[str, Any]):
        """Send success notification to Slack."""
        try:
            # Use the enhanced Slack notifier
            success = self.slack_notifier.notify_kdp_publishing_success(
                book_id=book_id,
                title=title,
                asin=result.get('asin'),
                kdp_url=result.get('book_url')
            )
            
            if success:
                logger.info("Success notification sent to Slack")
            else:
                logger.warning("Failed to send success notification to Slack")
            
        except Exception as e:
            logger.warning(f"Failed to send success notification: {e}")
    
    async def _send_failure_notification(self, book_id: str, error_message: str):
        """Send failure notification to Slack."""
        try:
            # Extract error details for better reporting
            errors = [error_message] if isinstance(error_message, str) else error_message
            
            # Use the enhanced Slack notifier
            success = self.slack_notifier.notify_kdp_publishing_failure(
                book_id=book_id,
                title="Unknown Title",  # Could be enhanced to pass title
                errors=errors
            )
            
            if success:
                logger.info("Failure notification sent to Slack")
            else:
                logger.warning("Failed to send failure notification to Slack")
            
        except Exception as e:
            logger.warning(f"Failed to send failure notification: {e}")

async def main():
    """Main entry point for the containerized KDP publisher."""
    try:
        logger.info("🚀 V3 Zero-Touch KDP Publisher Container Starting...")
        
        # Get task input from environment variable or command line
        task_input_json = os.getenv('TASK_INPUT')
        if not task_input_json:
            # For testing, use a default input
            task_input_json = sys.argv[1] if len(sys.argv) > 1 else None
        
        if not task_input_json:
            raise ValueError("TASK_INPUT environment variable or command line argument required")
        
        # Parse task input
        task_input = json.loads(task_input_json)
        logger.info(f"📋 Task input received: {task_input.get('book_id', 'unknown')}")
        
        # Execute publishing task
        publisher_task = KDPPublisherTask()
        result = await publisher_task.execute_publishing_task(task_input)
        
        # Output result
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        exit_code = 0 if result['status'] == 'success' else 1
        logger.info(f"🏁 Task completed with exit code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"💥 Fatal error in KDP publisher task: {str(e)}")
        
        # Try to send failure notification
        try:
            notifier = SlackNotifier()
            await notifier.send_notification(
                message=f"💥 *V3 Zero-Touch Engine CRITICAL ERROR*\n\nError: {str(e)}",
                channel="#kindlemint-alerts"
            )
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())