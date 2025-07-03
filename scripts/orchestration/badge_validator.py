#!/usr/bin/env python3
"""
Badge Validator for Worktree Orchestration
Ensures critical badges are never removed from README.md
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

REQUIRED_BADGES = {
    'Tests': r'\[!\[Tests\].*?\]',
    'codecov': r'\[!\[codecov\].*?\]',
    'Quality Gate Status': r'\[!\[Quality Gate Status\].*?\]',
    'Maintainability Rating': r'\[!\[Maintainability Rating\].*?\]',
    'Hygiene Score': r'\[!\[Hygiene Score\].*?\]',
    'MTD Cost': r'\[!\[MTD Cost\].*?\]',
    'Orchestration Savings': r'\[!\[Orchestration Savings\].*?\]',
    'Cursor Bugbot': r'\[!\[Cursor Bugbot\].*?\]',
    'GitHub Issues': r'\[!\[GitHub Issues\].*?\]',
    'GitHub Pull Requests': r'\[!\[GitHub Pull Requests\].*?\]',
    'Last Commit': r'\[!\[Last Commit\].*?\]',
    'Contributors': r'\[!\[Contributors\].*?\]',
    'Code Size': r'\[!\[Code Size\].*?\]'
}

def validate_badges(readme_path: Path) -> Tuple[bool, List[str]]:
    """Validate that all required badges are present in README.md"""
    if not readme_path.exists():
        return False, ["README.md not found"]
    
    content = readme_path.read_text()
    missing_badges = []
    
    for badge_name, pattern in REQUIRED_BADGES.items():
        if not re.search(pattern, content, re.DOTALL):
            missing_badges.append(badge_name)
    
    return len(missing_badges) == 0, missing_badges

def get_badge_health_report(readme_path: Path) -> Dict[str, bool]:
    """Get health status of all badges"""
    content = readme_path.read_text() if readme_path.exists() else ""
    health_report = {}
    
    for badge_name, pattern in REQUIRED_BADGES.items():
        health_report[badge_name] = bool(re.search(pattern, content, re.DOTALL))
    
    return health_report

def main():
    """Main validation function"""
    repo_root = Path(__file__).parent.parent.parent
    readme_path = repo_root / "README.md"
    
    is_valid, missing = validate_badges(readme_path)
    
    if not is_valid:
        print("❌ BADGE VALIDATION FAILED!")
        print(f"\nMissing {len(missing)} required badges:")
        for badge in missing:
            print(f"  - {badge}")
        
        print("\n⚠️  As CTO, you must ensure all project visibility metrics are maintained!")
        print("📊 These badges provide critical insights for stakeholders.")
        sys.exit(1)
    else:
        health_report = get_badge_health_report(readme_path)
        print("✅ All required badges are present!")
        print("\n📊 Badge Health Report:")
        for badge, status in health_report.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {badge}")
        
        print("\n💡 Badge validation passed. Project visibility maintained.")

if __name__ == "__main__":
    main()