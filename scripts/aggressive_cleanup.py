#!/usr/bin/env python3
"""
AGGRESSIVE HYGIENE ORCHESTRATION
Remove all bloat and unused dependencies
"""

PACKAGES_TO_REMOVE = [
    # Browser automation we don't need
    "playwright",
    
    # Mystery packages
    "nova-act",
    
    # Questionable dependencies
    "pytrends",  # Google Trends - not needed
    "pytest-json-report",  # Overkill
    "pytest-metadata",  # Overkill
    "requests-file",  # Rarely needed
    "requests-toolbelt",  # Unnecessary
    "numpydoc",  # We're not building scientific libraries
    "typing-inspection",  # Not needed in production
    
    # Duplicates (keep lowercase versions)
    "PyPDF2",  # Keep pypdf2
    "PyYAML",  # Keep pyyaml  
    "Pillow",  # Keep pillow
]

def clean_requirements():
    """Remove bloat from requirements.txt"""
    with open("../requirements.txt", "r") as f:
        lines = f.readlines()
    
    cleaned = []
    removed = []
    
    for line in lines:
        package = line.split("==")[0].strip()
        if package in PACKAGES_TO_REMOVE:
            removed.append(line.strip())
        else:
            cleaned.append(line)
    
    with open("../requirements.txt", "w") as f:
        f.writelines(cleaned)
    
    print("🧹 AGGRESSIVE CLEANUP COMPLETE!")
    print(f"📦 Removed {len(removed)} packages:")
    for pkg in removed:
        print(f"  ❌ {pkg}")
    print(f"\n✅ Requirements reduced to {len(cleaned)} packages")

if __name__ == "__main__":
    clean_requirements()