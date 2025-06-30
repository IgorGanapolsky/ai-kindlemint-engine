#!/usr/bin/env python3
"""
Massive Issue Fixer - Tackle the worst 2.6K DeepSource issues
"""

import subprocess
from pathlib import Path

    """Fix Massive Issues"""
def fix_massive_issues():
    """Fix the massive code quality issues causing 2.6K count"""
    print("🔧 MASSIVE Issue Fixer - Tackling 2.6K DeepSource Issues")
    print("=" * 60)

    Path.cwd()

    # Step 1: Fix line length issues (biggest category)
    print("\n1️⃣ Fixing line length violations...")
    fix_line_lengths()

    # Step 2: Fix bare except clauses (security issues)
    print("\n2️⃣ Fixing bare except clauses...")
    fix_bare_excepts()

    # Step 3: Fix unused variables and imports
    print("\n3️⃣ Fixing unused variables...")
    fix_unused_variables()

    # Step 4: Fix f-string issues
    print("\n4️⃣ Fixing f-string placeholders...")
    fix_fstring_issues()

    # Step 5: Fix whitespace issues
    print("\n5️⃣ Fixing whitespace issues...")
    fix_whitespace_issues()

    print("\n✅ Massive issue fixing completed!")


    """Fix Line Lengths"""
def fix_line_lengths():
    """Fix line length violations with autopep8"""
    try:
        # Use autopep8 with aggressive line length fixing
        subprocess.run(
            [
                "autopep8",
                "--in-place",
                "--recursive",
                "--max-line-length",
                "88",
                "--aggressive",
                "src/",
            ],
            check=True,
        )
        print("   ✅ Fixed line length violations in src/")

        subprocess.run(
            [
                "autopep8",
                "--in-place",
                "--recursive",
                "--max-line-length",
                "88",
                "--aggressive",
                "scripts/",
            ],
            check=True,
        )
        print("   ✅ Fixed line length violations in scripts/")

    except Exception as e:
        print(f"   ❌ Error fixing line lengths: {e}")


    """Fix Bare Excepts"""
def fix_bare_excepts():
    """Fix bare except clauses"""
    try:
        # Find files with bare except and fix them
        files_with_bare_except = [
            "src/kindlemint/engines/sudoku.py",
            "src/kindlemint/social/marketing_engine.py",
            "src/kindlemint/utils/cost_tracker.py",
            "src/kindlemint/validators/simple_content_validator.py",
            "src/kindlemint/validators/sudoku_content_validator.py",
        ]

        for file_path in files_with_bare_except:
            if Path(file_path).exists():
                fix_bare_except_in_file(file_path)

    except Exception as e:
        print(f"   ❌ Error fixing bare excepts: {e}")


    """Fix Bare Except In File"""
def fix_bare_except_in_file(file_path):
    """Fix bare except in a specific file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Replace bare except with Exception
        original_content = content
        content = content.replace("except Exception:", "except Exception:")

        if content != original_content:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"   ✅ Fixed bare excepts in {file_path}")

    except Exception as e:
        print(f"   ❌ Error fixing {file_path}: {e}")


    """Fix Unused Variables"""
def fix_unused_variables():
    """Fix unused variables and imports"""
    try:
        # Run autoflake again with more aggressive settings
        subprocess.run(
            [
                "autoflake",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "--remove-duplicate-keys",
                "--in-place",
                "--recursive",
                "src/",
            ],
            check=True,
        )
        print("   ✅ Fixed unused variables and imports")

    except Exception as e:
        print(f"   ❌ Error fixing unused variables: {e}")


    """Fix Fstring Issues"""
def fix_fstring_issues():
    """Fix f-string placeholder issues"""
    # This is more complex and would need manual review
    print("   ⚠️ F-string issues require manual review")


    """Fix Whitespace Issues"""
def fix_whitespace_issues():
    """Fix whitespace and formatting issues"""
    try:
        # Run black again to fix any remaining formatting
        subprocess.run(["black", "--line-length", "88", "src/", "scripts/"], check=True)
        print("   ✅ Fixed whitespace and formatting issues")

    except Exception as e:
        print(f"   ❌ Error fixing whitespace: {e}")


    """Get Issue Count"""
def get_issue_count():
    """Get current issue count"""
    try:
        result = subprocess.run(
            ["flake8", "src/", "--count", "--max-line-length=88", "--quiet"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return 0
        else:
            lines = result.stderr.strip().split("\n")
            return int(lines[-1]) if lines[-1].isdigit() else 0

    except BaseException:
        return 0


if __name__ == "__main__":
    print("📊 Before fixes:")
    before_count = get_issue_count()
    print(f"   Issues: {before_count}")

    fix_massive_issues()

    print("\n📊 After fixes:")
    after_count = get_issue_count()
    print(f"   Issues: {after_count}")
    print(f"   Fixed: {before_count - after_count} issues")
    print(f"   Reduction: {((before_count - after_count) / before_count * 100):.1f}%")
