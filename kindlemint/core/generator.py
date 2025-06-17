"""Content generation using AI."""
import logging
import os
import json
import uuid
from typing import List, Dict, Optional, Union
from openai import OpenAI
from pathlib import Path

from ..utils.text_processing import clean_text
from ..memory import KDPMemory

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates book content using AI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        enable_memory: bool = True,
    ):
        """Initialize the content generator.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
            model: The OpenAI model to use for generation.
            temperature: Controls randomness in generation (0-1).
            max_tokens: Maximum number of tokens to generate per request.
            enable_memory: Whether to use memory-driven topic selection.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enable_memory = enable_memory
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize memory system if enabled
        if self.enable_memory:
            try:
                self.memory = KDPMemory()
                logger.info("Memory-driven publishing enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize memory system: {e}")
                self.enable_memory = False
    
    def generate_chapter(
        self,
        title: str,
        outline: str = "",
        style: str = "professional",
        word_count: int = 1500,
        **kwargs
    ) -> Dict[str, str]:
        """Generate a book chapter.
        
        Args:
            title: Chapter title
            outline: Chapter outline or key points to cover
            style: Writing style (e.g., professional, conversational, academic)
            word_count: Target word count for the chapter
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict with 'title' and 'content' keys
        """
        prompt = self._build_chapter_prompt(title, outline, style, word_count)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            return {
                "title": title,
                "content": clean_text(content)
            }
            
        except Exception as e:
            logger.error(f"Error generating chapter: {str(e)}")
            raise
    
    def generate_book_outline(
        self,
        topic: str,
        num_chapters: int = 10,
        style: str = "professional",
        **kwargs
    ) -> List[Dict[str, str]]:
        """Generate a book outline with chapter titles and summaries.
        
        Args:
            topic: Book topic or title
            num_chapters: Number of chapters to generate
            style: Writing style
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            List of chapter dicts with 'title' and 'summary' keys
        """
        prompt = (
            f"Create a detailed outline for a book about '{topic}'. "
            f"The book should have {num_chapters} chapters. "
            f"For each chapter, provide a title and a 2-3 sentence summary. "
            f"Use a {style} writing style. "
            "Format the response as a JSON array of objects with 'title' and 'summary' fields."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature * 0.8,  # Slightly less random for outlines
                max_tokens=self.max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            # Try to parse JSON from the response
            try:
                # Sometimes the response might include markdown code blocks
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].strip()
                    if content.startswith('json'):
                        content = content[4:].strip()
                
                chapters = json.loads(content)
                if not isinstance(chapters, list):
                    chapters = [chapters]
                return chapters
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from response: {e}")
                # Fallback to parsing the text format
                return self._parse_outline_from_text(content)
                
        except Exception as e:
            logger.error(f"Error generating book outline: {str(e)}")
            raise
    
    def _parse_outline_from_text(self, text: str) -> List[Dict[str, str]]:
        """Parse chapter outlines from plain text when JSON parsing fails."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        chapters = []
        current_chapter = {}
        
        for line in lines:
            if line.lower().startswith('chapter') or line.split('.')[0].isdigit():
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {'title': line, 'summary': ''}
            elif current_chapter and 'title' in current_chapter:
                current_chapter['summary'] += ' ' + line
        
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def _build_chapter_prompt(
        self,
        title: str,
        outline: str,
        style: str,
        word_count: int
    ) -> str:
        """Build the prompt for chapter generation."""
        prompt = (
            f"Write a chapter titled '{title}'.\n\n"
        )
        
        if outline:
            prompt += f"Here's an outline of what to cover:\n{outline}\n\n"
        
        prompt += (
            f"Writing style: {style}. "
            f"Target length: approximately {word_count} words. "
            "The chapter should be well-structured with proper paragraphs. "
            "Use markdown formatting for headings, lists, and emphasis."
        )
        
        return prompt
    
    def generate_profitable_book_topic(self, fallback_niche: Optional[str] = None) -> Dict[str, str]:
        """Generate a book topic based on memory-driven analysis of profitable niches.
        
        Args:
            fallback_niche: Niche to use if memory system is unavailable
            
        Returns:
            Dict with 'topic', 'niche', 'book_id', and 'reasoning' keys
        """
        book_id = str(uuid.uuid4())
        
        if self.enable_memory and hasattr(self, 'memory'):
            try:
                # Get top performing niches from memory
                top_niches = self.memory.get_top_performing_niches(limit=3)
                
                if top_niches:
                    # Use the most profitable niche
                    target_niche = top_niches[0]['niche']
                    niche_performance = top_niches[0]['average_roi']
                    logger.info(f"Targeting profitable niche: {target_niche} (ROI: {niche_performance:.2f})")
                else:
                    # No historical data, use fallback or generate new niche
                    target_niche = fallback_niche or self._generate_trending_niche()
                    logger.info(f"No historical data, using niche: {target_niche}")
            except Exception as e:
                logger.warning(f"Memory system error, using fallback: {e}")
                target_niche = fallback_niche or "productivity"
        else:
            target_niche = fallback_niche or "productivity"
        
        # Generate topic within the profitable niche
        topic_prompt = (
            f"Generate a compelling book topic in the '{target_niche}' niche that would appeal to "
            f"a broad audience and have strong sales potential on Amazon KDP. "
            f"The topic should be:\n"
            f"1. Specific enough to be actionable\n"
            f"2. Broad enough to have market appeal\n"
            f"3. Trending or evergreen in nature\n"
            f"4. Suitable for a 150-200 page book\n\n"
            f"Respond with just the book title/topic, nothing else."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": topic_prompt}],
                temperature=0.8,
                max_tokens=100
            )
            
            topic = response.choices[0].message.content.strip().strip('"')
            
            # Store the new book record in memory
            if self.enable_memory and hasattr(self, 'memory'):
                try:
                    self.memory.store_book_record(
                        book_id=book_id,
                        topic=topic,
                        niche=target_niche,
                        metadata={'generation_method': 'memory_driven'}
                    )
                    logger.info(f"Stored new book record: {book_id}")
                except Exception as e:
                    logger.warning(f"Failed to store book record: {e}")
            
            return {
                'book_id': book_id,
                'topic': topic,
                'niche': target_niche,
                'reasoning': f"Selected based on niche performance analysis"
            }
            
        except Exception as e:
            logger.error(f"Error generating profitable topic: {str(e)}")
            raise
    
    def _generate_trending_niche(self) -> str:
        """Generate a trending niche when no historical data is available."""
        niche_prompt = (
            "List 5 trending and profitable book niches for Amazon KDP publishing in 2025. "
            "Focus on evergreen topics with broad appeal. "
            "Respond with just one niche name that has the highest profit potential."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": niche_prompt}],
                temperature=0.7,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip().lower()
            
        except Exception as e:
            logger.warning(f"Failed to generate trending niche: {e}")
            return "personal development"
    
    def generate_cover_prompt(
        self,
        book_title: str,
        book_description: str,
        genre: str,
        style: str = "professional",
        **kwargs
    ) -> str:
        """Generate a prompt for creating a book cover.
        
        Args:
            book_title: Title of the book
            book_description: Brief description of the book
            genre: Book genre
            style: Style of the cover (e.g., minimalist, photorealistic, illustrated)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            A detailed prompt for generating a book cover
        """
        prompt = (
            f"Create a detailed description for a book cover with the following details:\n"
            f"Title: {book_title}\n"
            f"Genre: {genre}\n"
            f"Style: {style}\n"
            f"Description: {book_description}\n\n"
            "The description should be suitable for an AI image generation model. "
            "Include details about the visual style, color scheme, typography, and key visual elements. "
            "Be specific about the mood and atmosphere the cover should convey."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating cover prompt: {str(e)}")
            raise
    
    def generate_kdp_description(
        self,
        book_title: str,
        book_content: str,
        niche: str,
        target_audience: str = "professionals and entrepreneurs",
        **kwargs
    ) -> str:
        """Generate a compelling 500-word KDP book description for maximum sales conversion.
        
        Args:
            book_title: Title of the book
            book_content: Brief overview or chapter outline of the book content
            niche: The book's niche (e.g., productivity, finance, health)
            target_audience: Primary target audience
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            A compelling 500-word KDP description with emotional hooks and clear benefits
        """
        description_prompt = (
            f"Write a compelling 500-word Amazon KDP book description for '{book_title}' in the {niche} niche.\n\n"
            f"Book Content Overview: {book_content[:500]}...\n"
            f"Target Audience: {target_audience}\n\n"
            
            "REQUIREMENTS for the description:\n"
            "1. Start with an emotional hook question that identifies the reader's pain point\n"
            "2. Include a bold promise or transformation statement\n"
            "3. Use bullet points (✅) to highlight 5-7 specific benefits/outcomes\n"
            "4. Add social proof elements (mention 'thousands of readers' or 'proven system')\n"
            "5. Include urgency and scarcity language\n"
            "6. End with a strong call-to-action\n"
            "7. Use emotional power words: 'transform', 'breakthrough', 'secrets', 'proven', 'ultimate'\n"
            "8. Make it scannable with short paragraphs and formatting\n"
            "9. Address objections and include a subtle guarantee or risk-reversal\n"
            "10. Keep it under 500 words total\n\n"
            
            "TONE: Authoritative, benefit-focused, emotionally compelling\n"
            "FORMAT: Use markdown formatting with **bold** text and bullet points\n"
            "GOAL: Maximize conversion from browser to buyer\n\n"
            
            "Write the complete KDP description now:"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": description_prompt}],
                temperature=0.8,  # Higher creativity for compelling copy
                max_tokens=800,   # Increased for longer descriptions
                **kwargs
            )
            
            description = response.choices[0].message.content.strip()
            logger.info(f"Generated KDP description ({len(description)} characters)")
            return description
            
        except Exception as e:
            logger.error(f"Error generating KDP description: {str(e)}")
            raise
