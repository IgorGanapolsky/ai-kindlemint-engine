"""
Series Publisher Agent - Multi-Book Series Creation Engine
Transforms single book publishing into profitable series creation with consistent branding.

BUSINESS IMPACT: Multiplies profit per customer through series publishing
STRATEGY: Volume 1 → Customer buys → Volume 2, 3, 4, 5 → 5x revenue per customer
"""
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SeriesBook:
    """Individual book within a series."""
    volume_number: int
    title: str
    subtitle: str
    unique_content_focus: str
    keywords: List[str]
    target_length: str
    book_id: str

@dataclass
class BookSeries:
    """Complete book series with branding and cross-promotion."""
    series_name: str
    series_brand: str
    micro_niche: str
    total_volumes: int
    books: List[SeriesBook]
    brand_colors: Dict[str, str]
    author_persona: str
    website_url: str
    email_capture_offer: str
    series_description: str

class SeriesPublisher:
    """Intelligent series creation and publishing system."""
    
    def __init__(self):
        """Initialize series publisher."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Series strategy configurations
        self.optimal_series_length = 5  # 5 books per series for maximum impact
        self.volume_spacing_days = 14  # Release new volume every 2 weeks
        
        # Content type specifications
        self.series_content_types = {
            "coloring": {"pages": 50, "type": "illustrated", "difficulty_progression": True},
            "puzzle": {"pages": 80, "type": "interactive", "difficulty_progression": True},
            "journal": {"pages": 120, "type": "prompted", "difficulty_progression": False},
            "activity": {"pages": 60, "type": "mixed", "difficulty_progression": True},
            "guide": {"pages": 100, "type": "educational", "difficulty_progression": False}
        }
    
    async def create_book_series(self, niche_opportunity: Dict[str, Any]) -> BookSeries:
        """
        Create a complete book series for approved niche opportunity.
        
        Args:
            niche_opportunity: Approved niche from Market Intelligence
            
        Returns:
            Complete BookSeries with all volumes planned
        """
        try:
            micro_niche = niche_opportunity['micro_niche']
            category = niche_opportunity.get('category', 'General')
            
            logger.info(f"📚 SERIES PUBLISHER ACTIVATED for: {micro_niche}")
            
            # Step 1: Generate series branding
            series_branding = await self._create_series_branding(micro_niche, category)
            
            # Step 2: Plan series structure
            series_structure = await self._plan_series_structure(micro_niche, category)
            
            # Step 3: Create individual book plans
            series_books = await self._create_series_books(micro_niche, series_structure)
            
            # Step 4: Generate cross-promotion strategy
            cross_promotion = await self._create_cross_promotion_strategy(series_books)
            
            # Step 5: Plan brand website and email capture
            brand_strategy = await self._create_brand_strategy(micro_niche, series_branding)
            
            # Assemble complete series
            book_series = BookSeries(
                series_name=series_branding['series_name'],
                series_brand=series_branding['brand_name'],
                micro_niche=micro_niche,
                total_volumes=len(series_books),
                books=series_books,
                brand_colors=series_branding['color_scheme'],
                author_persona=series_branding['author_persona'],
                website_url=brand_strategy['website_url'],
                email_capture_offer=brand_strategy['email_offer'],
                series_description=series_structure['series_description']
            )
            
            logger.info(f"✅ Series created: {book_series.series_name} ({book_series.total_volumes} volumes)")
            logger.info(f"   Brand: {book_series.series_brand}")
            logger.info(f"   Website: {book_series.website_url}")
            
            return book_series
            
        except Exception as e:
            logger.error(f"❌ Series creation failed: {str(e)}")
            raise
    
    async def _create_series_branding(self, micro_niche: str, category: str) -> Dict[str, Any]:
        """Create cohesive branding for the book series."""
        try:
            from openai import OpenAI
            
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Create compelling branding for a book series in this micro-niche: {micro_niche}
            Category: {category}
            
            Generate:
            1. Series Name (brandable, memorable, 2-4 words)
            2. Brand Name (author/publisher brand for this niche)
            3. Author Persona (name and brief background)
            4. Color Scheme (3 colors that work for covers)
            5. Brand Personality (tone and style)
            6. Tagline (what the brand represents)
            
            Requirements:
            - Professional and trustworthy
            - Appeals to target audience
            - Easy to remember and spell
            - Works across multiple volumes
            - Suggests quality and expertise
            
            Format as JSON:
            {{
                "series_name": "series name",
                "brand_name": "brand name",
                "author_persona": {{
                    "name": "author name",
                    "background": "brief credible background",
                    "expertise": "why they're qualified"
                }},
                "color_scheme": {{
                    "primary": "#hexcolor",
                    "secondary": "#hexcolor", 
                    "accent": "#hexcolor"
                }},
                "brand_personality": "tone and style description",
                "tagline": "compelling tagline"
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
            
            branding = json.loads(content)
            return branding
            
        except Exception as e:
            logger.warning(f"AI branding generation failed: {e}")
            return self._fallback_branding(micro_niche)
    
    def _fallback_branding(self, micro_niche: str) -> Dict[str, Any]:
        """Fallback branding if AI generation fails."""
        # Extract key theme from micro-niche
        words = micro_niche.split()
        key_theme = words[0].title()
        
        return {
            "series_name": f"{key_theme} Masters Series",
            "brand_name": f"{key_theme} Studio",
            "author_persona": {
                "name": "Creative Studio Team",
                "background": f"Expert creators specializing in {micro_niche}",
                "expertise": "Years of experience in educational content creation"
            },
            "color_scheme": {
                "primary": "#2C3E50",
                "secondary": "#3498DB",
                "accent": "#E74C3C"
            },
            "brand_personality": "Professional, educational, engaging",
            "tagline": f"Quality {key_theme} Content for Everyone"
        }
    
    async def _plan_series_structure(self, micro_niche: str, category: str) -> Dict[str, Any]:
        """Plan the overall structure and progression of the series."""
        try:
            from openai import OpenAI
            
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            Plan a profitable 5-book series structure for: {micro_niche}
            Category: {category}
            
            Create a logical progression that:
            1. Starts with beginner-friendly Volume 1
            2. Gradually increases in complexity/variety
            3. Each volume offers unique value
            4. Encourages readers to buy the next volume
            5. Works well for the target audience
            
            For each volume, specify:
            - Volume focus/theme
            - Unique selling point
            - How it builds on previous volumes
            - Target difficulty level
            - Page count estimate
            
            Also provide:
            - Overall series description
            - Why someone would want all 5 volumes
            - Cross-promotion strategy
            
            Format as JSON:
            {{
                "series_description": "compelling overall description",
                "volume_progression": [
                    {{
                        "volume": 1,
                        "focus": "specific focus",
                        "unique_value": "what makes this volume special",
                        "difficulty": "Beginner/Intermediate/Advanced",
                        "page_estimate": 50,
                        "hook": "reason to buy next volume"
                    }}
                ],
                "series_value_proposition": "why buy all volumes",
                "content_type": "coloring/puzzle/journal/activity/guide"
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
            
            structure = json.loads(content)
            return structure
            
        except Exception as e:
            logger.warning(f"AI series planning failed: {e}")
            return self._fallback_series_structure(micro_niche)
    
    def _fallback_series_structure(self, micro_niche: str) -> Dict[str, Any]:
        """Fallback series structure if AI planning fails."""
        return {
            "series_description": f"Complete {micro_niche} series with progressive difficulty and variety",
            "volume_progression": [
                {
                    "volume": 1,
                    "focus": "Introduction and basics",
                    "unique_value": "Perfect starting point",
                    "difficulty": "Beginner",
                    "page_estimate": 50,
                    "hook": "More challenging content in Volume 2"
                },
                {
                    "volume": 2, 
                    "focus": "Intermediate level content",
                    "unique_value": "Builds on Volume 1 skills",
                    "difficulty": "Intermediate",
                    "page_estimate": 60,
                    "hook": "Advanced techniques in Volume 3"
                },
                {
                    "volume": 3,
                    "focus": "Advanced content",
                    "unique_value": "Expert-level challenges",
                    "difficulty": "Advanced", 
                    "page_estimate": 70,
                    "hook": "Special themes in Volume 4"
                },
                {
                    "volume": 4,
                    "focus": "Special themed content",
                    "unique_value": "Unique themed approach",
                    "difficulty": "Intermediate",
                    "page_estimate": 60,
                    "hook": "Ultimate collection in Volume 5"
                },
                {
                    "volume": 5,
                    "focus": "Ultimate collection",
                    "unique_value": "Best of the entire series",
                    "difficulty": "Mixed",
                    "page_estimate": 80,
                    "hook": "Complete mastery achieved"
                }
            ],
            "series_value_proposition": "Complete progression from beginner to expert with unique content in each volume",
            "content_type": "mixed"
        }
    
    async def _create_series_books(self, micro_niche: str, series_structure: Dict[str, Any]) -> List[SeriesBook]:
        """Create detailed plans for each book in the series."""
        try:
            series_books = []
            
            for volume_plan in series_structure['volume_progression']:
                # Generate unique book ID
                book_id = f"series_{uuid.uuid4().hex[:8]}"
                
                # Create volume title
                volume_num = volume_plan['volume']
                base_title = micro_niche.title()
                volume_title = f"{base_title} - Volume {volume_num}"
                
                # Generate volume-specific subtitle
                subtitle = f"{volume_plan['focus'].title()} | {volume_plan['difficulty']} Level"
                
                # Extract keywords for this volume
                volume_keywords = self._generate_volume_keywords(micro_niche, volume_plan)
                
                # Determine target length
                target_length = f"{volume_plan['page_estimate']} pages"
                
                series_book = SeriesBook(
                    volume_number=volume_num,
                    title=volume_title,
                    subtitle=subtitle,
                    unique_content_focus=volume_plan['focus'],
                    keywords=volume_keywords,
                    target_length=target_length,
                    book_id=book_id
                )
                
                series_books.append(series_book)
            
            return series_books
            
        except Exception as e:
            logger.error(f"Series books creation failed: {e}")
            return []
    
    def _generate_volume_keywords(self, micro_niche: str, volume_plan: Dict[str, Any]) -> List[str]:
        """Generate specific keywords for each volume."""
        # Base keywords from micro-niche
        base_keywords = micro_niche.lower().split()
        
        # Add volume-specific keywords
        volume_keywords = base_keywords.copy()
        
        # Add difficulty level
        difficulty = volume_plan['difficulty'].lower()
        if difficulty not in volume_keywords:
            volume_keywords.append(difficulty)
        
        # Add volume number
        volume_keywords.append(f"volume {volume_plan['volume']}")
        
        # Add focus area keywords
        focus_words = volume_plan['focus'].lower().split()
        for word in focus_words:
            if word not in volume_keywords and len(word) > 3:
                volume_keywords.append(word)
        
        # Limit to 7 keywords for KDP
        return volume_keywords[:7]
    
    async def _create_cross_promotion_strategy(self, series_books: List[SeriesBook]) -> Dict[str, Any]:
        """Create cross-promotion strategy for the series."""
        try:
            # Generate "Also in this series" content for each book
            cross_promotion = {}
            
            for book in series_books:
                other_books = [b for b in series_books if b.volume_number != book.volume_number]
                
                # Create promotion text for this book's back matter
                promo_text = "📚 ALSO IN THIS SERIES:\n\n"
                
                for other_book in sorted(other_books, key=lambda x: x.volume_number):
                    promo_text += f"• {other_book.title}\n"
                    promo_text += f"  {other_book.unique_content_focus.title()}\n"
                    promo_text += f"  Search: '{other_book.keywords[0]}' on Amazon\n\n"
                
                promo_text += "🎯 Collect the complete series for the ultimate experience!\n"
                promo_text += "⭐ Leave a review and help others discover quality content!"
                
                cross_promotion[book.book_id] = {
                    "back_matter_text": promo_text,
                    "related_volumes": [b.book_id for b in other_books],
                    "next_volume": None,
                    "previous_volume": None
                }
                
                # Set next/previous volume relationships
                if book.volume_number > 1:
                    prev_book = next((b for b in series_books if b.volume_number == book.volume_number - 1), None)
                    if prev_book:
                        cross_promotion[book.book_id]["previous_volume"] = prev_book.book_id
                
                if book.volume_number < len(series_books):
                    next_book = next((b for b in series_books if b.volume_number == book.volume_number + 1), None)
                    if next_book:
                        cross_promotion[book.book_id]["next_volume"] = next_book.book_id
            
            return cross_promotion
            
        except Exception as e:
            logger.error(f"Cross-promotion strategy creation failed: {e}")
            return {}
    
    async def _create_brand_strategy(self, micro_niche: str, series_branding: Dict[str, Any]) -> Dict[str, Any]:
        """Create brand website and email capture strategy."""
        try:
            brand_name = series_branding.get('brand_name', 'Creative Studio')
            
            # Generate website URL (using free platform)
            website_slug = brand_name.lower().replace(' ', '-').replace('&', 'and')
            website_url = f"https://{website_slug}.carrd.co"
            
            # Create email capture offer
            content_type = self._determine_content_type(micro_niche)
            
            if "coloring" in content_type:
                email_offer = "5 Exclusive Bonus Coloring Pages"
            elif "puzzle" in content_type:
                email_offer = "Bonus Puzzle Pack (10 Extra Puzzles)"
            elif "journal" in content_type:
                email_offer = "Printable Planning Templates"
            elif "activity" in content_type:
                email_offer = "Bonus Activity Worksheets"
            else:
                email_offer = "Exclusive Digital Bonus Content"
            
            return {
                "website_url": website_url,
                "email_offer": email_offer,
                "brand_value_proposition": f"Quality {micro_niche} content with exclusive bonuses",
                "call_to_action": f"Get your FREE {email_offer}!",
                "platform": "Carrd.co (free tier)",
                "email_service": "ConvertKit or Mailchimp (free tier)"
            }
            
        except Exception as e:
            logger.error(f"Brand strategy creation failed: {e}")
            return {
                "website_url": "https://example.carrd.co",
                "email_offer": "Exclusive Digital Bonus",
                "brand_value_proposition": "Quality content with bonuses",
                "call_to_action": "Get your FREE bonus content!",
                "platform": "Carrd.co",
                "email_service": "ConvertKit"
            }
    
    def _determine_content_type(self, micro_niche: str) -> str:
        """Determine the primary content type from micro-niche."""
        niche_lower = micro_niche.lower()
        
        if "coloring" in niche_lower:
            return "coloring"
        elif "puzzle" in niche_lower or "sudoku" in niche_lower or "crossword" in niche_lower:
            return "puzzle"
        elif "journal" in niche_lower or "planner" in niche_lower:
            return "journal"
        elif "activity" in niche_lower or "workbook" in niche_lower:
            return "activity"
        else:
            return "guide"
    
    def generate_back_matter_content(self, book: SeriesBook, series: BookSeries, cross_promotion: Dict[str, Any]) -> str:
        """Generate complete back matter content for a book."""
        try:
            back_matter = "\n" + "="*50 + "\n"
            back_matter += f"Thank you for reading {book.title}!\n"
            back_matter += "="*50 + "\n\n"
            
            # Series cross-promotion
            if book.book_id in cross_promotion:
                back_matter += cross_promotion[book.book_id]["back_matter_text"]
                back_matter += "\n\n"
            
            # Email capture offer
            back_matter += "🎁 FREE BONUS CONTENT!\n"
            back_matter += f"Get your {series.email_capture_offer}\n"
            back_matter += f"Visit: {series.website_url}\n\n"
            
            # Brand information
            back_matter += f"📍 About {series.series_brand}:\n"
            back_matter += f"{series.author_persona} creates quality {series.micro_niche} content.\n"
            back_matter += f"Follow us for new releases and exclusive content!\n\n"
            
            # Review request
            back_matter += "⭐ LOVE THIS BOOK?\n"
            back_matter += "Please leave a review on Amazon!\n"
            back_matter += "Your feedback helps us create better content.\n\n"
            
            back_matter += "="*50 + "\n"
            back_matter += f"© {datetime.now().year} {series.series_brand} | All Rights Reserved\n"
            back_matter += "="*50
            
            return back_matter
            
        except Exception as e:
            logger.error(f"Back matter generation failed: {e}")
            return f"\nThank you for reading {book.title}!\nVisit {series.website_url} for bonus content."

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for series publishing.
    """
    try:
        logger.info("📚 SERIES PUBLISHER ACTIVATED")
        
        # Get approved niche opportunity
        niche_opportunity = event.get('niche_opportunity')
        if not niche_opportunity:
            raise ValueError("No niche opportunity provided")
        
        # Initialize series publisher
        publisher = SeriesPublisher()
        
        # Create book series
        book_series = asyncio.run(publisher.create_book_series(niche_opportunity))
        
        # Format response
        series_data = {
            'series_name': book_series.series_name,
            'series_brand': book_series.series_brand,
            'micro_niche': book_series.micro_niche,
            'total_volumes': book_series.total_volumes,
            'website_url': book_series.website_url,
            'email_offer': book_series.email_capture_offer,
            'books': [
                {
                    'volume': book.volume_number,
                    'title': book.title,
                    'subtitle': book.subtitle,
                    'focus': book.unique_content_focus,
                    'keywords': book.keywords,
                    'book_id': book.book_id
                }
                for book in book_series.books
            ]
        }
        
        logger.info(f"✅ Series created: {book_series.series_name} ({book_series.total_volumes} volumes)")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'series': series_data,
                'next_action': 'begin_volume_1_creation'
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Series publishing failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Series publishing failed: {str(e)}'
            })
        }

if __name__ == "__main__":
    # Test series publisher
    test_niche = {
        'micro_niche': 'Large print crossword puzzles for seniors',
        'category': 'Puzzle Books',
        'profit_potential_daily': 15.0,
        'confidence_score': 85.0
    }
    
    import asyncio
    publisher = SeriesPublisher()
    series = asyncio.run(publisher.create_book_series(test_niche))
    
    print(f"\n📚 SERIES CREATED: {series.series_name}")
    print(f"Brand: {series.series_brand}")
    print(f"Website: {series.website_url}")
    print(f"Email Offer: {series.email_capture_offer}")
    print(f"\nBooks in Series:")
    for book in series.books:
        print(f"  {book.volume_number}. {book.title}")
        print(f"     Focus: {book.unique_content_focus}")
        print(f"     Keywords: {', '.join(book.keywords[:3])}...")