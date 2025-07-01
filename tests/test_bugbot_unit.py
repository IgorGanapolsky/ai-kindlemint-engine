#!/usr/bin/env python3
"""
Unit tests for test_bugbot.py module
Tests the fetch_data function with timeout parameter changes
"""

import sys
import unittest
from unittest.mock import Mock, patch

from requests.exceptions import ConnectTimeout, ReadTimeout, Timeout

import test_bugbot

# Add the project root to the Python path
sys.path.insert(0, ".")

# Import the module under test


class TestFetchData(unittest.TestCase):
    """Test cases for the fetch_data function"""

    @patch("test_bugbot.requests.get")
    def test_fetch_data_with_timeout_success(self, mock_get):
        """Test that fetch_data calls requests.get with timeout=60 on success"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        # Act
        result = test_bugbot.fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)

    @patch("test_bugbot.requests.get")
    def test_fetch_data_with_timeout_parameter_verification(self, mock_get):
        """Test that the timeout parameter is correctly passed as 60 seconds"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act
        test_bugbot.fetch_data()

        # Assert - Verify the exact call arguments
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://api.example.com")
        self.assertEqual(kwargs["timeout"], 60)

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_connect_timeout(self, mock_get):
        """Test that fetch_data handles ConnectTimeout exceptions gracefully"""
        # Arrange
        mock_get.side_effect = ConnectTimeout("Connection timed out")

        # Act & Assert - Should not raise exception
        try:
            result = test_bugbot.fetch_data()
            # If we get here, the exception was handled properly
        except ConnectTimeout:
            self.fail("fetch_data should handle ConnectTimeout exceptions")

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_read_timeout(self, mock_get):
        """Test that fetch_data handles ReadTimeout exceptions gracefully"""
        # Arrange
        mock_get.side_effect = ReadTimeout("Read timed out")

        # Act & Assert - Should not raise exception
        try:
            result = test_bugbot.fetch_data()
            # If we get here, the exception was handled properly
        except ReadTimeout:
            self.fail("fetch_data should handle ReadTimeout exceptions")

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_generic_timeout(self, mock_get):
        """Test that fetch_data handles generic Timeout exceptions gracefully"""
        # Arrange
        mock_get.side_effect = Timeout("Request timed out")

        # Act & Assert - Should not raise exception
        try:
            result = test_bugbot.fetch_data()
            # If we get here, the exception was handled properly
        except Timeout:
            self.fail("fetch_data should handle Timeout exceptions")

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_import_error(self, mock_get):
        """Test that fetch_data handles import errors gracefully"""
        # Arrange - Mock the import to fail
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named requests")
        ):
            # Act & Assert - Should not raise exception
            try:
                result = test_bugbot.fetch_data()
                # If we get here, the exception was handled properly
            except ImportError:
                self.fail("fetch_data should handle ImportError exceptions")

    @patch("test_bugbot.requests.get")
    def test_fetch_data_handles_http_errors(self, mock_get):
        """Test that fetch_data handles HTTP errors gracefully"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception(
            "HTTP 500 Error")
        mock_get.return_value = mock_response

        # Act & Assert - Should not raise exception
        try:
            result = test_bugbot.fetch_data()
            # If we get here, the exception was handled properly
        except Exception:
            self.fail("fetch_data should handle HTTP errors gracefully")

    @patch("test_bugbot.requests.get")
    def test_fetch_data_url_verification(self, mock_get):
        """Test that fetch_data calls the correct URL"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act
        test_bugbot.fetch_data()

        # Assert
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://api.example.com")

    @patch("test_bugbot.requests.get")
    def test_fetch_data_timeout_value_is_integer(self, mock_get):
        """Test that the timeout value is an integer (60)"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act
        test_bugbot.fetch_data()

        # Assert
        args, kwargs = mock_get.call_args
        self.assertIsInstance(kwargs["timeout"], int)
        self.assertEqual(kwargs["timeout"], 60)


if __name__ == "__main__":
    unittest.main()
