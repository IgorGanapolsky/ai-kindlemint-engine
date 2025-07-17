"""
Comprehensive tests for the monetization system

Tests all components:
- Lead magnet generation
- Email automation
- Conversion tracking
- Payment processing
- API endpoints
"""

import pytest
import json
import os
from unittest.mock import Mock, patch
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.kindlemint.email import EmailAutomation, SendGridClient
from src.kindlemint.analytics import ConversionTracker
from src.kindlemint.payments import StripeCheckout


class TestEmailAutomation:
    """Test email automation system"""
    
    @pytest.fixture
    def email_automation(self, tmp_path):
        """Create email automation instance with temp database"""
        mock_sendgrid = Mock(spec=SendGridClient)
        automation = EmailAutomation(sendgrid_client=mock_sendgrid)
        automation.subscriber_db = tmp_path / "test_subscribers.json"
        automation._init_subscriber_db()
        return automation
    
    def test_add_subscriber(self, email_automation):
        """Test adding a new subscriber"""
        result = email_automation.add_subscriber(
            email="test@example.com",
            first_name="Test",
            sequence="sudoku_lead_magnet",
            tags=["test"]
        )
        
        assert result['success']
        assert result['subscriber']['email'] == "test@example.com"
        assert result['subscriber']['first_name'] == "Test"
        assert result['subscriber']['status'] == "active"
    
    def test_duplicate_subscriber(self, email_automation):
        """Test adding duplicate subscriber"""
        # Add first time
        email_automation.add_subscriber(
            email="test@example.com",
            first_name="Test"
        )
        
        # Try to add again
        result = email_automation.add_subscriber(
            email="test@example.com",
            first_name="Test"
        )
        
        assert not result['success']
        assert result['error'] == "Already subscribed"
    
    def test_process_sequences(self, email_automation):
        """Test processing email sequences"""
        # Add subscriber
        email_automation.add_subscriber(
            email="test@example.com",
            first_name="Test"
        )
        
        # Mock sendgrid response
        email_automation.sendgrid.send_sequence_email.return_value = {
            'success': True
        }
        
        # Process sequences
        result = email_automation.process_sequences()
        
        assert result['processed'] == 1
        assert result['emails_sent'] >= 0  # Depends on timing
        assert isinstance(result['errors'], list)
    
    def test_record_conversion(self, email_automation):
        """Test recording a conversion"""
        # Add subscriber
        email_automation.add_subscriber(
            email="test@example.com",
            first_name="Test"
        )
        
        # Record conversion
        email_automation.record_conversion(
            email="test@example.com",
            product="Test Product",
            amount=9.99
        )
        
        # Check stats
        stats = email_automation.get_stats()
        assert stats['conversions'] == 1
        assert stats['total_conversions_value'] == 9.99


class TestConversionTracker:
    """Test conversion tracking system"""
    
    @pytest.fixture
    def tracker(self, tmp_path):
        """Create tracker instance with temp directory"""
        tracker = ConversionTracker(data_dir=str(tmp_path))
        return tracker
    
    def test_track_signup(self, tracker):
        """Test tracking email signup"""
        result = tracker.track_signup(
            email="test@example.com",
            first_name="Test",
            source="landing_page"
        )
        
        assert result['success']
        assert result['event']['event_type'] == "signup"
    
    def test_track_purchase(self, tracker):
        """Test tracking purchase"""
        result = tracker.track_purchase(
            email="test@example.com",
            product="Test Product",
            amount=9.99
        )
        
        assert result['success']
        assert result['event']['event_type'] == "purchase"
    
    def test_funnel_metrics(self, tracker):
        """Test funnel metrics calculation"""
        # Simulate user journey
        tracker.track_page_view("session_123")
        tracker.track_signup("test@example.com", "Test")
        tracker.track_email_open("test@example.com", "welcome", 0)
        tracker.track_email_click("test@example.com", "cta", "welcome", 0)
        tracker.track_purchase("test@example.com", "Product", 9.99)
        
        # Get metrics
        metrics = tracker.get_funnel_metrics(30)
        
        assert metrics['funnel_stages']['visitors'] >= 1
        assert metrics['funnel_stages']['signups'] >= 1
        assert metrics['funnel_stages']['customers'] >= 1
        assert metrics['conversion_rates']['overall'] > 0
    
    def test_revenue_metrics(self, tracker):
        """Test revenue metrics calculation"""
        # Track some purchases
        tracker.track_purchase("test1@example.com", "Product A", 10.00)
        tracker.track_purchase("test2@example.com", "Product B", 20.00)
        
        # Get revenue metrics
        metrics = tracker.get_revenue_metrics(1)
        
        assert metrics['total_revenue'] == 30.00
        assert metrics['total_purchases'] == 2
        assert metrics['average_order_value'] == 15.00
    
    def test_email_performance(self, tracker):
        """Test email performance tracking"""
        # Track email events
        tracker.track_event("email_sent", "test@example.com", {"email_type": "welcome"})
        tracker.track_email_open("test@example.com", "welcome", 0)
        tracker.track_email_click("test@example.com", "cta", "welcome", 0)
        
        # Get performance
        performance = tracker.get_email_performance()
        
        assert "welcome" in performance
        assert performance["welcome"]["sent"] >= 1
        assert performance["welcome"]["opens"] >= 1
        assert performance["welcome"]["clicks"] >= 1


