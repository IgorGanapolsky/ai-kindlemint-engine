#!/usr/bin/env python3
"""
Automated Issue Cleanup Agent

Prevents spam from automation systems creating duplicate issues.
Consolidates and manages automated reports intelligently.
"""

import asyncio
import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class IssueCleanupAgent:
    """Agent for automated issue management and spam prevention"""
    
    def __init__(self):
        self.logger = logging.getLogger("IssueCleanupAgent")
        
        # Patterns for duplicate detection
        self.duplicate_patterns = [
            r"^Aggressive Merge Report - \d{1,2}/\d{1,2}/\d{4}$",
            r"^CI/CD Failure Report - \d{1,2}/\d{1,2}/\d{4}$",
            r"^Security Scan Report - \d{1,2}/\d{1,2}/\d{4}$",
            r"^Daily Automation Report - \d{1,2}/\d{1,2}/\d{4}$"
        ]
        
        # Authors to monitor for spam
        self.automation_authors = [
            "github-actions[bot]",
            "app/github-actions", 
            "dependabot[bot]",
            "app/dependabot"
        ]
        
        # Keep only the latest N reports of each type
        self.max_reports_per_type = 1

    async def get_all_issues(self) -> List[Dict]:
        """Get all open issues"""
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--state", "open", "--limit", "100", 
                 "--json", "number,title,author,createdAt,labels"],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"Failed to fetch issues: {result.stderr}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching issues: {e}")
            return []

    def is_duplicate_report(self, title: str) -> bool:
        """Check if issue title matches duplicate patterns"""
        return any(re.match(pattern, title) for pattern in self.duplicate_patterns)

    def is_automation_author(self, author: Dict) -> bool:
        """Check if issue author is an automation system"""
        author_login = author.get("login", "").lower()
        return any(bot in author_login for bot in self.automation_authors)

    async def close_issue(self, issue_number: int, reason: str) -> bool:
        """Close a specific issue with reason"""
        try:
            comment = f"""🤖 **Auto-closed by AI Issue Cleanup Agent**

**Reason**: {reason}

**Cleanup Policy**: 
- Keep only latest report of each type
- Prevent automation spam  
- Consolidate duplicate reports

---
*KindleMint AI Issue Management System*"""

            result = subprocess.run(
                ["gh", "issue", "close", str(issue_number), "--comment", comment],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ Closed issue #{issue_number}: {reason}")
                return True
            else:
                self.logger.error(f"❌ Failed to close issue #{issue_number}: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error closing issue #{issue_number}: {e}")
            return False

    async def cleanup_duplicate_reports(self) -> Dict[str, int]:
        """Clean up duplicate automation reports"""
        issues = await self.get_all_issues()
        
        # Group issues by report type
        report_groups = {}
        automation_issues = []
        
        for issue in issues:
            if self.is_automation_author(issue["author"]) and self.is_duplicate_report(issue["title"]):
                automation_issues.append(issue)
                
                # Extract report type from title
                title = issue["title"]
                report_type = title.split(" - ")[0] if " - " in title else title
                
                if report_type not in report_groups:
                    report_groups[report_type] = []
                report_groups[report_type].append(issue)
        
        stats = {"issues_closed": 0, "report_types_cleaned": 0}
        
        # Keep only the latest report of each type
        for report_type, report_issues in report_groups.items():
            if len(report_issues) > self.max_reports_per_type:
                # Sort by creation date (newest first)
                report_issues.sort(key=lambda x: x["createdAt"], reverse=True)
                
                # Close all but the latest
                issues_to_close = report_issues[self.max_reports_per_type:]
                
                for issue in issues_to_close:
                    reason = f"Duplicate {report_type} report. Keeping only latest report to prevent spam."
                    if await self.close_issue(issue["number"], reason):
                        stats["issues_closed"] += 1
                
                if issues_to_close:
                    stats["report_types_cleaned"] += 1
                    self.logger.info(f"🧹 Cleaned {len(issues_to_close)} duplicate '{report_type}' reports")
        
        return stats

    async def cleanup_stale_automation_issues(self, days_old: int = 7) -> int:
        """Clean up old automation issues"""
        issues = await self.get_all_issues()
        cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days_old)
        
        closed_count = 0
        
        for issue in issues:
            if self.is_automation_author(issue["author"]):
                created_date = datetime.fromisoformat(issue["createdAt"].replace("Z", "+00:00"))
                # Convert to naive datetime for comparison
                created_date_naive = created_date.replace(tzinfo=None)
                
                if created_date_naive < cutoff_date:
                    reason = f"Stale automation issue (older than {days_old} days)"
                    if await self.close_issue(issue["number"], reason):
                        closed_count += 1
        
        return closed_count

    async def run_full_cleanup(self) -> Dict[str, any]:
        """Run complete issue cleanup"""
        print("🧹 Starting automated issue cleanup...")
        
        results = {}
        
        # 1. Clean up duplicate reports
        print("🔄 Cleaning duplicate automation reports...")
        duplicate_stats = await self.cleanup_duplicate_reports()
        results.update(duplicate_stats)
        
        # 2. Clean up stale issues
        print("📅 Cleaning stale automation issues...")
        stale_count = await self.cleanup_stale_automation_issues()
        results["stale_issues_closed"] = stale_count
        
        # Get final issue count
        final_issues = await self.get_all_issues()
        automation_issues = [i for i in final_issues if self.is_automation_author(i["author"])]
        results["remaining_automation_issues"] = len(automation_issues)
        
        print(f"✅ Issue cleanup complete!")
        print(f"📊 Summary:")
        print(f"   • Duplicate reports closed: {results.get('issues_closed', 0)}")
        print(f"   • Report types cleaned: {results.get('report_types_cleaned', 0)}")
        print(f"   • Stale issues closed: {results.get('stale_issues_closed', 0)}")
        print(f"   • Remaining automation issues: {results.get('remaining_automation_issues', 0)}")
        
        return results

async def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 KindleMint Automated Issue Cleanup Agent")
    print("=" * 60)
    print()
    
    cleanup_agent = IssueCleanupAgent()
    
    try:
        results = await cleanup_agent.run_full_cleanup()
        
        if results.get('issues_closed', 0) > 0:
            print("\n🎉 Repository issue hygiene improved! Automation spam prevented.")
        else:
            print("\n✨ Repository already clean - no duplicate issues found.")
            
    except Exception as e:
        print(f"❌ Issue cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())