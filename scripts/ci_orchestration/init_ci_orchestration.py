#!/usr/bin/env python3
"""
CI Orchestration Initialization Script
Sets up the CI orchestration system with proper configuration and validation
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CIOrchestrationSetup:
    """Setup and initialization for CI orchestration system"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.orchestration_path = repo_path / "scripts" / "ci_orchestration"
        self.github_workflows_path = repo_path / ".github" / "workflows"

    def setup_complete_system(self) -> bool:
        """Set up the complete CI orchestration system"""
        logger.info("Starting CI orchestration system setup")

        setup_steps = [
            ("Validating repository structure", self._validate_repo_structure),
            ("Installing Python dependencies", self._install_dependencies),
            ("Configuring environment", self._setup_environment),
            ("Validating GitHub access", self._validate_github_access),
            ("Setting up configuration", self._setup_configuration),
            ("Creating log directories", self._setup_logging),
            ("Validating workflows", self._validate_workflows),
            ("Testing system components", self._test_system_components),
            ("Creating startup scripts", self._create_startup_scripts),
            ("Setting up monitoring", self._setup_monitoring),
        ]

        for step_name, step_func in setup_steps:
            logger.info(f"Step: {step_name}")
            try:
                if not step_func():
                    logger.error(f"Failed: {step_name}")
                    return False
                logger.info(f"✅ Completed: {step_name}")
            except Exception as e:
                logger.error(f"❌ Error in {step_name}: {e}")
                return False

        logger.info("🎉 CI orchestration system setup completed successfully!")
        self._print_usage_instructions()
        return True

    def _validate_repo_structure(self) -> bool:
        """Validate repository structure"""
        required_paths = [
            self.repo_path / "scripts",
            self.repo_path / ".github" / "workflows",
            self.repo_path / "src",
            self.repo_path / "tests",
        ]

        for path in required_paths:
            if not path.exists():
                logger.error(f"Required path missing: {path}")
                return False

        # Check for orchestration scripts
        orchestration_scripts = [
            "ci_monitor.py",
            "ci_analyzer.py",
            "ci_fixer.py",
            "ci_orchestrator.py",
        ]

        for script in orchestration_scripts:
            script_path = self.orchestration_path / script
            if not script_path.exists():
                logger.error(f"Required script missing: {script_path}")
                return False

        return True

    def _install_dependencies(self) -> bool:
        """Install required Python dependencies"""
        required_packages = [
            "requests",
            "PyGithub",
            "autopep8",
            "black",
            "isort",
            "flake8",
            "mypy",
            "pytest",
        ]

        for package in required_packages:
            if not self._is_package_installed(package):
                logger.info(f"Installing {package}...")
                if not self._install_package(package):
                    logger.error(f"Failed to install {package}")
                    return False

        return True

    def _setup_environment(self) -> bool:
        """Set up environment variables and configuration"""
        # Check for GitHub token
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            logger.warning("GITHUB_TOKEN not found in environment")
            logger.info("Please set GITHUB_TOKEN environment variable:")
            logger.info("export GITHUB_TOKEN='your_token_here'")

            # Try to read from .env file
            env_file = self.repo_path / ".env"
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("GITHUB_TOKEN="):
                            github_token = line.split("=", 1)[1].strip()
                            os.environ["GITHUB_TOKEN"] = github_token
                            logger.info("Found GITHUB_TOKEN in .env file")
                            break

        if not github_token:
            logger.error("GITHUB_TOKEN is required for CI orchestration")
            return False

        # Set up Python path
        python_path = os.environ.get("PYTHONPATH", "")
        repo_path_str = str(self.repo_path)
        if repo_path_str not in python_path:
            os.environ["PYTHONPATH"] = f"{python_path}:{repo_path_str}"

        return True

    def _validate_github_access(self) -> bool:
        """Validate GitHub API access"""
        try:
            import requests

            github_token = os.environ.get("GITHUB_TOKEN")
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # Test API access
            response = requests.get("https://api.github.com/user", headers=headers)
            if response.status_code != 200:
                logger.error(f"GitHub API access failed: {response.status_code}")
                return False

            user_data = response.json()
            logger.info(
                f"GitHub API access validated for user: {user_data.get('login')}"
            )

            # Test repository access
            repo_url = (
                "https://api.github.com/repos/igorganapolsky/ai-kindlemint-engine"
            )
            response = requests.get(repo_url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Repository access failed: {response.status_code}")
                return False

            logger.info("Repository access validated")
            return True

        except Exception as e:
            logger.error(f"GitHub validation failed: {e}")
            return False

    def _setup_configuration(self) -> bool:
        """Set up configuration files"""
        config_file = self.orchestration_path / "config.json"

        # Load existing config or create default
        if config_file.exists():
            logger.info("Configuration file already exists")
            return True

        default_config = {
            "monitoring": {
                "lookback_minutes": 60,
                "check_interval_seconds": 300,
                "max_failures_per_run": 20,
            },
            "analysis": {"confidence_threshold": 0.7, "max_strategies_per_failure": 3},
            "fixing": {
                "max_fixes_per_run": 5,
                "auto_fix_confidence_threshold": 0.8,
                "enable_auto_commit": False,
                "enable_auto_pr": False,
            },
            "notifications": {"slack_webhook": None, "email_recipients": []},
        }

        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)

        logger.info(f"Created default configuration: {config_file}")
        return True

    def _setup_logging(self) -> bool:
        """Set up logging directories and configuration"""
        log_dir = self.orchestration_path / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create log rotation configuration
        log_config = {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(log_dir / "ci_orchestration.log"),
                    "maxBytes": 10485760,
                    "backupCount": 5,
                    "formatter": "default",
                },
                "console": {"class": "logging.StreamHandler", "formatter": "default"},
            },
            "root": {"level": "INFO", "handlers": ["file", "console"]},
        }

        log_config_file = self.orchestration_path / "logging_config.json"
        with open(log_config_file, "w") as f:
            json.dump(log_config, f, indent=2)

        return True

    def _validate_workflows(self) -> bool:
        """Validate GitHub workflows"""
        autofixer_workflow = self.github_workflows_path / "ci_autofixer.yml"

        if not autofixer_workflow.exists():
            logger.error("CI autofixer workflow not found")
            return False

        # Validate workflow syntax (basic check)
        try:
            import yaml

            with open(autofixer_workflow, "r") as f:
                yaml.safe_load(f)
            logger.info("Workflow syntax is valid")
        except ImportError:
            logger.warning("PyYAML not installed - skipping workflow validation")
        except Exception as e:
            logger.error(f"Workflow validation failed: {e}")
            return False

        return True

    def _test_system_components(self) -> bool:
        """Test system components"""
        logger.info("Testing CI orchestration components...")

        # Test imports
        sys.path.append(str(self.orchestration_path))

        try:
            from ci_analyzer import CIAnalyzer
            from ci_fixer import CIFixer
            from ci_monitor import CIMonitor
            from ci_orchestrator import CIOrchestrator

            logger.info("✅ All components imported successfully")
        except ImportError as e:
            logger.error(f"Import failed: {e}")
            return False

        # Test component initialization
        try:
            monitor = CIMonitor("igorganapolsky", "ai-kindlemint-engine")
            analyzer = CIAnalyzer(self.repo_path)
            fixer = CIFixer(self.repo_path, dry_run=True)
            orchestrator = CIOrchestrator(
                "igorganapolsky", "ai-kindlemint-engine", self.repo_path, dry_run=True
            )

            logger.info("✅ All components initialized successfully")
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False

        # Test dry run
        try:
            results = orchestrator.run_single_cycle()
            logger.info(f"✅ Dry run completed: {results.get('summary', 'No summary')}")
        except Exception as e:
            logger.error(f"Dry run failed: {e}")
            return False

        return True

    def _create_startup_scripts(self) -> bool:
        """Create convenient startup scripts"""
        scripts = {
            "start_monitoring.sh": """#!/bin/bash
# Start CI orchestration monitoring
cd "$(dirname "$0")"
python ci_orchestrator.py --mode continuous --lookback-minutes 60
""",
            "run_analysis.sh": """#!/bin/bash
# Run single CI analysis
cd "$(dirname "$0")"
python ci_orchestrator.py --mode single --dry-run
""",
            "apply_fixes.sh": """#!/bin/bash
# Apply CI fixes with confirmation
cd "$(dirname "$0")"
echo "This will apply automatic fixes to CI failures."
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python ci_orchestrator.py --mode single --confidence-threshold 0.9
else
    echo "Cancelled."
fi
""",
        }

        for script_name, content in scripts.items():
            script_path = self.orchestration_path / script_name
            with open(script_path, "w") as f:
                f.write(content)
            script_path.chmod(0o755)  # Make executable

        logger.info("Created startup scripts")
        return True

    def _setup_monitoring(self) -> bool:
        """Set up system monitoring"""
        # Create systemd service file (if on Linux)
        if sys.platform.startswith("linux"):
            service_content = f"""[Unit]
Description=CI Orchestration Monitor
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.orchestration_path}
Environment=PYTHONPATH={self.repo_path}
Environment=GITHUB_TOKEN={os.environ.get('GITHUB_TOKEN', '')}
ExecStart=/usr/bin/python3 ci_orchestrator.py --mode continuous
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""

            service_file = self.orchestration_path / "ci-orchestration.service"
            with open(service_file, "w") as f:
                f.write(service_content)

            logger.info("Created systemd service file")
            logger.info(f"To install: sudo cp {service_file} /etc/systemd/system/")
            logger.info("Then: sudo systemctl enable ci-orchestration")

        # Create cron job suggestion
        cron_content = f"""# CI Orchestration - Run every 15 minutes
