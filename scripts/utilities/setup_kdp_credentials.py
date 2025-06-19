#!/usr/bin/env python3
"""
KDP Credentials Setup
Securely configure KDP publishing credentials
"""
import os
import getpass
from pathlib import Path

def setup_kdp_credentials():
    """Interactive setup for KDP credentials."""
    print("=" * 60)
    print("🔐 KDP CREDENTIALS SETUP")
    print("=" * 60)
    print("This will configure your Amazon KDP credentials for automated publishing.")
    print("Your credentials will be stored as environment variables.")
    print()
    
    # Get credentials
    print("📧 Enter your Amazon KDP email address:")
    kdp_email = input("KDP Email: ").strip()
    
    if not kdp_email:
        print("❌ Email cannot be empty")
        return False
    
    print("\n🔑 Enter your Amazon KDP password:")
    kdp_password = getpass.getpass("KDP Password: ").strip()
    
    if not kdp_password:
        print("❌ Password cannot be empty")
        return False
    
    print("\n🔒 Configuring credentials...")
    
    try:
        # Create .env file in project root
        env_file = Path(__file__).parent.parent.parent / ".env"
        
        # Read existing .env if it exists
        env_content = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        # Remove existing KDP credentials
        env_content = [line for line in env_content 
                      if not line.startswith('KDP_EMAIL=') 
                      and not line.startswith('KDP_PASSWORD=')]
        
        # Add new credentials
        env_content.append(f"KDP_EMAIL={kdp_email}\n")
        env_content.append(f"KDP_PASSWORD={kdp_password}\n")
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.writelines(env_content)
        
        print("✅ Credentials saved to .env file")
        
        # Set environment variables for current session
        os.environ['KDP_EMAIL'] = kdp_email
        os.environ['KDP_PASSWORD'] = kdp_password
        
        print("✅ Environment variables set for current session")
        
        print("\n" + "=" * 60)
        print("🎉 KDP CREDENTIALS CONFIGURED SUCCESSFULLY!")
        print("=" * 60)
        print("📋 Next Steps:")
        print("1. Your credentials are now ready for automated publishing")
        print("2. Run the Volume 1 publishing script")
        print("3. Monitor the automated publishing process")
        print()
        print("💡 Security Notes:")
        print("- Credentials are stored in .env file (excluded from git)")
        print("- Never share your .env file or commit it to version control")
        print("- Use app-specific passwords if you have 2FA enabled")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")
        return False

def test_credentials():
    """Test if credentials are properly configured."""
    kdp_email = os.getenv('KDP_EMAIL')
    kdp_password = os.getenv('KDP_PASSWORD')
    
    if kdp_email and kdp_password:
        print("✅ KDP credentials are configured")
        print(f"📧 Email: {kdp_email}")
        print(f"🔑 Password: {'*' * len(kdp_password)}")
        return True
    else:
        print("❌ KDP credentials not found")
        return False

def main():
    """Main setup function."""
    print("🔍 Checking current credential status...")
    
    if test_credentials():
        print("\n💡 Credentials already configured. Reconfigure? (y/n): ", end="")
        response = input().strip().lower()
        if response not in ['y', 'yes']:
            print("✅ Using existing credentials")
            return True
    
    return setup_kdp_credentials()

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)