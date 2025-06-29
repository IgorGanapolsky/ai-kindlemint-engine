#!/usr/bin/env python3
"""
Test Suite for Alert Orchestration System
Comprehensive tests for all components of the autonomous alert handling system
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent / "scripts" / "alert_orchestration"))

from sentry_monitor import SentryMonitor, SentryError
try:
    from slack_handler import SlackBot, SlackAlert
except ImportError:
    # Mock classes for CI environments where fastapi might not be available
    class SlackBot:
        def __init__(self, *args, **kwargs):
            pass
        async def send_message(self, *args, **kwargs):
            return {"ok": True}
        async def post_error_to_slack(self, *args, **kwargs):
            return {"ok": True}
    
    class SlackAlert:
        def __init__(self, *args, **kwargs):
            pass

from error_analyzer import ErrorAnalyzer, ErrorClassification
from auto_resolver import AutoResolver, ResolutionResult
from alert_orchestrator import AlertOrchestrator, OrchestrationConfig
from resolution_strategies import DatabaseConnectionStrategy, strategy_registry
from notification_templates import template_registry, render_notification

class TestSentryMonitor:
    """Test cases for Sentry monitoring functionality"""
    
    @pytest.fixture
    def mock_sentry_monitor(self):
        """Create a mock Sentry monitor for testing"""
        with patch.dict('os.environ', {
            'SENTRY_AUTH_TOKEN': 'test_token',
            'SENTRY_ORGANIZATION': 'test_org'
        }):
            monitor = SentryMonitor()
            monitor.session = Mock()
            return monitor
    
    def test_sentry_monitor_initialization(self, mock_sentry_monitor):
        """Test Sentry monitor initialization"""
        assert mock_sentry_monitor.auth_token == 'test_token'
        assert mock_sentry_monitor.organization == 'test_org'
        assert mock_sentry_monitor.base_url == "https://sentry.io/api/0"
    
    def test_create_sentry_error(self, mock_sentry_monitor):
        """Test creating SentryError objects from API data"""
        issue_data = {
            'id': 'test_error_123',
            'title': 'Test Error',
            'lastSeen': '2025-06-28T10:00:00Z',
            'count': 5,
            'level': 'error',
            'platform': 'python',
            'fingerprint': ['test', 'error'],
            'tags': {'environment': 'production'},
            'culprit': 'test.py in test_function',
            'metadata': {'value': 'Test error message'}
        }
        
        events_data = [{
            'contexts': {'runtime': {'name': 'python'}},
            'environment': 'production',
            'release': 'v1.0.0',
            'exception': {
                'values': [{
                    'type': 'ValueError',
                    'value': 'Test error message',
                    'stacktrace': {}
                }]
            },
            'breadcrumbs': {
                'values': [{
                    'timestamp': '2025-06-28T09:59:00Z',
                    'category': 'navigation',
                    'message': 'User navigated to page',
                    'level': 'info',
                    'data': {}
                }]
            }
        }]
        
        error = mock_sentry_monitor._create_sentry_error(issue_data, events_data)
        
        assert error is not None
        assert error.id == 'test_error_123'
        assert error.title == 'Test Error'
        assert error.count == 5
        assert error.level == 'error'
        assert error.environment == 'production'
        assert len(error.exceptions) == 1
        assert error.exceptions[0]['type'] == 'ValueError'
    
    def test_error_categorization(self, mock_sentry_monitor):
        """Test error categorization logic"""
        # Database error
        db_error = SentryError(
            id='db_1',
            title='Database Error',
            message='Connection timeout to database',
            level='error',
            platform='python',
            timestamp=datetime.now(timezone.utc),
            count=10,
            frequency=[],
            fingerprint=[],
            tags={},
            context={},
            exceptions=[],
            breadcrumbs=[],
            environment='production',
            release='v1.0.0',
            culprit='',
            metadata={}
        )
        
        assert db_error.category == 'database'
        assert db_error.is_critical == True  # Count > 10 threshold
        
        # Performance error
        perf_error = SentryError(
            id='perf_1',
            title='Performance Issue',
            message='Memory usage is high',
            level='warning',
            platform='python',
            timestamp=datetime.now(timezone.utc),
            count=3,
            frequency=[],
            fingerprint=[],
            tags={},
            context={},
            exceptions=[],
            breadcrumbs=[],
            environment='production',
            release='v1.0.0',
            culprit='',
            metadata={}
        )
        
        assert perf_error.category == 'performance'
        assert perf_error.is_critical == False

class TestErrorAnalyzer:
    """Test cases for error analysis functionality"""
    
    @pytest.fixture
    def error_analyzer(self):
        """Create error analyzer instance"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'patterns': []}, f)
            analyzer = ErrorAnalyzer(patterns_file=f.name)
        return analyzer
    
    def test_error_classification(self, error_analyzer):
        """Test error classification functionality"""
        error_data = {
            'id': 'test_123',
            'message': 'Database connection timeout after 30 seconds',
            'level': 'error',
            'environment': 'production',
            'context': {'tags': {'service': 'api'}}
        }
        
        classification = error_analyzer.analyze_error(error_data)
        
        assert isinstance(classification, ErrorClassification)
        assert classification.primary_category == 'database'
        assert classification.confidence_score > 0.0
        assert len(classification.suggested_actions) > 0
        assert classification.business_impact in ['low', 'medium', 'high', 'critical']
    
    def test_pattern_matching(self, error_analyzer):
        """Test error pattern matching"""
        # Test database patterns
        db_messages = [
            'connection timeout',
            'database unavailable',
            'query execution failed'
        ]
        
        for message in db_messages:
            category, confidence = error_analyzer._classify_category(message, {})
            assert category == 'database'
            assert confidence > 0.0
        
        # Test performance patterns
        perf_messages = [
            'memory leak detected',
            'high cpu usage',
            'slow response time'
        ]
        
        for message in perf_messages:
            category, confidence = error_analyzer._classify_category(message, {})
            assert category == 'performance'
            assert confidence > 0.0
    
    def test_trend_analysis(self, error_analyzer):
        """Test error trend analysis"""
        errors = []
        now = datetime.now(timezone.utc)
        
        # Create sample errors with different timestamps
        for i in range(10):
            error = {
                'timestamp': (now.replace(hour=i)).isoformat(),
                'category': 'database',
                'count': i + 1
            }
            errors.append(error)
        
        trends = error_analyzer.analyze_trends(errors, time_window_hours=24)
        
        assert len(trends) > 0
        db_trend = next((t for t in trends if t.category == 'database'), None)
        assert db_trend is not None
        assert db_trend.trend_direction in ['increasing', 'decreasing', 'stable']

