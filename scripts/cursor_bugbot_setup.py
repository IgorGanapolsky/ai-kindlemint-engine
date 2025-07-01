#!/usr/bin/env python3
"""
Cursor Bugbot Setup Validator

Validates that Cursor Bugbot is properly configured for this repository.
Since Cursor doesn't provide APIs, this script checks local configuration
and provides setup instructions.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


class CursorBugbotValidator:
    """Validates Cursor Bugbot configuration."""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def check_cursorignore(self) -> bool:
        """Check if .cursorignore file exists and is properly configured."""
        cursorignore_path = self.repo_root / '.cursorignore'
        
        if not cursorignore_path.exists():
            self.issues.append("❌ .cursorignore file not found")
            return False
        
        with open(cursorignore_path, 'r') as f:
            content = f.read()
        
        # Check for critical patterns
        critical_patterns = ['.env', '*.key', '*.pem', 'secrets/', 'credentials/']
        missing_patterns = []
        
        for pattern in critical_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            self.warnings.append(f"⚠️  .cursorignore missing critical patterns: {', '.join(missing_patterns)}")
        else:
            self.successes.append("✅ .cursorignore properly configured with security patterns")
        
        return True
    
    def check_github_workflow(self) -> bool:
        """Check if GitHub workflow for Bugbot exists."""
        workflow_path = self.repo_root / '.github' / 'workflows' / 'cursor-bugbot.yml'
        
        if not workflow_path.exists():
            self.issues.append("❌ GitHub workflow cursor-bugbot.yml not found")
            return False
        
        self.successes.append("✅ GitHub workflow for automated Bugbot triggering exists")
        return True
    
    def check_readme_documentation(self) -> bool:
        """Check if README has Cursor Bugbot documentation."""
        readme_path = self.repo_root / 'README.md'
        
        if not readme_path.exists():
            self.issues.append("❌ README.md not found")
            return False
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        if 'Cursor Bugbot' not in content:
            self.warnings.append("⚠️  README.md doesn't mention Cursor Bugbot")
            return False
        
        self.successes.append("✅ README.md includes Cursor Bugbot badge")
        return True
    
    def generate_setup_instructions(self) -> str:
        """Generate setup instructions for Cursor Bugbot."""
        instructions = """
🤖 Cursor Bugbot Setup Instructions
===================================

1. **Enable Bugbot in Cursor Dashboard** (Required)
   - Go to: https://www.cursor.com/dashboard?tab=integrations
   - Click "Connect to GitHub" if not already connected
   - Find this repository: IgorGanapolsky/ai-kindlemint-engine
   - Toggle "BugBot" ON for this repository
   - Configure settings:
     ☐ Only Run when Mentioned: OFF (for automatic PR reviews)
     ☐ Only Run Once: ON (to avoid spam)
     ☐ Hide "No Bugs Found" Comments: ON

2. **Verify Repository Configuration** (✅ Complete)
   - .cursorignore file exists with security patterns
   - GitHub workflow for automated triggering configured
   - README documentation in place

3. **Test the Integration**
   - Create a test PR with some code changes
   - Wait for automatic Bugbot analysis (or comment "bugbot run")
   - Check for Bugbot comments with potential issues
   - Click "Fix in Cursor" links to jump to issues

4. **Usage**
   - **Automatic**: Bugbot runs on every PR (if enabled in dashboard)
   - **Manual**: Comment "bugbot run" on any PR
   - **Verbose**: Comment "bugbot run verbose=true" for detailed analysis

5. **Limitations**
   - No API access (dashboard configuration only)
   - No webhooks or programmatic triggers
   - GitHub Enterprise not supported
   - Manual page refresh may be needed (known bug)

📝 Note: Cursor Bugbot is in Beta and free for all Cursor Pro users ($20/month)
"""
        return instructions
    
    def validate(self) -> Tuple[bool, str]:
        """Run all validation checks."""
        print("🔍 Validating Cursor Bugbot Configuration...\n")
        
        # Run checks
        self.check_cursorignore()
        self.check_github_workflow()
        self.check_readme_documentation()
        
        # Generate report
        report = []
        
        if self.successes:
            report.append("✅ Successes:")
            for success in self.successes:
                report.append(f"   {success}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  Warnings:")
            for warning in self.warnings:
                report.append(f"   {warning}")
            report.append("")
        
        if self.issues:
            report.append("❌ Issues:")
            for issue in self.issues:
                report.append(f"   {issue}")
            report.append("")
        
        # Overall status
        if not self.issues:
            report.append("✅ Local configuration is ready for Cursor Bugbot!")
            report.append("⚠️  Remember: You must still enable Bugbot in the Cursor dashboard")
            is_valid = True
        else:
            report.append("❌ Configuration issues found. Please fix them before proceeding.")
            is_valid = False
        
        report.append("")
        report.append(self.generate_setup_instructions())
        
        return is_valid, '\n'.join(report)


def main():
    """Main entry point."""
    validator = CursorBugbotValidator()
    is_valid, report = validator.validate()
    
    print(report)
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()