#!/usr/bin/env python3
"""
Clean up the validator chaos - establish single source of truth
"""

import shutil
from pathlib import Path

# Validators to deprecate (not delete, just move to deprecated folder)
DEPRECATED_VALIDATORS = [
    "scripts/sudoku_validator.py",
    "scripts/crossword_content_validator.py",
    "scripts/comprehensive_qa_validator.py",
    "scripts/production_qa_validator.py",
    "scripts/enhanced_qa_validator.py",
    "scripts/enhanced_qa_validator_v2.py",
    "scripts/enhanced_qa_validator_v3.py",
    "scripts/test_standard_validator.py",
]

# Report generators to deprecate
DEPRECATED_REPORT_GENERATORS = [
    "simple_content_validation",
    "sudoku_content_validation",
    "pdf_image_validation",
]


    """Cleanup Validators"""
def cleanup_validators():
    """Move deprecated validators to archive."""
    base_dir = Path(__file__).parent.parent
    deprecated_dir = base_dir / "deprecated_validators"
    deprecated_dir.mkdir(exist_ok=True)

    print("🧹 Cleaning up validator chaos...")
    print(f"📁 Moving deprecated validators to: {deprecated_dir}")

    moved_count = 0
    for validator in DEPRECATED_VALIDATORS:
        validator_path = base_dir / validator
        if validator_path.exists():
            dest = deprecated_dir / validator_path.name
            shutil.move(str(validator_path), str(dest))
            print(f"  ✓ Moved: {validator}")
            moved_count += 1

    print(f"\n✅ Moved {moved_count} deprecated validators")

    # Create a README in the deprecated folder
    readme_content = """# Deprecated Validators

These validators have been replaced by the unified validator:
- `/scripts/unified_sudoku_qa_validator.py` - Single source of truth

## Why these were deprecated:
- Multiple validators creating contradicting reports
- Each checking different aspects without coordination
- Confusing output with 5+ different report files
- No visual validation in most validators

## DO NOT USE THESE - Use unified_sudoku_qa_validator.py instead!
"""

    with open(deprecated_dir / "README.md", "w") as f:
        f.write(readme_content)

    # Update the main QA validator to use the unified one
    main_qa_path = base_dir / "src/kindlemint/validators/sudoku_book_qa.py"
    if main_qa_path.exists():
        print(f"\n📝 Adding deprecation notice to: {main_qa_path}")

        with open(main_qa_path, "r") as f:
            content = f.read()

        if "DEPRECATED" not in content:
            deprecation_notice = '''"""
DEPRECATED: This validator produces incomplete/misleading results.
Use scripts/unified_sudoku_qa_validator.py instead!

'''
            content = content.replace('"""', deprecation_notice, 1)

            with open(main_qa_path, "w") as f:
                f.write(content)

    print("\n✅ Validator cleanup complete!")
    print("📊 From now on, use: scripts/unified_sudoku_qa_validator.py")


if __name__ == "__main__":
    cleanup_validators()
