"""
Event-Driven Marketing Agent using Spiking Neural Network principles

This module implements an event-driven marketing automation system inspired by
Spiking Neural Networks (SNNs) that react to market "spikes" or significant events.
Based on insights from the NVIDIA AI Podcast featuring Alembic CEO Tomás Puig.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of market events that can trigger actions"""
    COMPETITOR_RANK_DROP = "competitor_rank_drop"
    COMPETITOR_PRICE_CHANGE = "competitor_price_change"
    KEYWORD_SPIKE = "keyword_spike"
    KEYWORD_TREND_DECLINE = "keyword_trend_decline"
    REVIEW_MILESTONE = "review_milestone"
    SALES_SPIKE = "sales_spike"
    SALES_DROP = "sales_drop"
    SOCIAL_MEDIA_TREND = "social_media_trend"
    SEASONAL_TRIGGER = "seasonal_trigger"
    INVENTORY_LOW = "inventory_low"
    PAGE_READ_SURGE = "page_read_surge"
    CATEGORY_RANK_CHANGE = "category_rank_change"


class ActionType(Enum):
    """Types of marketing actions that can be triggered"""
    LAUNCH_AD_CAMPAIGN = "launch_ad_campaign"
    ADJUST_PRICING = "adjust_pricing"
    CREATE_CONTENT = "create_content"
    UPDATE_KEYWORDS = "update_keywords"
    SEND_EMAIL_CAMPAIGN = "send_email_campaign"
    BOOST_SOCIAL_POST = "boost_social_post"
    GENERATE_BLOG_POST = "generate_blog_post"
    CREATE_BUNDLE_OFFER = "create_bundle_offer"
    SCHEDULE_PROMOTION = "schedule_promotion"
    UPDATE_BOOK_DESCRIPTION = "update_book_description"


