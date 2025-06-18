# Simple Google Drive Setup (No App Verification Required)

## Method 1: Use Google Apps Script (Recommended)

1. **Go to Google Apps Script**: https://script.google.com/
2. **Create New Project**: Click "New project"
3. **Paste this code**:

```javascript
function uploadKindleMintBooks() {
  // Get your target folder ID from the URL
  var targetFolderId = "1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB";
  var targetFolder = DriveApp.getFolderById(targetFolderId);
  
  Logger.log("Ready to upload books to: " + targetFolder.getName());
  Logger.log("Use the file upload dialog or drag files into this folder");
  
  return "Setup complete! You can now upload books manually or use the Drive web interface";
}

function createBookFolder(bookName) {
  var targetFolderId = "1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB";
  var targetFolder = DriveApp.getFolderById(targetFolderId);
  
  var bookFolder = targetFolder.createFolder(bookName);
  Logger.log("Created folder: " + bookName);
  Logger.log("Folder URL: " + bookFolder.getUrl());
  
  return bookFolder.getUrl();
}
```

4. **Save**: Click "Save" (disk icon)
5. **Run**: Click "Run" to test
6. **Authorize**: Grant permissions when prompted

## Method 2: Manual Upload Process

For now, while we fix the OAuth verification, here's the manual process:

1. **Open Google Drive**: https://drive.google.com/
2. **Navigate to your folder**: https://drive.google.com/drive/folders/1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB
3. **Create folders** for each book volume:
   - `Large Print Crossword Masters Vol 1`
   - `Large Print Crossword Masters Vol 2`
   - `Large Print Crossword Masters Vol 3`
   - `Large Print Crossword Masters Vol 4`
   - `Large Print Crossword Masters Vol 5`

4. **Upload files** from each book folder in `output/generated_books/`

## Method 3: Use Google Drive Desktop App

1. **Install Google Drive Desktop**: https://www.google.com/drive/download/
2. **Sync your folder**: Right-click the folder and select "Available offline"
3. **Copy files** directly to the synced folder on your computer

## Temporary Workaround Script

```bash
# Create a simple backup script
#!/bin/bash
echo "📁 Creating manual backup folders..."

# Copy all generated books to a backup directory
cp -r output/generated_books/ ~/Desktop/KindleMint_Backup/

echo "✅ Backup created at ~/Desktop/KindleMint_Backup/"
echo "📤 Now manually upload these folders to Google Drive"
```

## Why the OAuth App Verification Failed

The Google Drive API requires app verification for production use. Your app is currently "unverified" which triggers the security warning. Options:

1. **Use manual upload** (current workaround)
2. **Submit app for verification** (takes 1-2 weeks)
3. **Use Google Apps Script** (no verification needed)
4. **Add test users** to the OAuth consent screen

## Next Steps

1. Use Method 1 (Google Apps Script) for automated folder creation
2. Use Method 2 (manual upload) for immediate file transfer
3. Continue with book generation and publishing workflow
4. We'll fix the OAuth verification separately

The book generation works perfectly - this is just a Drive backup issue!