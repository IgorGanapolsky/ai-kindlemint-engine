#!/usr/bin/env python3
"""
Series Strategy Enforcer
Ensures every series directory has a comprehensive SERIES_STRATEGY_COMPLETE.md file
This is a CRITICAL requirement for all book series production
"""

import json
from datetime import datetime
from pathlib import Path


class SeriesStrategyEnforcer:
    """Enforce series strategy requirements across all series directories"""

    def __init__(self, base_path: Path = None):
        if base_path is None:
            self.base_path = (
                Path(__file__).parent.parent / "books" / "active_production"
            )
        else:
            self.base_path = base_path

        self.required_file = "SERIES_STRATEGY_COMPLETE.md"
        self.violations = []
        self.compliant_series = []

    def scan_all_series(self):
        """Scan all series directories for strategy compliance"""
        print("🔍 Scanning all series directories for strategy compliance...")

        if not self.base_path.exists():
            print(f"❌ Base path not found: {self.base_path}")
            return False

        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                self.check_series_compliance(item)

        return len(self.violations) == 0

    def check_series_compliance(self, series_dir: Path):
        """Check if a single series directory has required strategy file"""
        series_name = series_dir.name
        strategy_file = series_dir / self.required_file

        if strategy_file.exists():
            print(f"✅ {series_name}: Strategy file found")
            self.compliant_series.append(series_name)
        else:
            print(f"❌ {series_name}: Missing {self.required_file}")
            self.violations.append(
                {
                    "series": series_name,
                    "path": str(series_dir),
                    "missing_file": str(strategy_file),
                }
            )

    def generate_violation_report(self):
        """Generate detailed report of compliance violations"""
        if not self.violations:
            print("\n🎉 ALL SERIES ARE COMPLIANT!")
            print(
                f"✅ {len(self.compliant_series)} series have complete strategy files"
            )
            return

        print(f"\n🚨 COMPLIANCE VIOLATIONS FOUND!")
        print(f"❌ {len(self.violations)} series missing strategy files")
        print(f"✅ {len(self.compliant_series)} series compliant")

        print("\n📋 VIOLATIONS DETAIL:")
        for violation in self.violations:
            print(f"  • {violation['series']}")
            print(f"    Path: {violation['path']}")
            print(f"    Missing: {violation['missing_file']}")

        print(f"\n🛠️  REQUIRED ACTION:")
        print(
            f"Create {self.required_file} for each violated series directory")
        print(
            f"Each file must contain comprehensive series strategy as per requirements"
        )

    def auto_generate_template_strategies(self):
        """Generate template strategy files for non-compliant series"""
        if not self.violations:
            print("No violations found - no templates needed")
            return

        print(
            f"\n🔧 Auto-generating strategy templates for {
                len(self.violations)} series..."
        )

        for violation in self.violations:
            series_name = violation["series"]
            series_path = Path(violation["path"])

            template_content = self.generate_strategy_template(series_name)

            strategy_file = series_path / self.required_file
            with open(strategy_file, "w") as f:
                f.write(template_content)

            print(f"✅ Generated strategy template for {series_name}")

    def generate_strategy_template(self, series_name: str) -> str:
        """Generate a comprehensive strategy template for a series"""
        clean_name = series_name.replace("_", " ").title()

        template = f"""# 🎯 {clean_name.upper()} - COMPLETE SERIES STRATEGY

## 📚 SERIES OVERVIEW

**Series Name:** {clean_name}
**Target:** [Define target audience - seniors, professionals, students, etc.]
**Market:** [Define market segment - puzzle enthusiasts, educational, entertainment]
**Unique Positioning:** [Define what makes this series unique and compelling]

---

## 🚀 KDP SERIES SETUP (Copy-Paste Ready)

### Series Configuration (Amazon KDP Series Page)

**Language:** `English`

**Series Title:** `{clean_name}`

**Reading Order:** `✅ Ordered` (Display numbers with titles)

**Series Description:**
```
[WRITE COMPELLING 200-WORD SERIES DESCRIPTION HERE]

Key points to include:
- Target audience and their needs
- Unique value proposition
- Content quality and expertise
- Benefits and outcomes
- Community/brand building
- Call to action

Example structure:
- Hook: Compelling opening statement
- Problem: What challenge does this solve?
- Solution: How this series addresses the challenge
- Proof: Quality, expertise, validation
- Benefits: What readers will gain
- Call to action: Encourage series adoption
```

---

## 📖 VOLUME STRATEGY & THEMES

### Volume 1: [Theme Name]
- **Focus:** [Primary theme and content focus]
- **Puzzles:** [Number and types of puzzles]
- **Target:** [Specific audience segment]
- **Launch Price:** $[X.97]
- **Goal:** [Sales and review targets]

### Volume 2: [Theme Name]
- **Focus:** [Second volume theme]
- **Puzzles:** [Content details]
- **Features:** [Special features or improvements]
- **Target:** [Audience expansion or retention]

### Volume 3-5: [Expansion Strategy]
- **Growth Plan:** [How series will expand]
- **Content Evolution:** [How content will develop]
- **Market Expansion:** [New audiences or formats]

---

## 💰 PRICING & REVENUE STRATEGY

### Pricing Model
**Launch Pricing:** $[X.97] - [Rationale]
**Standard Pricing:** $[X.97] - [Market positioning]
**Premium Pricing:** $[X.97] - [Advanced content]

### Revenue Projections
- **Month 1-3:** $[Amount] (Volume 1 launch)
- **Month 4-9:** $[Amount] (Volumes 2-3)
- **Month 10-15:** $[Amount] (Complete series)
- **Year 2:** $[Amount] annually

### Bundle Strategy
- **2-Volume Bundle:** [Discount %]
- **Complete Series:** [Discount %] + [Bonus content]

---

## 🎯 MARKETING STRATEGY

### Target Audience
**Primary:** [Main demographic - age, interests, needs]
**Secondary:** [Additional segments]
**Niche:** [Specialized segments]

### Marketing Channels
**Digital:**
- Amazon KDP advertising
- Social media marketing ([platforms])
- Content marketing and SEO
- Email marketing campaigns

**Traditional:**
- [Print advertising opportunities]
- [Radio/podcast sponsorships]
- [Event marketing]
- [Partnership opportunities]

### Launch Campaign
**Pre-Launch (Weeks 1-2):**
- [Preparation activities]

**Launch (Weeks 3-4):**
- [Launch activities and promotions]

**Post-Launch (Weeks 5-8):**
- [Optimization and scaling]

---

## 📊 SUCCESS METRICS & KPIs

### Volume-Level Metrics
- **Sales Target:** [Number] copies/month by month 3
- **Review Score:** [Rating]+ stars average
- **Category Ranking:** Top [Number] in [category]
- **Return Rate:** Keep under [Percentage]%

### Series-Level Metrics
- **Cross-Volume Sales:** [Percentage]% buy multiple volumes
- **Customer LTV:** $[Amount] average customer value
- **Market Position:** [Positioning goal]
- **Brand Recognition:** [Awareness targets]

---

## 🔄 PRODUCTION PIPELINE

### Volume Creation Process ([X]-day cycle)
**Days 1-[X]: Content Creation**
- [Content development activities]

**Days [X]-[X]: Design & Layout**
- [Design and formatting activities]

**Days [X]-[X]: Quality Assurance**
- [QA and testing activities]

**Days [X]-[X]: Launch Preparation**
- [Pre-launch activities]

---

## 🎨 BRAND CONSISTENCY GUIDELINES

### Visual Identity
- **Color Scheme:** [Colors and rationale]
- **Typography:** [Font choices and sizing]
- **Layout:** [Spacing and design principles]

### Content Standards
- **Quality:** [Quality requirements]
- **Difficulty:** [Progression standards]
- **Accessibility:** [Accessibility requirements]

---

## 📧 EMAIL MARKETING & COMMUNITY

### Lead Magnets
- **Free Sample:** [Description]
- **Bonus Content:** [Additional offerings]

### Email Sequences
- **Welcome Series:** [Number] emails over [timeframe]
- **Ongoing Campaign:** [Frequency and content]

---

## 🤝 PARTNERSHIP OPPORTUNITIES

### Target Partners
- [Educational institutions]
- [Community organizations]
- [Industry partners]
- [Media partnerships]

---

## 📈 EXPANSION OPPORTUNITIES

### Format Variations
- [Digital formats]
- [Size variations]
- [Interactive versions]

### Content Expansions
- [Theme variations]
- [Difficulty specializations]
- [Educational tie-ins]

---

## 🏆 COMPETITIVE ADVANTAGES

### Unique Positioning
- [Key differentiators]
- [Market advantages]
- [Quality factors]

### Barriers to Entry
- [Competitive moats]
- [Expertise requirements]
- [Brand development]

---

## 🎯 IMMEDIATE ACTION PLAN

### Next 7 Days
1. [Specific action item]
2. [Specific action item]
3. [Specific action item]

### Next 30 Days
1. [30-day goals]
2. [Development milestones]
3. [Market preparation]

### Next 90 Days
1. [Quarter goals]
2. [Series establishment]
3. [Growth metrics]

---

# 🚀 READY TO DOMINATE THE MARKET!

This comprehensive strategy provides the framework for building a successful, profitable series that serves customers and builds sustainable competitive advantage.

**Execute systematically and build your publishing empire!** 📚💰🎯

---

## 📝 COMPLETION CHECKLIST

- [ ] Series overview completed and validated
- [ ] KDP setup information ready for copy-paste
- [ ] Volume themes and progression planned
- [ ] Pricing strategy determined and justified
- [ ] Marketing plan developed with specific tactics
- [ ] Success metrics defined and measurable
- [ ] Production pipeline established
- [ ] Brand guidelines documented
- [ ] Partnership opportunities identified
- [ ] Expansion roadmap planned
- [ ] Competitive advantages articulated
- [ ] Action plan with specific timelines created

**STATUS:** [TEMPLATE - REQUIRES COMPLETION]
**PRIORITY:** [HIGH - COMPLETE BEFORE SERIES LAUNCH]
**OWNER:** [ASSIGN RESPONSIBLE PERSON]
**DUE DATE:** [SET COMPLETION DEADLINE]
"""
        return template

    def validate_strategy_completeness(self, strategy_file: Path) -> bool:
        """Validate that a strategy file is complete and not just a template"""
        if not strategy_file.exists():
            return False

        with open(strategy_file, "r") as f:
            content = f.read()

        # Check for template indicators
        template_indicators = [
            "[WRITE COMPELLING",
            "[Define target audience",
            "[TEMPLATE - REQUIRES COMPLETION]",
            "[X.97]",
            "[Amount]",
        ]

        for indicator in template_indicators:
            if indicator in content:
                return False

        # Check for required sections
        required_sections = [
            "SERIES OVERVIEW",
            "KDP SERIES SETUP",
            "PRICING & REVENUE STRATEGY",
            "MARKETING STRATEGY",
            "SUCCESS METRICS",
        ]

        for section in required_sections:
            if section not in content:
                return False

        return True

    def enforce_compliance(self, auto_generate: bool = True):
        """Main enforcement method - scan and ensure compliance"""
        print("🔒 ENFORCING SERIES STRATEGY COMPLIANCE")
        print("=" * 50)

        # Scan for compliance
        is_compliant = self.scan_all_series()

        # Generate report
        self.generate_violation_report()

        if not is_compliant and auto_generate:
            self.auto_generate_template_strategies()
            print(f"\n✅ Template strategies generated for all non-compliant series")
            print(
                f"⚠️  IMPORTANT: These are templates and MUST be completed before series launch!"
            )

        return is_compliant

    def generate_compliance_summary(self):
        """Generate summary for management reporting"""
        total_series = len(self.compliant_series) + len(self.violations)
        compliance_rate = (
            len(self.compliant_series) / total_series *
            100 if total_series > 0 else 0
        )

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_series": total_series,
            "compliant_series": len(self.compliant_series),
            "violations": len(self.violations),
            "compliance_rate": compliance_rate,
            "compliant_list": self.compliant_series,
            "violation_list": [v["series"] for v in self.violations],
        }

        # Save summary
        summary_file = self.base_path.parent / "series_compliance_report.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n📊 COMPLIANCE SUMMARY:")
        print(f"  Total Series: {total_series}")
        print(f"  Compliant: {len(self.compliant_series)}")
        print(f"  Violations: {len(self.violations)}")
        print(f"  Compliance Rate: {compliance_rate:.1f}%")
        print(f"  Summary saved: {summary_file}")

        return summary


def main():
    """Main execution function"""
    print("🎯 SERIES STRATEGY COMPLIANCE ENFORCER")
    print("=" * 50)
    print("CRITICAL REQUIREMENT: Every series MUST have SERIES_STRATEGY_COMPLETE.md")
    print("=" * 50)

    enforcer = SeriesStrategyEnforcer()

    # Enforce compliance
    is_compliant = enforcer.enforce_compliance(auto_generate=True)

    # Generate summary
    enforcer.generate_compliance_summary()

    if not is_compliant:
        print(f"\n🚨 ACTION REQUIRED:")
        print(
            f"Complete the generated strategy templates before proceeding with series production!"
        )
        exit(1)
    else:
        print(f"\n🎉 ALL SERIES COMPLIANT - READY FOR PRODUCTION!")
        exit(0)


if __name__ == "__main__":
    main()
