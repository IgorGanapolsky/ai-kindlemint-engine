"""
Event-Driven Marketing Agent with SNN-inspired Event Detection

This module implements a Spiking Neural Network (SNN) inspired approach to marketing
event detection and response, following the Alembic strategy of distilling complex
neural dynamics into actionable marketing insights.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
from collections import deque, defaultdict
from enum import Enum
import pandas as pd
import networkx as nx
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of marketing events the system can detect"""
    VIRAL_MOMENT = "viral_moment"
    TRENDING_TOPIC = "trending_topic"
    COMPETITOR_LAUNCH = "competitor_launch"
    SEASONAL_SPIKE = "seasonal_spike"
    REVIEW_SURGE = "review_surge"
    PRICE_SENSITIVITY = "price_sensitivity"
    MARKET_SHIFT = "market_shift"
    INFLUENCER_MENTION = "influencer_mention"
    ALGORITHM_CHANGE = "algorithm_change"
    CUSTOMER_SENTIMENT_SHIFT = "customer_sentiment_shift"


@dataclass
class Spike:
    """Represents a neural spike in the SNN"""
    timestamp: datetime
    neuron_id: str
    intensity: float
    source_data: Dict[str, Any]
    decay_rate: float = 0.1


@dataclass
class MarketingEvent:
    """Detected marketing event with response recommendations"""
    event_type: EventType
    timestamp: datetime
    confidence: float
    magnitude: float
    data: Dict[str, Any]
    recommended_actions: List[str]
    urgency: str  # "immediate", "high", "medium", "low"
    expected_duration: Optional[timedelta] = None


@dataclass
class NeuronState:
    """State of a single neuron in the SNN"""
    neuron_id: str
    membrane_potential: float = 0.0
    threshold: float = 1.0
    refractory_period: float = 0.0
    spike_history: deque = field(default_factory=lambda: deque(maxlen=100))
    connections: Dict[str, float] = field(default_factory=dict)
    last_spike_time: Optional[datetime] = None


