"""Content generation using AI."""

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..memory import KDPMemory
from ..utils.api_manager import get_api_manager  # Added
from ..utils.text_processing import clean_text

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates book content using AI."""

    def __init__(
        self,
        # api_key: Optional[str] = None, # Removed: Handled by APIManager
        # model: str = "gpt-4", # Removed: Handled by APIManager
        temperature: float = 0.7,  # Retained: May be used for specific task types or passed via kwargs if APIManager supports
        max_tokens: int = 2000,  # Retained: Passed to APIManager
        enable_memory: bool = True,
    ):
        """Initialize the content generator.

        Args:
            temperature: Controls randomness in generation (0-1). Used if APIManager supports it.
            max_tokens: Maximum number of tokens to generate per request.
            enable_memory: Whether to use memory-driven topic selection.
        """
        # self.api_key = api_key or os.getenv("OPENAI_API_KEY") # Removed
        # if not self.api_key: # Removed
        #     raise ValueError( # Removed
        #         "OpenAI API key not provided and OPENAI_API_KEY environment variable not set" # Removed
        #     ) # Removed

        # self.model = model # Removed
        self.temperature = temperature  # Retained for now, though APIManager doesn't directly use it in generate_text
        self.max_tokens = max_tokens
        self.enable_memory = enable_memory
        # self.client = OpenAI(api_key=self.api_key) # Removed
        self.api_manager = get_api_manager()  # Added

        # Initialize memory system if enabled
        if self.enable_memory:
            try:
                self.memory = KDPMemory()
                logger.info("Memory-driven publishing enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize memory system: {e}")
                self.enable_memory = False
        else:  # Added
            self.memory = None  # Ensure self.memory exists even if disabled

    def generate_chapter(
        self,
        title: str,
        outline: str = "",
        style: str = "professional",
        word_count: int = 1500,
        **kwargs,  # Retained for flexibility, though APIManager may not use all
    ) -> Dict[str, str]:
        """Generate a book chapter.

        Args:
            title: Chapter title
            outline: Chapter outline or key points to cover
            style: Writing style (e.g., professional, conversational, academic)
            word_count: Target word count for the chapter
            **kwargs: Additional parameters (currently not directly passed to APIManager.generate_text)

        Returns:
            Dict with 'title' and 'content' keys
        """
        prompt = self._build_chapter_prompt(title, outline, style, word_count)

        try:
            # APIManager.generate_text uses internal temperature settings
            # model selection is handled by APIManager based on priority/task_type
            content = self.api_manager.generate_text(
                prompt=prompt,
                max_tokens=self.max_tokens,  # Use instance max_tokens
                task_type="text_generation",  # Default task type
                priority="quality",  # Assuming chapters need quality
            )

            if content is None:
                raise Exception("API Manager failed to generate chapter content.")

            return {"title": title, "content": clean_text(content)}

        except Exception as e:
            logger.error(f"Error generating chapter: {str(e)}")
            raise

    def generate_book_outline(
        self,
        topic: str,
        num_chapters: int = 10,
        style: str = "professional",
        **kwargs,  # Retained for flexibility
    ) -> List[Dict[str, str]]:
        """Generate a book outline with chapter titles and summaries.

        Args:
            topic: Book topic or title
            num_chapters: Number of chapters to generate
            style: Writing style
            **kwargs: Additional parameters

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
            # Temperature for outlines might be desired to be lower, APIManager internal logic applies
            content = self.api_manager.generate_text(
                prompt=prompt,
                max_tokens=self.max_tokens,
                task_type="text_generation",
                priority="quality",  # Outlines benefit from quality
            )

            if content is None:
                raise Exception("API Manager failed to generate book outline.")
            # Try to parse JSON from the response
            try:
                # Sometimes the response might include markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()
                    if content.startswith("json"):
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
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        chapters = []
        current_chapter = {}

        for line in lines:
            if line.lower().startswith("chapter") or line.split(".")[0].isdigit():
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {"title": line, "summary": ""}
            elif (
                current_chapter and "title" in current_chapter
            ):  # Ensure current_chapter is initialized
                current_chapter["summary"] += " " + line

        if (
            current_chapter and "title" in current_chapter
        ):  # Ensure current_chapter is initialized before appending
            chapters.append(current_chapter)

        return chapters

    def _build_chapter_prompt(
        self, title: str, outline: str, style: str, word_count: int
    ) -> str:
        """Build the prompt for chapter generation."""
        prompt = f"Write a chapter titled '{title}'.\n\n"

        if outline:
            prompt += f"Here's an outline of what to cover:\n{outline}\n\n"

        prompt += (
            f"Writing style: {style}. "
            f"Target length: approximately {word_count} words. "
            "The chapter should be well-structured with proper paragraphs. "
            "Use markdown formatting for headings, lists, and emphasis."
        )

        return prompt

    def generate_profitable_book_topic(
        self, fallback_niche: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate a book topic based on memory-driven analysis of profitable niches.

        Args:
            fallback_niche: Niche to use if memory system is unavailable

        Returns:
            Dict with 'topic', 'niche', 'book_id', and 'reasoning' keys
        """
        book_id = str(uuid.uuid4())

        if self.enable_memory and self.memory is not None:
            try:
                # Get top performing niches from memory
                top_niches = self.memory.get_top_performing_niches(limit=3)

                if top_niches:
                    # Use the most profitable niche
                    target_niche = top_niches[0]["niche"]
                    niche_performance = top_niches[0]["average_roi"]
                    logger.info(
                        f"Targeting profitable niche: {target_niche} (ROI: {niche_performance:.2f})"
                    )
                else:
                    # No historical data, use fallback or generate new niche
                    # _generate_trending_niche will now use APIManager
                    generated_niche = self._generate_trending_niche()
                    target_niche = fallback_niche or generated_niche
                    logger.info(f"No historical data, using niche: {target_niche}")
            except Exception as e:
                logger.warning(f"Memory system error, using fallback: {e}")
                target_niche = (
                    fallback_niche or self._generate_trending_niche()
                )  # Ensure generation if fallback_niche is None
        else:
            target_niche = (
                fallback_niche or self._generate_trending_niche()
            )  # Ensure generation if fallback_niche is None

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
            topic = self.api_manager.generate_text(
                prompt=topic_prompt,
                max_tokens=100,  # Original max_tokens
                task_type="text_generation",
                priority="quality",  # For creative topic generation
            )

            if topic is None:
                raise Exception("API Manager failed to generate book topic.")

            topic = topic.strip().strip('"')

            # Store the new book record in memory
            if self.enable_memory and self.memory is not None:
                try:
                    self.memory.store_book_record(
                        book_id=book_id,
                        topic=topic,
                        niche=target_niche,
                        metadata={"generation_method": "memory_driven"},
                    )
                    logger.info(f"Stored new book record: {book_id}")
                except Exception as e:
                    logger.warning(f"Failed to store book record: {e}")

            return {
                "book_id": book_id,
                "topic": topic,
                "niche": target_niche,
                "reasoning": f"Selected based on niche performance analysis or generation",
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
            niche = self.api_manager.generate_text(
                prompt=niche_prompt,
                max_tokens=50,  # Original max_tokens
                task_type="text_generation",
                priority="balanced",  # For niche generation
            )
            if niche is None:
                logger.warning(
                    "API Manager failed to generate trending niche, using fallback."
                )
                return "personal development"  # Fallback
            return niche.strip().lower()

        except Exception as e:
            logger.warning(f"Failed to generate trending niche: {e}, using fallback.")
            return "personal development"  # Fallback

    def generate_cover_prompt(
        self,
        book_title: str,
        book_description: str,
        genre: str,
        style: str = "professional",
        **kwargs,  # Retained for flexibility
    ) -> str:
        """Generate a prompt for creating a book cover.

        Args:
            book_title: Title of the book
            book_description: Brief description of the book
            genre: Book genre
            style: Style of the cover (e.g., minimalist, photorealistic, illustrated)
            **kwargs: Additional parameters

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
            cover_prompt_text = self.api_manager.generate_text(
                prompt=prompt,
                max_tokens=500,  # Original max_tokens
                task_type="text_generation",
                priority="quality",  # Detailed prompt needs quality
            )
            if cover_prompt_text is None:
                raise Exception("API Manager failed to generate cover prompt.")
            return cover_prompt_text.strip()

        except Exception as e:
            logger.error(f"Error generating cover prompt: {str(e)}")
            raise

    def generate_kdp_description(
        self,
        book_title: str,
        book_content: str,
        niche: str,
        target_audience: str = "professionals and entrepreneurs",
        **kwargs,  # Retained for flexibility
    ) -> str:
        """Generate a compelling 500-word KDP book description for maximum sales conversion.

        Args:
            book_title: Title of the book
            book_content: Brief overview or chapter outline of the book content
            niche: The book's niche (e.g., productivity, finance, health)
            target_audience: Primary target audience
            **kwargs: Additional parameters

        Returns:
            A compelling 500-word KDP description with emotional hooks and clear benefits
        """
        description_prompt_text = (
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
            description = self.api_manager.generate_text(
                prompt=description_prompt_text,
                max_tokens=800,  # Original max_tokens
                task_type="text_generation",
                priority="quality",  # Compelling copy needs quality
            )
            if description is None:
                raise Exception("API Manager failed to generate KDP description.")

            logger.info(f"Generated KDP description ({len(description)} characters)")
            return description.strip()

        except Exception as e:
            logger.error(f"Error generating KDP description: {str(e)}")
            raise
