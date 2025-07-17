#!/usr/bin/env python3
"""
Autonomous Syntax Fixer for CI Failures
Monitors CI, detects syntax errors, and auto-fixes them
"""

import os
import re
import subprocess
import time
from datetime import datetime
from typing import List, Tuple

class AutonomousSyntaxFixer:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo = "IgorGanapolsky/ai-kindlemint-engine"
        
    def get_latest_failures(self) -> List[Tuple[str, int]]:
        """Extract file:line from CI failure logs"""
        cmd = [
            "gh", "run", "list", 
            "--workflow=tests.yml",
            "--limit=1",
            "--json", "databaseId"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return []
            
        # Get the run ID and fetch logs
        import json
        runs = json.loads(result.stdout)
        if not runs:
            return []
            
        run_id = runs[0]['databaseId']
        
        # Get failure logs
        cmd = ["gh", "run", "view", str(run_id), "--log"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Extract file:line patterns
        failures = []
        pattern = r'File "([^"]+)", line (\d+)'
        for match in re.finditer(pattern, result.stdout):
            filepath = match.group(1)
            line_num = int(match.group(2))
            # Convert absolute path to relative
            if "/ai-kindlemint-engine/" in filepath:
                filepath = filepath.split("/ai-kindlemint-engine/")[1]
            failures.append((filepath, line_num))
            
        return failures
    
    def fix_common_syntax_errors(self, filepath: str) -> bool:
        """Fix common syntax patterns that break CI"""
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        original = content
        
        # Fix broken f-strings
        content = re.sub(
            r'f"\s*{\s*\n\s*([^}]+)\s*}',
            r'f"{\1}',
            content,
            flags=re.MULTILINE
        )
        
        # Fix async function definitions  
        content = re.sub(
            r'async\s+"""([^"]+)"""\s*\ndef\s+(\w+)',
            r'async def \2():\n    """\1"""',
            content
        )
        
        # Fix duplicate __init__ methods
        lines = content.split('\n')
        cleaned_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            if line.strip() == 'def __init__(self):' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == '' or next_line.startswith('def __init__'):
                    skip_next = True
                    continue
                    
            cleaned_lines.append(line)
            
        content = '\n'.join(cleaned_lines)
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
            
        return False
    
    def create_fix_commit(self, fixed_files: List[str]):
        """Create and push a fix commit"""
        # Stage files
        subprocess.run(["git", "add"] + fixed_files)
        
        # Commit
        message = f"""fix: Auto-repair syntax errors breaking CI

Fixed {len(fixed_files)} files with syntax errors:
{chr(10).join('- ' + f for f in fixed_files)}

Automated fix by CI orchestration"""
        
        subprocess.run(["git", "commit", "-m", message])
        subprocess.run(["git", "push"])
        
    def run_continuous_monitoring(self):
        """Run continuous monitoring and fixing"""
        print("🤖 Autonomous Syntax Fixer Started")
        print("=" * 50)
        
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for CI failures...")
            
            failures = self.get_latest_failures()
            if failures:
                print(f"🔴 Found {len(failures)} syntax errors")
                
                fixed_files = []
                for filepath, line_num in failures:
                    print(f"  Fixing: {filepath}:{line_num}")
                    if self.fix_common_syntax_errors(filepath):
                        fixed_files.append(filepath)
                        
                if fixed_files:
                    print(f"✅ Fixed {len(fixed_files)} files")
                    self.create_fix_commit(fixed_files)
                    print("📤 Pushed fixes to main")
                else:
                    print("⚠️  Unable to auto-fix, manual intervention needed")
            else:
                print("✅ No syntax errors detected")
                
            # Wait 5 minutes before next check
            time.sleep(300)

if __name__ == "__main__":
    fixer = AutonomousSyntaxFixer()
    
    # One-time check mode
    failures = fixer.get_latest_failures()
    if failures:
        print(f"Found {len(failures)} syntax errors to fix")
        for f, l in failures:
            print(f"  - {f}:{l}")
    else:
        print("No syntax errors found in latest CI run")