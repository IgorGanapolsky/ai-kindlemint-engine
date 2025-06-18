#!/usr/bin/env python3
"""
Log cleanup and consolidation script for KindleMint Engine.
Consolidates duplicate log files and implements rotation.
"""
import os
import sys
import shutil
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger, rotate_logs

def main():
    """Main cleanup function."""
    logger = get_logger('log_cleanup')
    
    logger.info("🧹 Starting log cleanup and consolidation...")
    
    # Trigger log rotation and cleanup
    rotate_logs()
    
    # Find and list all log files
    project_root = Path(__file__).parent.parent
    log_files = []
    
    for log_file in project_root.rglob("*.log"):
        # Skip virtual environment logs
        if 'venv' in str(log_file) or '__pycache__' in str(log_file):
            continue
        log_files.append(log_file)
    
    logger.info(f"Found {len(log_files)} log files:")
    for log_file in log_files:
        size_mb = log_file.stat().st_size / (1024 * 1024)
        logger.info(f"  {log_file.relative_to(project_root)}: {size_mb:.2f} MB")
    
    # Clean up any empty log directories
    empty_dirs = []
    for log_dir in project_root.rglob("logs"):
        if log_dir.is_dir() and not any(log_dir.iterdir()):
            empty_dirs.append(log_dir)
    
    for empty_dir in empty_dirs:
        logger.info(f"Removing empty log directory: {empty_dir.relative_to(project_root)}")
        empty_dir.rmdir()
    
    logger.info("✅ Log cleanup completed")
    
    # Show final log structure
    main_logs_dir = project_root / "logs"
    if main_logs_dir.exists():
        logger.info("\n📁 Final log structure:")
        for item in main_logs_dir.iterdir():
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                logger.info(f"  {item.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()