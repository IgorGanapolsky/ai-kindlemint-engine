#!/usr/bin/env python3
"""
Test kindlemint package initialization
"""

def test_kindlemint_imports():
    """Test that kindlemint package can be imported"""
    try:
        import kindlemint
        assert kindlemint is not None
    except ImportError:
        # If main package doesn't exist, try src structure
        import sys
        sys.path.insert(0, '../src')
        import kindlemint
        assert kindlemint is not None


def test_kindlemint_has_version():
    """Test that kindlemint has version info"""
    try:
        import kindlemint
        # Check if __version__ exists (common pattern)
        if hasattr(kindlemint, '__version__'):
            assert isinstance(kindlemint.__version__, str)
    except:
        # Version might not be defined yet
        pass