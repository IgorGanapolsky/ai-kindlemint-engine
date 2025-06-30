#!/usr/bin/env python3
"""
Performance Profiler for AI KindleMint Engine

This script profiles the performance of the Crossword Engine, specifically
focusing on the puzzle generation process to identify bottlenecks and ensure
it meets performance targets.

Key Features:
- Profiles the CrosswordEngineV3 using Python's built-in cProfile.
- Measures total and average time per puzzle generation.
- Compares performance against a configurable target (e.g., <10 seconds/puzzle).
- Identifies the most time-consuming functions (bottlenecks).
- Generates a detailed Markdown report with analysis and recommendations.
- Can be run from the command line and integrated into CI/CD workflows.

Usage:
  python scripts/performance_profiler.py --count 10 --report-path reports/perf_report.md
"""

import argparse
import cProfile
import io
import pstats
import shutil
import sys
import time
from pathlib import Path

# Ensure the 'scripts' directory is in the Python path for importing the engine
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

try:
    from scripts.crossword_engine_v3_fixed import CrosswordEngineV3
except ImportError:
    print(
        "❌ ERROR: Could not import CrosswordEngineV3. Make sure you are running this script from the project root."
    )
    sys.exit(1)

# --- Configuration ---
DEFAULT_PUZZLE_COUNT = 10
PERFORMANCE_TARGET_SECONDS = 10.0  # Target time per puzzle
TEMP_OUTPUT_DIR = project_root / "tmp_profiler_output"


