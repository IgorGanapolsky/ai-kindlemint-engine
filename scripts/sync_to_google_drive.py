#!/usr/bin/env python3
"""
Sync generated books to Google Drive automatically.
Uploads book packages while keeping local copies for development.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def setup_google_drive_service():
    """Set up Google Drive API service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        # Scopes for Google Drive access
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        creds = None
        token_file = Path(__file__).parent.parent / "secrets" / "google_drive_token.json"
        credentials_file = Path(__file__).parent.parent / "secrets" / "google_drive_credentials.json"
        
        # Load existing token
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    raise FileNotFoundError(f"Google Drive credentials not found at {credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            token_file.parent.mkdir(exist_ok=True)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        service = build('drive', 'v3', credentials=creds)
        return service
        
    except ImportError:
        raise ImportError("Google Drive API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

def upload_book_to_drive(service, book_folder: Path, target_folder_id: str, logger):
    """Upload a book folder to Google Drive."""
    try:
        from googleapiclient.http import MediaFileUpload
        
        # Create folder for this book
        folder_metadata = {
            'name': book_folder.name,
            'parents': [target_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        book_folder_id = folder.get('id')
        
        logger.info(f"📁 Created Google Drive folder: {book_folder.name}")
        
        # Upload all files in the book folder
        uploaded_files = []
        for file_path in book_folder.iterdir():
            if file_path.is_file():
                file_metadata = {
                    'name': file_path.name,
                    'parents': [book_folder_id]
                }
                
                media = MediaFileUpload(str(file_path), resumable=True)
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size'
                ).execute()
                
                size_kb = int(file.get('size', 0)) / 1024
                logger.info(f"   📄 Uploaded: {file.get('name')} ({size_kb:.1f} KB)")
                uploaded_files.append(file.get('name'))
        
        # Create sharing link for the folder
        sharing_permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=book_folder_id,
            body=sharing_permission
        ).execute()
        
        # Get shareable link
        folder_info = service.files().get(
            fileId=book_folder_id, 
            fields='webViewLink'
        ).execute()
        
        share_link = folder_info.get('webViewLink')
        
        logger.info(f"✅ Book uploaded to Google Drive")
        logger.info(f"🔗 Share link: {share_link}")
        
        return {
            'folder_id': book_folder_id,
            'share_link': share_link,
            'uploaded_files': uploaded_files
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to upload to Google Drive: {e}")
        return None

def sync_all_books_to_drive():
    """Sync all generated books to Google Drive."""
    logger = get_logger('drive_sync')
    
    logger.info("☁️ Starting Google Drive sync...")
    
    try:
        # Set up Google Drive service
        service = setup_google_drive_service()
        
        # Your shared folder ID from the URL
        # https://drive.google.com/drive/folders/1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB?usp=sharing
        target_folder_id = "1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB"
        
        # Find all book directories
        output_dir = Path(__file__).parent.parent / "output" / "generated_books"
        book_dirs = [d for d in output_dir.iterdir() 
                    if d.is_dir() and d.name != 'archive']
        
        if not book_dirs:
            logger.warning("⚠️ No books found to sync")
            return
        
        # Check which books are already uploaded
        uploaded_books = get_uploaded_books(service, target_folder_id)
        
        new_uploads = 0
        for book_dir in book_dirs:
            if book_dir.name not in uploaded_books:
                logger.info(f"📤 Uploading new book: {book_dir.name}")
                result = upload_book_to_drive(service, book_dir, target_folder_id, logger)
                if result:
                    new_uploads += 1
                    
                    # Save upload info for tracking
                    upload_info_file = book_dir / "google_drive_info.json"
                    with open(upload_info_file, 'w') as f:
                        json.dump(result, f, indent=2)
            else:
                logger.info(f"✓ Already uploaded: {book_dir.name}")
        
        logger.info(f"✅ Google Drive sync complete: {new_uploads} new uploads")
        
        if new_uploads > 0:
            logger.info(f"📂 View all books: https://drive.google.com/drive/folders/{target_folder_id}")
        
        return new_uploads
        
    except Exception as e:
        logger.error(f"❌ Google Drive sync failed: {e}")
        return 0

def get_uploaded_books(service, folder_id: str):
    """Get list of already uploaded book folders."""
    try:
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = service.files().list(q=query, fields="files(name)").execute()
        items = results.get('files', [])
        return [item['name'] for item in items]
    except Exception:
        return []

def setup_google_drive_automation():
    """Set up Google Drive credentials and automation."""
    logger = get_logger('drive_setup')
    
    logger.info("🔧 Setting up Google Drive integration...")
    
    # Check if secrets directory exists
    secrets_dir = Path(__file__).parent.parent / "secrets"
    secrets_dir.mkdir(exist_ok=True)
    
    credentials_file = secrets_dir / "google_drive_credentials.json"
    
    if not credentials_file.exists():
        logger.info("📋 Google Drive Setup Instructions:")
        logger.info("1. Go to https://console.cloud.google.com/")
        logger.info("2. Create a new project or select existing project")
        logger.info("3. Enable Google Drive API")
        logger.info("4. Create credentials (OAuth 2.0 Client IDs)")
        logger.info("5. Download the credentials JSON file")
        logger.info(f"6. Save it as: {credentials_file}")
        logger.info("7. Run this script again")
        
        # Create template credentials file
        template = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID.googleusercontent.com",
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": ["http://localhost"]
            }
        }
        
        with open(credentials_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"📝 Template created at: {credentials_file}")
        logger.info("Replace the template values with your actual credentials")
        
        return False
    else:
        logger.info("✅ Google Drive credentials found")
        return True

def main():
    """Main function to sync books to Google Drive."""
    logger = get_logger('drive_sync')
    
    # Check setup
    if not setup_google_drive_automation():
        logger.info("⚠️ Complete Google Drive setup first")
        return False
    
    # Sync books
    uploaded_count = sync_all_books_to_drive()
    
    if uploaded_count > 0:
        logger.info(f"🎉 Successfully uploaded {uploaded_count} new books to Google Drive")
    else:
        logger.info("📁 All books are already synced to Google Drive")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)