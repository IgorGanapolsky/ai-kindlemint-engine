#!/usr/bin/env python3
"""
Alert Orchestrator - Main orchestration system for autonomous alert handling
Coordinates Sentry monitoring, Slack alerts, error analysis, and automated resolution
"""

import asyncio
import json
import logging
import os
import signal
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Import our components
from .sentry_monitor import SentryMonitor, SentryError
from .slack_handler import SlackBot, SlackWebhookHandler
from .error_analyzer import ErrorAnalyzer, ErrorClassification
from .auto_resolver import AutoResolver, ResolutionResult

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertOrchestrator")

@dataclass
class OrchestrationConfig:
    """Configuration for alert orchestration"""
    sentry_enabled: bool = True
    slack_enabled: bool = True
    auto_resolution_enabled: bool = True
    dry_run: bool = False
    monitoring_interval: int = 300  # seconds
    max_concurrent_resolutions: int = 3
    escalation_thresholds: Dict[str, int] = None
    notification_channels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.escalation_thresholds is None:
            self.escalation_thresholds = {
                'critical_errors_per_hour': 10,
                'failed_resolutions_per_hour': 5,
                'error_rate_increase_percent': 50
            }
        
        if self.notification_channels is None:
            self.notification_channels = {
                'alerts': '#alerts',
                'resolutions': '#devops',
                'escalations': '#oncall'
            }

@dataclass
class OrchestrationMetrics:
    """Metrics for orchestration performance"""
    total_errors_processed: int = 0
    auto_resolutions_attempted: int = 0
    auto_resolutions_successful: int = 0
    alerts_sent: int = 0
    escalations_triggered: int = 0
    average_resolution_time: float = 0.0
    error_categories: Dict[str, int] = None
    
    def __post_init__(self):
        if self.error_categories is None:
            self.error_categories = {}

