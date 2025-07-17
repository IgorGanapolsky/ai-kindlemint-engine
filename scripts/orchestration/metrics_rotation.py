#!/usr/bin/env python3
"""
Metrics Rotation System for Worktree Orchestration
Automatically rotates commit metrics files monthly
"""
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class MetricsRotation:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.metrics_dir = self.repo_root / "reports" / "orchestration"
        self.archive_dir = self.metrics_dir / "archive"
        
    def should_rotate(self) -> bool:
        """Check if we need to rotate (it's the 1st of the month)"""
        return datetime.now().day == 1
    
    def get_previous_month(self) -> str:
        """Get previous month in YYYY-MM format"""
        today = datetime.now()
        first_day = today.replace(day=1)
        last_month = first_day - timedelta(days=1)
        return last_month.strftime("%Y-%m")
    
    def archive_commit_metrics(self):
        """Archive previous month's commit metrics"""
        previous_month = self.get_previous_month()
        archive_month_dir = self.archive_dir / previous_month
        archive_month_dir.mkdir(parents=True, exist_ok=True)
        
        # Move all commit_metrics files from previous month
        moved_count = 0
        for file in self.metrics_dir.glob("commit_metrics_*.json"):
            # Extract date from filename
            try:
                date_str = file.stem.split("_")[2]  # e.g., "20250703"
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                # If file is from previous month or older, archive it
                if file_date.strftime("%Y-%m") <= previous_month:
                    dest = archive_month_dir / file.name
                    shutil.move(str(file), str(dest))
                    moved_count += 1
            except Exception:
                # Skip files that don't match expected format
                continue
        
        return moved_count
    
    def clean_old_archives(self, months_to_keep: int = 3):
        """Remove archives older than specified months"""
        if not self.archive_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=months_to_keep * 30)
        removed_count = 0
        
        for month_dir in self.archive_dir.iterdir():
            if month_dir.is_dir():
                try:
                    dir_date = datetime.strptime(month_dir.name, "%Y-%m")
                    if dir_date < cutoff_date:
                        shutil.rmtree(month_dir)
                        removed_count += 1
                except Exception:
                    continue
        
        return removed_count
    
    def update_gitignore(self):
        """Ensure archive directory is in .gitignore"""
        gitignore_path = self.repo_root / ".gitignore"
        archive_pattern = "reports/orchestration/archive/"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if archive_pattern not in content:
                with open(gitignore_path, "a") as f:
                    f.write(f"\n# Orchestration metrics archives\n{archive_pattern}\n")
    
    def create_rotation_summary(self, archived: int, cleaned: int):
        """Create a summary of the rotation"""
        summary = {
            "rotation_date": datetime.now().isoformat(),
            "previous_month": self.get_previous_month(),
            "files_archived": archived,
            "old_archives_removed": cleaned,
            "archive_location": str(self.archive_dir)
        }
        
        summary_path = self.metrics_dir / "last_rotation.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def rotate(self, force: bool = False):
        """Perform monthly rotation"""
        if not force and not self.should_rotate():
            print("📅 Not the 1st of the month - skipping rotation")
            print("   Use --force to rotate anyway")
            return
        
        print("🔄 Starting monthly metrics rotation...")
        
        # Archive previous month's files
        archived = self.archive_commit_metrics()
        print(f"📦 Archived {archived} commit metrics files")
        
        # Clean old archives (keep 3 months)
        cleaned = self.clean_old_archives(months_to_keep=3)
        if cleaned > 0:
            print(f"🧹 Removed {cleaned} old archive directories")
        
        # Update .gitignore
        self.update_gitignore()
        
        # Create summary
        summary = self.create_rotation_summary(archived, cleaned)
        print("\n✅ Rotation complete!")
        print(f"   Previous month's files: {self.archive_dir / self.get_previous_month()}")
        print("   Archives are kept for 3 months")
        
        return summary


def main():
    """Main function for CLI usage"""
    import sys
    
    rotator = MetricsRotation()
    force = "--force" in sys.argv
    
    if "--check" in sys.argv:
        # Just check if rotation is needed
        if rotator.should_rotate():
            print("📅 It's the 1st - rotation needed!")
        else:
            print("📅 Not the 1st - no rotation needed")
            current_files = len(list(rotator.metrics_dir.glob("commit_metrics_*.json")))
            print(f"   Current commit metrics files: {current_files}")
    else:
        # Perform rotation
        rotator.rotate(force=force)


if __name__ == "__main__":
    main()