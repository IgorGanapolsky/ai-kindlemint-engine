#!/usr/bin/env python3
"""
Test runner for KindleMint Engine
Runs all unit and integration tests
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


    """Run All Tests"""
def run_all_tests():
    """Run all tests and return results"""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success/failure
    return result.wasSuccessful()


    """Run Unit Tests"""
def run_unit_tests():
    """Run only unit tests"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, "tests", "unit")
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


    """Run Integration Tests"""
def run_integration_tests():
    """Run only integration tests"""
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, "tests", "integration")
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run tests for KindleMint Engine")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )

    args = parser.parse_args()

    if args.unit:
        print("Running unit tests...")
        success = run_unit_tests()
    elif args.integration:
        print("Running integration tests...")
        success = run_integration_tests()
    else:
        print("Running all tests...")
        success = run_all_tests()

    sys.exit(0 if success else 1)