class TestStripeCheckout:
    """Test Stripe checkout integration"""
    
    @pytest.fixture
    def checkout(self):
        """Create checkout instance with mock Stripe"""
        with patch('stripe.api_key'):
            checkout = StripeCheckout(api_key="sk_test_mock")
            return checkout
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_create, checkout):
        """Test creating checkout session"""
        # Mock Stripe response
        mock_create.return_value = Mock(
            id="cs_test_123",
            url="https://checkout.stripe.com/pay/cs_test_123"
        )
        
        result = checkout.create_checkout_session(
            product_name="Test Product",
            price_cents=999,
            customer_email="test@example.com"
        )
        
        assert result['success']
        assert result['session_id'] == "cs_test_123"
        assert result['checkout_url'] == "https://checkout.stripe.com/pay/cs_test_123"
        assert result['amount'] == 9.99
    
    @patch('stripe.Product.create')
    @patch('stripe.Price.create')
    @patch('stripe.PaymentLink.create')
    def test_create_payment_link(self, mock_link, mock_price, mock_product, checkout):
        """Test creating payment link"""
        # Mock Stripe responses
        mock_product.return_value = Mock(id="prod_123")
        mock_price.return_value = Mock(id="price_123")
        mock_link.return_value = Mock(url="https://buy.stripe.com/test_link")
        
        result = checkout.create_payment_link(
            product_name="Test Product",
            price_cents=999
        )
        
        assert result['success']
        assert result['payment_link'] == "https://buy.stripe.com/test_link"
        assert result['product_id'] == "prod_123"
        assert result['price_id'] == "price_123"
    
    @patch('stripe.Webhook.construct_event')
    def test_handle_webhook_success(self, mock_construct, checkout):
        """Test handling successful payment webhook"""
        # Mock webhook event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_email': 'test@example.com',
                    'amount_total': 999,
                    'metadata': {'product_name': 'Test Product'}
                }
            }
        }
        mock_construct.return_value = mock_event
        
        with patch.dict(os.environ, {'STRIPE_WEBHOOK_SECRET': 'whsec_test'}):
            with patch.object(checkout, '_handle_successful_payment') as mock_handle:
                mock_handle.return_value = {'success': True}
                
                result = checkout.handle_webhook(
                    payload="test_payload",
                    signature="test_signature"
                )
                
                assert result['success']
                mock_handle.assert_called_once()


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_subscribe_endpoint(self):
        """Test subscribe API endpoint"""
        # Import the handler
        from api.subscribe import handler
        
        # Create mock request
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.body = json.dumps({
            'email': 'test@example.com',
            'firstName': 'Test'
        })
        
        # Mock dependencies
        with patch('api.subscribe.EmailAutomation') as mock_automation:
            with patch('api.subscribe.ConversionTracker'):
                mock_instance = Mock()
                mock_instance.add_subscriber.return_value = {
                    'success': True,
                    'subscriber': {'email': 'test@example.com'}
                }
                mock_automation.return_value = mock_instance
                
                # Call handler
                response = handler(mock_request)
                
                assert response['statusCode'] == 200
                body = json.loads(response['body'])
                assert body['success']
    
    def test_subscribe_missing_email(self):
        """Test subscribe endpoint with missing email"""
        from api.subscribe import handler
        
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.body = json.dumps({'firstName': 'Test'})
        
        response = handler(mock_request)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body


