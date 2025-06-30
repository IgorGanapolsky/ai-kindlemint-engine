#!/usr/bin/env python3
"""
Sentry Monitor - Advanced Sentry API integration for autonomous error monitoring
Provides comprehensive error fetching, analysis, and pattern detection
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentryMonitor")


@dataclass
class SentryError:
    """Sentry error event data structure"""

    id: str
    title: str
    message: str
    level: str
    platform: str
    timestamp: datetime
    count: int
    frequency: List[Tuple[str, int]]  # (timestamp, count) pairs
    fingerprint: List[str]
    tags: Dict[str, str]
    context: Dict[str, Any]
    exceptions: List[Dict[str, Any]]
    breadcrumbs: List[Dict[str, Any]]
    environment: str
    release: str
    culprit: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @property
    def is_critical(self) -> bool:
        """Determine if this error is critical based on level and frequency"""
        return (
            self.level in ["fatal", "error"]
            or self.count > 10
            or any(
                count > 5 for _, count in self.frequency[-24:]
            )  # High frequency in last 24 hours
        )

    @property
    def category(self) -> str:
        """Categorize error based on message and context"""
        message_lower = self.message.lower()

        # Performance issues
        if any(
            keyword in message_lower for keyword in ["timeout", "slow", "memory", "cpu"]
        ):
            return "performance"

        # Application errors
        if any(
            keyword in message_lower
            for keyword in ["import", "module", "syntax", "attribute"]
        ):
            return "application"

        # Infrastructure issues
        if any(
            keyword in message_lower
            for keyword in ["connection", "network", "service", "rate limit"]
        ):
            return "infrastructure"

        # Security issues
        if any(
            keyword in message_lower
            for keyword in ["unauthorized", "permission", "authentication"]
        ):
            return "security"

        # Database issues
        if any(
            keyword in message_lower
            for keyword in ["database", "query", "transaction", "deadlock"]
        ):
            return "database"

        return "unknown"


@dataclass
class SentryProject:
    """Sentry project configuration"""

    id: str
    slug: str
    name: str
    organization: str
    platform: str


class SentryMonitor:
    """
    Advanced Sentry monitoring system for autonomous error detection and analysis

    Features:
    - Real-time error fetching from Sentry API
    - Intelligent error categorization and pattern analysis
    - Frequency analysis and trend detection
    - Automatic severity assessment
    - Error correlation and grouping
    """

        """  Init  """
def __init__(
        self, auth_token: Optional[str] = None, organization: Optional[str] = None
    ):
        """Initialize Sentry monitor with API credentials"""
        self.auth_token = auth_token or os.getenv("SENTRY_AUTH_TOKEN")
        self.organization = organization or os.getenv("SENTRY_ORGANIZATION")
        self.base_url = "https://sentry.io/api/0"

        if not self.auth_token:
            raise ValueError("SENTRY_AUTH_TOKEN environment variable is required")

        if not self.organization:
            raise ValueError("SENTRY_ORGANIZATION environment variable is required")

        # Configure HTTP session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set headers
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
            }
        )

        # Cache and state
        self.projects: List[SentryProject] = []
        self.error_cache: Dict[str, SentryError] = {}
        self.last_fetch_time: Optional[datetime] = None
        self.pattern_cache: Dict[str, List[str]] = {}

        logger.info(f"Sentry monitor initialized for organization: {self.organization}")

    def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Sentry API with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Sentry API request failed: {e}")
            raise

    def get_projects(self) -> List[SentryProject]:
        """Fetch all projects for the organization"""
        if self.projects:
            return self.projects

        logger.info("Fetching Sentry projects...")

        try:
            data = self._make_request(f"/organizations/{self.organization}/projects/")

            self.projects = [
                SentryProject(
                    id=project["id"],
                    slug=project["slug"],
                    name=project["name"],
                    organization=project["organization"]["slug"],
                    platform=project.get("platform", "unknown"),
                )
                for project in data
            ]

            logger.info(f"Found {len(self.projects)} projects")
            return self.projects

        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            return []

    def fetch_errors(
        self,
        project_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
        query: Optional[str] = None,
    ) -> List[SentryError]:
        """
        Fetch errors from Sentry with advanced filtering

        Args:
            project_id: Specific project ID (fetch from all projects if None)
            since: Fetch errors since this timestamp
            limit: Maximum number of errors to fetch
            query: Search query for filtering errors

        Returns:
            List of SentryError objects
        """
        projects = [project_id] if project_id else [p.id for p_var in self.get_projects()]
        all_errors = []

        # Default to last 24 hours if no since time provided
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(hours=24)

        for project in projects:
            try:
                logger.info(f"Fetching errors for project {project}...")

                # Build query parameters
                params = {"statsPeriod": "24h", "limit": limit, "sort": "date"}

                if query:
                    params["query"] = query

                # Fetch issues (grouped errors)
                issues_data = self._make_request(
                    f"/projects/{self.organization}/{project}/issues/", params=params
                )

                for issue in issues_data:
                    # Fetch detailed error events for this issue
                    events_data = self._make_request(
                        f"/issues/{issue['id']}/events/",
                        params={"limit": 10},  # Get recent events for this issue
                    )

                    # Create SentryError from issue and events
                    error = self._create_sentry_error(issue, events_data)
                    if error and error.timestamp >= since:
                        all_errors.append(error)
                        self.error_cache[error.id] = error

            except Exception as e:
                logger.error(f"Failed to fetch errors for project {project}: {e}")
                continue

        self.last_fetch_time = datetime.now(timezone.utc)
        logger.info(f"Fetched {len(all_errors)} errors from {len(projects)} projects")

        return sorted(all_errors, key=lambda x: x.timestamp, reverse=True)

    def _create_sentry_error(
        self, issue: Dict, events: List[Dict]
    ) -> Optional[SentryError]:
        """Create SentryError object from Sentry issue and events data"""
        try:
            # Get the latest event for detailed information
            latest_event = events[0] if events else {}

            # Parse timestamp
            timestamp_str = issue.get("lastSeen") or issue.get("firstSeen")
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            # Extract frequency data from stats
            frequency = []
            stats = issue.get("stats", {}).get("24h", [])
            for stat in stats:
                freq_time = datetime.fromtimestamp(stat[0], tz=timezone.utc)
                freq_count = stat[1]
                frequency.append((freq_time.isoformat(), freq_count))

            # Extract exceptions
            exceptions = []
            if latest_event and "exception" in latest_event:
                for exc in latest_event["exception"].get("values", []):
                    exceptions.append(
                        {
                            "type": exc.get("type", ""),
                            "value": exc.get("value", ""),
                            "stacktrace": exc.get("stacktrace", {}),
                        }
                    )

            # Extract breadcrumbs
            breadcrumbs = []
            if latest_event and "breadcrumbs" in latest_event:
                for breadcrumb in latest_event["breadcrumbs"].get("values", []):
                    breadcrumbs.append(
                        {
                            "timestamp": breadcrumb.get("timestamp", ""),
                            "category": breadcrumb.get("category", ""),
                            "message": breadcrumb.get("message", ""),
                            "level": breadcrumb.get("level", ""),
                            "data": breadcrumb.get("data", {}),
                        }
                    )

            return SentryError(
                id=issue["id"],
                title=issue.get("title", ""),
                message=issue.get("metadata", {}).get("value", "")
                or issue.get("culprit", ""),
                level=issue.get("level", "info"),
                platform=issue.get("platform", "unknown"),
                timestamp=timestamp,
                count=issue.get("count", 0),
                frequency=frequency,
                fingerprint=issue.get("fingerprint", []),
                tags=issue.get("tags", {}),
                context=latest_event.get("contexts", {}) if latest_event else {},
                exceptions=exceptions,
                breadcrumbs=breadcrumbs,
                environment=latest_event.get("environment", "") if latest_event else "",
                release=latest_event.get("release", "") if latest_event else "",
                culprit=issue.get("culprit", ""),
                metadata=issue.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"Failed to create SentryError object: {e}")
            return None

    def analyze_error_patterns(self, errors: List[SentryError]) -> Dict[str, Any]:
        """
        Analyze error patterns and trends

        Returns:
            Dictionary containing pattern analysis results
        """
        if not errors:
            return {}

        # Categorize errors
        categories = {}
        for error in errors:
            category = error.category
            if category not in categories:
                categories[category] = []
            categories[category].append(error)

        # Analyze frequency trends
        frequency_trends = {}
        for category, cat_errors in categories.items():
            total_count = sum(error.count for error in cat_errors)
            avg_count = total_count / len(cat_errors) if cat_errors else 0

            # Calculate trend (increasing/decreasing frequency)
            recent_counts = []
            for error in cat_errors:
                if error.frequency:
                    # Get last 6 hours of frequency data
                    recent_freq = error.frequency[-6:]
                    recent_counts.extend([count for _, count in recent_freq])

            trend = "stable"
            if len(recent_counts) >= 2:
                if recent_counts[-1] > recent_counts[0] * 1.5:
                    trend = "increasing"
                elif recent_counts[-1] < recent_counts[0] * 0.5:
                    trend = "decreasing"

            frequency_trends[category] = {
                "count": len(cat_errors),
                "total_occurrences": total_count,
                "avg_occurrences": avg_count,
                "trend": trend,
                "critical_errors": len([e for e_var in cat_errors if e.is_critical]),
            }

        # Identify error correlations
        correlations = self._find_error_correlations(errors)

        # Identify new errors (not seen before)
        new_errors = [
            error
            for error in errors
            if error.id not in self.error_cache
            or error.timestamp
            > (self.last_fetch_time or datetime.min.replace(tzinfo=timezone.utc))
        ]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_errors": len(errors),
            "categories": frequency_trends,
            "new_errors": len(new_errors),
            "critical_errors": len([e for e_var in errors if e.is_critical]),
            "correlations": correlations,
            "top_errors": [
                {
                    "id": error.id,
                    "title": error.title,
                    "count": error.count,
                    "level": error.level,
                    "category": error.category,
                }
                for error in sorted(errors, key=lambda x: x.count, reverse=True)[:10]
            ],
        }

    def _find_error_correlations(
        self, errors: List[SentryError]
    ) -> List[Dict[str, Any]]:
        """Find correlations between different errors"""
        correlations = []

        # Group errors by time windows (1 hour)
        time_windows = {}
        for error in errors:
            window = error.timestamp.replace(minute=0, second=0, microsecond=0)
            if window not in time_windows:
                time_windows[window] = []
            time_windows[window].append(error)

        # Find co-occurring errors
        for window, window_errors in time_windows.items():
            if len(window_errors) > 1:
                # Check for errors that happen together
                error_types = [error.category for error in window_errors]
                unique_types = set(error_types)

                if len(unique_types) > 1:
                    correlations.append(
                        {
                            "window": window.isoformat(),
                            "correlated_categories": list(unique_types),
                            "error_count": len(window_errors),
                            "potential_root_cause": self._identify_root_cause(
                                window_errors
                            ),
                        }
                    )

        return correlations

    def _identify_root_cause(self, related_errors: List[SentryError]) -> str:
        """Attempt to identify root cause from related errors"""
        # Simple heuristic: infrastructure errors often cause cascading issues
        categories = [error.category for error in related_errors]

        if "infrastructure" in categories:
            return "infrastructure"
        elif "database" in categories:
            return "database"
        elif "performance" in categories and len(set(categories)) > 1:
            return "performance_cascade"
        else:
            return "unknown"

    def get_error_suggestions(self, error: SentryError) -> List[Dict[str, str]]:
        """Get automated resolution suggestions for an error"""
        suggestions = []

        message_lower = error.message.lower()
        category = error.category

        # Performance suggestions
        if category == "performance":
            if "timeout" in message_lower:
                suggestions.append(
                    {
                        "type": "configuration",
                        "title": "Increase timeout values",
                        "description": "Consider increasing request timeout settings",
                        "confidence": "medium",
                    }
                )
            if "memory" in message_lower:
                suggestions.append(
                    {
                        "type": "optimization",
                        "title": "Memory optimization",
                        "description": "Review memory usage patterns and implement garbage collection",
                        "confidence": "high",
                    }
                )

        # Application suggestions
        elif category == "application":
            if "import" in message_lower or "module" in message_lower:
                suggestions.append(
                    {
                        "type": "dependency",
                        "title": "Fix import dependencies",
                        "description": "Check and update missing dependencies in requirements.txt",
                        "confidence": "high",
                    }
                )
            if "attribute" in message_lower:
                suggestions.append(
                    {
                        "type": "code_fix",
                        "title": "Fix attribute access",
                        "description": "Review object attribute access patterns",
                        "confidence": "medium",
                    }
                )

        # Infrastructure suggestions
        elif category == "infrastructure":
            if "connection" in message_lower:
                suggestions.append(
                    {
                        "type": "configuration",
                        "title": "Connection pool settings",
                        "description": "Adjust connection pool size and retry logic",
                        "confidence": "high",
                    }
                )
            if "rate limit" in message_lower:
                suggestions.append(
                    {
                        "type": "throttling",
                        "title": "Implement rate limiting",
                        "description": "Add exponential backoff and rate limiting",
                        "confidence": "high",
                    }
                )

        return suggestions

    async def monitor_continuously(
        self, interval_seconds: int = 300, callback: Optional[callable] = None
    ) -> None:
        """
        Continuously monitor Sentry for new errors

        Args:
            interval_seconds: Time between monitoring cycles
            callback: Optional callback function to handle new errors
        """
        logger.info(f"Starting continuous monitoring (interval: {interval_seconds}s)")

        while True:
            try:
                # Fetch recent errors
                errors = self.fetch_errors(
                    since=datetime.now(timezone.utc)
                    - timedelta(seconds=interval_seconds * 2)
                )

                if errors:
                    logger.info(f"Found {len(errors)} recent errors")

                    # Analyze patterns
                    analysis = self.analyze_error_patterns(errors)

                    # Call callback if provided
                    if callback:
                        await callback(errors, analysis)

                # Wait for next cycle
                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(interval_seconds)

    def export_error_data(self, errors: List[SentryError], filepath: str) -> None:
        """Export error data to JSON file"""
        try:
            data = {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "error_count": len(errors),
                "errors": [error.to_dict() for error in errors],
            }

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported {len(errors)} errors to {filepath}")

        except Exception as e:
            logger.error(f"Failed to export error data: {e}")


# Example usage and testing
async     """Example Usage"""
def example_usage():
    """Example of how to use the Sentry monitor"""
    try:
        # Initialize monitor
        monitor = SentryMonitor()

        # Fetch recent errors
        errors = monitor.fetch_errors(limit=50)
        print(f"Fetched {len(errors)} errors")

        # Analyze patterns
        analysis = monitor.analyze_error_patterns(errors)
        print(f"Analysis: {json.dumps(analysis, indent=2, default=str)}")

        # Get suggestions for critical errors
        critical_errors = [e for e_var in errors if e.is_critical]
        for error in critical_errors[:3]:
            suggestions = monitor.get_error_suggestions(error)
            print(f"Suggestions for {error.title}: {suggestions}")

        # Export data
        monitor.export_error_data(errors, "/tmp/sentry_errors.json")

    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
