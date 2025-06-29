#!/usr/bin/env python3
"""
Automated Market Research PR Reviewer
Analyzes market research reports and makes decisions on content generation
"""

import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class MarketResearchAutoReviewer:
    """Automated reviewer for market research PRs"""

    def __init__(self):
        self.min_opportunity_score = 0.7  # Minimum score to consider an opportunity
        self.max_niches_per_day = 5  # Maximum niches to pursue daily
        self.required_criteria = {
            "market_size": 1000,  # Minimum market size
            "competition": "low",  # Maximum competition level
            "trend": "rising",  # Required trend direction
        }

    def analyze_pr(self, pr_number: str = None) -> Dict:
        """Analyze a market research PR and make decisions"""
        print("🤖 AUTOMATED MARKET RESEARCH REVIEWER")
        print("=" * 50)

        # Get PR details if number provided
        if pr_number:
            pr_files = self._get_pr_files(pr_number)
        else:
            # Find latest research files
            pr_files = self._find_latest_research_files()

        if not pr_files:
            return {"status": "error", "message": "No research files found"}

        # Analyze the research data
        analysis = self._analyze_research_data(pr_files)

        # Make decisions
        decisions = self._make_decisions(analysis)

        # Execute decisions
        if decisions["auto_merge"]:
            self._execute_decisions(decisions, pr_number)

        return decisions

    def _get_pr_files(self, pr_number: str) -> Dict:
        """Get files from a specific PR"""
        try:
            # Get PR files using gh CLI
            result = subprocess.run(
                ["gh", "pr", "view", pr_number, "--json", "files"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                pr_data = json.loads(result.stdout)
                files = {}

                for file in pr_data.get("files", []):
                    filename = file["path"]
                    if "market_analysis.csv" in filename:
                        files["csv"] = filename
                    elif "summary.json" in filename:
                        files["json"] = filename
                    elif "report.md" in filename:
                        files["report"] = filename

                return files
        except Exception as e:
            print(f"Error getting PR files: {e}")
            return {}

    def _find_latest_research_files(self) -> Dict:
        """Find the latest research files in the repository"""
        research_dir = Path("research")
        today = datetime.now().strftime("%Y-%m-%d")

        files = {}
        if research_dir.exists():
            today_dir = research_dir / today
            if today_dir.exists():
                csv_file = today_dir / "market_analysis.csv"
                json_file = today_dir / "summary.json"
                report_file = today_dir / "report.md"

                if csv_file.exists():
                    files["csv"] = str(csv_file)
                if json_file.exists():
                    files["json"] = str(json_file)
                if report_file.exists():
                    files["report"] = str(report_file)

        return files

    def _analyze_research_data(self, files: Dict) -> Dict:
        """Analyze the research data from files"""
        analysis = {
            "opportunities": [],
            "total_niches": 0,
            "viable_niches": 0,
            "top_scores": [],
            "market_trends": {},
        }

        # Analyze JSON summary
        if "json" in files:
            try:
                with open(files["json"], "r") as f:
                    summary = json.load(f)

                # Extract opportunities
                for niche in summary.get("niches", []):
                    score = self._calculate_opportunity_score(niche)
                    if score >= self.min_opportunity_score:
                        analysis["opportunities"].append(
                            {
                                "niche": niche.get("name", "Unknown"),
                                "score": score,
                                "metrics": niche,
                            }
                        )

                analysis["total_niches"] = len(summary.get("niches", []))
                analysis["viable_niches"] = len(analysis["opportunities"])

            except Exception as e:
                print(f"Error analyzing JSON: {e}")

        # Analyze CSV for detailed metrics
        if "csv" in files:
            try:
                with open(files["csv"], "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Extract market trends
                        trend = row.get("trend", "stable")
                        analysis["market_trends"][trend] = (
                            analysis["market_trends"].get(trend, 0) + 1
                        )
            except Exception as e:
                print(f"Error analyzing CSV: {e}")

        # Sort opportunities by score
        analysis["opportunities"].sort(key=lambda x: x["score"], reverse=True)
        analysis["top_scores"] = [opp["score"] for opp in analysis["opportunities"][:5]]

        return analysis

    def _calculate_opportunity_score(self, niche: Dict) -> float:
        """Calculate opportunity score for a niche"""
        score = 0.0
        weights = {
            "market_size": 0.3,
            "competition": 0.3,
            "trend": 0.2,
            "profitability": 0.2,
        }

        # Market size score
        market_size = niche.get("market_size", 0)
        if market_size > 10000:
            score += weights["market_size"] * 1.0
        elif market_size > 5000:
            score += weights["market_size"] * 0.7
        elif market_size > 1000:
            score += weights["market_size"] * 0.4

        # Competition score
        competition = niche.get("competition", "high")
        if competition == "low":
            score += weights["competition"] * 1.0
        elif competition == "medium":
            score += weights["competition"] * 0.5

        # Trend score
        trend = niche.get("trend", "stable")
        if trend == "rising":
            score += weights["trend"] * 1.0
        elif trend == "stable":
            score += weights["trend"] * 0.5

        # Profitability score
        profit_margin = niche.get("profit_margin", 0)
        if profit_margin > 50:
            score += weights["profitability"] * 1.0
        elif profit_margin > 30:
            score += weights["profitability"] * 0.7
        elif profit_margin > 20:
            score += weights["profitability"] * 0.4

        return round(score, 2)

    def _make_decisions(self, analysis: Dict) -> Dict:
        """Make automated decisions based on analysis"""
        decisions = {
            "auto_merge": False,
            "selected_niches": [],
            "reasoning": [],
            "actions": [],
        }

        # Check if we have viable opportunities
        if analysis["viable_niches"] == 0:
            decisions["reasoning"].append("No viable niches found with score >= 0.7")
            decisions["actions"].append("Request manual review for edge cases")
            return decisions

        # Select top niches
        selected_count = min(self.max_niches_per_day, len(analysis["opportunities"]))
        decisions["selected_niches"] = analysis["opportunities"][:selected_count]

        # Determine if we should auto-merge
        if analysis["viable_niches"] >= 3 and analysis["top_scores"][0] >= 0.8:
            decisions["auto_merge"] = True
            decisions["reasoning"].append(
                f"Found {analysis['viable_niches']} high-quality opportunities"
            )
            decisions["reasoning"].append(
                f"Top opportunity score: {analysis['top_scores'][0]}"
            )

            # Generate actions
            for niche in decisions["selected_niches"]:
                decisions["actions"].append(
                    f"Generate content for: {niche['niche']} (score: {niche['score']})"
                )
        else:
            decisions["reasoning"].append("Opportunities need manual review")
            decisions["reasoning"].append(
                f"Best score: {analysis['top_scores'][0] if analysis['top_scores'] else 0}"
            )

        # Add market insights
        rising_trends = analysis["market_trends"].get("rising", 0)
        if rising_trends > 0:
            decisions["reasoning"].append(f"Found {rising_trends} rising market trends")

        return decisions

    def _execute_decisions(self, decisions: Dict, pr_number: str = None):
        """Execute the automated decisions"""
        print("\n📊 DECISION REPORT")
        print("=" * 50)

        # Print reasoning
        print("\n🧠 Reasoning:")
        for reason in decisions["reasoning"]:
            print(f"  • {reason}")

        # Print selected niches
        print(
            f"\n✅ Selected {len(decisions['selected_niches'])} niches for content generation:"
        )
        for niche in decisions["selected_niches"]:
            print(f"  • {niche['niche']} (score: {niche['score']})")

        # Print actions
        print("\n🎯 Actions to execute:")
        for action in decisions["actions"]:
            print(f"  • {action}")

        if decisions["auto_merge"] and pr_number:
            print(f"\n🤖 Auto-merging PR #{pr_number}...")

            # Create content generation tasks
            self._create_content_tasks(decisions["selected_niches"])

            # Merge the PR
            try:
                result = subprocess.run(
                    ["gh", "pr", "merge", pr_number, "--auto", "--merge"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ PR merged successfully!")
                else:
                    print(f"❌ Failed to merge PR: {result.stderr}")
            except Exception as e:
                print(f"❌ Error merging PR: {e}")
        else:
            print("\n⚠️ Manual review required - PR not auto-merged")

    def _create_content_tasks(self, selected_niches: List[Dict]):
        """Create content generation tasks for selected niches"""
        tasks_file = Path("tasks") / "content_generation_queue.json"
        tasks_file.parent.mkdir(exist_ok=True)

        # Load existing tasks
        existing_tasks = []
        if tasks_file.exists():
            with open(tasks_file, "r") as f:
                existing_tasks = json.load(f)

        # Add new tasks
        for niche in selected_niches:
            task = {
                "id": f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(existing_tasks)}",
                "type": "content_generation",
                "niche": niche["niche"],
                "priority": "high" if niche["score"] >= 0.9 else "medium",
                "metrics": niche["metrics"],
                "created_at": datetime.now().isoformat(),
                "status": "pending",
            }
            existing_tasks.append(task)

        # Save updated tasks
        with open(tasks_file, "w") as f:
            json.dump(existing_tasks, f, indent=2)

        print(f"\n📝 Created {len(selected_niches)} content generation tasks")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Market Research PR Reviewer"
    )
    parser.add_argument("--pr", type=str, help="PR number to review")
    parser.add_argument(
        "--auto", action="store_true", help="Enable fully automated mode"
    )

    args = parser.parse_args()

    reviewer = MarketResearchAutoReviewer()

    # Analyze and make decisions
    decisions = reviewer.analyze_pr(args.pr)

    # In manual mode, ask for confirmation
    if not args.auto and decisions.get("auto_merge"):
        print("\n❓ Proceed with automated actions? (y/n): ", end="")
        if input().lower() != "y":
            print("🚫 Automated actions cancelled")
            decisions["auto_merge"] = False

    return 0 if decisions.get("status") != "error" else 1


if __name__ == "__main__":
    sys.exit(main())
