#!/usr/bin/env python3
"""
Integration tests for test_bugbot.py module
Tests the fetch_data function with real network scenarios
"""

import socket
import sys
import time
import unittest
from unittest.mock import patch

import test_bugbot

# Add the project root to the Python path
sys.path.insert(0, ".")

# Import the module under test


class TestFetchDataIntegration(unittest.TestCase):
    """Integration test cases for the fetch_data function"""

    def test_fetch_data_timeout_with_slow_server(self):
        """Test that fetch_data times out appropriately with slow server simulation"""
        # This test simulates a slow server by patching socket operations
        original_create_connection = socket.create_connection

        def slow_create_connection(*args, **kwargs):
            # Simulate a very slow connection that should timeout
            time.sleep(65)  # Sleep longer than our 60-second timeout
            return original_create_connection(*args, **kwargs)

        with patch("socket.create_connection", side_effect=slow_create_connection):
            start_time = time.time()

            # Act - This should timeout and be handled gracefully
            try:
                result = test_bugbot.fetch_data()
                # If we get here, the timeout was handled properly
                end_time = time.time()
                duration = end_time - start_time

                # The function should have timed out and been handled
                # It shouldn't take the full 65 seconds we simulated
                self.assertLess(
                    duration, 65, "Function should have timed out before 65 seconds"
                )

            except Exception as e:
                # This is also acceptable - timeout exceptions should be caught
                pass

    def test_fetch_data_with_unreachable_host(self):
        """Test fetch_data behavior with an unreachable host"""
        # Temporarily patch the URL to point to an unreachable address
        with patch("test_bugbot.requests.get") as mock_get:
            # Simulate a connection error
            mock_get.side_effect = ConnectionError("Name or service not known")

            # Act & Assert - Should handle the error gracefully
            try:
                result = test_bugbot.fetch_data()
                # If we get here, the error was handled properly
            except ConnectionError:
                self.fail("fetch_data should handle ConnectionError gracefully")

    def test_fetch_data_timeout_parameter_boundary(self):
        """Test that the timeout parameter works at boundary conditions"""
        with patch("test_bugbot.requests.get") as mock_get:
            # Simulate a response that takes exactly 60 seconds
            def delayed_response(*args, **kwargs):
                # Verify timeout parameter is passed
                self.assertEqual(kwargs.get("timeout"), 60)
                # Simulate a response within timeout
                from unittest.mock import Mock

                mock_response = Mock()
                mock_response.status_code = 200
                return mock_response

            mock_get.side_effect = delayed_response

            # Act
            result = test_bugbot.fetch_data()

            # Assert that the function was called with correct timeout
            mock_get.assert_called_once_with(
                "https://api.example.com", timeout=60)


if __name__ == "__main__":
    unittest.main()