class EventDrivenMarketingAgent:
    """
    SNN-inspired agent for detecting and responding to marketing events.
    
    Implements the Alembic approach by transforming complex market signals
    into discrete, actionable marketing events through spike-based processing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the event-driven marketing agent"""
        self.config = config or self._default_config()
        self.neurons = {}
        self.event_queue = asyncio.Queue()
        self.event_history = deque(maxlen=1000)
        self.active_campaigns = {}
        self.network = nx.DiGraph()
        self._initialize_neural_network()
        self.executor = ThreadPoolExecutor(max_workers=self.config["max_workers"])
        self.running = False
        self.processing_loop_task = None
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the agent"""
        return {
            "spike_threshold": 1.0,
            "decay_rate": 0.1,
            "refractory_period": 0.5,
            "time_window": 300,  # 5 minutes
            "min_spike_rate": 0.1,
            "plasticity_rate": 0.01,
            "max_workers": 4,
            "event_cooldown": 3600,  # 1 hour
            "sensitivity_factors": {
                "viral_moment": 0.8,
                "trending_topic": 0.7,
                "competitor_launch": 0.9,
                "seasonal_spike": 0.6,
                "review_surge": 0.85
            }
        }
    
    def _initialize_neural_network(self):
        """Initialize the SNN structure for event detection"""
        # Input neurons for different data streams
        input_neurons = [
            "social_media_mentions",
            "search_volume",
            "competitor_activity",
            "sales_velocity",
            "review_rate",
            "click_through_rate",
            "conversion_rate",
            "seasonal_indicators",
            "price_elasticity",
            "content_engagement"
        ]
        
        # Hidden layer neurons for pattern detection
        hidden_neurons = [
            "trend_detector",
            "anomaly_detector",
            "sentiment_analyzer",
            "velocity_tracker",
            "correlation_finder",
            "threshold_monitor",
            "pattern_matcher",
            "spike_aggregator"
        ]
        
        # Output neurons for event types
        output_neurons = [event.value for event in EventType]
        
        # Create neurons
        all_neurons = input_neurons + hidden_neurons + output_neurons
        for neuron_id in all_neurons:
            self.neurons[neuron_id] = NeuronState(
                neuron_id=neuron_id,
                threshold=self.config["spike_threshold"]
            )
            self.network.add_node(neuron_id)
        
        # Create connections (synapses)
        # Input to hidden connections
        for input_n in input_neurons:
            for hidden_n in hidden_neurons:
                weight = np.random.uniform(0.3, 0.7)
                self.neurons[input_n].connections[hidden_n] = weight
                self.network.add_edge(input_n, hidden_n, weight=weight)
        
        # Hidden to output connections
        connection_patterns = {
            "trend_detector": [EventType.TRENDING_TOPIC.value, EventType.VIRAL_MOMENT.value],
            "anomaly_detector": [EventType.ALGORITHM_CHANGE.value, EventType.MARKET_SHIFT.value],
            "sentiment_analyzer": [EventType.CUSTOMER_SENTIMENT_SHIFT.value, EventType.REVIEW_SURGE.value],
            "velocity_tracker": [EventType.VIRAL_MOMENT.value, EventType.SEASONAL_SPIKE.value],
            "correlation_finder": [EventType.COMPETITOR_LAUNCH.value, EventType.PRICE_SENSITIVITY.value],
            "threshold_monitor": [EventType.REVIEW_SURGE.value, EventType.SEASONAL_SPIKE.value],
            "pattern_matcher": [EventType.TRENDING_TOPIC.value, EventType.INFLUENCER_MENTION.value],
            "spike_aggregator": [EventType.VIRAL_MOMENT.value, EventType.MARKET_SHIFT.value]
        }
        
        for hidden_n, outputs in connection_patterns.items():
            for output_n in outputs:
                weight = np.random.uniform(0.5, 0.9)
                self.neurons[hidden_n].connections[output_n] = weight
                self.network.add_edge(hidden_n, output_n, weight=weight)
    
    async def start(self):
        """Start the event-driven marketing agent"""
        self.running = True
        self.processing_loop_task = asyncio.create_task(self._processing_loop())
        logger.info("Event-driven marketing agent started")
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        if self.processing_loop_task:
            await self.processing_loop_task
        self.executor.shutdown(wait=True)
        logger.info("Event-driven marketing agent stopped")
    
    async def _processing_loop(self):
        """Main processing loop for the agent"""
        while self.running:
            try:
                # Process spikes and detect events
                await self._process_neural_activity()
                
                # Apply synaptic plasticity
                self._update_synaptic_weights()
                
                # Process detected events
                await self._process_event_queue()
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1)
    
    async def inject_market_signal(self, 
                                 signal_type: str,
                                 value: float,
                                 metadata: Optional[Dict[str, Any]] = None):
        """
        Inject a market signal into the neural network
        
        Args:
            signal_type: Type of signal (must match input neuron)
            value: Signal strength (0-1 normalized)
            metadata: Additional data about the signal
        """
        if signal_type not in self.neurons:
            logger.warning(f"Unknown signal type: {signal_type}")
            return
        
        # Convert signal to spike intensity
        spike_intensity = self._signal_to_spike_intensity(value, signal_type)
        
        # Create spike
        spike = Spike(
            timestamp=datetime.now(),
            neuron_id=signal_type,
            intensity=spike_intensity,
            source_data=metadata or {},
            decay_rate=self.config["decay_rate"]
        )
        
        # Process spike
        await self._process_spike(spike)
    
    def _signal_to_spike_intensity(self, value: float, signal_type: str) -> float:
        """Convert raw signal value to spike intensity"""
        # Apply sensitivity factors
        sensitivity = self.config["sensitivity_factors"].get(
            signal_type, 
            0.5
        )
        
        # Non-linear transformation (sigmoid-like)
        transformed = 1 / (1 + np.exp(-10 * (value - 0.5)))
        
        return transformed * sensitivity
    
    async def _process_spike(self, spike: Spike):
        """Process a single spike through the network"""
        neuron = self.neurons[spike.neuron_id]
        
        # Check refractory period
        if neuron.refractory_period > 0:
            return
        
        # Update membrane potential
        neuron.membrane_potential += spike.intensity
        
        # Check for firing
        if neuron.membrane_potential >= neuron.threshold:
            # Neuron fires!
            neuron.spike_history.append(spike)
            neuron.last_spike_time = spike.timestamp
            neuron.refractory_period = self.config["refractory_period"]
            
            # Reset membrane potential
            neuron.membrane_potential = 0
            
            # Propagate spike to connected neurons
            for target_id, weight in neuron.connections.items():
                propagated_spike = Spike(
                    timestamp=spike.timestamp,
                    neuron_id=target_id,
                    intensity=spike.intensity * weight,
                    source_data=spike.source_data,
                    decay_rate=spike.decay_rate
                )
                
                # Async propagation
                asyncio.create_task(self._process_spike(propagated_spike))
            
            # Check if this is an output neuron
            if spike.neuron_id in [e.value for e in EventType]:
                await self._check_for_event(spike.neuron_id, spike)
    
    async def _check_for_event(self, event_type_str: str, spike: Spike):
        """Check if spike activity indicates a marketing event"""
        neuron = self.neurons[event_type_str]
        
        # Calculate spike rate in time window
        recent_spikes = [
            s for s in neuron.spike_history
            if (spike.timestamp - s.timestamp).total_seconds() < self.config["time_window"]
        ]
        
        if len(recent_spikes) < 3:  # Need minimum spikes
            return
        
        spike_rate = len(recent_spikes) / self.config["time_window"]
        
        if spike_rate >= self.config["min_spike_rate"]:
            # Event detected!
            event_type = EventType(event_type_str)
            
            # Calculate confidence and magnitude
            confidence = min(1.0, spike_rate / (self.config["min_spike_rate"] * 2))
            magnitude = np.mean([s.intensity for s in recent_spikes])
            
            # Generate event
            event = await self._generate_marketing_event(
                event_type, confidence, magnitude, spike.source_data
            )
            
            # Add to queue
            await self.event_queue.put(event)
    
    async def _generate_marketing_event(self,
                                      event_type: EventType,
                                      confidence: float,
                                      magnitude: float,
                                      data: Dict[str, Any]) -> MarketingEvent:
        """Generate a complete marketing event with recommendations"""
        
        # Determine urgency
        urgency = self._calculate_urgency(event_type, magnitude, confidence)
        
        # Generate recommended actions
        actions = self._generate_recommended_actions(event_type, data, urgency)
        
        # Estimate duration
        duration = self._estimate_event_duration(event_type, magnitude)
        
        return MarketingEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            confidence=confidence,
            magnitude=magnitude,
            data=data,
            recommended_actions=actions,
            urgency=urgency,
            expected_duration=duration
        )
    
    def _calculate_urgency(self, 
                         event_type: EventType,
                         magnitude: float,
                         confidence: float) -> str:
        """Calculate event urgency level"""
        urgency_score = magnitude * confidence
        
        # Event-specific urgency modifiers
        urgency_modifiers = {
            EventType.VIRAL_MOMENT: 1.5,
            EventType.COMPETITOR_LAUNCH: 1.3,
            EventType.ALGORITHM_CHANGE: 1.4,
            EventType.PRICE_SENSITIVITY: 1.2,
            EventType.INFLUENCER_MENTION: 1.3
        }
        
        modifier = urgency_modifiers.get(event_type, 1.0)
        urgency_score *= modifier
        
        if urgency_score > 0.8:
            return "immediate"
        elif urgency_score > 0.6:
            return "high"
        elif urgency_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_recommended_actions(self,
                                    event_type: EventType,
                                    data: Dict[str, Any],
                                    urgency: str) -> List[str]:
        """Generate specific recommended actions for the event"""
        
        action_templates = {
            EventType.VIRAL_MOMENT: [
                "Boost social media ad spend immediately (3x normal budget)",
                "Create real-time response content within 2 hours",
                "Engage with viral posts and trending hashtags",
                "Launch flash sale to capitalize on attention",
                "Update book descriptions with trending keywords"
            ],
            EventType.TRENDING_TOPIC: [
                "Create content series around the trend",
                "Update keywords in book metadata",
                "Launch targeted ad campaign for trend-related books",
                "Commission trend-aligned book covers",
                "Partner with trend influencers"
            ],
            EventType.COMPETITOR_LAUNCH: [
                "Analyze competitor pricing and adjust accordingly",
                "Launch counter-promotion with unique value prop",
                "Highlight differentiating features in marketing",
                "Increase review generation efforts",
                "Target competitor's audience with comparison ads"
            ],
            EventType.SEASONAL_SPIKE: [
                "Increase inventory for high-demand titles",
                "Launch seasonal bundle promotions",
                "Update cover designs with seasonal elements",
                "Create gift-focused marketing campaigns",
                "Partner with seasonal gift guides"
            ],
            EventType.REVIEW_SURGE: [
                "Amplify positive reviews in marketing materials",
                "Launch testimonial-based ad campaign",
                "Reach out to reviewers for extended testimonials",
                "Create social proof focused landing pages",
                "Implement review-powered email campaign"
            ],
            EventType.PRICE_SENSITIVITY: [
                "Test multiple price points via A/B testing",
                "Launch limited-time discount promotion",
                "Create value-added bundles",
                "Highlight cost-per-entertainment-hour value",
                "Implement dynamic pricing strategy"
            ],
            EventType.MARKET_SHIFT: [
                "Pivot content strategy to new market preferences",
                "Commission market research for deeper insights",
                "Adjust long-term publishing calendar",
                "Re-evaluate target audience personas",
                "Test new genres/niches aligned with shift"
            ],
            EventType.INFLUENCER_MENTION: [
                "Reach out for partnership opportunity",
                "Create co-branded content",
                "Amplify mention across all channels",
                "Send thank you package with book bundle",
                "Launch influencer-specific discount code"
            ],
            EventType.ALGORITHM_CHANGE: [
                "Audit and update all book metadata",
                "Test new keyword strategies",
                "Adjust advertising targeting parameters",
                "Monitor ranking changes closely",
                "Diversify traffic sources"
            ],
            EventType.CUSTOMER_SENTIMENT_SHIFT: [
                "Conduct customer survey for insights",
                "Address concerns in marketing messaging",
                "Update book descriptions to match sentiment",
                "Launch customer appreciation campaign",
                "Implement feedback into future products"
            ]
        }
        
        base_actions = action_templates.get(event_type, [])
        
        # Filter by urgency
        if urgency == "immediate":
            return base_actions[:3]  # Top 3 most important
        elif urgency == "high":
            return base_actions[:4]
        else:
            return base_actions
    
    def _estimate_event_duration(self,
                               event_type: EventType,
                               magnitude: float) -> timedelta:
        """Estimate how long an event will last"""
        
        base_durations = {
            EventType.VIRAL_MOMENT: timedelta(hours=24),
            EventType.TRENDING_TOPIC: timedelta(days=7),
            EventType.COMPETITOR_LAUNCH: timedelta(days=30),
            EventType.SEASONAL_SPIKE: timedelta(days=45),
            EventType.REVIEW_SURGE: timedelta(days=14),
            EventType.PRICE_SENSITIVITY: timedelta(days=7),
            EventType.MARKET_SHIFT: timedelta(days=180),
            EventType.INFLUENCER_MENTION: timedelta(days=3),
            EventType.ALGORITHM_CHANGE: timedelta(days=60),
            EventType.CUSTOMER_SENTIMENT_SHIFT: timedelta(days=30)
        }
        
        base_duration = base_durations.get(event_type, timedelta(days=7))
        
        # Adjust by magnitude
        duration_seconds = base_duration.total_seconds() * (0.5 + magnitude)
        
        return timedelta(seconds=duration_seconds)
    
    async def _process_neural_activity(self):
        """Process ongoing neural activity and decay"""
        datetime.now()
        
        for neuron in self.neurons.values():
            # Decay membrane potential
            if neuron.membrane_potential > 0:
                neuron.membrane_potential *= (1 - self.config["decay_rate"])
                
                if neuron.membrane_potential < 0.01:
                    neuron.membrane_potential = 0
            
            # Update refractory period
            if neuron.refractory_period > 0:
                neuron.refractory_period -= 0.1
                
                if neuron.refractory_period < 0:
                    neuron.refractory_period = 0
    
    def _update_synaptic_weights(self):
        """Update synaptic weights based on spike-timing dependent plasticity"""
        for neuron_id, neuron in self.neurons.items():
            if not neuron.spike_history:
                continue
            
            recent_spike = neuron.spike_history[-1]
            
            for target_id, weight in neuron.connections.items():
                target_neuron = self.neurons[target_id]
                
                if target_neuron.last_spike_time:
                    # Calculate time difference
                    time_diff = (target_neuron.last_spike_time - recent_spike.timestamp).total_seconds()
                    
                    # STDP rule
                    if abs(time_diff) < 1.0:  # Within 1 second
                        if time_diff > 0:  # Pre before post - strengthen
                            delta_w = self.config["plasticity_rate"] * np.exp(-abs(time_diff))
                        else:  # Post before pre - weaken
                            delta_w = -self.config["plasticity_rate"] * np.exp(-abs(time_diff)) * 0.5
                        
                        # Update weight
                        new_weight = np.clip(weight + delta_w, 0.1, 1.0)
                        neuron.connections[target_id] = new_weight
                        
                        # Update network graph
                        if self.network.has_edge(neuron_id, target_id):
                            self.network[neuron_id][target_id]["weight"] = new_weight
    
    async def _process_event_queue(self):
        """Process detected marketing events"""
        try:
            while not self.event_queue.empty():
                event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
                
                # Check cooldown
                if self._is_event_in_cooldown(event):
                    continue
                
                # Log event
                logger.info(f"Marketing event detected: {event.event_type.value} "
                          f"(confidence: {event.confidence:.2f}, urgency: {event.urgency})")
                
                # Store in history
                self.event_history.append(event)
                
                # Execute recommended actions
                await self._execute_event_actions(event)
                
        except asyncio.TimeoutError:
            pass
    
    def _is_event_in_cooldown(self, event: MarketingEvent) -> bool:
        """Check if similar event was recently processed"""
        cooldown_period = timedelta(seconds=self.config["event_cooldown"])
        
        for past_event in self.event_history:
            if past_event.event_type == event.event_type:
                time_since = event.timestamp - past_event.timestamp
                if time_since < cooldown_period:
                    return True
        
        return False
    
    async def _execute_event_actions(self, event: MarketingEvent):
        """Execute recommended actions for a marketing event"""
        # Create campaign
        campaign_id = f"{event.event_type.value}_{event.timestamp.isoformat()}"
        
        campaign = {
            "id": campaign_id,
            "event": event,
            "status": "active",
            "actions_executed": [],
            "results": {}
        }
        
        self.active_campaigns[campaign_id] = campaign
        
        # Execute actions based on urgency
        if event.urgency == "immediate":
            # Execute all actions immediately
            for action in event.recommended_actions:
                asyncio.create_task(self._execute_action(campaign_id, action))
        else:
            # Schedule actions
            for i, action in enumerate(event.recommended_actions):
                delay = i * 300  # 5 minutes between actions
                asyncio.create_task(self._delayed_action_execution(campaign_id, action, delay))
    
    async def _execute_action(self, campaign_id: str, action: str):
        """Execute a single marketing action"""
        logger.info(f"Executing action for campaign {campaign_id}: {action}")
        
        # Record execution
        if campaign_id in self.active_campaigns:
            self.active_campaigns[campaign_id]["actions_executed"].append({
                "action": action,
                "timestamp": datetime.now(),
                "status": "completed"
            })
        
        # In a real implementation, this would integrate with various marketing platforms
        # For now, we'll simulate the execution
        await asyncio.sleep(0.1)
    
    async def _delayed_action_execution(self, campaign_id: str, action: str, delay: float):
        """Execute an action after a delay"""
        await asyncio.sleep(delay)
        await self._execute_action(campaign_id, action)
    
    def get_active_events(self) -> List[MarketingEvent]:
        """Get currently active marketing events"""
        active_events = []
        current_time = datetime.now()
        
        for event in self.event_history:
            if event.expected_duration:
                event_end = event.timestamp + event.expected_duration
                if current_time < event_end:
                    active_events.append(event)
        
        return active_events
    
    def get_network_state(self) -> Dict[str, Any]:
        """Get current state of the neural network"""
        return {
            "neurons": {
                neuron_id: {
                    "membrane_potential": neuron.membrane_potential,
                    "refractory_period": neuron.refractory_period,
                    "recent_spikes": len(neuron.spike_history),
                    "connections": len(neuron.connections)
                }
                for neuron_id, neuron in self.neurons.items()
            },
            "active_events": len(self.get_active_events()),
            "event_history_size": len(self.event_history),
            "active_campaigns": len(self.active_campaigns)
        }
    
    def train_on_historical_data(self, 
                               historical_events: pd.DataFrame,
                               outcomes: pd.DataFrame):
        """
        Train the SNN on historical marketing data
        
        Args:
            historical_events: DataFrame with past marketing events
            outcomes: DataFrame with outcomes (sales, engagement, etc.)
        """
        logger.info("Training SNN on historical data")
        
        # Pair events with outcomes
        for idx, event_row in historical_events.iterrows():
            # Find corresponding outcome
            event_time = pd.to_datetime(event_row["timestamp"])
            
            # Look for outcomes within event window
            outcome_mask = (
                (outcomes["timestamp"] >= event_time) & 
                (outcomes["timestamp"] <= event_time + timedelta(days=7))
            )
            
            if outcome_mask.any():
                event_outcomes = outcomes[outcome_mask]
                
                # Calculate success metrics
                success_score = self._calculate_success_score(event_outcomes)
                
                # Adjust weights based on success
                self._reinforce_successful_patterns(
                    event_row["event_type"],
                    event_row["signals"],
                    success_score
                )
    
    def _calculate_success_score(self, outcomes: pd.DataFrame) -> float:
        """Calculate success score from outcomes"""
        # Weighted combination of different metrics
        weights = {
            "sales_increase": 0.4,
            "engagement_rate": 0.3,
            "conversion_rate": 0.2,
            "roi": 0.1
        }
        
        score = 0
        for metric, weight in weights.items():
            if metric in outcomes.columns:
                score += outcomes[metric].mean() * weight
        
        return np.clip(score, 0, 1)
    
    def _reinforce_successful_patterns(self,
                                     event_type: str,
                                     signals: Dict[str, float],
                                     success_score: float):
        """Reinforce neural pathways that led to successful outcomes"""
        # Find paths that led to this event type
        if event_type in self.neurons:
            # Strengthen connections proportional to success
            for source_neuron in self.network.predecessors(event_type):
                if source_neuron in self.neurons:
                    current_weight = self.neurons[source_neuron].connections.get(event_type, 0)
                    
                    # Reinforcement learning update
                    delta = self.config["plasticity_rate"] * success_score * (1 - current_weight)
                    new_weight = np.clip(current_weight + delta, 0.1, 1.0)
                    
                    self.neurons[source_neuron].connections[event_type] = new_weight
                    
                    if self.network.has_edge(source_neuron, event_type):
                        self.network[source_neuron][event_type]["weight"] = new_weight
    
    def predict_next_events(self, 
                          current_signals: Dict[str, float],
                          time_horizon: timedelta) -> List[Tuple[EventType, float, datetime]]:
        """
        Predict likely upcoming marketing events
        
        Args:
            current_signals: Current market signals
            time_horizon: How far ahead to predict
            
        Returns:
            List of (event_type, probability, estimated_time)
        """
        predictions = []
        
        # Simulate network forward in time
        simulated_spikes = []
        
        # Inject current signals
        for signal_type, value in current_signals.items():
            if signal_type in self.neurons:
                spike_intensity = self._signal_to_spike_intensity(value, signal_type)
                simulated_spikes.append((signal_type, spike_intensity, 0))  # Time 0
        
        # Propagate through network
        time_steps = int(time_horizon.total_seconds() / 60)  # 1-minute steps
        
        for t in range(time_steps):
            new_spikes = []
            
            for neuron_id, intensity, spike_time in simulated_spikes:
                if spike_time == t:  # Process spikes at current time
                    neuron = self.neurons[neuron_id]
                    
                    for target_id, weight in neuron.connections.items():
                        propagated_intensity = intensity * weight * (1 - self.config["decay_rate"] * t)
                        
                        if propagated_intensity > 0.1:  # Threshold
                            new_spikes.append((target_id, propagated_intensity, t + 1))
            
            simulated_spikes.extend(new_spikes)
        
        # Aggregate predictions for output neurons
        event_predictions = defaultdict(list)
        
        for neuron_id, intensity, spike_time in simulated_spikes:
            if neuron_id in [e.value for e in EventType]:
                event_predictions[neuron_id].append((intensity, spike_time))
        
        # Calculate probabilities
        for event_type_str, spike_data in event_predictions.items():
            if spike_data:
                # Aggregate intensity
                total_intensity = sum(intensity for intensity, _ in spike_data)
                avg_time = np.mean([time for _, time in spike_data])
                
                # Convert to probability
                probability = 1 - np.exp(-total_intensity)
                
                # Estimate time
                estimated_time = datetime.now() + timedelta(minutes=avg_time)
                
                predictions.append((
                    EventType(event_type_str),
                    probability,
                    estimated_time
                ))
        
        # Sort by probability
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions
    
    def export_model(self) -> Dict[str, Any]:
        """Export the SNN model for persistence"""
        return {
            "config": self.config,
            "network": nx.node_link_data(self.network),
            "neuron_states": {
                neuron_id: {
                    "threshold": neuron.threshold,
                    "connections": neuron.connections
                }
                for neuron_id, neuron in self.neurons.items()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def import_model(self, model_data: Dict[str, Any]):
        """Import a previously exported model"""
        self.config.update(model_data.get("config", {}))
        self.network = nx.node_link_graph(model_data["network"])
        
        # Restore neuron states
        for neuron_id, state_data in model_data.get("neuron_states", {}).items():
            if neuron_id in self.neurons:
                self.neurons[neuron_id].threshold = state_data.get("threshold", 1.0)
                self.neurons[neuron_id].connections = state_data.get("connections", {})
        
        logger.info(f"Imported SNN model from {model_data.get('timestamp', 'unknown')}")