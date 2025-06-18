"""
Brand Builder & Funnel Agent - Direct Customer Relationship Engine
Creates branded websites and email capture systems for long-term customer value.

BUSINESS IMPACT: Transforms one-time buyers into lifetime customers
STRATEGY: Book → Website → Email → Direct Marketing → Repeat Sales
"""
import json
import logging
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BrandWebsite:
    """Brand website configuration and content."""
    url: str
    title: str
    description: str
    email_offer: str
    download_link: str
    brand_colors: Dict[str, str]
    call_to_action: str
    social_proof: str
    platform: str

@dataclass
class EmailFunnel:
    """Email marketing funnel configuration."""
    provider: str
    list_name: str
    welcome_email: str
    nurture_sequence: List[Dict[str, str]]
    conversion_emails: List[Dict[str, str]]
    automation_trigger: str

@dataclass
class BrandAssets:
    """Complete brand assets and digital products."""
    logo_prompt: str
    bonus_content: Dict[str, Any]
    email_templates: List[str]
    social_media_kit: Dict[str, str]
    brand_guidelines: Dict[str, str]

class BrandBuilder:
    """Intelligent brand building and funnel creation system."""
    
    def __init__(self):
        """Initialize brand builder."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            logger.error("❌ OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY is required for Brand Builder functionality")
        
        # Platform configurations
        self.website_platforms = {
            "carrd": {"limit": "3 sites free", "custom_domain": "premium"},
            "netlify": {"limit": "unlimited", "custom_domain": "free"},
            "github_pages": {"limit": "unlimited", "custom_domain": "free"}
        }
        
        self.email_providers = {
            "convertkit": {"free_limit": 1000, "automation": True},
            "mailchimp": {"free_limit": 2000, "automation": "limited"},
            "beehiiv": {"free_limit": 2500, "automation": True}
        }
    
    async def build_complete_brand_system(self, book_series: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build complete brand system with website and email funnel.
        
        Args:
            book_series: Series information from Series Publisher
            
        Returns:
            Complete brand system configuration
        """
        try:
            series_name = book_series['series_name']
            series_brand = book_series['series_brand']
            micro_niche = book_series['micro_niche']
            
            logger.info(f"🏗️ BRAND BUILDER ACTIVATED for: {series_brand}")
            
            # Step 1: Create brand identity and assets
            brand_assets = await self._create_brand_assets(series_brand, micro_niche)
            
            # Step 2: Design and deploy brand website
            brand_website = await self._create_brand_website(book_series, brand_assets)
            
            # Step 3: Create bonus digital product
            bonus_product = await self._create_bonus_digital_product(micro_niche, series_name)
            
            # Step 4: Set up email capture and funnel
            email_funnel = await self._create_email_funnel(series_brand, micro_niche, bonus_product)
            
            # Step 5: Generate integration code for books
            book_integration = await self._create_book_integration_content(brand_website, bonus_product)
            
            # Step 6: Create launch automation
            launch_automation = await self._create_launch_automation(book_series, brand_website, email_funnel)
            
            brand_system = {
                'brand_name': series_brand,
                'website': {
                    'url': brand_website.url,
                    'title': brand_website.title,
                    'platform': brand_website.platform,
                    'email_offer': brand_website.email_offer
                },
                'email_funnel': {
                    'provider': email_funnel.provider,
                    'list_name': email_funnel.list_name,
                    'automation_sequences': len(email_funnel.nurture_sequence)
                },
                'bonus_product': bonus_product,
                'book_integration': book_integration,
                'launch_automation': launch_automation,
                'brand_assets': brand_assets.__dict__,
                'estimated_setup_time': '2-3 hours',
                'monthly_cost': '$0 (free tiers)',
                'expected_email_capture_rate': '15-25%'
            }
            
            logger.info(f"✅ Brand system created: {brand_website.url}")
            logger.info(f"   Email Provider: {email_funnel.provider}")
            logger.info(f"   Bonus Offer: {bonus_product['title']}")
            
            return brand_system
            
        except Exception as e:
            logger.error(f"❌ Brand system creation failed: {str(e)}")
            raise
    
    async def _create_brand_assets(self, series_brand: str, micro_niche: str) -> BrandAssets:
        """Create comprehensive brand assets."""
        try:
            from openai import OpenAI
            
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Create comprehensive brand assets for: {series_brand}
            Niche: {micro_niche}
            
            Generate:
            1. Logo Design Prompt (for AI image generation)
            2. Brand Color Palette (3-4 colors with hex codes)
            3. Typography Recommendations
            4. Brand Voice & Tone Guidelines
            5. Social Media Bio Template
            6. Brand Story (2-3 sentences)
            7. Value Proposition Statement
            
            Requirements:
            - Professional and trustworthy
            - Appeals to target audience
            - Consistent across all platforms
            - Memorable and distinctive
            - Suitable for book covers and website
            
            Format as JSON:
            {{
                "logo_prompt": "detailed prompt for AI logo generation",
                "color_palette": {{
                    "primary": "#hexcode",
                    "secondary": "#hexcode",
                    "accent": "#hexcode",
                    "neutral": "#hexcode"
                }},
                "typography": {{
                    "heading_font": "font recommendation",
                    "body_font": "font recommendation"
                }},
                "brand_voice": {{
                    "tone": "description of tone",
                    "personality": "brand personality traits",
                    "messaging_style": "how to communicate"
                }},
                "social_media_bio": "engaging bio template",
                "brand_story": "compelling 2-3 sentence story",
                "value_proposition": "clear value statement"
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            
            brand_data = json.loads(content)
            
            # Create bonus content specifications
            bonus_content = await self._design_bonus_content(micro_niche)
            
            # Generate email templates
            email_templates = await self._create_email_templates(series_brand, micro_niche)
            
            # Create social media kit
            social_kit = self._create_social_media_kit(brand_data)
            
            return BrandAssets(
                logo_prompt=brand_data['logo_prompt'],
                bonus_content=bonus_content,
                email_templates=email_templates,
                social_media_kit=social_kit,
                brand_guidelines=brand_data
            )
            
        except Exception as e:
            logger.warning(f"AI brand assets creation failed: {e}")
            return self._fallback_brand_assets(series_brand, micro_niche)
    
    def _fallback_brand_assets(self, series_brand: str, micro_niche: str) -> BrandAssets:
        """Fallback brand assets if AI generation fails."""
        return BrandAssets(
            logo_prompt=f"Professional logo for {series_brand}, clean design, {micro_niche} theme, modern typography",
            bonus_content={"type": "digital_download", "title": "Bonus Content Pack"},
            email_templates=["Welcome", "Bonus Delivery", "New Release Notification"],
            social_media_kit={"bio": f"Quality {micro_niche} content creator", "hashtags": ["#books", "#quality"]},
            brand_guidelines={
                "color_palette": {"primary": "#2C3E50", "secondary": "#3498DB"},
                "brand_voice": {"tone": "professional", "personality": "helpful"}
            }
        )
    
    async def _create_brand_website(self, book_series: Dict[str, Any], brand_assets: BrandAssets) -> BrandWebsite:
        """Create and configure brand website."""
        try:
            series_brand = book_series['series_brand']
            series_name = book_series['series_name']
            email_offer = book_series.get('email_offer', 'Exclusive Bonus Content')
            
            # Generate website content
            website_content = await self._generate_website_content(book_series, brand_assets)
            
            # Choose platform (start with Carrd for simplicity)
            platform = "carrd.co"
            
            # Generate website URL
            brand_slug = series_brand.lower().replace(' ', '-').replace('&', 'and')
            website_url = f"https://{brand_slug}.carrd.co"
            
            return BrandWebsite(
                url=website_url,
                title=website_content['title'],
                description=website_content['description'],
                email_offer=email_offer,
                download_link=website_content['download_section'],
                brand_colors=brand_assets.brand_guidelines.get('color_palette', {}),
                call_to_action=website_content['cta'],
                social_proof=website_content['social_proof'],
                platform=platform
            )
            
        except Exception as e:
            logger.error(f"Website creation failed: {e}")
            # Return basic website config
            return BrandWebsite(
                url="https://example.carrd.co",
                title=book_series['series_brand'],
                description=f"Quality {book_series['micro_niche']} content",
                email_offer=book_series.get('email_offer', 'Bonus Content'),
                download_link="/download",
                brand_colors={"primary": "#2C3E50"},
                call_to_action="Get Your Free Bonus!",
                social_proof="Trusted by readers worldwide",
                platform="carrd.co"
            )
    
    async def _generate_website_content(self, book_series: Dict[str, Any], brand_assets: BrandAssets) -> Dict[str, Any]:
        """Generate compelling website content."""
        try:
            from openai import OpenAI
            
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            series_brand = book_series['series_brand']
            series_name = book_series['series_name']
            micro_niche = book_series['micro_niche']
            email_offer = book_series.get('email_offer', 'Exclusive Bonus Content')
            
            prompt = f"""
            Create compelling website content for: {series_brand}
            Book Series: {series_name}
            Niche: {micro_niche}
            Email Offer: {email_offer}
            
            Generate a single-page website with:
            1. Compelling headline
            2. Clear value proposition
            3. Book series showcase
            4. Email capture section with benefit-focused copy
            5. About section
            6. Social proof elements
            7. Strong call-to-action
            
            Requirements:
            - Convert visitors to email subscribers
            - Professional and trustworthy tone
            - Focus on value and benefits
            - Clear next steps
            - Mobile-friendly copy
            
            Format as JSON:
            {{
                "title": "compelling page title",
                "headline": "attention-grabbing headline",
                "description": "clear value proposition",
                "series_showcase": "brief series description",
                "email_capture_section": "benefit-focused email capture copy",
                "about_section": "credible about content",
                "social_proof": "trust-building elements",
                "cta": "compelling call-to-action",
                "download_section": "bonus content description"
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            
            website_content = json.loads(content)
            return website_content
            
        except Exception as e:
            logger.warning(f"Website content generation failed: {e}")
            return self._fallback_website_content(book_series)
    
    def _fallback_website_content(self, book_series: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback website content if AI generation fails."""
        series_brand = book_series['series_brand']
        series_name = book_series['series_name']
        
        return {
            "title": f"{series_brand} - Quality Content",
            "headline": f"Discover the {series_name}",
            "description": f"Professional {book_series['micro_niche']} content for every level",
            "series_showcase": f"Complete {series_name} with progressive difficulty",
            "email_capture_section": f"Get exclusive bonus content delivered to your inbox",
            "about_section": f"{series_brand} creates quality educational content",
            "social_proof": "Trusted by readers who value quality",
            "cta": "Get Your Free Bonus Now!",
            "download_section": "Exclusive bonus content available after signup"
        }
    
    async def _create_bonus_digital_product(self, micro_niche: str, series_name: str) -> Dict[str, Any]:
        """Create valuable bonus digital product for email capture."""
        try:
            from openai import OpenAI
            
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Design a valuable bonus digital product for: {micro_niche}
            Series: {series_name}
            
            Create something that:
            1. Provides immediate value
            2. Is easy to create and deliver
            3. Complements the main book series
            4. Makes people want to buy the books
            5. Can be automated
            
            Suggest:
            - Product type and format
            - Specific content ideas
            - Number of pages/items
            - Delivery method
            - Creation requirements
            
            Format as JSON:
            {{
                "title": "compelling product title",
                "description": "what it contains",
                "format": "PDF/digital/printable/etc",
                "content_outline": ["item 1", "item 2", "item 3"],
                "page_count": 10,
                "creation_method": "how to create it",
                "delivery_method": "how to deliver it",
                "value_proposition": "why it's valuable",
                "time_to_create": "estimated creation time"
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            
            bonus_product = json.loads(content)
            return bonus_product
            
        except Exception as e:
            logger.warning(f"Bonus product creation failed: {e}")
            return self._fallback_bonus_product(micro_niche)
    
    def _fallback_bonus_product(self, micro_niche: str) -> Dict[str, Any]:
        """Fallback bonus product if AI generation fails."""
        content_type = self._determine_content_type(micro_niche)
        
        if "coloring" in content_type:
            return {
                "title": "5 Exclusive Bonus Coloring Pages",
                "description": "Beautiful designs not found in any book",
                "format": "Printable PDF",
                "content_outline": ["Design 1", "Design 2", "Design 3", "Design 4", "Design 5"],
                "page_count": 5,
                "creation_method": "AI-generated designs or simple templates",
                "delivery_method": "Email PDF attachment",
                "value_proposition": "Exclusive content for subscribers only",
                "time_to_create": "2-3 hours"
            }
        else:
            return {
                "title": "Exclusive Bonus Content Pack",
                "description": "Additional content to complement the book series",
                "format": "Digital Download",
                "content_outline": ["Bonus item 1", "Bonus item 2", "Bonus item 3"],
                "page_count": 10,
                "creation_method": "Content creation using existing tools",
                "delivery_method": "Download link via email",
                "value_proposition": "Extra value for subscribers",
                "time_to_create": "3-4 hours"
            }
    
    def _determine_content_type(self, micro_niche: str) -> str:
        """Determine content type from micro-niche."""
        niche_lower = micro_niche.lower()
        
        if "coloring" in niche_lower:
            return "coloring"
        elif "puzzle" in niche_lower:
            return "puzzle"
        elif "journal" in niche_lower:
            return "journal"
        elif "activity" in niche_lower:
            return "activity"
        else:
            return "general"
    
    async def _create_email_funnel(self, series_brand: str, micro_niche: str, bonus_product: Dict[str, Any]) -> EmailFunnel:
        """Create automated email marketing funnel."""
        try:
            # Choose email provider (start with ConvertKit for automation features)
            provider = "ConvertKit"
            
            # Create list name
            list_name = f"{series_brand} Subscribers"
            
            # Generate welcome email
            welcome_email = await self._generate_welcome_email(series_brand, bonus_product)
            
            # Create nurture sequence
            nurture_sequence = await self._generate_nurture_sequence(series_brand, micro_niche)
            
            # Create conversion emails
            conversion_emails = await self._generate_conversion_emails(series_brand, micro_niche)
            
            return EmailFunnel(
                provider=provider,
                list_name=list_name,
                welcome_email=welcome_email,
                nurture_sequence=nurture_sequence,
                conversion_emails=conversion_emails,
                automation_trigger="email_signup"
            )
            
        except Exception as e:
            logger.error(f"Email funnel creation failed: {e}")
            return self._fallback_email_funnel(series_brand, bonus_product)
    
    async def _generate_welcome_email(self, series_brand: str, bonus_product: Dict[str, Any]) -> str:
        """Generate welcome email template."""
        welcome_email = f"""
Subject: Welcome! Your {bonus_product['title']} is here 🎁

Hi there!

Welcome to the {series_brand} community!

I'm thrilled you've joined us. As promised, here's your {bonus_product['title']}:

👉 [DOWNLOAD LINK]

This exclusive content is my way of saying thank you for trusting me with your inbox.

What's next?
- Download your bonus content
- Keep an eye out for new releases
- Reply and let me know what you think!

I'm here to provide you with the highest quality content, and I'd love to hear from you.

Happy reading!

Best regards,
{series_brand} Team

P.S. Make sure to add this email to your contacts so you never miss an update!
        """.strip()
        
        return welcome_email
    
    async def _generate_nurture_sequence(self, series_brand: str, micro_niche: str) -> List[Dict[str, str]]:
        """Generate nurture email sequence."""
        sequence = [
            {
                "day": 3,
                "subject": f"How are you enjoying your {micro_niche} content?",
                "content": f"I hope you're loving the bonus content! Here's a quick tip..."
            },
            {
                "day": 7,
                "subject": "Behind the scenes at {series_brand}",
                "content": f"I wanted to share the story of how {series_brand} started..."
            },
            {
                "day": 14,
                "subject": "New release announcement!",
                "content": f"Exciting news! A new volume in our {micro_niche} series is coming..."
            }
        ]
        
        return sequence
    
    async def _generate_conversion_emails(self, series_brand: str, micro_niche: str) -> List[Dict[str, str]]:
        """Generate conversion-focused emails."""
        conversion_emails = [
            {
                "trigger": "new_book_release",
                "subject": f"🚨 New {micro_niche} book is live!",
                "content": f"The latest volume in our {series_brand} series is now available..."
            },
            {
                "trigger": "subscriber_milestone",
                "subject": "Special offer just for you",
                "content": f"As a valued {series_brand} subscriber, you get early access..."
            }
        ]
        
        return conversion_emails
    
    def _fallback_email_funnel(self, series_brand: str, bonus_product: Dict[str, Any]) -> EmailFunnel:
        """Fallback email funnel if generation fails."""
        return EmailFunnel(
            provider="ConvertKit",
            list_name=f"{series_brand} List",
            welcome_email=f"Welcome! Here's your {bonus_product['title']}",
            nurture_sequence=[{"day": 7, "subject": "How's it going?", "content": "Hope you're enjoying the content!"}],
            conversion_emails=[{"trigger": "new_release", "subject": "New book available", "content": "Check out our latest release"}],
            automation_trigger="signup"
        )
    
    async def _design_bonus_content(self, micro_niche: str) -> Dict[str, Any]:
        """Design specific bonus content based on niche."""
        content_type = self._determine_content_type(micro_niche)
        
        bonus_designs = {
            "coloring": {
                "type": "printable_pages",
                "count": 5,
                "themes": ["exclusive designs", "bonus patterns", "special themes"],
                "format": "high-res PDF"
            },
            "puzzle": {
                "type": "puzzle_pack",
                "count": 10,
                "themes": ["bonus puzzles", "different difficulty", "special themes"],
                "format": "printable PDF"
            },
            "journal": {
                "type": "templates",
                "count": 3,
                "themes": ["planning templates", "tracking sheets", "reflection guides"],
                "format": "editable PDF"
            },
            "activity": {
                "type": "worksheets",
                "count": 8,
                "themes": ["bonus activities", "skill builders", "fun exercises"],
                "format": "printable PDF"
            }
        }
        
        return bonus_designs.get(content_type, bonus_designs["coloring"])
    
    async def _create_email_templates(self, series_brand: str, micro_niche: str) -> List[str]:
        """Create email template library."""
        templates = [
            "Welcome Email with Bonus Delivery",
            "New Release Announcement",
            "Subscriber-Only Special Offer",
            "Behind the Scenes Content",
            "Customer Success Story",
            "Re-engagement Campaign",
            "Holiday/Seasonal Promotion"
        ]
        
        return templates
    
    def _create_social_media_kit(self, brand_data: Dict[str, Any]) -> Dict[str, str]:
        """Create social media marketing kit."""
        return {
            "bio_template": brand_data.get('social_media_bio', 'Quality content creator'),
            "hashtag_strategy": "#books #quality #educational #learning",
            "post_templates": "New release, Behind scenes, Customer features",
            "visual_guidelines": "Use brand colors, consistent fonts, professional imagery"
        }
    
    async def _create_book_integration_content(self, website: BrandWebsite, bonus_product: Dict[str, Any]) -> Dict[str, str]:
        """Create content for book back matter integration."""
        integration_content = {
            "back_matter_cta": f"""
🎁 GET EXCLUSIVE BONUS CONTENT!

Visit: {website.url}
Get your FREE {bonus_product['title']}

Join our community of readers and get:
• Exclusive bonus content
• Early access to new releases  
• Special subscriber-only offers

👉 {website.url}
            """.strip(),
            
            "book_description_addon": f"Includes link to exclusive bonus content at {website.url}",
            
            "author_bio_addon": f"Get exclusive bonus content at {website.url}",
            
            "qr_code_text": f"Scan for bonus content: {website.url}"
        }
        
        return integration_content
    
    async def _create_launch_automation(self, book_series: Dict[str, Any], website: BrandWebsite, email_funnel: EmailFunnel) -> Dict[str, Any]:
        """Create automated launch sequence."""
        automation = {
            "website_setup": {
                "platform": website.platform,
                "template": "single_page_conversion",
                "setup_time": "30-60 minutes",
                "cost": "$0 (free tier)"
            },
            "email_setup": {
                "provider": email_funnel.provider,
                "automation_sequences": len(email_funnel.nurture_sequence),
                "setup_time": "60-90 minutes",
                "cost": "$0 (free tier up to limits)"
            },
            "integration_steps": [
                "1. Set up website on chosen platform",
                "2. Create email list and automation",
                "3. Connect website form to email provider",
                "4. Upload bonus content for delivery",
                "5. Test complete funnel",
                "6. Add back matter to all books",
                "7. Monitor and optimize conversion rates"
            ],
            "success_metrics": {
                "email_capture_rate": "15-25% target",
                "email_open_rate": "25-35% target",
                "conversion_to_purchase": "5-10% target"
            }
        }
        
        return automation

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for brand building.
    """
    try:
        logger.info("🏗️ BRAND BUILDER ACTIVATED")
        
        # Get book series information
        book_series = event.get('book_series')
        if not book_series:
            raise ValueError("No book series information provided")
        
        # Initialize brand builder
        builder = BrandBuilder()
        
        # Build complete brand system
        brand_system = asyncio.run(builder.build_complete_brand_system(book_series))
        
        logger.info(f"✅ Brand system created: {brand_system['website']['url']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'brand_system': brand_system,
                'next_action': 'implement_brand_setup'
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Brand building failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Brand building failed: {str(e)}'
            })
        }

if __name__ == "__main__":
    # Test brand builder
    test_series = {
        'series_name': 'Large Print Crossword Masters',
        'series_brand': 'Senior Puzzle Studio',
        'micro_niche': 'Large print crossword puzzles for seniors',
        'email_offer': '5 Exclusive Bonus Puzzles'
    }
    
    import asyncio
    builder = BrandBuilder()
    brand_system = asyncio.run(builder.build_complete_brand_system(test_series))
    
    print(f"\n🏗️ BRAND SYSTEM CREATED")
    print(f"Website: {brand_system['website']['url']}")
    print(f"Email Provider: {brand_system['email_funnel']['provider']}")
    print(f"Bonus Product: {brand_system['bonus_product']['title']}")
    print(f"Setup Time: {brand_system['estimated_setup_time']}")
    print(f"Monthly Cost: {brand_system['monthly_cost']}")
    print(f"Expected Capture Rate: {brand_system['expected_email_capture_rate']}")