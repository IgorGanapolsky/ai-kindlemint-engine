#!/usr/bin/env python3
"""
Build Standalone Executable for KindleMint
Package the entire system into a single executable file for easy distribution.
"""

import sys
import subprocess
import os
from pathlib import Path
import shutil

def install_dependencies():
    """Install required packaging dependencies"""
    print("📦 Installing packaging dependencies...")
    
    dependencies = [
        "pyinstaller>=5.0",
        "nuitka>=1.5"  # Alternative packager
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {dep}")

def create_spec_file():
    """Create PyInstaller spec file for customization"""
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['generate_book.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('scripts/', 'scripts/'),
        ('config/', 'config/'),
        ('templates/', 'templates/'),
    ],
    hiddenimports=[
        'PIL',
        'reportlab',
        'pathlib',
        'datetime',
        'argparse',
        'subprocess',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KindleMint-BookGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('KindleMint.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file: KindleMint.spec")

def build_with_pyinstaller():
    """Build executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    try:
        # Create spec file
        create_spec_file()
        
        # Build using spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm", 
            "KindleMint.spec"
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller build completed!")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller build failed: {e.stderr}")
        return False

def build_with_nuitka():
    """Alternative build using Nuitka (often smaller executables)"""
    print("🔨 Building executable with Nuitka...")
    
    try:
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile",
            "--assume-yes-for-downloads",
            "--output-filename=KindleMint-BookGenerator",
            "--include-data-dir=scripts=scripts",
            "--include-data-dir=config=config",
            "--include-data-dir=templates=templates",
            "generate_book.py"
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Nuitka build completed!")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Nuitka build failed: {e.stderr}")
        return False

def create_distribution_package():
    """Create a complete distribution package"""
    print("📦 Creating distribution package...")
    
    dist_dir = Path("dist/KindleMint-Distribution")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_files = list(Path("dist").glob("KindleMint-BookGenerator*"))
    if exe_files:
        shutil.copy2(exe_files[0], dist_dir)
        exe_name = exe_files[0].name
    else:
        print("❌ No executable found to package")
        return False
    
    # Create README for distribution
    readme_content = f"""# KindleMint Book Generator
    
## Generate Profitable Crossword Books in Minutes!

### What This Does
- Creates complete, KDP-ready crossword puzzle books
- Generates 30-50 high-quality puzzles per book
- Includes professional PDF layout and cover instructions
- Provides market validation and pricing guidance

### How to Use

#### Quick Start (3 commands):
```bash
# Generate a book (interactive mode)
./{exe_name}

# Or specify everything at once
./{exe_name} "Garden Flowers" 40 medium

# Or use flags for clarity
./{exe_name} --theme "Science" --count 50 --difficulty hard
```

#### What You Get:
- ✅ Complete puzzle book (PDF interior)
- ✅ Cover design instructions  
- ✅ KDP upload checklist
- ✅ Market validation report
- ✅ Pricing recommendations

### Examples

Generate different types of books:
```bash
# Popular theme, medium difficulty
./{exe_name} "Garden Flowers" 40 medium

# Educational theme, harder puzzles
./{exe_name} "Famous Authors" 50 hard

# Broad appeal theme
./{exe_name} "Animals" 45 mixed

# Niche but profitable
./{exe_name} "Science" 35 medium --format hardcover
```

### Market-Proven Themes
- 🌸 Garden Flowers ($7.99-$12.99)
- 🎬 Classic Movies ($8.99-$14.99)  
- 📚 Famous Authors ($7.99-$11.99)
- 🌍 World Capitals ($6.99-$10.99)
- 🔬 Science ($8.99-$13.99)
- 🍳 Food & Cooking ($7.99-$12.99)

### Success Tips
1. **Choose proven themes** (use the market validation)
2. **Price competitively** ($6.99-$12.99 sweet spot)
3. **Create a series** (Volume 1, 2, 3 for recurring income)
4. **Use all 7 KDP keywords** (provided in checklist)
5. **Professional presentation** (follow the cover instructions)

### Output Location
Books are generated in: `~/Downloads/KindleMint_Books/`

### Support
- Read the KDP_UPLOAD_CHECKLIST.md for detailed instructions
- Follow pricing recommendations based on theme
- Use market validation suggestions for best results

---
**Transform your puzzle book idea into profit in under 30 minutes!**
"""
    
    with open(dist_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    # Create simple batch file for Windows
    if sys.platform == "win32":
        batch_content = f"""@echo off
echo KindleMint Book Generator
echo.
{exe_name} %*
pause
"""
        with open(dist_dir / "run.bat", 'w') as f:
            f.write(batch_content)
    
    # Create shell script for Unix
    shell_content = f"""#!/bin/bash
echo "🎯 KindleMint Book Generator"
echo
./{exe_name} "$@"
"""
    with open(dist_dir / "run.sh", 'w') as f:
        f.write(shell_content)
    
    os.chmod(dist_dir / "run.sh", 0o755)
    
    print(f"✅ Distribution package created in: {dist_dir}")
    return True

def main():
    """Main build process"""
    print("🚀 Building KindleMint Standalone Executable")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("generate_book.py").exists():
        print("❌ Error: generate_book.py not found. Run from project root.")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Try PyInstaller first
    print("\\n🔨 Attempting build with PyInstaller...")
    if build_with_pyinstaller():
        print("✅ PyInstaller build successful!")
    else:
        print("⚠️  PyInstaller failed, trying Nuitka...")
        if build_with_nuitka():
            print("✅ Nuitka build successful!")
        else:
            print("❌ Both build methods failed. Check dependencies and try manually.")
            sys.exit(1)
    
    # Create distribution package
    if create_distribution_package():
        print("\\n🎉 SUCCESS! Executable package ready for distribution.")
        print("\\n📦 Distribution contents:")
        print("   • Standalone executable (no Python required)")
        print("   • User-friendly README with examples") 
        print("   • Quick-start scripts (run.sh / run.bat)")
        print("\\n💰 Ready to sell on Gumroad/LemonSqueezy for $97!")
        print("\\n📁 Location: dist/KindleMint-Distribution/")
    else:
        print("❌ Failed to create distribution package")
        sys.exit(1)

if __name__ == "__main__":
    main()
