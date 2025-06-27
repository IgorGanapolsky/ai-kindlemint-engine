#!/usr/bin/env python3
"""
Archive Published Books to GitHub LFS
Moves completed books from active_production to published_archive
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


class BookArchiver:
    """Archive published books to GitHub LFS for long-term storage."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.active_dir = self.base_dir / "books" / "active_production"
        self.archive_dir = self.base_dir / "books" / "published_archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def check_git_lfs(self):
        """Verify Git LFS is installed and initialized."""
        try:
            result = subprocess.run(["git", "lfs", "version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Git LFS is not installed. Please install it first:")
                print("   brew install git-lfs")
                print("   git lfs install")
                return False
            return True
        except FileNotFoundError:
            print("❌ Git is not installed")
            return False
    
    def get_book_info(self, book_path: Path) -> dict:
        """Extract book metadata from the directory structure."""
        info = {
            "series_name": book_path.parent.name,
            "volume": book_path.name,
            "path": book_path,
            "files": {
                "paperback": list(book_path.glob("paperback/*.pdf")),
                "kindle": list(book_path.glob("kindle/*.epub")),
                "hardcover": list(book_path.glob("hardcover/*.pdf")),
                "puzzles": len(list(book_path.glob("puzzles/puzzles/*.png")))
            }
        }
        return info
    
    def archive_book(self, series_name: str, volume: str, keep_puzzles: bool = False):
        """Archive a specific book to GitHub LFS."""
        source_path = self.active_dir / series_name / volume
        
        if not source_path.exists():
            print(f"❌ Book not found: {source_path}")
            return False
        
        # Get book info
        book_info = self.get_book_info(source_path)
        
        # Create archive path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        archive_path = self.archive_dir / f"{series_name}_{timestamp}" / volume
        
        print(f"📚 Archiving: {series_name} - {volume}")
        print(f"📁 From: {source_path}")
        print(f"📁 To: {archive_path}")
        
        # Create archive metadata
        metadata = {
            "archived_date": datetime.now().isoformat(),
            "series_name": series_name,
            "volume": volume,
            "file_counts": book_info["files"],
            "archive_version": "1.0"
        }
        
        # Copy files to archive
        directories_to_copy = ["paperback", "kindle", "hardcover", "metadata"]
        if not keep_puzzles:
            # Skip puzzle images to save space
            print("💾 Skipping puzzle images (regeneratable)")
        else:
            directories_to_copy.append("puzzles")
        
        for dir_name in directories_to_copy:
            source_dir = source_path / dir_name
            if source_dir.exists():
                dest_dir = archive_path / dir_name
                print(f"  📂 Copying {dir_name}/")
                shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        
        # Save archive metadata
        metadata_path = archive_path / "archive_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Add to Git LFS
        print("🔄 Adding to Git LFS...")
        os.chdir(self.base_dir)
        
        # Add files to git
        subprocess.run(["git", "add", str(archive_path.relative_to(self.base_dir))])
        
        # Remove from active production
        if self.confirm_removal(source_path):
            print("🗑️  Removing from active_production...")
            shutil.rmtree(source_path)
            
            # Clean up empty series directory
            if not list(source_path.parent.iterdir()):
                source_path.parent.rmdir()
        
        print(f"✅ Archived successfully: {archive_path}")
        return True
    
    def confirm_removal(self, path: Path) -> bool:
        """Confirm before removing from active production."""
        response = input(f"\n⚠️  Remove from active production? {path} [y/N]: ")
        return response.lower() == 'y'
    
    def list_active_books(self):
        """List all books in active production."""
        print("\n📚 Books in Active Production:")
        print("="*60)
        
        for series_dir in sorted(self.active_dir.iterdir()):
            if series_dir.is_dir():
                print(f"\n📗 {series_dir.name}")
                for volume_dir in sorted(series_dir.iterdir()):
                    if volume_dir.is_dir():
                        info = self.get_book_info(volume_dir)
                        print(f"  📖 {volume_dir.name}")
                        print(f"     PDF: {len(info['files']['paperback'])}")
                        print(f"     EPUB: {len(info['files']['kindle'])}")
                        print(f"     Puzzles: {info['files']['puzzles']}")
    
    def archive_series(self, series_name: str, keep_puzzles: bool = False):
        """Archive all volumes in a series."""
        series_path = self.active_dir / series_name
        
        if not series_path.exists():
            print(f"❌ Series not found: {series_path}")
            return False
        
        volumes = [d for d in series_path.iterdir() if d.is_dir()]
        print(f"📚 Found {len(volumes)} volumes to archive")
        
        for volume_dir in sorted(volumes):
            self.archive_book(series_name, volume_dir.name, keep_puzzles)
        
        return True
    
    def commit_archives(self, message: str = None):
        """Commit archived books to Git with LFS."""
        os.chdir(self.base_dir)
        
        if not message:
            message = f"Archive published books - {datetime.now().strftime('%Y-%m-%d')}"
        
        print("\n📤 Committing to Git LFS...")
        subprocess.run(["git", "add", ".gitattributes"])
        subprocess.run(["git", "add", "books/published_archive/"])
        
        result = subprocess.run(["git", "commit", "-m", message], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Committed to Git LFS successfully")
            print("\n💡 Don't forget to push: git push origin main")
        else:
            print("⚠️  Nothing to commit or commit failed")
            print(result.stderr)


def main():
    """Main entry point for book archiver."""
    parser = argparse.ArgumentParser(description='Archive published books to GitHub LFS')
    parser.add_argument('--list', action='store_true', 
                        help='List all books in active production')
    parser.add_argument('--series', help='Archive all volumes in a series')
    parser.add_argument('--book', nargs=2, metavar=('SERIES', 'VOLUME'),
                        help='Archive a specific book')
    parser.add_argument('--keep-puzzles', action='store_true',
                        help='Keep puzzle images (default: skip to save space)')
    parser.add_argument('--commit', action='store_true',
                        help='Commit archives to Git after archiving')
    parser.add_argument('--message', help='Custom commit message')
    
    args = parser.parse_args()
    
    archiver = BookArchiver()
    
    # Check Git LFS
    if not archiver.check_git_lfs():
        return 1
    
    # Execute command
    if args.list:
        archiver.list_active_books()
    elif args.series:
        archiver.archive_series(args.series, args.keep_puzzles)
        if args.commit:
            archiver.commit_archives(args.message)
    elif args.book:
        series, volume = args.book
        archiver.archive_book(series, volume, args.keep_puzzles)
        if args.commit:
            archiver.commit_archives(args.message)
    else:
        # Default: list books
        archiver.list_active_books()
        print("\n💡 Usage examples:")
        print("  Archive a series: python scripts/archive_published_books.py --series Large_Print_Sudoku_Masters")
        print("  Archive one book: python scripts/archive_published_books.py --book Large_Print_Sudoku_Masters volume_1")
        print("  Keep puzzle images: python scripts/archive_published_books.py --series Large_Print_Sudoku_Masters --keep-puzzles")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())