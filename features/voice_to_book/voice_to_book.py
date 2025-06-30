"""
Voice to Book Pipeline - Convert voice recordings to publishable books
"""

import logging
from pathlib import Path
from typing import Dict

import whisper
from pydub import AudioSegment

from ..context.author_context import AuthorContext
from ..context.voice_processing import VoiceProcessor
from ..engines.content_generator import ContentGenerator


class VoiceToBookPipeline:
    """
    Complete pipeline for converting voice to books
    """

        """  Init  """
def __init__(self, whisper_model: str = "base"):
        self.logger = logging.getLogger(__name__)
        self.whisper_model = whisper.load_model(whisper_model)
        self.voice_processor = VoiceProcessor()
        self.content_generator = ContentGenerator()

    async def process_voice_file(self, audio_path: Path) -> Dict:
        """
        Process a voice recording file
        """
        self.logger.info(f"Processing voice file: {audio_path}")

        # Load and preprocess audio
        audio = AudioSegment.from_file(audio_path)

        # Transcribe with Whisper
        result = self.whisper_model.transcribe(str(audio_path))
        transcript = result["text"]

        # Extract intent and context
        intent = await self.voice_processor.extract_intent(transcript)
        context = await self._build_author_context(transcript, intent)

        # Generate book content
        book_content = await self.content_generator.generate_from_voice(
            transcript=transcript, intent=intent, context=context
        )

        return {
            "transcript": transcript,
            "intent": intent,
            "book_content": book_content,
            "metadata": {
                "duration": len(audio) / 1000,  # seconds
                "word_count": len(transcript.split()),
                "detected_language": result.get("language", "en"),
            },
        }

    async def _build_author_context(
        self, transcript: str, intent: Dict
    ) -> AuthorContext:
        """
        Build author context from transcript and intent
        """
        return AuthorContext(
            expertise=intent.get("expertise", []),
            tone=intent.get("tone", "professional"),
            target_audience=intent.get("audience", "general"),
            goals=intent.get("goals", []),
        )

    async def create_book(self, voice_data: Dict, book_type: str = "guide") -> Dict:
        """
        Create a complete book from voice data
        """
        # Generate chapters
        chapters = await self._generate_chapters(voice_data, book_type)

        # Create book structure
        book = {
            "title": voice_data["intent"].get("title", "Untitled Book"),
            "subtitle": voice_data["intent"].get("subtitle", ""),
            "author": voice_data["intent"].get("author", "Anonymous"),
            "chapters": chapters,
            "metadata": voice_data["metadata"],
        }

        return book

    async def _generate_chapters(self, voice_data: Dict, book_type: str) -> List[Dict]:
        """
        Generate book chapters from voice data
        """
        # Implementation for chapter generation
        chapters = []

        # Split content into logical sections
        sections = await self.content_generator.split_into_sections(
            voice_data["book_content"]
        )

        for i, section in enumerate(sections):
            chapter = {
                "number": i + 1,
                "title": section.get("title", f"Chapter {i + 1}"),
                "content": section["content"],
                "word_count": len(section["content"].split()),
            }
            chapters.append(chapter)

        return chapters
