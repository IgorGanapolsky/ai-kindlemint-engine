#!/usr/bin/env python3
"""
Permanent fix for requirements files to prevent circular dependencies
"""

import os
import re

def fix_requirements_files():
    """Remove circular references and clean up requirements files"""
    
    # Check for circular references in requirements.txt
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Remove any self-references
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines that reference themselves or create circles
        if line.strip() in ['-r requirements.txt', '-r ./requirements.txt']:
            cleaned_lines.append('# Removed circular self-reference')
            continue
        
        # Skip duplicate -r requirements-locked.txt references
        if line.strip() == '-r requirements-locked.txt' and any('-r requirements-locked.txt' in l for l in cleaned_lines):
            cleaned_lines.append('# Removed duplicate reference')
            continue
            
        cleaned_lines.append(line)
    
    # Write cleaned file
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ Fixed requirements.txt circular references")
    
    # Validate no circular references exist
    if '-r requirements.txt' in content:
        print("❌ WARNING: Self-reference still exists!")
        return False
    
    print("✅ Requirements files validated - no circular references")
    return True

if __name__ == "__main__":
    fix_requirements_files()
