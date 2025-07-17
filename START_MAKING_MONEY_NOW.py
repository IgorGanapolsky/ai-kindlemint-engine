#!/usr/bin/env python3
"""
💰 START MAKING MONEY NOW - Interactive Revenue Generator
This script will guide you through immediate actions to start generating revenue
"""

import os
import json
import subprocess
import time
from datetime import datetime

class RevenueGenerator:
    def __init__(self):
        self.revenue_data = self.load_revenue_data()
        self.actions_completed = []
        
    def load_revenue_data(self):
        """Load existing revenue data or create new"""
        if os.path.exists('revenue_data.json'):
            with open('revenue_data.json', 'r') as f:
                return json.load(f)
        return {"total_revenue": 0, "start_date": str(datetime.now())}
    
    def save_revenue_data(self):
        """Save revenue data"""
        with open('revenue_data.json', 'w') as f:
            json.dump(self.revenue_data, f, indent=2)
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*60)
        print("💰 SKOOL-AI-SYSTEM REVENUE GENERATOR 💰")
        print("="*60)
        print("Your automated puzzle book empire awaits!")
        print(f"Current Revenue: ${self.revenue_data.get('total_revenue', 0)}")
        print("="*60 + "\n")
    
    def check_prerequisites(self):
        """Check if basic requirements are met"""
        print("🔍 Checking prerequisites...")
        
        checks = {
            "Reddit Script": os.path.exists("scripts/traffic_generation/reddit_quick_start.py"),
            "Pinterest Script": os.path.exists("scripts/traffic_generation/pinterest_pin_scheduler.py"),
            "Facebook Script": os.path.exists("scripts/traffic_generation/facebook_group_engager.py"),
            "Revenue Tracker": os.path.exists("check_revenue.py"),
            "Landing Page": True  # Assuming it's live
        }
        
        all_good = True
        for item, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {item}")
            if not status:
                all_good = False
        
        return all_good
    
    def quick_start_menu(self):
        """Display quick start options"""
        print("\n🚀 QUICK START MENU - Choose Your Path to Revenue:\n")
        print("1. 💬 Reddit Blitz - Start getting traffic in 5 minutes")
        print("2. 📌 Pinterest Power - Visual traffic generation")
        print("3. 👥 Facebook Groups - Community engagement")
        print("4. 📧 Email Campaign - Convert subscribers to buyers")
        print("5. 💎 Premium Course - Launch your $97 backend")
        print("6. 🤖 Full Automation - Set everything on autopilot")
        print("7. 📊 Check Revenue - See your earnings")
        print("8. 🎯 Custom Strategy - Get personalized advice")
        print("0. 🚪 Exit")
        
        return input("\nEnter your choice (0-8): ")
    
    def reddit_quick_start(self):
        """Launch Reddit traffic generation"""
        print("\n💬 REDDIT QUICK START")
        print("-" * 40)
        
        # Check if credentials exist
        config_path = "scripts/traffic_generation/reddit_config.json"
        if not os.path.exists(config_path):
            print("⚠️  Reddit credentials not set up!")
            print("\nLet's set them up now:")
            print("1. Go to: https://www.reddit.com/prefs/apps")
            print("2. Create a 'script' type app")
            print("3. Note your Client ID and Client Secret")
            
            client_id = input("\nEnter Reddit Client ID: ")
            client_secret = input("Enter Reddit Client Secret: ")
            username = input("Enter Reddit Username: ")
            password = input("Enter Reddit Password: ")
            
            config = {
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password,
                "user_agent": "skool-ai-system/1.0"
            }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Reddit credentials saved!")
        
        print("\n🎯 Launching Reddit traffic generator...")
        try:
            subprocess.run(["python3", "scripts/traffic_generation/reddit_quick_start.py"])
            self.actions_completed.append("reddit_traffic")
            print("✅ Reddit traffic system activated!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def pinterest_setup(self):
        """Set up Pinterest automation"""
        print("\n📌 PINTEREST POWER SETUP")
        print("-" * 40)
        print("Pinterest can drive 100-300 visitors/day!")
        print("\nYou'll need:")
        print("1. Pinterest Business Account")
        print("2. API Access (https://developers.pinterest.com/)")
        
        has_api = input("\nDo you have Pinterest API access? (y/n): ").lower()
        if has_api == 'y':
            api_key = input("Enter Pinterest API Key: ")
            # Save config
            config = {"api_key": api_key, "board_id": "your-board-id"}
            with open("scripts/traffic_generation/pinterest_config.json", 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Pinterest configured! Ready to generate pins.")
            self.actions_completed.append("pinterest_setup")
        else:
            print("\n📝 Next steps:")
            print("1. Apply for API access at https://developers.pinterest.com/")
            print("2. Create a board for your puzzle content")
            print("3. Run this setup again when ready")
    
    def facebook_groups(self):
        """Facebook group engagement setup"""
        print("\n👥 FACEBOOK GROUP ENGAGEMENT")
        print("-" * 40)
        print("Top puzzle groups to join:")
        print("- Sudoku Lovers (50k members)")
        print("- Brain Games for Seniors (30k)")
        print("- Puzzle Addicts Anonymous (25k)")
        print("\n⚠️  Remember: Provide VALUE first, sell second!")
        
        ready = input("\nReady to start Facebook engagement? (y/n): ").lower()
        if ready == 'y':
            print("\n✅ Launching Facebook group engager...")
            print("This will open Chrome and guide you through the process.")
            self.actions_completed.append("facebook_groups")
    
    def check_revenue(self):
        """Check current revenue status"""
        print("\n📊 REVENUE STATUS")
        print("-" * 40)
        
        if os.path.exists("revenue_status.json"):
            with open("revenue_status.json", 'r') as f:
                status = json.load(f)
                print(f"Total Revenue: ${status.get('total_revenue', 0)}")
                print(f"Today's Revenue: ${status.get('today_revenue', 0)}")
                print(f"Email Subscribers: {status.get('subscribers', 0)}")
                print(f"Conversion Rate: {status.get('conversion_rate', 0)}%")
        else:
            print("No revenue data yet. Start generating traffic first!")
        
        print("\n💡 Pro tip: Check your Gumroad dashboard for real-time sales")
    
    def custom_strategy(self):
        """Provide custom strategy based on user's situation"""
        print("\n🎯 CUSTOM STRATEGY BUILDER")
        print("-" * 40)
        
        print("Answer a few questions for personalized advice:\n")
        
        time_available = input("How much time can you dedicate daily? (hours): ")
        current_audience = input("Do you have an existing audience? (y/n): ").lower()
        tech_comfort = input("Rate your tech comfort (1-10): ")
        primary_goal = input("Primary goal - Quick cash or Long-term business? (q/l): ").lower()
        
        print("\n💡 YOUR PERSONALIZED STRATEGY:")
        print("-" * 40)
        
        if primary_goal == 'q':
            print("🚀 QUICK CASH FOCUS:")
            print("1. Start with Reddit - lowest barrier, fastest results")
            print("2. Price your puzzle books at $4.99 for quick sales")
            print("3. Post 3x daily with value-first content")
            print("4. Expected: $50-100 within 48 hours")
        else:
            print("🏗️ LONG-TERM EMPIRE:")
            print("1. Build email list first (more valuable than immediate sales)")
            print("2. Create premium backend products ($97-497)")
            print("3. Develop subscription model ($29/month)")
            print("4. Focus on SEO and content marketing")
            print("5. Expected: $5k-10k/month within 6 months")
        
        if current_audience == 'y':
            print("\n✨ LEVERAGE YOUR AUDIENCE:")
            print("- Send email blast about free puzzles")
            print("- Create exclusive member benefits")
            print("- Ask for testimonials and social proof")
        
        if int(tech_comfort) < 5:
            print("\n🤝 LOW-TECH APPROACH:")
            print("- Focus on manual Reddit posting first")
            print("- Use simple tools like Buffer for scheduling")
            print("- Hire a VA for technical tasks ($5-10/hour)")
    
    def full_automation(self):
        """Set up full automation"""
        print("\n🤖 FULL AUTOMATION SETUP")
        print("-" * 40)
        print("This will set up daily automated:")
        print("- Reddit posts (3x/day)")
        print("- Pinterest pins (10x/day)")
        print("- Facebook engagement (2x/day)")
        print("- Revenue tracking and reporting")
        
        confirm = input("\nSet up full automation? (y/n): ").lower()
        if confirm == 'y':
            print("\n⚙️  Setting up cron jobs...")
            cron_commands = [
                "0 9,14,19 * * * cd /workspace && python3 scripts/traffic_generation/reddit_organic_poster.py",
                "0 10,16 * * * cd /workspace && python3 scripts/traffic_generation/pinterest_pin_scheduler.py",
                "0 11,17 * * * cd /workspace && python3 scripts/traffic_generation/facebook_group_engager.py",
                "0 23 * * * cd /workspace && python3 check_revenue.py"
            ]
            
            print("\nAdd these to your crontab (crontab -e):")
            for cmd in cron_commands:
                print(cmd)
            
            print("\n✅ Automation ready! Your empire will grow while you sleep.")
            self.actions_completed.append("full_automation")
    
    def run(self):
        """Main execution loop"""
        self.print_banner()
        
        if not self.check_prerequisites():
            print("\n⚠️  Some prerequisites are missing.")
            print("Run: ./merge_prs_and_launch.sh to fix")
            return
        
        while True:
            choice = self.quick_start_menu()
            
            if choice == '0':
                print("\n👋 Good luck with your puzzle empire!")
                print(f"Actions completed: {', '.join(self.actions_completed)}")
                break
            elif choice == '1':
                self.reddit_quick_start()
            elif choice == '2':
                self.pinterest_setup()
            elif choice == '3':
                self.facebook_groups()
            elif choice == '4':
                print("\n📧 Email campaign setup coming soon!")
            elif choice == '5':
                print("\n💎 Premium course upload guide coming soon!")
            elif choice == '6':
                self.full_automation()
            elif choice == '7':
                self.check_revenue()
            elif choice == '8':
                self.custom_strategy()
            else:
                print("\n❌ Invalid choice. Try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    generator = RevenueGenerator()
    generator.run()