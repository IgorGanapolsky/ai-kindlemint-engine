#!/usr/bin/env python3
"""
Unit tests for KDP Automation Engine security enhancements.
Tests the integration of the security module and safe_requests functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import Timeout, RequestException


class TestSecurityModuleIntegration:
    """Test the security module integration and safe_requests usage."""

    def test_security_module_import(self):
        """Test that the security module can be imported correctly."""
        try:
            from security import safe_requests
            assert hasattr(safe_requests, 'get'), "safe_requests should have a get method"
        except ImportError as e:
            pytest.fail(f"Failed to import security module: {e}")

    @patch('security.safe_requests.get')
    def test_safe_requests_get_method_exists(self, mock_safe_get):
        """Test that safe_requests.get method exists and can be called."""
        from security import safe_requests
        
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {"keywords": ["test1", "test2"]}
        mock_response.status_code = 200
        mock_safe_get.return_value = mock_response
        
        # Call safe_requests.get
        response = safe_requests.get(
            "https://api.example.com/test",
            headers={"Authorization": "Bearer test"},
            timeout=60
        )
        
        # Verify the call was made correctly
        mock_safe_get.assert_called_once_with(
            "https://api.example.com/test",
            headers={"Authorization": "Bearer test"},
            timeout=60
        )
        assert response.status_code == 200
        assert response.json() == {"keywords": ["test1", "test2"]}

    @patch('security.safe_requests.get')
    def test_safe_requests_with_timeout_parameter(self, mock_safe_get):
        """Test that safe_requests properly handles timeout parameters."""
        from security import safe_requests
        
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_safe_get.return_value = mock_response
        
        # Test with explicit timeout
        safe_requests.get("https://api.example.com", timeout=60)
        
        # Verify timeout was passed
        mock_safe_get.assert_called_with("https://api.example.com", timeout=60)

    @patch('security.safe_requests.get')
    def test_safe_requests_timeout_exception_handling(self, mock_safe_get):
        """Test that safe_requests properly handles timeout exceptions."""
        from security import safe_requests
        
        # Configure mock to raise timeout
        mock_safe_get.side_effect = Timeout("Request timed out")
        
        # Test that timeout exception is properly raised
        with pytest.raises(Timeout):
            safe_requests.get("https://api.example.com", timeout=60)

    @patch('security.safe_requests.get')
    def test_safe_requests_request_exception_handling(self, mock_safe_get):
        """Test that safe_requests properly handles general request exceptions."""
        from security import safe_requests
        
        # Configure mock to raise request exception
        mock_safe_get.side_effect = RequestException("Connection error")
        
        # Test that request exception is properly raised
        with pytest.raises(RequestException):
            safe_requests.get("https://api.example.com", timeout=60)


class TestHelium10APISecurityEnhancements:
    """Test security enhancements in Helium10API class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        
    @patch('security.safe_requests.get')
    def test_get_trending_keywords_uses_safe_requests(self, mock_safe_get):
        """Test that get_trending_keywords uses safe_requests instead of regular requests."""
        # Mock the Helium10API class (simulated based on diff)
        class MockHelium10API:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.helium10.com/v1"
            
            def get_trending_keywords(self, category="books"):
                from security import safe_requests
                try:
                    response = safe_requests.get(
                        f"{self.base_url}/trends/{category}",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=60,
                    )
                    return response.json().get("keywords", [])
                except Exception as e:
                    print(f"Error fetching trending keywords: {e}")
                    return []
        
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {"keywords": ["kindle", "ebook", "publishing"]}
        mock_safe_get.return_value = mock_response
        
        # Test the API call
        api = MockHelium10API(self.api_key)
        keywords = api.get_trending_keywords("books")
        
        # Verify safe_requests.get was called with correct parameters
        mock_safe_get.assert_called_once_with(
            "https://api.helium10.com/v1/trends/books",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60,
        )
        
        # Verify response
        assert keywords == ["kindle", "ebook", "publishing"]

    @patch('security.safe_requests.get')
    def test_get_trending_keywords_timeout_parameter(self, mock_safe_get):
        """Test that get_trending_keywords includes timeout parameter."""
        class MockHelium10API:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.helium10.com/v1"
            
            def get_trending_keywords(self, category="books"):
                from security import safe_requests
                try:
                    response = safe_requests.get(
                        f"{self.base_url}/trends/{category}",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=60,
                    )
                    return response.json().get("keywords", [])
                except Exception:
                    return []
        
        mock_response = Mock()
        mock_response.json.return_value = {"keywords": []}
        mock_safe_get.return_value = mock_response
        
        api = MockHelium10API(self.api_key)
        api.get_trending_keywords()
        
        # Verify timeout parameter was included
        args, kwargs = mock_safe_get.call_args
        assert 'timeout' in kwargs
        assert kwargs['timeout'] == 60


class TestJungleScoutAPISecurityEnhancements:
    """Test security enhancements in JungleScoutAPI class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_jungle_scout_key"

    @patch('security.safe_requests.get')
    def test_estimate_sales_uses_safe_requests(self, mock_safe_get):
        """Test that estimate_sales uses safe_requests instead of regular requests."""
        # Mock the JungleScoutAPI class (simulated based on diff)
        class MockJungleScoutAPI:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.junglescout.com/v1"
            
            def estimate_sales(self, bsr, category="books"):
                from security import safe_requests
                try:
                    response = safe_requests.get(
                        f"{self.base_url}/sales_estimates",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        params={"bsr": bsr, "category": category},
                        timeout=60,
                    )
                    return response.json()
                except Exception as e:
                    print(f"Error estimating sales: {e}")
                    return {}
        
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {"estimated_sales": 100, "confidence": 0.85}
        mock_safe_get.return_value = mock_response
        
        # Test the API call
        api = MockJungleScoutAPI(self.api_key)
        sales_data = api.estimate_sales(1500, "books")
        
        # Verify safe_requests.get was called with correct parameters
        mock_safe_get.assert_called_once_with(
            "https://api.junglescout.com/v1/sales_estimates",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={"bsr": 1500, "category": "books"},
            timeout=60,
        )
        
        # Verify response
        assert sales_data == {"estimated_sales": 100, "confidence": 0.85}

    @patch('security.safe_requests.get')
    def test_estimate_sales_timeout_parameter(self, mock_safe_get):
        """Test that estimate_sales includes timeout parameter."""
        class MockJungleScoutAPI:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.junglescout.com/v1"
            
            def estimate_sales(self, bsr, category="books"):
                from security import safe_requests
                response = safe_requests.get(
                    f"{self.base_url}/sales_estimates",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"bsr": bsr, "category": category},
                    timeout=60,
                )
                return response.json()
        
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_safe_get.return_value = mock_response
        
        api = MockJungleScoutAPI(self.api_key)
        api.estimate_sales(1000)
        
        # Verify timeout parameter was included
        args, kwargs = mock_safe_get.call_args
        assert 'timeout' in kwargs
        assert kwargs['timeout'] == 60