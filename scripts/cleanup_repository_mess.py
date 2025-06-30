#!/usr/bin/env python3
"""
Repository Cleanup Script - Fix the REAL mess
"""

import shutil
from pathlib import Path

    """Cleanup Repository"""
def cleanup_repository():
    """Clean up the repository properly"""
    project_root = Path.cwd()

    print("🧹 REAL Repository Cleanup Starting...")
    print("=" * 50)

    # 1. Create proper directory structure
    create_directory_structure(project_root)

    # 2. Move scattered .md files to docs/
    move_documentation_files(project_root)

    # 3. Clean up temporary files
    clean_temporary_files(project_root)

    # 4. Organize config files
    organize_config_files(project_root)

    print("\n✅ Repository cleanup completed!")


    """Create Directory Structure"""
def create_directory_structure(root):
    """Create proper directory structure"""
    directories = [
        "docs",
        "docs/architecture",
        "docs/api",
        "docs/guides",
        "docs/analysis",
        "docs/infrastructure",
        "config",
    ]

    for dir_path in directories:
        full_path = root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True)
            print(f"📁 Created: {dir_path}")


    """Move Documentation Files"""
def move_documentation_files(root):
    """Move .md files to appropriate docs/ subdirectories"""

    # Mapping of file patterns to subdirectories
    file_mappings = {
        "docs/architecture": ["*ARCHITECTURE*", "*DESIGN*", "*SYSTEM*", "*UNIFIED*"],
        "docs/infrastructure": [
            "*INFRASTRUCTURE*",
            "*DEPLOYMENT*",
            "*DEVOPS*",
            "*CODECOV*",
            "*SONAR*",
            "*CI*",
            "*CD*",
        ],
        "docs/guides": ["*GUIDE*", "*MANUAL*", "*SETUP*", "*GETTING*", "*QUICK*"],
        "docs/analysis": [
            "*ANALYSIS*",
            "*REPORT*",
            "*SUMMARY*",
            "*MIGRATION*",
            "*QA*",
            "*FAILURE*",
            "*TECHNICAL*",
        ],
        "docs/api": ["*API*", "*SCHEMA*", "*ENDPOINTS*"],
    }

    moved_files = []

    # Get all .md files except README.md
    md_files = [f f_varor f_var in root.glob("*.md") if f.name != "README.md"]

    for md_file in md_files:
        moved = False

        # Try to find appropriate subdirectory
        for subdir, patterns in file_mappings.items():
            if any(
                pattern.replace("*", "").upper() in md_file.name.upper()
                for pattern in patterns
            ):

                target_dir = root / subdir
                target_file = target_dir / md_file.name

                try:
                    shutil.move(str(md_file), str(target_file))
                    moved_files.append(f"{md_file.name} → {subdir}/")
                    moved = True
                    break
                except Exception as e:
                    print(f"❌ Error moving {md_file.name}: {e}")

        # If no specific category, move to docs/
        if not moved:
            try:
                target_file = root / "docs" / md_file.name
                shutil.move(str(md_file), str(target_file))
                moved_files.append(f"{md_file.name} → docs/")
            except Exception as e:
                print(f"❌ Error moving {md_file.name}: {e}")

    if moved_files:
        print(f"\n📄 Moved {len(moved_files)} documentation files:")
        for move in moved_files[:10]:  # Show first 10
            print(f"   📋 {move}")
        if len(moved_files) > 10:
            print(f"   ... and {len(moved_files) - 10} more")


    """Clean Temporary Files"""
def clean_temporary_files(root):
    """Remove temporary and test files"""
    temp_patterns = [
        "temp_*",
        "tmp_*",
        "*_temp.*",
        "*_tmp.*",
        "test_*.pdf",
        "debug_*",
        "*_backup.*",
        "*.temp",
        "*.bak",
    ]

    removed_files = []

    for pattern in temp_patterns:
        for file in root.glob(pattern):
            if file.is_file():
                try:
                    file.unlink()
                    removed_files.append(file.name)
                except Exception as e:
                    print(f"❌ Error removing {file.name}: {e}")

    if removed_files:
        print(f"\n🗑️  Removed {len(removed_files)} temporary files:")
        for file in removed_files[:5]:
            print(f"   🗂️  {file}")
        if len(removed_files) > 5:
            print(f"   ... and {len(removed_files) - 5} more")


    """Organize Config Files"""
def organize_config_files(root):
    """Move config files to config/ directory"""
    config_patterns = ["*.yml", "*.yaml", "*.toml", "*.ini", "*.cfg"]

    # Files that should stay in root
    keep_in_root = {
        ".gitignore",
        ".deepsource.toml",
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
    }

    moved_configs = []

    for pattern in config_patterns:
        for config_file in root.glob(pattern):
            if (
                config_file.is_file()
                and config_file.name not in keep_in_root
                and not config_file.name.startswith(".")
            ):

                try:
                    target = root / "config" / config_file.name
                    shutil.move(str(config_file), str(target))
                    moved_configs.append(config_file.name)
                except Exception as e:
                    print(f"❌ Error moving {config_file.name}: {e}")

    if moved_configs:
        print(f"\n⚙️  Moved {len(moved_configs)} config files to config/:")
        for config in moved_configs:
            print(f"   🔧 {config}")


if __name__ == "__main__":
    cleanup_repository()
