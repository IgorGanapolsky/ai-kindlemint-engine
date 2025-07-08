"""Automated cover generation agent using DALL-E 3 API."""

import logging
from pathlib import Path

# import os # Removed: API key handled by APIManager
# import base64 # Seems unused, will remove if confirmed
from typing import Tuple

import requests  # Retain for downloading image from URL
from PIL import ImageFont

# from openai import OpenAI # Removed: Client handled by APIManager
from ..utils.api_manager import get_api_manager  # Added

logger = logging.getLogger(__name__)


class CoverAgent:
    """Generates professional book covers using DALL-E 3 API with quality analysis."""

    def __init__(self):  # Removed api_key parameter
        """Initialize the cover generation agent."""
        # self.api_key = api_key or os.getenv("OPENAI_API_KEY") # Removed
        # if not self.api_key: # Removed
        #     raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set") # Removed

        # self.client = OpenAI(api_key=self.api_key) # Removed
        self.api_manager = get_api_manager()  # Added
        self.cover_cache = {}
        self.fonts_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
        self.fonts_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        """ Load Font"""
def _load_font(self, font_filename: str, size: int):
        """
        Loads a font from the assets/fonts directory, with fallback to default.
        """
        font_path = self.fonts_dir / font_filename
        try:
            return ImageFont.truetype(str(font_path), size)
        except IOError:
            logger.warning(
                f"Font file not found at {font_path}. Falling back to default font."
            )
            return ImageFont.load_default()

    def generate_professional_cover(
        self,
        book_title: str,
        subtitle: str = "",
        niche: str = "non-fiction",
        num_options: int = 1,
        output_path: str = "generated_cover.jpg",
    ) -> Tuple[str, float]:
        """Generate a professional book cover using DALL-E 3.

        Args:
            book_title: The title of the book
            subtitle: Optional subtitle
            niche: Book niche/genre for style guidance
            num_options: Number of cover options to generate
            output_path: Where to save the final cover

        Returns:
            Tuple of (output_path, quality_score)
        """
        try:
            logger.info(f"Generating cover for '{book_title}' in {niche} niche")

            # Generate multiple cover options
            cover_options = []
            for i in range(
                min(num_options, 4)
            ):  # DALL-E 3 rate limits (assuming APIManager handles this)
                try:
                    prompt = self._create_cover_prompt(
                        book_title, subtitle, niche, variation=i
                    )
                    # _generate_single_cover now uses APIManager
                    cover_data = self._generate_single_cover(prompt, f"option_{i+1}")

                    if cover_data:
                        # Analyze quality
                        quality_score = self._analyze_cover_quality(
                            cover_data["image"], book_title
                        )
                        cover_data["quality_score"] = quality_score
                        cover_options.append(cover_data)
                        logger.info(
                            f"Generated cover option {i+1} with quality score: {quality_score:.2f}"
                        )
                    else:
                        logger.warning(f"Failed to generate cover option {i+1}")

                except Exception as e:
                    logger.error(f"Error generating cover option {i+1}: {str(e)}")

            # Select best option
            if cover_options:
                best_cover = max(cover_options, key=lambda x: x["quality_score"])
                logger.info(
                    f"Selected best cover with quality score: {best_cover['quality_score']:.2f}"
                )

                # Save the final cover
                final_path = self._save_cover_image(best_cover["image"], output_path)
                return final_path, best_cover["quality_score"]
            else:
                logger.error("Failed to generate any valid cover options")
                return "", 0.0

        except Exception as e:
            logger.error(f"Error in cover generation process: {str(e)}")
            return "", 0.0

    def _create_cover_prompt(
        self, title: str, subtitle: str, niche: str, variation: int = 0
    ) -> str:
        """Create a detailed prompt for DALL-E 3 cover generation.

        Args:
            title: Book title
            subtitle: Book subtitle
            niche: Book niche/genre
            variation: Which variation to generate (affects style)

        Returns:
            Detailed prompt string
        """
        # Base prompt with title and subtitle
        prompt = f"Create a professional book cover for '{title}'"
        if subtitle:
            prompt += f" with subtitle '{subtitle}'"

        # Add niche-specific styling
        if niche.lower() == "self-help" or niche.lower() == "personal development":
            prompt += " in the self-help genre. Use inspiring imagery, clean typography, and motivational visual elements."

        elif niche.lower() == "business" or niche.lower() == "finance":
            prompt += " in the business/finance genre. Use professional, authoritative design with clean lines and sophisticated color schemes."
