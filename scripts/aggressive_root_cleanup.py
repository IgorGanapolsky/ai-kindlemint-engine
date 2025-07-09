#!/usr/bin/env python3
"""
Aggressive Root Directory Cleanup
---------------------------------
This script specifically targets root directory clutter and moves files to appropriate directories.
"""

import os
import shutil
from pathlib import Path
import sys

def clean_root_directory():
    """Aggressively clean the root directory"""
    project_root = Path.cwd()
    
    print("🧹 AGGRESSIVE Root Directory Cleanup")
    print("=" * 50)
    
    # Create necessary directories
    dirs_to_create = [
        "scripts/utilities",
        "docs/checklists",
        "docs/templates",
        "config/keys",
        "infrastructure/setup",
        "tools/setup"
    ]
    
    for dir_path in dirs_to_create:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Files that should stay in root
    essential_files = {
        'README.md', 'LICENSE', 'requirements.txt', 'setup.py', 
        '.gitignore', '.gitattributes', '.deepsource.toml', '.env.example',
        'sonar-project.properties', 'claude-code', 'claude-flow', 
        'claude-flow-costs', 'claude-flow-costs-notify', '.ccfignore',
        'Dockerfile', 'docker-compose.yml', 'pyproject.toml'
    }
    
    # Mapping of file patterns to target directories
    file_mappings = {
        # Python scripts
        "*.py": "scripts/utilities",
        # Shell scripts
        "*.sh": "scripts/utilities",
        # HTML files
        "*.html": "docs/templates",
        # Markdown files (except README)
        "*.md": "docs/checklists",
        # Config files
        "*.yml": "config",
        "*.yaml": "config",
        "*.toml": "config",
        "*.json": "config",
        # Key files
        "*.pem": "config/keys",
        # Text files
        "*.txt": "docs",
        "*.tsx": "src/components",
        # Setup files
        "*setup*.py": "tools/setup",
        "*setup*.sh": "tools/setup",
        # Orchestration files
        "*orchestration*.sh": "scripts/orchestration",
        "*orchestration*.py": "scripts/orchestration",
    }
    
    # Specific file mappings
    specific_mappings = {
        "AWS_MIGRATION_CHECKLIST.md": "docs/checklists/AWS_MIGRATION_CHECKLIST.md",
        "EMAIL_TEMPLATES.md": "docs/templates/EMAIL_TEMPLATES.md",
        "GUMROAD_SETUP_NOW.md": "docs/setup/GUMROAD_SETUP_NOW.md",
        "IMMEDIATE_FIXES.md": "docs/tasks/IMMEDIATE_FIXES.md",
        "LAUNCH_CHECKLIST.md": "docs/checklists/LAUNCH_CHECKLIST.md",
        "mcp-server-key.pem": "config/keys/mcp-server-key.pem",
        "index.tsx": "src/index.tsx",
        "Dockerfile.trends": "infrastructure/docker/Dockerfile.trends",
    }
    
    # Process files
    moved_files = []
    root_files = [f for f in project_root.iterdir() if f.is_file()]
    
    for file in root_files:
        # Skip essential files
        if file.name in essential_files:
            continue
        
        # Check specific mappings first
        if file.name in specific_mappings:
            target_path = project_root / specific_mappings[file.name]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(file), str(target_path))
                moved_files.append((file.name, target_path))
                continue
            except Exception as e:
                print(f"Error moving {file.name}: {e}")
        
        # Check pattern mappings
        moved = False
        for pattern, target_dir in file_mappings.items():
            if file.match(pattern):
                target_path = project_root / target_dir / file.name
                target_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(file), str(target_path))
                    moved_files.append((file.name, target_path))
                    moved = True
                    break
                except Exception as e:
                    print(f"Error moving {file.name}: {e}")
        
        if not moved:
            print(f"⚠️ Didn't move {file.name} - no matching rule")
    
    # Print results
    print(f"\n📊 Moved {len(moved_files)} files from root directory")
    
    # Check final root file count
    root_files = [f for f in project_root.iterdir() if f.is_file()]
    print(f"📁 Final root file count: {len(root_files)}")
    
    # List remaining root files
    print("\n📂 Remaining root files:")
    for file in sorted(root_files):
        print(f"   {file.name}")

if __name__ == "__main__":
    clean_root_directory()