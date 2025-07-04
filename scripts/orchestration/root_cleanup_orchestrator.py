#!/usr/bin/env python3
"""
Root Directory Cleanup Orchestrator
Organizes files from root into appropriate directories
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class RootCleanupOrchestrator:
    def __init__(self):
        self.root = Path(os.getcwd())
        self.moves = []
        
        # Define organization rules
        self.organization_rules = {
            "reports": {
                "dir": "reports/hygiene",
                "patterns": ["hygiene_report*.json", "archive_cleanup_report.json", "*_report.json", "*_report.md"]
            },
            "costs": {
                "dir": "reports/costs",
                "patterns": ["*_costs.json", "cost_*.json", "CLAUDE_COSTS.md"]
            },
            "scripts_to_move": {
                "dir": "scripts/utilities",
                "patterns": ["ceo_notification_fix.sh", "disable_noisy_workflows.py", "add_book_asins.py"]
            },
            "service_files": {
                "dir": "infrastructure/services",
                "patterns": ["*.service"]
            },
            "amp_files": {
                "dir": "docs/amp",
                "patterns": ["amp.progress.txt"]
            },
            "test_outputs": {
                "dir": "tests/outputs",
                "patterns": ["test_*.pdf", "test_*.png", "test_*.json", "*_test.pdf", "*_test.png"]
            },
            "temp_files": {
                "dir": "tests/tmp",
                "patterns": ["*.tmp", "*.temp", "tmp_*", "temp_*"]
            }
        }
        
        # Define directory organization rules
        self.directory_rules = {
            "archive": {
                "dest": "archive_backup",
                "description": "Old archives and backups"
            },
            "sentry_enhanced": {
                "dest": "reports/sentry",
                "description": "Sentry research data"
            },
            "deprecated_validators": {
                "dest": "archive_backup/deprecated",
                "description": "Deprecated code"
            },
            "test_outputs": {
                "dest": "tests/outputs",
                "description": "Test output files"
            },
            "content": {
                "dest": "marketing/content",
                "description": "Marketing content and strategies"
            },
            "aws_code_backup_20250701_121329": {
                "dest": "archive_backup/aws",
                "description": "AWS infrastructure backup"
            },
            # Generic patterns for common directories
            "test_output": {
                "dest": "tests/outputs",
                "description": "Test output files"
            },
            "tmp": {
                "dest": "tests/tmp",
                "description": "Temporary test files"
            },
            "temp": {
                "dest": "tests/tmp",
                "description": "Temporary files"
            }
        }
        
        # Define directory organization rules
        self.directory_rules = {
            "archive": {
                "dest": "archive_backup",
                "description": "Old archives and backups"
            },
            "sentry_enhanced": {
                "dest": "reports/sentry",
                "description": "Sentry research data"
            },
            "deprecated_validators": {
                "dest": "archive_backup/deprecated",
                "description": "Deprecated code"
            },
            "features": {
                "dest": "archive_backup/auto_generated_stubs",
                "description": "Auto-generated feature stubs"
            }
        }
        
    def analyze_root(self):
        """Analyze root directory for files and directories to organize"""
        if not self.quiet:
            print("🔍 Analyzing root directory for cleanup...")
            print("=" * 60)
        
        root_files = [f for f in self.root.glob("*") if f.is_file()]
        root_dirs = [d for d in self.root.glob("*") if d.is_dir() and not d.name.startswith('.')]
        
        if not self.quiet:
            print(f"📊 Found {len(root_files)} files in root directory")
            print(f"📁 Found {len(root_dirs)} directories in root directory")
        
        # Files that should stay in root
        keep_in_root = {
            "README.md", "LICENSE", "LICENSE.md", "LICENSE.txt",
            ".gitignore", ".gitattributes", ".env.example",
            "requirements.txt", "requirements-locked.txt",
            "setup.py", "setup.cfg", "pyproject.toml",
            "Makefile", "Dockerfile", "docker-compose.yml",
            "package.json", "package-lock.json",
            "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
            "SECURITY.md", "CHANGELOG.md",
            ".worktree_config.json", ".worktree_orchestration_config.json",
            ".deepsource.toml", "sonar-project.properties"
        }
        
        # Directories that should stay in root
        keep_dirs_in_root = {
            "src", "tests", "scripts", "docs", "assets",
            "landing-pages", "agents", "reports", "infrastructure",
            "worktrees", "templates", "fonts", ".github", "__pycache__"
        }
        
        files_to_move = []
        for file in root_files:
            if file.name not in keep_in_root:
                files_to_move.append(file)
        
        dirs_to_move = []
        for dir in root_dirs:
            if dir.name not in keep_dirs_in_root:
                dirs_to_move.append(dir)
            # Check for stub/empty directories even if whitelisted
            elif dir.name == "features":
                # Check if it's just auto-generated stubs
                py_files = list(dir.rglob("*.py"))
                if py_files:
                    # Check if files are just stubs (< 100 lines total)
                    total_lines = 0
                    for py_file in py_files:
                        try:
                            total_lines += len(py_file.read_text().splitlines())
                        except:
                            pass
                    if total_lines < 100 and len(py_files) < 5:
                        dirs_to_move.append(dir)
                        if not self.quiet:
                            print(f"  🚨 Detected stub directory: {dir.name}/")
                
        if not self.quiet:
            print(f"✅ {len(root_files) - len(files_to_move)} files should stay in root")
            print(f"✅ {len(root_dirs) - len(dirs_to_move)} directories should stay in root")
            print(f"📦 {len(files_to_move)} files can be organized")
            print(f"📁 {len(dirs_to_move)} directories can be organized")
            
            if dirs_to_move:
                print("\n📁 Directories to organize:")
                for dir in dirs_to_move:
                    file_count = len(list(dir.rglob("*")))
                    print(f"  - {dir.name}/ ({file_count} items)")
        
        return files_to_move, dirs_to_move
        
    def plan_moves(self, files_to_move, dirs_to_move):
        """Plan file and directory moves based on organization rules"""
        file_moves = []
        dir_moves = []
        unmatched_files = []
        unmatched_dirs = []
        
        # Plan file moves
        for file in files_to_move:
            matched = False
            for category, rule in self.organization_rules.items():
                for pattern in rule["patterns"]:
                    if file.match(pattern):
                        dest_dir = self.root / rule["dir"]
                        file_moves.append({
                            "file": file,
                            "dest_dir": dest_dir,
                            "category": category
                        })
                        matched = True
                        break
                if matched:
                    break
                    
            if not matched:
                unmatched_files.append(file)
        
        # Plan directory moves
        for dir_path in dirs_to_move:
            if dir_path.name in self.directory_rules:
                rule = self.directory_rules[dir_path.name]
                dest_dir = self.root / rule["dest"]
                dir_moves.append({
                    "dir": dir_path,
                    "dest_dir": dest_dir,
                    "description": rule["description"]
                })
            else:
                unmatched_dirs.append(dir_path)
                
        if not self.quiet:
            print(f"\n📋 Organization Plan:")
            print(f"  - Files to organize: {len(file_moves)}")
            print(f"  - Directories to organize: {len(dir_moves)}")
            print(f"  - Unmatched files: {len(unmatched_files)}")
            print(f"  - Unmatched directories: {len(unmatched_dirs)}")
            
            if unmatched_files:
                print(f"\n⚠️  Unmatched files (need manual review):")
                for f in unmatched_files[:10]:  # Show first 10
                    print(f"    - {f.name}")
                    
            if unmatched_dirs:
                print(f"\n⚠️  Unmatched directories (need manual review):")
                for d in unmatched_dirs[:10]:  # Show first 10
                    print(f"    - {d.name}/")
                
        return file_moves, dir_moves, unmatched_files, unmatched_dirs
        
    def execute_moves(self, file_moves, dir_moves):
        """Execute the file and directory moves"""
        if not self.quiet:
            print(f"\n🚀 Executing organization...")
        
        total_moves = 0
        
        # Execute file moves
        if file_moves:
            if not self.quiet:
                print("\n📄 Moving files...")
            
            # Group by destination
            by_dest = {}
            for move in file_moves:
                dest = move["dest_dir"]
                if dest not in by_dest:
                    by_dest[dest] = []
                by_dest[dest].append(move)
                
            # Execute file moves
            for dest_dir, move_list in by_dest.items():
                # Create destination directory
                dest_dir.mkdir(parents=True, exist_ok=True)
                if not self.quiet:
                    print(f"\n📁 Moving to {dest_dir.relative_to(self.root)}:")
                
                for move in move_list:
                    src = move["file"]
                    dest = dest_dir / src.name
                    
                    # Handle existing files
                    if dest.exists():
                        # Add timestamp to avoid overwriting
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest = dest_dir / f"{src.stem}_{timestamp}{src.suffix}"
                        
                    if not self.quiet:
                        print(f"  - {src.name} → {dest.relative_to(self.root)}")
                    shutil.move(str(src), str(dest))
                    total_moves += 1
        
        # Execute directory moves
        if dir_moves:
            if not self.quiet:
                print(f"\n📁 Moving directories...")
            
            for move in dir_moves:
                src_dir = move["dir"]
                dest_parent = move["dest_dir"]
                dest_dir = dest_parent / src_dir.name
                
                # Create parent directory if it doesn't exist
                dest_parent.mkdir(parents=True, exist_ok=True)
                
                # Handle existing directories
                if dest_dir.exists():
                    # Add timestamp to avoid overwriting
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_dir = dest_parent / f"{src_dir.name}_{timestamp}"
                
                if not self.quiet:
                if not self.quiet:
                    print(f"  - {src_dir.name}/ → {dest_dir.relative_to(self.root)}/ ({move['description']})")
                
                shutil.move(str(src_dir), str(dest_dir))
                total_moves += 1
                
        if not self.quiet:
            print(f"\n✅ Moved {total_moves} items successfully!")
        
    def run(self, quiet=False):
        """Run the complete cleanup orchestration"""
        self.quiet = quiet
        
        if not quiet:
            print("🧹 Root Directory Cleanup Orchestrator")
            print("=" * 60)
        
        # Step 1: Analyze
        files_to_move, dirs_to_move = self.analyze_root()
        
        if not files_to_move and not dirs_to_move:
            if not quiet:
                print("\n✨ Root directory is already clean!")
            return
            
        # Step 2: Plan
        file_moves, dir_moves, unmatched_files, unmatched_dirs = self.plan_moves(files_to_move, dirs_to_move)
        
        if not file_moves and not dir_moves:
            if not quiet:
                print("\n⚠️  No files or directories matched organization rules")
            return
            
        # Step 3: Execute
        self.execute_moves(file_moves, dir_moves)
        
        # Step 4: Report
        if not quiet:
            print("\n📊 Final Statistics:")
            root_files_after = len([f for f in self.root.glob("*") if f.is_file()])
            root_dirs_after = len([d for d in self.root.glob("*") if d.is_dir() and not d.name.startswith('.')])
            print(f"  - Root files before: {len(files_to_move) + root_files_after}")
            print(f"  - Root files after: {root_files_after}")
            print(f"  - Root directories before: {len(dirs_to_move) + root_dirs_after}")
            print(f"  - Root directories after: {root_dirs_after}")
            print(f"  - Files organized: {len(file_moves)}")
            print(f"  - Directories organized: {len(dir_moves)}")
            if unmatched_files:
                print(f"  - Files needing manual review: {len(unmatched_files)}")
            if unmatched_dirs:
                print(f"  - Directories needing manual review: {len(unmatched_dirs)}")
            
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_moved": len(file_moves),
            "directories_moved": len(dir_moves),
            "files_unmatched": len(unmatched_files),
            "directories_unmatched": len(unmatched_dirs),
            "root_files_remaining": len([f for f in self.root.glob("*") if f.is_file()]),
            "root_dirs_remaining": len([d for d in self.root.glob("*") if d.is_dir() and not d.name.startswith('.')]),
            "file_moves": [{"file": str(m["file"].name), "dest": str(m["dest_dir"].relative_to(self.root))} for m in file_moves],
            "dir_moves": [{"dir": str(m["dir"].name), "dest": str(m["dest_dir"].relative_to(self.root)), "description": m["description"]} for m in dir_moves],
            "unmatched_files": [str(f.name) for f in unmatched_files],
            "unmatched_dirs": [str(d.name) for d in unmatched_dirs]
        }
        
        report_dir = self.root / "reports" / "orchestration"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"root_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        if not quiet:
            print(f"\n📄 Report saved to: {report_path.relative_to(self.root)}")


if __name__ == "__main__":
    import sys
    import os
    
    quiet = "--quiet" in sys.argv
    orchestrator = RootCleanupOrchestrator()
    
    if quiet:
        # Redirect stdout to suppress output
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
    try:
        orchestrator.run(quiet=quiet)
    finally:
        if quiet:
            sys.stdout = old_stdout