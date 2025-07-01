#!/usr/bin/env python3
"""
Generate Claude Cost Badges with Clear Time Period Labels
Creates multiple badges showing different cost metrics
"""

import json
import re
import sys
from pathlib import Path

from src.kindlemint.utils.cost_analytics import CostAnalytics

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def update_readme_badges(badges: dict, analytics: dict):
    """Update README.md with all cost badges"""
    repo_root = Path(__file__).parent.parent
    readme_file = repo_root / "README.md"
    cost_report_file = repo_root / "CLAUDE_COSTS.md"

    if not readme_file.exists():
        print("❌ README.md not found")
        return False

    # Read current README
    with open(readme_file, "r") as f:
        content = f.read()

    # Create badge markdown
    primary_badges = []
    secondary_badges = []

    # Primary row: Monthly, Budget, Trend
    primary_badges.append(
        f"[![Claude Monthly Cost]({badges['monthly']})](./CLAUDE_COSTS.md)"
    )
    primary_badges.append(
        f"[![Budget Status]({badges['budget']})](./CLAUDE_COSTS.md#budget)"
    )
    primary_badges.append(
        f"[![Cost Trend]({badges['trend']})](./CLAUDE_COSTS.md#trends)"
    )

    # Secondary row: Daily, Weekly, YTD
    secondary_badges.append(
        f"[![Daily Average]({badges['daily_avg']})](./CLAUDE_COSTS.md#daily)"
    )
    secondary_badges.append(
        f"[![Weekly Cost]({badges['weekly']})](./CLAUDE_COSTS.md#weekly)"
    )
    secondary_badges.append(
        f"[![YTD Cost]({badges['ytd']})](./CLAUDE_COSTS.md#yearly)")

    # Combined badge section
    badge_section = "\n".join(
        [
            "<!-- Claude Cost Tracking -->",
            " ".join(primary_badges),
            " ".join(secondary_badges),
            "",
        ]
    )

    # Pattern to match old Claude cost badge(s)
    old_badge_pattern = r"!\[Claude Cost\]\([^)]+\)"

    # Pattern to match the complete cost tracking section
    section_pattern = r"<!-- Claude Cost Tracking -->[\s\S]*?(?=\n(?:!\[|$))"

    # Try to replace existing section first
    if re.search(section_pattern, content):
        content = re.sub(section_pattern, badge_section.strip(), content)
        print("✅ Updated existing Claude cost tracking section")
    elif re.search(old_badge_pattern, content):
        # Replace old single badge with new section
        content = re.sub(old_badge_pattern,
                         badge_section.strip(), content, count=1)
        print("✅ Replaced old badge with new cost tracking section")
    else:
        # Add new section after other badges
        lines = content.split("\n")
        badge_line = None

        for i, line in enumerate(lines):
            # Find the last badge line
            if "img.shields.io" in line and "![" in line:
                badge_line = i

        if badge_line is not None:
            lines.insert(badge_line + 1, "")
            lines.insert(badge_line + 2, badge_section.strip())
            content = "\n".join(lines)
            print("✅ Added new Claude cost tracking section")

    # Write updated README
    with open(readme_file, "w") as f:
        f.write(content)

    # Generate detailed cost report
    analytics_engine = CostAnalytics()
    report = analytics_engine.generate_cost_report()

    with open(cost_report_file, "w") as f:
        f.write(report)

    print(f"✅ Generated detailed cost report: {cost_report_file}")

    return True


def main():
    """Main execution"""
    print("🔄 Generating Claude Cost Analytics...")

    # Initialize analytics engine
    analytics = CostAnalytics()

    # Calculate all time periods
    cost_data = analytics.calculate_time_periods()

    # Generate all badges
    badges = analytics.generate_badges(cost_data)

    # Display summary
    print("\n📊 Cost Summary:")
    print(f"  This Month: ${cost_data['periods']['month']['cost']:.2f}")
    print(f"  Daily Average: ${cost_data['daily_average']:.2f}")
    print(f"  Projected Monthly: ${cost_data['monthly_projection']:.2f}")
    print(
        f"  Budget Status: {(cost_data['periods']['month']['cost'] / 50.0 * 100):.0f}% of $50"
    )

    trend = cost_data["trends"]["month_over_month"]
    trend_symbol = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
    print(f"  Month-over-Month: {trend_symbol} {trend:+.1f}%")

    # Update README
    if update_readme_badges(badges, cost_data):
        print("\n✅ README.md updated with comprehensive cost tracking")
        print("📋 View detailed breakdown in CLAUDE_COSTS.md")
    else:
        print("\n❌ Failed to update README.md")


if __name__ == "__main__":
    main()
