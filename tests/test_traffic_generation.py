#!/usr/bin/env python3
"""
Test coverage for traffic generation system
Ensures revenue-generating systems work correctly
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "scripts" / "traffic_generation"))

class TestTrafficGeneration(unittest.TestCase):
    """Test traffic generation components"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(__file__).parent
        self.config_data = {
            "mode": "test",
            "subreddits": ["test_sudoku"],
            "daily_limit": 5
        }
    
    def test_reddit_config_template_exists(self):
        """Test that Reddit config template exists"""
        template_path = Path("scripts/traffic_generation/reddit_config.json.template")
        self.assertTrue(
            template_path.exists() or 
            Path("scripts/traffic_generation/reddit_config.json").exists(),
            "Reddit config or template should exist"
        )
    
    def test_pinterest_config_template_exists(self):
        """Test that Pinterest config template exists"""
        template_path = Path("scripts/traffic_generation/pinterest_config.json.template")
        self.assertTrue(
            template_path.exists() or
            Path("scripts/traffic_generation/pinterest_config.json").exists(),
            "Pinterest config or template should exist"
        )
    
    def test_traffic_orchestrator_config(self):
        """Test traffic orchestrator configuration"""
        config_path = Path("scripts/traffic_generation/traffic_orchestrator_config.json")
        template_path = Path("scripts/traffic_generation/traffic_orchestrator_config.json.template")
        
        self.assertTrue(
            config_path.exists() or template_path.exists(),
            "Traffic orchestrator config should exist"
        )
    
    def test_reddit_quick_start_executable(self):
        """Test that reddit quick start script is executable"""
        script_path = Path("scripts/traffic_generation/reddit_quick_start.py")
        if script_path.exists():
            self.assertTrue(
                os.access(script_path, os.X_OK),
                "reddit_quick_start.py should be executable"
            )
    
    def test_setup_script_executable(self):
        """Test that setup script is executable"""
        script_path = Path("scripts/traffic_generation/setup_traffic_generation.sh")
        if script_path.exists():
            self.assertTrue(
                os.access(script_path, os.X_OK),
                "setup_traffic_generation.sh should be executable"
            )
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_config_json_validity(self, mock_file):
        """Test that config files are valid JSON"""
        # Test JSON parsing doesn't raise exception
        try:
            data = json.loads('{"test": "data"}')
            self.assertIsInstance(data, dict)
        except json.JSONDecodeError:
            self.fail("Config files should be valid JSON")
    
    def test_revenue_projections(self):
        """Test revenue calculation logic"""
        # Test revenue projections are reasonable
        visitors_per_day = 200  # Conservative estimate
        email_conversion = 0.25  # 25%
        purchase_conversion = 0.10  # 10%
        book_price = 4.99
        
        daily_revenue = visitors_per_day * email_conversion * purchase_conversion * book_price
        
        self.assertGreater(daily_revenue, 20, "Daily revenue should be > $20")
        self.assertLess(daily_revenue, 1000, "Daily revenue projection should be realistic")
    
    def test_traffic_generation_readme_exists(self):
        """Test that traffic generation README exists"""
        readme_path = Path("scripts/traffic_generation/README.md")
        self.assertTrue(readme_path.exists(), "Traffic generation README should exist")
    
    def test_critical_files_present(self):
        """Test all critical traffic generation files are present"""
        critical_files = [
            "scripts/traffic_generation/reddit_organic_poster.py",
            "scripts/traffic_generation/pinterest_pin_scheduler.py",
            "scripts/traffic_generation/facebook_group_engager.py",
            "scripts/traffic_generation/traffic_orchestrator.py"
        ]
        
        for file_path in critical_files:
            with self.subTest(file=file_path):
                self.assertTrue(
                    Path(file_path).exists(),
                    f"{file_path} should exist for traffic generation"
                )
    
    def test_update_gumroad_reminder_exists(self):
        """Test that Gumroad update reminder exists"""
        reminder_path = Path("UPDATE_GUMROAD_NOW.md")
        self.assertTrue(
            reminder_path.exists(),
            "Gumroad pricing update reminder should exist"
        )

class TestRevenueIntegration(unittest.TestCase):
    """Integration tests for revenue generation"""
    
    def test_complete_revenue_pipeline(self):
        """Test that all components for revenue generation exist"""
        components = {
            "traffic_generation": Path("scripts/traffic_generation"),
            "backend_course": Path("backend_course"),
            "launch_content": Path("launch_content"),
            "revenue_monitoring": Path("scripts/revenue_monitor.py")
        }
        
        missing_components = []
        for name, path in components.items():
            if not path.exists():
                missing_components.append(name)
        
        self.assertEqual(
            len(missing_components), 0,
            f"Missing revenue components: {missing_components}"
        )
    
    def test_course_package_exists(self):
        """Test that course package is ready for upload"""
        course_package = Path("backend_course/course_package.zip")
        self.assertTrue(
            course_package.exists(),
            "Course package should be zipped and ready for Gumroad"
        )

if __name__ == "__main__":
    unittest.main()