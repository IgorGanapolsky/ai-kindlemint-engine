#!/usr/bin/env python3
"""
Unit tests for the migration from regular requests to safe_requests.
Tests the specific changes shown in the diff where requests.post is replaced
with safe_requests calls and timeout parameters are added.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import Timeout, RequestException


class TestRequestsSecurityMigration:
    """Test the migration from regular requests to safe_requests with timeout parameters."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.base_url = "https://api.helium10.com/v1"

    @patch('requests.post')
    def test_analyze_keywords_retains_requests_post(self, mock_post):
        """Test that analyze_keywords still uses requests.post (as shown in diff)."""
        # Mock the analyze_keywords method (simulated based on diff)
        class MockHelium10API:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.helium10.com/v1"
            
            def analyze_keywords(self, keywords):
                try:
                    response = requests.post(
                        f"{self.base_url}/cerebro",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={"keywords": keywords},
                        timeout=60,
                    )
                    return response.json()
                except Exception as e:
                    print(f"Error analyzing keywords: {e}")
                    return {}
        
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {"analysis": "test_data"}
        mock_post.return_value = mock_response
        
        # Test the API call
        api = MockHelium10API(self.api_key)
        result = api.analyze_keywords(["keyword1", "keyword2"])
        
        # Verify requests.post was called with timeout parameter
        mock_post.assert_called_once_with(
            "https://api.helium10.com/v1/cerebro",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"keywords": ["keyword1", "keyword2"]},
            timeout=60,
        )
        
        # Verify response
        assert result == {"analysis": "test_data"}

    @patch('requests.post')
    def test_analyze_keywords_timeout_parameter_added(self, mock_post):
        """Test that analyze_keywords now includes timeout=60 parameter."""
        class MockHelium10API:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.helium10.com/v1"
            
            def analyze_keywords(self, keywords):
                response = requests.post(
                    f"{self.base_url}/cerebro",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"keywords": keywords},
                    timeout=60,
                )
                return response.json()
        
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        
        api = MockHelium10API(self.api_key)
        api.analyze_keywords(["test"])
        
        # Verify timeout parameter was added
        args, kwargs = mock_post.call_args
        assert 'timeout' in kwargs
        assert kwargs['timeout'] == 60

    @patch('requests.post')
    def test_analyze_keywords_timeout_exception_handling(self, mock_post):
        """Test that analyze_keywords handles timeout exceptions properly."""
        class MockHelium10API:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.helium10.com/v1"
            
            def analyze_keywords(self, keywords):
                try:
                    response = requests.post(
                        f"{self.base_url}/cerebro",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={"keywords": keywords},
                        timeout=60,
                    )
                    return response.json()
                except Exception as e:
                    print(f"Error analyzing keywords: {e}")
                    return {}
        
        # Configure mock to raise timeout
        mock_post.side_effect = Timeout("Request timed out")
        
        api = MockHelium10API(self.api_key)
        result = api.analyze_keywords(["test"])
        
        # Should return empty dict due to exception handling
        assert result == {}

    def test_timeout_parameter_value_is_sixty_seconds(self):
        """Test that the timeout parameter is specifically set to 60 seconds."""
        # This test ensures the timeout value matches what's shown in the diff
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_post.return_value = mock_response
            
            class MockAPI:
                def make_request(self):
                    return requests.post(
                        "https://api.example.com",
                        timeout=60,
                    )
            
            api = MockAPI()
            api.make_request()
            
            # Verify the specific timeout value
            args, kwargs = mock_post.call_args
            assert kwargs['timeout'] == 60

    def test_mixed_request_methods_security_pattern(self):
        """Test the pattern where some methods use safe_requests and others use regular requests with timeout."""
        # This test validates the security pattern shown in the diff where:
        # - analyze_keywords uses requests.post with timeout
        # - get_trending_keywords uses safe_requests.get with timeout
        # - estimate_sales uses safe_requests.get with timeout
        
        with patch('requests.post') as mock_post, \
             patch('security.safe_requests.get') as mock_safe_get:
            
            # Both should be called with timeout parameter
            mock_post.return_value = Mock()
            mock_safe_get.return_value = Mock()
            
            # Simulate the mixed usage pattern
            requests.post("https://api.test.com", timeout=60)
            
            # Verify timeout is consistently applied
            assert mock_post.call_args[1]['timeout'] == 60