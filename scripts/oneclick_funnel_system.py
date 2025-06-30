#!/usr/bin/env python3
"""
One-Click Funnel System for KindleMint Engine
Implements Marketing School's "One-Click Simplification" principle
"Remove friction at every step of the customer journey" - Neil Patel & Eric Siu
"""

import json
import sys
from pathlib import Path
from typing import Dict

try:
    pass

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class OneClickFunnelSystem:
    """
    Creates complete one-click funnel automation system
    Removes friction and automates customer journey
    """

    def __init__(self, book_config: Dict, book_artifacts: Dict):
        """Initialize the One-Click Funnel System"""
        self.book_config = book_config
        self.book_artifacts = book_artifacts
        self.series_name = book_config.get("series_name", "Default_Series")
        self.volume = book_config.get("volume", 1)
        self.title = book_config.get(
            "title", f"{self.series_name} Volume {self.volume}"
        )
        self.author = book_config.get("author", "OneClick Publishing")

        # Create funnel output directory
        self.output_dir = Path(
            f"books/active_production/{self.series_name}/volume_{self.volume}/oneclick_funnel"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Marketing School funnel principles
        self.funnel_principles = {
            "one_click_rule": "Every action should require only one click",
            "friction_elimination": "Remove every unnecessary step",
            "instant_gratification": "Deliver value immediately",
            "progressive_commitment": "Small yes leads to bigger yes",
            "automation_first": "Automate everything possible",
        }

    def build_complete_funnel(self) -> Dict:
        """
        Build complete one-click funnel system
        Returns dictionary of all funnel components
        """
        print("🖱️ Building Complete One-Click Funnel System...")

        assets = {}

        # 1. Create Landing Page System
        assets.update(self._create_landing_pages())

        # 2. Build Email Capture Automation
        assets.update(self._build_email_capture())

        # 3. Design Purchase Funnel
        assets.update(self._design_purchase_funnel())

        # 4. Create Automated Sequences
        assets.update(self._create_automated_sequences())

        # 5. Build Upsell Automation
        assets.update(self._build_upsell_automation())

        # 6. Implement Conversion Tracking
        assets.update(self._implement_conversion_tracking())

        # 7. Create A/B Testing Framework
        assets.update(self._create_ab_testing())

        # 8. Build Analytics Dashboard
        assets.update(self._build_analytics_dashboard())

        # 9. Create Mobile Optimization
        assets.update(self._create_mobile_optimization())

        return assets

    def _create_landing_pages(self) -> Dict:
        """Create optimized landing pages"""
        print("  📄 Creating Landing Pages...")

        # Landing Page Strategy
        landing_strategy = {
            "core_principle": "Single focus, clear value, one action",
            "conversion_targets": {
                "email_capture": "25% of visitors",
                "direct_purchase": "5% of visitors",
                "total_engagement": "30% of visitors",
            },
        }

        # Landing Page Templates
        landing_templates = {
            "lead_magnet_page": {
                "purpose": "Capture emails with free chapter",
                "headline": f"Get the First Chapter of '{self.title}' FREE",
                "subheadline": "Discover why thousands of puzzle lovers call this the most accessible crossword book ever created",
                "value_points": [
                    "✅ Large 14-point font - easy on the eyes",
                    "✅ Progressive difficulty - builds confidence",
                    "✅ Tested by 100+ seniors - proven effective",
                    "✅ Instant download - start solving today",
                ],
                "social_proof": [
                    "★★★★★ 'Finally, crosswords I can actually see!' - Margaret, 72",
                    "★★★★★ 'Perfect difficulty progression' - Robert, 68",
                    "★★★★★ 'Best puzzle book I've found' - Helen, 75",
                ],
                "cta": "Get Your Free Chapter Now",
                "form_fields": ["email_only"],
                "delivery": "Instant PDF download + email course",
            },
            "direct_purchase_page": {
                "purpose": "Direct book sales from ads",
                "headline": f"The Crossword Book That Actually Works for Seniors",
                "subheadline": f"'{self.title}' - Large Print, Fair Clues, Progressive Difficulty",
                "value_stack": [
                    f"✅ {self.title} - Complete puzzle book ($24.99 value)",
                    "✅ Solving Strategies Guide - Bonus PDF ($19.99 value)",
                    "✅ Large Print Guarantee - Perfect for aging eyes",
                    "✅ 30-Day Money Back Guarantee - Zero risk",
                    "✅ Instant Digital Access - Start solving today",
                ],
                "urgency": "Limited Time: 70% Off Launch Price",
                "price_display": {
                    "original": "$44.98",
                    "your_price": "$6.99",
                    "savings": "Save $37.99",
                },
                "cta": "Get Your Copy Now - Just $6.99",
                "guarantee": "30-day money-back guarantee",
            },
            "upsell_page": {
                "purpose": "Workbook upsell after book purchase",
                "headline": "Congratulations! Want to 10X Your Solving Skills?",
                "subheadline": "Get the Complete Solutions + Advanced Techniques Workbook",
                "offer_details": [
                    "✅ Complete solutions to every puzzle in your book",
                    "✅ Advanced solving techniques not in the main book",
                    "✅ 25 bonus practice puzzles with solutions",
                    "✅ Speed solving methods and timing strategies",
                ],
                "special_pricing": {
                    "regular_price": "$19.99",
                    "special_price": "$9.99",
                    "condition": "Available only to book purchasers",
                },
                "cta": "Yes, Add the Workbook - Just $9.99",
                "timer": "This offer expires in 15 minutes",
            },
        }

        # HTML Templates Generation
        html_templates = {}
        for page_type, page_data in landing_templates.items():
            html_templates[page_type] = self._generate_html_template(
                page_type, page_data
            )

        # Mobile Optimization
        mobile_optimization = {
            "responsive_design": "Mobile-first approach",
            "touch_targets": "Minimum 44px for easy tapping",
            "load_speed": "Under 3 seconds on 3G",
            "form_optimization": "Large input fields, minimal typing",
            "cta_placement": "Always visible, thumb-friendly",
        }

        # Conversion Elements
        conversion_elements = {
            "trust_signals": [
                "SSL certificate badge",
                "Money-back guarantee seal",
                "Customer testimonials with photos",
                "Author credentials and photo",
            ],
            "urgency_elements": [
                "Countdown timer for special offers",
                "Limited quantity messaging",
                "Social proof notifications (X people bought today)",
                "Price increase warnings",
            ],
            "social_proof": [
                "Customer review widgets",
                "Social media mentions",
                "Sales counter displays",
                "Press mention badges",
            ],
        }

        # Save landing pages
        landing_file = self.output_dir / "landing_pages.json"
        landing_data = {
            "landing_strategy": landing_strategy,
            "landing_templates": landing_templates,
            "html_templates": html_templates,
            "mobile_optimization": mobile_optimization,
            "conversion_elements": conversion_elements,
            "testing_checklist": [
                "Test on all major browsers",
                "Test on mobile devices",
                "Test form submissions",
                "Test payment processing",
                "Test load speed optimization",
            ],
        }

        with open(landing_file, "w") as f:
            json.dump(landing_data, f, indent=2)

        # Create actual HTML files
        self._create_html_files(html_templates)

        return {"landing_pages": str(landing_file)}

    def _generate_html_template(self, page_type: str, page_data: Dict) -> str:
        """Generate HTML template for landing page"""

        base_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data.get('headline', 'Default Title')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Georgia', serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .headline {{ font-size: 2.5em; font-weight: bold; margin-bottom: 20px; color: #2c3e50; }}
        .subheadline {{ font-size: 1.3em; color: #7f8c8d; margin-bottom: 30px; }}
        .value-points {{ margin: 30px 0; }}
        .value-points li {{ font-size: 1.2em; margin: 10px 0; list-style: none; }}
        .social-proof {{ background: #f8f9fa; padding: 20px; margin: 30px 0; border-radius: 10px; }}
        .testimonial {{ margin: 15px 0; font-style: italic; }}
        .cta-section {{ text-align: center; margin: 40px 0; }}
        .cta-button {{
            background: #e74c3c; color: white; padding: 20px 40px;
            font-size: 1.5em; border: none; border-radius: 10px;
            cursor: pointer; text-decoration: none; display: inline-block;
            transition: background 0.3s;
        }}
        .cta-button:hover {{ background: #c0392b; }}
        .form-section {{ max-width: 400px; margin: 0 auto; }}
        .form-input {{ width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #ddd; border-radius: 5px; font-size: 1.1em; }}
        .guarantee {{ text-align: center; margin: 20px 0; font-weight: bold; color: #27ae60; }}
        .timer {{ text-align: center; font-size: 1.3em; color: #e74c3c; margin: 20px 0; }}
        @media (max-width: 768px) {{
            .headline {{ font-size: 2em; }}
            .container {{ padding: 15px; }}
            .cta-button {{ padding: 15px 30px; font-size: 1.2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="headline">{page_data.get('headline', 'Default Headline')}</h1>
            <p class="subheadline">{page_data.get('subheadline', 'Default subheadline')}</p>
        </div>
"""

        # Add specific content based on page type
        if page_type == "lead_magnet_page":
            base_template += f"""
        <div class="value-points">
            <ul>
                {''.join([f'<li>{point}</li>' for point in page_data.get('value_points', [])])}
            </ul>
        </div>

        <div class="social-proof">
            {''.join([f'<div class="testimonial">{proof}</div>' for proof in page_data.get('social_proof', [])])}
        </div>

        <div class="cta-section">
            <form class="form-section" action="/capture-email" method="POST">
                <input type="email" class="form-input" placeholder="Enter your email address" name="email" required>
                <button type="submit" class="cta-button">{page_data.get('cta', 'Get Free Chapter')}</button>
            </form>
        </div>

        <div class="guarantee">
            <p>✅ Instant download • No spam ever • Unsubscribe anytime</p>
        </div>
"""

        elif page_type == "direct_purchase_page":
            base_template += f"""
        <div class="value-points">
            <ul>
                {''.join([f'<li>{point}</li>' for point in page_data.get('value_stack', [])])}
            </ul>
        </div>

        <div class="price-section" style="text-align: center; margin: 30px 0;">
            <div style="font-size: 1.5em;">
                <span style="text-decoration: line-through; color: #7f8c8d;">${page_data.get('price_display', {}).get('original', '44.98')}</span>
                <span style="font-size: 2em; color: #e74c3c; font-weight: bold;">${page_data.get('price_display', {}).get('your_price', '6.99')}</span>
            </div>
            <p style="color: #27ae60; font-weight: bold;">{page_data.get('price_display', {}).get('savings', 'Save $37.99')}</p>
        </div>

        <div class="cta-section">
            <a href="/purchase" class="cta-button">{page_data.get('cta', 'Get Your Copy Now')}</a>
        </div>

        <div class="guarantee">
            <p>🛡️ {page_data.get('guarantee', '30-day money-back guarantee')}</p>
        </div>
"""

        elif page_type == "upsell_page":
            base_template += f"""
        <div class="value-points">
            <ul>
                {''.join([f'<li>{point}</li>' for point in page_data.get('offer_details', [])])}
            </ul>
        </div>

        <div class="timer">
            ⏰ This exclusive offer expires in <span id="countdown">15:00</span>
        </div>

        <div class="price-section" style="text-align: center; margin: 30px 0;">
            <div style="font-size: 1.5em;">
                <span style="text-decoration: line-through; color: #7f8c8d;">${page_data.get('special_pricing', {}).get('regular_price', '19.99')}</span>
                <span style="font-size: 2em; color: #e74c3c; font-weight: bold;">${page_data.get('special_pricing', {}).get('special_price', '9.99')}</span>
            </div>
            <p style="color: #27ae60; font-weight: bold;">Special Price for Book Buyers Only!</p>
        </div>

        <div class="cta-section">
            <a href="/upsell-purchase" class="cta-button">{page_data.get('cta', 'Yes, Add the Workbook')}</a>
            <br><br>
            <a href="/no-thanks" style="color: #7f8c8d; text-decoration: underline;">No thanks, I'll pass on this offer</a>
        </div>

        <script>
            // Countdown timer
            let timeLeft = 15 * 60; // 15 minutes in seconds
            const countdown = document.getElementById('countdown');

            function updateTimer() {{
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                countdown.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;

                if (timeLeft > 0) {{
                    timeLeft--;
                    setTimeout(updateTimer, 1000);
                }} else {{
                    countdown.textContent = 'EXPIRED';
                    document.querySelector('.cta-button').style.display = 'none';
                }}
            }}
            updateTimer();
        </script>
"""

        base_template += """
    </div>
</body>
</html>"""

        return base_template

    def _create_html_files(self, html_templates: Dict) -> None:
        """Create actual HTML files from templates"""
        html_dir = self.output_dir / "html_pages"
        html_dir.mkdir(exist_ok=True)

        for page_type, html_content in html_templates.items():
            html_file = html_dir / f"{page_type}.html"
            with open(html_file, "w") as f:
                f.write(html_content)

    def _build_email_capture(self) -> Dict:
        """Build email capture automation"""
        print("  📧 Building Email Capture Automation...")

        # Email Capture Strategy
        capture_strategy = {
            "lead_magnets": [
                "Free chapter download",
                "Solving tips email course",
                "Bonus puzzle pack",
                "Advanced strategies guide",
            ],
            "capture_points": [
                "Landing page primary form",
                "Exit-intent popup",
                "Scroll-triggered sidebar",
                "Content upgrade boxes",
            ],
        }

        # Lead Magnet Creation
        lead_magnets = {
            "free_chapter": {
                "title": f"Free Chapter from '{self.title}'",
                "description": "Get the first 10 pages plus bonus solving tips",
                "file_format": "PDF download",
                "delivery_method": "Instant email delivery",
                "follow_up": "7-day email course",
            },
            "solving_course": {
                "title": "7-Day Crossword Mastery Email Course",
                "description": "Daily tips to improve your solving skills",
                "format": "Email series",
                "delivery_method": "Daily emails for 7 days",
                "follow_up": "Weekly newsletter",
            },
            "bonus_puzzles": {
                "title": "Exclusive Bonus Puzzle Pack",
                "description": "5 additional large-print puzzles with solutions",
                "file_format": "PDF download",
                "delivery_method": "Instant email delivery",
                "follow_up": "Monthly puzzle updates",
            },
        }

        # Email Automation Sequences
        automation_sequences = {
            "welcome_sequence": [
                {
                    "trigger": "Email signup",
                    "delay": "Immediate",
                    "subject": f"Your free chapter from '{self.title}' is here!",
                    "content": "Welcome + deliver lead magnet + soft introduction to book",
                    "cta": "Read your free chapter",
                },
                {
                    "trigger": "Previous email",
                    "delay": "24 hours",
                    "subject": "Did you enjoy your free chapter?",
                    "content": "Value-first email with solving tip + book mention",
                    "cta": "Get the complete book",
                },
                {
                    "trigger": "Previous email",
                    "delay": "48 hours",
                    "subject": "The #1 mistake most crossword solvers make",
                    "content": "Educational content + social proof + book offer",
                    "cta": "Avoid this mistake - get the book",
                },
                {
                    "trigger": "Previous email",
                    "delay": "72 hours",
                    "subject": "Last chance for launch pricing",
                    "content": "Urgency + scarcity + final book offer",
                    "cta": "Get your copy before price increase",
                },
            ],
            "nurture_sequence": [
                {
                    "trigger": "Welcome sequence completion",
                    "frequency": "Weekly",
                    "content_types": [
                        "Educational content about puzzle solving",
                        "Behind-the-scenes author content",
                        "Reader success stories",
                        "New puzzle releases and updates",
                    ],
                }
            ],
        }

        # Segmentation Strategy
        segmentation_strategy = {
            "subscriber_segments": {
                "new_subscribers": "Recently joined, not purchased",
                "book_buyers": "Purchased core book",
                "ecosystem_members": "Purchased multiple products",
                "inactive_subscribers": "Low engagement, no purchases",
            },
            "personalization_rules": {
                "content_preferences": "Track which email topics get highest engagement",
                "purchase_behavior": "Recommend products based on previous purchases",
                "engagement_level": "Adjust email frequency based on engagement",
                "demographic_data": "Customize content for age and skill level",
            },
        }

        # Email Templates
        email_templates = {
            "welcome_email": {
                "subject": f"Your free chapter from '{self.title}' is here! 📚",
                "content": f"""Hi there!

Welcome to our puzzle-loving community! 🎯

As promised, here's your FREE chapter from '{self.title}':

[DOWNLOAD LINK]

I created this book specifically for people who love crosswords but struggle with:
• Print that's too small to see comfortably
• Clues that are unfairly difficult or obscure
• Inconsistent difficulty that jumps around

This book solves all three problems.

Tomorrow, I'll share the #1 technique that helped 500+ readers solve puzzles 50% faster.

Happy puzzling!
{self.author}

P.S. Have questions about any puzzle? Just reply - I read every email!""",
                "cta": "Download Your Free Chapter",
            }
        }

        # Save email capture system
        capture_file = self.output_dir / "email_capture_system.json"
        capture_data = {
            "capture_strategy": capture_strategy,
            "lead_magnets": lead_magnets,
            "automation_sequences": automation_sequences,
            "segmentation_strategy": segmentation_strategy,
            "email_templates": email_templates,
            "technical_setup": [
                "ConvertKit or ActiveCampaign integration",
                "Landing page form connections",
                "Automatic PDF delivery setup",
                "Segmentation rules configuration",
                "Analytics tracking implementation",
            ],
        }

        with open(capture_file, "w") as f:
            json.dump(capture_data, f, indent=2)

        return {"email_capture_system": str(capture_file)}

    def _design_purchase_funnel(self) -> Dict:
        """Design optimized purchase funnel"""
        print("  💳 Designing Purchase Funnel...")

        # Purchase Funnel Strategy
        funnel_strategy = {
            "core_principle": "Minimize clicks from interest to purchase",
            "conversion_targets": {
                "landing_to_cart": "15%",
                "cart_to_purchase": "85%",
                "overall_conversion": "12.75%",
            },
        }

        # Funnel Flow Design
        funnel_flow = {
            "step_1_awareness": {
                "source": "Facebook ad, LinkedIn post, email link",
                "destination": "Product landing page",
                "goal": "Generate interest and desire",
                "conversion_metric": "Click-through rate",
            },
            "step_2_interest": {
                "source": "Landing page",
                "destination": "Checkout page",
                "goal": "Convert interest to purchase intent",
                "conversion_metric": "Add to cart rate",
            },
            "step_3_purchase": {
                "source": "Checkout page",
                "destination": "Thank you page",
                "goal": "Complete transaction",
                "conversion_metric": "Purchase completion rate",
            },
            "step_4_fulfillment": {
                "source": "Thank you page",
                "destination": "Product delivery + upsell",
                "goal": "Deliver product and present upsell",
                "conversion_metric": "Upsell acceptance rate",
            },
        }

        # Checkout Optimization
        checkout_optimization = {
            "page_elements": {
                "product_summary": "Clear display of what they're buying",
                "trust_signals": "SSL badges, guarantee, testimonials",
                "social_proof": "Recent purchases, customer count",
                "urgency_elements": "Limited time offers, countdown timers",
            },
            "form_optimization": {
                "guest_checkout": "Allow purchase without account creation",
                "minimal_fields": "Only essential information required",
                "autofill_support": "Browser autofill compatibility",
                "payment_options": "Credit card, PayPal, Apple Pay",
            },
            "mobile_optimization": {
                "thumb_friendly_buttons": "Large, easy-to-tap elements",
                "simplified_layout": "Single column on mobile",
                "fast_loading": "Optimized images and code",
                "keyboard_friendly": "Proper input types for mobile keyboards",
            },
        }

        # Cart Abandonment Recovery
        abandonment_recovery = {
            "exit_intent_popup": {
                "trigger": "Mouse moves toward browser close button",
                "offer": "10% discount to complete purchase",
                "headline": "Wait! Don't leave empty-handed",
                "cta": "Get 10% off - Complete Your Order",
            },
            "email_recovery_sequence": [
                {
                    "delay": "1 hour",
                    "subject": "You left something in your cart...",
                    "content": "Gentle reminder with product benefits",
                    "offer": "Free bonus guide with purchase",
                },
                {
                    "delay": "24 hours",
                    "subject": "Still thinking about [PRODUCT]?",
                    "content": "Address common objections + testimonials",
                    "offer": "15% discount code",
                },
                {
                    "delay": "72 hours",
                    "subject": "Last chance for your reserved copy",
                    "content": "Final urgency + scarcity messaging",
                    "offer": "20% discount - expires in 24 hours",
                },
            ],
            "retargeting_ads": {
                "platform": "Facebook and Google",
                "audience": "Cart abandoners last 7 days",
                "creative": "Dynamic product ads with discount offers",
                "budget": "20% of total ad spend",
            },
        }

        # Payment Processing
        payment_processing = {
            "primary_processor": "Stripe for reliability and features",
            "backup_processor": "PayPal for redundancy",
            "supported_methods": [
                "Credit/debit cards (Visa, MC, Amex)",
                "PayPal account",
                "Apple Pay",
                "Google Pay",
            ],
            "security_features": [
                "SSL encryption",
                "PCI compliance",
                "Fraud detection",
                "3D secure authentication",
            ],
        }

        # Save purchase funnel
        funnel_file = self.output_dir / "purchase_funnel.json"
        funnel_data = {
            "funnel_strategy": funnel_strategy,
            "funnel_flow": funnel_flow,
            "checkout_optimization": checkout_optimization,
            "abandonment_recovery": abandonment_recovery,
            "payment_processing": payment_processing,
            "testing_priorities": [
                "A/B test checkout page layouts",
                "Test different payment button colors",
                "Test various urgency messages",
                "Test mobile vs desktop flows",
                "Test guest vs account checkout",
            ],
        }

        with open(funnel_file, "w") as f:
            json.dump(funnel_data, f, indent=2)

        return {"purchase_funnel": str(funnel_file)}

    def _create_automated_sequences(self) -> Dict:
        """Create comprehensive automated sequences"""
        print("  🤖 Creating Automated Sequences...")

        # Automation Strategy
        automation_strategy = {
            "core_principle": "Right message, right person, right time",
            "sequence_types": [
                "Welcome and onboarding",
                "Purchase confirmation and delivery",
                "Upsell and cross-sell",
                "Re-engagement and win-back",
            ],
        }

        # Post-Purchase Sequences
        post_purchase_sequences = {
            "immediate_confirmation": {
                "trigger": "Purchase completion",
                "delay": "Immediate",
                "subject": f"Your '{self.title}' download is ready!",
                "content": [
                    "Thank you for your purchase",
                    "Download links for all purchased items",
                    "Getting started guide and tips",
                    "Introduction to customer community",
                    "Soft mention of complementary products",
                ],
                "attachments": ["PDF download", "bonus_materials.pdf"],
            },
            "day_3_check_in": {
                "trigger": "3 days after purchase",
                "subject": "How are you enjoying your puzzles?",
                "content": [
                    "Check on customer satisfaction",
                    "Provide additional solving tips",
                    "Address common questions",
                    "Invite to share feedback or questions",
                ],
                "goal": "Ensure customer success and satisfaction",
            },
            "day_7_upsell": {
                "trigger": "7 days after purchase",
                "subject": "Ready to take your solving to the next level?",
                "content": [
                    "Celebrate their progress so far",
                    "Introduce workbook companion",
                    "Share success stories from workbook users",
                    "Limited-time special pricing offer",
                ],
                "offer": "Workbook companion at 50% off",
                "goal": "Convert to ecosystem second purchase",
            },
        }

        # Engagement-Based Sequences
        engagement_sequences = {
            "high_engagement": {
                "trigger": "Opens 80%+ of emails, clicks frequently",
                "sequence": [
                    "VIP recognition and appreciation",
                    "Exclusive early access to new products",
                    "Invitation to beta test programs",
                    "Personal note from author",
                ],
            },
            "medium_engagement": {
                "trigger": "Opens 40-80% of emails",
                "sequence": [
                    "Continued value delivery",
                    "Personal success stories",
                    "Community highlights",
                    "Gentle product recommendations",
                ],
            },
            "low_engagement": {
                "trigger": "Opens <40% of emails",
                "sequence": [
                    "Re-engagement campaign with best content",
                    "Survey to understand preferences",
                    "Exclusive re-engagement offer",
                    "Final 'we'll miss you' email with unsubscribe",
                ],
            },
        }

        # Behavioral Triggers
        behavioral_triggers = {
            "email_link_clicks": {
                "trigger": "Clicks specific product links in emails",
                "action": "Add to targeted product sequence",
                "timing": "Next email in sequence",
            },
            "website_behavior": {
                "trigger": "Visits pricing page multiple times",
                "action": "Send targeted offer email",
                "timing": "Within 2 hours of visit",
            },
            "social_engagement": {
                "trigger": "Shares content on social media",
                "action": "Thank you email + exclusive bonus",
                "timing": "Within 24 hours",
            },
            "support_contact": {
                "trigger": "Contacts customer support",
                "action": "Follow-up satisfaction sequence",
                "timing": "24 hours after resolution",
            },
        }

        # Seasonal Sequences
        seasonal_sequences = {
            "holiday_campaigns": {
                "thanksgiving": "Gratitude-focused content + special offers",
                "christmas": "Gift guide for puzzle lovers + gift certificates",
                "new_year": "New year resolution support + goal setting",
                "valentines": "Puzzles for couples + romantic themes",
            },
            "personal_milestones": {
                "birthday": "Personal birthday message + special discount",
                "anniversary": "Subscription anniversary celebration",
                "achievement": "Completion of course or program milestone",
            },
        }

        # Save automated sequences
        sequences_file = self.output_dir / "automated_sequences.json"
        sequences_data = {
            "automation_strategy": automation_strategy,
            "post_purchase_sequences": post_purchase_sequences,
            "engagement_sequences": engagement_sequences,
            "behavioral_triggers": behavioral_triggers,
            "seasonal_sequences": seasonal_sequences,
            "technical_requirements": [
                "Marketing automation platform (ConvertKit/ActiveCampaign)",
                "Website tracking and tagging system",
                "Email template library",
                "A/B testing capabilities",
                "Analytics and reporting dashboard",
            ],
        }

        with open(sequences_file, "w") as f:
            json.dump(sequences_data, f, indent=2)

        return {"automated_sequences": str(sequences_file)}

    def _build_upsell_automation(self) -> Dict:
        """Build upsell automation system"""
        print("  📈 Building Upsell Automation...")

        # Upsell Strategy
        upsell_strategy = {
            "core_principle": "Natural progression through value ladder",
            "timing_rules": [
                "Immediate post-purchase for impulse offers",
                "7-day mark for relationship-based offers",
                "30-day mark for advanced products",
                "Quarterly for premium programs",
            ],
        }

        # Upsell Flows
        upsell_flows = {
            "immediate_upsell": {
                "trigger": "Book purchase completion",
                "timing": "Redirect to upsell page immediately",
                "product": "Workbook companion",
                "pricing": "50% off regular price",
                "urgency": "Limited time offer expires in 15 minutes",
                "conversion_target": "30% of book buyers",
            },
            "email_upsell_sequence": {
                "trigger": "7 days after book purchase",
                "product": "Audio course",
                "sequence": [
                    {
                        "day": 7,
                        "subject": "Ready for the next level?",
                        "content": "Introduction to audio course + preview",
                        "offer": "Early bird pricing",
                    },
                    {
                        "day": 10,
                        "subject": "Listen to what others are saying...",
                        "content": "Success stories and testimonials",
                        "offer": "Social proof reinforcement",
                    },
                    {
                        "day": 14,
                        "subject": "Last chance for special pricing",
                        "content": "Final offer with urgency",
                        "offer": "Price increases tomorrow",
                    },
                ],
            },
            "behavioral_upsells": {
                "high_engagement": {
                    "trigger": "High email engagement + website visits",
                    "product": "Video series",
                    "approach": "Personal invitation from author",
                    "timing": "30 days after previous purchase",
                },
                "course_completion": {
                    "trigger": "Audio course completion",
                    "product": "Coaching program application",
                    "approach": "Achievement-based invitation",
                    "timing": "Within 7 days of completion",
                },
            },
        }

        # Cross-Sell Opportunities
        crosssell_opportunities = {
            "complementary_products": {
                "book_buyers": [
                    "Large print journal for notes",
                    "Puzzle solving timer",
                    "Magnifying glass with light",
                    "Ergonomic book stand",
                ],
                "course_students": [
                    "Advanced puzzle collections",
                    "Competition preparation guides",
                    "Teaching materials for sharing skills",
                    "Puzzle creation software",
                ],
            },
            "seasonal_offers": {
                "back_to_school": "Study skills and brain training bundles",
                "holidays": "Gift sets for puzzle lovers",
                "new_year": "Self-improvement and goal setting packages",
                "summer": "Travel-friendly puzzle collections",
            },
        }

        # Personalization Rules
        personalization_rules = {
            "customer_segments": {
                "price_sensitive": {
                    "approach": "Emphasize value and savings",
                    "offers": "Bundle discounts and payment plans",
                    "timing": "Longer consideration periods",
                },
                "quality_focused": {
                    "approach": "Emphasize premium features and benefits",
                    "offers": "Exclusive access and personalization",
                    "timing": "Immediate availability",
                },
                "community_oriented": {
                    "approach": "Emphasize social aspects and connections",
                    "offers": "Group programs and community access",
                    "timing": "Based on community engagement",
                },
            },
            "purchase_history": {
                "single_purchase": "Focus on building relationship and trust",
                "multiple_purchases": "Offer premium and advanced options",
                "high_value": "VIP treatment and exclusive access",
            },
        }

        # Upsell Page Templates
        upsell_templates = {
            "one_time_offer": {
                "headline": "Special One-Time Offer for New Customers",
                "subheadline": "Get the Complete Solving System at 70% Off",
                "elements": [
                    "Countdown timer for urgency",
                    "Value stack with crossed-out prices",
                    "Risk reversal with guarantee",
                    "Social proof from other customers",
                ],
            },
            "email_based": {
                "subject_lines": [
                    "Your next step is ready...",
                    "Join 500+ students who have already upgraded",
                    "Last chance for early bird pricing",
                ],
                "content_structure": [
                    "Congratulate on previous purchase",
                    "Share relevant success story",
                    "Present logical next step",
                    "Include limited-time incentive",
                ],
            },
        }

        # Save upsell automation
        upsell_file = self.output_dir / "upsell_automation.json"
        upsell_data = {
            "upsell_strategy": upsell_strategy,
            "upsell_flows": upsell_flows,
            "crosssell_opportunities": crosssell_opportunities,
            "personalization_rules": personalization_rules,
            "upsell_templates": upsell_templates,
            "success_metrics": [
                "Immediate upsell conversion: 30%",
                "Email upsell conversion: 15%",
                "Customer lifetime value: $150+",
                "Ecosystem completion rate: 40%",
            ],
        }

        with open(upsell_file, "w") as f:
            json.dump(upsell_data, f, indent=2)

        return {"upsell_automation": str(upsell_file)}

    def _implement_conversion_tracking(self) -> Dict:
        """Implement comprehensive conversion tracking"""
        print("  📊 Implementing Conversion Tracking...")

        # Tracking Strategy
        tracking_strategy = {
            "core_principle": "Track every step of the customer journey",
            "attribution_model": "Multi-touch attribution with time decay",
            "data_privacy": "GDPR and CCPA compliant tracking",
        }

        # Tracking Implementation
        tracking_implementation = {
            "google_analytics": {
                "setup": "GA4 with Enhanced Ecommerce",
                "goals": [
                    "Email signup (micro-conversion)",
                    "Book purchase (macro-conversion)",
                    "Upsell purchase (secondary conversion)",
                    "High-value page views (engagement)",
                ],
                "custom_events": [
                    "PDF download",
                    "Video play completion",
                    "Email link clicks",
                    "Upsell page visits",
                ],
            },
            "facebook_pixel": {
                "standard_events": [
                    "ViewContent (landing page)",
                    "AddToCart (checkout initiation)",
                    "Purchase (transaction completion)",
                    "Lead (email signup)",
                ],
                "custom_events": [
                    "DownloadLead (lead magnet download)",
                    "UpsellView (upsell page visit)",
                    "CourseSignup (program enrollment)",
                ],
            },
        }

        # UTM Parameter System
        utm_system = {
            "parameter_structure": {
                "utm_source": ["facebook", "google", "linkedin", "email", "organic"],
                "utm_medium": ["cpc", "social", "email", "referral", "organic"],
                "utm_campaign": ["book_launch", "lead_magnet", "upsell", "retargeting"],
                "utm_content": ["ad_variant", "email_position", "page_element"],
                "utm_term": ["keyword", "audience_segment", "demographic"],
            },
            "tracking_urls": {
                "facebook_ads": "utm_source=facebook&utm_medium=cpc&utm_campaign=book_launch&utm_content=video_ad",
                "email_links": "utm_source=email&utm_medium=email&utm_campaign=newsletter&utm_content=cta_button",
                "linkedin_posts": "utm_source=linkedin&utm_medium=social&utm_campaign=organic_post&utm_content=carousel",
            },
        }

        # Conversion Funnel Tracking
        funnel_tracking = {
            "awareness_stage": {
                "metrics": ["Impressions", "Reach", "Click-through rate"],
                "sources": ["Social media", "Google Ads", "Organic search"],
                "tracking": "UTM parameters and referrer data",
            },
            "interest_stage": {
                "metrics": ["Landing page views", "Time on page", "Scroll depth"],
                "actions": ["Email signup", "Lead magnet download"],
                "tracking": "Google Analytics events and goals",
            },
            "consideration_stage": {
                "metrics": ["Product page views", "Pricing page visits", "FAQ views"],
                "actions": ["Add to cart", "Checkout initiation"],
                "tracking": "Enhanced ecommerce events",
            },
            "purchase_stage": {
                "metrics": ["Conversion rate", "Average order value", "Revenue"],
                "actions": ["Transaction completion", "Thank you page view"],
                "tracking": "Purchase events with transaction IDs",
            },
            "retention_stage": {
                "metrics": [
                    "Upsell conversion",
                    "Email engagement",
                    "Repeat purchases",
                ],
                "actions": ["Additional purchases", "Referrals", "Reviews"],
                "tracking": "Customer lifetime value analysis",
            },
        }

        # Attribution Modeling
        attribution_modeling = {
            "first_touch": "Credit the first interaction for awareness generation",
            "last_touch": "Credit the final interaction before conversion",
            "linear": "Equal credit to all touchpoints in the journey",
            "time_decay": "More credit to recent interactions",
            "position_based": "40% to first and last, 20% distributed among middle",
        }

        # Reporting Dashboard
        reporting_dashboard = {
            "daily_metrics": [
                "Traffic sources and quality",
                "Conversion rates by channel",
                "Revenue and average order value",
                "Email signup and engagement rates",
            ],
            "weekly_analysis": [
                "Customer journey path analysis",
                "Attribution model comparisons",
                "A/B test results and significance",
                "Customer lifetime value trends",
            ],
            "monthly_reviews": [
                "Channel performance and ROI",
                "Customer acquisition cost trends",
                "Funnel optimization opportunities",
                "Predictive analytics and forecasting",
            ],
        }

        # Save conversion tracking
        tracking_file = self.output_dir / "conversion_tracking.json"
        tracking_data = {
            "tracking_strategy": tracking_strategy,
            "tracking_implementation": tracking_implementation,
            "utm_system": utm_system,
            "funnel_tracking": funnel_tracking,
            "attribution_modeling": attribution_modeling,
            "reporting_dashboard": reporting_dashboard,
            "privacy_compliance": [
                "Cookie consent implementation",
                "GDPR data processing agreements",
                "CCPA opt-out mechanisms",
                "Data retention policies",
            ],
        }

        with open(tracking_file, "w") as f:
            json.dump(tracking_data, f, indent=2)

        return {"conversion_tracking": str(tracking_file)}

    def _create_ab_testing(self) -> Dict:
        """Create A/B testing framework"""
        print("  🧪 Creating A/B Testing Framework...")

        # Testing Strategy
        testing_strategy = {
            "core_principle": "Test everything, assume nothing",
            "testing_priorities": [
                "High-impact, low-effort tests first",
                "One test at a time per funnel stage",
                "Statistical significance before decisions",
                "Long-term value over short-term gains",
            ],
        }

        # Test Categories
        test_categories = {
            "landing_page_tests": [
                "Headlines and value propositions",
                "Call-to-action button text and color",
                "Social proof placement and format",
                "Form field requirements and layout",
                "Trust signals and guarantee prominence",
            ],
            "email_tests": [
                "Subject line variations",
                "Send time optimization",
                "Content length and format",
                "Personalization levels",
                "Call-to-action placement",
            ],
            "checkout_tests": [
                "Page layout and element order",
                "Payment options and prominence",
                "Trust badges and security messaging",
                "Pricing display and formatting",
                "Guest vs. account checkout",
            ],
            "upsell_tests": [
                "Offer timing and placement",
                "Pricing and discount strategies",
                "Product bundling options",
                "Urgency and scarcity elements",
                "Value proposition messaging",
            ],
        }

        # Priority Test Queue
        test_queue = {
            "high_priority_tests": [
                {
                    "test_name": "Landing Page Headline",
                    "hypothesis": "Benefit-focused headline will outperform feature-focused",
                    "variants": [
                        "Finally, Crosswords You Can Actually See and Solve",
                        "Large Print Crossword Book with Progressive Difficulty",
                    ],
                    "metric": "Email signup conversion rate",
                    "estimated_impact": "15-25% improvement",
                },
                {
                    "test_name": "CTA Button Color",
                    "hypothesis": "Red button will outperform blue for urgency",
                    "variants": ["Red (#e74c3c)", "Blue (#3498db)"],
                    "metric": "Click-through rate",
                    "estimated_impact": "5-10% improvement",
                },
            ],
            "medium_priority_tests": [
                {
                    "test_name": "Email Subject Lines",
                    "hypothesis": "Curiosity-driven subjects outperform direct benefit",
                    "variants": [
                        "The puzzle mistake 90% of people make",
                        "Improve your crossword solving today",
                    ],
                    "metric": "Email open rate",
                    "estimated_impact": "10-15% improvement",
                }
            ],
        }

        # Testing Methodology
        testing_methodology = {
            "sample_size_calculation": "Use statistical power calculator for 95% confidence",
            "test_duration": "Minimum 1 week, maximum 4 weeks",
            "significance_threshold": "95% confidence level",
            "minimum_sample": "100 conversions per variant",
            "traffic_split": "50/50 for most tests, 90/10 for high-risk tests",
        }

        # Test Documentation
        test_documentation = {
            "test_planning_template": {
                "hypothesis": "Clear prediction of expected outcome",
                "test_design": "Control vs. variant description",
                "success_metrics": "Primary and secondary KPIs",
                "sample_size": "Required visitors for statistical significance",
                "duration": "Planned test length in days",
                "risk_assessment": "Potential downside if variant loses",
            },
            "results_analysis_template": {
                "statistical_significance": "P-value and confidence interval",
                "practical_significance": "Business impact of observed difference",
                "segment_analysis": "Performance by traffic source/device",
                "learnings": "Key insights for future tests",
                "implementation": "Winner implementation timeline",
            },
        }

        # Testing Tools
        testing_tools = {
            "landing_pages": "Unbounce or Leadpages built-in testing",
            "website_elements": "Google Optimize or VWO",
            "email_campaigns": "ConvertKit or ActiveCampaign A/B features",
            "ad_creative": "Facebook Ads Manager split testing",
            "statistical_analysis": "Google Analytics Intelligence or custom calculators",
        }

        # Save A/B testing framework
        testing_file = self.output_dir / "ab_testing_framework.json"
        testing_data = {
            "testing_strategy": testing_strategy,
            "test_categories": test_categories,
            "test_queue": test_queue,
            "testing_methodology": testing_methodology,
            "test_documentation": test_documentation,
            "testing_tools": testing_tools,
            "best_practices": [
                "Test one element at a time",
                "Run tests for full business cycles",
                "Document all tests and results",
                "Share learnings across team",
                "Never stop testing and optimizing",
            ],
        }

        with open(testing_file, "w") as f:
            json.dump(testing_data, f, indent=2)

        return {"ab_testing_framework": str(testing_file)}

    def _build_analytics_dashboard(self) -> Dict:
        """Build comprehensive analytics dashboard"""
        print("  📈 Building Analytics Dashboard...")

        # Dashboard Strategy
        dashboard_strategy = {
            "purpose": "Real-time visibility into funnel performance",
            "user_types": ["Author/owner", "Marketing team", "Technical team"],
            "update_frequency": "Real-time with daily summaries",
        }

        # Key Metrics
        key_metrics = {
            "traffic_metrics": [
                "Unique visitors by source",
                "Page views and session duration",
                "Bounce rate by landing page",
                "Mobile vs desktop performance",
            ],
            "conversion_metrics": [
                "Email signup conversion rate",
                "Purchase conversion rate",
                "Upsell conversion rate",
                "Customer lifetime value",
            ],
            "revenue_metrics": [
                "Daily revenue and trends",
                "Average order value",
                "Revenue per visitor",
                "Monthly recurring revenue",
            ],
            "engagement_metrics": [
                "Email open and click rates",
                "Content consumption patterns",
                "Community participation",
                "Customer satisfaction scores",
            ],
        }

        # Dashboard Layouts
        dashboard_layouts = {
            "executive_summary": {
                "purpose": "High-level overview for decision makers",
                "widgets": [
                    "Revenue today vs. yesterday/last week",
                    "Conversion funnel with current rates",
                    "Top traffic sources and their quality",
                    "Key alerts and action items",
                ],
            },
            "marketing_performance": {
                "purpose": "Detailed marketing metrics for optimization",
                "widgets": [
                    "Channel performance and ROI",
                    "Campaign attribution analysis",
                    "A/B test results and significance",
                    "Customer acquisition cost trends",
                ],
            },
            "customer_journey": {
                "purpose": "Understanding customer behavior and paths",
                "widgets": [
                    "Funnel visualization with drop-off points",
                    "Customer segment performance",
                    "Lifetime value by acquisition source",
                    "Retention and churn analysis",
                ],
            },
        }

        # Automated Alerts
        automated_alerts = {
            "performance_alerts": [
                "Conversion rate drops below 10%",
                "Daily revenue drops 20% vs. 7-day average",
                "Email deliverability issues detected",
                "Website downtime or slow loading",
            ],
            "opportunity_alerts": [
                "High-converting traffic source identified",
                "A/B test reaches statistical significance",
                "Seasonal trend pattern detected",
                "New customer segment emerging",
            ],
            "system_alerts": [
                "Tracking code errors detected",
                "Form submission failures",
                "Payment processing issues",
                "Email automation failures",
            ],
        }

        # Custom Reports
        custom_reports = {
            "weekly_performance": {
                "recipients": ["Author", "Marketing team"],
                "content": [
                    "Traffic and conversion summary",
                    "Revenue and customer acquisition",
                    "Top performing content and campaigns",
                    "Action items for next week",
                ],
            },
            "monthly_analysis": {
                "recipients": ["Management", "Stakeholders"],
                "content": [
                    "Monthly growth metrics and trends",
                    "Customer lifetime value analysis",
                    "Channel ROI and budget recommendations",
                    "Strategic insights and opportunities",
                ],
            },
            "campaign_reports": {
                "recipients": ["Campaign managers"],
                "content": [
                    "Campaign performance vs. goals",
                    "Audience insights and behavior",
                    "Creative performance analysis",
                    "Optimization recommendations",
                ],
            },
        }

        # Technical Implementation
        technical_implementation = {
            "data_sources": [
                "Google Analytics 4",
                "Facebook Ads Manager API",
                "Email platform APIs (ConvertKit)",
                "Payment processor APIs (Stripe)",
                "Custom database queries",
            ],
            "dashboard_platform": "Google Data Studio or Tableau",
            "data_refresh": "Hourly for real-time metrics, daily for reports",
            "access_control": "Role-based permissions by team function",
            "backup_systems": "Automated data backups and redundancy",
        }

        # Save analytics dashboard
        dashboard_file = self.output_dir / "analytics_dashboard.json"
        dashboard_data = {
            "dashboard_strategy": dashboard_strategy,
            "key_metrics": key_metrics,
            "dashboard_layouts": dashboard_layouts,
            "automated_alerts": automated_alerts,
            "custom_reports": custom_reports,
            "technical_implementation": technical_implementation,
            "success_criteria": [
                "All stakeholders can find needed metrics in <30 seconds",
                "Alerts catch issues before significant impact",
                "Data accuracy >99% across all sources",
                "Dashboard loads in <5 seconds",
            ],
        }

        with open(dashboard_file, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        return {"analytics_dashboard": str(dashboard_file)}

    def _create_mobile_optimization(self) -> Dict:
        """Create mobile optimization system"""
        print("  📱 Creating Mobile Optimization...")

        # Mobile Strategy
        mobile_strategy = {
            "core_principle": "Mobile-first design and optimization",
            "target_performance": "3-second load time on 3G networks",
            "user_experience": "Thumb-friendly navigation and interactions",
        }

        # Mobile Conversion Optimization
        mobile_optimization = {
            "design_principles": [
                "Single-column layout for easy scrolling",
                "Large touch targets (minimum 44px)",
                "Readable fonts without zooming (16px+)",
                "Minimal form fields and inputs",
                "Fast-loading images and graphics",
            ],
            "checkout_optimization": [
                "Auto-detect and format phone numbers",
                "One-page checkout process",
                "Mobile payment options (Apple Pay, Google Pay)",
                "Address autocomplete functionality",
                "Large, prominent CTA buttons",
            ],
            "form_optimization": [
                "Email input with proper keyboard",
                "Phone number input with numeric pad",
                "Autofill support for faster completion",
                "Clear error messages and validation",
                "Progress indicators for multi-step forms",
            ],
        }

        # Performance Optimization
        performance_optimization = {
            "page_speed": [
                "Optimize images with WebP format",
                "Minimize CSS and JavaScript",
                "Use CDN for faster content delivery",
                "Implement lazy loading for images",
                "Enable browser caching",
            ],
            "technical_requirements": [
                "Responsive design that scales to any screen",
                "AMP pages for ultra-fast loading",
                "Progressive Web App features",
                "Offline functionality where appropriate",
                "Touch gesture support",
            ],
        }

        # Mobile-Specific Features
        mobile_features = {
            "native_app_integration": [
                "Smart app banners for relevant apps",
                "Deep linking to app content",
                "App download prompts where beneficial",
                "Cross-platform experience consistency",
            ],
            "device_capabilities": [
                "Location services for local offers",
                "Camera access for QR code scanning",
                "Push notifications for engagement",
                "Device orientation optimization",
            ],
        }

        # Testing and Analytics
        mobile_testing = {
            "device_testing": [
                "iPhone (various models and iOS versions)",
                "Android (Samsung, Google, others)",
                "Tablet experiences (iPad, Android tablets)",
                "Different screen sizes and resolutions",
            ],
            "performance_monitoring": [
                "Page load speed by device type",
                "Conversion rates mobile vs desktop",
                "Form completion rates on mobile",
                "User behavior flow analysis",
            ],
            "usability_testing": [
                "Finger-friendly touch targets",
                "Easy navigation without zooming",
                "Readable text and clear CTAs",
                "Smooth scrolling and interactions",
            ],
        }

        # Save mobile optimization
        mobile_file = self.output_dir / "mobile_optimization.json"
        mobile_data = {
            "mobile_strategy": mobile_strategy,
            "mobile_optimization": mobile_optimization,
            "performance_optimization": performance_optimization,
            "mobile_features": mobile_features,
            "mobile_testing": mobile_testing,
            "implementation_checklist": [
                "Implement responsive design framework",
                "Optimize all images for mobile",
                "Test checkout flow on multiple devices",
                "Set up mobile-specific analytics",
                "Configure mobile payment options",
            ],
        }

        with open(mobile_file, "w") as f:
            json.dump(mobile_data, f, indent=2)

        return {"mobile_optimization": str(mobile_file)}


def main():
    """CLI interface for one-click funnel system"""
    import argparse

    parser = argparse.ArgumentParser(
        description="One-Click Funnel System for KindleMint"
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

    # Run one-click funnel system
    funnel_system = OneClickFunnelSystem(book_config, artifacts)
    results = funnel_system.build_complete_funnel()

    print(f"\n🖱️ One-Click Funnel System built successfully!")
    print(f"📁 Output directory: {funnel_system.output_dir}")

    for asset_type, file_path in results.items():
        print(f"   • {asset_type}: {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
