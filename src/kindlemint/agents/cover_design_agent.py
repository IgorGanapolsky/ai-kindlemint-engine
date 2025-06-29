"""
Cover Design Agent for creating book covers (front and back) using AI
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.api import call_ai_api
from .agent_types import AgentCapability
from .base_agent import BaseAgent
from .task_system import Task, TaskResult, TaskType


class CoverDesignAgent(BaseAgent):
    """Agent responsible for creating book covers using AI image generation"""

    def __init__(self, agent_id: str = "cover-design-agent"):
        capabilities = [AgentCapability.COVER_DESIGN]
        super().__init__(agent_id=agent_id, capabilities=capabilities)
        self.logger = logging.getLogger(f"CoverDesignAgent-{agent_id}")

    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute cover design task"""
        if task.task_type != TaskType.DESIGN_COVER:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"Unsupported task type: {task.task_type}",
            )

        try:
            # Extract task parameters
            title = task.input_data.get("title", "Untitled Book")
            author = task.input_data.get("author", "Unknown Author")
            cover_type = task.input_data.get("cover_type", "front")  # front or back
            format_type = task.input_data.get("format_type", "paperback")
            output_dir = task.input_data.get("output_dir", ".")
            metadata = task.input_data.get("metadata", {})

            # Get DALL-E prompt from metadata
            cover_design = metadata.get("cover_design", {})
            if cover_type == "back":
                prompt = cover_design.get("back_cover_dalle_prompt")
                if not prompt:
                    # Generate a basic back cover prompt if missing
                    prompt = self._generate_back_cover_prompt(title, author, metadata)
            else:
                prompt = cover_design.get("dalle_prompt")
                if not prompt:
                    # Generate a basic front cover prompt if missing
                    prompt = self._generate_front_cover_prompt(title, author, metadata)

            if not prompt:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    error_message=f"No DALL-E prompt found for {cover_type} cover",
                )

            self.logger.info(f"Creating {cover_type} cover for '{title}'")

            # Generate cover image using DALL-E
            start_time = datetime.now()

            # Call DALL-E API (placeholder - would need actual implementation)
            # For now, return a success message indicating what would be done
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            cover_filename = f"{title.replace(' ', '_')}_{cover_type}_cover.png"
            cover_path = output_path / cover_filename

            # In production, this would call DALL-E API
            # For now, create a placeholder response
            generation_result = {
                "image_url": f"https://dalle-placeholder/{cover_filename}",
                "prompt_used": prompt,
                "generated_at": datetime.now().isoformat(),
            }

            execution_time = (datetime.now() - start_time).total_seconds()

            # For physical books, ensure both covers are generated
            additional_tasks = []
            if format_type in ["paperback", "hardcover"] and cover_type == "front":
                # Suggest generating back cover too
                additional_tasks.append(
                    {
                        "task_type": "CREATE_COVER_DESIGN",
                        "cover_type": "back",
                        "note": f"Physical {format_type} books need both front and back covers",
                    }
                )

            return TaskResult(
                success=True,
                task_id=task.task_id,
                agent_id=self.agent_id,
                execution_time=execution_time,
                output_data={
                    "cover_path": str(cover_path),
                    "cover_type": cover_type,
                    "format_type": format_type,
                    "generation_result": generation_result,
                    "suggested_tasks": additional_tasks,
                },
                metrics={
                    "generation_time": execution_time,
                    "prompt_length": len(prompt),
                    "cover_type": cover_type,
                },
            )

        except Exception as e:
            self.logger.error(f"Cover design failed: {e}")
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=str(e),
                error_details={"type": type(e).__name__},
            )

    def _generate_front_cover_prompt(
        self, title: str, author: str, metadata: Dict
    ) -> str:
        """Generate a basic front cover prompt if none provided"""
        subtitle = metadata.get("subtitle", "")
        is_large_print = "Large Print" in title

        prompt = f"""Create a professional book cover for '{title}' by {author}.

Design requirements:
- Clean, modern layout suitable for {metadata.get('format', {}).get('type', 'paperback')}
- Large, readable title text{"(extra large for senior readers)" if is_large_print else ""}
- Professional typography
- Eye-catching but not cluttered
- Suitable for online thumbnail and physical bookshelf

Style: Professional, clean, accessible
Target audience: {metadata.get('target_audience', {}).get('primary', 'General readers')}

NO text generation - only design elements and layout."""

        return prompt

    def _generate_back_cover_prompt(
        self, title: str, author: str, metadata: Dict
    ) -> str:
        """Generate a basic back cover prompt if none provided"""
        is_large_print = "Large Print" in title
        description = metadata.get("description", "").split("\n")[0]  # First line

        prompt = f"""Create a professional back cover design for '{title}' by {author}.

Design requirements:
- Clean layout matching front cover style
- Space for book description and author bio
- Barcode placeholder area (bottom right)
- Publisher logo area (bottom left)
- Professional typography
- {metadata.get('format', {}).get('page_count', '100+')} pages noted

Include placeholder areas for:
- Book title and author at top
- Main description area (center)
- Testimonial quote box
- Author bio section
- ISBN barcode
- Publisher information

Style: Clean, professional, matching front cover
NO text generation - only design layout and placeholders."""

        return prompt

    async def validate_capabilities(self) -> Dict[str, Any]:
        """Validate agent capabilities"""
        return {
            "can_create_covers": True,
            "supported_formats": ["paperback", "hardcover", "ebook"],
            "cover_types": ["front", "back", "spine", "full_wrap"],
            "ai_models": ["dall-e-3", "dall-e-2"],
            "output_formats": ["png", "jpg", "pdf-ready"],
        }
