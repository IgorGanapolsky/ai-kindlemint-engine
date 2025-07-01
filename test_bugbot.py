#!/usr/bin/env python3
"""
Unit tests for bugbot functionality.
Tests the fetch_data function with timeout parameter.
"""

import unittest
from unittest.mock import Mock, patch

import requests


def fetch_data():
    """Fetch data from API with timeout."""
    try:
        import requests

        response = requests.get("https://api.example.com", timeout=60)
    except:
        pass


class TestFetchData(unittest.TestCase):
    """Test cases for the fetch_data function."""

    @patch("requests.get")
    def test_fetch_data_with_timeout_parameter(self, mock_get):
        """Test that fetch_data calls requests.get with timeout=60."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        # Act
        fetch_data()

        # Assert
        mock_get.assert_called_once_with("https://api.example.com", timeout=60)

    @patch("requests.get")
    def test_fetch_data_handles_request_exception(self, mock_get):
        """Test that fetch_data handles exceptions gracefully."""
        # Arrange
        mock_get.side_effect = requests.RequestException("Connection error")

        # Act & Assert - should not raise exception
        try:
            fetch_data()
        except Exception as e:
            self.fail(
                f"fetch_data raised an exception when it should handle it: {e}")

    @patch("requests.get")
    def test_fetch_data_handles_timeout_exception(self, mock_get):
        """Test that fetch_data handles timeout exceptions gracefully."""
        # Arrange
        mock_get.side_effect = requests.Timeout("Request timed out")

        # Act & Assert - should not raise exception
        try:
            fetch_data()
        except Exception as e:
            self.fail(
                f"fetch_data raised an exception when it should handle it: {e}")

    @patch("requests.get")
    def test_fetch_data_handles_http_error(self, mock_get):
        """Test that fetch_data handles HTTP errors gracefully."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "500 Server Error"
        )
        mock_get.return_value = mock_response

        # Act & Assert - should not raise exception
        try:
            fetch_data()
        except Exception as e:
            self.fail(
                f"fetch_data raised an exception when it should handle it: {e}")

    @patch("requests.get")
    def test_fetch_data_uses_correct_url(self, mock_get):
        """Test that fetch_data uses the correct API URL."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act
        fetch_data()

        # Assert
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://api.example.com")
        self.assertEqual(kwargs.get("timeout"), 60)


if __name__ == "__main__":
    unittest.main()
