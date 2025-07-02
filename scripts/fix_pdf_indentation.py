#!/usr/bin/env python3
"""
Fix indentation issues in PDF generators
"""

import re
from pathlib import Path


def fix_function_indentation(file_path):
    """Fix function indentation in PDF generator files"""

    with open(file_path, "r") as f:
        content = f.read()

    # Fix patterns like:
    # """Comment"""
    # def function_name(self):

    # Pattern 1: Comment followed by unindented function
    content = re.sub(
        r'(\s*)""".*?"""\s*\ndef ([a-zA-Z_][a-zA-Z0-9_]*\(self)',
        r"\1def \2",
        content,
        flags=re.MULTILINE,
    )

    # Pattern 2: Class with unindented methods
    lines = content.split("\n")
    fixed_lines = []
    in_class = False
    class_indent = 0

    for line in lines:
        # Check if we're starting a class
        if line.strip().startswith("class ") and ":" in line:
            in_class = True
            class_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue

        # Check if we're starting a function outside class
        if line.strip().startswith("def ") and not line.strip().startswith("def __"):
            if in_class and line.startswith("def "):
                # This is a class method that needs indentation
                fixed_line = " " * (class_indent + 4) + line.strip()
                fixed_lines.append(fixed_line)
                continue

        # Check if we're leaving the class
        if (
            in_class
            and line.strip()
            and not line.startswith(" ")
            and not line.strip().startswith("#")
        ):
            if not line.strip().startswith('"""') and not line.strip().startswith(
                "'''"
            ):
                if line.strip().startswith("def ") or line.strip().startswith("class "):
                    in_class = False

        fixed_lines.append(line)

    # Write back the fixed content
    with open(file_path, "w") as f:
        f.write("\n".join(fixed_lines))

    print(f"✅ Fixed indentation in {file_path}")


def main():
    """Fix indentation in all PDF generators"""

    scripts_dir = Path(".")

    pdf_generators = ["market_aligned_sudoku_pdf.py",
                      "sudoku_pdf_layout_v2.py"]

    for generator in pdf_generators:
        file_path = scripts_dir / generator
        if file_path.exists():
            fix_function_indentation(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")


if __name__ == "__main__":
    main()
