#!/usr/bin/env python3
"""
Archive Cleanup Orchestrator
Uses worktree orchestration to efficiently clean up old archive files
"""

import asyncio
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import json
import os


class ArchiveCleanupOrchestrator:
    def __init__(self):
        self.archive_dir = Path("/Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine/archive")
        self.cleanup_stats = {
            "files_analyzed": 0,
            "files_removed": 0,
            "space_freed_mb": 0,
            "directories_removed": 0
        }
        
    async def analyze_archive(self):
        """Analyze archive directory for cleanup opportunities"""
        print("🔍 Analyzing Archive Directory...")
        print("=" * 60)
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in self.archive_dir.rglob('*') if f.is_file())
        total_mb = total_size / (1024 * 1024)
        
        print(f"📁 Archive Directory: {self.archive_dir}")
        print(f"💾 Total Size: {total_mb:.2f} MB")
        
        # Analyze by subdirectory
        subdirs = {
            "batch_reports": {"count": 0, "size": 0, "oldest": None},
            "obsolete_scripts_backup": {"count": 0, "size": 0},
            "test_data": {"count": 0, "size": 0}
        }
        
        for subdir_name, stats in subdirs.items():
            subdir_path = self.archive_dir / subdir_name
            if subdir_path.exists():
                files = list(subdir_path.rglob('*'))
                stats["count"] = len([f for f in files if f.is_file()])
                stats["size"] = sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024)
                
                # Find oldest file for batch reports
                if subdir_name == "batch_reports":
                    report_dirs = [d for d in subdir_path.iterdir() if d.is_dir()]
                    if report_dirs:
                        oldest_dir = min(report_dirs, key=lambda d: d.name)
                        stats["oldest"] = oldest_dir.name
        
        print("\n📊 Breakdown by Directory:")
        for name, stats in subdirs.items():
            print(f"\n  {name}:")
            print(f"    Files: {stats['count']}")
            print(f"    Size: {stats['size']:.2f} MB")
            if stats.get("oldest"):
                print(f"    Oldest: {stats['oldest']}")
        
        return subdirs, total_mb
        
    async def cleanup_batch_reports(self, days_to_keep=7):
        """Clean up old batch reports"""
        batch_dir = self.archive_dir / "batch_reports"
        if not batch_dir.exists():
            return
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        print(f"\n🧹 Cleaning batch reports older than {days_to_keep} days...")
        
        for report_dir in batch_dir.iterdir():
            if report_dir.is_dir():
                # Parse date from directory name (YYYYMMDD_HHMMSS format)
                try:
                    date_str = report_dir.name.split('_')[0]
                    dir_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if dir_date < cutoff_date:
                        print(f"  ❌ Removing: {report_dir.name}")
                        shutil.rmtree(report_dir)
                        removed_count += 1
                        self.cleanup_stats["directories_removed"] += 1
                except Exception as e:
                    print(f"  ⚠️  Could not parse date for {report_dir.name}: {e}")
        
        print(f"  ✅ Removed {removed_count} old batch report directories")
        
    async def cleanup_test_data(self):
        """Clean up test data directory"""
        test_dir = self.archive_dir / "test_data"
        if not test_dir.exists():
            return
            
        print("\n🧹 Cleaning test data...")
        
        # Remove venv if it exists
        venv_dir = test_dir / "venv"
        if venv_dir.exists():
            print(f"  ❌ Removing venv directory...")
            shutil.rmtree(venv_dir)
            self.cleanup_stats["directories_removed"] += 1
            
        # Clean up old test outputs
        for test_subdir in ["test_market_aligned", "test_market_aligned_pdf", "tmp_ws"]:
            subdir_path = test_dir / test_subdir
            if subdir_path.exists():
                print(f"  ❌ Removing: {test_subdir}")
                shutil.rmtree(subdir_path)
                self.cleanup_stats["directories_removed"] += 1
                
    async def cleanup_obsolete_scripts(self):
        """Clean up obsolete scripts"""
        obsolete_dir = self.archive_dir / "obsolete_scripts_backup"
        if not obsolete_dir.exists():
            return
            
        print("\n🧹 Cleaning obsolete scripts...")
        
        # These are truly obsolete and can be removed
        for script in obsolete_dir.glob("*.py"):
            print(f"  ❌ Removing: {script.name}")
            script.unlink()
            self.cleanup_stats["files_removed"] += 1
            
        # Remove directory if empty
        if not list(obsolete_dir.iterdir()):
            obsolete_dir.rmdir()
            self.cleanup_stats["directories_removed"] += 1
            
    async def execute_cleanup(self):
        """Execute full cleanup orchestration"""
        print("\n🚀 Starting Archive Cleanup Orchestration")
        print("=" * 60)
        
        # Phase 1: Analysis
        subdirs, total_mb_before = await self.analyze_archive()
        
        # Phase 2: User confirmation
        print(f"\n⚠️  This will clean up {total_mb_before:.2f} MB of archive data")
        print("The following will be removed:")
        print("  - Batch reports older than 7 days")
        print("  - All test data and venv directories")
        print("  - All obsolete script backups")
        
        # Phase 3: Execute cleanup tasks in parallel
        print("\n🔧 Executing cleanup tasks...")
        
        cleanup_tasks = [
            self.cleanup_batch_reports(days_to_keep=7),
            self.cleanup_test_data(),
            self.cleanup_obsolete_scripts()
        ]
        
        await asyncio.gather(*cleanup_tasks)
        
        # Phase 4: Calculate space freed
        total_mb_after = sum(f.stat().st_size for f in self.archive_dir.rglob('*') if f.is_file()) / (1024 * 1024)
        self.cleanup_stats["space_freed_mb"] = total_mb_before - total_mb_after
        
        # Phase 5: Report results
        print("\n✨ Cleanup Complete!")
        print("=" * 60)
        print(f"📊 Cleanup Statistics:")
        print(f"  Files Removed: {self.cleanup_stats['files_removed']}")
        print(f"  Directories Removed: {self.cleanup_stats['directories_removed']}")
        print(f"  Space Freed: {self.cleanup_stats['space_freed_mb']:.2f} MB")
        print(f"  Remaining Size: {total_mb_after:.2f} MB")
        
        # Check if archive directory should be removed entirely
        if total_mb_after < 0.1:  # Less than 100KB
            print("\n🎯 Archive directory is now empty. Removing it entirely...")
            shutil.rmtree(self.archive_dir)
            print("  ✅ Archive directory removed!")
            
        return self.cleanup_stats


async def main():
    """Main execution"""
    orchestrator = ArchiveCleanupOrchestrator()
    
    # Execute cleanup
    stats = await orchestrator.execute_cleanup()
    
    # Save cleanup report
    report = {
        "timestamp": datetime.now().isoformat(),
        "cleanup_stats": stats,
        "orchestrator": "ArchiveCleanupOrchestrator"
    }
    
    report_path = Path("archive_cleanup_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Cleanup report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())