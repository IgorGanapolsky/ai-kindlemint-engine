import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime
from pathlib import Path

from kindlemint.orchestrator.feature_developer import FeatureDeveloper
from kindlemint.context.voice_processing import VoiceProcessor
from kindlemint.context.author_context import AuthorContext
from kindlemint.engines.content_generator import ContentGenerator


class TestVoiceToBookPipeline:
    @pytest.fixture
    def pipeline(self):
        with patch("whisper.load_model") as mock_load_model, patch(
            "pydub.AudioSegment.from_file"
        ) as mock_from_file:
            mock_load_model.return_value.transcribe.return_value = {
                "text": "test transcript",
                "language": "en",
            }
            mock_from_file.return_value.duration_seconds = 10
            pipeline = FeatureDeveloper().feature_templates["voice_to_book"](
                {}
            )  # Pass empty requirements for now
            pipeline.voice_processor = AsyncMock(spec=VoiceProcessor)
            pipeline.content_generator = AsyncMock(spec=ContentGenerator)
            yield pipeline

    @pytest.mark.asyncio
    async def test_process_voice_file(self, pipeline):
        pipeline.voice_processor.extract_intent.return_value = {
            "expertise": ["tech"],
            "tone": "formal",
            "audience": "developers",
            "goals": ["educate"],
        }
        pipeline.content_generator.generate_from_voice.return_value = "book content"

        audio_path = Path("dummy.mp3")
        result = await pipeline.process_voice_file(audio_path)

        assert result["transcript"] == "test transcript"
        assert result["intent"] == {
            "expertise": ["tech"],
            "tone": "formal",
            "audience": "developers",
            "goals": ["educate"],
        }
        assert result["book_content"] == "book content"
        assert "duration" in result["metadata"]
        assert "word_count" in result["metadata"]
        assert "detected_language" in result["metadata"]

    @pytest.mark.asyncio
    async def test_build_author_context(self, pipeline):
        transcript = "This is a test transcript about AI."
        intent = {
            "expertise": ["AI"],
            "tone": "informal",
            "audience": "general",
            "goals": ["inform"],
        }
        context = await pipeline._build_author_context(transcript, intent)

        assert isinstance(context, AuthorContext)
        assert context.expertise == ["AI"]
        assert context.tone == "informal"
        assert context.target_audience == "general"
        assert context.goals == ["inform"]

    @pytest.mark.asyncio
    async def test_create_book(self, pipeline):
        voice_data = {
            "transcript": "test transcript",
            "intent": {"title": "Test Book", "subtitle": "A Test", "author": "Tester"},
            "book_content": "chapter one content. chapter two content.",
            "metadata": {"duration": 10, "word_count": 5, "detected_language": "en"},
        }
        pipeline.content_generator.split_into_sections.return_value = [
            {"title": "Chapter 1", "content": "chapter one content."},
            {"title": "Chapter 2", "content": "chapter two content."},
        ]

        book = await pipeline.create_book(voice_data, "guide")

        assert book["title"] == "Test Book"
        assert book["author"] == "Tester"
        assert len(book["chapters"]) == 2
        assert book["chapters"][0]["title"] == "Chapter 1"
        assert book["chapters"][1]["content"] == "chapter two content."

    @pytest.mark.asyncio
    async def test_create_book_default_title_author(self, pipeline):
        voice_data = {
            "transcript": "test transcript",
            "intent": {},
            "book_content": "some content",
            "metadata": {"duration": 10, "word_count": 2, "detected_language": "en"},
        }
        pipeline.content_generator.split_into_sections.return_value = [
            {"content": "some content"}
        ]

        book = await pipeline.create_book(voice_data)

        assert book["title"] == "Untitled Book"
        assert book["author"] == "Anonymous"

    @pytest.mark.asyncio
    async def test_generate_chapters(self, pipeline):
        voice_data = {"book_content": "Section 1. Section 2. Section 3."}
        pipeline.content_generator.split_into_sections.return_value = [
            {"content": "Section 1.", "title": "Section 1"},
            {"content": "Section 2.", "title": "Section 2"},
            {"content": "Section 3.", "title": "Section 3"},
        ]

        chapters = await pipeline._generate_chapters(voice_data, "novel")

        assert len(chapters) == 3
        assert chapters[0]["number"] == 1
        assert chapters[0]["title"] == "Section 1"
        assert chapters[2]["word_count"] == 2
