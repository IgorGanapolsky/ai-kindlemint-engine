#!/usr/bin/env python3
"""
Intelligent Merge Conflict Resolver
Automatically resolves common merge conflicts using AI and pattern recognition
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import openai
from anthropic import Anthropic


class ConflictType(Enum):
    """Types of merge conflicts"""

    IMPORT_STATEMENTS = "import_statements"
    VERSION_NUMBERS = "version_numbers"
    WHITESPACE = "whitespace"
    FORMATTING = "formatting"
    SIMPLE_ADDITION = "simple_addition"
    DEPENDENCY_VERSION = "dependency_version"
    CONFIG_MERGE = "config_merge"
    SEMANTIC = "semantic"
    COMPLEX = "complex"


@dataclass
class ConflictResolution:
    """Resolution for a merge conflict"""

    file_path: str
    conflict_type: ConflictType
    resolution: str
    confidence: float
    explanation: str


class MergeConflictResolver:
    """Intelligently resolves merge conflicts"""

    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        if use_ai:
            self.openai_client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"))
            self.anthropic_client = Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Patterns for identifying conflict types
        self.conflict_patterns = {
            ConflictType.IMPORT_STATEMENTS: re.compile(
                r"^(from|import)\s+.*$", re.MULTILINE
            ),
            ConflictType.VERSION_NUMBERS: re.compile(
                r'version\s*[=:]\s*["\']?[\d.]+["\']?', re.IGNORECASE
            ),
            ConflictType.WHITESPACE: re.compile(r"^[\s\t]*$", re.MULTILINE),
            ConflictType.DEPENDENCY_VERSION: re.compile(r"[\w-]+\s*[=<>]+\s*[\d.]+"),
        }

    def analyze_repository_conflicts(self) -> List[str]:
        """Find all files with merge conflicts in the repository"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True,
                check=True,
            )

            conflicted_files = result.stdout.strip().split("\n")
            return [f for f in conflicted_files if f]
        except subprocess.CalledProcessError:
            return []

    def extract_conflict_blocks(self, file_content: str) -> List[Dict[str, str]]:
        """Extract conflict blocks from file content"""
        conflicts = []
        lines = file_content.split("\n")

        i = 0
        while i < len(lines):
            if lines[i].startswith("<<<<<<<"):
                # Found conflict start
                ours_start = i + 1
                theirs_start = None
                end = None

                # Find markers
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("======="):
                        theirs_start = j + 1
                    elif lines[j].startswith(">>>>>>>"):
                        end = j
                        break

                if theirs_start and end:
                    conflicts.append(
                        {
                            "ours": "\n".join(lines[ours_start: theirs_start - 1]),
                            "theirs": "\n".join(lines[theirs_start:end]),
                            "start_line": i,
                            "end_line": end,
                        }
                    )
                    i = end + 1
                else:
                    i += 1
            else:
                i += 1

        return conflicts

    def identify_conflict_type(self, conflict: Dict[str, str]) -> ConflictType:
        """Identify the type of conflict"""
        ours = conflict["ours"]
        theirs = conflict["theirs"]

        # Check for import statements
        if self.conflict_patterns[ConflictType.IMPORT_STATEMENTS].search(
            ours
        ) and self.conflict_patterns[ConflictType.IMPORT_STATEMENTS].search(theirs):
            return ConflictType.IMPORT_STATEMENTS

        # Check for version numbers
        if self.conflict_patterns[ConflictType.VERSION_NUMBERS].search(
            ours
        ) or self.conflict_patterns[ConflictType.VERSION_NUMBERS].search(theirs):
            return ConflictType.VERSION_NUMBERS

        # Check for dependency versions
        if self.conflict_patterns[ConflictType.DEPENDENCY_VERSION].search(
            ours
        ) and self.conflict_patterns[ConflictType.DEPENDENCY_VERSION].search(theirs):
            return ConflictType.DEPENDENCY_VERSION

        # Check for whitespace-only conflicts
        if ours.strip() == "" or theirs.strip() == "":
            return ConflictType.WHITESPACE

        # Check for simple additions (both sides add different content)
        if not ours or not theirs:
            return ConflictType.SIMPLE_ADDITION

        # Check for configuration files
        if any(
            conflict.get("file_path", "").endswith(ext)
            for ext in [".json", ".yaml", ".yml", ".toml"]
        ):
            return ConflictType.CONFIG_MERGE

        # Default to semantic for code conflicts
        return ConflictType.SEMANTIC

    def resolve_import_conflict(self, ours: str, theirs: str) -> Tuple[str, float]:
        """Resolve import statement conflicts"""
        # Combine all unique imports
        our_imports = set(line.strip()
                          for line in ours.split("\n") if line.strip())
        their_imports = set(line.strip()
                            for line in theirs.split("\n") if line.strip())

        # Merge and sort imports
        all_imports = our_imports.union(their_imports)

        # Group imports
        from_imports = sorted(
            [imp for imp in all_imports if imp.startswith("from")])
        direct_imports = sorted(
            [imp for imp in all_imports if imp.startswith("import")]
        )

        # Combine with proper formatting
        result = []
        if direct_imports:
            result.extend(direct_imports)
        if from_imports and direct_imports:
            result.append("")  # Blank line between import types
        if from_imports:
            result.extend(from_imports)

        return "\n".join(result), 0.95

    def resolve_version_conflict(self, ours: str, theirs: str) -> Tuple[str, float]:
        """Resolve version number conflicts"""
        # Extract version numbers
        our_version = self.extract_version(ours)
        their_version = self.extract_version(theirs)

        if our_version and their_version:
            # Use the higher version
            if self.compare_versions(our_version, their_version) >= 0:
                return ours, 0.8
            else:
                return theirs, 0.8

        # If can't determine, prefer theirs (incoming changes)
        return theirs, 0.6

    def extract_version(self, text: str) -> Optional[str]:
        """Extract version number from text"""
        match = re.search(r"([\d]+\.[\d]+\.[\d]+)", text)
        return match.group(1) if match else None

    def compare_versions(self, v1: str, v2: str) -> int:
        """Compare version strings"""
        v1_parts = list(map(int, v1.split(".")))
        v2_parts = list(map(int, v2.split(".")))

        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0

            if v1_part > v2_part:
                return 1
            elif v1_part < v2_part:
                return -1

        return 0

    def resolve_whitespace_conflict(self, ours: str, theirs: str) -> Tuple[str, float]:
        """Resolve whitespace-only conflicts"""
        # Prefer non-empty content
        if ours.strip():
            return ours, 0.9
        elif theirs.strip():
            return theirs, 0.9
        else:
            # Both are whitespace, use minimal
            return "", 1.0

    def resolve_dependency_conflict(self, ours: str, theirs: str) -> Tuple[str, float]:
        """Resolve dependency version conflicts"""
        # Parse dependencies
        our_deps = self.parse_dependencies(ours)
        their_deps = self.parse_dependencies(theirs)

        # Merge, preferring higher versions
        merged = {}
        for dep in set(list(our_deps.keys()) + list(their_deps.keys())):
            if dep in our_deps and dep in their_deps:
                # Compare versions
                if self.compare_versions(our_deps[dep], their_deps[dep]) >= 0:
                    merged[dep] = our_deps[dep]
                else:
                    merged[dep] = their_deps[dep]
            elif dep in our_deps:
                merged[dep] = our_deps[dep]
            else:
                merged[dep] = their_deps[dep]

        # Reconstruct dependency list
        result = []
        for dep, version in sorted(merged.items()):
            result.append(f"{dep}>={version}")

        return "\n".join(result), 0.85

    def parse_dependencies(self, text: str) -> Dict[str, str]:
        """Parse dependency specifications"""
        deps = {}
        for line in text.split("\n"):
            match = re.match(r"([\w-]+)\s*[=<>]+\s*([\d.]+)", line.strip())
            if match:
                deps[match.group(1)] = match.group(2)
        return deps

    def resolve_with_ai(
        self, conflict: Dict[str, str], file_path: str, conflict_type: ConflictType
    ) -> Tuple[str, float, str]:
        """Use AI to resolve complex conflicts"""
        if not self.use_ai:
            return conflict["theirs"], 0.5, "AI disabled, using incoming changes"

        prompt = f"""Resolve this merge conflict in {file_path}.
        
Conflict type: {conflict_type.value}

Current branch (ours):
```
{conflict['ours']}
```

Incoming branch (theirs):
```
{conflict['theirs']}
```

Provide:
1. The resolved code (no conflict markers)
2. Confidence score (0-1)
3. Brief explanation of resolution

Consider:
- Preserve functionality from both sides
- Maintain code style consistency
- Prefer safer resolutions
- If unsure, explain why manual review is needed
"""

        try:
            # Try Claude first for better code understanding
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content = response.content[0].text

            # Extract resolved code
            code_match = re.search(r"```[\w]*\n(.*?)\n```", content, re.DOTALL)
            resolved_code = code_match.group(
                1) if code_match else conflict["theirs"]

            # Extract confidence
            conf_match = re.search(
                r"confidence[:\s]*([\d.]+)", content, re.IGNORECASE)
            confidence = float(conf_match.group(1)) if conf_match else 0.6

            # Extract explanation
            explanation = "AI-resolved conflict based on semantic analysis"

            return resolved_code, confidence, explanation

        except Exception as e:
            # Fallback to simpler resolution
            return conflict["theirs"], 0.5, f"AI resolution failed: {str(e)}"

    def resolve_conflict(
        self, conflict: Dict[str, str], file_path: str
    ) -> ConflictResolution:
        """Resolve a single conflict"""
        conflict_type = self.identify_conflict_type(conflict)
        conflict["file_path"] = file_path

        resolution = None
        confidence = 0.0
        explanation = ""

        # Apply type-specific resolution strategies
        if conflict_type == ConflictType.IMPORT_STATEMENTS:
            resolution, confidence = self.resolve_import_conflict(
                conflict["ours"], conflict["theirs"]
            )
            explanation = "Merged and sorted import statements"

        elif conflict_type == ConflictType.VERSION_NUMBERS:
            resolution, confidence = self.resolve_version_conflict(
                conflict["ours"], conflict["theirs"]
            )
            explanation = "Selected higher version number"

        elif conflict_type == ConflictType.WHITESPACE:
            resolution, confidence = self.resolve_whitespace_conflict(
                conflict["ours"], conflict["theirs"]
            )
            explanation = "Resolved whitespace conflict"

        elif conflict_type == ConflictType.DEPENDENCY_VERSION:
            resolution, confidence = self.resolve_dependency_conflict(
                conflict["ours"], conflict["theirs"]
            )
            explanation = "Merged dependencies with higher versions"

        elif conflict_type == ConflictType.SIMPLE_ADDITION:
            # Both additions are usually wanted
            if conflict["ours"] and conflict["theirs"]:
                resolution = f"{conflict['ours']}\n{conflict['theirs']}"
                confidence = 0.7
                explanation = "Kept both additions"
            else:
                resolution = conflict["ours"] or conflict["theirs"]
                confidence = 0.9
                explanation = "Kept single addition"

        else:
            # Complex conflicts need AI or manual review
            resolution, confidence, explanation = self.resolve_with_ai(
                conflict, file_path, conflict_type
            )

        return ConflictResolution(
            file_path=file_path,
            conflict_type=conflict_type,
            resolution=resolution,
            confidence=confidence,
            explanation=explanation,
        )

    def resolve_file_conflicts(
        self, file_path: str, min_confidence: float = 0.7
    ) -> List[ConflictResolution]:
        """Resolve all conflicts in a file"""
        with open(file_path, "r") as f:
            content = f.read()

        conflicts = self.extract_conflict_blocks(content)
        resolutions = []

        for conflict in conflicts:
            resolution = self.resolve_conflict(conflict, file_path)
            resolutions.append(resolution)

        # Apply resolutions if confidence is high enough
        if all(r.confidence >= min_confidence for r in resolutions):
            self.apply_resolutions(file_path, content, conflicts, resolutions)

        return resolutions

    def apply_resolutions(
        self,
        file_path: str,
        original_content: str,
        conflicts: List[Dict],
        resolutions: List[ConflictResolution],
    ):
        """Apply resolutions to file"""
        lines = original_content.split("\n")

        # Apply resolutions in reverse order to maintain line numbers
        for conflict, resolution in zip(reversed(conflicts), reversed(resolutions)):
            start = conflict["start_line"]
            end = conflict["end_line"] + 1

            # Replace conflict with resolution
            lines[start:end] = resolution.resolution.split("\n")

        # Write resolved content
        with open(file_path, "w") as f:
            f.write("\n".join(lines))

    def resolve_all_conflicts(
        self, auto_apply: bool = False, min_confidence: float = 0.7
    ) -> Dict[str, List[ConflictResolution]]:
        """Resolve all conflicts in the repository"""
        conflicted_files = self.analyze_repository_conflicts()
        all_resolutions = {}

        for file_path in conflicted_files:
            try:
                resolutions = self.resolve_file_conflicts(
                    file_path, min_confidence)
                all_resolutions[file_path] = resolutions

                if auto_apply and all(
                    r.confidence >= min_confidence for r in resolutions
                ):
                    print(f"✅ Auto-resolved {file_path} with high confidence")
                else:
                    print(
                        f"⚠️  {file_path} needs manual review (confidence too low)")

            except Exception as e:
                print(f"❌ Error resolving {file_path}: {e}")
                all_resolutions[file_path] = []

        return all_resolutions

    def generate_resolution_report(
        self, resolutions: Dict[str, List[ConflictResolution]]
    ) -> Dict:
        """Generate a report of all resolutions"""
        report = {
            "total_files": len(resolutions),
            "total_conflicts": sum(len(r) for r in resolutions.values()),
            "auto_resolved": 0,
            "manual_review_needed": 0,
            "resolutions_by_type": {},
            "confidence_distribution": {
                "high": 0,  # >= 0.8
                "medium": 0,  # 0.6 - 0.8
                "low": 0,  # < 0.6
            },
            "files": {},
        }

        for file_path, file_resolutions in resolutions.items():
            file_report = {
                "conflicts": len(file_resolutions),
                "min_confidence": (
                    min(r.confidence for r in file_resolutions)
                    if file_resolutions
                    else 0
                ),
                "resolutions": [],
            }

            all_high_confidence = all(
                r.confidence >= 0.7 for r in file_resolutions)
            if all_high_confidence and file_resolutions:
                report["auto_resolved"] += 1
            else:
                report["manual_review_needed"] += 1

            for resolution in file_resolutions:
                # Count by type
                conflict_type = resolution.conflict_type.value
                report["resolutions_by_type"][conflict_type] = (
                    report["resolutions_by_type"].get(conflict_type, 0) + 1
                )

                # Count by confidence
                if resolution.confidence >= 0.8:
                    report["confidence_distribution"]["high"] += 1
                elif resolution.confidence >= 0.6:
                    report["confidence_distribution"]["medium"] += 1
                else:
                    report["confidence_distribution"]["low"] += 1

                file_report["resolutions"].append(
                    {
                        "type": conflict_type,
                        "confidence": resolution.confidence,
                        "explanation": resolution.explanation,
                    }
                )

            report["files"][file_path] = file_report

        return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Intelligent Merge Conflict Resolver")
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Automatically apply high-confidence resolutions",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence threshold for auto-apply",
    )
    parser.add_argument(
        "--use-ai", action="store_true", help="Use AI for complex conflict resolution"
    )
    parser.add_argument("--report", type=str,
                        help="Save resolution report to file")

    args = parser.parse_args()

    resolver = MergeConflictResolver(use_ai=args.use_ai)
    resolutions = resolver.resolve_all_conflicts(
        auto_apply=args.auto_apply, min_confidence=args.min_confidence
    )

    # Generate and display report
    report = resolver.generate_resolution_report(resolutions)

    print("\n📊 Merge Conflict Resolution Report")
    print("=" * 50)
    print(f"Total files with conflicts: {report['total_files']}")
    print(f"Total conflicts found: {report['total_conflicts']}")
    print(f"Auto-resolved: {report['auto_resolved']}")
    print(f"Manual review needed: {report['manual_review_needed']}")

    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {args.report}")
