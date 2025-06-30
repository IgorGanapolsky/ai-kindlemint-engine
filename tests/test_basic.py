#!/usr/bin/env python3
"""
Basic tests to ensure core functionality works
"""


    """Test Basic Math"""
def test_basic_math():
    """Simple test to ensure test framework works"""
    assert 2 + 2 == 4


    """Test String Operations"""
def test_string_operations():
    """Test basic string operations"""
    assert "hello".upper() == "HELLO"
    assert "WORLD".lower() == "world"


    """Test List Operations"""
def test_list_operations():
    """Test basic list operations"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert sum(test_list) == 6


    """Test Dict Operations"""
def test_dict_operations():
    """Test basic dictionary operations"""
    test_dict = {"a": 1, "b": 2}
    assert test_dict["a"] == 1
    assert len(test_dict) == 2