@dataclass
class MarketEvent:
    """Represents a market event or "spike" that can trigger actions"""
    event_type: EventType
    timestamp: datetime
    book_id: Optional[str]
    magnitude: float  # 0.0 to 1.0, representing event significance
    data: Dict[str, Any]
    source: str  # Where the event was detected (e.g., "kdp_api", "google_trends")
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary for storage/transmission"""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "book_id": self.book_id,
            "magnitude": self.magnitude,
            "data": self.data,
            "source": self.source
        }


@dataclass
class MarketingAction:
    """Represents a marketing action to be executed"""
    action_type: ActionType
    target_book_id: Optional[str]
    parameters: Dict[str, Any]
    priority: int = 5  # 1-10, with 10 being highest priority
    scheduled_time: Optional[datetime] = None
    triggered_by: Optional[MarketEvent] = None
    
    def to_dict(self) -> Dict:
        """Convert action to dictionary for storage/transmission"""
        return {
            "action_type": self.action_type.value,
            "target_book_id": self.target_book_id,
            "parameters": self.parameters,
            "priority": self.priority,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "triggered_by": self.triggered_by.to_dict() if self.triggered_by else None
        }


@dataclass
class EventRule:
    """Defines a rule for mapping events to actions"""
    event_type: EventType
    condition: Callable[[MarketEvent], bool]
    action_factory: Callable[[MarketEvent], MarketingAction]
    cooldown_minutes: int = 60  # Prevent rapid-fire triggers
    min_magnitude: float = 0.3  # Minimum event magnitude to trigger
    description: str = ""


class EventDetector(ABC):
    """Abstract base class for event detection"""
    
    @abstractmethod
    async def detect_events(self) -> List[MarketEvent]:
        """Detect and return a list of market events"""
        pass


class ActionExecutor(ABC):
    """Abstract base class for action execution"""
    
    @abstractmethod
    async def execute_action(self, action: MarketingAction) -> Dict[str, Any]:
        """Execute a marketing action and return results"""
        pass


class EventDrivenMarketingAgent:
    """
    Listens for market events ("spikes") and triggers
    pre-defined marketing actions in response.
    
    Inspired by Spiking Neural Networks (SNNs) that only
    activate when input exceeds a threshold.
    """
    
    def __init__(self, 
                 event_detectors: List[EventDetector] = None,
                 action_executors: Dict[ActionType, ActionExecutor] = None):
        self.event_detectors = event_detectors or []
        self.action_executors = action_executors or {}
        self.event_rules: List[EventRule] = []
        self.event_history: List[MarketEvent] = []
        self.action_history: List[MarketingAction] = []
        self.cooldown_tracker: Dict[str, datetime] = {}
        self.is_running = False
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configure default event-action mappings"""
        
        # Rule: Competitor rank drop → Launch targeted ad campaign
        self.add_rule(EventRule(
            event_type=EventType.COMPETITOR_RANK_DROP,
            condition=lambda e: e.magnitude > 0.5,
            action_factory=lambda e: MarketingAction(
                action_type=ActionType.LAUNCH_AD_CAMPAIGN,
                target_book_id=e.data.get("our_book_id"),
                parameters={
                    "campaign_type": "competitor_targeting",
                    "budget": 50.0 * e.magnitude,
                    "duration_days": 7,
                    "target_keywords": e.data.get("keywords", [])
                },
                priority=8,
                triggered_by=e
            ),
            cooldown_minutes=120,
            description="Launch ads when competitor drops significantly in rank"
        ))
        
        # Rule: Keyword spike → Generate optimized content
        self.add_rule(EventRule(
            event_type=EventType.KEYWORD_SPIKE,
            condition=lambda e: e.magnitude > 0.7,
            action_factory=lambda e: MarketingAction(
                action_type=ActionType.GENERATE_BLOG_POST,
                target_book_id=e.book_id,
                parameters={
                    "keyword": e.data.get("keyword"),
                    "content_type": "seo_optimized_article",
                    "word_count": 1500,
                    "include_book_promotion": True
                },
                priority=6,
                triggered_by=e
            ),
            cooldown_minutes=240,
            description="Create content when keywords spike in popularity"
        ))
        
        # Rule: Review milestone → Send celebration email
        self.add_rule(EventRule(
            event_type=EventType.REVIEW_MILESTONE,
            condition=lambda e: e.data.get("review_count", 0) in [50, 100, 250, 500, 1000],
            action_factory=lambda e: MarketingAction(
                action_type=ActionType.SEND_EMAIL_CAMPAIGN,
                target_book_id=e.book_id,
                parameters={
                    "campaign_type": "milestone_celebration",
                    "discount_percentage": 20,
                    "duration_hours": 48,
                    "subject": f"Celebrating {e.data.get('review_count')} Reviews!"
                },
                priority=7,
                triggered_by=e
            ),
            cooldown_minutes=0,  # No cooldown for milestones
            description="Celebrate review milestones with email campaigns"
        ))
        
        # Rule: Sales drop → Adjust pricing strategy
        self.add_rule(EventRule(
            event_type=EventType.SALES_DROP,
            condition=lambda e: e.magnitude > 0.4 and e.data.get("drop_percentage", 0) > 30,
            action_factory=lambda e: MarketingAction(
                action_type=ActionType.ADJUST_PRICING,
                target_book_id=e.book_id,
                parameters={
                    "strategy": "temporary_discount",
                    "discount_percentage": min(30, e.data.get("drop_percentage", 0) * 0.5),
                    "duration_days": 5
                },
                priority=9,
                triggered_by=e
            ),
            cooldown_minutes=168 * 60,  # Weekly cooldown
            description="Apply strategic discounts when sales drop significantly"
        ))
        
        # Rule: Seasonal trigger → Launch themed promotion
        self.add_rule(EventRule(
            event_type=EventType.SEASONAL_TRIGGER,
            condition=lambda e: e.data.get("season") in ["holiday", "summer", "back_to_school"],
            action_factory=lambda e: MarketingAction(
                action_type=ActionType.SCHEDULE_PROMOTION,
                target_book_id=e.book_id,
                parameters={
                    "theme": e.data.get("season"),
                    "bundle_books": e.data.get("related_books", []),
                    "discount": 25,
                    "marketing_copy": f"Special {e.data.get('season').title()} Offer!"
                },
                priority=7,
                triggered_by=e
            ),
            cooldown_minutes=24 * 60,  # Daily cooldown
            description="Create seasonal promotions automatically"
        ))
    
    def add_rule(self, rule: EventRule):
        """Add a new event-action rule"""
        self.event_rules.append(rule)
        logger.info(f"Added rule: {rule.description}")
    
    def add_detector(self, detector: EventDetector):
        """Add a new event detector"""
        self.event_detectors.append(detector)
    
    def add_executor(self, action_type: ActionType, executor: ActionExecutor):
        """Add a new action executor"""
        self.action_executors[action_type] = executor
    
    async def listen_for_events(self):
        """Main event loop - monitors data streams for significant events"""
        self.is_running = True
        logger.info("Event-driven marketing agent started")
        
        while self.is_running:
            try:
                # Collect events from all detectors
                all_events = []
                for detector in self.event_detectors:
                    events = await detector.detect_events()
                    all_events.extend(events)
                
                # Process each event
                for event in all_events:
                    await self.process_event(event)
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                await asyncio.sleep(30)  # Longer delay on error
    
    async def process_event(self, event: MarketEvent):
        """Process a single event and trigger appropriate actions"""
        logger.info(f"Processing event: {event.event_type.value} with magnitude {event.magnitude}")
        self.event_history.append(event)
        
        # Find matching rules
        for rule in self.event_rules:
            if rule.event_type == event.event_type:
                # Check if rule conditions are met
                if event.magnitude >= rule.min_magnitude and rule.condition(event):
                    # Check cooldown
                    cooldown_key = f"{rule.event_type.value}:{event.book_id}"
                    if self._is_in_cooldown(cooldown_key, rule.cooldown_minutes):
                        logger.info(f"Rule {rule.description} is in cooldown")
                        continue
                    
                    # Create and execute action
                    action = rule.action_factory(event)
                    await self.trigger_action(action)
                    
                    # Update cooldown
                    self.cooldown_tracker[cooldown_key] = datetime.now()
    
    async def trigger_action(self, action: MarketingAction):
        """Execute a marketing action based on the event"""
        logger.info(f"Triggering action: {action.action_type.value} for book {action.target_book_id}")
        self.action_history.append(action)
        
        # Find appropriate executor
        executor = self.action_executors.get(action.action_type)
        if executor:
            try:
                result = await executor.execute_action(action)
                logger.info(f"Action executed successfully: {result}")
            except Exception as e:
                logger.error(f"Failed to execute action: {e}")
        else:
            logger.warning(f"No executor found for action type: {action.action_type}")
    
    def _is_in_cooldown(self, key: str, cooldown_minutes: int) -> bool:
        """Check if an event-book combination is in cooldown"""
        if cooldown_minutes == 0:
            return False
        
        last_triggered = self.cooldown_tracker.get(key)
        if not last_triggered:
            return False
        
        cooldown_until = last_triggered + timedelta(minutes=cooldown_minutes)
        return datetime.now() < cooldown_until
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about processed events and triggered actions"""
        event_counts = {}
        for event in self.event_history:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        action_counts = {}
        for action in self.action_history:
            action_type = action.action_type.value
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "total_actions": len(self.action_history),
            "event_counts": event_counts,
            "action_counts": action_counts,
            "active_rules": len(self.event_rules),
            "recent_events": [e.to_dict() for e in self.event_history[-10:]],
            "recent_actions": [a.to_dict() for a in self.action_history[-10:]]
        }
    
    def stop(self):
        """Stop the event listening loop"""
        self.is_running = False
        logger.info("Event-driven marketing agent stopped")


# Example concrete implementations

class KDPEventDetector(EventDetector):
    """Detects events from KDP data"""
    
    async def detect_events(self) -> List[MarketEvent]:
        # Placeholder - would connect to real KDP data
        return []


class GoogleTrendsEventDetector(EventDetector):
    """Detects keyword spikes from Google Trends"""
    
    async def detect_events(self) -> List[MarketEvent]:
        # Placeholder - would connect to Google Trends API
        return []


class EmailActionExecutor(ActionExecutor):
    """Executes email marketing campaigns"""
    
    async def execute_action(self, action: MarketingAction) -> Dict[str, Any]:
        # Placeholder - would integrate with email service
        return {"status": "sent", "recipients": 1000}


class AdCampaignExecutor(ActionExecutor):
    """Executes advertising campaigns"""
    
    async def execute_action(self, action: MarketingAction) -> Dict[str, Any]:
        # Placeholder - would integrate with ad platforms
        return {"status": "launched", "budget": action.parameters.get("budget")}