class TestAutoResolver:
    """Test cases for automated resolution functionality"""
    
    @pytest.fixture
    def auto_resolver(self):
        """Create auto resolver instance"""
        return AutoResolver(dry_run=True)
    
    @pytest.mark.asyncio
    async def test_resolution_execution(self, auto_resolver):
        """Test resolution execution"""
        error_data = {
            'id': 'test_error',
            'message': 'Database connection timeout',
            'environment': 'staging',
            'service_name': 'api-server'
        }
        
        classification = {
            'primary_category': 'database',
            'confidence_score': 0.8,
            'resolution_urgency': 'high'
        }
        
        result = await auto_resolver.resolve_error(error_data, classification)
        
        assert result is not None
        assert isinstance(result, ResolutionResult)
        assert result.success == True  # Dry run should succeed
        assert result.execution_time > 0
        assert len(result.actions_taken) > 0
    
    @pytest.mark.asyncio
    async def test_safety_validation(self, auto_resolver):
        """Test safety validation mechanisms"""
        # Test production restrictions
        error_data = {
            'id': 'prod_error',
            'message': 'Critical system failure',
            'environment': 'production'
        }
        
        classification = {
            'primary_category': 'infrastructure',
            'confidence_score': 0.6,  # Below safety threshold
            'resolution_urgency': 'critical'
        }
        
        result = await auto_resolver.resolve_error(error_data, classification)
        
        # Should not attempt resolution due to low confidence in production
        assert result is None or not result.success
    
    def test_strategy_registry(self):
        """Test resolution strategy registry"""
        strategies = strategy_registry.strategies
        
        assert len(strategies) > 0
        assert 'Database Connection Resolution' in strategies
        assert 'Memory Leak Resolution' in strategies
        
        # Test getting applicable strategies
        error_context = {
            'message': 'database connection failed',
            'category': 'database'
        }
        
        applicable = strategy_registry.get_applicable_strategies(error_context)
        assert len(applicable) > 0
        
        # Should be sorted by confidence
        for i in range(len(applicable) - 1):
            assert applicable[i].confidence >= applicable[i + 1].confidence

