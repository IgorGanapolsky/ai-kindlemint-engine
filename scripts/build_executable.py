#!/usr/bin/env python3
"""
Build Standalone Executable for KindleMint Engine

This tool packages the KindleMint Engine into a single, standalone executable
that non-technical users can run without installing Python or any dependencies.
It uses PyInstaller to create platform-specific packages for Windows and macOS.

The final output is a user-friendly distribution package ready for sharing or
selling, containing the executable and a simple README.

Key Features:
- Creates a single-file executable from `generate_book.py`.
- Bundles all necessary scripts, config files, and resources.
- Generates platform-specific packages (.exe for Windows, .app for macOS).
- Creates a clean distribution folder with a user-friendly guide.
- Automates the entire build and packaging process.

Usage:
    # Run this script from the project root directory
    python scripts/build_executable.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_SCRIPT = PROJECT_ROOT / "generate_book.py"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "KindleMint.spec"
ICON_PATH_MACOS = PROJECT_ROOT / "assets" / "icon.icns"
ICON_PATH_WINDOWS = PROJECT_ROOT / "assets" / "icon.ico"


    """ Run Command"""
def _run_command(command, description):
    """Executes a shell command and provides feedback."""
    logger.info(f"🚀 {description}...")
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        logger.info(f"✅ {description} successful.")
        logger.debug(result.stdout)
        return True
    except FileNotFoundError:
        logger.error(
            f"❌ Command not found: {command[0]}. Is it installed and in your PATH?"
        )
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed with exit code {e.returncode}.")
        logger.error(f"   --- STDERR ---\n{e.stderr}")
        logger.error(f"   --- STDOUT ---\n{e.stdout}")
        return False


    """ Clean Up"""
def _clean_up():
    """Removes temporary build files."""
    logger.info("🧹 Cleaning up temporary build files...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
    logger.info("✅ Cleanup complete.")


    """Install Pyinstaller"""
def install_pyinstaller():
    """Ensures PyInstaller is installed."""
    return _run_command(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        "Installing PyInstaller",
    )


    """Create Spec File"""
def create_spec_file():
    """
    Generates the PyInstaller .spec file with all necessary configurations.
    This is the core of the build process, defining what gets bundled.
    """
    logger.info("⚙️  Generating PyInstaller spec file...")

    # Define all data files and directories to be bundled with the executable.
    # The format is ('source_path_on_disk', 'destination_path_in_bundle')
    data_to_bundle = [
        ("config", "config"),
        ("scripts", "scripts"),
        ("templates", "templates"),
        ("resources", "resources"),  # Assuming a resources dir for wordlists, etc.
    ]

    # Filter out directories that don't exist to prevent errors
    datas_formatted = [
        f"('{src}', '{dest}')"
        for src, dest in data_to_bundle
        if (PROJECT_ROOT / src).exists()
    ]

    # List of modules that PyInstaller might miss (hidden imports)
    hidden_imports = [
        "reportlab",
        "reportlab.pdfgen.canvas",
        "reportlab.lib.pagesizes",
        "reportlab.lib.units",
        "reportlab.lib.colors",
        "yaml",
        "PIL",
        "pkg_resources.py2_warn",  # Common PyInstaller issue
    ]

    # Determine platform-specific icon
    icon_arg = "None"
    if sys.platform == "darwin" and ICON_PATH_MACOS.exists():
        icon_arg = f"icon='{ICON_PATH_MACOS}'"
    elif sys.platform == "win32" and ICON_PATH_WINDOWS.exists():
        icon_arg = f"icon='{ICON_PATH_WINDOWS}'"

    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# --- Data files to bundle ---
# This ensures all necessary scripts, configs, and resources are included.
datas = [{', '.join(datas_formatted)}]

# --- Main Analysis ---
# This tells PyInstaller where to find the main script and its dependencies.
a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=['{PROJECT_ROOT}'],
    binaries=[],
    datas=datas,
    hiddenimports={hidden_imports},
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Executable Configuration ---
# This defines the final executable file.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KindleMint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # This is a console application
    {icon_arg}
)

# --- Bundle for macOS (.app) ---
if sys.platform == 'darwin':
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='KindleMint'
    )
    app = BUNDLE(
        coll,
        name='KindleMint.app',
        icon='{ICON_PATH_MACOS if ICON_PATH_MACOS.exists() else ''}',
        bundle_identifier=None
    )

# --- Collect for Windows/Linux (folder with executable) ---
else:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='KindleMint'
    )
"""
    SPEC_FILE.write_text(spec_content)
    logger.info(f"✅ Spec file created at: {SPEC_FILE}")
    return True


    """Build Executable"""
