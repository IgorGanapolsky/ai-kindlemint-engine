#!/usr/bin/env python3
"""
Autonomous Google Drive Upload System
Automatically uploads all book packages to Google Drive for backup
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger

def setup_google_drive_service():
    """Setup Google Drive API service with GitHub secrets"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        # Get credentials from environment variable (GitHub secret)
        credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
        if not credentials_json:
            raise ValueError("GOOGLE_DRIVE_CREDENTIALS not found in environment")
        
        # Parse credentials
        credentials_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        return service
        
    except Exception as e:
        print(f"❌ Google Drive setup failed: {e}")
        return None

def create_drive_folder(service, folder_name, parent_folder_id):
    """Create a folder in Google Drive"""
    try:
        folder_metadata = {
            'name': folder_name,
            'parents': [parent_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(body=folder_metadata, fields='id,name').execute()
        return folder.get('id')
        
    except Exception as e:
        print(f"❌ Failed to create folder {folder_name}: {e}")
        return None

def upload_file_to_drive(service, file_path, parent_folder_id):
    """Upload a single file to Google Drive"""
    try:
        from googleapiclient.http import MediaFileUpload
        
        file_metadata = {
            'name': file_path.name,
            'parents': [parent_folder_id]
        }
        
        media = MediaFileUpload(str(file_path), resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size'
        ).execute()
        
        return file.get('id')
        
    except Exception as e:
        print(f"❌ Failed to upload {file_path.name}: {e}")
        return None

def autonomous_drive_upload():
    """Autonomously upload all books to Google Drive"""
    logger = get_logger('autonomous_drive_upload')
    
    logger.info("☁️ Starting autonomous Google Drive upload...")
    
    # Setup Google Drive service
    service = setup_google_drive_service()
    if not service:
        logger.error("❌ Failed to setup Google Drive service")
        return False
    
    # Target folder ID (your shared folder)
    target_folder_id = "1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB"
    
    # Create series folder with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    series_folder_name = f"Large_Print_Crossword_Masters_AUTO_{timestamp}"
    
    series_folder_id = create_drive_folder(service, series_folder_name, target_folder_id)
    if not series_folder_id:
        logger.error("❌ Failed to create series folder")
        return False
    
    logger.info(f"📁 Created series folder: {series_folder_name}")
    
    # Find and upload all books
    books_dir = Path("output/generated_books")
    uploaded_count = 0
    
    for vol_num in range(1, 6):
        # Find volume folder
        vol_folders = [f for f in books_dir.iterdir() 
                      if f.is_dir() and f"vol_{vol_num}_final" in f.name]
        
        if not vol_folders:
            logger.warning(f"⚠️ Volume {vol_num} folder not found")
            continue
            
        vol_folder = vol_folders[0]
        
        # Create volume folder in Drive
        vol_folder_name = f"Volume_{vol_num:02d}"
        vol_folder_id = create_drive_folder(service, vol_folder_name, series_folder_id)
        
        if not vol_folder_id:
            logger.error(f"❌ Failed to create folder for Volume {vol_num}")
            continue
        
        # Upload all files in volume folder
        files_uploaded = 0
        for file_path in vol_folder.iterdir():
            if file_path.is_file():
                file_id = upload_file_to_drive(service, file_path, vol_folder_id)
                if file_id:
                    files_uploaded += 1
                    logger.info(f"   📄 Uploaded: {file_path.name}")
        
        if files_uploaded > 0:
            uploaded_count += 1
            logger.info(f"✅ Volume {vol_num} uploaded ({files_uploaded} files)")
        else:
            logger.error(f"❌ No files uploaded for Volume {vol_num}")
    
    # Create upload summary
    summary = {
        'upload_date': datetime.now().isoformat(),
        'series_folder': series_folder_name,
        'volumes_uploaded': uploaded_count,
        'drive_folder_id': series_folder_id,
        'status': 'completed' if uploaded_count == 5 else 'partial'
    }
    
    # Save summary locally
    summary_file = Path("output/drive_upload_summary.json")
    summary_file.parent.mkdir(exist_ok=True)
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"📊 Upload summary: {uploaded_count}/5 volumes uploaded")
    logger.info(f"🔗 Drive folder: https://drive.google.com/drive/folders/{series_folder_id}")
    
    return uploaded_count == 5

def main():
    """Main autonomous upload function"""
    print("=" * 60)
    print("☁️ AUTONOMOUS GOOGLE DRIVE UPLOAD")
    print("=" * 60)
    
    success = autonomous_drive_upload()
    
    print("=" * 60)
    if success:
        print("🎉 GOOGLE DRIVE UPLOAD COMPLETED!")
        print("✅ All volumes backed up to Google Drive")
    else:
        print("⚠️ GOOGLE DRIVE UPLOAD PARTIAL/FAILED")
        print("❌ Check logs for details")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)