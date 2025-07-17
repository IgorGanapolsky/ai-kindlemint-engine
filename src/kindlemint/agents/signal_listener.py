#!/usr/bin/env python3
"""
Signal Listener

Real-time signal monitoring and alert system that detects emerging opportunities
and market shifts across multiple data sources.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

class SignalListener:
    """Real-time signal monitoring and alert system."""
    
    def __init__(self, data_manager, config: Dict):
        self.data_manager = data_manager
        self.config = config
        self.monitoring = False
        self.alert_handlers = []
        self.signal_history = []
        self.alert_threshold = config.get("alert_threshold", 0.8)
        self.check_interval = config.get("check_interval_seconds", 300)
        
    async def start_monitoring(self) -> None:
        """Start real-time signal monitoring."""
        logger.info("🔍 Starting signal monitoring...")
        
        self.monitoring = True
        
        # Start monitoring tasks
        asyncio.create_task(self.monitor_reddit_signals())
        asyncio.create_task(self.monitor_tiktok_signals())
        asyncio.create_task(self.monitor_google_trends_signals())
        asyncio.create_task(self.monitor_amazon_signals())
        
        logger.info("✅ Signal monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop signal monitoring."""
        logger.info("🛑 Stopping signal monitoring...")
        
        self.monitoring = False
        
        logger.info("✅ Signal monitoring stopped")
    
    async def monitor_signals(self) -> List[Dict]:
        """Monitor all signal sources."""
        signals = []
        
        try:
            # Monitor each source
            reddit_signals = await self.monitor_reddit_signals()
            tiktok_signals = await self.monitor_tiktok_signals()
            google_signals = await self.monitor_google_trends_signals()
            amazon_signals = await self.monitor_amazon_signals()
            
            # Combine all signals
            signals = reddit_signals + tiktok_signals + google_signals + amazon_signals
            
            # Store in history
            self.signal_history.extend(signals)
            
            # Keep only recent signals (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.signal_history = [
                signal for signal in self.signal_history
                if datetime.fromisoformat(signal.get("timestamp", "1970-01-01")) > cutoff_time
            ]
            
            logger.info(f"📡 Monitored {len(signals)} signals")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Signal monitoring failed: {e}")
            return []
    
    async def monitor_reddit_signals(self) -> List[Dict]:
        """Monitor Reddit for emerging signals."""
        signals = []
        
        try:
            # Mock Reddit signal detection
            reddit_signals = [
                {
                    "id": f"reddit_signal_{int(time.time())}",
                    "source": "reddit",
                    "type": "trending_post",
                    "subreddit": "books",
                    "title": "New puzzle book trend emerging",
                    "score": 150,
                    "comments": 45,
                    "signal_strength": 0.75,
                    "timestamp": datetime.now().isoformat(),
                    "keywords": ["puzzle", "trend", "new"]
                },
                {
                    "id": f"reddit_signal_{int(time.time()) + 1}",
                    "source": "reddit",
                    "type": "viral_comment",
                    "subreddit": "Kindle",
                    "title": "Activity books for kids are selling out",
                    "score": 89,
                    "comments": 23,
                    "signal_strength": 0.65,
                    "timestamp": datetime.now().isoformat(),
                    "keywords": ["activity", "kids", "selling"]
                }
            ]
            
            # Filter signals above threshold
            for signal in reddit_signals:
                if signal.get("signal_strength", 0) > self.alert_threshold:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Reddit signal monitoring failed: {e}")
            return []
    
    async def monitor_tiktok_signals(self) -> List[Dict]:
        """Monitor TikTok for emerging signals."""
        signals = []
        
        try:
            # Mock TikTok signal detection
            tiktok_signals = [
                {
                    "id": f"tiktok_signal_{int(time.time())}",
                    "source": "tiktok",
                    "type": "viral_video",
                    "hashtag": "#booktok",
                    "title": "Puzzle books going viral",
                    "views": 1500000,
                    "likes": 45000,
                    "signal_strength": 0.85,
                    "timestamp": datetime.now().isoformat(),
                    "keywords": ["puzzle", "viral", "trending"]
                }
            ]
            
            # Filter signals above threshold
            for signal in tiktok_signals:
                if signal.get("signal_strength", 0) > self.alert_threshold:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ TikTok signal monitoring failed: {e}")
            return []
    
    async def monitor_google_trends_signals(self) -> List[Dict]:
        """Monitor Google Trends for emerging signals."""
        signals = []
        
        try:
            # Mock Google Trends signal detection
            google_signals = [
                {
                    "id": f"google_signal_{int(time.time())}",
                    "source": "google_trends",
                    "type": "trending_keyword",
                    "keyword": "activity books for kids",
                    "trend_score": 92,
                    "growth_rate": 0.45,
                    "signal_strength": 0.78,
                    "timestamp": datetime.now().isoformat(),
                    "keywords": ["activity", "kids", "trending"]
                }
            ]
            
            # Filter signals above threshold
            for signal in google_signals:
                if signal.get("signal_strength", 0) > self.alert_threshold:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Google Trends signal monitoring failed: {e}")
            return []
    
    async def monitor_amazon_signals(self) -> List[Dict]:
        """Monitor Amazon for emerging signals."""
        signals = []
        
        try:
            # Mock Amazon signal detection
            amazon_signals = [
                {
                    "id": f"amazon_signal_{int(time.time())}",
                    "source": "amazon",
                    "type": "bestseller_movement",
                    "category": "Children's Books",
                    "title": "New activity book climbing ranks",
                    "rank_change": -15,
                    "signal_strength": 0.72,
                    "timestamp": datetime.now().isoformat(),
                    "keywords": ["activity", "climbing", "ranks"]
                }
            ]
            
            # Filter signals above threshold
            for signal in amazon_signals:
                if signal.get("signal_strength", 0) > self.alert_threshold:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Amazon signal monitoring failed: {e}")
            return []
    
    async def process_alerts(self, signals: List[Dict]) -> List[Dict]:
        """Process signals and generate alerts."""
        alerts = []
        
        try:
            for signal in signals:
                # Analyze signal
                alert = await self.analyze_signal(signal)
                
                if alert:
                    alerts.append(alert)
            
            logger.info(f"🚨 Generated {len(alerts)} alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Alert processing failed: {e}")
            return []
    
    async def analyze_signal(self, signal: Dict) -> Optional[Dict]:
        """Analyze a signal and generate an alert if necessary."""
        signal_strength = signal.get("signal_strength", 0)
        
        if signal_strength < self.alert_threshold:
            return None
        
        # Determine alert type and priority
        alert_type = self.determine_alert_type(signal)
        priority = self.calculate_alert_priority(signal)
        
        # Generate alert message
        message = self.generate_alert_message(signal, alert_type)
        
        # Create alert
        alert = {
            "id": f"alert_{int(time.time())}",
            "signal_id": signal.get("id"),
            "type": alert_type,
            "priority": priority,
            "title": f"Signal Alert: {signal.get('title', 'Unknown')}",
            "message": message,
            "source": signal.get("source"),
            "signal_strength": signal_strength,
            "keywords": signal.get("keywords", []),
            "timestamp": datetime.now().isoformat(),
            "action_required": self.determine_action_required(alert_type, priority)
        }
        
        return alert
    
    def determine_alert_type(self, signal: Dict) -> str:
        """Determine the type of alert based on signal characteristics."""
        signal_type = signal.get("type", "")
        signal.get("source", "")
        
        if "viral" in signal_type.lower():
            return "viral_trend"
        elif "trending" in signal_type.lower():
            return "trending_topic"
        elif "bestseller" in signal_type.lower():
            return "market_movement"
        elif "comment" in signal_type.lower():
            return "community_signal"
        else:
            return "general_signal"
    
    def calculate_alert_priority(self, signal: Dict) -> str:
        """Calculate alert priority based on signal strength and characteristics."""
        signal_strength = signal.get("signal_strength", 0)
        
        if signal_strength > 0.9:
            return "critical"
        elif signal_strength > 0.8:
            return "high"
        elif signal_strength > 0.7:
            return "medium"
        else:
            return "low"
    
    def generate_alert_message(self, signal: Dict, alert_type: str) -> str:
        """Generate a human-readable alert message."""
        source = signal.get("source", "Unknown")
        title = signal.get("title", "Unknown signal")
        strength = signal.get("signal_strength", 0)
        
        if alert_type == "viral_trend":
            return f"🚀 Viral trend detected on {source}: {title} (Strength: {strength:.2f})"
        elif alert_type == "trending_topic":
            return f"📈 Trending topic on {source}: {title} (Strength: {strength:.2f})"
        elif alert_type == "market_movement":
            return f"📊 Market movement on {source}: {title} (Strength: {strength:.2f})"
        elif alert_type == "community_signal":
            return f"💬 Community signal on {source}: {title} (Strength: {strength:.2f})"
        else:
            return f"📡 Signal detected on {source}: {title} (Strength: {strength:.2f})"
    
    def determine_action_required(self, alert_type: str, priority: str) -> str:
        """Determine what action is required based on alert type and priority."""
        if priority == "critical":
            return "immediate_response"
        elif priority == "high":
            return "urgent_review"
        elif priority == "medium":
            return "monitor_closely"
        else:
            return "note_for_reference"
    
    async def send_alert(self, alert: Dict) -> bool:
        """Send an alert through configured channels."""
        try:
            # Log the alert
            logger.info(f"🚨 Alert: {alert.get('title')} - {alert.get('message')}")
            
            # Save alert to storage
            await self.data_manager.save_data(
                f"alerts/{alert['id']}.json",
                alert
            )
            
            # Trigger alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"❌ Alert handler failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")
            return False
    
    def add_alert_handler(self, handler: Callable) -> None:
        """Add a custom alert handler."""
        self.alert_handlers.append(handler)
    
    async def get_signal_summary(self, hours: int = 24) -> Dict:
        """Get a summary of signals from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_signals = [
            signal for signal in self.signal_history
            if datetime.fromisoformat(signal.get("timestamp", "1970-01-01")) > cutoff_time
        ]
        
        # Group by source
        source_counts = {}
        type_counts = {}
        strength_sum = 0
        
        for signal in recent_signals:
            source = signal.get("source", "unknown")
            signal_type = signal.get("type", "unknown")
            strength = signal.get("signal_strength", 0)
            
            source_counts[source] = source_counts.get(source, 0) + 1
            type_counts[signal_type] = type_counts.get(signal_type, 0) + 1
            strength_sum += strength
        
        avg_strength = strength_sum / len(recent_signals) if recent_signals else 0
        
        return {
            "total_signals": len(recent_signals),
            "time_period_hours": hours,
            "source_distribution": source_counts,
            "type_distribution": type_counts,
            "average_signal_strength": avg_strength,
            "high_strength_signals": len([s for s in recent_signals if s.get("signal_strength", 0) > 0.8])
        }
    
    async def get_trending_keywords(self, hours: int = 24) -> List[Dict]:
        """Get trending keywords from recent signals."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_signals = [
            signal for signal in self.signal_history
            if datetime.fromisoformat(signal.get("timestamp", "1970-01-01")) > cutoff_time
        ]
        
        # Count keyword occurrences
        keyword_counts = {}
        keyword_strengths = {}
        
        for signal in recent_signals:
            keywords = signal.get("keywords", [])
            strength = signal.get("signal_strength", 0)
            
            for keyword in keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                if keyword not in keyword_strengths:
                    keyword_strengths[keyword] = []
                keyword_strengths[keyword].append(strength)
        
        # Calculate average strength for each keyword
        trending_keywords = []
        for keyword, count in keyword_counts.items():
            avg_strength = sum(keyword_strengths[keyword]) / len(keyword_strengths[keyword])
            trending_keywords.append({
                "keyword": keyword,
                "occurrences": count,
                "average_strength": avg_strength,
                "trend_score": count * avg_strength
            })
        
        # Sort by trend score
        trending_keywords.sort(key=lambda x: x["trend_score"], reverse=True)
        
        return trending_keywords[:10]  # Return top 10 trending keywords 