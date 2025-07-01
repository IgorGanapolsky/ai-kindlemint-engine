#!/usr/bin/env python3
"""
Tactical Command Center - CLI Interface
Command line interface for tactical orchestration and competitive advantage
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from kindlemint.orchestrator.competitive_intelligence_orchestrator import (
    CompetitiveIntelligenceOrchestrator,
)
from kindlemint.orchestrator.professional_quality_orchestrator import (
    ProfessionalQualityOrchestrator,
)
from kindlemint.orchestrator.tactical_advantage_orchestrator import (
    TacticalAdvantageOrchestrator,
)
from kindlemint.orchestrator.tactical_seo_orchestrator import (
    TacticalSEOOrchestrator,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TacticalCommandCenter:
    """Command center for tactical orchestration operations"""

    def __init__(self):
        self.advantage_orchestrator = TacticalAdvantageOrchestrator()
        self.seo_orchestrator = TacticalSEOOrchestrator()
        self.competitive_orchestrator = CompetitiveIntelligenceOrchestrator()
        self.quality_orchestrator = ProfessionalQualityOrchestrator()

    async def run_full_tactical_analysis(
        self, book_metadata: Dict, output_file: Optional[str] = None
    ) -> Dict:
        """Run complete tactical analysis for competitive advantage"""
        print("🎯 TACTICAL COMMAND CENTER - INITIATING FULL ANALYSIS")
        print("=" * 60)

        # Run master tactical advantage orchestration
        print("🚀 Running master tactical advantage orchestration...")
        tactical_report = (
            await self.advantage_orchestrator.orchestrate_tactical_advantage(
                book_metadata
            )
        )

        # Save results if output file specified
        if output_file:
            with open(output_file, "w") as f:
                json.dump(tactical_report, f, indent=2, default=str)
            print(f"📊 Results saved to: {output_file}")

        # Display executive summary
        self._display_executive_summary(tactical_report)

        return tactical_report

    async def run_seo_dominance(
        self, book_metadata: Dict, output_file: Optional[str] = None
    ) -> Dict:
        """Run tactical SEO analysis for 2025 dominance"""
        print("🔍 TACTICAL SEO DOMINANCE ANALYSIS")
        print("=" * 40)

        seo_report = await self.seo_orchestrator.orchestrate_seo_intelligence(
            book_metadata
        )

        if output_file:
            with open(output_file, "w") as f:
                json.dump(seo_report, f, indent=2, default=str)

        self._display_seo_summary(seo_report)
        return seo_report

    async def run_competitive_intelligence(
        self, output_file: Optional[str] = None
    ) -> Dict:
        """Run competitive intelligence analysis"""
        print("🕵️ COMPETITIVE INTELLIGENCE ANALYSIS")
        print("=" * 40)

        competitive_report = (
            await self.competitive_orchestrator.orchestrate_competitive_intelligence()
        )

        if output_file:
            with open(output_file, "w") as f:
                json.dump(competitive_report, f, indent=2, default=str)

        self._display_competitive_summary(competitive_report)
        return competitive_report

    async def run_quality_assessment(
        self, book_project: Dict, output_file: Optional[str] = None
    ) -> Dict:
        """Run professional quality assessment"""
        print("🎨 PROFESSIONAL QUALITY ASSESSMENT")
        print("=" * 40)

        quality_report = await self.quality_orchestrator.orchestrate_quality_assurance(
            book_project
        )

        if output_file:
            with open(output_file, "w") as f:
                json.dump(quality_report, f, indent=2, default=str)

        self._display_quality_summary(quality_report)
        return quality_report

    def _display_executive_summary(self, tactical_report: Dict):
        """Display executive summary of tactical analysis"""
        print("\n📋 EXECUTIVE SUMMARY")
        print("-" * 30)

        advantage_score = tactical_report.get("advantage_score", 0)
        dominance_potential = tactical_report.get(
            "market_dominance_potential", {})

        print(f"Overall Advantage Score: {advantage_score:.2f}/1.0")
        print(
            f"Market Dominance Potential: {dominance_potential.get('potential', 'Unknown')}"
        )
        print(
            f"Success Probability: {dominance_potential.get('probability', 0):.0%}")

        # Top strategic advantages
        strategic_advantages = tactical_report.get("strategic_advantages", {})
        top_advantages = strategic_advantages.get("top_advantages", [])[:3]

        if top_advantages:
            print("\n🎯 TOP STRATEGIC ADVANTAGES:")
            for i, advantage in enumerate(top_advantages, 1):
                print(f"  {i}. {advantage.get('advantage_type', 'Unknown')}")
                print(
                    f"     Impact: {advantage.get('competitive_impact', 0):.0%}")
                print(
                    f"     Priority: {advantage.get('priority_score', 0):.2f}")

        # Implementation timeline
        implementation = tactical_report.get("implementation_plan", {})
        phases = implementation.get("implementation_phases", {})

        print(f"\n⏱️ IMPLEMENTATION TIMELINE:")
        print(f"  Immediate Actions: {len(phases.get('immediate', []))}")
        print(f"  Short-term (1-4 weeks): {len(phases.get('short_term', []))}")
        print(
            f"  Medium-term (1-3 months): {len(phases.get('medium_term', []))}")
        print(f"  Long-term (3+ months): {len(phases.get('long_term', []))}")

        # ROI projections
        roi = implementation.get("roi_projections", {})
        if roi:
            print(f"\n💰 ROI PROJECTIONS:")
            print(f"  6-month ROI: {roi.get('6_month_roi', 'TBD')}%")
            print(f"  12-month ROI: {roi.get('12_month_roi', 'TBD')}%")
            print(f"  Break-even: {roi.get('break_even', 'TBD')}")

    def _display_seo_summary(self, seo_report: Dict):
        """Display SEO analysis summary"""
        print(
            f"\n📈 SEO Advantage Score: {seo_report.get('competitive_advantage_score', 0):.2f}"
        )

        optimization_2025 = seo_report.get("2025_optimization", {})
        print(
            f"2025 Readiness: {optimization_2025.get('overall_2025_score', 0):.2f}")
        print(
            f"Readiness Level: {optimization_2025.get('readiness_level', 'Unknown')}")

        trends = seo_report.get("trend_opportunities", {})
        print(f"Trend Urgency Score: {trends.get('urgency_score', 0):.2f}")

        if "hot_keywords" in trends:
            print(f"Hot Keywords: {', '.join(trends['hot_keywords'][:3])}")

    def _display_competitive_summary(self, competitive_report: Dict):
        """Display competitive analysis summary"""
        print(
            f"\n🏆 Competitive Score: {competitive_report.get('competitive_advantage_score', 0):.2f}"
        )

        threat_assessment = competitive_report.get("threat_assessment", {})
        print(
            f"Threat Level: {threat_assessment.get('overall_threat_level', 'Unknown')}"
        )

        opportunities = competitive_report.get("market_opportunities", {})
        top_opportunities = opportunities.get("top_opportunities", [])[:2]

        if top_opportunities:
            print("Top Market Opportunities:")
            for opp in top_opportunities:
                print(
                    f"  - {opp.get('niche', 'Unknown')}: {opp.get('strategic_fit', 0):.2f}"
                )

    def _display_quality_summary(self, quality_report: Dict):
        """Display quality assessment summary"""
        print(
            f"\n🎨 Overall Quality Score: {quality_report.get('overall_quality_score', 0):.2f}"
        )

        certification = quality_report.get("quality_certification", {})
        print(
            f"Quality Certification: {certification.get('certification_level', 'None')}"
        )

        compliance = quality_report.get("professional_compliance", {})
        print(
            f"Professional Compliance: {compliance.get('overall_compliance', 0):.2f}")

        visual_quality = quality_report.get("visual_quality", {})
        print(
            f"Visual Quality Level: {visual_quality.get('professional_level', 'Unknown')}"
        )


def load_book_metadata(metadata_file: str) -> Dict:
    """Load book metadata from file"""
    try:
        with open(metadata_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return {}


def create_sample_metadata() -> Dict:
    """Create sample book metadata for testing"""
    return {
        "title": "Large Print Crossword Masters",
        "subtitle": "50 Easy, Relaxing Crossword Puzzles for Seniors - Volume 1",
        "author": "Crossword Masters Publishing",
        "category": "puzzle_books",
        "target_audience": "seniors",
        "keywords": [
            "large print crossword puzzles",
            "senior crossword book",
            "easy crossword puzzles",
            "brain games for seniors",
        ],
        "description": "Professional crossword puzzles designed for seniors with large print format",
        "price": 12.99,
        "pages": 120,
        "format": "paperback",
        "competitive_positioning": "quality_leader",
    }


async def main():
    """Main command center interface"""
    parser = argparse.ArgumentParser(
        description="Tactical Command Center - Competitive Advantage Orchestration"
    )

    parser.add_argument(
        "command",
        choices=["full-analysis", "seo", "competitive", "quality"],
        help="Tactical analysis command to run",
    )

    parser.add_argument("--metadata", type=str,
                        help="Path to book metadata JSON file")
    parser.add_argument("--output", type=str, help="Output file for results")
    parser.add_argument(
        "--sample", action="store_true", help="Use sample metadata for testing"
    )

    args = parser.parse_args()

    # Initialize command center
    command_center = TacticalCommandCenter()

    # Load metadata
    if args.sample:
        metadata = create_sample_metadata()
        print("📘 Using sample book metadata")
    elif args.metadata:
        metadata = load_book_metadata(args.metadata)
        if not metadata:
            print("❌ Failed to load metadata. Exiting.")
            return
    else:
        print("❌ No metadata provided. Use --metadata or --sample flag.")
        return

    # Generate output filename if not provided
    output_file = args.output
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"tactical_analysis_{args.command}_{timestamp}.json"

    # Execute command
    try:
        if args.command == "full-analysis":
            result = await command_center.run_full_tactical_analysis(
                metadata, output_file
            )
        elif args.command == "seo":
            result = await command_center.run_seo_dominance(metadata, output_file)
        elif args.command == "competitive":
            result = await command_center.run_competitive_intelligence(output_file)
        elif args.command == "quality":
            result = await command_center.run_quality_assessment(metadata, output_file)

        print(f"\n✅ Analysis complete! Results saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🎯 TACTICAL COMMAND CENTER")
    print("Advanced Competitive Advantage Orchestration")
    print("=" * 50)
    asyncio.run(main())
