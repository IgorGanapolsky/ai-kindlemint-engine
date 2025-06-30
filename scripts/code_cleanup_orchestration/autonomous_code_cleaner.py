#!/usr/bin/env python3
"""
Autonomous Code Cleanup Orchestrator
Immediately identifies and removes dead files, duplicate code, and unnecessary files
"""

import hashlib
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class AutonomousCodeCleaner:
    """
    Autonomous code cleanup system that immediately cleans the codebase
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "files_removed": [],
            "duplicates_removed": [],
            "bytes_saved": 0,
            "directories_cleaned": [],
            "summary": {},
        }

        # Patterns for files that are likely safe to remove
        self.safe_removal_patterns = [
            r".*\.pyc$",
            r".*\.pyo$",
            r".*/__pycache__/.*",
            r".*\.DS_Store$",
            r".*\.pytest_cache/.*",
            r".*\.coverage$",
            r".*\.coverage\..*",
            r".*\.log$",
            r".*\.tmp$",
            r".*\.temp$",
            r".*\.bak$",
            r".*\.backup$",
            r".*~$",
            r".*\.swp$",
            r".*\.swo$",
        ]

        # High-confidence duplicate removal patterns
        self.duplicate_removal_patterns = [
            "archive/obsolete_scripts_backup/",
            "archive/scripts_backup_2025/",
            ".pytest_tmp/",
            "__pycache__/",
            ".coverage",
            "*.pyc",
            "*.pyo",
            "*.log",
            "*.tmp",
        ]

        print(f"🧹 Autonomous Code Cleaner initialized for: {self.repo_path}")

    def run_immediate_cleanup(self) -> Dict[str, Any]:
        """Run immediate autonomous cleanup"""
        print("🚀 STARTING IMMEDIATE CODE CLEANUP...")

        # Step 1: Remove obvious junk files
        self.remove_cache_and_temp_files()

        # Step 2: Clean archive directories
        self.clean_archive_directories()

        # Step 3: Remove duplicate files
        self.remove_duplicate_files()

        # Step 4: Remove empty directories
        self.remove_empty_directories()

        # Step 5: Generate cleanup report
        self.generate_cleanup_report()

        # Step 6: Rotate old cleanup reports (keep last 3)
        self._rotate_old_reports()

        print(f"✅ CLEANUP COMPLETE! Saved {self.cleanup_results['bytes_saved']} bytes")
        return self.cleanup_results

    def remove_cache_and_temp_files(self):
        """Remove cache, temp, and build artifacts"""
        print("🗑️  Removing cache and temp files...")

        cache_patterns = [
            "**/__pycache__",
            "**/.pytest_cache",
            "**/*.pyc",
            "**/*.pyo",
            "**/.DS_Store",
            "**/*.log",
            "**/*.tmp",
            "**/*.bak",
            "**/*~",
            "**/.coverage*",
            "**/coverage.xml",
            "**/test-results.xml",
        ]

        removed_count = 0
        bytes_saved = 0

        for pattern in cache_patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.exists():
                    try:
                        size = self.get_file_size(file_path)
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)

                        self.cleanup_results["files_removed"].append(
                            str(file_path.relative_to(self.repo_path))
                        )
                        removed_count += 1
                        bytes_saved += size
                        print(f"   ✓ Removed: {file_path.relative_to(self.repo_path)}")
                    except Exception as e:
                        print(f"   ⚠️ Could not remove {file_path}: {e}")

        self.cleanup_results["bytes_saved"] += bytes_saved
        print(f"   📊 Removed {removed_count} cache/temp files ({bytes_saved} bytes)")

    def clean_archive_directories(self):
        """Clean up archive and backup directories"""
        print("🗂️  Cleaning archive directories...")

        archive_dirs = [
            "archive/obsolete_scripts_backup",
            "archive/scripts_backup_2025",
            ".pytest_tmp",
        ]

        for archive_dir in archive_dirs:
            archive_path = self.repo_path / archive_dir
            if archive_path.exists() and archive_path.is_dir():
                try:
                    self.get_directory_size(archive_path)

                    # For archive directories, we'll be more selective
                    # Remove only obvious duplicates and very old files
                    files_removed = self.clean_archive_directory_selective(archive_path)

                    if files_removed > 0:
                        self.cleanup_results["directories_cleaned"].append(archive_dir)
                        print(
                            f"   ✓ Cleaned {archive_dir}: {files_removed} files removed"
                        )

                except Exception as e:
                    print(f"   ⚠️ Could not clean {archive_dir}: {e}")

    def clean_archive_directory_selective(self, archive_path: Path) -> int:
        """Selectively clean an archive directory"""
        files_removed = 0

        # Remove obvious duplicates and build artifacts from archives
        patterns_to_remove = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.DS_Store",
            "**/*.log",
            "**/*.tmp",
        ]

        for pattern in patterns_to_remove:
            for file_path in archive_path.glob(pattern):
                if file_path.exists():
                    try:
                        size = self.get_file_size(file_path)
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)

                        self.cleanup_results["files_removed"].append(
                            str(file_path.relative_to(self.repo_path))
                        )
                        self.cleanup_results["bytes_saved"] += size
                        files_removed += 1

                    except Exception as e:
                        print(f"     ⚠️ Could not remove {file_path}: {e}")

        return files_removed

    def remove_duplicate_files(self):
        """Remove duplicate files based on content hash"""
        print("🔍 Finding and removing duplicate files...")

        file_hashes = defaultdict(list)

        # Scan all Python files and other important files including PDFs and images
        for file_path in self.repo_path.rglob("*"):
            if (
                file_path.is_file()
                and not self.is_in_ignored_directory(file_path)
                and file_path.suffix
                in [
                    ".py",
                    ".md",
                    ".txt",
                    ".json",
                    ".yaml",
                    ".yml",
                    ".pdf",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".epub",
                    ".mobi",
                ]
            ):

                try:
                    content_hash = self.get_file_hash(file_path)
                    file_hashes[content_hash].append(file_path)
                except Exception:
                    continue

        # Find duplicates and remove them intelligently
        duplicates_removed = 0
        for content_hash, file_list in file_hashes.items():
            if len(file_list) > 1:
                # Keep the file in the most "canonical" location
                # Prefer: scripts/ > src/ > tests/ > archive/
                sorted_files = sorted(file_list, key=self.get_file_priority)

                # Keep the first (highest priority) file, remove the rest
                keep_file = sorted_files[0]
                remove_files = sorted_files[1:]

                for remove_file in remove_files:
                    # Enhanced duplicate removal logic
                    should_remove = False

                    # Always remove if in archive, backup, or temp directories
                    if (
                        "archive" in str(remove_file)
                        or "backup" in str(remove_file)
                        or "BACKUP" in str(remove_file)
                        or ".pytest_tmp" in str(remove_file)
                    ):
                        should_remove = True

                    # For PDFs and books: Remove if filename suggests it's intermediate/draft
                    elif remove_file.suffix == ".pdf":
                        name_lower = remove_file.stem.lower()
                        # Extended list of indicators for intermediate/test files
                        removal_indicators = [
                            "interior",
                            "draft",
                            "old",
                            "temp",
                            "backup",
                            "canvas",
                            "test",
                            "fixed",
                            "render",
                            "direct",
                            "broken",
                            "bad",
                            "copy",
                            "dup",
                            "duplicate",
                        ]
                        if any(x in name_lower for x in removal_indicators):
                            # But keep if it's the only PDF in the directory
                            pdf_count = len(list(remove_file.parent.glob("*.pdf")))
                            if pdf_count > 1:
                                should_remove = True

                    # For duplicate images: Remove if they are backups
                    elif remove_file.suffix in [".png", ".jpg", ".jpeg"]:
                        if (
                            "BACKUP" in remove_file.stem
                            or "_backup" in remove_file.stem
                        ):
                            should_remove = True

                    if should_remove:
                        try:
                            size = remove_file.stat().st_size
                            remove_file.unlink()

                            self.cleanup_results["duplicates_removed"].append(
                                {
                                    "removed": str(
                                        remove_file.relative_to(self.repo_path)
                                    ),
                                    "kept": str(keep_file.relative_to(self.repo_path)),
                                    "size": size,
                                }
                            )
                            self.cleanup_results["bytes_saved"] += size
                            duplicates_removed += 1
                            print(
                                f"   ✓ Removed duplicate: {remove_file.relative_to(self.repo_path)}"
                            )

                        except Exception as e:
                            print(f"   ⚠️ Could not remove duplicate {remove_file}: {e}")

        print(f"   📊 Removed {duplicates_removed} duplicate files")

    def remove_empty_directories(self):
        """Remove empty directories"""
        print("📁 Removing empty directories...")

        removed_count = 0

        # Find all directories in reverse order (deepest first)
        all_dirs = []
        for root, dirs, files in os.walk(self.repo_path):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                all_dirs.append(dir_path)

        # Sort by depth (deepest first)
        all_dirs.sort(key=lambda x: len(x.parts), reverse=True)

        for dir_path in all_dirs:
            if (
                dir_path.exists()
                and dir_path.is_dir()
                and not self.is_important_directory(dir_path)
                and not list(dir_path.iterdir())
            ):  # Empty directory
                try:
                    dir_path.rmdir()
                    self.cleanup_results["files_removed"].append(
                        str(dir_path.relative_to(self.repo_path)) + "/"
                    )
                    removed_count += 1
                    print(
                        f"   ✓ Removed empty directory: {dir_path.relative_to(self.repo_path)}"
                    )
                except Exception:
                    continue

        print(f"   📊 Removed {removed_count} empty directories")

    def get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file content"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except Exception:
            return ""

    def get_file_size(self, file_path: Path) -> int:
        """Get file or directory size in bytes"""
        if file_path.is_file():
            return file_path.stat().st_size
        elif file_path.is_dir():
            return self.get_directory_size(file_path)
        return 0

    def get_directory_size(self, dir_path: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                file_path = Path(root) / file_name
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    continue
        return total_size

    def get_file_priority(self, file_path: Path) -> int:
        """Get priority score for keeping a file (lower = keep)"""
        path_str = str(file_path).lower()

        if "scripts/" in path_str and "archive" not in path_str:
            return 1
        elif "src/" in path_str:
            return 2
        elif "tests/" in path_str:
            return 3
        elif "lambda/" in path_str:
            return 4
        elif "archive" in path_str:
            return 100
        elif "backup" in path_str:
            return 101
        elif ".pytest_tmp" in path_str:
            return 102
        else:
            return 50

    def is_in_ignored_directory(self, file_path: Path) -> bool:
        """Check if file is in a directory we should ignore"""
        ignored_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__"}

        for part in file_path.parts:
            if part in ignored_dirs:
                return True
        return False

    def is_important_directory(self, dir_path: Path) -> bool:
        """Check if directory should never be removed"""
        important_dirs = {
            ".git",
            ".github",
            "src",
            "scripts",
            "tests",
            "lambda",
            "output",
            "kindlemint",
            "config",
            "docs",
        }

        dir_name = dir_path.name
        return dir_name in important_dirs or dir_path == self.repo_path

    def generate_cleanup_report(self):
        """Generate cleanup report"""
        report_path = (
            self.repo_path
            / "scripts/code_cleanup_orchestration/reports/cleanup_report.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        self.cleanup_results["summary"] = {
            "total_files_removed": len(self.cleanup_results["files_removed"]),
            "total_duplicates_removed": len(self.cleanup_results["duplicates_removed"]),
            "total_bytes_saved": self.cleanup_results["bytes_saved"],
            "total_directories_cleaned": len(
                self.cleanup_results["directories_cleaned"]
            ),
            "mb_saved": round(self.cleanup_results["bytes_saved"] / (1024 * 1024), 2),
        }

        with open(report_path, "w") as f:
            json.dump(self.cleanup_results, f, indent=2)

        print(f"📊 Cleanup report saved to: {report_path}")

        # Print summary
        summary = self.cleanup_results["summary"]
        print("\n" + "=" * 50)
        print("🎉 CLEANUP SUMMARY")
        print("=" * 50)
        print(f"Files removed: {summary['total_files_removed']}")
        print(f"Duplicates removed: {summary['total_duplicates_removed']}")
        print(f"Directories cleaned: {summary['total_directories_cleaned']}")
        print(f"Space saved: {summary['mb_saved']} MB")
        print("=" * 50)

    def _rotate_old_reports(self):
        """Keep only the last 3 cleanup reports"""
        reports_dir = self.repo_path / "scripts/code_cleanup_orchestration/reports"
        if not reports_dir.exists():
            return

        # Find all cleanup reports
        report_files = list(reports_dir.glob("cleanup_report*.json"))

        if len(report_files) <= 3:
            return

        # Sort by modification time (oldest first)
        report_files.sort(key=lambda f: f.stat().st_mtime)

        # Remove old reports
        to_remove = report_files[:-3]  # Keep last 3
        for old_report in to_remove:
            try:
                old_report.unlink()
                print(f"   ✓ Rotated old report: {old_report.name}")
            except Exception:
                pass


def main():
    """Main entry point for autonomous code cleanup"""
    print("🤖 AUTONOMOUS CODE CLEANUP ORCHESTRATOR")
    print("=" * 50)

    # Initialize and run cleanup
    cleaner = AutonomousCodeCleaner()
    results = cleaner.run_immediate_cleanup()

    # Success!
    print("\n✅ AUTONOMOUS CODE CLEANUP COMPLETE!")
    print(f"🎯 Total cleanup: {results['summary']['mb_saved']} MB saved")

    return results


if __name__ == "__main__":
    main()
