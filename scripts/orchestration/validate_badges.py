#!/usr/bin/env python3
"""
Badge validation script to ensure critical project badges are present in README.md
"""

import re
import sys
from pathlib import Path

REQUIRED_BADGES = [
    'Tests',
    'codecov', 
    'Quality Gate Status',
    'Maintainability Rating',
    'Hygiene Score',
    'MTD Cost',
    'Orchestration Savings',
    'Cursor Bugbot',
    'GitHub Issues',
    'GitHub Pull Requests',
    'Last Commit',
    'Contributors',
    'Code Size'
]

def validate_badges():
    """Validate that all required badges are present in README.md"""
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    
    if not readme_path.exists():
        print("❌ README.md not found!")
        return False
    
    content = readme_path.read_text()
    
    missing_badges = []
    for badge in REQUIRED_BADGES:
        # Check for badge in various formats
        patterns = [
            rf'\[{re.escape(badge)}\]',
            rf'badge/{re.escape(badge.replace(" ", "_"))}-',
            rf'badge/{re.escape(badge.replace(" ", "%20"))}-',
            rf'{re.escape(badge.lower())}'
        ]
        
        found = any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
        if not found:
            missing_badges.append(badge)
    
    if missing_badges:
        print(f"❌ Missing required badges: {', '.join(missing_badges)}")
        return False
    
    print("✅ All required badges are present!")
    return True

if __name__ == "__main__":
    success = validate_badges()
    sys.exit(0 if success else 1)
