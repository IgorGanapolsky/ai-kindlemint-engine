#!/usr/bin/env python3
"""
REAL Repository Hygiene Analyzer
Analyzes actual repository organization, not just untracked files
"""

import os
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime


class RealHygieneAnalyzer:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or os.getcwd())

    def analyze_real_hygiene(self):
        """Analyze ACTUAL repository organization"""
        print("🔍 REAL Repository Hygiene Analysis")
        print("=" * 50)

        issues = []
        root_files = list(self.project_root.glob("*"))

        # 1. Check root directory clutter
        root_clutter = self._check_root_clutter(root_files)
        if root_clutter:
            issues.extend(root_clutter)

        # 2. Check documentation organization
        doc_issues = self._check_documentation_organization()
        if doc_issues:
            issues.extend(doc_issues)

        # 3. Check for scattered config files
        config_issues = self._check_scattered_configs()
        if config_issues:
            issues.extend(config_issues)

        # Calculate REAL hygiene score
        hygiene_score = self._calculate_real_score(issues, root_files)

        report = {
            "timestamp": datetime.now().isoformat(),
            "real_hygiene_score": hygiene_score,
            "total_issues": len(issues),
            "issues": issues,
            "root_file_count": len([f for f in root_files if f.is_file()]),
            "recommendations": self._generate_recommendations(issues),
        }

        self._print_report(report)
        return report

    def _check_root_clutter(self, root_files):
        """Check for files that shouldn't be in root directory"""
        issues = []

        # Files that should be in docs/
        root_md_files = [
            f for f in root_files if f.suffix == ".md" and f.name != "README.md"
        ]
        if len(root_md_files) > 3:  # Allow a few, but not dozens
            issues.append(
                {
                    "type": "root_documentation_clutter",
                    "severity": "high",
                    "count": len(root_md_files),
                    "message": f"{len(root_md_files)} .md files in root (should be in docs/)",
                    "files": [f.name for f in root_md_files[:10]],
                    "all_files": [f.name for f in root_md_files],
                }
            )

        # Check for other clutter
        suspicious_files = []
        for file in root_files:
            if file.is_file():
                name = file.name.lower()
                # Files that suggest poor organization
                if any(
                    keyword in name
                    for keyword in [
                        "temp",
                        "tmp",
                        "backup",
                        "old",
                        "copy",
                        "test_",
                        "debug",
                        "migration",
                        "analysis",
                        "report",
                        "summary",
                    ]
                ):
                    suspicious_files.append(file.name)

        if suspicious_files:
            issues.append(
                {
                    "type": "suspicious_root_files",
                    "severity": "medium",
                    "count": len(suspicious_files),
                    "message": "Temporary/analysis files in root directory",
                    "files": suspicious_files,
                }
            )

        return issues

    def _check_documentation_organization(self):
        """Check if documentation is properly organized"""
        issues = []

        docs_dir = self.project_root / "docs"
        root_md_count = len(list(self.project_root.glob("*.md"))) - 1  # Exclude README

        if root_md_count > 5 and not docs_dir.exists():
            issues.append(
                {
                    "type": "missing_docs_directory",
                    "severity": "high",
                    "message": f"{root_md_count} .md files in root but no docs/ directory",
                    "recommendation": "Create docs/ directory and organize documentation",
                }
            )

        # Check for poorly named documentation
        md_files = list(self.project_root.glob("*.md"))
        verbose_names = [f for f in md_files if len(f.stem) > 30]
        if verbose_names:
            issues.append(
                {
                    "type": "verbose_documentation_names",
                    "severity": "medium",
                    "count": len(verbose_names),
                    "message": "Documentation files with overly long names",
                    "files": [f.name for f in verbose_names],
                }
            )

        return issues

    def _check_scattered_configs(self):
        """Check for configuration files that should be organized"""
        issues = []

        config_extensions = [".yml", ".yaml", ".json", ".toml", ".ini", ".cfg"]
        root_configs = [
            f
            for f in self.project_root.glob("*")
            if f.is_file()
            and f.suffix in config_extensions
            and not f.name.startswith(".")  # Exclude dotfiles like .gitignore
        ]

        if len(root_configs) > 8:  # Some configs in root are normal
            issues.append(
                {
                    "type": "excessive_root_configs",
                    "severity": "medium",
                    "count": len(root_configs),
                    "message": f"{len(root_configs)} config files in root directory",
                    "files": [f.name for f in root_configs],
                }
            )

        return issues

    def _calculate_real_score(self, issues, root_files):
        """Calculate actual repository hygiene score"""
        score = 100.0

        # Penalize root clutter heavily
        root_file_count = len([f for f in root_files if f.is_file()])
        if root_file_count > 15:  # Reasonable limit
            score -= min(30, (root_file_count - 15) * 2)  # -2 points per extra file

        # Penalize issues
        for issue in issues:
            if issue["severity"] == "high":
                score -= 20
            elif issue["severity"] == "medium":
                score -= 10
            else:
                score -= 5

        return max(0, score)

    def _generate_recommendations(self, issues):
        """Generate cleanup recommendations"""
        recommendations = []

        for issue in issues:
            if issue["type"] == "root_documentation_clutter":
                recommendations.append(
                    {
                        "action": "create_docs_directory",
                        "priority": "high",
                        "description": "Create docs/ directory and move .md files there",
                        "commands": ["mkdir docs", "mv *.md docs/ (except README.md)"],
                    }
                )

            elif issue["type"] == "missing_docs_directory":
                recommendations.append(
                    {
                        "action": "organize_documentation",
                        "priority": "high",
                        "description": "Create proper documentation structure",
                        "commands": [
                            "mkdir docs",
                            "mkdir docs/architecture docs/api docs/guides",
                        ],
                    }
                )

        return recommendations

    def _print_report(self, report):
        """Print detailed hygiene report"""
        print(f"\n📊 REAL Hygiene Score: {report['real_hygiene_score']:.1f}/100")
        print(f"🗂️  Root Files: {report['root_file_count']}")
        print(f"⚠️  Issues Found: {report['total_issues']}")

        if report["issues"]:
            print(f"\n🚨 Issues:")
            for issue in report["issues"]:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(
                    f"   {
                        severity_emoji.get(
                            issue['severity'],
                            '⚪')} {
                        issue['message']}"
                )
                if "files" in issue and len(issue["files"]) <= 5:
                    for file in issue["files"]:
                        print(f"      - {file}")
                elif "files" in issue:
                    for file in issue["files"][:3]:
                        print(f"      - {file}")
                    print(f"      ... and {len(issue['files']) - 3} more")

        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   📋 {rec['description']} (Priority: {rec['priority']})")


if __name__ == "__main__":
    analyzer = RealHygieneAnalyzer()
    analyzer.analyze_real_hygiene()
