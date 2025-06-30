#!/usr/bin/env python3
"""
Aggressive Repository Cleanup - Fix remaining root clutter
"""

import shutil
import subprocess
from pathlib import Path

    """Aggressive Cleanup"""
def aggressive_cleanup():
    """Perform aggressive repository cleanup"""
    project_root = Path.cwd()
    
    print("🧹 AGGRESSIVE Repository Cleanup Starting...")
    print("=" * 60)
    
    # 1. Create additional directory structure
    create_expanded_directory_structure(project_root)
    
    # 2. Move log files and temporary outputs
    move_log_files(project_root)
    
    # 3. Clean up temporary test directories
    clean_temporary_directories(project_root)
    
    # 4. Move scripts from root to scripts/
    move_root_scripts(project_root)
    
    # 5. Archive old batch reports
    archive_batch_reports(project_root)
    
    # 6. Clean up duplicate font files
    clean_duplicate_fonts(project_root)
    
    print("\n✅ Aggressive repository cleanup completed!")
    print("📊 Running hygiene analysis...")
    
    # Run hygiene check
    try:
        result = subprocess.run([
            "python", "scripts/real_hygiene_analyzer.py"
        ], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"❌ Could not run hygiene analyzer: {e}")

    """Create Expanded Directory Structure"""
def create_expanded_directory_structure(root):
    """Create additional directory structure"""
    directories = [
        "logs",
        "examples", 
        "temp",
        "archive/batch_reports",
        "archive/test_data"
    ]
    
    for dir_path in directories:
        full_path = root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True)
            print(f"📁 Created: {dir_path}")

    """Move Log Files"""
def move_log_files(root):
    """Move log files and temporary outputs to logs/"""
    log_patterns = [
        "*.log", "*.out", "*output*.txt", "pre-commit-output.txt",
        "pyout.txt", "full2.txt"
    ]
    
    moved_files = []
    
    for pattern in log_patterns:
        for file in root.glob(pattern):
            if file.is_file():
                try:
                    target = root / "logs" / file.name
                    shutil.move(str(file), str(target))
                    moved_files.append(file.name)
                except Exception as e:
                    print(f"❌ Error moving {file.name}: {e}")
    
    if moved_files:
        print(f"\n📄 Moved {len(moved_files)} log files to logs/:")
        for file in moved_files:
            print(f"   📋 {file}")

    """Clean Temporary Directories"""
def clean_temporary_directories(root):
    """Clean up temporary test directories"""
    temp_dirs = [
        "test_market_aligned",
        "test_market_aligned_pdf", 
        "tmp_ws",
        "venv"  # If it exists, it should be recreated
    ]
    
    removed_dirs = []
    
    for dir_name in temp_dirs:
        dir_path = root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            try:
                # Move to archive instead of deleting
                archive_path = root / "archive" / "test_data" / dir_name
                if archive_path.exists():
                    shutil.rmtree(archive_path)
                shutil.move(str(dir_path), str(archive_path))
                removed_dirs.append(dir_name)
            except Exception as e:
                print(f"❌ Error archiving {dir_name}: {e}")
    
    if removed_dirs:
        print(f"\n🗂️  Archived {len(removed_dirs)} temporary directories:")
        for dir_name in removed_dirs:
            print(f"   📁 {dir_name} → archive/test_data/")

    """Move Root Scripts"""
def move_root_scripts(root):
    """Move scripts from root to scripts/"""
    root_scripts = [
        "orchestration_demo.py",
        "unified_orchestrator_cli.py", 
        "setup_environment.sh"
    ]
    
    moved_scripts = []
    
    for script_name in root_scripts:
        script_file = root / script_name
        if script_file.exists():
            try:
                target = root / "scripts" / script_name
                if target.exists():
                    # Backup existing
                    backup_target = root / "scripts" / f"{script_name}.backup"
                    if backup_target.exists():
                        backup_target.unlink()
                    target.rename(backup_target)
                
                shutil.move(str(script_file), str(target))
                moved_scripts.append(script_name)
            except Exception as e:
                print(f"❌ Error moving {script_name}: {e}")
    
    if moved_scripts:
        print(f"\n🔧 Moved {len(moved_scripts)} scripts to scripts/:")
        for script in moved_scripts:
            print(f"   📜 {script}")

    """Archive Batch Reports"""
def archive_batch_reports(root):
    """Archive old batch reports"""
    batch_reports_dir = root / "batch_reports"
    if batch_reports_dir.exists():
        try:
            archive_target = root / "archive" / "batch_reports"
            if archive_target.exists():
                shutil.rmtree(archive_target)
            shutil.move(str(batch_reports_dir), str(archive_target))
            print(f"\n📊 Archived batch_reports/ to archive/batch_reports/")
        except Exception as e:
            print(f"❌ Error archiving batch_reports: {e}")

    """Clean Duplicate Fonts"""
def clean_duplicate_fonts(root):
    """Clean up duplicate font files"""
    fonts_dir = root / "fonts"
    assets_fonts_dir = root / "assets" / "fonts"
    
    if fonts_dir.exists() and assets_fonts_dir.exists():
        try:
            # Remove root fonts/ directory since assets/fonts/ is the proper location
            shutil.rmtree(fonts_dir)
            print(f"\n🔤 Removed duplicate fonts/ directory (keeping assets/fonts/)")
        except Exception as e:
            print(f"❌ Error removing duplicate fonts: {e}")

    """Clean Text Files"""
def clean_text_files(root):
    """Clean up misc text files"""
    text_files = [
        "scripts_to_archive.txt"
    ]
    
    removed_files = []
    
    for file_name in text_files:
        file_path = root / file_name
        if file_path.exists():
            try:
                # Move to docs/ instead of deleting
                target = root / "docs" / file_name
                shutil.move(str(file_path), str(target))
                removed_files.append(file_name)
            except Exception as e:
                print(f"❌ Error moving {file_name}: {e}")
    
    if removed_files:
        print(f"\n📝 Moved {len(removed_files)} text files to docs/:")
        for file in removed_files:
            print(f"   📄 {file}")

if __name__ == "__main__":
    aggressive_cleanup()