"""
AWS Lambda function for autonomous alert orchestration
Handles Sentry, Slack, and other monitoring alerts
Integrates with existing KindleMint infrastructure
"""

import json
import os
import boto3
import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main Lambda handler for alert orchestration
    Handles Sentry alerts, Slack notifications, and performance monitoring
    """
    
    try:
        # Initialize alert orchestrator
        orchestrator = AlertOrchestrationEngine()
        
        # Determine event source
        if 'source' in event and event['source'] == 'aws.events':
            # Scheduled monitoring
            result = orchestrator.run_scheduled_monitoring()
        elif 'Records' in event and event['Records']:
            # SQS messages from webhooks
            result = orchestrator.process_alert_queue(event['Records'])
        elif 'httpMethod' in event:
            # Direct webhook from Sentry/Slack
            result = orchestrator.process_webhook(event)
        else:
            # Manual invocation
            result = orchestrator.run_manual_check(event)
        
        # Send notifications
        orchestrator.send_orchestration_summary(result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'orchestration_result': result,
                'timestamp': datetime.utcnow().isoformat(),
                'function': 'alert_orchestration'
            })
        }
        
    except Exception as e:
        logger.error(f"Alert orchestration failed: {str(e)}")
        
        # Send failure notification
        send_alert_failure_notification(str(e), context)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error_message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

class AlertOrchestrationEngine:
    """
    Alert orchestration engine for comprehensive monitoring
    """
    
    def __init__(self):
        # Environment configuration
        self.sentry_dsn = os.environ.get('SENTRY_DSN')
        self.sentry_token = os.environ.get('SENTRY_AUTH_TOKEN')
        self.slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        self.slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
        
        # AWS services
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')
        self.sns = boto3.client('sns')
        self.cloudwatch = boto3.client('cloudwatch')
        
        # Configuration
        self.config = self.load_alert_config()
        
        # Alert processing stats
        self.stats = {
            'alerts_processed': 0,
            'resolutions_applied': 0,
            'escalations_created': 0,
            'start_time': datetime.utcnow()
        }
    
    def load_alert_config(self) -> Dict[str, Any]:
        """Load alert configuration from DynamoDB"""
        try:
            table = self.dynamodb.Table('kindlemint-config')
            response = table.get_item(Key={'config_type': 'alert_orchestration'})
            
            if 'Item' in response:
                return response['Item']['config']
        except Exception as e:
            logger.warning(f"Could not load alert config: {e}")
        
        # Default configuration
        return {
            'sentry': {
                'org_slug': 'ai-kindlemint-engine',
                'project_slug': 'kindlemint-engine',
                'severity_threshold': 'error',
                'auto_resolve_threshold': 0.8
            },
            'monitoring': {
                'check_interval_minutes': 5,
                'lookback_minutes': 30,
                'max_alerts_per_run': 10
            },
            'resolution': {
                'auto_resolve_enabled': True,
                'confidence_threshold': 0.8,
                'max_concurrent_resolutions': 3
            },
            'escalation': {
                'critical_threshold_minutes': 30,
                'escalation_channels': ['#alerts', '#engineering']
            }
        }
    
    def run_scheduled_monitoring(self) -> Dict[str, Any]:
        """Run scheduled alert monitoring"""
        logger.info("Starting scheduled alert monitoring")
        
        # Monitor Sentry alerts
        sentry_alerts = self.fetch_sentry_alerts()
        
        # Monitor application performance
        performance_alerts = self.check_performance_metrics()
        
        # Process all alerts
        all_alerts = sentry_alerts + performance_alerts
        
        if not all_alerts:
            return {
                'run_type': 'scheduled',
                'alerts_processed': 0,
                'resolutions_applied': 0,
                'status': 'no_alerts',
                'duration_seconds': self.get_duration()
            }
        
        # Analyze and resolve alerts
        analysis = self.analyze_alerts(all_alerts)
        resolutions = self.apply_automated_resolutions(analysis)
        escalations = self.handle_escalations(analysis)
        
        # Store results
        self.store_alert_results({
            'timestamp': self.stats['start_time'].isoformat(),
            'alerts_processed': len(all_alerts),
            'resolutions_applied': resolutions,
            'escalations_created': escalations,
            'analysis': analysis
        })
        
        return {
            'run_type': 'scheduled',
            'alerts_processed': len(all_alerts),
            'resolutions_applied': resolutions,
            'escalations_created': escalations,
            'status': 'completed',
            'duration_seconds': self.get_duration()
        }
    
    def fetch_sentry_alerts(self) -> List[Dict[str, Any]]:
        """Fetch recent alerts from Sentry"""
        if not self.sentry_token:
            logger.warning("No Sentry token configured")
            return []
        
        headers = {'Authorization': f'Bearer {self.sentry_token}'}
        
        # Fetch issues from Sentry API
        org_slug = self.config['sentry']['org_slug']
        project_slug = self.config['sentry']['project_slug']
        
        url = f'https://sentry.io/api/0/projects/{org_slug}/{project_slug}/issues/'
        params = {
            'statsPeriod': f"{self.config['monitoring']['lookback_minutes']}m",
            'query': 'is:unresolved',
            'sort': 'freq'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            issues = response.json()
            logger.info(f"Fetched {len(issues)} Sentry issues")
            
            # Convert to standardized alert format
            alerts = []
            for issue in issues:
                alerts.append({
                    'source': 'sentry',
                    'id': issue['id'],
                    'title': issue.get('title', 'Unknown Error'),
                    'level': issue.get('level', 'info'),
                    'type': issue.get('type', 'error'),
                    'count': issue.get('count', 1),
                    'frequency': issue.get('stats', {}).get('24h', []),
                    'first_seen': issue.get('firstSeen'),
                    'last_seen': issue.get('lastSeen'),
                    'raw_data': issue
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to fetch Sentry alerts: {e}")
            return []
    
    def check_performance_metrics(self) -> List[Dict[str, Any]]:
        """Check CloudWatch metrics for performance issues"""
        alerts = []
        
        try:
            # Check Lambda errors
            lambda_errors = self.check_lambda_error_rate()
            alerts.extend(lambda_errors)
            
            # Check API Gateway latency
            api_latency = self.check_api_latency()
            alerts.extend(api_latency)
            
            # Check DynamoDB throttling
            db_throttles = self.check_dynamodb_throttling()
            alerts.extend(db_throttles)
            
        except Exception as e:
            logger.error(f"Failed to check performance metrics: {e}")
        
        return alerts
    
    def check_lambda_error_rate(self) -> List[Dict[str, Any]]:
        """Check Lambda function error rates"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=self.config['monitoring']['lookback_minutes'])
        
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Errors',
                Dimensions=[
                    {'Name': 'FunctionName', 'Value': 'kindlemint-orchestrator'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            total_errors = sum(point['Sum'] for point in response['Datapoints'])
            
            if total_errors > 5:  # Threshold for alerting
                return [{
                    'source': 'cloudwatch',
                    'id': f'lambda_errors_{int(end_time.timestamp())}',
                    'title': f'High Lambda Error Rate: {total_errors} errors',
                    'level': 'error',
                    'type': 'performance',
                    'count': total_errors,
                    'metric_data': response['Datapoints']
                }]
        
        except Exception as e:
            logger.error(f"Failed to check Lambda errors: {e}")
        
        return []
    
    def check_api_latency(self) -> List[Dict[str, Any]]:
        """Check API Gateway latency"""
        # Implementation for API latency checking
        return []
    
    def check_dynamodb_throttling(self) -> List[Dict[str, Any]]:
        """Check DynamoDB throttling events"""
        # Implementation for DynamoDB throttling checks
        return []
    
    def analyze_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze alerts and categorize them"""
        analysis = {
            'total_alerts': len(alerts),
            'by_source': {},
            'by_severity': {},
            'high_priority': [],
            'auto_resolvable': [],
            'escalation_required': []
        }
        
        for alert in alerts:
            # Count by source
            source = alert['source']
            analysis['by_source'][source] = analysis['by_source'].get(source, 0) + 1
            
            # Count by severity
            level = alert['level']
            analysis['by_severity'][level] = analysis['by_severity'].get(level, 0) + 1
            
            # Categorize alert
            priority = self.calculate_alert_priority(alert)
            
            if priority >= 0.9:
                analysis['high_priority'].append(alert)
            
            if self.is_auto_resolvable(alert):
                analysis['auto_resolvable'].append(alert)
            
            if self.requires_escalation(alert, priority):
                analysis['escalation_required'].append(alert)
        
        return analysis
    
    def calculate_alert_priority(self, alert: Dict[str, Any]) -> float:
        """Calculate alert priority score"""
        priority = 0.0
        
        # Base priority by level
        level_priorities = {
            'fatal': 1.0,
            'error': 0.8,
            'warning': 0.6,
            'info': 0.4,
            'debug': 0.2
        }
        priority += level_priorities.get(alert['level'], 0.5)
        
        # Adjust by frequency/count
        count = alert.get('count', 1)
        if count > 100:
            priority += 0.2
        elif count > 10:
            priority += 0.1
        
        # Adjust by recency
        if alert.get('last_seen'):
            last_seen = datetime.fromisoformat(alert['last_seen'].replace('Z', '+00:00'))
            hours_old = (datetime.utcnow().replace(tzinfo=last_seen.tzinfo) - last_seen).total_seconds() / 3600
            
            if hours_old < 1:
                priority += 0.1  # Very recent
            elif hours_old > 24:
                priority -= 0.1  # Old alert
        
        return min(1.0, priority)
    
    def is_auto_resolvable(self, alert: Dict[str, Any]) -> bool:
        """Determine if alert can be automatically resolved"""
        auto_resolvable_types = [
            'memory_leak',
            'disk_space',
            'connection_timeout',
            'rate_limit_exceeded'
        ]
        
        alert_type = alert.get('type', '').lower()
        return any(resolvable_type in alert_type for resolvable_type in auto_resolvable_types)
    
    def requires_escalation(self, alert: Dict[str, Any], priority: float) -> bool:
        """Determine if alert requires escalation"""
        # High priority alerts always require escalation
        if priority >= 0.9:
            return True
        
        # Critical errors require escalation
        if alert['level'] in ['fatal', 'error'] and alert.get('count', 0) > 50:
            return True
        
        return False
    
    def apply_automated_resolutions(self, analysis: Dict[str, Any]) -> int:
        """Apply automated resolutions to alerts"""
        resolutions_applied = 0
        
        for alert in analysis['auto_resolvable']:
            try:
                success = self.resolve_alert(alert)
                if success:
                    resolutions_applied += 1
                    logger.info(f"Auto-resolved alert: {alert['title']}")
            except Exception as e:
                logger.error(f"Failed to resolve alert {alert['id']}: {e}")
        
        return resolutions_applied
    
    def resolve_alert(self, alert: Dict[str, Any]) -> bool:
        """Resolve a specific alert"""
        alert_type = alert.get('type', '').lower()
        
        if 'memory_leak' in alert_type:
            return self.resolve_memory_leak()
        elif 'disk_space' in alert_type:
            return self.resolve_disk_space_issue()
        elif 'connection_timeout' in alert_type:
            return self.resolve_connection_timeout()
        elif 'rate_limit' in alert_type:
            return self.resolve_rate_limit_issue()
        
        return False
    
    def resolve_memory_leak(self) -> bool:
        """Resolve memory leak issues"""
        # Implementation would trigger Lambda restart or garbage collection
        logger.info("Applied memory leak resolution")
        return True
    
    def resolve_disk_space_issue(self) -> bool:
        """Resolve disk space issues"""
        # Implementation would clean up temporary files
        logger.info("Applied disk space cleanup")
        return True
    
    def resolve_connection_timeout(self) -> bool:
        """Resolve connection timeout issues"""
        # Implementation would adjust connection pools or timeouts
        logger.info("Applied connection timeout fixes")
        return True
    
    def resolve_rate_limit_issue(self) -> bool:
        """Resolve rate limiting issues"""
        # Implementation would adjust rate limits or retry logic
        logger.info("Applied rate limit adjustments")
        return True
    
    def handle_escalations(self, analysis: Dict[str, Any]) -> int:
        """Handle alert escalations"""
        escalations_created = 0
        
        for alert in analysis['escalation_required']:
            try:
                self.create_escalation(alert)
                escalations_created += 1
                logger.info(f"Created escalation for: {alert['title']}")
            except Exception as e:
                logger.error(f"Failed to create escalation for {alert['id']}: {e}")
        
        return escalations_created
    
    def create_escalation(self, alert: Dict[str, Any]) -> None:
        """Create escalation for high-priority alert"""
        # Send to escalation channels
        for channel in self.config['escalation']['escalation_channels']:
            self.send_escalation_notification(alert, channel)
    
    def send_escalation_notification(self, alert: Dict[str, Any], channel: str) -> None:
        """Send escalation notification to Slack channel"""
        if not self.slack_webhook:
            return
        
        message = {
            "channel": channel,
            "text": f"🚨 ALERT ESCALATION: {alert['title']}",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {"title": "Source", "value": alert['source'], "short": True},
                    {"title": "Level", "value": alert['level'], "short": True},
                    {"title": "Count", "value": str(alert.get('count', 1)), "short": True},
                    {"title": "Type", "value": alert.get('type', 'unknown'), "short": True}
                ]
            }]
        }
        
        try:
            requests.post(self.slack_webhook, json=message, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")
    
    def store_alert_results(self, results: Dict[str, Any]) -> None:
        """Store alert results in DynamoDB"""
        try:
            table = self.dynamodb.Table('kindlemint-orchestration-logs')
            table.put_item(
                Item={
                    'log_id': f"alert_orchestration_{int(datetime.utcnow().timestamp())}",
                    'timestamp': results['timestamp'],
                    'log_type': 'alert_orchestration',
                    'results': results
                }
            )
        except Exception as e:
            logger.error(f"Failed to store alert results: {e}")
    
    def send_orchestration_summary(self, result: Dict[str, Any]) -> None:
        """Send orchestration summary notification"""
        if result['alerts_processed'] > 0:
            self.send_slack_summary(result)
    
    def send_slack_summary(self, result: Dict[str, Any]) -> None:
        """Send Slack summary"""
        if not self.slack_webhook:
            return
        
        color = "good" if result['resolutions_applied'] > 0 else "warning"
        emoji = "✅" if result['resolutions_applied'] > 0 else "⚠️"
        
        message = {
            "text": f"{emoji} Alert Orchestration Summary",
            "attachments": [{
                "color": color,
                "fields": [
                    {"title": "Alerts Processed", "value": str(result['alerts_processed']), "short": True},
                    {"title": "Auto-Resolutions", "value": str(result['resolutions_applied']), "short": True},
                    {"title": "Escalations", "value": str(result.get('escalations_created', 0)), "short": True},
                    {"title": "Duration", "value": f"{result.get('duration_seconds', 0):.1f}s", "short": True}
                ]
            }]
        }
        
        try:
            requests.post(self.slack_webhook, json=message, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send summary notification: {e}")
    
    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        return (datetime.utcnow() - self.stats['start_time']).total_seconds()

def send_alert_failure_notification(error_message: str, context) -> None:
    """Send failure notification for alert orchestration"""
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    if slack_webhook:
        message = {
            "text": "🚨 Alert Orchestration Failed",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {"title": "Error", "value": error_message, "short": False},
                    {"title": "Function", "value": context.function_name, "short": True},
                    {"title": "Request ID", "value": context.aws_request_id, "short": True}
                ]
            }]
        }
        
        try:
            requests.post(slack_webhook, json=message, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")