class PerformanceProfiler:
    """Profiles the Crossword Engine and generates a performance report."""

    def __init__(self, puzzle_count, report_path, word_list_path=None):
        """
        Initializes the profiler.

        Args:
            puzzle_count (int): The number of puzzles to generate for the profile run.
            report_path (str): The path to save the output Markdown report.
            word_list_path (str, optional): Path to a custom word list for the engine.
        """
        self.puzzle_count = puzzle_count
        self.report_path = Path(report_path)
        self.word_list_path = word_list_path
        self.profiler = cProfile.Profile()
        self.total_duration = 0.0

    def _setup_environment(self):
        """Creates a temporary directory for the engine to write its output."""
        print(f"Setting up temporary environment at: {TEMP_OUTPUT_DIR}")
        if TEMP_OUTPUT_DIR.exists():
            shutil.rmtree(TEMP_OUTPUT_DIR)
        TEMP_OUTPUT_DIR.mkdir(parents=True)

    def _run_profiling(self):
        """Executes the crossword engine under the profiler."""
        print(f"\nProfiling CrosswordEngineV3 with {self.puzzle_count} puzzle(s)...")

        engine = CrosswordEngineV3(
            output_dir=str(TEMP_OUTPUT_DIR),
            puzzle_count=self.puzzle_count,
            word_list_path=self.word_list_path,
        )

        start_time = time.time()

        # Run the puzzle generation with the profiler enabled
        self.profiler.enable()
        engine.generate_puzzles()
        self.profiler.disable()

        end_time = time.time()
        self.total_duration = end_time - start_time

        print(f"Profiling complete. Total time: {self.total_duration:.2f} seconds.")

    def _generate_report(self):
        """Analyzes profiler data and generates a Markdown report."""
        print(f"Generating performance report at: {self.report_path}")

        # Create a string stream to capture pstats output
        s = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=s).sort_stats("cumulative")
        stats.print_stats()  # Print all stats to the stream

        profiler_output = s.getvalue()

        # --- Analysis ---
        avg_time_per_puzzle = (
            self.total_duration / self.puzzle_count if self.puzzle_count > 0 else 0
        )
        verdict = (
            "✅ PASS"
            if avg_time_per_puzzle <= PERFORMANCE_TARGET_SECONDS
            else "❌ FAIL"
        )

        # Find top 5 bottlenecks
        stats.sort_stats("tottime")  # Sort by time spent inside the function
        s_bottlenecks = io.StringIO()
        stats.print_stats(5)
        top_5_functions = (
            s_bottlenecks.getvalue()
        )  # This is a simplified way; direct parsing is better

        # A more robust way to get top functions
        top_functions_list = []
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            top_functions_list.append(
                {
                    "function": f"{func[2]} ({func[0]}:{func[1]})",
                    "ncalls": nc,
                    "tottime": tt,
                    "cumtime": ct,
                }
            )

        top_5_tottime = sorted(
            top_functions_list, key=lambda x: x["tottime"], reverse=True
        )[:5]
        top_5_cumtime = sorted(
            top_functions_list, key=lambda x: x["cumtime"], reverse=True
        )[:5]

        # --- Report Generation ---
        report_content = f"""
# ⚙️ Crossword Engine Performance Report

*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*

## 1. Executive Summary

| Metric                      | Value                               | Status                                      |
| --------------------------- | ----------------------------------- | ------------------------------------------- |
| Puzzles Generated           | `{self.puzzle_count}`               |                                             |
| Total Generation Time       | `{self.total_duration:.2f} seconds` |                                             |
| **Average Time per Puzzle** | `{avg_time_per_puzzle:.2f} seconds` | **{verdict}** (Target: < {PERFORMANCE_TARGET_SECONDS:.1f}s) |

---

## 2. Bottleneck Analysis

The following functions are the most significant contributors to the total execution time.

### Top 5 Functions by Total Time (Self)

*This measures time spent within the function itself, excluding sub-calls. High values here indicate inefficient code within the function.*

| Function Name | Total Time (s) | Num. Calls |
| ------------- | -------------- | ---------- |
"""
        for func in top_5_tottime:
            report_content += f"| `{func['function']}` | `{func['tottime']:.4f}` | `{func['ncalls']}` |\n"

        report_content += """
### Top 5 Functions by Cumulative Time

*This measures time spent in the function AND all functions it calls. High values here point to inefficient call chains.*

| Function Name | Cumulative Time (s) | Num. Calls |
| ------------- | ------------------- | ---------- |
"""
        for func in top_5_cumtime:
            report_content += f"| `{func['function']}` | `{func['cumtime']:.4f}` | `{func['ncalls']}` |\n"

        report_content += """
## 3. Recommendations

"""
        # Automated recommendations based on common bottlenecks
        bottleneck_found = False
        for func in top_5_tottime:
            if "_find_valid_words" in func["function"]:
                report_content += "- **High Priority**: The `_find_valid_words` function is a major bottleneck. This function iterates through the entire word dictionary for every slot. **Recommendation**: Pre-process the dictionary into a more efficient data structure, like a Trie or a hash map keyed by word length and letters at specific positions.\n"
                bottleneck_found = True
            if "_backtrack_fill" in func["function"]:
                report_content += "- **Medium Priority**: The `_backtrack_fill` function shows high cumulative time, which is expected for a backtracking algorithm. **Recommendation**: Ensure the slot-ordering heuristic (most constrained first) is effective. Profile the constraint-checking logic within the backtracking loop.\n"
                bottleneck_found = True

        if not bottleneck_found:
            report_content += "- No common bottlenecks were automatically detected. Review the full profiler output below for a detailed analysis.\n"

        report_content += f"""
---

## 4. Full Profiler Output (cProfile)

<details>
<summary>Click to expand the full profiler statistics</summary>

```
{profiler_output}
```
</details>
"""
        # Ensure the report directory exists
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w") as f:
            f.write(report_content)

        print("✅ Report generation complete.")

    def _cleanup(self):
        """Removes the temporary directory."""
        print(f"Cleaning up temporary environment: {TEMP_OUTPUT_DIR}")
        if TEMP_OUTPUT_DIR.exists():
            shutil.rmtree(TEMP_OUTPUT_DIR)

    def run(self):
        """Orchestrates the profiling process: setup, run, report, and cleanup."""
        try:
            self._setup_environment()
            self._run_profiling()
            self._generate_report()
        finally:
            self._cleanup()


def main():
    """Main entry point for the command-line profiler."""
    parser = argparse.ArgumentParser(
        description="Performance Profiler for the AI KindleMint Crossword Engine.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_PUZZLE_COUNT,
        help="Number of puzzles to generate during the profiling run.",
    )
    parser.add_argument(
        "--report-path",
        type=str,
        default=str(
            project_root
            / "reports"
            / f"performance_report_{time.strftime('%Y%m%d-%H%M%S')}.md"
        ),
        help="Output path for the Markdown performance report.",
    )
    parser.add_argument(
        "--word-list",
        type=str,
        help="Optional path to a custom word list file for the engine.",
    )

    args = parser.parse_args()

    if args.count <= 0:
        print("❌ ERROR: Puzzle count must be a positive integer.")
        sys.exit(1)

    profiler = PerformanceProfiler(
        puzzle_count=args.count,
        report_path=args.report_path,
        word_list_path=args.word_list,
    )
    profiler.run()


if __name__ == "__main__":
    main()
