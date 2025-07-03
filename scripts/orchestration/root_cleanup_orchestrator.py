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
            }
        }
        
    def analyze_root(self):
        """Analyze root directory for files to organize"""
        print("🔍 Analyzing root directory for cleanup...")
        print("=" * 60)
        
        root_files = [f for f in self.root.glob("*") if f.is_file()]
        print(f"📊 Found {len(root_files)} files in root directory")
        
        # Files that should stay in root
        keep_in_root = {
            "README.md", "LICENSE", "LICENSE.md", "LICENSE.txt",
            ".gitignore", ".gitattributes", ".env.example",
            "requirements.txt", "requirements-locked.txt",
            "setup.py", "setup.cfg", "pyproject.toml",
            "Makefile", "Dockerfile", "docker-compose.yml",
            "package.json", "package-lock.json",
            "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
            "SECURITY.md", "CHANGELOG.md"
        }
        
        files_to_move = []
        for file in root_files:
            if file.name not in keep_in_root:
                files_to_move.append(file)
                
        print(f"✅ {len(root_files) - len(files_to_move)} files should stay in root")
        print(f"📦 {len(files_to_move)} files can be organized")
        
        return files_to_move
        
    def plan_moves(self, files_to_move):
        """Plan file moves based on organization rules"""
        moves = []
        unmatched = []
        
        for file in files_to_move:
            matched = False
            for category, rule in self.organization_rules.items():
                for pattern in rule["patterns"]:
                    if file.match(pattern):
                        dest_dir = self.root / rule["dir"]
                        moves.append({
                            "file": file,
                            "dest_dir": dest_dir,
                            "category": category
                        })
                        matched = True
                        break
                if matched:
                    break
                    
            if not matched:
                unmatched.append(file)
                
        print(f"\n📋 Organization Plan:")
        print(f"  - Files to organize: {len(moves)}")
        print(f"  - Unmatched files: {len(unmatched)}")
        
        if unmatched:
            print(f"\n⚠️  Unmatched files (need manual review):")
            for f in unmatched[:10]:  # Show first 10
                print(f"    - {f.name}")
                
        return moves, unmatched
        
    def execute_moves(self, moves):
        """Execute the file moves"""
        print(f"\n🚀 Executing file organization...")
        
        # Group by destination
        by_dest = {}
        for move in moves:
            dest = move["dest_dir"]
            if dest not in by_dest:
                by_dest[dest] = []
            by_dest[dest].append(move)
            
        # Execute moves
        for dest_dir, move_list in by_dest.items():
            # Create destination directory
            dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n📁 Moving to {dest_dir.relative_to(self.root)}:")
            
            for move in move_list:
                src = move["file"]
                dest = dest_dir / src.name
                
                # Handle existing files
                if dest.exists():
                    # Add timestamp to avoid overwriting
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest = dest_dir / f"{src.stem}_{timestamp}{src.suffix}"
                    
                print(f"  - {src.name} → {dest.relative_to(self.root)}")
                shutil.move(str(src), str(dest))
                
        print(f"\n✅ Moved {len(moves)} files successfully!")
        
    def run(self, quiet=False):
        """Run the complete cleanup orchestration"""
        if not quiet:
            print("🧹 Root Directory Cleanup Orchestrator")
            print("=" * 60)
        
        # Step 1: Analyze
        files_to_move = self.analyze_root()
        
        if not files_to_move:
            if not quiet:
                print("\n✨ Root directory is already clean!")
            return
            
        # Step 2: Plan
        moves, unmatched = self.plan_moves(files_to_move)
        
        if not moves:
            print("\n⚠️  No files matched organization rules")
            return
            
        # Step 3: Execute
        self.execute_moves(moves)
        
        # Step 4: Report
        print("\n📊 Final Statistics:")
        root_files_after = len([f for f in self.root.glob("*") if f.is_file()])
        print(f"  - Root files before: {len(files_to_move) + root_files_after}")
        print(f"  - Root files after: {root_files_after}")
        print(f"  - Files organized: {len(moves)}")
        if unmatched:
            print(f"  - Files needing manual review: {len(unmatched)}")
            
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_moved": len(moves),
            "files_unmatched": len(unmatched),
            "root_files_remaining": root_files_after,
            "moves": [{"file": str(m["file"].name), "dest": str(m["dest_dir"].relative_to(self.root))} for m in moves],
            "unmatched": [str(f.name) for f in unmatched]
        }
        
        report_dir = self.root / "reports" / "orchestration"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"root_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
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