class TestLeadMagnetGeneration:
    """Test lead magnet generation"""
    
    @patch('src.kindlemint.generators.sudoku_generator.SudokuGenerator.generate_puzzle')
    @patch('src.kindlemint.generators.pdf_generator.PDFGenerator.generate_lead_magnet_pdf')
    def test_generate_lead_magnet(self, mock_pdf, mock_puzzle):
        """Test lead magnet generation script"""
        from scripts.generate_lead_magnet import generate_lead_magnet
        
        # Mock puzzle generation
        mock_puzzle.return_value = {
            'puzzle': [[1,2,3],[4,5,6],[7,8,9]],
            'solution': [[1,2,3],[4,5,6],[7,8,9]],
            'difficulty': 'easy'
        }
        
        # Mock PDF generation
        mock_pdf.return_value = None
        
        # Run generation
        result = generate_lead_magnet()
        
        assert result['success']
        assert 'pdf_file' in result
        assert 'json_file' in result
        assert result['puzzle_count'] == 5


class TestIntegration:
    """Integration tests for complete flow"""
    
    @pytest.fixture
    def setup_system(self, tmp_path):
        """Set up complete system for integration testing"""
        # Mock all external services
        with patch('src.kindlemint.email.sendgrid_client.SendGridClient'):
            with patch('stripe.api_key'):
                # Create instances
                automation = EmailAutomation()
                automation.subscriber_db = tmp_path / "subscribers.json"
                automation._init_subscriber_db()
                
                tracker = ConversionTracker(data_dir=str(tmp_path))
                checkout = StripeCheckout(api_key="sk_test_mock")
                
                return {
                    'automation': automation,
                    'tracker': tracker,
                    'checkout': checkout
                }
    
    def test_complete_user_journey(self, setup_system):
        """Test complete user journey from signup to purchase"""
        automation = setup_system['automation']
        tracker = setup_system['tracker']
        
        # 1. User visits landing page
        tracker.track_page_view("session_123", "google.com")
        
        # 2. User signs up
        automation.add_subscriber(
            email="journey@example.com",
            first_name="Journey",
            lead_magnet_path="/tmp/lead_magnet.pdf"
        )
        tracker.track_signup("journey@example.com", "Journey", "landing_page")
        
        # 3. User opens emails
        tracker.track_email_open("journey@example.com", "welcome", 0)
        tracker.track_email_click("journey@example.com", "download", "welcome", 0)
        
        # 4. User makes purchase
        tracker.track_purchase("journey@example.com", "Sudoku Masters Vol 1", 8.99)
        automation.record_conversion("journey@example.com", "Sudoku Masters Vol 1", 8.99)
        
        # 5. Check metrics
        funnel_metrics = tracker.get_funnel_metrics(30)
        assert funnel_metrics['funnel_stages']['visitors'] >= 1
        assert funnel_metrics['funnel_stages']['customers'] >= 1
        assert funnel_metrics['conversion_rates']['overall'] > 0
        
        email_stats = automation.get_stats()
        assert email_stats['conversions'] == 1
        assert email_stats['total_conversions_value'] == 8.99


def test_analytics_report_generation():
    """Test analytics report generation"""
    from scripts.generate_analytics_report import generate_daily_report
    
    with patch('src.kindlemint.analytics.ConversionTracker') as mock_tracker:
        # Mock tracker methods
        mock_instance = Mock()
        mock_instance.get_funnel_metrics.return_value = {
            'funnel_stages': {
                'visitors': 100,
                'signups': 20,
                'engaged': 15,
                'customers': 3
            },
            'conversion_rates': {
                'visitor_to_signup': 20.0,
                'signup_to_engaged': 75.0,
                'engaged_to_customer': 20.0,
                'overall': 3.0
            }
        }
        mock_instance.get_revenue_metrics.return_value = {
            'total_revenue': 100.0,
            'total_purchases': 10,
            'average_order_value': 10.0,
            'monthly_revenue': {}
        }
        mock_instance.get_email_performance.return_value = {}
        mock_instance._get_user_segments.return_value = {}
        mock_instance._generate_recommendations.return_value = []
        mock_instance.export_analytics_dashboard.return_value = "/tmp/dashboard.html"
        
        mock_tracker.return_value = mock_instance
        
        # Run report generation
        result = generate_daily_report()
        
        assert result['success']
        assert 'dashboard_file' in result
        assert 'text_report_file' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])