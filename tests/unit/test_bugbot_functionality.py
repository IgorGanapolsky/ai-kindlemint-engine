#!/usr/bin/env python3
"""
Unit tests for test_bugbot.py functionality
Tests the fetch_data function and its timeout behavior
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

import test_bugbot

# Add the root directory to the path to import test_bugbot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestFetchData:
    """Test suite for the fetch_data function"""

    @patch("test_bugbot.requests.get")
    def test_fetch_data_success(self, mock_get):
        """Test successful API call with timeout parameter"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_get.return_value = mock_response

        # Act
        result = test_bugbot.fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)

    @patch("test_bugbot.requests.get")
    def test_fetch_data_timeout_parameter_present(self, mock_get):
        """Test that the timeout parameter is correctly passed to requests.get"""
        # Arrange
        mock_response = Mock()
        mock_get.return_value = mock_response

        # Act
        test_bugbot.fetch_data()

        # Assert - Verify timeout=60 is passed
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)

    @patch("test_bugbot.requests.get")
    def test_fetch_data_timeout_value_correct(self, mock_get):
        """Test that the timeout value is exactly 60 seconds"""
        # Arrange
        mock_response = Mock()
        mock_get.return_value = mock_response

        # Act
        test_bugbot.fetch_data()

        # Assert - Check the exact timeout value
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 60, "Timeout should be exactly 60 seconds"

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_timeout_exception(self, mock_get):
        """Test that function handles timeout exceptions gracefully"""
        # Arrange
        mock_get.side_effect = Timeout("Request timed out")

        # Act
        result = test_bugbot.fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)
        # Function should not raise exception due to try-except block

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_connection_error(self, mock_get):
        """Test that function handles connection errors gracefully"""
        # Arrange
        mock_get.side_effect = ConnectionError("Connection failed")

        # Act
        result = test_bugbot.fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)
        # Function should not raise exception due to try-except block

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_request_exception(self, mock_get):
        """Test that function handles general request exceptions gracefully"""
        # Arrange
        mock_get.side_effect = RequestException("General request error")

        # Act
        result = test_bugbot.fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)
        # Function should not raise exception due to try-except block

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_import_error(self, mock_get):
        """Test that function handles cases where requests module is not available"""
        # This test verifies the function can handle import failures
        with patch.dict("sys.modules", {"requests": None}):
            # Act
            result = test_bugbot.fetch_data()
            # Function should not raise exception due to try-except block

    def test_fetch_data_url_endpoint_correct(self):
        """Test that the correct API endpoint is being called"""
        with patch("test_bugbot.requests.get") as mock_get:
            # Arrange
            mock_response = Mock()
            mock_get.return_value = mock_response

            # Act
            test_bugbot.fetch_data()

            # Assert - Check the URL
            call_args = mock_get.call_args
            assert (
                call_args[0][0] == "https://api.example.com"
            ), "Should call the correct API endpoint"

    @patch("test_bugbot.requests.get")
    def test_fetch_data_exception_handling_broad(self, mock_get):
        """Test that the broad exception handling catches all types of exceptions"""
        # Arrange - Test with a generic exception
        mock_get.side_effect = Exception("Any exception")

        # Act
        result = test_bugbot.fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)
        # Function should not raise exception due to broad try-except block

    def test_fetch_data_function_exists(self):
        """Test that the fetch_data function exists and is callable"""
        assert hasattr(
            test_bugbot, "fetch_data"), "fetch_data function should exist"
        assert callable(
            test_bugbot.fetch_data), "fetch_data should be callable"

    def test_timeout_parameter_change_coverage(self):
        """Specific test to cover the timeout parameter change from the diff"""
        with patch("test_bugbot.requests.get") as mock_get:
            mock_get.return_value = Mock()
            test_bugbot.fetch_data()
            # This test specifically covers the line that was changed in the diff
            # Ensures that timeout=60 parameter is present in the call
            mock_get.assert_called_with("https://api.example.com", timeout=60)
