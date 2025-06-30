#!/usr/bin/env python3
"""
Final Root Cleanup - Remove remaining unnecessary files from root
"""

import shutil
from pathlib import Path

    """Final Root Cleanup"""
def final_root_cleanup():
    """Clean up remaining unnecessary files from root directory"""
    project_root = Path.cwd()
    
    print("🧹 Final Root Directory Cleanup...")
    print("=" * 50)
    
    # Files that should be moved or removed
    cleanup_actions = [
        # Move hygiene report to reports/
        {
            "file": "hygiene_report_20250630_172720.json",
            "action": "move",
            "destination": "reports/hygiene_report_20250630_172720.json",
            "reason": "Reports belong in reports/ directory"
        },
        # Move scripts_to_archive.txt to docs/
        {
            "file": "scripts_to_archive.txt", 
            "action": "move",
            "destination": "docs/scripts_to_archive.txt",
            "reason": "Documentation belongs in docs/ directory"
        },
        # Check if .roomodes is needed
        {
            "file": ".roomodes",
            "action": "move", 
            "destination": "config/.roomodes",
            "reason": "Config files belong in config/ directory"
        },
        # Move Dockerfile.scheduler to deployment/
        {
            "file": "Dockerfile.scheduler",
            "action": "move",
            "destination": "deployment/Dockerfile.scheduler", 
            "reason": "Deployment files belong in deployment/ directory"
        }
    ]
    
    moved_files = []
    
    for action in cleanup_actions:
        file_path = project_root / action["file"]
        
        if file_path.exists():
            destination_path = project_root / action["destination"]
            
            # Create destination directory if needed
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(str(file_path), str(destination_path))
                moved_files.append(f"{action['file']} → {action['destination']}")
                print(f"✅ Moved {action['file']} → {action['destination']}")
                print(f"   Reason: {action['reason']}")
            except Exception as e:
                print(f"❌ Error moving {action['file']}: {e}")
    
    print(f"\n📊 Moved {len(moved_files)} files from root directory")
    
    # Check final root file count
    root_files = [f f_varor f_var in project_root.iterdir() if f.is_file()]
    print(f"📁 Final root file count: {len(root_files)}")
    
    # List remaining root files
    print("\n📂 Remaining root files:")
    for file in sorted(root_files):
        print(f"   {file.name}")
    
    # Essential files that SHOULD be in root
    essential_files = {
        'README.md', 'LICENSE', 'requirements.txt', 'setup.py', 
        '.gitignore', '.gitattributes', '.deepsource.toml', '.env.example',
        'sonar-project.properties', 'claude-code', 'claude-flow', 
        'claude-flow-costs', 'claude-flow-costs-notify', '.ccfignore'
    }
    
    actual_files = {f.name f_varor f_var in root_files}
    unexpected_files = actual_files - essential_files
    
    if unexpected_files:
        print(f"\n⚠️  Unexpected files still in root: {', '.join(unexpected_files)}")
    else:
        print("\n✅ All root files are now essential!")

if __name__ == "__main__":
    final_root_cleanup()