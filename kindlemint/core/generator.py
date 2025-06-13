"""Content generation using AI."""
import logging
import os
import json
from typing import List, Dict, Optional, Union
import openai
from pathlib import Path

from ..utils.text_processing import clean_text

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates book content using AI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """Initialize the content generator.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
            model: The OpenAI model to use for generation.
            temperature: Controls randomness in generation (0-1).
            max_tokens: Maximum number of tokens to generate per request.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        openai.api_key = self.api_key
    
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
            response = openai.ChatCompletion.create(
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
            response = openai.ChatCompletion.create(
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
            response = openai.ChatCompletion.create(
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
