"""
Botpress Integration Module for KindleMint

This module provides integration with Botpress conversational AI platform,
enabling KindleMint to offer dialogue-driven experiences for authors and readers.

Classes:
    BotpressClient: Core client for Botpress API communication
    BaseBot: Abstract base class for all bot implementations
    AuthorInterviewBot: Conducts structured interviews to extract book content
    ReaderFeedbackBot: Collects reader insights and feedback
    WritingCoachBot: Provides real-time writing assistance
    ConversationalMarketingBot: Handles marketing and sales conversations
    WebhookHandler: Processes incoming webhooks from Botpress

Usage:
    from kindlemint.integrations.botpress import BotpressClient, AuthorInterviewBot

    client = BotpressClient(api_key="your_api_key")
    author_bot = AuthorInterviewBot(client)
    content = author_bot.conduct_interview(author_id="auth123", book_topic="puzzle books")
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import requests
from requests.exceptions import RequestException, Timeout

# Import KindleMint utilities
from kindlemint.utils.api import APIManager
from kindlemint.utils.cost_tracker import CostTracker

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class BotpressError(Exception):
    """Base exception for Botpress integration errors."""


class BotpressAPIError(BotpressError):
    """Exception raised for errors in the Botpress API."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Botpress API Error ({status_code}): {message}")


class BotpressConfigError(BotpressError):
    """Exception raised for configuration errors."""


class BotpressWebhookError(BotpressError):
    """Exception raised for webhook processing errors."""


class BotType(Enum):
    """Types of bots supported in the integration."""

    AUTHOR_INTERVIEW = "author_interview"
    READER_FEEDBACK = "reader_feedback"
    WRITING_COACH = "writing_coach"
    MARKETING = "marketing"
    CUSTOM = "custom"


@dataclass
class BotpressConfig:
    """Configuration for Botpress integration."""

    api_key: str
    workspace_id: str
    base_url: str = "https://api.botpress.cloud/v1"
    timeout: int = DEFAULT_TIMEOUT
    track_costs: bool = True
    webhook_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "BotpressConfig":
        """Create configuration from environment variables."""
        api_key = os.environ.get("BOTPRESS_API_KEY")
        workspace_id = os.environ.get("BOTPRESS_WORKSPACE_ID")

        if not api_key or not workspace_id:
            raise BotpressConfigError(
                "Missing required environment variables: "
                "BOTPRESS_API_KEY and BOTPRESS_WORKSPACE_ID must be set"
            )

        return cls(
            api_key=api_key,
            workspace_id=workspace_id,
            base_url=os.environ.get(
                "BOTPRESS_BASE_URL", "https://api.botpress.cloud/v1"
            ),
            timeout=int(os.environ.get("BOTPRESS_TIMEOUT", str(DEFAULT_TIMEOUT))),
            track_costs=os.environ.get("BOTPRESS_TRACK_COSTS", "true").lower()
            == "true",
            webhook_secret=os.environ.get("BOTPRESS_WEBHOOK_SECRET"),
        )


