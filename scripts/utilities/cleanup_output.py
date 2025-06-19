#!/usr/bin/env python3
"""
Clean up output directory - remove duplicates and organize properly
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_output_directory():
    """Clean up the messy output directory and keep only what's needed"""
    
    print("🧹 Cleaning up output directory...")
    
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Output directory not found")
        return
    
    # Create backup first
    backup_dir = Path("output_backup_" + datetime.now().strftime('%Y%m%d_%H%M%S'))
    print(f"📦 Creating backup at: {backup_dir}")
    shutil.copytree(output_dir, backup_dir)
    
    # Identify what to keep
    keep_folders = [
        "PUBLISHING_READY",  # Our final organized structure
    ]
    
    # Identify duplicates and wrong folders to remove
    generated_books_dir = output_dir / "generated_books"
    if generated_books_dir.exists():
        print(f"📁 Found generated_books with {len(list(generated_books_dir.iterdir()))} items")
        
        # Keep only the correctly numbered latest volumes
        correct_volumes = {}
        
        for folder in generated_books_dir.iterdir():
            if folder.is_dir():
                folder_name = folder.name
                print(f"   📂 Analyzing: {folder_name}")
                
                # Keep the correctly numbered volumes (latest timestamp for each)
                if "crossword_masters_vol_1_" in folder_name and folder_name.endswith("122347"):
                    correct_volumes[1] = folder
                    print(f"      ✅ Keeping Volume 1: {folder_name}")
                elif "crossword_masters_vol_2_" in folder_name:
                    correct_volumes[2] = folder
                    print(f"      ✅ Keeping Volume 2: {folder_name}")
                elif "crossword_masters_vol_3_" in folder_name:
                    correct_volumes[3] = folder
                    print(f"      ✅ Keeping Volume 3: {folder_name}")
                elif "crossword_masters_vol_4_" in folder_name:
                    correct_volumes[4] = folder
                    print(f"      ✅ Keeping Volume 4: {folder_name}")
                elif "crossword_masters_vol_5_" in folder_name:
                    correct_volumes[5] = folder
                    print(f"      ✅ Keeping Volume 5: {folder_name}")
                else:
                    print(f"      🗑️  Will remove duplicate/incorrect: {folder_name}")
        
        print(f"\n📊 Found {len(correct_volumes)} correct volumes to keep")
        
        # Remove generated_books and recreate with only correct volumes
        print("🗑️  Removing messy generated_books directory...")
        
        # Create clean generated_books
        clean_generated_dir = output_dir / "generated_books_clean"
        clean_generated_dir.mkdir(exist_ok=True)
        
        # Copy only correct volumes
        for vol_num, folder in correct_volumes.items():
            new_name = f"large_print_crossword_masters_vol_{vol_num}_final"
            target = clean_generated_dir / new_name
            shutil.copytree(folder, target)
            print(f"   ✅ Cleaned Volume {vol_num}: {new_name}")
        
        # Remove old generated_books
        shutil.rmtree(generated_books_dir)
        
        # Rename clean version
        clean_generated_dir.rename(generated_books_dir)
    
    # Remove other messy folders
    folders_to_remove = [
        "KDP_READY",
        "READY_FOR_GOOGLE_DRIVE",
    ]
    
    for folder_name in folders_to_remove:
        folder_path = output_dir / folder_name
        if folder_path.exists():
            print(f"🗑️  Removing duplicate folder: {folder_name}")
            shutil.rmtree(folder_path)
    
    # Clean up any other random files
    for item in output_dir.iterdir():
        if item.is_file() and item.suffix in ['.md', '.json']:
            if "publishing_checklist" in item.name or "series_manifest" in item.name:
                print(f"🗑️  Removing duplicate file: {item.name}")
                item.unlink()
    
    print("\n✅ Cleanup completed!")
    print("📁 Final structure:")
    print("   output/")
    print("   ├── generated_books/ (5 clean volumes)")
    print("   └── PUBLISHING_READY/ (final organized structure)")
    print(f"   📦 Backup available at: {backup_dir}")

def show_clean_structure():
    """Show the cleaned directory structure"""
    print("\n📋 CLEAN OUTPUT STRUCTURE:")
    
    output_dir = Path("output")
    if output_dir.exists():
        for item in sorted(output_dir.iterdir()):
            if item.is_dir():
                print(f"📁 {item.name}/")
                if item.name == "generated_books":
                    for subitem in sorted(item.iterdir()):
                        if subitem.is_dir():
                            print(f"   📖 {subitem.name}/")
                elif item.name == "PUBLISHING_READY":
                    for subitem in sorted(item.iterdir()):
                        print(f"   📄 {subitem.name}")
            else:
                print(f"📄 {item.name}")

if __name__ == "__main__":
    cleanup_output_directory()
    show_clean_structure()
    
    print("\n🎯 WHAT TO USE:")
    print("✅ Use: output/PUBLISHING_READY/ - This is your final organized structure")
    print("✅ Backup: output/generated_books/ - Clean volume source files")
    print("🗑️  Removed: All duplicate and incorrectly named folders")
    print("\n🚀 Ready to proceed with publishing using PUBLISHING_READY folder!")