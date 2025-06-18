"""
Centralized file management for KindleMint book generation.
Ensures consistent output structure across all generation methods.
"""
from pathlib import Path
from datetime import datetime
import json
import shutil
from typing import Dict, Any, Optional

from kindlemint.utils.logger import get_logger

class FileManager:
    """Manages all file operations for book generation."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize file manager."""
        if project_root is None:
            # Auto-detect project root
            current = Path(__file__).parent
            while current.parent != current:
                if (current / "kindlemint").exists() and (current / ".git").exists():
                    project_root = current
                    break
                current = current.parent
            else:
                project_root = Path.cwd()
        
        self.project_root = project_root
        self.output_dir = project_root / "output" / "generated_books"
        self.logger = get_logger('file_manager')
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def cleanup_lambda_output(self):
        """Clean up redundant lambda/output directory."""
        lambda_output = self.project_root / "lambda" / "output"
        
        if lambda_output.exists():
            self.logger.info("🧹 Consolidating lambda/output into main output directory...")
            
            # Move any books from lambda/output to main output
            moved_count = 0
            for item in lambda_output.iterdir():
                if item.is_dir():
                    target_path = self.output_dir / item.name
                    if not target_path.exists():
                        shutil.move(str(item), str(target_path))
                        moved_count += 1
                        self.logger.info(f"📁 Moved: {item.name}")
                    else:
                        self.logger.info(f"⚠️ Skipped duplicate: {item.name}")
                elif item.is_file():
                    # Move individual files to archive or appropriate location
                    archive_dir = self.output_dir / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    target_file = archive_dir / item.name
                    if not target_file.exists():
                        shutil.move(str(item), str(target_file))
                        self.logger.info(f"📄 Archived file: {item.name}")
            
            # Remove lambda/output if empty
            remaining_items = list(lambda_output.iterdir())
            if not remaining_items:
                lambda_output.rmdir()
                self.logger.info("🗑️ Removed empty lambda/output directory")
            
            if moved_count > 0:
                self.logger.info(f"✅ Consolidated {moved_count} items from lambda/output")
            
            return moved_count
        
        return 0

def get_file_manager() -> FileManager:
    """Get global file manager instance."""
    return FileManager()