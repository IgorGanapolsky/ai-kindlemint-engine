#!/usr/bin/env python3
"""
Unit tests for test_bugbot.py module.
These tests verify the intentionally buggy functions work as expected for BugBot testing.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import io

# Import the module under test
from test_bugbot import (
    divide_numbers,
    process_user_input,
    fetch_data,
    insecure_password_check
)


class TestBugbotFunctions(unittest.TestCase):
    """Test suite for bugbot test functions"""

    def test_divide_numbers_normal_operation(self):
        """Test divide_numbers with normal inputs"""
        result = divide_numbers(10, 2)
        self.assertEqual(result, 5.0)
        
        result = divide_numbers(15, 3)
        self.assertEqual(result, 5.0)
        
        result = divide_numbers(7, 2)
        self.assertEqual(result, 3.5)

    def test_divide_numbers_zero_division_error(self):
        """Test that divide_numbers raises ZeroDivisionError with zero divisor"""
        with self.assertRaises(ZeroDivisionError):
            divide_numbers(10, 0)
        
        with self.assertRaises(ZeroDivisionError):
            divide_numbers(5, 0)

    def test_process_user_input_simple_expressions(self):
        """Test process_user_input with simple safe expressions"""
        result = process_user_input("2 + 2")
        self.assertEqual(result, 4)
        
        result = process_user_input("10 * 3")
        self.assertEqual(result, 30)
        
        result = process_user_input("'hello' + ' world'")
        self.assertEqual(result, "hello world")

    def test_process_user_input_dangerous_code(self):
        """Test that process_user_input can execute dangerous code (intentional bug)"""
        # This test demonstrates the security vulnerability
        result = process_user_input("__import__('os').getcwd()")
        # Should return current working directory, showing eval vulnerability
        self.assertIsInstance(result, str)

    @patch('test_bugbot.requests')
    def test_fetch_data_success(self, mock_requests):
        """Test fetch_data when request succeeds"""
        mock_response = MagicMock()
        mock_requests.get.return_value = mock_response
        
        # Should not raise an exception
        result = fetch_data()
        self.assertIsNone(result)  # Function doesn't return anything
        mock_requests.get.assert_called_once_with("https://api.example.com")

    @patch('test_bugbot.requests')
    def test_fetch_data_exception_handling(self, mock_requests):
        """Test fetch_data handles exceptions with bare except (intentional bug)"""
        mock_requests.get.side_effect = Exception("Network error")
        
        # Should not raise an exception due to bare except clause
        result = fetch_data()
        self.assertIsNone(result)  # Function should complete without error

    def test_insecure_password_check_correct_password(self):
        """Test insecure_password_check with hardcoded password"""
        result = insecure_password_check("admin123")
        self.assertTrue(result)

    def test_insecure_password_check_incorrect_password(self):
        """Test insecure_password_check with wrong passwords"""
        self.assertFalse(insecure_password_check("wrongpassword"))
        self.assertFalse(insecure_password_check("admin"))
        self.assertFalse(insecure_password_check("123"))
        self.assertFalse(insecure_password_check(""))
        self.assertFalse(insecure_password_check("Admin123"))  # Case sensitive


class TestBugbotMainExecution(unittest.TestCase):
    """Test the main execution block of test_bugbot.py"""

    @patch('builtins.print')
    def test_main_execution_with_division_by_zero(self, mock_print):
        """Test that main execution block handles division by zero"""
        # Import the module to trigger the main block
        with patch('test_bugbot.divide_numbers') as mock_divide:
            mock_divide.side_effect = ZeroDivisionError("division by zero")
            
            # Re-import to trigger __main__ block
            import importlib
            import test_bugbot
            
            # Verify the function was called with problematic values
            # Note: This test documents the intentional bug in the main block
            with self.assertRaises(ZeroDivisionError):
                divide_numbers(10, 0)


if __name__ == "__main__":
    unittest.main()
