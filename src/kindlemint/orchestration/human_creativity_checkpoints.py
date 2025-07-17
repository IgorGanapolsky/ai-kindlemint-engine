"""
Human-in-the-Loop Creativity Checkpoints for KindleMint

This module formalizes human oversight at critical stages of the publishing pipeline,
ensuring AI-generated content aligns with brand and quality standards.
Based on the principle that human creativity is the indispensable final layer.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from abc import ABC, abstractmethod
import asyncio


logger = logging.getLogger(__name__)


class CheckpointType(Enum):
    """Types of human review checkpoints"""
    TITLE_SELECTION = "title_selection"
    COVER_PROMPT_APPROVAL = "cover_prompt_approval"
    MARKETING_ANGLE_SELECTION = "marketing_angle_selection"
    BOOK_DESCRIPTION_REVIEW = "book_description_review"
    CATEGORY_SELECTION = "category_selection"
    PRICING_STRATEGY = "pricing_strategy"
    SERIES_PLANNING = "series_planning"
    CONTENT_QUALITY_REVIEW = "content_quality_review"
    BRAND_ALIGNMENT = "brand_alignment"
    FINAL_APPROVAL = "final_approval"


class ApprovalStatus(Enum):
    """Status of human approval"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"
    EXPIRED = "expired"


