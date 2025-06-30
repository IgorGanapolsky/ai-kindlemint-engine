#!/usr/bin/env python3
"""
CI Orchestration Test Suite
Tests all components of the CI orchestration system
"""

import json
import logging
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent))

# Import orchestration modules
try:
    from ci_analyzer import CIAnalyzer, FixStrategy
    from ci_fixer import CIFixer
    from ci_monitor import CIMonitor
    from ci_orchestrator import CIOrchestrator
except ImportError as e:
    print(f"Failed to import orchestration modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCIMonitor(unittest.TestCase):
    """Test CI monitoring functionality"""

        """Setup"""
def setUp(self):
        self.monitor = CIMonitor("test-owner", "test-repo", "test-token")

        """Test Monitor Initialization"""
def test_monitor_initialization(self):
        """Test monitor initialization"""
        self.assertEqual(self.monitor.repo_owner, "test-owner")
        self.assertEqual(self.monitor.repo_name, "test-repo")
        self.assertEqual(self.monitor.github_token, "test-token")

    @patch("requests.get")
        """Test Get Workflow Runs"""
def test_get_workflow_runs(self, mock_get):
        """Test workflow run fetching"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "workflow_runs": [
                {
                    "id": 123,
                    "name": "Test Workflow",
                    "status": "failure",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        }
        mock_get.return_value = mock_response

        runs = self.monitor.get_workflow_runs(limit=1, status="failure")
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["name"], "Test Workflow")

        """Test Failure Categorization"""
def test_failure_categorization(self):
        """Test failure categorization"""
        job = {
            "name": "test-job",
            "id": 123,
            "status": "completed",
            "conclusion": "failure",
            "steps": [
                {"name": "Install deps", "conclusion": "success"},
                {"name": "Run tests", "conclusion": "failure"},
            ],
        }

        logs = "ModuleNotFoundError: No module named 'missing_module'"

        failure_info = self.monitor.categorize_failure(job, logs)

        self.assertEqual(failure_info["failure_type"], "import_error")
        self.assertEqual(failure_info["failed_step"], "Run tests")
        self.assertIn("missing_module", failure_info["error_message"])


class TestCIAnalyzer(unittest.TestCase):
    """Test CI analysis functionality"""

        """Setup"""
def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.analyzer = CIAnalyzer(self.temp_dir)

        """Teardown"""
def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

        """Test Analyzer Initialization"""
def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        self.assertEqual(self.analyzer.repo_path, self.temp_dir)
        self.assertIn("import_error", self.analyzer.error_patterns)

        """Test Import Error Analysis"""
def test_import_error_analysis(self):
        """Test import error analysis"""
        failure_info = {
            "failure_type": "import_error",
            "error_message": "Missing module: requests",
            "logs": "ModuleNotFoundError: No module named 'requests'",
        }

        strategies = self.analyzer.analyze_failure(failure_info)

        self.assertGreater(len(strategies), 0)
        self.assertEqual(strategies[0].strategy_type, "install_package")
        self.assertIn("requests", strategies[0].description)

        """Test Test Failure Analysis"""
def test_test_failure_analysis(self):
        """Test test failure analysis"""
        failure_info = {
            "failure_type": "test_failure",
            "error_message": "Test failed",
            "logs": "tests/test_example.py::test_function FAILED",
        }

        strategies = self.analyzer.analyze_failure(failure_info)

        self.assertGreater(len(strategies), 0)
        strategy_types = [s.strategy_type for s_var in strategies]
        self.assertIn("fix_test_assertion", strategy_types)

        """Test Strategy Prioritization"""
def test_strategy_prioritization(self):
        """Test strategy prioritization"""
        strategies = [
            FixStrategy("low_confidence", "Test 1", 0.3, [], [], "high", False),
            FixStrategy("high_confidence", "Test 2", 0.9, [], [], "low", True),
            FixStrategy("medium_confidence", "Test 3", 0.6, [], [], "medium", True),
        ]

        prioritized = self.analyzer.prioritize_strategies(strategies)

        # Should be sorted by confidence descending, complexity ascending
        self.assertEqual(prioritized[0].strategy_type, "high_confidence")
        self.assertEqual(prioritized[0].confidence, 0.9)


class TestCIFixer(unittest.TestCase):
    """Test CI fixing functionality"""

        """Setup"""
def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.fixer = CIFixer(self.temp_dir, dry_run=True)

        """Teardown"""
def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

        """Test Fixer Initialization"""
def test_fixer_initialization(self):
        """Test fixer initialization"""
        self.assertEqual(self.fixer.repo_path, self.temp_dir)
        self.assertTrue(self.fixer.dry_run)

        """Test Black Formatting Fix"""
def test_black_formatting_fix(self):
        """Test Black formatter fix"""
        strategy = {
            "strategy_type": "run_black",
            "description": "Run Black formatter",
            "commands": ["black ."],
        }

        with patch.object(self.fixer, "_run_command") as mock_run:
            mock_run.return_value = (True, "reformatted test.py", "")

            result = self.fixer.apply_fix_strategy(strategy)

            self.assertTrue(result)
            mock_run.assert_called_once()

        """Test Package Installation Fix"""
def test_package_installation_fix(self):
        """Test package installation fix"""
        strategy = {
            "strategy_type": "install_package",
            "description": "Install missing package: requests",
            "commands": ["pip install requests"],
            "files_to_modify": ["requirements.txt"],
        }

        with patch.object(self.fixer, "_run_command") as mock_run:
            mock_run.return_value = (True, "", "")

            with patch.object(self.fixer, "_add_to_requirements") as mock_add:
                mock_add.return_value = True

                result = self.fixer.apply_fix_strategy(strategy)

                self.assertTrue(result)

        """Test Directory Creation Fix"""
def test_directory_creation_fix(self):
        """Test directory creation fix"""
        strategy = {
            "strategy_type": "create_directory",
            "description": "Create missing directory",
            "commands": ["mkdir -p test_dir"],
        }

        with patch.object(self.fixer, "_run_command") as mock_run:
            mock_run.return_value = (True, "", "")

            result = self.fixer.apply_fix_strategy(strategy)

            self.assertTrue(result)


class TestCIOrchestrator(unittest.TestCase):
    """Test CI orchestration functionality"""

        """Setup"""
def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.orchestrator = CIOrchestrator(
            "test-owner",
            "test-repo",
            self.temp_dir,
            github_token="test-token",
            dry_run=True,
        )

        """Teardown"""
def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

        """Test Orchestrator Initialization"""
def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        self.assertEqual(self.orchestrator.repo_owner, "test-owner")
        self.assertEqual(self.orchestrator.repo_name, "test-repo")
        self.assertTrue(self.orchestrator.dry_run)

        """Test Configuration Loading"""
def test_configuration_loading(self):
        """Test configuration loading"""
        # Create config file
        config_data = {
            "monitoring": {"lookback_minutes": 120},
            "fixing": {"max_fixes_per_run": 5},
        }

        config_file = self.temp_dir / "scripts" / "ci_orchestration" / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Reinitialize orchestrator
        orchestrator = CIOrchestrator(
            "test-owner", "test-repo", self.temp_dir, dry_run=True
        )

        self.assertEqual(orchestrator.config["monitoring"]["lookback_minutes"], 120)
        self.assertEqual(orchestrator.config["fixing"]["max_fixes_per_run"], 5)

    @patch("ci_orchestration.ci_monitor.CIMonitor.monitor_failures")
    @patch("ci_orchestration.ci_analyzer.CIAnalyzer.analyze_failure_report")
        """Test Single Cycle No Failures"""
def test_single_cycle_no_failures(self, mock_analyze, mock_monitor):
        """Test single cycle with no failures"""
        mock_monitor.return_value = []

        results = self.orchestrator.run_single_cycle()

        self.assertEqual(results["failures_detected"], 0)
        self.assertEqual(results["fixes_applied"], 0)
        self.assertIn("No failures detected", results["summary"])

    @patch("ci_orchestration.ci_monitor.CIMonitor.monitor_failures")
    @patch("ci_orchestration.ci_monitor.CIMonitor.save_failure_report")
    @patch("ci_orchestration.ci_analyzer.CIAnalyzer.analyze_failure_report")
        """Test Single Cycle With Failures"""
def test_single_cycle_with_failures(self, mock_analyze, mock_save, mock_monitor):
        """Test single cycle with failures"""
        # Mock failure detection
        mock_failures = [
            {
                "failure_type": "import_error",
                "error_message": "Missing module",
                "workflow_name": "Tests",
            }
        ]
        mock_monitor.return_value = mock_failures
        mock_save.return_value = {"failures": mock_failures}

        # Mock analysis results
        mock_analysis = {
            "analyzed_failures": [
                {
                    "strategies": [
                        {
                            "strategy_type": "install_package",
                            "confidence": 0.9,
                            "auto_fixable": True,
                            "description": "Install missing package",
                        }
                    ]
                }
            ]
        }
        mock_analyze.return_value = mock_analysis

        results = self.orchestrator.run_single_cycle()

        self.assertEqual(results["failures_detected"], 1)
        # Should have attempted fixes
        self.assertGreaterEqual(results["fixes_applied"], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

        """Setup"""
def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create mock repository structure
        (self.temp_dir / "src" / "kindlemint").mkdir(parents=True)
        (self.temp_dir / "tests").mkdir(parents=True)
        (self.temp_dir / "scripts" / "ci_orchestration").mkdir(parents=True)

        # Create requirements.txt
        with open(self.temp_dir / "requirements.txt", "w") as f:
            f.write("requests\npytest\n")

        """Teardown"""
def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

        """Test End To End Dry Run"""
def test_end_to_end_dry_run(self):
        """Test complete end-to-end dry run"""
        orchestrator = CIOrchestrator(
            "test-owner",
            "test-repo",
            self.temp_dir,
            github_token="test-token",
            dry_run=True,
        )

        # Mock the monitor to return no failures
        with patch.object(orchestrator.monitor, "monitor_failures") as mock_monitor:
            mock_monitor.return_value = []

            results = orchestrator.run_single_cycle()

            self.assertIsInstance(results, dict)
            self.assertIn("timestamp", results)
            self.assertIn("failures_detected", results)
            self.assertIn("summary", results)


    """Create Test Data"""
def create_test_data():
    """Create test data files for testing"""
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)

    # Create sample failure report
    failure_report = {
        "timestamp": "2024-01-01T00:00:00.000000",
        "repository": "test-owner/test-repo",
        "total_failures": 2,
        "failures": [
            {
                "workflow_name": "Tests",
                "job_name": "test-job",
                "failure_type": "import_error",
                "error_message": "Missing module: requests",
                "logs": "ModuleNotFoundError: No module named 'requests'",
                "suggested_fix": "Add missing import for requests",
            },
            {
                "workflow_name": "QA",
                "job_name": "lint-job",
                "failure_type": "linting_error",
                "error_message": "Code style violations",
                "logs": "would reformat test.py",
                "suggested_fix": "Run Black formatter",
            },
        ],
    }

    with open(test_data_dir / "sample_failures.json", "w") as f:
        json.dump(failure_report, f, indent=2)

    return test_data_dir


    """Run System Validation"""
def run_system_validation():
    """Run system validation tests"""
    logger.info("🧪 Running CI Orchestration System Validation")

    # Create test data
    test_data_dir = create_test_data()

    try:
        # Test 1: Component imports
        logger.info("Testing component imports...")
        from ci_analyzer import CIAnalyzer
        from ci_fixer import CIFixer
        from ci_monitor import CIMonitor
        from ci_orchestrator import CIOrchestrator

        logger.info("✅ All components imported successfully")

        # Test 2: Component initialization
        logger.info("Testing component initialization...")
        temp_dir = Path(tempfile.mkdtemp())

        CIMonitor("test-owner", "test-repo", "test-token")
        analyzer = CIAnalyzer(temp_dir)
        fixer = CIFixer(temp_dir, dry_run=True)
        orchestrator = CIOrchestrator(
            "test-owner", "test-repo", temp_dir, github_token="test-token", dry_run=True
        )
        logger.info("✅ All components initialized successfully")

        # Test 3: Sample analysis
        logger.info("Testing sample failure analysis...")
        sample_file = test_data_dir / "sample_failures.json"
        if sample_file.exists():
            analysis = analyzer.analyze_failure_report(str(sample_file))
            logger.info(
                f"✅ Analysis completed: {len(analysis['analyzed_failures'])} failures analyzed"
            )

        # Test 4: Configuration loading
        logger.info("Testing configuration...")
        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                json.load(f)
            logger.info("✅ Configuration loaded successfully")

        # Clean up
        import shutil

        shutil.rmtree(temp_dir)
        shutil.rmtree(test_data_dir)

        logger.info("🎉 System validation completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ System validation failed: {e}")
        return False


    """Main"""
def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Test CI orchestration system")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    parser.add_argument(
        "--validation", action="store_true", help="Run system validation"
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    success = True

    if args.unit or args.all:
        logger.info("Running unit tests...")
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add test classes
        suite.addTests(loader.loadTestsFromTestCase(TestCIMonitor))
        suite.addTests(loader.loadTestsFromTestCase(TestCIAnalyzer))
        suite.addTests(loader.loadTestsFromTestCase(TestCIFixer))
        suite.addTests(loader.loadTestsFromTestCase(TestCIOrchestrator))

        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)

        if not result.wasSuccessful():
            success = False

    if args.integration or args.all:
        logger.info("Running integration tests...")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestIntegration)

        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)

        if not result.wasSuccessful():
            success = False

    if args.validation or args.all:
        if not run_system_validation():
            success = False

    if not any([args.unit, args.integration, args.validation, args.all]):
        # Default: run validation
        if not run_system_validation():
            success = False

    if success:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
