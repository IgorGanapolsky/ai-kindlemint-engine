#!/usr/bin/env python3
"""
Dan Kennedy's Magnetic Marketing System for KindleMint Engine
Implements the Magnetic Marketing Triangle: Message → Market → Media
"Stop chasing readers. Make them magnetically attracted to your books."
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


class MagneticMarketingEngine:
    """
    Implements Dan Kennedy's Magnetic Marketing principles
    Transforms books from invisible to irresistible
    """

    def __init__(self, book_config: Dict, book_artifacts: Dict):
        """Initialize magnetic marketing engine"""
        self.book_config = book_config
        self.book_artifacts = book_artifacts
        self.series_name = book_config.get("series_name", "Default_Series")
        self.volume = book_config.get("volume", 1)
        self.title = book_config.get(
            "title", f"{self.series_name} Volume {self.volume}"
        )
        self.author = book_config.get("author", "Publishing Expert")

        # Create magnetic marketing output directory
        self.output_dir = Path(
            f"books/active_production/{self.series_name}/volume_{
                self.volume}/magnetic_marketing"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Kennedy's core principles
        self.kennedy_principles = {
            "message_before_market": True,
            "direct_response_only": True,
            "premium_positioning": True,
            "backend_focus": True,
            "deadline_driven": True,
            "social_proof_heavy": True,
        }

    def create_magnetic_marketing_system(self) -> Dict:
        """
        Create complete magnetic marketing system following Kennedy's methodology
        Returns dictionary of all marketing assets
        """
        print("🧲 Creating Magnetic Marketing System...")

        assets = {}

        # 1. Create hyper-specific avatar (WHO before WHAT)
        assets.update(self._create_avatar_system())

        # 2. Build Magnetic Marketing Triangle (Message → Market → Media)
        assets.update(self._build_magnetic_triangle())

        # 3. Generate direct response titles and descriptions
        assets.update(self._create_direct_response_copy())

        # 4. Build lead magnet funnel system
        assets.update(self._create_lead_magnet_funnel())

        # 5. Implement premium positioning strategy
        assets.update(self._create_premium_positioning())

        # 6. Design shock and awe launch package
        assets.update(self._create_shock_and_awe_package())

        # 7. Build deadline funnel system
        assets.update(self._create_deadline_funnel())

        # 8. Create multi-channel media domination plan
        assets.update(self._create_media_domination_plan())

        # 9. Design backend/continuity systems
        assets.update(self._create_backend_systems())

        # 10. Build social proof and testimonial systems
        assets.update(self._create_social_proof_systems())

        return assets

    def _create_avatar_system(self) -> Dict:
        """Create hyper-specific customer avatar following Kennedy's WHO methodology"""
        print("  👤 Creating hyper-specific customer avatar...")

        # Get book theme and target from config
        book_theme = self.book_config.get("puzzle_type", "crossword")
        self.book_config.get("target_audience", "general")

        # Kennedy-style avatar templates based on book type
        avatar_templates = {
            "crossword": {
                "generic": "People who like word puzzles",
                "magnetic": {
                    "demographics": "Retired professionals aged 62-75 who worked in management or education",
                    "psychographics": "Feel mentally sharp but worry about cognitive decline; want intellectual challenge without frustration",
                    "specific_pain": "Can't find crosswords that are challenging but fair - either too easy (boring) or impossibly hard (frustrating)",
                    "specific_desire": "30 minutes of satisfying mental exercise that makes them feel accomplished and sharp",
                    "objections": "Worried about eye strain, print too small, or clues that are unfairly obscure",
                    "buying_triggers": "Large print, tested difficulty progression, money-back guarantee",
                },
            },
            "sudoku": {
                "generic": "Logic puzzle enthusiasts",
                "magnetic": {
                    "demographics": "Software engineers and accountants aged 28-45 working remote",
                    "psychographics": "High-stress job, seek mental downtime that's still intellectually stimulating",
                    "specific_pain": "Need to decompress after coding/analyzing all day but TV feels like 'wasted time'",
                    "specific_desire": "15-20 minute mental break that feels productive and meditative",
                    "objections": "Don't want puzzles that require guessing or have multiple solutions",
                    "buying_triggers": "Guaranteed unique solutions, progressive difficulty, mobile-friendly format",
                },
            },
            "productivity": {
                "generic": "People wanting to be more productive",
                "magnetic": {
                    "demographics": "Startup founders aged 28-35 who've raised Series A funding",
                    "psychographics": "Working 80+ hour weeks, successful but burning out, marriage/relationships suffering",
                    "specific_pain": "Can't scale past 14-hour days without losing control of the business",
                    "specific_desire": "Work 40 hours a week while growing revenue 50% year-over-year",
                    "objections": "Tried productivity methods before, skeptical of 'guru' advice from people who haven't built real businesses",
                    "buying_triggers": "Specific revenue/time metrics, case studies from similar companies, 90-day guarantee",
                },
            },
        }

        # Select appropriate template
        template_key = book_theme if book_theme in avatar_templates else "crossword"
        avatar_data = avatar_templates[template_key]["magnetic"]

        # Create detailed avatar profile
        avatar_profile = {
            "avatar_name": f"The Ideal {self.title.split()[0]} Reader",
            "kennedy_methodology": "WHO before WHAT - hyper-specific targeting",
            "demographics": avatar_data["demographics"],
            "psychographics": avatar_data["psychographics"],
            "specific_pain_points": [
                avatar_data["specific_pain"],
                "Overwhelmed by generic options in the market",
                "Frustrated by previous disappointing purchases",
                "Time-conscious and value-focused",
            ],
            "specific_desires": [
                avatar_data["specific_desire"],
                "Feel confident in purchase decision",
                "Get immediate value and satisfaction",
                "Recommend to friends with pride",
            ],
            "objections_and_concerns": [
                avatar_data["objections"],
                "Skeptical of bold claims",
                "Worried about wasting money",
                "Concerned about time investment",
            ],
            "buying_triggers": [
                avatar_data["buying_triggers"],
                "Strong guarantee",
                "Social proof from similar people",
                "Urgency/scarcity elements",
            ],
            "media_consumption": self._get_media_channels(template_key),
            "message_resonance": self._get_message_hooks(template_key),
        }

        # Create marketing message matrix
        message_matrix = {
            "pain_agitation": [
                f"Are you tired of {avatar_data['specific_pain'].lower()}?",
                f"Sick of books that promise everything but deliver nothing?",
                f"Fed up with generic solutions that don't understand your specific situation?",
            ],
            "solution_promise": [
                f"Finally, a {book_theme} book designed specifically for {
                    avatar_data['demographics'].lower()}",
                f"The exact system that helps {
                    avatar_data['demographics'].lower()} {
                    avatar_data['specific_desire'].lower()}",
                f"Proven method used by hundreds of people just like you",
            ],
            "proof_elements": [
                "Real case studies from actual readers",
                "30-day money-back guarantee",
                f"Specifically tested with {avatar_data['demographics'].lower()}",
            ],
        }

        # Save avatar system
        avatar_file = self.output_dir / "customer_avatar.json"
        avatar_system = {
            "avatar_profile": avatar_profile,
            "message_matrix": message_matrix,
            "kennedy_principle": "Know exactly WHO you want your customers to be BEFORE creating WHAT you're selling",
            "implementation_notes": [
                "Use avatar language in all copy",
                "Target avatar's specific media channels",
                "Address avatar's exact objections",
                "Speak to avatar's precise desires",
            ],
        }

        with open(avatar_file, "w") as f:
            json.dump(avatar_system, f, indent=2)

        return {"customer_avatar": str(avatar_file)}

    def _get_media_channels(self, template_key: str) -> List[str]:
        """Get media channels for specific avatar types"""
        media_channels = {
            "crossword": [
                "AARP Magazine",
                "Local newspaper puzzle sections",
                "Library book clubs",
                "Senior center newsletters",
                "Facebook groups for retirees",
                "PBS programming guides",
            ],
            "sudoku": [
                "Hacker News",
                "Reddit r/programming",
                "LinkedIn",
                "Tech Twitter",
                "Developer newsletters",
                "Remote work blogs",
                "Productivity podcasts",
            ],
            "productivity": [
                "TechCrunch",
                "Y Combinator forums",
                "Founder Slack communities",
                "Startup podcasts",
                "AngelList",
                "First Round Review",
                "SaaStr events",
            ],
        }
        return media_channels.get(template_key, media_channels["crossword"])

    def _get_message_hooks(self, template_key: str) -> List[str]:
        """Get message hooks that resonate with specific avatars"""
        message_hooks = {
            "crossword": [
                "Keep your mind sharp",
                "Proven by retirement experts",
                "Doctor recommended",
                "Large print comfort",
                "No frustration guarantee",
                "Community tested",
            ],
            "sudoku": [
                "Scientifically designed",
                "Developer approved",
                "Logic-based approach",
                "Stress-relief verified",
                "Remote worker tested",
                "Productivity enhanced",
            ],
            "productivity": [
                "Founder proven",
                "Revenue per hour",
                "Scale without burnout",
                "VC recommended",
                "Unicorn methods",
                "Work-life integration",
            ],
        }
        return message_hooks.get(template_key, message_hooks["crossword"])

    def _build_magnetic_triangle(self) -> Dict:
        """Build Kennedy's Magnetic Marketing Triangle: Message → Market → Media"""
        print("  🔺 Building Magnetic Marketing Triangle...")

        # Load avatar data
        avatar_file = self.output_dir / "customer_avatar.json"
        if avatar_file.exists():
            with open(avatar_file, "r") as f:
                avatar_data = json.load(f)
        else:
            avatar_data = {"avatar_profile": {"demographics": "puzzle enthusiasts"}}

        # Create the triangle
        magnetic_triangle = {
            "kennedy_principle": "Message → Market → Media (in that exact order)",
            "message": {
                "core_promise": f"The ONLY {self.book_config.get('puzzle_type', 'puzzle')} book designed specifically for {avatar_data['avatar_profile'].get('demographics', 'your specific situation')}",
                "unique_mechanism": f"The {self.series_name} Method™",
                "proof_points": [
                    f"Tested with 100+ {
                        avatar_data['avatar_profile'].get(
                            'demographics', 'readers')}",
                    f"Guaranteed results in 30 days or money back",
                    f"Only book that addresses {avatar_data['avatar_profile'].get('specific_pain_points', ['common frustrations'])[
                        0] if avatar_data['avatar_profile'].get('specific_pain_points') else 'your specific needs'}",
                ],
                "irresistible_offer": f"{self.title} + Bonus Materials + 30-Day Guarantee + Limited-Time Pricing",
            },
            "market": {
                "primary_avatar": avatar_data["avatar_profile"].get(
                    "demographics", "target audience"
                ),
                "market_size": "Estimated 50,000+ perfect prospects",
                "market_channels": avatar_data["avatar_profile"].get(
                    "media_consumption", ["online", "retail"]
                ),
                "market_temperature": {
                    "hot": "Previous customers and email subscribers",
                    "warm": "People who've engaged with related content",
                    "cold": "Target avatar who hasn't heard of you yet",
                },
            },
            "media": {
                "primary_channels": avatar_data["avatar_profile"].get(
                    "media_consumption", ["general"]
                ),
                "message_matching": "Each channel gets avatar-specific messaging",
                "media_budget_allocation": {
                    "direct_response_ads": "40%",
                    "email_marketing": "30%",
                    "content_marketing": "20%",
                    "partnerships": "10%",
                },
            },
        }

        # Create implementation roadmap
        implementation_roadmap = {
            "week_1_message": [
                "Finalize core promise and unique mechanism",
                "Create irresistible offer structure",
                "Write and test all copy variations",
            ],
            "week_2_market": [
                "Validate avatar assumptions with surveys",
                "Map customer journey from awareness to purchase",
                "Identify market segments and prioritize",
            ],
            "week_3_media": [
                "Launch paid campaigns to primary channels",
                "Begin content marketing in target communities",
                "Activate email sequences for different temperatures",
            ],
            "week_4_optimize": [
                "Analyze conversion rates by channel",
                "Double down on highest-performing media",
                "Refine message based on market feedback",
            ],
        }

        # Save triangle system
        triangle_file = self.output_dir / "magnetic_triangle.json"
        triangle_data = {
            "magnetic_triangle": magnetic_triangle,
            "implementation_roadmap": implementation_roadmap,
            "kennedy_quote": "The foundation of any marketing is knowing exactly who you want your customers to be",
        }

        with open(triangle_file, "w") as f:
            json.dump(triangle_data, f, indent=2)

        return {"magnetic_triangle": str(triangle_file)}

    def _create_direct_response_copy(self) -> Dict:
        """Generate direct response titles and descriptions using Kennedy's formulas"""
        print("  📝 Creating direct response copy...")

        # Kennedy's direct response title formulas
        title_formulas = [
            "How I [ACHIEVED RESULT] in [TIME PERIOD] [WITHOUT COMMON METHOD]",
            "The [NUMBER] [THING] That [BENEFIT] (Even If [OBJECTION])",
            "[TARGET PERSON]'s Guide to [SPECIFIC OUTCOME] Without [PAIN/SACRIFICE]",
            "Why [COMMON BELIEF] is Wrong and What [TARGET] Should Do Instead",
            "The [SECRET/SIMPLE] [SYSTEM/METHOD] [AUTHORITY FIGURE] Uses to [BENEFIT]",
        ]

        # Generate magnetic titles based on book theme
        book_theme = self.book_config.get("puzzle_type", "crossword")
        magnetic_titles = []

        if book_theme == "crossword":
            magnetic_titles = [
                "How I Solved My Daily Crossword in 15 Minutes Without Cheating (And You Can Too)",
                "The 7 Crossword Secrets That Senior Centers Don't Want You to Know",
                "Retired Teacher's Guide to Staying Mentally Sharp Without Boring Puzzles",
                "Why 'Brain Training' Apps Are Wrong and What Crossword Lovers Should Do Instead",
                "The Simple System Retirement Homes Use to Keep Residents' Minds Razor-Sharp",
            ]
        elif book_theme == "sudoku":
            magnetic_titles = [
                "How I Solved Expert Sudoku in 10 Minutes Without Guessing",
                "The 5 Logic Patterns That Transform Any Sudoku From Impossible to Easy",
                "Software Engineer's Guide to Stress Relief Without Wasting Time",
                "Why Random Sudoku Apps Are Wrong and What Developers Should Do Instead",
                "The Secret Method Japanese Masters Use to Solve Any Sudoku Instantly",
            ]

        # Kennedy's sales letter formula for descriptions
        sales_letter_template = """
{PAIN_AGITATION}

{BOLD_PROMISE}

Here's what you'll discover inside:

{BENEFIT_BULLETS}

{GUARANTEE}

{URGENCY_BONUS}

{CALL_TO_ACTION}
"""

        # Generate magnetic book descriptions
        descriptions = []
        for title in magnetic_titles[:3]:  # Use top 3 titles
            if book_theme == "crossword":
                description = self._generate_crossword_description(title)
            elif book_theme == "sudoku":
                description = self._generate_sudoku_description(title)
            else:
                description = self._generate_generic_description(title)

            descriptions.append(
                {
                    "title": title,
                    "description": description,
                    "kennedy_elements": [
                        "Pain agitation (first 3 sentences)",
                        "Bold promise (specific claim)",
                        "Benefit bullets (proof)",
                        "Risk reversal (guarantee)",
                        "Urgency element (bonus)",
                    ],
                }
            )

        # Create A/B testing framework
        ab_testing_framework = {
            "title_variations": magnetic_titles,
            "description_variations": descriptions,
            "testing_methodology": [
                "Test 2 titles simultaneously",
                "Measure click-through rates",
                "Track conversion to sales",
                "Winner becomes permanent",
            ],
            "kennedy_principle": "Test everything, assume nothing",
        }

        # Save copy system
        copy_file = self.output_dir / "direct_response_copy.json"
        copy_data = {
            "magnetic_titles": magnetic_titles,
            "magnetic_descriptions": descriptions,
            "ab_testing_framework": ab_testing_framework,
            "kennedy_formulas": title_formulas,
            "implementation_notes": [
                "Use specific numbers and timeframes",
                "Address target avatar directly",
                "Include social proof elements",
                "Always end with clear call-to-action",
            ],
        }

        with open(copy_file, "w") as f:
            json.dump(copy_data, f, indent=2)

        return {"direct_response_copy": str(copy_file)}

    def _generate_crossword_description(self, title: str) -> str:
        """Generate Kennedy-style sales letter for crossword book"""
        # Extract the main benefit from title safely
        benefit = "solved crosswords 50% faster"
        if "How I" in title and "(And You Can Too)" in title:
            try:
                benefit = title.split("How I")[1].split("(And You Can Too)")[0].strip()
            except IndexError:
                benefit = "mastered the crossword solving system"
        elif "How I" in title:
            try:
                benefit = title.split("How I")[1].strip()
            except IndexError:
                benefit = "discovered the secret to crossword mastery"

        return f"""Are you tired of crossword puzzles that are either insultingly easy or impossibly hard? Sick of straining your eyes over tiny print just to enjoy your daily mental exercise?

I {benefit} - and now you can use the exact same method.

Here's what you'll discover inside:

• The "Corner Start" technique that unlocks 70% of any grid in under 5 minutes (Page 12)
• Why starting with long answers is the #1 mistake most solvers make (Chapter 2)
• The 3-clue pattern that appears in 95% of professional crosswords (you'll never get stuck again)
• Large print format designed specifically for comfortable solving - no eye strain guaranteed

GUARANTEE: Solve puzzles 50% faster in 30 days or return this book for a full refund PLUS keep the bonus solving guide ($19 value).

BONUS: Order today and get "The Crossword Solver's Cheat Sheet" - 200+ common crossword answers that appear in 80% of all puzzles.

Click "Buy Now" to start solving crosswords like a pro - your brain (and your eyes) will thank you."""

    def _generate_sudoku_description(self, title: str) -> str:
        """Generate Kennedy-style sales letter for sudoku book"""
        # Extract the main benefit from title safely
        benefit = "mastered expert sudoku solving"
        if "How I" in title:
            try:
                benefit = title.split("How I")[1].strip()
            except IndexError:
                benefit = "solved sudoku puzzles systematically"

        return f"""Are you stuck guessing your way through sudoku puzzles? Frustrated by apps that claim to have "unique solutions" but still leave you confused?

I {benefit} - and I'll show you exactly how.

Here's what you'll discover inside:

• The "Naked Singles" technique that solves 40% of any puzzle automatically (Page 8)
• Why most sudoku books teach backwards logic (and the Japanese method that actually works)
• The 5 advanced patterns that turn "impossible" puzzles into 10-minute victories
• Scientific progression from easy to expert - no frustrating difficulty jumps

GUARANTEE: Master expert-level sudoku in 30 days or return this book for double your money back.

BONUS: Order in the next 24 hours and get my "Logic Pattern Quick Reference Card" ($15 value) that fits in your wallet for solving on-the-go.

Click "Add to Cart" now - your logical mind deserves puzzles that make sense."""

    def _generate_generic_description(self, title: str) -> str:
        """Generate Kennedy-style sales letter for generic book"""
        return f"""Are you tired of books that promise everything but deliver nothing? Frustrated by generic advice that doesn't apply to your specific situation?

This book reveals the exact system behind {title.lower()}.

Here's what you'll discover inside:

• The one technique that changes everything (Chapter 1)
• Why conventional wisdom is wrong (and what works instead)
• Real case studies from people just like you
• Step-by-step implementation guide

GUARANTEE: See results in 30 days or full refund.

BONUS: Limited-time bonus materials worth $47.

Order now and transform your results."""

    def _create_lead_magnet_funnel(self) -> Dict:
        """Create Kennedy's lead generation magnet system"""
        print("  🧲 Creating lead magnet funnel...")

        # Kennedy's funnel structure: Free → Tripwire → Core → Backend
        book_theme = self.book_config.get("puzzle_type", "crossword")

        funnel_templates = {
            "crossword": {
                "lead_magnet": {
                    "title": "7 Retirement Home Directors Share Their Residents' Favorite Brain-Boosting Crossword Secrets",
                    "format": "Free PDF Report",
                    "value_perception": "$19 value",
                    "delivery": "Instant download + email course",
                },
                "tripwire": {
                    "title": "The 15-Minute Crossword: Quick Puzzles for Busy Retirees",
                    "price": "$0.99",
                    "format": "Mini puzzle book (25 puzzles)",
                    "value_perception": "$9.99 value",
                },
                "core_offer": {
                    "title": self.title,
                    "price": "$6.99",
                    "format": "Complete puzzle book",
                    "value_perception": "$19.99 value",
                },
                "backend": {
                    "title": "The Golden Years Brain Club",
                    "price": "$19.97/month",
                    "format": "Monthly puzzle subscription + community",
                    "value_perception": "$97/month value",
                },
            },
            "sudoku": {
                "lead_magnet": {
                    "title": "5 Silicon Valley Engineers Share Their Stress-Relief Sudoku Systems",
                    "format": "Free video training",
                    "value_perception": "$47 value",
                    "delivery": "Email series + bonus worksheets",
                },
                "tripwire": {
                    "title": "Coffee Break Sudoku: 15 Logic Puzzles for Busy Developers",
                    "price": "$1.99",
                    "format": "Digital puzzle pack",
                    "value_perception": "$12.99 value",
                },
                "core_offer": {
                    "title": self.title,
                    "price": "$7.99",
                    "format": "Complete sudoku system",
                    "value_perception": "$24.99 value",
                },
                "backend": {
                    "title": "Logic Masters Academy",
                    "price": "$29.97/month",
                    "format": "Advanced puzzle training + live sessions",
                    "value_perception": "$197/month value",
                },
            },
        }

        # Select appropriate funnel
        funnel_data = funnel_templates.get(book_theme, funnel_templates["crossword"])

        # Create complete funnel system
        funnel_system = {
            "kennedy_principle": "Attract → Convert → Retain → Refer",
            "funnel_stages": {
                "attract": {
                    "offer": funnel_data["lead_magnet"],
                    "goal": "Build email list with qualified prospects",
                    "conversion_target": "25% of visitors",
                    "traffic_sources": [
                        "Facebook ads",
                        "Content marketing",
                        "Partnerships",
                    ],
                },
                "convert": {
                    "tripwire": funnel_data["tripwire"],
                    "goal": "Turn leads into buyers",
                    "conversion_target": "8-12% of leads",
                    "psychology": "Micro-commitment, overcome skepticism",
                },
                "retain": {
                    "core_offer": funnel_data["core_offer"],
                    "goal": "Deliver main value and profit",
                    "conversion_target": "25-35% of tripwire buyers",
                    "fulfillment": "Immediate digital delivery",
                },
                "refer": {
                    "backend": funnel_data["backend"],
                    "goal": "Maximize lifetime value",
                    "conversion_target": "10-15% of core buyers",
                    "retention": "Monthly recurring revenue",
                },
            },
        }

        # Create email sequences for each stage
        email_sequences = {
            "lead_magnet_sequence": [
                {
                    "day": 0,
                    "subject": f"Your free report: {funnel_data['lead_magnet']['title']}",
                    "purpose": "Deliver lead magnet + introduce tripwire",
                },
                {
                    "day": 1,
                    "subject": "The #1 mistake I see people make...",
                    "purpose": "Build authority + soft pitch tripwire",
                },
                {
                    "day": 3,
                    "subject": "Special offer expires at midnight",
                    "purpose": "Hard pitch tripwire with urgency",
                },
            ],
            "tripwire_sequence": [
                {
                    "day": 0,
                    "subject": "Your order is confirmed + special bonus inside",
                    "purpose": "Deliver tripwire + introduce core offer",
                },
                {
                    "day": 2,
                    "subject": "How to get 10x more value...",
                    "purpose": "Soft pitch core offer",
                },
                {
                    "day": 7,
                    "subject": "Last chance for the complete system",
                    "purpose": "Hard pitch core offer",
                },
            ],
            "core_buyer_sequence": [
                {
                    "day": 0,
                    "subject": "Welcome to the inner circle",
                    "purpose": "Deliver core product + backend preview",
                },
                {
                    "day": 14,
                    "subject": "Ready for the next level?",
                    "purpose": "Introduce backend membership",
                },
                {
                    "day": 21,
                    "subject": "Founding member pricing ends soon",
                    "purpose": "Backend membership with urgency",
                },
            ],
        }

        # Create conversion optimization strategies
        optimization_strategies = {
            "headline_testing": [
                "Test benefit-focused vs. curiosity-driven headlines",
                "Test specific numbers vs. general claims",
                "Test different target avatars",
            ],
            "price_testing": [
                "Test $0.99 vs. $1.99 vs. $2.99 for tripwire",
                "Test $6.99 vs. $9.99 vs. $12.99 for core",
                "Test monthly vs. quarterly vs. annual backend pricing",
            ],
            "bonus_testing": [
                "Test digital vs. physical bonuses",
                "Test single bonus vs. bonus stack",
                "Test limited-time vs. always-available bonuses",
            ],
        }

        # Save funnel system
        funnel_file = self.output_dir / "lead_magnet_funnel.json"
        complete_funnel = {
            "funnel_system": funnel_system,
            "email_sequences": email_sequences,
            "optimization_strategies": optimization_strategies,
            "revenue_projections": {
                "monthly_traffic": 1000,
                "lead_conversion": "25%",
                "tripwire_conversion": "10%",
                "core_conversion": "30%",
                "backend_conversion": "12%",
                "projected_monthly_revenue": "$1,247",
            },
        }

        with open(funnel_file, "w") as f:
            json.dump(complete_funnel, f, indent=2)

        return {"lead_magnet_funnel": str(funnel_file)}

    def _create_premium_positioning(self) -> Dict:
        """Create premium positioning strategy following Kennedy's 'Pay, Stay, Refer' model"""
        print("  💎 Creating premium positioning strategy...")

        # Kennedy's positioning principles
        positioning_strategy = {
            "kennedy_principle": "Never compete on price - compete on value and unique positioning",
            "premium_elements": {
                "positioning_statement": f"The ONLY {self.book_config.get('puzzle_type', 'puzzle')} book designed by [AUTHORITY] for [SPECIFIC AVATAR]",
                "unique_mechanism": f"The {self.series_name} Method™",
                "authority_building": [
                    f"Creator of the {self.series_name} system",
                    f"Trusted by [NUMBER] satisfied readers",
                    f"Featured expert in [PUBLICATION]",
                ],
                "scarcity_elements": [
                    "Limited edition printing",
                    "Exclusive bonus materials",
                    "First-time-ever pricing",
                ],
            },
        }

        # Pricing strategy
        pricing_strategy = {
            "never_lowest_price": "Always price 20-30% above similar books",
            "price_anchoring": {
                "anchor_price": "$24.99",
                "your_price": "$6.99",
                "savings_emphasized": "Save $18 - but only for limited time",
            },
            "value_stacking": {
                "core_book": "$24.99 value",
                "bonus_materials": "$47 value",
                "guarantee": "$97 value (peace of mind)",
                "total_value": "$168.98",
                "your_investment": "Just $6.99",
            },
            "backend_monetization": {
                "book_profit": "$3.50 per sale",
                "email_value": "$15 lifetime value",
                "backend_value": "$197 average",
                "total_customer_value": "$215.50",
            },
        }

        # Pay, Stay, Refer system
        pay_stay_refer = {
            "PAY": {
                "strategy": "Premium pricing with overwhelming value",
                "tactics": [
                    "Price 30% above competition",
                    "Massive bonus stack",
                    "Risk-free guarantee",
                    "Payment plan options for backend",
                ],
                "psychology": "Higher price = higher perceived value",
            },
            "STAY": {
                "strategy": "Continuity and recurring revenue",
                "tactics": [
                    "Monthly membership program",
                    "Email newsletter with exclusive content",
                    "Private Facebook group",
                    "Monthly Q&A sessions",
                ],
                "programs": {
                    "basic_continuity": "$19.97/month",
                    "vip_continuity": "$49.97/month",
                    "done_with_you": "$197/month",
                },
            },
            "REFER": {
                "strategy": "Turn customers into sales force",
                "tactics": [
                    "Affiliate program (30% commission)",
                    "Referral bonuses for customers",
                    "Gift programs for friends",
                    "Testimonial incentives",
                ],
                "programs": {
                    "affiliate_commission": "30% of all sales",
                    "customer_referral": "$5 credit per referral",
                    "gift_program": "Buy 2, gift 1 free",
                },
            },
        }

        # Authority building system
        authority_system = {
            "credibility_markers": [
                f"Author of {self.title}",
                f"Creator of the {self.series_name} Method™",
                f"Trusted by [NUMBER] customers",
                "Featured in [PUBLICATIONS]",
            ],
            "social_proof_elements": [
                "Customer testimonials with photos",
                "Media mentions and features",
                "Expert endorsements",
                "Sales numbers and rankings",
            ],
            "positioning_copy": f"""
Unlike other {self.book_config.get('puzzle_type', 'puzzle')} books created by nameless publishing houses,
{self.title} was personally designed by {self.author} using the revolutionary {self.series_name} Method™.

This isn't another generic puzzle book. This is a carefully crafted system that has already helped
[NUMBER] people [SPECIFIC RESULT]. When you invest in {self.title}, you're not just buying a book -
you're getting access to a proven methodology that [SPECIFIC OUTCOME].

That's why we can offer our unconditional 30-day guarantee. We're so confident in the {self.series_name} Method™
that if you don't see [SPECIFIC RESULT] in 30 days, we'll refund every penny and let you keep the book.
""",
        }

        # Save positioning strategy
        positioning_file = self.output_dir / "premium_positioning.json"
        positioning_data = {
            "positioning_strategy": positioning_strategy,
            "pricing_strategy": pricing_strategy,
            "pay_stay_refer_system": pay_stay_refer,
            "authority_system": authority_system,
            "implementation_checklist": [
                "Never mention or acknowledge competition",
                "Always lead with value, not price",
                "Create category of one positioning",
                "Build authority before selling",
                "Design for backend monetization",
            ],
        }

        with open(positioning_file, "w") as f:
            json.dump(positioning_data, f, indent=2)

        return {"premium_positioning": str(positioning_file)}

    def _create_shock_and_awe_package(self) -> Dict:
        """Create Kennedy's 'Shock and Awe' overwhelming value package"""
        print("  💥 Creating shock and awe package...")

        # Kennedy principle: Overwhelm with value upfront
        book_theme = self.book_config.get("puzzle_type", "crossword")

        shock_and_awe_templates = {
            "crossword": {
                "core_product": {
                    "item": self.title,
                    "value": "$24.99",
                    "description": "50 large-print crosswords with progressive difficulty",
                },
                "bonus_stack": [
                    {
                        "item": "The Crossword Master's Cheat Sheet",
                        "value": "$19.99",
                        "description": "200+ common answers that appear in 80% of all puzzles",
                    },
                    {
                        "item": "Large Print Solving Guide",
                        "value": "$14.99",
                        "description": "Step-by-step techniques for faster solving",
                    },
                    {
                        "item": "Printable Practice Grids",
                        "value": "$9.99",
                        "description": "Blank grids for creating your own puzzles",
                    },
                    {
                        "item": "60-Day Email Coaching Series",
                        "value": "$47.00",
                        "description": "Daily tips and encouragement delivered to inbox",
                    },
                    {
                        "item": "Private Facebook Group Access",
                        "value": "$27.00",
                        "description": "Connect with other crossword enthusiasts",
                    },
                ],
            },
            "sudoku": {
                "core_product": {
                    "item": self.title,
                    "value": "$27.99",
                    "description": "Complete sudoku mastery system with 100+ puzzles",
                },
                "bonus_stack": [
                    {
                        "item": "The Logic Pattern Quick Reference",
                        "value": "$17.99",
                        "description": "Laminated card with all 5 advanced techniques",
                    },
                    {
                        "item": "Sudoku Timer & Tracker App",
                        "value": "$12.99",
                        "description": "Track your progress and beating times",
                    },
                    {
                        "item": "Video Training Series",
                        "value": "$97.00",
                        "description": "Watch over-the-shoulder solving demonstrations",
                    },
                    {
                        "item": "Monthly New Puzzle Pack",
                        "value": "$19.99",
                        "description": "Fresh puzzles delivered monthly for 3 months",
                    },
                ],
            },
        }

        # Select appropriate template
        template = shock_and_awe_templates.get(
            book_theme, shock_and_awe_templates["crossword"]
        )

        # Calculate total value
        core_value = float(template["core_product"]["value"].replace("$", ""))
        bonus_value = sum(
            float(bonus["value"].replace("$", "")) for bonus in template["bonus_stack"]
        )
        total_value = core_value + bonus_value

        # Create the package
        shock_and_awe_package = {
            "kennedy_principle": "Overwhelm with value to eliminate price resistance",
            "core_product": template["core_product"],
            "bonus_stack": template["bonus_stack"],
            "value_calculation": {
                "core_value": f"${core_value:.2f}",
                "bonus_value": f"${bonus_value:.2f}",
                "total_value": f"${total_value:.2f}",
                "your_investment": "$6.99",
                "savings": f"${total_value - 6.99:.2f}",
                "value_multiplier": f"{total_value / 6.99:.1f}x",
            },
        }

        # Create presentation copy
        presentation_copy = f"""
🎁 COMPLETE {self.title.upper()} PACKAGE

When you order {self.title} today, you don't just get the book...

✅ {template['core_product']['item']} ({template['core_product']['value']} value)
{template['core_product']['description']}

PLUS these exclusive bonuses:

"""

        for bonus in template["bonus_stack"]:
            presentation_copy += f"✅ {bonus['item']
                                      } ({bonus['value']} value)\n{bonus['description']}\n\n"

        presentation_copy += f"""
TOTAL VALUE: ${total_value:.2f}
YOUR INVESTMENT TODAY: Just $6.99

That's a savings of ${total_value - 6.99:.2f} - but only if you order now!

This complete package normally sells for ${total_value:.2f}, but for a limited time,
you can get everything for just $6.99.

Why such a crazy deal? Because I know that once you experience the power of the
{self.series_name} Method™, you'll become a customer for life.

Click "Add to Cart" now to claim your complete package...
"""

        # Create delivery sequence
        delivery_sequence = {
            "immediate": [
                "Core book download",
                "Bonus materials download",
                "Welcome email with access instructions",
            ],
            "day_1": [
                "Email coaching series begins",
                "Facebook group invitation",
                "Getting started guide",
            ],
            "day_7": [
                "Check-in email with tips",
                "Success stories from other users",
                "Additional resources",
            ],
            "day_30": [
                "Advanced techniques training",
                "Invitation to VIP program",
                "Satisfaction survey",
            ],
        }

        # Save shock and awe package
        package_file = self.output_dir / "shock_and_awe_package.json"
        package_data = {
            "shock_and_awe_package": shock_and_awe_package,
            "presentation_copy": presentation_copy,
            "delivery_sequence": delivery_sequence,
            "psychology_notes": [
                "High perceived value reduces price sensitivity",
                "Multiple bonuses create multiple reasons to buy",
                "Immediate gratification with downloads",
                "Future value with ongoing elements",
            ],
        }

        with open(package_file, "w") as f:
            json.dump(package_data, f, indent=2)

        return {"shock_and_awe_package": str(package_file)}

    def _create_deadline_funnel(self) -> Dict:
        """Create Kennedy's deadline-driven urgency system"""
        print("  ⏰ Creating deadline funnel system...")

        # Kennedy principle: Everything must have a deadline
        deadline_system = {
            "kennedy_principle": "Everything expires. No exceptions. Urgency drives action.",
            "urgency_types": {
                "quantity_scarcity": "Only 500 copies available",
                "time_scarcity": "Offer expires in 72 hours",
                "bonus_scarcity": "Bonuses disappear at midnight",
                "price_scarcity": "Price increases after launch week",
            },
        }

        # Create 7-day launch sequence
        launch_sequence = {
            "day_1": {
                "theme": "Launch Announcement",
                "price": "$0.99",
                "urgency": "24-hour introductory pricing",
                "messaging": "Brand new book launches at 89% off - today only",
                "social_proof": "Join the first 100 readers",
            },
            "day_2": {
                "theme": "Early Bird Special",
                "price": "$2.99",
                "urgency": "Early bird pricing ends tomorrow",
                "messaging": "Price goes up tomorrow - last chance for early bird discount",
                "social_proof": "247 copies sold in first 24 hours",
            },
            "day_3": {
                "theme": "Regular Launch Price",
                "price": "$4.99",
                "urgency": "Bonuses expire in 4 days",
                "messaging": "Regular price now in effect, but bonuses still included",
                "social_proof": "Over 500 readers already transforming their results",
            },
            "day_4_5": {
                "theme": "Bonus Warning",
                "price": "$4.99",
                "urgency": "Bonuses disappear in 48 hours",
                "messaging": "Final warning: $143 in bonuses expire soon",
                "social_proof": "Join 750+ satisfied readers",
            },
            "day_6": {
                "theme": "Final Day for Bonuses",
                "price": "$4.99",
                "urgency": "Bonuses expire at midnight tonight",
                "messaging": "This is it - bonuses disappear forever at midnight",
                "social_proof": "Don't be the one who waited too long",
            },
            "day_7": {
                "theme": "Final Price Increase",
                "price": "$6.99",
                "urgency": "Final price - no more increases",
                "messaging": "Price increase now in effect - this is the final price",
                "social_proof": "1,000+ readers can't be wrong",
            },
        }

        # Create evergreen deadline funnel
        evergreen_funnel = {
            "trigger": "Email signup or first visit",
            "sequence": [
                {
                    "hours": 0,
                    "message": "Welcome! Special 24-hour pricing just for you",
                    "discount": "50% off",
                    "urgency": "This special pricing expires in 24 hours",
                },
                {
                    "hours": 20,
                    "message": "4 hours left for your special pricing",
                    "discount": "50% off",
                    "urgency": "Price returns to normal at midnight",
                },
                {
                    "hours": 24,
                    "message": "Special pricing expired - regular price now",
                    "discount": "0%",
                    "urgency": "Join thousands of satisfied readers",
                },
                {
                    "hours": 72,
                    "message": "Final chance - 3-day email exclusive",
                    "discount": "25% off",
                    "urgency": "This offer expires in 24 hours and won't repeat",
                },
            ],
        }

        # Create urgency copy templates
        urgency_templates = {
            "email_subject_lines": [
                "URGENT: Offer expires at midnight",
                "Final hours: Don't miss out",
                "Price increase in 3... 2... 1...",
                "Last call for bonuses",
                "This disappears forever in [TIME]",
            ],
            "countdown_copy": [
                "Only [TIME] remaining at this price",
                "Offer expires in [COUNTDOWN]",
                "Join [NUMBER] others before it's too late",
                "Price increases permanently in [TIME]",
                "Don't be the one who waited too long",
            ],
            "scarcity_elements": [
                "Only [NUMBER] copies remaining",
                "Limited to first [NUMBER] customers",
                "Exclusive bonus for next [NUMBER] buyers",
                "Just [NUMBER] spots left in program",
            ],
        }

        # Create deadline psychology
        deadline_psychology = {
            "loss_aversion": "People fear losing more than they enjoy gaining",
            "social_proof": "Others are buying - don't be left out",
            "authority": "Expert recommends acting now",
            "commitment": "Price increase forces decision",
            "reciprocity": "Special deal creates obligation",
        }

        # Save deadline funnel
        deadline_file = self.output_dir / "deadline_funnel.json"
        deadline_data = {
            "deadline_system": deadline_system,
            "launch_sequence": launch_sequence,
            "evergreen_funnel": evergreen_funnel,
            "urgency_templates": urgency_templates,
            "deadline_psychology": deadline_psychology,
            "implementation_rules": [
                "Every offer must have a real deadline",
                "Never extend deadlines publicly",
                "Always follow through on expiration",
                "Create new urgency for non-buyers",
                "Track urgency vs. conversion rates",
            ],
        }

        with open(deadline_file, "w") as f:
            json.dump(deadline_data, f, indent=2)

        return {"deadline_funnel": str(deadline_file)}

    def _create_media_domination_plan(self) -> Dict:
        """Create multi-channel media domination following Kennedy's methodology"""
        print("  📺 Creating media domination plan...")

        # Load avatar data for media targeting
        avatar_file = self.output_dir / "customer_avatar.json"
        if avatar_file.exists():
            with open(avatar_file, "r") as f:
                avatar_data = json.load(f)
            media_channels = avatar_data["avatar_profile"].get(
                "media_consumption", ["general"]
            )
        else:
            media_channels = ["Facebook", "Email", "Content Marketing"]

        # Kennedy's multi-channel approach
        media_domination = {
            "kennedy_principle": "Be everywhere your customer is, with the right message for each medium",
            "omni_presence_strategy": "Dominate 3-5 channels completely rather than dabbling in many",
            "message_matching": "Each channel gets avatar-specific messaging",
        }

        # Channel-specific strategies
        channel_strategies = {}

        # Primary channels based on avatar
        primary_channels = media_channels[:5]  # Focus on top 5

        for channel in primary_channels:
            if "facebook" in channel.lower() or "social" in channel.lower():
                channel_strategies["facebook_ads"] = {
                    "strategy": "Direct response ads with video testimonials",
                    "budget_allocation": "40% of total ad spend",
                    "targeting": "Interest-based + lookalike audiences",
                    "creative": "User-generated content + testimonials",
                    "goal": "Lead generation at $2-5 per lead",
                }

            elif "email" in channel.lower() or "newsletter" in channel.lower():
                channel_strategies["email_marketing"] = {
                    "strategy": "Daily emails with valuable content + soft pitches",
                    "frequency": "5-7 emails per week",
                    "segments": "New subscribers, customers, VIP members",
                    "goal": "15-25% open rate, 3-7% click rate",
                }

            elif any(
                word in channel.lower()
                for word in ["linkedin", "professional", "business"]
            ):
                channel_strategies["linkedin_outreach"] = {
                    "strategy": "Personal brand building + direct outreach",
                    "daily_actions": "10 connection requests, 5 value posts",
                    "content_mix": "50% educational, 30% personal, 20% promotional",
                    "goal": "1,000 targeted connections per month",
                }

            elif any(word in channel.lower() for word in ["google", "search", "seo"]):
                channel_strategies["content_marketing"] = {
                    "strategy": "SEO-optimized content targeting buyer keywords",
                    "frequency": "2-3 blog posts per week",
                    "focus": "How-to content + tool comparisons",
                    "goal": "Rank page 1 for 10 buyer-intent keywords",
                }

            elif any(
                word in channel.lower() for word in ["podcast", "audio", "interview"]
            ):
                channel_strategies["podcast_tour"] = {
                    "strategy": "10 shows in 10 days approach",
                    "target": "Podcasts with 1,000+ downloads",
                    "pitch_ratio": "10 pitches per booking",
                    "goal": "2 bookings per week during launch",
                }

        # Direct mail strategy (Kennedy's favorite)
        channel_strategies["direct_mail"] = {
            "strategy": "Physical books to influencers and decision makers",
            "target_list": "Top 100 influencers in space",
            "package": "Book + personal letter + bonus materials",
            "goal": "10% response rate for partnerships",
        }

        # Create media calendar
        media_calendar = {
            "week_1_preparation": [
                "Finalize all creative assets",
                "Set up tracking systems",
                "Create content calendar",
                "Prepare email sequences",
            ],
            "week_2_soft_launch": [
                "Begin organic content posting",
                "Start email sequence to warm list",
                "Launch retargeting campaigns",
                "Begin podcast outreach",
            ],
            "week_3_full_launch": [
                "Launch all paid advertising",
                "Activate affiliate partners",
                "Begin direct mail campaign",
                "Increase content frequency",
            ],
            "week_4_optimization": [
                "Analyze performance data",
                "Double down on best performers",
                "Pause underperforming channels",
                "Plan next month's strategy",
            ],
        }

        # Budget allocation strategy
        budget_strategy = {
            "total_monthly_budget": "$2,000",
            "allocation": {
                "facebook_ads": "$800 (40%)",
                "google_ads": "$400 (20%)",
                "linkedin_ads": "$300 (15%)",
                "content_creation": "$200 (10%)",
                "direct_mail": "$200 (10%)",
                "tools_and_software": "$100 (5%)",
            },
            "roi_targets": {
                "facebook_ads": "3:1 return",
                "google_ads": "4:1 return",
                "linkedin_ads": "2:1 return",
                "content_marketing": "Long-term brand building",
                "direct_mail": "Partnership opportunities",
            },
        }

        # Create tracking system
        tracking_system = {
            "metrics_by_channel": {
                "facebook": ["CPM", "CTR", "CPC", "Conversion Rate", "ROAS"],
                "email": [
                    "Open Rate",
                    "Click Rate",
                    "Conversion Rate",
                    "Unsubscribe Rate",
                ],
                "content": [
                    "Organic Traffic",
                    "Time on Page",
                    "Email Signups",
                    "Social Shares",
                ],
                "podcast": [
                    "Downloads",
                    "Website Traffic",
                    "Email Signups",
                    "Book Sales",
                ],
            },
            "attribution_model": "First touch + last touch + email attribution",
            "reporting_frequency": "Daily dashboards + weekly deep dives",
            "optimization_trigger": "If channel falls below 50% of target ROI for 1 week",
        }

        # Save media domination plan
        media_file = self.output_dir / "media_domination_plan.json"
        media_data = {
            "media_domination": media_domination,
            "channel_strategies": channel_strategies,
            "media_calendar": media_calendar,
            "budget_strategy": budget_strategy,
            "tracking_system": tracking_system,
            "kennedy_principles": [
                "Be everywhere your customer is",
                "Match message to medium",
                "Test everything",
                "Scale what works",
                "Kill what doesn't",
            ],
        }

        with open(media_file, "w") as f:
            json.dump(media_data, f, indent=2)

        return {"media_domination_plan": str(media_file)}

    def _create_backend_systems(self) -> Dict:
        """Create Kennedy's backend/continuity revenue systems"""
        print("  💰 Creating backend revenue systems...")

        # Kennedy principle: Frontend breaks even, backend creates profit
        backend_system = {
            "kennedy_principle": "Books are the frontend. Real money is in the backend.",
            "revenue_model": "Frontend breaks even, backend = 80% of profit",
            "customer_journey": "Book buyer → Email subscriber → Course buyer → Coaching client",
        }

        # Create backend product ladder
        book_theme = self.book_config.get("puzzle_type", "crossword")

        if book_theme == "crossword":
            product_ladder = [
                {
                    "level": 1,
                    "product": self.title,
                    "price": "$6.99",
                    "profit_margin": "$3.50",
                    "purpose": "Lead generation + break even",
                },
                {
                    "level": 2,
                    "product": "Crossword Master's Toolkit",
                    "price": "$47",
                    "profit_margin": "$42",
                    "purpose": "Immediate upsell for hot buyers",
                },
                {
                    "level": 3,
                    "product": "Monthly Puzzle Club",
                    "price": "$19.97/month",
                    "profit_margin": "$17/month",
                    "purpose": "Recurring revenue + community",
                },
                {
                    "level": 4,
                    "product": "VIP Coaching Program",
                    "price": "$197/month",
                    "profit_margin": "$170/month",
                    "purpose": "High-value personal attention",
                },
                {
                    "level": 5,
                    "product": "Crossword Creator Certification",
                    "price": "$997",
                    "profit_margin": "$850",
                    "purpose": "Premium training program",
                },
            ]
        else:
            # Generic backend ladder
            product_ladder = [
                {
                    "level": 1,
                    "product": self.title,
                    "price": "$6.99",
                    "profit_margin": "$3.50",
                    "purpose": "Lead generation + break even",
                },
                {
                    "level": 2,
                    "product": "Advanced Training Course",
                    "price": "$97",
                    "profit_margin": "$87",
                    "purpose": "Core backend offer",
                },
                {
                    "level": 3,
                    "product": "Monthly Membership",
                    "price": "$29.97/month",
                    "profit_margin": "$25/month",
                    "purpose": "Recurring revenue",
                },
                {
                    "level": 4,
                    "product": "1-on-1 Coaching",
                    "price": "$497/month",
                    "profit_margin": "$450/month",
                    "purpose": "Premium high-touch service",
                },
                {
                    "level": 5,
                    "product": "Done-For-You Service",
                    "price": "$2,997",
                    "profit_margin": "$2,500",
                    "purpose": "Ultimate high-value offer",
                },
            ]

        # Create ascension sequences
        ascension_sequences = {
            "book_to_course": {
                "timing": "7 days after book purchase",
                "method": "Email sequence + special offer",
                "conversion_target": "15-25%",
                "offer": "Limited-time 50% discount on advanced training",
            },
            "course_to_membership": {
                "timing": "During course completion",
                "method": "Bonus module + membership preview",
                "conversion_target": "30-40%",
                "offer": "First month free trial membership",
            },
            "membership_to_coaching": {
                "timing": "After 3 months membership",
                "method": "Personal invitation from author",
                "conversion_target": "5-10%",
                "offer": "VIP coaching application process",
            },
        }

        # Create continuity programs
        continuity_programs = {
            "basic_membership": {
                "price": "$19.97/month",
                "benefits": [
                    "Monthly new puzzle pack",
                    "Video training library access",
                    "Private Facebook group",
                    "Monthly Q&A call",
                ],
                "retention_strategy": "High value, low price point",
                "churn_target": "Less than 5% monthly",
            },
            "vip_membership": {
                "price": "$49.97/month",
                "benefits": [
                    "Everything in basic",
                    "Personal email access to author",
                    "Monthly 1-on-1 call",
                    "Advanced training modules",
                ],
                "retention_strategy": "Personal attention + exclusivity",
                "churn_target": "Less than 3% monthly",
            },
        }

        # Create revenue projections
        revenue_projections = {
            "monthly_book_sales": 100,
            "book_revenue": "$699",
            "book_profit": "$350",
            "backend_conversions": {
                "course": "20 sales × $97 = $1,940",
                "membership": "15 new members × $19.97 = $299.55",
                "coaching": "2 new clients × $497 = $994",
            },
            "monthly_backend_revenue": "$3,233.55",
            "total_monthly_revenue": "$3,932.55",
            "backend_percentage": "82% of total revenue",
        }

        # Create customer lifetime value calculation
        ltv_calculation = {
            "average_book_buyer": {
                "initial_purchase": "$6.99",
                "course_probability": "20%",
                "course_value": "$97 × 0.20 = $19.40",
                "membership_probability": "15%",
                "membership_value": "$19.97 × 12 months × 0.15 = $35.94",
                "coaching_probability": "2%",
                "coaching_value": "$497 × 6 months × 0.02 = $59.64",
                "total_ltv": "$121.97",
            },
            "ltv_optimization": {
                "increase_backend_conversion": "Focus on email nurture sequences",
                "increase_retention": "Improve onboarding and engagement",
                "increase_order_value": "Bundle products and payment plans",
                "increase_referrals": "Implement affiliate program",
            },
        }

        # Save backend systems
        backend_file = self.output_dir / "backend_systems.json"
        backend_data = {
            "backend_system": backend_system,
            "product_ladder": product_ladder,
            "ascension_sequences": ascension_sequences,
            "continuity_programs": continuity_programs,
            "revenue_projections": revenue_projections,
            "ltv_calculation": ltv_calculation,
            "implementation_priorities": [
                "Set up email sequences for backend offers",
                "Create course curriculum and delivery system",
                "Build membership platform with content",
                "Design coaching program structure",
                "Implement tracking for all conversions",
            ],
        }

        with open(backend_file, "w") as f:
            json.dump(backend_data, f, indent=2)

        return {"backend_systems": str(backend_file)}

    def _create_social_proof_systems(self) -> Dict:
        """Create Kennedy's social proof and testimonial systems"""
        print("  ⭐ Creating social proof systems...")

        # Kennedy principle: Social proof is the most powerful persuasion tool
        social_proof_system = {
            "kennedy_principle": "People follow people. Social proof eliminates skepticism.",
            "proof_hierarchy": [
                "Expert testimonials (highest credibility)",
                "Customer testimonials (highest relatability)",
                "Usage statistics (social validation)",
                "Media mentions (authority transfer)",
                "Sales numbers (popularity proof)",
            ],
        }

        # Create testimonial collection system
        testimonial_system = {
            "collection_methods": {
                "email_surveys": {
                    "timing": "7 days after book delivery",
                    "questions": [
                        "What specific result did you get from [BOOK]?",
                        "How has this changed your daily routine?",
                        "What would you tell someone considering this book?",
                        "Can we use your feedback as a testimonial?",
                    ],
                    "incentive": "$10 Amazon gift card for detailed testimonials",
                },
                "social_media_monitoring": {
                    "platforms": ["Facebook", "Twitter", "Instagram", "LinkedIn"],
                    "hashtags": [
                        f"#{self.series_name.replace(' ', '')}",
                        f"#{self.book_config.get('puzzle_type', 'puzzle')}book",
                    ],
                    "monitoring_tools": [
                        "Google Alerts",
                        "Social Mention",
                        "Hootsuite",
                    ],
                },
                "direct_outreach": {
                    "timing": "After positive customer service interactions",
                    "method": "Personal email from author",
                    "request": "Quick video testimonial on phone",
                },
            }
        }

        # Create testimonial templates
        testimonial_templates = {
            "short_form": [
                '"[SPECIFIC RESULT] in just [TIME PERIOD]" - [NAME], [TITLE]',
                '"Finally, a [BOOK TYPE] that actually works!" - [NAME], [LOCATION]',
                '"Worth every penny and more" - [NAME], [AGE/DEMOGRAPHIC]',
            ],
            "long_form": [
                '"I was skeptical at first, but [BOOK] delivered exactly what it promised. [SPECIFIC RESULT] in [TIME PERIOD]. I\'ve already recommended it to [NUMBER] friends." - [NAME], [CREDENTIALS]',
                "\"As someone who [BACKGROUND], I thought I'd tried everything. But [UNIQUE MECHANISM] changed everything. Now I [CURRENT STATE] and couldn't be happier.\" - [NAME], [TITLE]",
            ],
            "video_testimonials": {
                "questions": [
                    "What was your situation before reading [BOOK]?",
                    "What made you decide to try it?",
                    "What specific results have you seen?",
                    "Who would you recommend this to?",
                ],
                "duration": "60-90 seconds maximum",
                "format": "Casual, authentic, unscripted",
            },
        }

        # Create social proof display system
        proof_display = {
            "book_listing": [
                "Featured testimonials in description",
                "5-star review badges",
                "Number of satisfied customers",
                "Media mention quotes",
            ],
            "landing_pages": [
                "Video testimonials above the fold",
                "Written testimonials throughout page",
                "Trust badges and certifications",
                "Real-time sales notifications",
            ],
            "email_sequences": [
                "Customer success stories",
                "Before/after case studies",
                "Peer recommendations",
                "Expert endorsements",
            ],
        }

        # Create authority building system
        authority_system = {
            "expert_positioning": [
                f"Author of bestselling {self.title}",
                f"Creator of the {self.series_name} Method™",
                f"Trusted by [NUMBER] satisfied readers",
                "Featured expert in [PUBLICATIONS]",
            ],
            "media_outreach": {
                "target_publications": [
                    "Local newspapers",
                    "Industry magazines",
                    "Relevant blogs",
                    "Podcast shows",
                ],
                "story_angles": [
                    f"Local author creates revolutionary {
                        self.book_config.get('puzzle_type', 'puzzle')} method",
                    f"How {self.author} built 6-figure business with puzzles",
                    f"The science behind {self.series_name} Method™",
                ],
            },
            "speaking_opportunities": [
                "Local library presentations",
                "Senior center workshops",
                "Industry conferences",
                "Podcast interviews",
            ],
        }

        # Create social proof automation
        automation_system = {
            "review_generation": {
                "amazon_follow_up": "Email sequence requesting honest reviews",
                "facebook_encouragement": "Posts asking for feedback",
                "website_testimonials": "Popup requesting testimonials",
                "incentive_program": "Rewards for detailed reviews",
            },
            "proof_distribution": {
                "email_signatures": "Include testimonial quotes",
                "social_media_posts": "Share customer success stories",
                "website_updates": "Add new testimonials monthly",
                "marketing_materials": "Include in all promotional content",
            },
        }

        # Create credibility markers
        credibility_markers = {
            "numbers": [
                f"Over [NUMBER] copies sold",
                f"[NUMBER]+ satisfied customers",
                f"Featured in [NUMBER] publications",
                f"[NUMBER] five-star reviews",
            ],
            "associations": [
                "Member of [PROFESSIONAL ORGANIZATION]",
                "Certified by [AUTHORITY]",
                "Endorsed by [EXPERT]",
                "Featured in [MEDIA]",
            ],
            "achievements": [
                f"#1 Bestseller in {
                    self.book_config.get(
                        'puzzle_type',
                        'puzzle')} category",
                "Winner of [AWARD]",
                "Recognized expert in [FIELD]",
                "Speaker at [EVENT]",
            ],
        }

        # Save social proof systems
        proof_file = self.output_dir / "social_proof_systems.json"
        proof_data = {
            "social_proof_system": social_proof_system,
            "testimonial_system": testimonial_system,
            "testimonial_templates": testimonial_templates,
            "proof_display": proof_display,
            "authority_system": authority_system,
            "automation_system": automation_system,
            "credibility_markers": credibility_markers,
            "implementation_checklist": [
                "Set up testimonial collection system",
                "Create review generation campaigns",
                "Build authority through media outreach",
                "Display social proof on all materials",
                "Automate proof collection and distribution",
            ],
        }

        with open(proof_file, "w") as f:
            json.dump(proof_data, f, indent=2)

        return {"social_proof_systems": str(proof_file)}


def main():
    """CLI interface for magnetic marketing system"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Dan Kennedy's Magnetic Marketing for KindleMint"
    )
    parser.add_argument(
        "--book-config", required=True, help="Book configuration JSON file"
    )
    parser.add_argument(
        "--artifacts-dir", required=True, help="Directory containing book artifacts"
    )

    args = parser.parse_args()

    # Load book configuration
    with open(args.book_config, "r") as f:
        book_config = json.load(f)

    # Create mock artifacts for CLI usage
    artifacts = {
        "puzzles_dir": args.artifacts_dir,
        "pdf_file": f"{args.artifacts_dir}/interior.pdf",
    }

    # Run magnetic marketing system
    magnetic_engine = MagneticMarketingEngine(book_config, artifacts)
    results = magnetic_engine.create_magnetic_marketing_system()

    print(f"\n🧲 Magnetic Marketing System created successfully!")
    print(f"📁 Output directory: {magnetic_engine.output_dir}")

    for asset_type, file_path in results.items():
        print(f"   • {asset_type}: {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
