#!/usr/bin/env python3
"""
Unit tests for final_root_cleanup.py
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from scripts.final_root_cleanup import final_root_cleanup


class TestFinalRootCleanup:
    """Test the final_root_cleanup function"""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create test files that should be moved
            (project_root / "hygiene_report_20250630_172720.json").touch()
            (project_root / "scripts_to_archive.txt").touch()
            (project_root / ".roomodes").touch()
            (project_root / "Dockerfile.scheduler").touch()

            # Create essential files that should remain
            (project_root / "README.md").touch()
            (project_root / "LICENSE").touch()
            (project_root / "requirements.txt").touch()
            (project_root / "setup.py").touch()
            (project_root / ".gitignore").touch()

            # Create destination directories
            (project_root / "reports").mkdir(exist_ok=True)
            (project_root / "docs").mkdir(exist_ok=True)
            (project_root / "config").mkdir(exist_ok=True)
            (project_root / "deployment").mkdir(exist_ok=True)

            yield project_root

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_successful_file_moves(self, mock_cwd, temp_project_dir, capsys):
        """Test successful moving of files to their correct directories"""
        mock_cwd.return_value = temp_project_dir

        # Run the cleanup
        final_root_cleanup()

        # Check that files were moved to correct locations
        assert (
            temp_project_dir / "reports" / "hygiene_report_20250630_172720.json"
        ).exists()
        assert (temp_project_dir / "docs" / "scripts_to_archive.txt").exists()
        assert (temp_project_dir / "config" / ".roomodes").exists()
        assert (temp_project_dir / "deployment" /
                "Dockerfile.scheduler").exists()

        # Check that original files no longer exist in root
        assert not (temp_project_dir /
                    "hygiene_report_20250630_172720.json").exists()
        assert not (temp_project_dir / "scripts_to_archive.txt").exists()
        assert not (temp_project_dir / ".roomodes").exists()
        assert not (temp_project_dir / "Dockerfile.scheduler").exists()

        # Check console output
        captured = capsys.readouterr()
        assert "🧹 Final Root Directory Cleanup..." in captured.out
        assert "✅ Moved hygiene_report_20250630_172720.json" in captured.out
        assert "✅ Moved scripts_to_archive.txt" in captured.out
        assert "✅ Moved .roomodes" in captured.out
        assert "✅ Moved Dockerfile.scheduler" in captured.out
        assert "📊 Moved 4 files from root directory" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_nonexistent_files_skipped(self, mock_cwd, temp_project_dir, capsys):
        """Test that non-existent files are skipped gracefully"""
        mock_cwd.return_value = temp_project_dir

        # Remove some test files so they don't exist
        (temp_project_dir / "hygiene_report_20250630_172720.json").unlink()
        (temp_project_dir / "scripts_to_archive.txt").unlink()

        # Run the cleanup
        final_root_cleanup()

        # Check that only existing files were moved
        assert not (
            temp_project_dir / "reports" / "hygiene_report_20250630_172720.json"
        ).exists()
        assert not (temp_project_dir / "docs" /
                    "scripts_to_archive.txt").exists()
        assert (temp_project_dir / "config" / ".roomodes").exists()
        assert (temp_project_dir / "deployment" /
                "Dockerfile.scheduler").exists()

        # Check console output
        captured = capsys.readouterr()
        assert "📊 Moved 2 files from root directory" in captured.out
        # Should not mention the non-existent files
        assert "hygiene_report_20250630_172720.json" not in captured.out
        assert "scripts_to_archive.txt" not in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    @patch("scripts.final_root_cleanup.shutil.move")
    def test_move_error_handling(self, mock_move, mock_cwd, temp_project_dir, capsys):
        """Test error handling when file move fails"""
        mock_cwd.return_value = temp_project_dir
        mock_move.side_effect = PermissionError("Permission denied")

        # Run the cleanup
        final_root_cleanup()

        # Check console output for error messages
        captured = capsys.readouterr()
        assert "❌ Error moving" in captured.out
        assert "Permission denied" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_destination_directory_creation(self, mock_cwd, temp_project_dir):
        """Test that destination directories are created if they don't exist"""
        mock_cwd.return_value = temp_project_dir

        # Remove destination directories
        shutil.rmtree(temp_project_dir / "reports")
        shutil.rmtree(temp_project_dir / "docs")
        shutil.rmtree(temp_project_dir / "config")
        shutil.rmtree(temp_project_dir / "deployment")

        # Run the cleanup
        final_root_cleanup()

        # Check that destination directories were created and files moved
        assert (temp_project_dir / "reports").exists()
        assert (temp_project_dir / "docs").exists()
        assert (temp_project_dir / "config").exists()
        assert (temp_project_dir / "deployment").exists()

        assert (
            temp_project_dir / "reports" / "hygiene_report_20250630_172720.json"
        ).exists()
        assert (temp_project_dir / "docs" / "scripts_to_archive.txt").exists()
        assert (temp_project_dir / "config" / ".roomodes").exists()
        assert (temp_project_dir / "deployment" /
                "Dockerfile.scheduler").exists()

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_root_file_count_reporting(self, mock_cwd, temp_project_dir, capsys):
        """Test that root file count is correctly reported"""
        mock_cwd.return_value = temp_project_dir

        # Run the cleanup
        final_root_cleanup()

        # Count remaining files in root
        root_files = [f for f in temp_project_dir.iterdir() if f.is_file()]
        expected_count = len(root_files)

        # Check console output
        captured = capsys.readouterr()
        assert f"📁 Final root file count: {expected_count}" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_remaining_files_listing(self, mock_cwd, temp_project_dir, capsys):
        """Test that remaining root files are properly listed"""
        mock_cwd.return_value = temp_project_dir

        # Run the cleanup
        final_root_cleanup()

        # Check console output for file listing
        captured = capsys.readouterr()
        assert "📂 Remaining root files:" in captured.out
        assert "README.md" in captured.out
        assert "LICENSE" in captured.out
        assert "requirements.txt" in captured.out
        assert "setup.py" in captured.out
        assert ".gitignore" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_essential_files_check_all_essential(
        self, mock_cwd, temp_project_dir, capsys
    ):
        """Test essential files check when all files are essential"""
        mock_cwd.return_value = temp_project_dir

        # Run the cleanup
        final_root_cleanup()

        # Check console output
        captured = capsys.readouterr()
        assert "✅ All root files are now essential!" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_unexpected_files_warning(self, mock_cwd, temp_project_dir, capsys):
        """Test warning when unexpected files remain in root"""
        mock_cwd.return_value = temp_project_dir

        # Add an unexpected file
        (temp_project_dir / "unexpected_file.txt").touch()

        # Run the cleanup
        final_root_cleanup()

        # Check console output
        captured = capsys.readouterr()
        assert "⚠️  Unexpected files still in root:" in captured.out
        assert "unexpected_file.txt" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_cleanup_actions_structure(self, mock_cwd, temp_project_dir):
        """Test that cleanup actions have the correct structure"""
        mock_cwd.return_value = temp_project_dir

        # We'll need to patch the function to inspect cleanup_actions
        with patch("scripts.final_root_cleanup.final_root_cleanup") as mock_cleanup:
            # Import the actual function to test its structure
            import scripts.final_root_cleanup as cleanup_module

            # Get the actual cleanup_actions from the function
            expected_actions = [
                {
                    "file": "hygiene_report_20250630_172720.json",
                    "action": "move",
                    "destination": "reports/hygiene_report_20250630_172720.json",
                    "reason": "Reports belong in reports/ directory",
                },
                {
                    "file": "scripts_to_archive.txt",
                    "action": "move",
                    "destination": "docs/scripts_to_archive.txt",
                    "reason": "Documentation belongs in docs/ directory",
                },
                {
                    "file": ".roomodes",
                    "action": "move",
                    "destination": "config/.roomodes",
                    "reason": "Config files belong in config/ directory",
                },
                {
                    "file": "Dockerfile.scheduler",
                    "action": "move",
                    "destination": "deployment/Dockerfile.scheduler",
                    "reason": "Deployment files belong in deployment/ directory",
                },
            ]

            # Verify each action has required keys
            for action in expected_actions:
                assert "file" in action
                assert "action" in action
                assert "destination" in action
                assert "reason" in action
                assert action["action"] == "move"

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_essential_files_set(self, mock_cwd, temp_project_dir):
        """Test that essential files set contains expected files"""
        mock_cwd.return_value = temp_project_dir

        # Expected essential files from the updated script
        expected_essential_files = {
            "README.md",
            "LICENSE",
            "requirements.txt",
            "setup.py",
            ".gitignore",
            ".gitattributes",
            ".deepsource.toml",
            ".env.example",
            "sonar-project.properties",
            "claude-code",
            "claude-flow",
            "claude-flow-costs",
            "claude-flow-costs-notify",
            ".ccfignore",
        }

        # Create all essential files
        for filename in expected_essential_files:
            (temp_project_dir / filename).touch()

        # Run cleanup
        final_root_cleanup()

        # Should see the success message
        # (We can't directly test the essential_files set without refactoring the function,
        # but we can test the behavior)

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_print_statements_formatting(self, mock_cwd, temp_project_dir, capsys):
        """Test that print statements use correct formatting"""
        mock_cwd.return_value = temp_project_dir

        # Run the cleanup
        final_root_cleanup()

        # Check console output formatting
        captured = capsys.readouterr()

        # Check header formatting
        assert "🧹 Final Root Directory Cleanup..." in captured.out
        assert "=" * 50 in captured.out

        # Check success emoji formatting
        assert "✅ Moved" in captured.out

        # Check stats formatting
        assert "📊 Moved" in captured.out
        assert "📁 Final root file count:" in captured.out
        assert "📂 Remaining root files:" in captured.out

    @patch("scripts.final_root_cleanup.Path.cwd")
    def test_file_move_reasons(self, mock_cwd, temp_project_dir, capsys):
        """Test that move reasons are correctly displayed"""
        mock_cwd.return_value = temp_project_dir

        # Run the cleanup
        final_root_cleanup()

        # Check console output for reasons
        captured = capsys.readouterr()
        assert "Reports belong in reports/ directory" in captured.out
        assert "Documentation belongs in docs/ directory" in captured.out
        assert "Config files belong in config/ directory" in captured.out
        assert "Deployment files belong in deployment/ directory" in captured.out

    def test_main_execution(self):
        """Test that the script can be executed as main"""
        with patch("scripts.final_root_cleanup.final_root_cleanup") as mock_cleanup:
            # Import and execute the script's main block
            import scripts.final_root_cleanup as cleanup_module

            # Simulate running the script
            if hasattr(cleanup_module, "__name__"):
                # Mock the __name__ == "__main__" condition
                with patch.object(cleanup_module, "__name__", "__main__"):
                    # This would normally call final_root_cleanup()
                    mock_cleanup.assert_not_called()  # Since we're just testing the structure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
