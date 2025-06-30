#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script Consolidation Analysis Tool for AI KindleMint Engine

This tool analyzes the numerous `create_volume_*.py` scripts to facilitate
their consolidation into the single `unified_volume_generator.py`.

It performs the following steps:
1.  Scans the `scripts/` directory for all volume creation scripts.
2.  Parses each script's Abstract Syntax Tree (AST) to analyze its structure,
    features, and dependencies without executing the code.
3.  Compares the scripts to identify functional overlap and unique features.
4.  Generates a detailed report with actionable recommendations, including:
    - A list of obsolete scripts safe for removal.
    - A summary of key features to migrate.
    - A migration checklist.
    - A safe backup plan.

Usage:
    python scripts/consolidation_analysis.py
"""

import ast
import logging
import textwrap
from collections import defaultdict
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TARGET_SCRIPT_PATTERN = "create_volume_*.py"
UNIFIED_GENERATOR = "unified_volume_generator.py"
BACKUP_DIR = PROJECT_ROOT / "archive" / "obsolete_scripts_backup"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScriptFeatureAnalyzer(ast.NodeVisitor):
    """
    An AST visitor to extract key features from a Python script.
    """

    def __init__(self):
        self.features = {
            "imports": set(),
            "classes": [],
            "functions": [],
            "hardcoded_paths": set(),
            "hardcoded_dimensions": set(),
            "has_word_db": False,
            "has_clue_db": False,
        }

    def visit_Import(self, node):
        for alias in node.names:
            self.features["imports"].add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.features["imports"].add(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.features["classes"].append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.features["functions"].append(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Look for variable assignments that might be hardcoded values
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            # Check for hardcoded paths
            if "/" in node.value.value or "\\" in node.value.value:
                if "books/active_production" in node.value.value:
                    self.features["hardcoded_paths"].add(node.value.value)

        # Check for hardcoded dimensions (e.g., PAGE_WIDTH = 6 * inch)
        if isinstance(node.value, ast.BinOp):
            if isinstance(node.value.op, ast.Mult):
                if (
                    hasattr(node.targets[0], "id")
                    and "PAGE" in node.targets[0].id.upper()
                ):
                    # Attempt to reconstruct the assignment string for context
                    try:
                        # This is a simplification; a full unparser would be more robust
                        target_name = node.targets[0].id
                        left_val = node.value.left.value
                        right_name = node.value.right.id
                        self.features["hardcoded_dimensions"].add(
                            f"{target_name} = {left_val} * {right_name}"
                        )
                    except AttributeError:
                        pass  # Ignore complex assignments

        # Check for large dictionary assignments (word/clue dbs)
        if isinstance(node.value, ast.Dict):
            if len(node.value.keys) > 20:  # Heuristic for a large dict
                if hasattr(node.targets[0], "id"):
                    target_name = node.targets[0].id.lower()
                    if "word" in target_name:
                        self.features["has_word_db"] = True
                    if "clue" in target_name:
                        self.features["has_clue_db"] = True
        self.generic_visit(node)


class ConsolidationAnalyzer:
    """Analyzes scripts and generates a consolidation plan."""

    def __init__(self):
        self.scripts_to_analyze = []
        self.analysis_results = {}
        self.consolidation_plan = {
            "to_remove": [],
            "to_keep_for_reference": [],
            "features_to_migrate": defaultdict(list),
        }

    def find_volume_scripts(self):
        """Finds all scripts matching the target pattern."""
        self.scripts_to_analyze = sorted(list(SCRIPTS_DIR.glob(TARGET_SCRIPT_PATTERN)))
        logger.info(
            f"Found {len(self.scripts_to_analyze)} volume creation scripts to analyze."
        )

    def analyze_scripts(self):
        """Analyzes each found script to extract its features."""
        for script_path in self.scripts_to_analyze:
            logger.info(f"Analyzing {script_path.name}...")
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                tree = ast.parse(source_code)
                analyzer = ScriptFeatureAnalyzer()
                analyzer.visit(tree)
                self.analysis_results[script_path.name] = analyzer.features
            except Exception as e:
                logger.error(f"Could not parse {script_path.name}: {e}")
                self.analysis_results[script_path.name] = {"error": str(e)}

    def generate_plan(self):
        """Generates the consolidation and migration plan."""
        if not self.analysis_results:
            logger.warning("No scripts analyzed, cannot generate a plan.")
            return

        for name, features in self.analysis_results.items():
            if "error" in features:
                continue

            # Identify features to migrate by checking for unique/important logic
            if features["has_word_db"] or features["has_clue_db"]:
                self.consolidation_plan["features_to_migrate"][
                    "Word/Clue Databases"
                ].append(name)
            if features["hardcoded_dimensions"]:
                self.consolidation_plan["features_to_migrate"][
                    "Page Layout & Dimensions"
                ].append(name)
            if (
                "create_crossword_pattern" in features["functions"]
                or "PUZZLE_TEMPLATES" in self.analysis_results[name]
            ):
                self.consolidation_plan["features_to_migrate"][
                    "Grid Pattern Generation"
                ].append(name)

            # Decide which scripts to remove. A script is a good candidate for removal
            # if it's a simple experiment or clearly superseded by a more robust
            # version.
            is_simple_experiment = (
                features["has_word_db"] and len(features["functions"]) < 15
            )
            is_superseded = any(
                kw in name for kw in ["simple", "working", "balanced", "proper"]
            )

            if is_simple_experiment or is_superseded:
                self.consolidation_plan["to_remove"].append(name)
            else:
                self.consolidation_plan["to_keep_for_reference"].append(name)

        # Ensure we don't suggest removing everything if all are similar
        if (
            len(self.consolidation_plan["to_remove"]) == len(self.scripts_to_analyze)
            and self.scripts_to_analyze
        ):
            # Keep the most complex one for reference
            most_complex_script = max(
                self.analysis_results.items(),
                key=lambda item: len(item[1].get("functions", [])),
            )
            if most_complex_script[0] in self.consolidation_plan["to_remove"]:
                self.consolidation_plan["to_remove"].remove(most_complex_script[0])
                self.consolidation_plan["to_keep_for_reference"].append(
                    most_complex_script[0]
                )

    def generate_report(self):
        """Prints the full analysis and consolidation report."""
        report = []

        report.append("# 🚀 Script Consolidation & Tech Debt Reduction Plan")
        report.append(
            textwrap.dedent(
                f"""\
            This report analyzes the **{len(self.scripts_to_analyze)}** `create_volume_*.py` scripts and provides an actionable
            plan to consolidate them into the single, unified `{UNIFIED_GENERATOR}`.
        """
            )
        )

        # --- Backup Plan ---
        report.append("\n# 📂 1. Backup Plan (Safety First)")
        report.append(
            textwrap.dedent(
                f"""\
            Before deleting any files, a complete backup of the scripts will be created.
            This makes the process fully reversible.

            **Automated Backup Command:**
            ```bash
            mkdir -p "{BACKUP_DIR.relative_to(PROJECT_ROOT)}" && cp scripts/create_volume_*.py "{BACKUP_DIR.relative_to(PROJECT_ROOT)}/"
            ```
        """
            )
        )

        # --- Consolidation Plan ---
        report.append("\n# 📊 2. Consolidation Plan")
        report.append(
            "Based on the analysis, here is the plan for script consolidation:"
        )

        report.append("\n### ✅ Scripts to Remove (Obsolete / Superseded)")
        if self.consolidation_plan["to_remove"]:
            for script in sorted(self.consolidation_plan["to_remove"]):
                report.append(f"- `scripts/{script}`")
        else:
            report.append(
                "No scripts identified for immediate removal. Review manually."
            )

        report.append("\n### ⚠️ Scripts to Keep for Reference (Contains Unique Logic)")
        if self.consolidation_plan["to_keep_for_reference"]:
            for script in sorted(self.consolidation_plan["to_keep_for_reference"]):
                report.append(f"- `scripts/{script}`")
        else:
            report.append("No scripts identified to keep for reference.")

        # --- Migration Checklist ---
        report.append("\n# 📋 3. Migration Checklist to Unified Generator")
        report.append(
            f"The following features should be migrated to `{
                UNIFIED_GENERATOR}` and `config.yaml`."
        )

        checklist = []
        for feature, scripts in self.consolidation_plan["features_to_migrate"].items():
            unique_scripts = sorted(list(set(scripts)))
            script_list = ", ".join([f"`{s}`" for s in unique_scripts[:2]])
            if len(unique_scripts) > 2:
                script_list += f" and {len(unique_scripts) - 2} others"
            checklist.append(
                f"- [ ] **Migrate {feature}**: Review logic from {script_list}."
            )

        checklist.append(
            "- [ ] **Centralize Dimensions**: Ensure all page/grid dimensions from analyzed scripts are moved to `config.yaml`."
        )
        checklist.append(
            "- [ ] **Unify PDF Layout**: Create a single `BookLayout` class in the unified generator that handles all formats (paperback, hardcover)."
        )
        checklist.append(
            "- [ ] **Test Unified Generator**: Run the new generator for volumes 1-3 and compare output against the best of the old PDFs."
        )
        checklist.append(
            "- [ ] **Update Workflows**: Ensure all GitHub Actions workflows call `unified_volume_generator.py` or `generate_book.py` instead of old scripts."
        )
        checklist.append(
            "- [ ] **Execute Backup**: Run the backup command before deleting any files."
        )
        checklist.append(
            "- [ ] **Delete Obsolete Scripts**: After successful testing and migration, remove the files listed in the 'to_remove' section."
        )

        report.extend(checklist)

        return "\n".join(report)

    def run(self):
        """Runs the full analysis and prints the report."""
        logger.info("Starting script consolidation analysis...")
        self.find_volume_scripts()
        if not self.scripts_to_analyze:
            logger.warning("No volume creation scripts found to analyze. Exiting.")
            return

        self.analyze_scripts()
        self.generate_plan()
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("          Script Consolidation Analysis & Migration Plan")
        print("=" * 80)
        print(report)
        print("=" * 80)
        logger.info("Analysis complete. Review the plan above for next steps.")


def main():
    """Main entry point."""
    try:
        analyzer = ConsolidationAnalyzer()
        analyzer.run()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