class AlertOrchestrator:
    """
    Main orchestration system for autonomous alert handling
    
    Features:
    - Continuous Sentry monitoring
    - Intelligent error analysis and categorization
    - Automated resolution attempts
    - Smart Slack notifications and escalation
    - Performance metrics and reporting
    - Graceful handling of multiple concurrent issues
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize alert orchestrator with configuration"""
        self.config = self._load_config(config_file)
        self.metrics = OrchestrationMetrics()
        
        # Initialize components
        self.sentry_monitor = None
        self.slack_bot = None
        self.error_analyzer = None
        self.auto_resolver = None
        
        # State management
        self.active_alerts: Dict[str, Dict] = {}
        self.resolution_queue: List[Dict] = []
        self.escalation_history: List[Dict] = []
        self.shutdown_requested = False
        
        # Initialize components based on configuration
        self._initialize_components()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Alert orchestrator initialized")
    
    def _load_config(self, config_file: Optional[str]) -> OrchestrationConfig:
        """Load configuration from file or environment"""
        config_data = {}
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
        
        # Override with environment variables
        env_config = {
            'sentry_enabled': os.getenv('SENTRY_ENABLED', 'true').lower() == 'true',
            'slack_enabled': os.getenv('SLACK_ENABLED', 'true').lower() == 'true',
            'auto_resolution_enabled': os.getenv('AUTO_RESOLUTION_ENABLED', 'true').lower() == 'true',
            'dry_run': os.getenv('DRY_RUN', 'false').lower() == 'true',
            'monitoring_interval': int(os.getenv('MONITORING_INTERVAL', '300'))
        }
        
        # Merge configurations
        config_data.update(env_config)
        
        return OrchestrationConfig(**config_data)
    
    def _initialize_components(self):
        """Initialize all orchestration components"""
        try:
            # Initialize Sentry monitor
            if self.config.sentry_enabled:
                self.sentry_monitor = SentryMonitor()
                logger.info("Sentry monitor initialized")
            
            # Initialize Slack bot
            if self.config.slack_enabled:
                self.slack_bot = SlackBot()
                logger.info("Slack bot initialized")
            
            # Initialize error analyzer
            self.error_analyzer = ErrorAnalyzer()
            logger.info("Error analyzer initialized")
            
            # Initialize auto resolver
            if self.config.auto_resolution_enabled:
                self.auto_resolver = AutoResolver(dry_run=self.config.dry_run)
                logger.info("Auto resolver initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    async def start_orchestration(self):
        """Start the main orchestration loop"""
        logger.info("Starting alert orchestration...")
        
        try:
            # Start continuous monitoring
            if self.sentry_monitor:
                monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Start resolution processing
            resolution_task = asyncio.create_task(self._resolution_loop())
            
            # Start metrics reporting
            metrics_task = asyncio.create_task(self._metrics_loop())
            
            # Wait for shutdown signal or task completion
            while not self.shutdown_requested:
                await asyncio.sleep(1)
            
            logger.info("Shutdown requested, stopping orchestration...")
            
            # Cancel tasks
            if self.sentry_monitor:
                monitoring_task.cancel()
            resolution_task.cancel()
            metrics_task.cancel()
            
            # Wait for graceful shutdown
            await asyncio.gather(
                monitoring_task, resolution_task, metrics_task,
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"Error in orchestration: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _monitoring_loop(self):
        """Main monitoring loop for Sentry errors"""
        logger.info("Starting monitoring loop...")
        
        last_fetch_time = datetime.now()
        
        while not self.shutdown_requested:
            try:
                # Fetch new errors from Sentry
                errors = self.sentry_monitor.fetch_errors(
                    since=last_fetch_time,
                    limit=100
                )
                
                if errors:
                    logger.info(f"Found {len(errors)} new errors")
                    await self._process_errors(errors)
                
                last_fetch_time = datetime.now()
                self.metrics.total_errors_processed += len(errors)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.monitoring_interval)
    
    async def _process_errors(self, errors: List[SentryError]):
        """Process a batch of errors"""
        for error in errors:
            try:
                await self._process_single_error(error)
            except Exception as e:
                logger.error(f"Error processing {error.id}: {e}")
    
    async def _process_single_error(self, error: SentryError):
        """Process a single error through the full pipeline"""
        error_id = error.id
        
        # Skip if already being processed
        if error_id in self.active_alerts:
            return
        
        logger.info(f"Processing error: {error.title}")
        
        # Add to active alerts
        self.active_alerts[error_id] = {
            'error': error,
            'start_time': datetime.now(),
            'status': 'analyzing'
        }
        
        try:
            # Analyze error
            error_data = {
                'id': error.id,
                'message': error.message,
                'level': error.level,
                'environment': error.environment,
                'count': error.count,
                'timestamp': error.timestamp.isoformat(),
                'context': error.context
            }
            
            classification = self.error_analyzer.analyze_error(error_data)
            
            # Update metrics
            category = classification.primary_category
            self.metrics.error_categories[category] = self.metrics.error_categories.get(category, 0) + 1
            
            # Determine if alert should be sent
            should_alert = self._should_send_alert(error, classification)
            
            if should_alert and self.slack_bot:
                await self._send_alert(error, classification)
            
            # Determine if auto-resolution should be attempted
            should_resolve = self._should_attempt_resolution(error, classification)
            
            if should_resolve and self.auto_resolver:
                await self._queue_resolution(error, classification)
            
            # Check for escalation
            should_escalate = self._should_escalate(error, classification)
            
            if should_escalate:
                await self._escalate_alert(error, classification)
            
            # Update alert status
            self.active_alerts[error_id]['status'] = 'processed'
            self.active_alerts[error_id]['classification'] = classification
            
        except Exception as e:
            logger.error(f"Error processing {error_id}: {e}")
            self.active_alerts[error_id]['status'] = 'failed'
            self.active_alerts[error_id]['error_message'] = str(e)
    
    def _should_send_alert(self, error: SentryError, classification: ErrorClassification) -> bool:
        """Determine if an alert should be sent to Slack"""
        # Always alert for critical errors
        if error.is_critical or classification.resolution_urgency == 'critical':
            return True
        
        # Alert for high confidence classifications
        if classification.confidence_score >= 0.8:
            return True
        
        # Alert for production errors
        if error.environment.lower() in ['production', 'prod'] and error.level in ['error', 'fatal']:
            return True
        
        # Alert for high frequency errors
        if error.count > 10:
            return True
        
        return False
    
    def _should_attempt_resolution(self, error: SentryError, classification: ErrorClassification) -> bool:
        """Determine if auto-resolution should be attempted"""
        # Skip if auto-resolution is disabled
        if not self.config.auto_resolution_enabled:
            return False
        
        # Skip if too many concurrent resolutions
        active_resolutions = len([r for r in self.resolution_queue if r.get('status') == 'in_progress'])
        if active_resolutions >= self.config.max_concurrent_resolutions:
            return False
        
        # Require minimum confidence for auto-resolution
        if classification.confidence_score < 0.7:
            return False
        
        # Auto-resolve for known patterns with high confidence
        if classification.primary_category in ['performance', 'network', 'authentication'] and classification.confidence_score >= 0.8:
            return True
        
        # Auto-resolve critical errors with very high confidence
        if classification.resolution_urgency == 'critical' and classification.confidence_score >= 0.9:
            return True
        
        return False
    
    def _should_escalate(self, error: SentryError, classification: ErrorClassification) -> bool:
        """Determine if alert should be escalated"""
        # Escalate critical errors immediately
        if error.is_critical or classification.resolution_urgency == 'critical':
            return True
        
        # Escalate if error rate is increasing rapidly
        recent_errors = [e for e in self.active_alerts.values() 
                        if e.get('start_time', datetime.min) > datetime.now() - timedelta(hours=1)]
        
        if len(recent_errors) > self.config.escalation_thresholds['critical_errors_per_hour']:
            return True
        
        # Escalate if auto-resolution failed multiple times
        failed_resolutions = len([r for r in self.resolution_queue 
                                 if r.get('status') == 'failed' and 
                                 r.get('timestamp', datetime.min) > datetime.now() - timedelta(hours=1)])
        
        if failed_resolutions > self.config.escalation_thresholds['failed_resolutions_per_hour']:
            return True
        
        return False
    
    async def _send_alert(self, error: SentryError, classification: ErrorClassification):
        """Send alert to Slack"""
        try:
            alert_data = {
                'title': error.title,
                'description': error.message,
                'error_details': error.message,
                'source': 'sentry',
                'environment': error.environment,
                'error_id': error.id,
                'timestamp': error.timestamp.isoformat(),
                'metrics': {
                    'count': error.count,
                    'level': error.level,
                    'confidence': classification.confidence_score,
                    'category': classification.primary_category
                }
            }
            
            # Determine alert type and severity
            alert_type = classification.primary_category
            severity = self._map_urgency_to_severity(classification.resolution_urgency)
            
            # Send to appropriate channel
            channel = self.config.notification_channels.get('alerts', '#alerts')
            
            message_ts = self.slack_bot.send_alert(
                channel=channel,
                alert_data=alert_data,
                alert_type=alert_type,
                severity=severity
            )
            
            self.metrics.alerts_sent += 1
            
            # Store alert info for thread management
            if error.id in self.active_alerts:
                self.active_alerts[error.id]['slack_message_ts'] = message_ts
            
            logger.info(f"Alert sent for error {error.id}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def _queue_resolution(self, error: SentryError, classification: ErrorClassification):
        """Queue error for automated resolution"""
        resolution_item = {
            'error_id': error.id,
            'error': error,
            'classification': classification,
            'status': 'queued',
            'timestamp': datetime.now(),
            'attempts': 0
        }
        
        self.resolution_queue.append(resolution_item)
        logger.info(f"Queued error {error.id} for auto-resolution")
    
    async def _escalate_alert(self, error: SentryError, classification: ErrorClassification):
        """Escalate alert to higher priority channels"""
        try:
            escalation_data = {
                'title': f"ESCALATED: {error.title}",
                'description': f"Critical error requires immediate attention: {error.message}",
                'error_details': error.message,
                'source': 'sentry_escalation',
                'environment': error.environment,
                'error_id': error.id,
                'escalation_reason': self._get_escalation_reason(error, classification),
                'suggested_actions': classification.suggested_actions
            }
            
            # Send to escalation channel
            channel = self.config.notification_channels.get('escalations', '#oncall')
            
            self.slack_bot.send_alert(
                channel=channel,
                alert_data=escalation_data,
                alert_type="escalation",
                severity="critical"
            )
            
            self.metrics.escalations_triggered += 1
            
            # Log escalation
            self.escalation_history.append({
                'error_id': error.id,
                'timestamp': datetime.now().isoformat(),
                'reason': escalation_data['escalation_reason']
            })
            
            logger.warning(f"Escalated error {error.id}")
            
        except Exception as e:
            logger.error(f"Failed to escalate alert: {e}")
    
    def _get_escalation_reason(self, error: SentryError, classification: ErrorClassification) -> str:
        """Get reason for escalation"""
        if error.is_critical:
            return "Critical error detected"
        elif classification.resolution_urgency == 'critical':
            return "High business impact error"
        elif error.count > 50:
            return "High frequency error (50+ occurrences)"
        else:
            return "Escalation threshold exceeded"
    
    async def _resolution_loop(self):
        """Process resolution queue"""
        logger.info("Starting resolution loop...")
        
        while not self.shutdown_requested:
            try:
                # Process queued resolutions
                for resolution_item in self.resolution_queue[:]:
                    if resolution_item['status'] == 'queued':
                        await self._attempt_resolution(resolution_item)
                
                # Clean up completed resolutions
                self.resolution_queue = [
                    r for r in self.resolution_queue 
                    if r['status'] in ['queued', 'in_progress']
                ]
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in resolution loop: {e}")
                await asyncio.sleep(30)
    
    async def _attempt_resolution(self, resolution_item: Dict):
        """Attempt to resolve an error"""
        error_id = resolution_item['error_id']
        error = resolution_item['error']
        classification = resolution_item['classification']
        
        logger.info(f"Attempting resolution for error {error_id}")
        
        resolution_item['status'] = 'in_progress'
        resolution_item['attempts'] += 1
        
        try:
            # Prepare error data for resolver
            error_data = {
                'id': error.id,
                'message': error.message,
                'environment': error.environment,
                'service_name': error.context.get('tags', {}).get('service', 'unknown'),
                'current_pool_size': 20  # Example - would extract from context
            }
            
            # Attempt resolution
            result = await self.auto_resolver.resolve_error(error_data, asdict(classification))
            
            self.metrics.auto_resolutions_attempted += 1
            
            if result and result.success:
                resolution_item['status'] = 'resolved'
                resolution_item['result'] = result
                self.metrics.auto_resolutions_successful += 1
                
                # Send success notification
                await self._send_resolution_notification(error, result, success=True)
                
                logger.info(f"Successfully resolved error {error_id}")
                
            else:
                resolution_item['status'] = 'failed'
                resolution_item['result'] = result
                
                # Send failure notification
                await self._send_resolution_notification(error, result, success=False)
                
                logger.warning(f"Failed to resolve error {error_id}")
            
        except Exception as e:
            resolution_item['status'] = 'failed'
            resolution_item['error_message'] = str(e)
            logger.error(f"Error during resolution attempt for {error_id}: {e}")
    
    async def _send_resolution_notification(self, error: SentryError, result: Optional[ResolutionResult], success: bool):
        """Send notification about resolution attempt"""
        if not self.slack_bot:
            return
        
        try:
            channel = self.config.notification_channels.get('resolutions', '#devops')
            
            if success:
                notification_data = {
                    'title': f"✅ Auto-Resolution Successful",
                    'description': f"Successfully resolved: {error.title}",
                    'source': 'auto_resolver',
                    'resolution_details': result.output if result else 'No details available',
                    'execution_time': f"{result.execution_time:.2f}s" if result else 'Unknown'
                }
                severity = 'low'
            else:
                notification_data = {
                    'title': f"❌ Auto-Resolution Failed", 
                    'description': f"Failed to resolve: {error.title}",
                    'source': 'auto_resolver',
                    'error_details': result.error_message if result else 'Unknown error',
                    'next_steps': 'Manual intervention may be required'
                }
                severity = 'medium'
            
            self.slack_bot.send_alert(
                channel=channel,
                alert_data=notification_data,
                alert_type="resolution",
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to send resolution notification: {e}")
    
    def _map_urgency_to_severity(self, urgency: str) -> str:
        """Map resolution urgency to Slack severity"""
        mapping = {
            'critical': 'critical',
            'high': 'high', 
            'medium': 'medium',
            'low': 'low'
        }
        return mapping.get(urgency, 'medium')
    
    async def _metrics_loop(self):
        """Periodic metrics reporting"""
        logger.info("Starting metrics loop...")
        
        while not self.shutdown_requested:
            try:
                await asyncio.sleep(3600)  # Report every hour
                await self._report_metrics()
                
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")
                await asyncio.sleep(3600)
    
    async def _report_metrics(self):
        """Report orchestration metrics"""
        try:
            # Calculate success rate
            success_rate = 0.0
            if self.metrics.auto_resolutions_attempted > 0:
                success_rate = (self.metrics.auto_resolutions_successful / 
                               self.metrics.auto_resolutions_attempted) * 100
            
            metrics_report = {
                'timestamp': datetime.now().isoformat(),
                'errors_processed': self.metrics.total_errors_processed,
                'alerts_sent': self.metrics.alerts_sent,
                'auto_resolutions_attempted': self.metrics.auto_resolutions_attempted,
                'auto_resolutions_successful': self.metrics.auto_resolutions_successful,
                'resolution_success_rate': f"{success_rate:.1f}%",
                'escalations_triggered': self.metrics.escalations_triggered,
                'active_alerts': len(self.active_alerts),
                'error_categories': self.metrics.error_categories
            }
            
            logger.info(f"Orchestration metrics: {json.dumps(metrics_report, indent=2)}")
            
            # Send metrics to Slack if enabled
            if self.slack_bot and self.metrics.total_errors_processed > 0:
                await self._send_metrics_report(metrics_report)
            
        except Exception as e:
            logger.error(f"Error reporting metrics: {e}")
    
    async def _send_metrics_report(self, metrics: Dict):
        """Send metrics report to Slack"""
        try:
            report_data = {
                'title': '📊 Alert Orchestration Metrics Report',
                'description': 'Hourly metrics for automated alert handling',
                'source': 'orchestrator_metrics',
                'metrics': metrics
            }
            
            channel = self.config.notification_channels.get('resolutions', '#devops')
            
            self.slack_bot.send_alert(
                channel=channel,
                alert_data=report_data,
                alert_type="metrics",
                severity="low"
            )
            
        except Exception as e:
            logger.error(f"Failed to send metrics report: {e}")
    
    async def _cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("Cleaning up orchestrator resources...")
        
        try:
            # Save state if needed
            state_data = {
                'shutdown_time': datetime.now().isoformat(),
                'active_alerts_count': len(self.active_alerts),
                'pending_resolutions': len([r for r in self.resolution_queue if r['status'] == 'queued']),
                'metrics': asdict(self.metrics)
            }
            
            # Save to file for potential recovery
            with open('orchestrator_state.json', 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            logger.info("Orchestrator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# CLI interface
async def main():
    """Main entry point for CLI execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alert Orchestrator")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
    args = parser.parse_args()
    
    # Override config with CLI args
    if args.dry_run:
        os.environ['DRY_RUN'] = 'true'
    
    try:
        orchestrator = AlertOrchestrator(config_file=args.config)
        await orchestrator.start_orchestration()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())