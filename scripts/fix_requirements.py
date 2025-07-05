#!/usr/bin/env python3
"""
Permanent fix for requirements files to prevent circular dependencies
"""

import os
import re
import subprocess

def fix_requirements_files():
    """Remove circular references and clean up requirements files"""
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False

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
        if line.strip() == '-r requirements-locked.txt' and os.path.exists('requirements-locked.txt') and any('-r requirements-locked.txt' in l for l in cleaned_lines):
            cleaned_lines.append('# Removed duplicate reference')
            continue
            
        cleaned_lines.append(line)

    # Write cleaned file
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(cleaned_lines))

    print("✅ Fixed requirements.txt circular references")

    # Re-read the cleaned file for validation
    with open('requirements.txt', 'r') as f:
        cleaned_content = f.read()

    # Validate no circular references exist
    if '-r requirements.txt' in cleaned_content:
        print("❌ WARNING: Self-reference still exists!")
        return False

    print("✅ Requirements files validated - no circular references")

    # Validate the fixed file can be installed
    try:
        result = subprocess.run(['pip', 'install', '--dry-run', '-r', 'requirements.txt'], 
                              capture_output=True, text=True, check=True)
        print("✅ Fixed requirements.txt can be installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Fixed requirements.txt cannot be installed: {e.stderr}")
        return False
    except Exception as e:
        print(f"⚠️  Could not validate fixed requirements: {e}")
        return False

if __name__ == "__main__":
    fix_requirements_files()
