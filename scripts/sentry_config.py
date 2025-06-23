"""
Sentry + Seer AI Configuration for KindleMint Engine
"""

import os
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

def init_sentry(script_name: str = "kindlemint-script"):
    """Initialize Sentry with Seer AI-optimized configuration"""
    
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if not sentry_dsn:
        print("⚠️ No SENTRY_DSN found - Sentry monitoring disabled")
        return False
    
    # Initialize Sentry with comprehensive integrations
    sentry_sdk.init(
        dsn=sentry_dsn,
        
        # Environment and release tracking
        environment=os.getenv('ENVIRONMENT', 'production'),
        release=f"kindlemint@{os.getenv('GITHUB_SHA', 'local')[:8]}",
        
        # Performance monitoring for Seer AI
        traces_sample_rate=1.0,  # 100% performance monitoring
        profiles_sample_rate=1.0,  # 100% profiling for Seer insights
        
        # Enhanced error tracking
        attach_stacktrace=True,
        send_default_pii=False,  # Privacy compliance
        max_breadcrumbs=50,
        
        # Integrations for complex debugging
        integrations=[
            LoggingIntegration(level=None, event_level=None),
            AsyncioIntegration(transaction_style="task"),
            ThreadingIntegration(propagate_hub=True),
        ],
        
        # Custom tags for KindleMint context
        initial_scope={
            "tags": {
                "component": script_name,
                "system": "kindlemint-engine",
                "automation_type": "kdp-publishing"
            }
        },
        
        # Seer AI optimization
        _experiments={
            "profiles_sample_rate": 1.0,
        }
    )
    
    # Set user context for better debugging
    sentry_sdk.set_user({
        "id": "kindlemint-automation",
        "system": script_name
    })
    
    # Set custom context for KDP automation
    sentry_sdk.set_context("kdp_automation", {
        "script": script_name,
        "python_version": os.sys.version,
        "environment": os.getenv('ENVIRONMENT', 'local')
    })
    
    print(f"✅ Sentry + Seer AI initialized for {script_name}")
    return True

def track_kdp_operation(operation_name: str, metadata: dict = None):
    """Track KDP operations for Seer AI analysis"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("kdp_operation", operation_name)
        if metadata:
            scope.set_context("operation_metadata", metadata)
        
        # Create transaction for Seer AI performance tracking
        transaction = sentry_sdk.start_transaction(
            op="kdp_automation",
            name=operation_name
        )
        
        return transaction

def capture_kdp_error(error: Exception, context: dict = None):
    """Capture KDP automation errors with rich context for Seer AI"""
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("error_category", "kdp_automation")
        
        if context:
            scope.set_context("kdp_error_context", context)
        
        # Additional context for browser automation errors
        if "playwright" in str(error).lower() or "selenium" in str(error).lower():
            scope.set_tag("automation_type", "browser")
            scope.set_context("browser_automation", {
                "error_type": type(error).__name__,
                "likely_cause": "browser_automation_failure"
            })
        
        # API integration error context
        if any(api in str(error).lower() for api in ["openai", "serpapi", "slack", "amazon"]):
            scope.set_tag("automation_type", "api_integration")
            scope.set_context("api_integration", {
                "error_type": type(error).__name__,
                "likely_cause": "external_api_failure"
            })
    
    return sentry_sdk.capture_exception(error)

def add_breadcrumb(message: str, category: str = "automation", level: str = "info", data: dict = None):
    """Add breadcrumbs for Seer AI debugging context"""
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )

# Context managers for automated tracking
class SentryKDPOperation:
    """Context manager for tracking KDP operations with Seer AI"""
    
    def __init__(self, operation_name: str, metadata: dict = None):
        self.operation_name = operation_name
        self.metadata = metadata or {}
        self.transaction = None
    
    def __enter__(self):
        self.transaction = track_kdp_operation(self.operation_name, self.metadata)
        add_breadcrumb(f"Starting KDP operation: {self.operation_name}", data=self.metadata)
        return self.transaction
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            capture_kdp_error(exc_val, {
                "operation": self.operation_name,
                "metadata": self.metadata
            })
            add_breadcrumb(f"KDP operation failed: {self.operation_name}", level="error")
        else:
            add_breadcrumb(f"KDP operation completed: {self.operation_name}", level="info")
        
        if self.transaction:
            self.transaction.finish()
        
        return False  # Don't suppress exceptions