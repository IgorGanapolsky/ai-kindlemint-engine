#!/usr/bin/env python3
"""
Enforce 8.5x11 standard for all paperback puzzle books
Reject any attempts to create 6x9 or other sizes
"""

import json
import sys
from pathlib import Path

def check_all_paperback_dimensions():
    """Find and validate all paperback configurations"""
    
    print("🔍 Enforcing 8.5x11 Standard for Paperbacks")
    print("=" * 70)
    
    violations = []
    fixed = []
    
    # Find all KDP metadata files
    for metadata_file in Path('.').glob('**/paperback/**/kdp_metadata*.json'):
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            
            # Check dimensions
            dimensions = data.get('dimensions', '')
            if '6 x 9' in dimensions or '6x9' in dimensions:
                violations.append(str(metadata_file))
                print(f"❌ VIOLATION: {metadata_file}")
                print(f"   Found: {dimensions}")
                print(f"   Required: 8.5 x 11 inches")
                
                # Auto-fix
                data['dimensions'] = '8.5 x 11 inches'
                if 'print_options' in data:
                    data['print_options']['trim_size'] = '8.5 x 11 inches'
                
                with open(metadata_file, 'w') as f:
                    json.dump(data, f, indent=2)
                fixed.append(str(metadata_file))
                
            elif '8.5 x 11' in dimensions or '8.5x11' in dimensions:
                print(f"✅ COMPLIANT: {metadata_file}")
            else:
                print(f"⚠️  UNKNOWN: {metadata_file} - dimensions: {dimensions}")
                
        except Exception as e:
            print(f"⚠️  ERROR reading {metadata_file}: {e}")
    
    # Check Python scripts
    for py_file in Path('scripts').glob('**/*pdf*.py'):
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            if 'PAGE_WIDTH = 6 * inch' in content:
                violations.append(str(py_file))
                print(f"\n❌ SCRIPT VIOLATION: {py_file}")
                print("   Contains 6x9 page setup - needs update to 8.5x11")
                
        except Exception as e:
            pass
    
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print(f"  - Found {len(violations)} violations")
    print(f"  - Fixed {len(fixed)} files")
    
    if violations:
        print("\n⚠️  Scripts that need manual updates:")
        for v in violations:
            if v.endswith('.py'):
                print(f"  - {v}")
    
    return len(violations) == 0


if __name__ == "__main__":
    success = check_all_paperback_dimensions()
    
    if not success:
        print("\n🚨 ACTION REQUIRED:")
        print("All paperback puzzle books MUST use 8.5x11 format")
        print("This is non-negotiable for Large Print accessibility")
        sys.exit(1)
    else:
        print("\n✅ All paperbacks comply with 8.5x11 standard!")
        sys.exit(0)