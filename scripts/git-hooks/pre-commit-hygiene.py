#!/usr/bin/env python3
"""
Pre-commit hygiene check for duplicate scripts
"""

import sys
from collections import defaultdict
from pathlib import Path


def check_duplicate_scripts():
    """Check for duplicate script functionality"""
    script_categories = defaultdict(list)
    
    # Common patterns that indicate similar functionality
    patterns = {
        'cleanup': ['clean', 'cleanup', 'hygiene', 'remove', 'delete', 'purge'],
        'fix': ['fix_', 'repair_', 'patch_', 'hotfix_'],
        'generate': ['generate_', 'create_', 'build_'],
        'validate': ['validate_', 'check_', 'verify_', 'qa_'],
        'emergency': ['emergency_', 'urgent_', 'critical_'],
    }
    
    scripts_dir = Path('scripts')
    if not scripts_dir.exists():
        return True
    
    # Categorize scripts
    for script in scripts_dir.rglob('*.py'):
        if '__pycache__' in str(script):
            continue
            
        script_name = script.stem.lower()
        
        for category, keywords in patterns.items():
            if any(keyword in script_name for keyword in keywords):
                script_categories[category].append(script)
                break
    
    # Check for potential duplicates
    issues = []
    for category, scripts in script_categories.items():
        if len(scripts) > 5:  # Threshold for too many similar scripts
            issues.append(
                f"Warning: {len(scripts)} '{category}' scripts found - consider consolidation:"
            )
            for script in scripts[:5]:
                issues.append(f"  - {script}")
            if len(scripts) > 5:
                issues.append(f"  ... and {len(scripts) - 5} more")
    
    if issues:
        print("\n🚨 Code Hygiene Warning: Potential duplicate scripts detected\n")
        for issue in issues:
            print(issue)
        print("\nConsider consolidating similar scripts to reduce duplication.")
        print("Run 'python agents/code_hygiene_orchestrator.py analyze' for full analysis.")
        return False
    
    return True


if __name__ == "__main__":
    if not check_duplicate_scripts():
        sys.exit(1)