*/15 * * * * cd {self.orchestration_path} && /usr/bin/python3 ci_orchestrator.py --mode single --quiet
"""

        cron_file = self.orchestration_path / "ci-orchestration.cron"
        with open(cron_file, "w") as f:
            f.write(cron_content)

        logger.info("Created cron job template")
        logger.info(
            f"To install: crontab -l > /tmp/cron.bak && cat {cron_file} >> /tmp/cron.bak && crontab /tmp/cron.bak"
        )

        return True

    def _is_package_installed(self, package: str) -> bool:
        """Check if a Python package is installed"""
        try:
            __import__(package.replace("-", "_"))
            return True
        except ImportError:
            return False

    def _install_package(self, package: str) -> bool:
        """Install a Python package"""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _print_usage_instructions(self):
        """Print usage instructions"""
        print("\n" + "=" * 60)
        print("🎉 CI ORCHESTRATION SETUP COMPLETE!")
        print("=" * 60)
        print()
        print("📋 Quick Start Commands:")
        print()
        print("1. Run Analysis (Dry Run):")
        print(f"   cd {self.orchestration_path}")
        print("   python ci_orchestrator.py --mode single --dry-run")
        print()
        print("2. Apply Fixes:")
        print("   ./apply_fixes.sh")
        print()
        print("3. Start Continuous Monitoring:")
        print("   ./start_monitoring.sh")
        print()
        print("4. Check Configuration:")
        print("   cat config.json")
        print()
        print("📖 Documentation:")
        print(f"   {self.orchestration_path / 'README.md'}")
        print()
        print("🔧 Configuration Files:")
        print(f"   • Main config: {self.orchestration_path / 'config.json'}")
        print(f"   • Logging: {self.orchestration_path / 'logging_config.json'}")
        print(f"   • Workflows: {self.github_workflows_path / 'ci_autofixer.yml'}")
        print()
        print("🚀 GitHub Actions:")
        print("   The ci_autofixer.yml workflow will automatically:")
        print("   • Monitor for CI failures")
        print("   • Analyze and fix issues")
        print("   • Create commits/PRs when configured")
        print()
        print("⚠️  Important Notes:")
        print("   • Set GITHUB_TOKEN environment variable")
        print("   • Review config.json before enabling auto-commit")
        print("   • Test with --dry-run first")
        print("   • Monitor logs in logs/ directory")
        print()
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize CI orchestration system")
    parser.add_argument(
        "--repo-path", help="Repository path (defaults to current directory)"
    )
    parser.add_argument("--force", action="store_true", help="Force re-initialization")

    args = parser.parse_args()

    # Determine repository path
    repo_path = Path(args.repo_path) if args.repo_path else Path.cwd()

    # Check if we're in the right directory
    if not (repo_path / ".git").exists():
        logger.error("Not in a git repository. Please run from repository root.")
        sys.exit(1)

    # Initialize setup
    setup = CIOrchestrationSetup(repo_path)

    # Check if already initialized
    if (setup.orchestration_path / "config.json").exists() and not args.force:
        logger.info("CI orchestration system already initialized")
        logger.info("Use --force to re-initialize")
        sys.exit(0)

    # Run setup
    if setup.setup_complete_system():
        logger.info("Setup completed successfully!")
        sys.exit(0)
    else:
        logger.error("Setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