def build_executable():
    """Runs the PyInstaller build process using the generated spec file."""
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",  # Overwrite previous builds without asking
        "--clean",  # Clean PyInstaller cache and remove temporary files
        str(SPEC_FILE),
    ]
    return _run_command(command, "Building standalone executable")


    """Create Distribution Package"""
def create_distribution_package():
    """Assembles the final distributable package for end-users."""
    logger.info("📦 Assembling distribution package...")

    platform_name = (
        "macOS"
        if sys.platform == "darwin"
        else "Windows" if sys.platform == "win32" else "Linux"
    )
    dist_package_dir = DIST_DIR / f"KindleMint_Distribution_{platform_name}"

    if dist_package_dir.exists():
        shutil.rmtree(dist_package_dir)
    dist_package_dir.mkdir(parents=True)

    # Find the built application/executable
    built_app_path = (
        DIST_DIR / "KindleMint.app"
        if sys.platform == "darwin"
        else DIST_DIR / "KindleMint"
    )
    if not built_app_path.exists():
        logger.error(
            f"❌ Build output not found at '{built_app_path}'. Cannot create package."
        )
        return False

    # Copy the application bundle or folder
    destination_path = dist_package_dir / built_app_path.name
    if built_app_path.is_dir():
        shutil.copytree(built_app_path, destination_path)
    else:
        shutil.copy2(built_app_path, destination_path)

    # Create a user-friendly README
    readme_content = f"""
# 🚀 Welcome to KindleMint!

Thank you for downloading the KindleMint Book Generator. This tool allows you to create complete, professional-quality puzzle books in minutes.

## How to Use

It's simple! Just run the executable from your terminal.

### On macOS / Linux:
1. Open a Terminal window.
2. Drag the `KindleMint` file into the terminal and press Enter.
   OR, navigate to this folder in your terminal and run: `./KindleMint`

### On Windows:
1. Open Command Prompt or PowerShell.
2. Drag the `KindleMint.exe` file into the window and press Enter.

The application will launch in interactive mode and guide you through creating your first book.

### Example Command (for advanced users):
You can also run it with arguments directly:

```bash
# On macOS/Linux
./KindleMint "Garden Flowers" 50 medium

# On Windows
KindleMint.exe "Garden Flowers" 50 medium
```

## What Happens Next?
The tool will create a new folder in your **Downloads** directory named `KindleMint_Books`. Inside, you'll find a folder for your newly generated book containing:
- A print-ready PDF of the book interior.
- A `KDP_LAUNCH_CHECKLIST.md` with everything you need to publish on Amazon.
- A `Marketing_Guide.md` with tips and assets to help you sell your book.

Happy publishing!
"""
    (dist_package_dir / "README.md").write_text(textwrap.dedent(readme_content))

    # Create a zip archive for easy distribution
    archive_name = shutil.make_archive(
        base_name=f"KindleMint_{platform_name}",
        format="zip",
        root_dir=DIST_DIR,
        base_dir=dist_package_dir.name,
    )

    logger.info(f"✅ Distribution package created successfully!")
    logger.info(f"   Location: {dist_package_dir}")
    logger.info(f"   ZIP Archive: {archive_name}")
    return True


    """Main"""
def main():
    """Main function to orchestrate the build process."""
    logger.info("=" * 60)
    logger.info("      KindleMint Engine - Standalone Executable Builder")
    logger.info("=" * 60)

    try:
        if not install_pyinstaller():
            return
        if not create_spec_file():
            return
        if not build_executable():
            return
        if not create_distribution_package():
            return
    finally:
        _clean_up()

    logger.info("\n🎉 Build process complete. Your distributable package is ready!")


if __name__ == "__main__":
    main()