class BotpressClient:
    """
    Client for interacting with the Botpress API.

    This class handles authentication, request formatting, and response parsing
    for all interactions with the Botpress platform.

    Attributes:
        config (BotpressConfig): Configuration for the client
        cost_tracker (Optional[CostTracker]): Tracks API usage costs if enabled
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace_id: Optional[str] = None,
        config: Optional[BotpressConfig] = None,
        cost_tracker: Optional[CostTracker] = None,
    ):
        """
        Initialize the Botpress client.

        Args:
            api_key: API key for Botpress authentication (optional if config provided)
            workspace_id: Botpress workspace ID (optional if config provided)
            config: Complete configuration object (takes precedence over individual params)
            cost_tracker: Cost tracker instance for monitoring API usage

        Raises:
            BotpressConfigError: If neither config nor required credentials are provided
        """
        if config:
            self.config = config
        elif api_key and workspace_id:
            self.config = BotpressConfig(api_key=api_key, workspace_id=workspace_id)
        else:
            try:
                self.config = BotpressConfig.from_env()
            except BotpressConfigError as e:
                raise BotpressConfigError(
                    "Botpress client initialization failed: provide either config, "
                    "credentials as parameters, or set environment variables"
                ) from e

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        )

        self.cost_tracker = cost_tracker
        if self.config.track_costs and not self.cost_tracker:
            try:
                self.cost_tracker = CostTracker(service_name="botpress")
            except Exception as e:
                logger.warning(f"Failed to initialize cost tracker: {e}")
                self.cost_tracker = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the Botpress API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base URL)
            data: Request body data
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            Dict containing the API response

        Raises:
            BotpressAPIError: For API-related errors
            BotpressError: For other errors
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.config.timeout

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method, url=url, json=data, params=params, timeout=timeout
                )

                if response.status_code >= 400:
                    error_msg = f"Request failed: {response.text}"
                    logger.error(error_msg)
                    raise BotpressAPIError(response.status_code, error_msg)

                # Track API usage if enabled
                if self.cost_tracker and method.upper() in ["POST", "PUT"]:
                    self._track_api_usage(method, endpoint, data)

                return response.json()

            except Timeout:
                logger.warning(
                    f"Request timed out (attempt {attempt + 1}/{MAX_RETRIES})"
                )
                if attempt == MAX_RETRIES - 1:
                    raise BotpressError(
                        f"Request to {url} timed out after {MAX_RETRIES} attempts"
                    )
                time.sleep(RETRY_DELAY)

            except RequestException as e:
                logger.error(f"Request error: {str(e)}")
                raise BotpressError(f"Request failed: {str(e)}")

    def _track_api_usage(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]]
    ) -> None:
        """Track API usage costs."""
        if not self.cost_tracker:
            return

        # Estimate token usage based on request data
        input_tokens = len(json.dumps(data)) // 4 if data else 0

        try:
            self.cost_tracker.track_request(
                model="botpress",
                input_tokens=input_tokens,
                output_tokens=0,  # Will be updated when response is received
                endpoint=f"{method}:{endpoint}",
            )
        except Exception as e:
            logger.warning(f"Failed to track API usage: {e}")

    def create_bot(
        self, name: str, bot_type: BotType, description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new bot in the Botpress workspace.

        Args:
            name: Name of the bot
            bot_type: Type of bot to create
            description: Bot description

        Returns:
            Dict containing the created bot details
        """
        data = {
            "name": name,
            "type": bot_type.value,
            "description": description,
            "workspace_id": self.config.workspace_id,
        }

        return self._make_request("POST", "/bots", data=data)

    def get_bot(self, bot_id: str) -> Dict[str, Any]:
        """
        Get details of a specific bot.

        Args:
            bot_id: ID of the bot

        Returns:
            Dict containing bot details
        """
        return self._make_request("GET", f"/bots/{bot_id}")

    def list_bots(self) -> List[Dict[str, Any]]:
        """
        List all bots in the workspace.

        Returns:
            List of bot details
        """
        response = self._make_request(
            "GET", "/bots", params={"workspace_id": self.config.workspace_id}
        )
        return response.get("bots", [])

    def send_message(
        self,
        bot_id: str,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a bot and get the response.

        Args:
            bot_id: ID of the bot to message
            user_id: ID of the user sending the message
            message: Text content of the message
            conversation_id: Optional conversation ID for continuing a conversation

        Returns:
            Dict containing the bot's response
        """
        data = {"bot_id": bot_id, "user_id": user_id, "message": message}

        if conversation_id:
            data["conversation_id"] = conversation_id

        return self._make_request("POST", "/conversations/messages", data=data)

    def create_flow(self, bot_id: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a conversation flow for a bot.

        Args:
            bot_id: ID of the bot
            flow_data: Flow definition data

        Returns:
            Dict containing the created/updated flow details
        """
        data = {"bot_id": bot_id, "flow": flow_data}

        return self._make_request("POST", "/flows", data=data)

    def register_webhook(
        self, bot_id: str, url: str, events: List[str], secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a webhook for bot events.

        Args:
            bot_id: ID of the bot
            url: Webhook URL to receive events
            events: List of event types to subscribe to
            secret: Secret for webhook verification

        Returns:
            Dict containing the webhook registration details
        """
        data = {"bot_id": bot_id, "url": url, "events": events}

        if secret or self.config.webhook_secret:
            data["secret"] = secret or self.config.webhook_secret

        return self._make_request("POST", "/webhooks", data=data)


class BaseBot(ABC):
    """
    Abstract base class for all Botpress bot implementations.

    Provides common functionality and enforces implementation
    of required methods for specific bot types.
    """

    def __init__(
        self,
        client: BotpressClient,
        bot_id: Optional[str] = None,
        bot_name: Optional[str] = None,
        bot_type: BotType = BotType.CUSTOM,
    ):
        """
        Initialize a bot instance.

        Args:
            client: BotpressClient instance for API communication
            bot_id: Existing bot ID (if None, a new bot will be created)
            bot_name: Name for the bot (required if bot_id is None)
            bot_type: Type of bot to create

        Raises:
            BotpressConfigError: If neither bot_id nor bot_name is provided
        """
        self.client = client
        self.bot_type = bot_type

        if bot_id:
            self.bot_id = bot_id
            try:
                bot_details = self.client.get_bot(bot_id)
                self.bot_name = bot_details.get("name", "Unknown Bot")
                logger.info(f"Using existing bot: {self.bot_name} ({self.bot_id})")
            except BotpressError as e:
                logger.error(f"Failed to get bot details: {e}")
                raise
        elif bot_name:
            try:
                # Create a new bot
                bot_details = self.client.create_bot(
                    name=bot_name,
                    bot_type=bot_type,
                    description=self._get_default_description(),
                )
                self.bot_id = bot_details.get("id")
                self.bot_name = bot_name
                logger.info(f"Created new bot: {self.bot_name} ({self.bot_id})")

                # Set up default flows
                self._setup_default_flows()
            except BotpressError as e:
                logger.error(f"Failed to create bot: {e}")
                raise
        else:
            raise BotpressConfigError("Either bot_id or bot_name must be provided")

    def _get_default_description(self) -> str:
        """Get default description based on bot type."""
        descriptions = {
            BotType.AUTHOR_INTERVIEW: "Conducts structured interviews to extract book content",
            BotType.READER_FEEDBACK: "Collects reader insights and feedback",
            BotType.WRITING_COACH: "Provides real-time writing assistance",
            BotType.MARKETING: "Handles marketing and sales conversations",
            BotType.CUSTOM: "Custom KindleMint bot",
        }
        return descriptions.get(self.bot_type, "KindleMint Botpress Integration")

    @abstractmethod
    def _setup_default_flows(self) -> None:
        """
        Set up default conversation flows for the bot.

        This method should be implemented by each specific bot type.
        """

    def send_message(
        self, user_id: str, message: str, conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the bot and get the response.

        Args:
            user_id: ID of the user sending the message
            message: Text content of the message
            conversation_id: Optional conversation ID for continuing a conversation

        Returns:
            Dict containing the bot's response
        """
        return self.client.send_message(
            bot_id=self.bot_id,
            user_id=user_id,
            message=message,
            conversation_id=conversation_id,
        )

    def register_webhook(
        self, url: str, events: List[str], secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a webhook for bot events.

        Args:
            url: Webhook URL to receive events
            events: List of event types to subscribe to
            secret: Secret for webhook verification

        Returns:
            Dict containing the webhook registration details
        """
        return self.client.register_webhook(
            bot_id=self.bot_id, url=url, events=events, secret=secret
        )


class AuthorInterviewBot(BaseBot):
    """
    Bot that conducts structured interviews to extract book content from authors.

    This bot guides authors through a series of questions to help them articulate
    their ideas, organize content, and develop their book structure.
    """

    def __init__(
        self,
        client: BotpressClient,
        bot_id: Optional[str] = None,
        bot_name: str = "KindleMint Author Interview",
    ):
        """
        Initialize an author interview bot.

        Args:
            client: BotpressClient instance for API communication
            bot_id: Existing bot ID (if None, a new bot will be created)
            bot_name: Name for the bot (used if creating a new bot)
        """
        super().__init__(
            client=client,
            bot_id=bot_id,
            bot_name=bot_name,
            bot_type=BotType.AUTHOR_INTERVIEW,
        )

    def _setup_default_flows(self) -> None:
        """Set up default conversation flows for author interviews."""
        # Create main interview flow
        interview_flow = {
            "name": "author_interview",
            "nodes": [
                {
                    "id": "welcome",
                    "type": "standard",
                    "content": {
                        "text": "Welcome to KindleMint Author Interview! I'll help you extract and organize your book ideas through a structured conversation."
                    },
                    "next": "book_topic",
                },
                {
                    "id": "book_topic",
                    "type": "question",
                    "content": {
                        "text": "What is the main topic or theme of your book?",
                        "variable": "book_topic",
                    },
                    "next": "target_audience",
                },
                {
                    "id": "target_audience",
                    "type": "question",
                    "content": {
                        "text": "Who is your target audience for this book?",
                        "variable": "target_audience",
                    },
                    "next": "key_sections",
                },
                {
                    "id": "key_sections",
                    "type": "question",
                    "content": {
                        "text": "What are the main sections or chapters you envision for your book?",
                        "variable": "key_sections",
                    },
                    "next": "summary",
                },
                {
                    "id": "summary",
                    "type": "standard",
                    "content": {
                        "text": "Great! Here's a summary of what we've discussed:\n\nTopic: {{book_topic}}\nAudience: {{target_audience}}\nKey Sections: {{key_sections}}\n\nI'll now ask more detailed questions about each section."
                    },
                    "next": "section_details",
                },
                {
                    "id": "section_details",
                    "type": "code",
                    "content": {
                        "script": "// Parse sections and create follow-up questions\nconst sections = bp.session.key_sections.split(',').map(s => s.trim());\nbp.session.current_section_index = 0;\nbp.session.sections = sections;\nbp.session.section_details = [];\nreturn 'section_loop';"
                    },
                    "next": "section_loop",
                },
                {
                    "id": "section_loop",
                    "type": "code",
                    "content": {
                        "script": "if (bp.session.current_section_index < bp.session.sections.length) {\n  bp.session.current_section = bp.session.sections[bp.session.current_section_index];\n  return 'ask_section_detail';\n} else {\n  return 'interview_complete';\n}"
                    },
                    "next": ["ask_section_detail", "interview_complete"],
                },
                {
                    "id": "ask_section_detail",
                    "type": "question",
                    "content": {
                        "text": 'Tell me more about the section "{{current_section}}":',
                        "variable": "current_section_detail",
                    },
                    "next": "store_section_detail",
                },
                {
                    "id": "store_section_detail",
                    "type": "code",
                    "content": {
                        "script": "bp.session.section_details.push({\n  title: bp.session.current_section,\n  content: bp.session.current_section_detail\n});\nbp.session.current_section_index++;\nreturn 'section_loop';"
                    },
                    "next": "section_loop",
                },
                {
                    "id": "interview_complete",
                    "type": "standard",
                    "content": {
                        "text": "Thank you! I've collected all the information. This will be processed into your book structure. You can continue refining these ideas or ask me specific questions about any section."
                    },
                    "next": "webhook_trigger",
                },
                {
                    "id": "webhook_trigger",
                    "type": "code",
                    "content": {
                        "script": "// Trigger webhook to KindleMint\nconst bookData = {\n  topic: bp.session.book_topic,\n  audience: bp.session.target_audience,\n  sections: bp.session.section_details\n};\nbp.session.book_data = bookData;\n// Webhook would be triggered here in production\nreturn 'end';"
                    },
                    "next": "end",
                },
                {
                    "id": "end",
                    "type": "standard",
                    "content": {
                        "text": "Your book outline has been sent to KindleMint for processing. You'll receive a notification when it's ready for review."
                    },
                },
            ],
        }

        try:
            self.client.create_flow(self.bot_id, interview_flow)
            logger.info(f"Created default interview flow for bot {self.bot_id}")
        except BotpressError as e:
            logger.error(f"Failed to create interview flow: {e}")
            # Continue without failing, as the bot can still function with default flows

    def conduct_interview(
        self, author_id: str, book_topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct an author interview to extract book content.

        Args:
            author_id: Unique identifier for the author
            book_topic: Optional initial book topic to start the conversation

        Returns:
            Dict containing the interview results and extracted content
        """
        # Start conversation
        conversation_id = f"interview_{author_id}_{int(time.time())}"

        # Send initial message
        initial_message = "Hi, I'm ready to discuss my book idea."
        if book_topic:
            initial_message = f"Hi, I want to write a book about {book_topic}."

        response = self.send_message(
            user_id=author_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "started",
            "initial_response": response,
            "instructions": "Continue the conversation by sending messages to the same conversation_id.",
        }

    def extract_book_structure(self, conversation_id: str) -> Dict[str, Any]:
        """
        Extract structured book content from a completed interview.

        Args:
            conversation_id: ID of the completed interview conversation

        Returns:
            Dict containing the structured book content
        """
        # In a real implementation, this would query the conversation history
        # and extract the structured data using the Botpress API

        # For now, return a placeholder
        return {
            "conversation_id": conversation_id,
            "status": "processing",
            "message": "Book structure extraction in progress. This may take a few minutes.",
        }


class ReaderFeedbackBot(BaseBot):
    """
    Bot that collects insights and feedback from readers.

    This bot engages with readers after they've consumed content to gather
    feedback, ratings, and suggestions for improvement.
    """

    def __init__(
        self,
        client: BotpressClient,
        bot_id: Optional[str] = None,
        bot_name: str = "KindleMint Reader Feedback",
    ):
        """
        Initialize a reader feedback bot.

        Args:
            client: BotpressClient instance for API communication
            bot_id: Existing bot ID (if None, a new bot will be created)
            bot_name: Name for the bot (used if creating a new bot)
        """
        super().__init__(
            client=client,
            bot_id=bot_id,
            bot_name=bot_name,
            bot_type=BotType.READER_FEEDBACK,
        )

    def _setup_default_flows(self) -> None:
        """Set up default conversation flows for reader feedback."""
        # Create feedback survey flow
        feedback_flow = {
            "name": "reader_feedback",
            "nodes": [
                {
                    "id": "welcome",
                    "type": "standard",
                    "content": {
                        "text": "Thank you for reading! I'd love to get your feedback to help improve future content."
                    },
                    "next": "rating_question",
                },
                {
                    "id": "rating_question",
                    "type": "choice",
                    "content": {
                        "text": "On a scale of 1-5, how would you rate this book?",
                        "choices": ["1", "2", "3", "4", "5"],
                        "variable": "book_rating",
                    },
                    "next": "favorite_part",
                },
                {
                    "id": "favorite_part",
                    "type": "question",
                    "content": {
                        "text": "What was your favorite part of the book?",
                        "variable": "favorite_part",
                    },
                    "next": "improvement_question",
                },
                {
                    "id": "improvement_question",
                    "type": "question",
                    "content": {
                        "text": "What could be improved in future editions?",
                        "variable": "improvement_suggestion",
                    },
                    "next": "recommendation_question",
                },
                {
                    "id": "recommendation_question",
                    "type": "choice",
                    "content": {
                        "text": "Would you recommend this book to others?",
                        "choices": ["Yes, definitely", "Maybe", "No"],
                        "variable": "would_recommend",
                    },
                    "next": "summary",
                },
                {
                    "id": "summary",
                    "type": "standard",
                    "content": {
                        "text": "Thank you for your feedback! Here's a summary:\n\nRating: {{book_rating}}/5\nFavorite part: {{favorite_part}}\nSuggestion: {{improvement_suggestion}}\nWould recommend: {{would_recommend}}"
                    },
                    "next": "webhook_trigger",
                },
                {
                    "id": "webhook_trigger",
                    "type": "code",
                    "content": {
                        "script": "// Trigger webhook to KindleMint\nconst feedbackData = {\n  rating: parseInt(bp.session.book_rating),\n  favorite_part: bp.session.favorite_part,\n  improvement: bp.session.improvement_suggestion,\n  would_recommend: bp.session.would_recommend\n};\nbp.session.feedback_data = feedbackData;\n// Webhook would be triggered here in production\nreturn 'end';"
                    },
                    "next": "end",
                },
                {
                    "id": "end",
                    "type": "standard",
                    "content": {
                        "text": "Your feedback has been recorded. Thank you for helping us improve!"
                    },
                },
            ],
        }

        try:
            self.client.create_flow(self.bot_id, feedback_flow)
            logger.info(f"Created default feedback flow for bot {self.bot_id}")
        except BotpressError as e:
            logger.error(f"Failed to create feedback flow: {e}")

    def collect_feedback(
        self, reader_id: str, book_id: str, book_title: str
    ) -> Dict[str, Any]:
        """
        Start a feedback collection conversation with a reader.

        Args:
            reader_id: Unique identifier for the reader
            book_id: ID of the book being reviewed
            book_title: Title of the book

        Returns:
            Dict containing the conversation details
        """
        conversation_id = f"feedback_{reader_id}_{book_id}_{int(time.time())}"

        # Customize the initial message with book details
        initial_message = (
            f"I just finished reading {book_title} and I'm ready to give feedback."
        )

        response = self.send_message(
            user_id=reader_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "started",
            "initial_response": response,
            "instructions": "Continue the conversation to complete the feedback survey.",
        }

    def get_feedback_summary(
        self, book_id: str, min_rating: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of reader feedback for a specific book.

        Args:
            book_id: ID of the book
            min_rating: Optional minimum rating filter

        Returns:
            Dict containing feedback summary statistics
        """
        # In a real implementation, this would query the feedback database
        # For now, return a placeholder
        return {
            "book_id": book_id,
            "status": "processing",
            "message": "Feedback summary generation in progress.",
        }


class WritingCoachBot(BaseBot):
    """
    Bot that provides real-time writing assistance.

    This bot helps authors improve their writing by offering style suggestions,
    helping overcome writer's block, and providing feedback on drafts.
    """

    def __init__(
        self,
        client: BotpressClient,
        bot_id: Optional[str] = None,
        bot_name: str = "KindleMint Writing Coach",
    ):
        """
        Initialize a writing coach bot.

        Args:
            client: BotpressClient instance for API communication
            bot_id: Existing bot ID (if None, a new bot will be created)
            bot_name: Name for the bot (used if creating a new bot)
        """
        super().__init__(
            client=client,
            bot_id=bot_id,
            bot_name=bot_name,
            bot_type=BotType.WRITING_COACH,
        )

    def _setup_default_flows(self) -> None:
        """Set up default conversation flows for writing coaching."""
        # Create writing coach flow
        coach_flow = {
            "name": "writing_coach",
            "nodes": [
                {
                    "id": "welcome",
                    "type": "standard",
                    "content": {
                        "text": "Welcome to your KindleMint Writing Coach! I'm here to help you improve your writing and overcome creative challenges."
                    },
                    "next": "coaching_menu",
                },
                {
                    "id": "coaching_menu",
                    "type": "choice",
                    "content": {
                        "text": "How can I help you today?",
                        "choices": [
                            "Get feedback on my writing",
                            "Help with writer's block",
                            "Style suggestions",
                            "Set writing goals",
                        ],
                        "variable": "coaching_need",
                    },
                    "next": "route_request",
                },
                {
                    "id": "route_request",
                    "type": "code",
                    "content": {
                        "script": "switch(bp.session.coaching_need) {\n  case 'Get feedback on my writing':\n    return 'feedback_flow';\n  case 'Help with writer\\'s block':\n    return 'writers_block_flow';\n  case 'Style suggestions':\n    return 'style_flow';\n  case 'Set writing goals':\n    return 'goals_flow';\n  default:\n    return 'feedback_flow';\n}"
                    },
                    "next": [
                        "feedback_flow",
                        "writers_block_flow",
                        "style_flow",
                        "goals_flow",
                    ],
                },
                {
                    "id": "feedback_flow",
                    "type": "question",
                    "content": {
                        "text": "Please share a paragraph or section you'd like feedback on:",
                        "variable": "writing_sample",
                    },
                    "next": "analyze_writing",
                },
                {
                    "id": "analyze_writing",
                    "type": "code",
                    "content": {
                        "script": "// In production, this would analyze the text\n// For now, return generic feedback\nbp.session.writing_feedback = 'Your writing shows good structure. Consider using more descriptive language and varying sentence length for better flow.';\nreturn 'provide_feedback';"
                    },
                    "next": "provide_feedback",
                },
                {
                    "id": "provide_feedback",
                    "type": "standard",
                    "content": {
                        "text": "Here's my feedback on your writing:\n\n{{writing_feedback}}"
                    },
                    "next": "coaching_menu",
                },
                {
                    "id": "writers_block_flow",
                    "type": "standard",
                    "content": {
                        "text": "Writer's block happens to everyone. Let's try some exercises to get your creativity flowing again."
                    },
                    "next": "block_exercise",
                },
                {
                    "id": "block_exercise",
                    "type": "question",
                    "content": {
                        "text": "Complete this sentence: 'The character opened the door and saw...'",
                        "variable": "exercise_response",
                    },
                    "next": "exercise_feedback",
                },
                {
                    "id": "exercise_feedback",
                    "type": "standard",
                    "content": {
                        "text": "Great start! Now try expanding on that idea for 5 minutes without stopping. Don't worry about quality, just keep writing."
                    },
                    "next": "coaching_menu",
                },
                {
                    "id": "style_flow",
                    "type": "standard",
                    "content": {
                        "text": "I can help you refine your writing style. Let me ask a few questions about your preferences."
                    },
                    "next": "style_question",
                },
                {
                    "id": "style_question",
                    "type": "choice",
                    "content": {
                        "text": "Which writing style do you prefer?",
                        "choices": [
                            "Concise and direct",
                            "Descriptive and vivid",
                            "Conversational and casual",
                            "Formal and academic",
                        ],
                        "variable": "preferred_style",
                    },
                    "next": "style_tips",
                },
                {
                    "id": "style_tips",
                    "type": "code",
                    "content": {
                        "script": "// Generate style tips based on preference\nlet tips = '';\nswitch(bp.session.preferred_style) {\n  case 'Concise and direct':\n    tips = 'Use short sentences. Avoid adverbs. Choose strong verbs. Eliminate filler words.';\n    break;\n  case 'Descriptive and vivid':\n    tips = 'Engage all five senses. Use specific, concrete details. Vary your sentence structure. Consider metaphors and similes.';\n    break;\n  case 'Conversational and casual':\n    tips = 'Write like you talk. Use contractions. Ask questions. Include personal anecdotes. Vary sentence length.';\n    break;\n  case 'Formal and academic':\n    tips = 'Use precise terminology. Maintain third-person perspective. Support claims with evidence. Avoid colloquialisms.';\n    break;\n  default:\n    tips = 'Focus on clarity. Revise thoroughly. Read your work aloud.';\n}\nbp.session.style_tips = tips;\nreturn 'show_style_tips';"
                    },
                    "next": "show_style_tips",
                },
                {
                    "id": "show_style_tips",
                    "type": "standard",
                    "content": {
                        "text": "Tips for {{preferred_style}} writing:\n\n{{style_tips}}"
                    },
                    "next": "coaching_menu",
                },
                {
                    "id": "goals_flow",
                    "type": "question",
                    "content": {
                        "text": "What's your daily writing goal (in words or minutes)?",
                        "variable": "writing_goal",
                    },
                    "next": "confirm_goal",
                },
                {
                    "id": "confirm_goal",
                    "type": "standard",
                    "content": {
                        "text": "Great! I've set your daily goal to {{writing_goal}}. I'll check in with you regularly to help you stay on track."
                    },
                    "next": "coaching_menu",
                },
            ],
        }

        try:
            self.client.create_flow(self.bot_id, coach_flow)
            logger.info(f"Created default writing coach flow for bot {self.bot_id}")
        except BotpressError as e:
            logger.error(f"Failed to create writing coach flow: {e}")

    def start_coaching(
        self, author_id: str, initial_need: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a writing coaching conversation.

        Args:
            author_id: Unique identifier for the author
            initial_need: Optional specific coaching need to start with

        Returns:
            Dict containing the conversation details
        """
        conversation_id = f"coaching_{author_id}_{int(time.time())}"

        # Customize the initial message based on coaching need
        initial_message = "I'd like some writing help."
        if initial_need:
            initial_message = f"I need help with {initial_need}."

        response = self.send_message(
            user_id=author_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "started",
            "initial_response": response,
            "instructions": "Continue the conversation to get writing assistance.",
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze a piece of writing and provide feedback.

        Args:
            text: The text to analyze

        Returns:
            Dict containing analysis results and suggestions
        """
        # In a real implementation, this would use NLP to analyze the text
        # For now, return placeholder feedback
        return {
            "word_count": len(text.split()),
            "readability_score": "intermediate",
            "suggestions": [
                "Consider varying sentence length for better rhythm",
                "Add more sensory details to engage readers",
                "Check for passive voice and convert to active where appropriate",
            ],
        }


class ConversationalMarketingBot(BaseBot):
    """
    Bot that handles marketing and sales conversations.

    This bot qualifies leads, recommends books, promotes premium content,
    and facilitates webinar registrations through natural conversations.
    """

    def __init__(
        self,
        client: BotpressClient,
        bot_id: Optional[str] = None,
        bot_name: str = "KindleMint Marketing Assistant",
    ):
        """
        Initialize a conversational marketing bot.

        Args:
            client: BotpressClient instance for API communication
            bot_id: Existing bot ID (if None, a new bot will be created)
            bot_name: Name for the bot (used if creating a new bot)
        """
        super().__init__(
            client=client, bot_id=bot_id, bot_name=bot_name, bot_type=BotType.MARKETING
        )

        self.engagement_flows = {
            "lead_qualification": self.qualify_prospects,
            "book_recommendation": self.suggest_books,
            "upsell_conversation": self.promote_premium,
            "webinar_registration": self.book_seats,
        }

    def _setup_default_flows(self) -> None:
        """Set up default conversation flows for marketing."""
        # Create marketing flow
        marketing_flow = {
            "name": "marketing_assistant",
            "nodes": [
                {
                    "id": "welcome",
                    "type": "standard",
                    "content": {
                        "text": "Welcome to KindleMint! I'm here to help you find the perfect books and resources for your needs."
                    },
                    "next": "intent_menu",
                },
                {
                    "id": "intent_menu",
                    "type": "choice",
                    "content": {
                        "text": "How can I assist you today?",
                        "choices": [
                            "Find a book recommendation",
                            "Learn about premium features",
                            "Register for a webinar",
                            "Get publishing advice",
                        ],
                        "variable": "user_intent",
                    },
                    "next": "route_intent",
                },
                {
                    "id": "route_intent",
                    "type": "code",
                    "content": {
                        "script": "switch(bp.session.user_intent) {\n  case 'Find a book recommendation':\n    return 'recommendation_flow';\n  case 'Learn about premium features':\n    return 'premium_flow';\n  case 'Register for a webinar':\n    return 'webinar_flow';\n  case 'Get publishing advice':\n    return 'publishing_flow';\n  default:\n    return 'recommendation_flow';\n}"
                    },
                    "next": [
                        "recommendation_flow",
                        "premium_flow",
                        "webinar_flow",
                        "publishing_flow",
                    ],
                },
                # Recommendation flow nodes
                {
                    "id": "recommendation_flow",
                    "type": "question",
                    "content": {
                        "text": "What type of books are you interested in?",
                        "variable": "book_interest",
                    },
                    "next": "ask_experience",
                },
                {
                    "id": "ask_experience",
                    "type": "choice",
                    "content": {
                        "text": "What's your experience level with {{book_interest}}?",
                        "choices": ["Beginner", "Intermediate", "Advanced"],
                        "variable": "experience_level",
                    },
                    "next": "generate_recommendations",
                },
                {
                    "id": "generate_recommendations",
                    "type": "code",
                    "content": {
                        "script": "// In production, this would query a book database\n// For now, return placeholder recommendations\nbp.session.recommendations = [\n  {\n    title: `The Complete Guide to ${bp.session.book_interest}`,\n    description: `Perfect for ${bp.session.experience_level.toLowerCase()} readers.`\n  },\n  {\n    title: `${bp.session.book_interest} Mastery`,\n    description: 'Take your skills to the next level.'\n  },\n  {\n    title: `${bp.session.book_interest} Projects`,\n    description: 'Learn by doing with practical exercises.'\n  }\n];\nreturn 'show_recommendations';"
                    },
                    "next": "show_recommendations",
                },
                {
                    "id": "show_recommendations",
                    "type": "standard",
                    "content": {
                        "text": "Based on your interest in {{book_interest}} at a {{experience_level}} level, here are my recommendations:\n\n1. {{recommendations[0].title}} - {{recommendations[0].description}}\n2. {{recommendations[1].title}} - {{recommendations[1].description}}\n3. {{recommendations[2].title}} - {{recommendations[2].description}}\n\nWould you like more information about any of these books?"
                    },
                    "next": "capture_lead",
                },
                {
                    "id": "capture_lead",
                    "type": "question",
                    "content": {
                        "text": "Would you like me to email you these recommendations? If so, please share your email address:",
                        "variable": "email",
                    },
                    "next": "thank_user",
                },
                # Premium flow nodes
                {
                    "id": "premium_flow",
                    "type": "standard",
                    "content": {
                        "text": "KindleMint Premium gives you access to exclusive content, advanced tools, and personalized coaching. Here are the key benefits:"
                    },
                    "next": "premium_benefits",
                },
                {
                    "id": "premium_benefits",
                    "type": "standard",
                    "content": {
                        "text": "✅ Unlimited access to all puzzle books\n✅ Personalized writing coach\n✅ Priority publishing support\n✅ Exclusive webinars and workshops\n✅ Advanced analytics dashboard"
                    },
                    "next": "premium_pricing",
                },
                {
                    "id": "premium_pricing",
                    "type": "choice",
                    "content": {
                        "text": "Premium membership is just $19.99/month or $199/year (save 17%). Would you like to learn more?",
                        "choices": ["Yes, tell me more", "No, maybe later"],
                        "variable": "premium_interest",
                    },
                    "next": "route_premium_interest",
                },
                {
                    "id": "route_premium_interest",
                    "type": "code",
                    "content": {
                        "script": "if (bp.session.premium_interest === 'Yes, tell me more') {\n  return 'premium_details';\n} else {\n  return 'thank_user';\n}"
                    },
                    "next": ["premium_details", "thank_user"],
                },
                {
                    "id": "premium_details",
                    "type": "question",
                    "content": {
                        "text": "Great! I'd be happy to send you more information about our premium features. What's your email address?",
                        "variable": "email",
                    },
                    "next": "premium_confirmation",
                },
                {
                    "id": "premium_confirmation",
                    "type": "standard",
                    "content": {
                        "text": "Thank you! I've sent premium membership details to {{email}}. Check your inbox in the next few minutes."
                    },
                    "next": "thank_user",
                },
                # Webinar flow nodes
                {
                    "id": "webinar_flow",
                    "type": "standard",
                    "content": {
                        "text": "We offer regular webinars on publishing, writing, and marketing. Here are our upcoming sessions:"
                    },
                    "next": "webinar_list",
                },
                {
                    "id": "webinar_list",
                    "type": "choice",
                    "content": {
                        "text": "Which webinar are you interested in?",
                        "choices": [
                            "Self-Publishing Masterclass (Tuesday)",
                            "Marketing Your Book (Thursday)",
                            "Writing Effective Puzzle Books (Saturday)",
                        ],
                        "variable": "webinar_choice",
                    },
                    "next": "webinar_registration",
                },
                {
                    "id": "webinar_registration",
                    "type": "question",
                    "content": {
                        "text": "Great choice! To register for {{webinar_choice}}, I'll need your email address:",
                        "variable": "email",
                    },
                    "next": "webinar_confirmation",
                },
                {
                    "id": "webinar_confirmation",
                    "type": "standard",
                    "content": {
                        "text": "You're all set! I've registered you for {{webinar_choice}}. A confirmation email with joining instructions has been sent to {{email}}."
                    },
                    "next": "thank_user",
                },
                # Publishing flow nodes
                {
                    "id": "publishing_flow",
                    "type": "question",
                    "content": {
                        "text": "What specific aspect of publishing are you interested in learning about?",
                        "variable": "publishing_interest",
                    },
                    "next": "publishing_advice",
                },
                {
                    "id": "publishing_advice",
                    "type": "code",
                    "content": {
                        "script": "// Generate advice based on interest\nlet advice = `Here's some advice about ${bp.session.publishing_interest}:\\n\\n`;\n\nif (bp.session.publishing_interest.toLowerCase().includes('amazon') || \n    bp.session.publishing_interest.toLowerCase().includes('kdp')) {\n  advice += '1. Ensure your book meets KDP formatting guidelines\\n';\n  advice += '2. Invest time in keyword research for better discoverability\\n';\n  advice += '3. Price competitively for your category\\n';\n  advice += '4. Consider enrolling in KDP Select for additional benefits';\n} else if (bp.session.publishing_interest.toLowerCase().includes('cover') || \n           bp.session.publishing_interest.toLowerCase().includes('design')) {\n  advice += '1. Research successful covers in your genre\\n';\n  advice += '2. Ensure text is readable in thumbnail size\\n';\n  advice += '3. Use high-quality images and typography\\n';\n  advice += '4. Consider professional design for best results';\n} else {\n  advice += '1. Start with a clear publishing goal\\n';\n  advice += '2. Research your target audience thoroughly\\n';\n  advice += '3. Create a marketing plan before publishing\\n';\n  advice += '4. Consider both digital and print formats';\n}\n\nbp.session.publishing_advice = advice;\nreturn 'show_publishing_advice';"
                    },
                    "next": "show_publishing_advice",
                },
                {
                    "id": "show_publishing_advice",
                    "type": "standard",
                    "content": {"text": "{{publishing_advice}}"},
                    "next": "publishing_resources",
                },
                {
                    "id": "publishing_resources",
                    "type": "question",
                    "content": {
                        "text": "Would you like me to email you some resources about {{publishing_interest}}? If so, please share your email:",
                        "variable": "email",
                    },
                    "next": "thank_user",
                },
                # Common end node
                {
                    "id": "thank_user",
                    "type": "standard",
                    "content": {
                        "text": "Thank you for chatting with KindleMint! Is there anything else I can help you with?"
                    },
                    "next": "intent_menu",
                },
            ],
        }

        try:
            self.client.create_flow(self.bot_id, marketing_flow)
            logger.info(f"Created default marketing flow for bot {self.bot_id}")
        except BotpressError as e:
            logger.error(f"Failed to create marketing flow: {e}")

    def qualify_prospects(
        self, user_id: str, initial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a lead qualification conversation.

        Args:
            user_id: Unique identifier for the user
            initial_data: Optional initial data about the prospect

        Returns:
            Dict containing the conversation details
        """
        conversation_id = f"qualify_{user_id}_{int(time.time())}"

        # Start with a custom message if we have initial data
        initial_message = "I'm interested in KindleMint."
        if initial_data and "interest" in initial_data:
            initial_message = f"I'm interested in {initial_data['interest']}."

        response = self.send_message(
            user_id=user_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "qualification_started",
            "initial_response": response,
        }

    def suggest_books(
        self, user_id: str, interests: List[str], experience_level: str = "Beginner"
    ) -> Dict[str, Any]:
        """
        Start a book recommendation conversation.

        Args:
            user_id: Unique identifier for the user
            interests: List of book topics the user is interested in
            experience_level: User's experience level

        Returns:
            Dict containing the conversation details
        """
        conversation_id = f"recommend_{user_id}_{int(time.time())}"

        # Craft an initial message based on interests
        interests_str = ", ".join(interests)
        initial_message = f"I'm looking for book recommendations about {
            interests_str}. I'm at a {experience_level} level."

        response = self.send_message(
            user_id=user_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "recommendation_started",
            "initial_response": response,
        }

    def promote_premium(self, user_id: str) -> Dict[str, Any]:
        """
        Start a conversation to promote premium features.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dict containing the conversation details
        """
        conversation_id = f"premium_{user_id}_{int(time.time())}"

        initial_message = "I'd like to learn about premium features."

        response = self.send_message(
            user_id=user_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "premium_promotion_started",
            "initial_response": response,
        }

    def book_seats(
        self, user_id: str, webinar_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a webinar registration conversation.

        Args:
            user_id: Unique identifier for the user
            webinar_id: Optional specific webinar ID

        Returns:
            Dict containing the conversation details
        """
        conversation_id = f"webinar_{user_id}_{int(time.time())}"

        # Customize based on webinar ID if provided
        initial_message = "I'm interested in registering for a webinar."
        if webinar_id:
            initial_message = f"I want to register for webinar {webinar_id}."

        response = self.send_message(
            user_id=user_id, message=initial_message, conversation_id=conversation_id
        )

        return {
            "conversation_id": conversation_id,
            "status": "webinar_registration_started",
            "initial_response": response,
        }


class WebhookHandler:
    """
    Handler for processing incoming webhooks from Botpress.

    This class validates and processes webhook events from Botpress,
    routing them to the appropriate handlers based on event type.
    """

    def __init__(self, config: Optional[BotpressConfig] = None):
        """
        Initialize the webhook handler.

        Args:
            config: Optional Botpress configuration with webhook secret
        """
        self.config = config or BotpressConfig.from_env()
        self.event_handlers: Dict[str, Callable] = {}

    def register_handler(self, event_type: str, handler_func: Callable) -> None:
        """
        Register a handler function for a specific event type.

        Args:
            event_type: Type of event to handle (e.g., 'conversation.started')
            handler_func: Function to call when this event is received
        """
        self.event_handlers[event_type] = handler_func
        logger.info(f"Registered handler for event type: {event_type}")

    def validate_webhook(self, headers: Dict[str, str], body: str) -> bool:
        """
        Validate that a webhook request is authentic.

        Args:
            headers: Request headers including signature
            body: Raw request body

        Returns:
            True if the webhook is valid, False otherwise
        """
        if not self.config.webhook_secret:
            logger.warning("No webhook secret configured, skipping validation")
            return True

        # In a real implementation, this would verify the signature
        # using the webhook secret and request body

        # For now, return True (assume valid)
        return True

    def process_webhook(
        self, headers: Dict[str, str], body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an incoming webhook from Botpress.

        Args:
            headers: Request headers
            body: Parsed request body

        Returns:
            Dict containing the processing result

        Raises:
            BotpressWebhookError: If webhook processing fails
        """
        # Validate the webhook
        if not self.validate_webhook(headers, json.dumps(body)):
            raise BotpressWebhookError("Invalid webhook signature")

        # Extract event type and data
        event_type = body.get("type")
        if not event_type:
            raise BotpressWebhookError("Missing event type in webhook")

        # Find and call the appropriate handler
        handler = self.event_handlers.get(event_type)
        if handler:
            try:
                result = handler(body)
                logger.info(f"Successfully processed {event_type} webhook")
                return result
            except Exception as e:
                logger.error(f"Error in webhook handler for {event_type}: {e}")
                raise BotpressWebhookError(f"Handler error: {str(e)}")
        else:
            logger.warning(f"No handler registered for event type: {event_type}")
            return {"status": "unhandled", "event_type": event_type}


# Integration with KindleMint MoA (Mixture of Agents)
def integrate_with_moa(
    bot_response: Dict[str, Any], moa_endpoint: str = "/api/v1/conversation_to_content"
) -> Dict[str, Any]:
    """
    Integrate Botpress conversation data with KindleMint MoA.

    Args:
        bot_response: Response data from a Botpress conversation
        moa_endpoint: API endpoint for the MoA integration

    Returns:
        Dict containing the MoA processing result
    """
    try:
        api_manager = APIManager()
        result = api_manager.post(
            endpoint=moa_endpoint,
            data=bot_response,
            timeout=60,  # Longer timeout for MoA processing
        )
        return result
    except Exception as e:
        logger.error(f"Failed to integrate with MoA: {e}")
        raise
