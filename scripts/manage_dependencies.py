#!/usr/bin/env python3
"""
Dependency management utility for KindleMint Engine
Helps maintain consistent and reproducible environments
"""

import subprocess
import sys
from pathlib import Path


def freeze_current_environment():
    """Freeze current environment to requirements-frozen.txt"""
    print("Freezing current environment...")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True
    )

    if result.returncode == 0:
        frozen_file = Path("requirements-frozen.txt")
        with open(frozen_file, "w") as f:
            f.write(
                "# Frozen requirements - "
                + subprocess.run(
                    ["date"], capture_output=True, text=True
                ).stdout.strip()
                + "\n"
            )
            f.write("# Python " + sys.version.split()[0] + "\n\n")
            f.write(result.stdout)

        print(f"✅ Environment frozen to {frozen_file}")
        return True
    else:
        print(f"❌ Error freezing environment: {result.stderr}")
        return False


def install_production_deps():
    """Install only production dependencies"""
    print("Installing production dependencies...")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-production.txt"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Production dependencies installed")
        return True
    else:
        print(f"❌ Error installing dependencies: {result.stderr}")
        return False


def install_all_deps():
    """Install all pinned dependencies"""
    print("Installing all pinned dependencies...")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-pinned.txt"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ All dependencies installed")
        return True
    else:
        print(f"❌ Error installing dependencies: {result.stderr}")
        return False


def check_dependency_versions():
    """Check installed versions against pinned requirements"""
    print("Checking dependency versions...")

    # Get installed packages
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Error getting installed packages")
        return

    import json

    installed = {
        pkg["name"].lower(): pkg["version"] for pkg in json.loads(result.stdout)
    }

    # Read pinned requirements
    pinned_file = Path("requirements-pinned.txt")
    if not pinned_file.exists():
        print("⚠️  No pinned requirements file found")
        return

    mismatches = []
    with open(pinned_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "==" in line:
                pkg_name, version = line.split("==")
                pkg_name = pkg_name.lower()

                if pkg_name in installed:
                    if installed[pkg_name] != version:
                        mismatches.append(
                            f"{pkg_name}: installed={installed[pkg_name]}, "
                            f"pinned={version}"
                        )

    if mismatches:
        print("⚠️  Version mismatches found:")
        for mismatch in mismatches:
            print(f"   - {mismatch}")
    else:
        print("✅ All installed versions match pinned requirements")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage dependencies for KindleMint Engine"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Freeze command
    freeze_parser = subparsers.add_parser(
        "freeze", help="Freeze current environment to requirements-frozen.txt"
    )

    # Install commands
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument(
        "--production", action="store_true", help="Install only production dependencies"
    )

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Check installed versions against pinned requirements"
    )

    args = parser.parse_args()

    if args.command == "freeze":
        freeze_current_environment()
    elif args.command == "install":
        if args.production:
            install_production_deps()
        else:
            install_all_deps()
    elif args.command == "check":
        check_dependency_versions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