class Priority(Enum):
    """Priority levels for review"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CreativeOption:
    """Represents a single creative option for human review"""
    option_id: str
    content: Any  # Could be string, dict, etc.
    ai_score: float  # AI's confidence/quality score (0-1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "option_id": self.option_id,
            "content": self.content,
            "ai_score": self.ai_score,
            "metadata": self.metadata
        }


@dataclass
class CheckpointRequest:
    """Request for human creativity review"""
    request_id: str
    checkpoint_type: CheckpointType
    book_id: str
    options: List[CreativeOption]
    context: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "checkpoint_type": self.checkpoint_type.value,
            "book_id": self.book_id,
            "options": [opt.to_dict() for opt in self.options],
            "context": self.context,
            "priority": self.priority.value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class CheckpointResponse:
    """Human response to a checkpoint request"""
    request_id: str
    selected_option_id: Optional[str]  # None if all rejected
    status: ApprovalStatus
    feedback: Optional[str] = None
    custom_content: Optional[Any] = None  # Human-provided alternative
    reviewer_id: Optional[str] = None
    reviewed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "selected_option_id": self.selected_option_id,
            "status": self.status.value,
            "feedback": self.feedback,
            "custom_content": self.custom_content,
            "reviewer_id": self.reviewer_id,
            "reviewed_at": self.reviewed_at.isoformat()
        }


class CheckpointHandler(ABC):
    """Abstract base class for checkpoint handlers"""
    
    @abstractmethod
    async def present_options(self, request: CheckpointRequest) -> CheckpointResponse:
        """Present options to human and get response"""
        pass
    
    @abstractmethod
    def format_options(self, request: CheckpointRequest) -> str:
        """Format options for human presentation"""
        pass


class HumanCreativityCheckpoints:
    """
    Manages human-in-the-loop checkpoints throughout the publishing pipeline.
    Ensures AI-generated content meets quality and brand standards.
    """
    
    def __init__(self):
        self.handlers: Dict[CheckpointType, CheckpointHandler] = {}
        self.pending_requests: Dict[str, CheckpointRequest] = {}
        self.response_history: List[CheckpointResponse] = []
        self.default_timeout_hours = 24
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Initialize default checkpoint handlers"""
        self.handlers[CheckpointType.TITLE_SELECTION] = TitleSelectionHandler()
        self.handlers[CheckpointType.COVER_PROMPT_APPROVAL] = CoverPromptHandler()
        self.handlers[CheckpointType.MARKETING_ANGLE_SELECTION] = MarketingAngleHandler()
        self.handlers[CheckpointType.BOOK_DESCRIPTION_REVIEW] = DescriptionReviewHandler()
    
    async def request_human_review(self,
                                  checkpoint_type: CheckpointType,
                                  book_id: str,
                                  options: List[CreativeOption],
                                  context: Optional[Dict[str, Any]] = None,
                                  priority: Priority = Priority.MEDIUM,
                                  timeout_hours: Optional[int] = None) -> CheckpointResponse:
        """
        Request human review for a creative decision.
        
        Args:
            checkpoint_type: Type of checkpoint
            book_id: ID of the book being processed
            options: List of AI-generated options
            context: Additional context for the reviewer
            priority: Priority level for the review
            timeout_hours: Hours until request expires
            
        Returns:
            CheckpointResponse with human decision
        """
        # Create request
        request = CheckpointRequest(
            request_id=f"{checkpoint_type.value}_{book_id}_{datetime.now().timestamp()}",
            checkpoint_type=checkpoint_type,
            book_id=book_id,
            options=options,
            context=context or {},
            priority=priority,
            deadline=datetime.now() + timedelta(hours=timeout_hours or self.default_timeout_hours)
        )
        
        # Store pending request
        self.pending_requests[request.request_id] = request
        
        # Get appropriate handler
        handler = self.handlers.get(checkpoint_type)
        if not handler:
            logger.error(f"No handler found for checkpoint type: {checkpoint_type}")
            return CheckpointResponse(
                request_id=request.request_id,
                selected_option_id=None,
                status=ApprovalStatus.REJECTED,
                feedback="No handler available"
            )
        
        try:
            # Present to human and get response
            response = await handler.present_options(request)
            
            # Store response
            self.response_history.append(response)
            
            # Remove from pending
            self.pending_requests.pop(request.request_id, None)
            
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Checkpoint request {request.request_id} timed out")
            return CheckpointResponse(
                request_id=request.request_id,
                selected_option_id=self._select_best_ai_option(options),
                status=ApprovalStatus.EXPIRED,
                feedback="Request timed out, using AI recommendation"
            )
    
    def _select_best_ai_option(self, options: List[CreativeOption]) -> str:
        """Select the best AI option when human review times out"""
        if not options:
            return None
        
        # Sort by AI score and return highest
        sorted_options = sorted(options, key=lambda x: x.ai_score, reverse=True)
        return sorted_options[0].option_id
    
    def get_checkpoint_analytics(self) -> Dict[str, Any]:
        """Get analytics on human checkpoint decisions"""
        total_requests = len(self.response_history)
        if total_requests == 0:
            return {"message": "No checkpoint data available"}
        
        # Calculate metrics
        approval_rate = sum(1 for r in self.response_history 
                          if r.status == ApprovalStatus.APPROVED) / total_requests
        
        rejection_rate = sum(1 for r in self.response_history 
                           if r.status == ApprovalStatus.REJECTED) / total_requests
        
        custom_content_rate = sum(1 for r in self.response_history 
                                if r.custom_content is not None) / total_requests
        
        avg_ai_score_selected = []
        for response in self.response_history:
            if response.selected_option_id and response.status == ApprovalStatus.APPROVED:
                # Find the selected option's AI score
                request = next((r for r in self.pending_requests.values() 
                              if r.request_id == response.request_id), None)
                if request:
                    option = next((o for o in request.options 
                                 if o.option_id == response.selected_option_id), None)
                    if option:
                        avg_ai_score_selected.append(option.ai_score)
        
        return {
            "total_checkpoints": total_requests,
            "approval_rate": approval_rate,
            "rejection_rate": rejection_rate,
            "custom_content_rate": custom_content_rate,
            "avg_ai_score_of_selected": sum(avg_ai_score_selected) / len(avg_ai_score_selected) if avg_ai_score_selected else 0,
            "pending_requests": len(self.pending_requests),
            "checkpoints_by_type": self._count_by_type(),
            "average_response_time": self._calculate_avg_response_time()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count checkpoints by type"""
        counts = {}
        for response in self.response_history:
            # Match with original request
            for request in self.pending_requests.values():
                if request.request_id == response.request_id:
                    checkpoint_type = request.checkpoint_type.value
                    counts[checkpoint_type] = counts.get(checkpoint_type, 0) + 1
                    break
        return counts
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time in hours"""
        response_times = []
        for response in self.response_history:
            # Find corresponding request
            for request in self.pending_requests.values():
                if request.request_id == response.request_id:
                    time_diff = response.reviewed_at - request.created_at
                    response_times.append(time_diff.total_seconds() / 3600)
                    break
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def create_checkpoint_summary(self, book_id: str) -> Dict[str, Any]:
        """Create a summary of all checkpoints for a specific book"""
        book_checkpoints = []
        
        for response in self.response_history:
            # Find matching request
            for request in self.pending_requests.values():
                if request.request_id == response.request_id and request.book_id == book_id:
                    book_checkpoints.append({
                        "checkpoint_type": request.checkpoint_type.value,
                        "status": response.status.value,
                        "selected_option": response.selected_option_id,
                        "feedback": response.feedback,
                        "timestamp": response.reviewed_at.isoformat()
                    })
                    break
        
        return {
            "book_id": book_id,
            "total_checkpoints": len(book_checkpoints),
            "checkpoints": book_checkpoints,
            "final_status": self._determine_final_status(book_checkpoints)
        }
    
    def _determine_final_status(self, checkpoints: List[Dict]) -> str:
        """Determine overall status based on all checkpoints"""
        if not checkpoints:
            return "no_checkpoints"
        
        if all(c["status"] == ApprovalStatus.APPROVED.value for c in checkpoints):
            return "fully_approved"
        elif any(c["status"] == ApprovalStatus.REJECTED.value for c in checkpoints):
            return "has_rejections"
        else:
            return "mixed_status"


# Concrete Handler Implementations

class TitleSelectionHandler(CheckpointHandler):
    """Handler for book title selection"""
    
    async def present_options(self, request: CheckpointRequest) -> CheckpointResponse:
        """Present title options to human"""
        # In production, this would interface with a UI
        # For now, simulate selection based on AI scores
        
        formatted = self.format_options(request)
        logger.info(f"Title selection request:\n{formatted}")
        
        # Simulate human decision
        # In reality, this would wait for human input
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Select option with highest AI score for demo
        best_option = max(request.options, key=lambda x: x.ai_score)
        
        return CheckpointResponse(
            request_id=request.request_id,
            selected_option_id=best_option.option_id,
            status=ApprovalStatus.APPROVED,
            feedback="Clear and engaging title that captures the book's essence"
        )
    
    def format_options(self, request: CheckpointRequest) -> str:
        """Format title options for display"""
        lines = [
            f"Book Title Selection for {request.book_id}",
            f"Context: {json.dumps(request.context, indent=2)}",
            "\nOptions:"
        ]
        
        for i, option in enumerate(request.options, 1):
            lines.append(f"\n{i}. {option.content}")
            lines.append(f"   AI Score: {option.ai_score:.2f}")
            if option.metadata:
                lines.append(f"   Metadata: {option.metadata}")
        
        return "\n".join(lines)


class CoverPromptHandler(CheckpointHandler):
    """Handler for cover art prompt approval"""
    
    async def present_options(self, request: CheckpointRequest) -> CheckpointResponse:
        """Present cover prompt options to human"""
        formatted = self.format_options(request)
        logger.info(f"Cover prompt approval request:\n{formatted}")
        
        # Simulate human review
        await asyncio.sleep(0.1)
        
        # For demo, approve with modifications
        best_option = max(request.options, key=lambda x: x.ai_score)
        
        return CheckpointResponse(
            request_id=request.request_id,
            selected_option_id=best_option.option_id,
            status=ApprovalStatus.APPROVED,
            feedback="Add more vibrant colors and ensure title is clearly visible",
            custom_content=f"{best_option.content} Style: Professional and eye-catching with high contrast."
        )
    
    def format_options(self, request: CheckpointRequest) -> str:
        """Format cover prompts for display"""
        lines = [
            f"Cover Art Prompt Approval for {request.book_id}",
            "\nProposed DALL-E Prompts:"
        ]
        
        for i, option in enumerate(request.options, 1):
            lines.append(f"\n{i}. Prompt:")
            lines.append(f"   {option.content}")
            lines.append(f"   AI Score: {option.ai_score:.2f}")
        
        return "\n".join(lines)


class MarketingAngleHandler(CheckpointHandler):
    """Handler for marketing angle selection"""
    
    async def present_options(self, request: CheckpointRequest) -> CheckpointResponse:
        """Present marketing angle options to human"""
        formatted = self.format_options(request)
        logger.info(f"Marketing angle selection:\n{formatted}")
        
        await asyncio.sleep(0.1)
        
        # Select based on context (e.g., target audience)
        target_audience = request.context.get("target_audience", "general")
        
        # Find option that best matches target audience
        best_option = request.options[0]  # Default
        for option in request.options:
            if target_audience.lower() in str(option.metadata).lower():
                best_option = option
                break
        
        return CheckpointResponse(
            request_id=request.request_id,
            selected_option_id=best_option.option_id,
            status=ApprovalStatus.APPROVED,
            feedback=f"This angle resonates well with our {target_audience} audience"
        )
    
    def format_options(self, request: CheckpointRequest) -> str:
        """Format marketing angles for display"""
        lines = [
            f"Marketing Angle Selection for {request.book_id}",
            f"Target Audience: {request.context.get('target_audience', 'Not specified')}",
            "\nProposed Angles:"
        ]
        
        for i, option in enumerate(request.options, 1):
            lines.append(f"\n{i}. {option.content}")
            lines.append(f"   Target: {option.metadata.get('target_segment', 'General')}")
            lines.append(f"   AI Score: {option.ai_score:.2f}")
        
        return "\n".join(lines)


class DescriptionReviewHandler(CheckpointHandler):
    """Handler for book description review"""
    
    async def present_options(self, request: CheckpointRequest) -> CheckpointResponse:
        """Present book description for review"""
        formatted = self.format_options(request)
        logger.info(f"Book description review:\n{formatted}")
        
        await asyncio.sleep(0.1)
        
        # For demo, request revision if description is too long
        description = request.options[0].content if request.options else ""
        
        if len(description) > 1000:
            return CheckpointResponse(
                request_id=request.request_id,
                selected_option_id=None,
                status=ApprovalStatus.REVISION_REQUESTED,
                feedback="Description is too long. Please condense to under 1000 characters while maintaining key selling points."
            )
        
        return CheckpointResponse(
            request_id=request.request_id,
            selected_option_id=request.options[0].option_id if request.options else None,
            status=ApprovalStatus.APPROVED,
            feedback="Description effectively communicates value proposition"
        )
    
    def format_options(self, request: CheckpointRequest) -> str:
        """Format book description for display"""
        lines = [
            f"Book Description Review for {request.book_id}",
            "\nProposed Description:"
        ]
        
        if request.options:
            lines.append(f"\n{request.options[0].content}")
            lines.append(f"\nCharacter Count: {len(request.options[0].content)}")
            lines.append(f"AI Score: {request.options[0].ai_score:.2f}")
        
        return "\n".join(lines)