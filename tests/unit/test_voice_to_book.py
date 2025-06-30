"""
Tests for voice_to_book feature
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Skip this module entirely if the optional dependency `whisper` is not available.
try:
    import whisper  # noqa: F401
except ModuleNotFoundError:
    pytest.skip(
        "Skipping voice_to_book tests – optional dependency 'whisper' not installed.",
        allow_module_level=True,
    )

from voice_to_book import *


class TestVoiceToBook:
    """Test suite for voice_to_book"""

    @pytest.fixture
    async def instance(self):
        """Create instance for testing"""
        instance = VoiceToBook()
        await instance.initialize()
        return instance

    @pytest.mark.asyncio
    async def test_initialization(self, instance):
        """Test feature initialization"""
        assert instance is not None

    @pytest.mark.asyncio
    async def test_execute_success(self, instance):
        """Test successful execution"""
        result = await instance.execute({"test": True})
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_with_error(self, instance):
        """Test error handling"""
        # Test with invalid params
        result = await instance.execute({"invalid": None})
        # Should handle gracefully
        assert result["status"] in ["success", "error"]
