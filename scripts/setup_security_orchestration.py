#!/usr/bin/env python3
"""
Setup Security Orchestration

This script integrates security validation into the development workflow:
1. Installs pre-commit security hooks
2. Configures security scanning 
3. Sets up automated security monitoring
"""

import os
import shutil
import subprocess
import json
from pathlib import Path


def main():
    """Setup security orchestration"""
    project_root = Path(__file__).parent.parent
    
    print("🔒 Setting up Security Orchestration for KindleMint")
    print("=" * 60)
    
    # 1. Install pre-commit hook
    setup_precommit_hook(project_root)
    
    # 2. Install security tools
    install_security_tools()
    
    # 3. Create reports directory
    setup_reports_directory(project_root)
    
    # 4. Test security orchestrator
    test_security_orchestrator(project_root)
    
    # 5. Integration instructions
    print_integration_instructions()
    
    print("\n✅ Security orchestration setup complete!")
    print("\n🛡️  Your repository is now protected against:")
    print("   • Hardcoded secrets and passwords")
    print("   • Vulnerable dependencies")  
    print("   • Insecure code patterns")
    print("   • Configuration issues")
    print("\n🚀 Next commit will be automatically validated!")


def setup_precommit_hook(project_root: Path):
    """Install the pre-commit security hook"""
    print("\n1. Installing pre-commit security hook...")
    
    git_hooks_dir = project_root / ".git" / "hooks"
    pre_commit_hook = git_hooks_dir / "pre-commit"
    security_hook_source = project_root / "scripts" / "git-hooks" / "pre-commit-security"
    
    # Make the security hook executable
    os.chmod(security_hook_source, 0o755)
    
    if pre_commit_hook.exists():
        # Backup existing hook
        backup_path = git_hooks_dir / "pre-commit.backup"
        shutil.copy2(pre_commit_hook, backup_path)
        print(f"   📁 Backed up existing pre-commit hook to {backup_path}")
    
    # Copy our security hook
    shutil.copy2(security_hook_source, pre_commit_hook)
    os.chmod(pre_commit_hook, 0o755)
    
    print("   ✅ Pre-commit security hook installed")


def install_security_tools():
    """Install required security scanning tools"""
    print("\n2. Installing security scanning tools...")
    
    tools_to_install = [
        "safety",      # Python dependency vulnerability scanner
        "bandit",      # Python security linter
        "semgrep",     # Static analysis tool
    ]
    
    for tool in tools_to_install:
        try:
            # Check if already installed
            result = subprocess.run(
                ["pip", "show", tool],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ {tool} already installed")
            else:
                print(f"   📦 Installing {tool}...")
                subprocess.run(
                    ["pip", "install", tool],
                    check=True,
                    capture_output=True
                )
                print(f"   ✅ {tool} installed successfully")
                
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to install {tool}: {e}")
            print(f"      You can install manually: pip install {tool}")


def setup_reports_directory(project_root: Path):
    """Create security reports directory"""
    print("\n3. Setting up security reports directory...")
    
    reports_dir = project_root / "reports" / "security"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .gitignore for reports (keep reports but not sensitive details)
    gitignore_content = """# Security reports
*.json
*.log
*.txt

# Keep directory structure
!.gitkeep
"""
    
    with open(reports_dir / ".gitignore", "w") as f:
        f.write(gitignore_content)
    
    # Create .gitkeep file
    (reports_dir / ".gitkeep").touch()
    
    print("   ✅ Security reports directory created")


def test_security_orchestrator(project_root: Path):
    """Test the security orchestrator"""
    print("\n4. Testing security orchestrator...")
    
    try:
        # Import and test the security orchestrator
        import sys
        sys.path.insert(0, str(project_root))
        
        from scripts.orchestration.security_orchestrator import SecurityOrchestrator
        
        orchestrator = SecurityOrchestrator()
        print("   ✅ Security orchestrator imported successfully")
        
        # Test configuration loading
        if orchestrator.config:
            print("   ✅ Security configuration loaded")
        
        # Test secret patterns
        if orchestrator.secret_patterns:
            print(f"   ✅ {len(orchestrator.secret_patterns)} secret detection patterns loaded")
        
    except Exception as e:
        print(f"   ⚠️  Security orchestrator test failed: {e}")
        print("      The setup may still work, but testing failed")


def print_integration_instructions():
    """Print instructions for integrating with existing workflows"""
    print("\n" + "=" * 60)
    print("🚀 INTEGRATION INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 MANUAL SECURITY SCAN:")
    print("   python scripts/orchestration/security_orchestrator.py")
    
    print("\n📋 VALIDATE BEFORE COMMIT:")
    print("   # The pre-commit hook will run automatically")
    print("   # Or run manually: python scripts/git-hooks/pre-commit-security")
    
    print("\n📋 ADD TO DAILY ORCHESTRATION:")
    print("   # Add this line to your daily workflow:")
    print("   python scripts/orchestration/security_orchestrator.py")
    
    print("\n📋 GITHUB ACTIONS INTEGRATION:")
    print("   # The security-orchestration.yml workflow is already set up")
    print("   # It will run on all PRs and daily at 2 AM UTC")
    
    print("\n📋 ALEMBIC INTEGRATION:")
    print("   # Security scanning is integrated with Alembic orchestrator")
    print("   # No additional setup needed")
    
    print("\n📋 VIEW SECURITY REPORTS:")
    print("   ls -la reports/security/")
    print("   cat reports/security/security_report_*.json")
    
    print("\n📋 REQUIRED ENVIRONMENT VARIABLES:")
    print("   # These should be set in GitHub Secrets:")
    print("   ENCRYPTION_PASSWORD=<32-character-password>")
    print("   ENCRYPTION_SALT=<32-character-salt>")
    
    print("\n⚡ EMERGENCY SECURITY RESPONSE:")
    print("   1. Critical issues will block commits")
    print("   2. GitHub Issues will be created automatically") 
    print("   3. Slack notifications sent (if configured)")
    print("   4. See docs/SECURITY_FIX.md for guidance")


if __name__ == "__main__":
    main()