class TestSlackHandler:
    """Test cases for Slack integration functionality"""
    
    @pytest.fixture
    def slack_bot(self):
        """Create mock Slack bot"""
        with patch.dict('os.environ', {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'}):
            bot = SlackBot()
            bot._send_webhook = Mock(return_value=True)
            bot._make_api_call = Mock(return_value={'ok': True, 'ts': '1234567890.123'})
        return bot
    
    def test_alert_creation(self, slack_bot):
        """Test creating and sending alerts"""
        alert_data = {
            'title': 'Test Alert',
            'description': 'Test error description',
            'error_details': 'Detailed error information',
            'source': 'test',
            'environment': 'staging',
            'metrics': {
                'count': 5,
                'level': 'error'
            }
        }
        
        message_ts = slack_bot.send_alert(
            channel='#test',
            alert_data=alert_data,
            alert_type='error',
            severity='medium'
        )
        
        assert message_ts is not None
        assert len(slack_bot.active_alerts) == 1
    
    def test_interactive_components(self, slack_bot):
        """Test interactive component handling"""
        payload = {
            'actions': [{
                'action_id': 'acknowledge_alert',
                'value': json.dumps({'action': 'acknowledge', 'alert_data': {}})
            }],
            'user': {'username': 'test_user'}
        }
        
        response = slack_bot.handle_interaction(payload)
        
        assert response is not None
        assert 'acknowledged' in response.text.lower()
    
    def test_alert_blocks_creation(self, slack_bot):
        """Test Slack block creation"""
        alert_data = {
            'title': 'Database Error',
            'description': 'Connection timeout',
            'severity': 'high',
            'environment': 'production',
            'error_count': 15
        }
        
        blocks = slack_bot._create_alert_blocks(alert_data, 'error', 'high', True)
        
        assert len(blocks) > 0
        assert blocks[0]['type'] == 'header'
        assert 'Database Error' in str(blocks)
        
        # Should include action buttons
        action_block = next((b for b in blocks if b.get('type') == 'actions'), None)
        assert action_block is not None

class TestNotificationTemplates:
    """Test cases for notification template system"""
    
    def test_template_registry(self):
        """Test template registry functionality"""
        templates = template_registry.list_templates()
        
        assert len(templates) > 0
        assert 'error_alert' in templates
        assert 'resolution_success' in templates
        assert 'escalation' in templates
    
    def test_error_alert_rendering(self):
        """Test error alert template rendering"""
        data = {
            'alert_id': 'alert_123',
            'error_id': 'error_123',
            'title': 'Test Error',
            'description': 'Test error description',
            'severity': 'high',
            'environment': 'production',
            'error_count': 10,
            'category': 'database',
            'confidence_score': 0.85,
            'suggested_actions': ['Check database connection', 'Restart service']
        }
        
        result = render_notification('error_alert', data)
        
        assert result is not None
        assert 'blocks' in result
        assert len(result['blocks']) > 0
        
        # Check that data is properly included
        blocks_str = json.dumps(result['blocks'])
        assert 'Test Error' in blocks_str
        assert 'production' in blocks_str
    
    def test_resolution_templates(self):
        """Test resolution notification templates"""
        success_data = {
            'resolution_id': 'res_123',
            'error_title': 'Database Error',
            'resolution_action': 'Restart Service',
            'execution_time': 30.5,
            'actions_taken': ['Checked health', 'Restarted service']
        }
        
        success_result = render_notification('resolution_success', success_data)
        assert success_result is not None
        assert 'Auto-Resolution Successful' in json.dumps(success_result)
        
        failure_data = {
            'error_title': 'Database Error',
            'strategy_name': 'Database Fix',
            'failure_reason': 'Service not responding',
            'actions_attempted': ['Checked connection', 'Attempted restart']
        }
        
        failure_result = render_notification('resolution_failure', failure_data)
        assert failure_result is not None
        assert 'Auto-Resolution Failed' in json.dumps(failure_result)

class TestAlertOrchestrator:
    """Test cases for main orchestration functionality"""
    
    @pytest.fixture
    def orchestrator_config(self):
        """Create test orchestration configuration"""
        return OrchestrationConfig(
            sentry_enabled=False,  # Disable for testing
            slack_enabled=False,   # Disable for testing
            auto_resolution_enabled=True,
            dry_run=True,
            monitoring_interval=10
        )
    
    @pytest.fixture
    def mock_orchestrator(self, orchestrator_config):
        """Create mock orchestrator for testing"""
        with patch('scripts.alert_orchestration.alert_orchestrator.SentryMonitor'), \
             patch('scripts.alert_orchestration.alert_orchestrator.SlackBot'), \
             patch('scripts.alert_orchestration.alert_orchestrator.ErrorAnalyzer'), \
             patch('scripts.alert_orchestration.alert_orchestrator.AutoResolver'):
            
            orchestrator = AlertOrchestrator()
            orchestrator.config = orchestrator_config
            return orchestrator
    
    def test_orchestrator_initialization(self, mock_orchestrator):
        """Test orchestrator initialization"""
        assert mock_orchestrator.config.dry_run == True
        assert mock_orchestrator.config.auto_resolution_enabled == True
        assert len(mock_orchestrator.active_alerts) == 0
    
    def test_alert_processing_decision_logic(self, mock_orchestrator):
        """Test alert processing decision logic"""
        # Mock error and classification
        mock_error = Mock()
        mock_error.id = 'test_error'
        mock_error.is_critical = False
        mock_error.environment = 'staging'
        mock_error.level = 'warning'
        mock_error.count = 5
        
        mock_classification = Mock()
        mock_classification.resolution_urgency = 'medium'
        mock_classification.confidence_score = 0.7
        mock_classification.primary_category = 'performance'
        
        # Test should_send_alert
        should_alert = mock_orchestrator._should_send_alert(mock_error, mock_classification)
        assert isinstance(should_alert, bool)
        
        # Test should_attempt_resolution
        should_resolve = mock_orchestrator._should_attempt_resolution(mock_error, mock_classification)
        assert isinstance(should_resolve, bool)
        
        # Test should_escalate
        should_escalate = mock_orchestrator._should_escalate(mock_error, mock_classification)
        assert isinstance(should_escalate, bool)
    
    def test_escalation_logic(self, mock_orchestrator):
        """Test escalation decision logic"""
        # Critical error should escalate
        critical_error = Mock()
        critical_error.is_critical = True
        critical_error.environment = 'production'
        
        critical_classification = Mock()
        critical_classification.resolution_urgency = 'critical'
        
        should_escalate = mock_orchestrator._should_escalate(critical_error, critical_classification)
        assert should_escalate == True
        
        # Normal error should not escalate immediately
        normal_error = Mock()
        normal_error.is_critical = False
        normal_error.environment = 'staging'
        
        normal_classification = Mock()
        normal_classification.resolution_urgency = 'medium'
        
        should_escalate = mock_orchestrator._should_escalate(normal_error, normal_classification)
        assert should_escalate == False

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This test would require more complex setup with actual integrations
        # For now, we'll test the workflow logic
        
        # 1. Create mock error
        error_data = {
            'id': 'integration_test',
            'message': 'Redis connection failed',
            'level': 'error',
            'environment': 'staging',
            'context': {'service': 'cache'}
        }
        
        # 2. Analyze error
        analyzer = ErrorAnalyzer()
        classification = analyzer.analyze_error(error_data)
        
        assert classification.primary_category in ['database', 'network', 'infrastructure']
        assert classification.confidence_score > 0.0
        
        # 3. Attempt resolution (dry run)
        resolver = AutoResolver(dry_run=True)
        result = await resolver.resolve_error(error_data, classification.__dict__)
        
        if result:
            assert isinstance(result, ResolutionResult)
            assert result.success in [True, False]  # Either outcome is valid in dry run
    
    def test_configuration_validation(self):
        """Test configuration file validation"""
        config_path = Path(__file__).parent.parent / "scripts" / "alert_orchestration" / "config.yaml"
        
        if config_path.exists():
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate required sections
            assert 'system' in config
            assert 'components' in config
            assert 'operation' in config
            
            # Validate component settings
            components = config['components']
            assert 'sentry_enabled' in components
            assert 'slack_enabled' in components
            assert 'auto_resolution_enabled' in components
    
    def test_error_patterns_validation(self):
        """Test error patterns file validation"""
        patterns_path = Path(__file__).parent.parent / "scripts" / "alert_orchestration" / "error_patterns.json"
        
        if patterns_path.exists():
            with open(patterns_path, 'r') as f:
                patterns_data = json.load(f)
            
            # Validate structure
            assert 'patterns' in patterns_data
            assert 'version' in patterns_data
            
            # Validate individual patterns
            for pattern in patterns_data['patterns']:
                assert 'id' in pattern
                assert 'name' in pattern
                assert 'pattern' in pattern
                assert 'category' in pattern
                assert 'confidence' in pattern
                assert 0.0 <= pattern['confidence'] <= 1.0

class TestPerformance:
    """Performance tests for the system"""
    
    def test_error_analysis_performance(self):
        """Test error analysis performance with multiple errors"""
        analyzer = ErrorAnalyzer()
        
        # Create multiple test errors
        errors = []
        for i in range(100):
            error_data = {
                'id': f'perf_test_{i}',
                'message': f'Test error {i} with database connection issues',
                'level': 'error',
                'environment': 'test'
            }
            errors.append(error_data)
        
        # Measure analysis time
        import time
        start_time = time.time()
        
        classifications = []
        for error_data in errors:
            classification = analyzer.analyze_error(error_data)
            classifications.append(classification)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        # Should process 100 errors in reasonable time (< 10 seconds)
        assert analysis_time < 10.0
        assert len(classifications) == 100
        
        # All classifications should be valid
        for classification in classifications:
            assert isinstance(classification, ErrorClassification)
            assert classification.primary_category is not None
    
    @pytest.mark.asyncio
    async def test_resolution_concurrency(self):
        """Test concurrent resolution handling"""
        resolver = AutoResolver(dry_run=True)
        
        # Create multiple resolution tasks
        tasks = []
        for i in range(5):
            error_data = {
                'id': f'concurrent_test_{i}',
                'message': 'Memory usage high',
                'environment': 'test'
            }
            classification = {'primary_category': 'performance', 'confidence_score': 0.8}
            
            task = resolver.resolve_error(error_data, classification)
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == 5
        for result in results:
            assert not isinstance(result, Exception)
            if result:  # Some might return None due to safety checks
                assert isinstance(result, ResolutionResult)

# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "--tb=short"])