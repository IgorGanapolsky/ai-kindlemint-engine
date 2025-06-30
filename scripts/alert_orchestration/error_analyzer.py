#!/usr/bin/env python3
"""
Error Analyzer - Advanced error pattern analysis and categorization system
Provides ML-powered error classification, pattern detection, and resolution recommendations
"""

import json
import logging
import os
import re
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ErrorAnalyzer")


@dataclass
class ErrorPattern:
    """Error pattern definition"""

    id: str
    name: str
    pattern: str
    category: str
    severity: str
    confidence: float
    frequency: int
    last_seen: datetime
    resolution_strategy: str
    similar_errors: List[str]
    metadata: Dict[str, Any]


@dataclass
class ErrorClassification:
    """Error classification result"""

    error_id: str
    primary_category: str
    secondary_categories: List[str]
    confidence_score: float
    suggested_actions: List[str]
    similar_patterns: List[str]
    root_cause_analysis: Dict[str, Any]
    business_impact: str
    resolution_urgency: str


@dataclass
class TrendAnalysis:
    """Error trend analysis result"""

    category: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0.0 to 1.0
    frequency_change: float  # percentage change
    peak_times: List[str]
    correlation_factors: List[str]
    prediction: Dict[str, Any]


class ErrorAnalyzer:
    """
    Advanced error analysis system with ML-powered pattern recognition

    Features:
    - Intelligent error categorization
    - Pattern detection and learning
    - Trend analysis and forecasting
    - Root cause analysis
    - Business impact assessment
    - Resolution recommendation engine
    """

    def __init__(
        self, patterns_file: Optional[str] = None, learning_enabled: bool = True
    ):
        """Initialize error analyzer with pattern database"""
        self.patterns_file = patterns_file or "error_patterns.json"
        self.learning_enabled = learning_enabled

        # Load existing patterns
        self.patterns: Dict[str, ErrorPattern] = {}
        self.load_patterns()

        # Analysis state
        self.error_history: List[Dict] = []
        self.category_stats: Dict[str, Dict] = defaultdict(dict)
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}

        # Pattern matching rules
        self.severity_keywords = {
            "critical": [
                "fatal",
                "critical",
                "emergency",
                "panic",
                "crash",
                "corruption",
            ],
            "high": ["error", "exception", "failed", "timeout", "refused", "denied"],
            "medium": ["warning", "deprecated", "slow", "retry", "fallback"],
            "low": ["info", "debug", "notice", "trace"],
        }

        # Category patterns
        self.category_patterns = {
            "performance": [
                r"timeout|slow|latency|memory|cpu|performance|bottleneck",
                r"response time|execution time|query time|load time",
                r"memory leak|out of memory|heap|garbage collection",
                r"high cpu|cpu usage|cpu load|processing time",
            ],
            "database": [
                r"database|sql|query|transaction|deadlock|connection pool",
                r"mysql|postgresql|mongodb|redis|elasticsearch",
                r"constraint|foreign key|duplicate key|syntax error",
                r"table|index|schema|migration|backup",
            ],
            "network": [
                r"connection|network|socket|dns|http|https|tcp|udp",
                r"refused|unreachable|timeout|proxy|gateway",
                r"ssl|tls|certificate|handshake|firewall",
                r"api|endpoint|service|microservice|webhook",
            ],
            "authentication": [
                r"auth|login|password|token|session|permission",
                r"unauthorized|forbidden|access denied|invalid credentials",
                r"oauth|jwt|saml|ldap|active directory",
                r"expire|revoke|validate|authenticate",
            ],
            "application": [
                r"import|module|package|dependency|library",
                r"syntax|attribute|method|function|class",
                r"null|undefined|reference|pointer|index",
                r"configuration|config|setting|parameter",
            ],
            "infrastructure": [
                r"server|service|container|kubernetes|docker",
                r"deployment|release|version|rollback|upgrade",
                r"resource|disk|storage|volume|mount",
                r"load balancer|proxy|cdn|cache|queue",
            ],
        }

        logger.info("Error analyzer initialized")

    def load_patterns(self) -> None:
        """Load error patterns from file"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, "r") as f:
                    data = json.load(f)

                for pattern_data in data.get("patterns", []):
                    pattern = ErrorPattern(
                        id=pattern_data["id"],
                        name=pattern_data["name"],
                        pattern=pattern_data["pattern"],
                        category=pattern_data["category"],
                        severity=pattern_data["severity"],
                        confidence=pattern_data["confidence"],
                        frequency=pattern_data.get("frequency", 0),
                        last_seen=datetime.fromisoformat(
                            pattern_data.get("last_seen", datetime.now().isoformat())
                        ),
                        resolution_strategy=pattern_data.get("resolution_strategy", ""),
                        similar_errors=pattern_data.get("similar_errors", []),
                        metadata=pattern_data.get("metadata", {}),
                    )
                    self.patterns[pattern.id] = pattern

                logger.info(f"Loaded {len(self.patterns)} error patterns")
            else:
                logger.info("No existing patterns file found, starting fresh")

        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")

    def save_patterns(self) -> None:
        """Save error patterns to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "pattern_count": len(self.patterns),
                "patterns": [
                    {**asdict(pattern), "last_seen": pattern.last_seen.isoformat()}
                    for pattern in self.patterns.values()
                ],
            }

            with open(self.patterns_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved {len(self.patterns)} patterns to {self.patterns_file}")

        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def analyze_error(self, error_data: Dict[str, Any]) -> ErrorClassification:
        """
        Analyze a single error and provide classification

        Args:
            error_data: Error information including message, context, etc.

        Returns:
            ErrorClassification with analysis results
        """
        error_id = error_data.get("id", str(datetime.now().timestamp()))
        message = error_data.get("message", "")
        context = error_data.get("context", {})

        # Classify error category
        primary_category, confidence = self._classify_category(message, context)
        secondary_categories = self._get_secondary_categories(message, context)

        # Find similar patterns
        similar_patterns = self._find_similar_patterns(message, context)

        # Perform root cause analysis
        root_cause = self._analyze_root_cause(error_data)

        # Assess business impact
        business_impact = self._assess_business_impact(error_data, primary_category)

        # Determine resolution urgency
        urgency = self._determine_urgency(error_data, primary_category, business_impact)

        # Generate suggested actions
        suggested_actions = self._generate_action_suggestions(
            primary_category, secondary_categories, root_cause, urgency
        )

        # Store for learning
        if self.learning_enabled:
            self._update_learning_data(error_data, primary_category, confidence)

        return ErrorClassification(
            error_id=error_id,
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            confidence_score=confidence,
            suggested_actions=suggested_actions,
            similar_patterns=similar_patterns,
            root_cause_analysis=root_cause,
            business_impact=business_impact,
            resolution_urgency=urgency,
        )

    def _classify_category(self, message: str, context: Dict) -> Tuple[str, float]:
        """Classify error into primary category with confidence score"""
        message_lower = message.lower()
        scores = {}

        # Check against known patterns first
        for pattern in self.patterns.values():
            if re.search(pattern.pattern, message_lower, re.IGNORECASE):
                scores[pattern.category] = max(
                    scores.get(pattern.category, 0), pattern.confidence
                )

        # Check against category patterns
        for category, patterns in self.category_patterns.items():
            category_score = 0
            matches = 0

            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    matches += 1
                    category_score += 1.0 / len(patterns)

            if matches > 0:
                # Boost score based on number of matching patterns
                category_score *= 1 + matches * 0.1
                scores[category] = max(scores.get(category, 0), category_score)

        # Consider context information
        context_score = self._analyze_context_for_category(context)
        for category, score in context_score.items():
            scores[category] = scores.get(category, 0) + score * 0.3

        # Find best category
        if scores:
            best_category = max(scores.keys(), key=lambda k: scores[k])
            confidence = min(scores[best_category], 1.0)
            return best_category, confidence
        else:
            return "unknown", 0.1

    def _get_secondary_categories(self, message: str, context: Dict) -> List[str]:
        """Get secondary categories that also match"""
        message_lower = message.lower()
        secondary = []

        for category, patterns in self.category_patterns.items():
            matches = sum(
                1
                for pattern in patterns
                if re.search(pattern, message_lower, re.IGNORECASE)
            )
            if matches > 0:
                secondary.append(category)

        return secondary[:3]  # Limit to top 3

    def _analyze_context_for_category(self, context: Dict) -> Dict[str, float]:
        """Analyze context information for category hints"""
        scores = {}

        # Check environment
        env = context.get("environment", "").lower()
        if env in ["production", "prod"]:
            scores["infrastructure"] = scores.get("infrastructure", 0) + 0.2

        # Check tags
        tags = context.get("tags", {})
        if "database" in str(tags).lower():
            scores["database"] = scores.get("database", 0) + 0.3
        if "api" in str(tags).lower():
            scores["network"] = scores.get("network", 0) + 0.3

        # Check user agent or platform
        platform = context.get("platform", "").lower()
        if "python" in platform:
            scores["application"] = scores.get("application", 0) + 0.1

        return scores

    def _find_similar_patterns(self, message: str, context: Dict) -> List[str]:
        """Find similar error patterns"""
        similar = []
        message_words = set(re.findall(r"\w+", message.lower()))

        for pattern in self.patterns.values():
            pattern_words = set(re.findall(r"\w+", pattern.pattern.lower()))

            # Calculate word overlap
            overlap = len(message_words & pattern_words)
            total_words = len(message_words | pattern_words)

            if total_words > 0:
                similarity = overlap / total_words
                if similarity > 0.3:  # Threshold for similarity
                    similar.append(pattern.id)

        return similar[:5]  # Return top 5 similar patterns

    def _analyze_root_cause(self, error_data: Dict) -> Dict[str, Any]:
        """Perform root cause analysis"""
        message = error_data.get("message", "")
        context = error_data.get("context", {})
        timestamp = error_data.get("timestamp")

        root_cause = {
            "likely_causes": [],
            "contributing_factors": [],
            "evidence": [],
            "confidence": 0.0,
        }

        # Analyze error message for cause indicators
        message_lower = message.lower()

        # Connection issues
        if any(
            keyword in message_lower for keyword in ["connection", "refused", "timeout"]
        ):
            root_cause["likely_causes"].append("Network connectivity issue")
            root_cause["evidence"].append("Connection-related error message")
            root_cause["confidence"] += 0.3

        # Resource issues
        if any(
            keyword in message_lower for keyword in ["memory", "disk", "space", "full"]
        ):
            root_cause["likely_causes"].append("Resource exhaustion")
            root_cause["evidence"].append("Resource-related error message")
            root_cause["confidence"] += 0.4

        # Configuration issues
        if any(
            keyword in message_lower
            for keyword in ["config", "setting", "parameter", "missing"]
        ):
            root_cause["likely_causes"].append("Configuration error")
            root_cause["evidence"].append("Configuration-related error message")
            root_cause["confidence"] += 0.3

        # Code issues
        if any(
            keyword in message_lower
            for keyword in ["syntax", "attribute", "method", "undefined"]
        ):
            root_cause["likely_causes"].append("Code defect")
            root_cause["evidence"].append("Code-related error message")
            root_cause["confidence"] += 0.5

        # Analyze context for additional clues
        if context.get("environment") == "production":
            root_cause["contributing_factors"].append("Production environment")

        if context.get("recent_deployment"):
            root_cause["contributing_factors"].append("Recent deployment")
            root_cause["confidence"] += 0.2

        # Time-based analysis
        if timestamp:
            try:
                error_time = datetime.fromisoformat(timestamp)
                hour = error_time.hour

                # Peak hours analysis
                if 9 <= hour <= 17:
                    root_cause["contributing_factors"].append("Peak business hours")
                elif 0 <= hour <= 5:
                    root_cause["contributing_factors"].append("Maintenance window")
            except:
                pass

        root_cause["confidence"] = min(root_cause["confidence"], 1.0)
        return root_cause

    def _assess_business_impact(self, error_data: Dict, category: str) -> str:
        """Assess business impact of the error"""
        # Extract impact indicators
        count = error_data.get("count", 1)
        environment = error_data.get("environment", "")
        affected_users = error_data.get("affected_users", 0)

        # Base impact assessment
        if environment.lower() in ["production", "prod"]:
            base_impact = "medium"
        else:
            base_impact = "low"

        # Adjust based on error category
        critical_categories = ["database", "authentication", "infrastructure"]
        if category in critical_categories:
            if base_impact == "low":
                base_impact = "medium"
            elif base_impact == "medium":
                base_impact = "high"

        # Adjust based on frequency and user impact
        if count > 100 or affected_users > 50:
            if base_impact == "low":
                base_impact = "medium"
            elif base_impact == "medium":
                base_impact = "high"
            elif base_impact == "high":
                base_impact = "critical"

        return base_impact

    def _determine_urgency(
        self, error_data: Dict, category: str, business_impact: str
    ) -> str:
        """Determine resolution urgency"""
        # Base urgency from business impact
        impact_urgency = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "critical": "critical",
        }

        urgency = impact_urgency.get(business_impact, "medium")

        # Adjust based on error characteristics
        level = error_data.get("level", "").lower()
        if level in ["fatal", "critical", "error"]:
            if urgency in ["low", "medium"]:
                urgency = "high"

        # Check for escalating frequency
        frequency_trend = error_data.get("frequency_trend", "stable")
        if frequency_trend == "increasing":
            urgency_levels = ["low", "medium", "high", "critical"]
            current_index = urgency_levels.index(urgency)
            if current_index < len(urgency_levels) - 1:
                urgency = urgency_levels[current_index + 1]

        return urgency

    def _generate_action_suggestions(
        self,
        primary_category: str,
        secondary_categories: List[str],
        root_cause: Dict,
        urgency: str,
    ) -> List[str]:
        """Generate suggested actions based on analysis"""
        suggestions = []

        # Category-specific suggestions
        category_actions = {
            "performance": [
                "Monitor resource utilization metrics",
                "Implement performance profiling",
                "Review and optimize slow queries",
                "Consider horizontal scaling",
            ],
            "database": [
                "Check database connection pool settings",
                "Review query performance and indexes",
                "Verify database server health",
                "Consider read replicas for load distribution",
            ],
            "network": [
                "Verify network connectivity and DNS resolution",
                "Check firewall and security group settings",
                "Review API rate limits and quotas",
                "Implement circuit breaker pattern",
            ],
            "authentication": [
                "Verify authentication service availability",
                "Check token expiration and refresh logic",
                "Review access permissions and roles",
                "Implement proper error handling for auth failures",
            ],
            "application": [
                "Review recent code changes and deployments",
                "Check dependency versions and compatibility",
                "Verify configuration settings",
                "Implement proper exception handling",
            ],
            "infrastructure": [
                "Check server and service health status",
                "Review resource allocation and limits",
                "Verify deployment and configuration",
                "Consider auto-scaling policies",
            ],
        }

        # Add primary category suggestions
        if primary_category in category_actions:
            suggestions.extend(category_actions[primary_category][:2])

        # Add root cause specific suggestions
        for cause in root_cause.get("likely_causes", []):
            if "Network connectivity" in cause:
                suggestions.append("Investigate network infrastructure and routing")
            elif "Resource exhaustion" in cause:
                suggestions.append("Scale resources or optimize resource usage")
            elif "Configuration error" in cause:
                suggestions.append("Review and validate configuration settings")
            elif "Code defect" in cause:
                suggestions.append("Perform code review and testing")

        # Add urgency-based suggestions
        if urgency == "critical":
            suggestions.insert(0, "Immediately escalate to on-call engineer")
            suggestions.insert(1, "Activate incident response protocol")
        elif urgency == "high":
            suggestions.insert(0, "Notify development team immediately")

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)

        return unique_suggestions[:6]  # Limit to top 6 suggestions

    def _update_learning_data(
        self, error_data: Dict, category: str, confidence: float
    ) -> None:
        """Update learning data for pattern improvement"""
        self.error_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "confidence": confidence,
                "message": error_data.get("message", ""),
                "resolved": False,  # Will be updated when resolution is confirmed
            }
        )

        # Update category statistics
        if category not in self.category_stats:
            self.category_stats[category] = {
                "count": 0,
                "avg_confidence": 0.0,
                "last_seen": None,
            }

        stats = self.category_stats[category]
        stats["count"] += 1
        stats["avg_confidence"] = (
            stats["avg_confidence"] * (stats["count"] - 1) + confidence
        ) / stats["count"]
        stats["last_seen"] = datetime.now().isoformat()

    def analyze_trends(
        self, errors: List[Dict], time_window_hours: int = 24
    ) -> List[TrendAnalysis]:
        """Analyze error trends over time"""
        if not errors:
            return []

        # Group errors by category and time
        category_timeseries = defaultdict(list)
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        for error in errors:
            try:
                timestamp = datetime.fromisoformat(error.get("timestamp", ""))
                if timestamp >= cutoff_time:
                    category = error.get("category", "unknown")
                    category_timeseries[category].append(timestamp)
            except:
                continue

        trends = []
        for category, timestamps in category_timeseries.items():
            trend = self._analyze_category_trend(
                category, timestamps, time_window_hours
            )
            trends.append(trend)

        return sorted(trends, key=lambda x: x.trend_strength, reverse=True)

    def _analyze_category_trend(
        self, category: str, timestamps: List[datetime], window_hours: int
    ) -> TrendAnalysis:
        """Analyze trend for a specific category"""
        # Create hourly buckets
        buckets = {}
        start_time = datetime.now() - timedelta(hours=window_hours)

        for i in range(window_hours):
            bucket_time = start_time + timedelta(hours=i)
            bucket_key = bucket_time.strftime("%Y-%m-%d %H:00")
            buckets[bucket_key] = 0

        # Count errors per hour
        for timestamp in timestamps:
            bucket_key = timestamp.strftime("%Y-%m-%d %H:00")
            if bucket_key in buckets:
                buckets[bucket_key] += 1

        # Analyze trend
        counts = list(buckets.values())

        if len(counts) < 2:
            return TrendAnalysis(
                category=category,
                trend_direction="stable",
                trend_strength=0.0,
                frequency_change=0.0,
                peak_times=[],
                correlation_factors=[],
                prediction={},
            )

        # Calculate trend direction and strength
        first_half = counts[: len(counts) // 2]
        second_half = counts[len(counts) // 2 :]

        first_avg = statistics.mean(first_half) if first_half else 0
        second_avg = statistics.mean(second_half) if second_half else 0

        if first_avg == 0:
            frequency_change = 100.0 if second_avg > 0 else 0.0
        else:
            frequency_change = ((second_avg - first_avg) / first_avg) * 100

        # Determine trend direction
        if abs(frequency_change) < 10:
            trend_direction = "stable"
            trend_strength = 0.1
        elif frequency_change > 0:
            trend_direction = "increasing"
            trend_strength = min(abs(frequency_change) / 100, 1.0)
        else:
            trend_direction = "decreasing"
            trend_strength = min(abs(frequency_change) / 100, 1.0)

        # Find peak times
        max_count = max(counts)
        peak_times = []
        for i, count in enumerate(counts):
            if count == max_count and max_count > 0:
                peak_time = start_time + timedelta(hours=i)
                peak_times.append(peak_time.strftime("%H:00"))

        return TrendAnalysis(
            category=category,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            frequency_change=frequency_change,
            peak_times=peak_times[:3],  # Top 3 peak times
            correlation_factors=[],  # TODO: Implement correlation analysis
            prediction=self._predict_future_trend(counts),
        )

    def _predict_future_trend(self, historical_counts: List[int]) -> Dict[str, Any]:
        """Simple trend prediction"""
        if len(historical_counts) < 3:
            return {"prediction": "insufficient_data"}

        # Simple linear trend analysis
        recent_trend = statistics.mean(historical_counts[-3:]) - statistics.mean(
            historical_counts[-6:-3]
        )

        prediction = {
            "next_hour_estimate": max(0, historical_counts[-1] + recent_trend),
            "trend_confidence": min(
                abs(recent_trend) / max(statistics.mean(historical_counts), 1), 1.0
            ),
            "recommendation": "monitor" if abs(recent_trend) < 2 else "investigate",
        }

        return prediction


# Example usage
def example_usage():
    """Example of how to use the error analyzer"""
    analyzer = ErrorAnalyzer()

    # Analyze a sample error
    error_data = {
        "id": "error_123",
        "message": "Database connection timeout after 30 seconds",
        "level": "error",
        "environment": "production",
        "count": 15,
        "timestamp": datetime.now().isoformat(),
        "context": {
            "tags": {"service": "api", "database": "postgresql"},
            "environment": "production",
        },
    }

    classification = analyzer.analyze_error(error_data)
    print(f"Error Classification: {classification}")

    # Save updated patterns
    analyzer.save_patterns()


if __name__ == "__main__":
    example_usage()
