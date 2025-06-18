#!/usr/bin/env python3
"""
Google Drive API Setup Script
Sets up authentication and tests connection to Google Drive
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for Google Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def setup_google_drive_auth():
    """Set up Google Drive authentication"""
    creds = None
    token_path = Path('token.json')
    credentials_path = Path('credentials.json')
    
    print("🔧 Setting up Google Drive API authentication...")
    
    # Check if credentials.json exists
    if not credentials_path.exists():
        print("❌ ERROR: credentials.json not found!")
        print("📋 Please follow the setup instructions in GOOGLE_DRIVE_SETUP.md")
        print("   1. Create Google Cloud project")
        print("   2. Enable Google Drive API") 
        print("   3. Download credentials.json file")
        return None
    
    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            print("   Your browser will open for authentication")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("✅ Token saved for future use")
    
    return creds

def test_drive_connection(creds, target_folder_id="1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB"):
    """Test connection to Google Drive and target folder"""
    try:
        service = build('drive', 'v3', credentials=creds)
        
        print("🧪 Testing Google Drive connection...")
        
        # Test basic connection
        about = service.about().get(fields="user").execute()
        user_email = about.get('user', {}).get('emailAddress', 'Unknown')
        print(f"✅ Connected as: {user_email}")
        
        # Test access to target folder
        folder = service.files().get(fileId=target_folder_id, fields="name,id").execute()
        folder_name = folder.get('name', 'Unknown')
        print(f"✅ Target folder accessible: '{folder_name}' ({target_folder_id})")
        
        # Create a test folder to verify write permissions
        test_folder_metadata = {
            'name': 'KindleMint_Test_Folder',
            'parents': [target_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        test_folder = service.files().create(body=test_folder_metadata, fields='id,name').execute()
        print(f"✅ Write test successful: Created test folder '{test_folder.get('name')}'")
        
        # Clean up test folder
        service.files().delete(fileId=test_folder.get('id')).execute()
        print("🧹 Test folder cleaned up")
        
        print("\n🎉 Google Drive setup completed successfully!")
        print("📁 Ready to sync books to your Drive folder")
        
        return True
        
    except Exception as e:
        print(f"❌ Drive connection test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("🚀 KINDLEMINT GOOGLE DRIVE SETUP")
    print("=" * 50)
    
    # Setup authentication
    creds = setup_google_drive_auth()
    
    if not creds:
        print("\n❌ Setup failed - please check credentials.json")
        return False
    
    print("✅ Authentication successful!")
    
    # Test connection
    if test_drive_connection(creds):
        print("\n🎯 Next Steps:")
        print("   1. Your Google Drive is now connected")
        print("   2. Books will automatically sync to your folder")
        print("   3. Run: python scripts/sync_to_google_drive.py")
        return True
    else:
        print("\n❌ Connection test failed")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        exit(1)