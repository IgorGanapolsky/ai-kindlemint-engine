#!/usr/bin/env python3
"""
Sentry & Seer AI Integration for KindleMint Empire
Professional-grade error tracking, performance monitoring, and AI-powered diagnostics
"""
import os
import sys
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from pathlib import Path
from typing import Optional, Dict, Any

class SentryManager:
    """Manages Sentry integration for the KindleMint Empire."""
    
    def __init__(self):
        self.dsn = os.getenv('SENTRY_DSN')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.release = self._get_release_version()
        self.is_initialized = False
        
    def initialize(self, 
                   service_name: str,
                   enable_seer: bool = True,
                   custom_tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Initialize Sentry with KindleMint-specific configuration.
        
        Args:
            service_name: Name of the service (e.g., 'kdp-publisher', 'content-generator')
            enable_seer: Enable Seer AI-powered diagnostics
            custom_tags: Additional tags for this service
            
        Returns:
            bool: True if initialized successfully
        """
        if not self.dsn:
            print("⚠️ SENTRY: DSN not configured - error tracking disabled")
            return False
            
        try:
            # Configure integrations
            integrations = [
                LoggingIntegration(
                    level=None,        # Capture info and above as breadcrumbs
                    event_level=None   # Send errors as events
                ),
                StdlibIntegration(),
                ExcepthookIntegration(always_run=True),
                ThreadingIntegration(propagate_hub=True),
            ]
            
            # Initialize Sentry
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                release=self.release,
                integrations=integrations,
                traces_sample_rate=0.1,  # 10% performance monitoring
                profiles_sample_rate=0.1,  # 10% profiling
                enable_tracing=True,
                attach_stacktrace=True,
                send_default_pii=False,  # Protect user data
                max_breadcrumbs=50,
                before_send=self._before_send_filter,
            )
            
            # Set service context
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("service", service_name)
                scope.set_tag("business", "kindlemint_empire")
                scope.set_tag("automation_type", "publishing")
                scope.set_context("runtime", {
                    "python_version": sys.version,
                    "platform": sys.platform,
                })
                
                # Add custom tags
                if custom_tags:
                    for key, value in custom_tags.items():
                        scope.set_tag(key, value)
                        
                # Business context
                scope.set_context("business_metrics", {
                    "series": "Large_Print_Crossword_Masters",
                    "target_market": "seniors_puzzles",
                    "automation_goal": "daily_publishing"
                })
            
            # Configure Seer AI (if enabled)
            if enable_seer:
                self._configure_seer_ai()
                
            self.is_initialized = True
            print(f"✅ SENTRY: Initialized for {service_name} (env: {self.environment})")
            
            # Test the integration
            self._send_initialization_event(service_name)
            
            return True
            
        except Exception as e:
            print(f"❌ SENTRY: Failed to initialize: {e}")
            return False
            
    def _get_release_version(self) -> str:
        """Get the current release version from git or environment."""
        # Try environment variable first
        version = os.getenv('RELEASE_VERSION')
        if version:
            return version
            
        # Try to get git commit hash
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return f"git-{result.stdout.strip()}"
        except:
            pass
            
        return "unknown"
        
    def _before_send_filter(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter and enhance events before sending to Sentry."""
        # Don't send events for expected business logic (like "no content to publish")
        if 'exception' in event:
            exc_info = hint.get('exc_info')
            if exc_info:
                exc_type, exc_value, _ = exc_info
                exc_message = str(exc_value)
                
                # Filter out expected business conditions
                if any(phrase in exc_message.lower() for phrase in [
                    'no content to publish',
                    'job skipped',
                    'already published',
                    'rate limit'
                ]):
                    return None  # Don't send to Sentry
                    
        # Enhance with business context
        event.setdefault('tags', {})
        event['tags']['business_critical'] = self._is_business_critical(event)
        
        return event
        
    def _is_business_critical(self, event: Dict[str, Any]) -> str:
        """Determine if an error is business critical."""
        if 'exception' in event:
            exc_info = event.get('exception', {}).get('values', [{}])
            if exc_info:
                exc_type = exc_info[0].get('type', '')
                
                # Publishing failures are critical
                if any(term in exc_type.lower() for term in ['kdp', 'publish', 'upload']):
                    return 'high'
                    
                # Cost tracking failures are critical
                if any(term in exc_type.lower() for term in ['cost', 'billing', 'revenue']):
                    return 'high'
                    
        return 'medium'
        
    def _configure_seer_ai(self):
        """Configure Seer AI for intelligent error analysis."""
        with sentry_sdk.configure_scope() as scope:
            scope.set_context("seer_config", {
                "ai_analysis": True,
                "business_domain": "automated_publishing",
                "error_categories": [
                    "kdp_publishing_errors",
                    "content_generation_failures", 
                    "api_integration_issues",
                    "automation_workflow_failures"
                ],
                "priority_workflows": [
                    "daily_publishing",
                    "cost_tracking",
                    "sales_reporting"
                ]
            })
            
    def _send_initialization_event(self, service_name: str):
        """Send initialization event to verify Sentry is working."""
        with sentry_sdk.configure_scope() as scope:
            scope.set_level('info')
            sentry_sdk.capture_message(
                f"KindleMint {service_name} service initialized with Sentry monitoring",
                level='info'
            )
            
    def capture_business_event(self, 
                             event_type: str, 
                             message: str,
                             level: str = 'info',
                             extra_data: Optional[Dict[str, Any]] = None):
        """Capture business-specific events for monitoring."""
        if not self.is_initialized:
            return
            
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("event_type", event_type)
            scope.set_level(level)
            
            if extra_data:
                scope.set_context("business_data", extra_data)
                
            sentry_sdk.capture_message(message, level=level)
            
    def capture_performance_metrics(self, 
                                  operation: str,
                                  duration: float,
                                  success: bool,
                                  metadata: Optional[Dict[str, Any]] = None):
        """Capture performance metrics for business operations."""
        if not self.is_initialized:
            return
            
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("operation", operation)
            scope.set_tag("success", str(success))
            scope.set_context("performance", {
                "duration_seconds": duration,
                "operation_type": operation,
                "success": success,
                "metadata": metadata or {}
            })
            
            message = f"Operation {operation} {'succeeded' if success else 'failed'} in {duration:.2f}s"
            level = 'info' if success else 'warning'
            sentry_sdk.capture_message(message, level=level)

# Global Sentry manager instance
sentry_manager = SentryManager()

def init_sentry(service_name: str, **kwargs) -> bool:
    """
    Initialize Sentry for a service.
    
    Usage:
        from kindlemint.utils.sentry_config import init_sentry
        init_sentry("kdp-publisher", custom_tags={"workflow": "autonomous"})
    """
    return sentry_manager.initialize(service_name, **kwargs)

def capture_business_event(event_type: str, message: str, **kwargs):
    """Capture a business event."""
    sentry_manager.capture_business_event(event_type, message, **kwargs)
    
def capture_performance(operation: str, duration: float, success: bool, **kwargs):
    """Capture performance metrics."""
    sentry_manager.capture_performance_metrics(operation, duration, success, **kwargs)

# Context managers for performance tracking
class SentryPerformanceTracker:
    """Context manager for tracking operation performance."""
    
    def __init__(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.metadata = metadata or {}
        self.start_time = None
        
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        success = exc_type is None
        
        capture_performance(
            self.operation_name,
            duration,
            success,
            metadata=self.metadata
        )
        
        return False  # Don't suppress exceptions