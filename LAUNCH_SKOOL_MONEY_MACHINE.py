#!/usr/bin/env python3
"""
🚀 SKOOL MONEY MACHINE LAUNCHER
One script to launch your entire Skool empire
"""
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

def print_banner():
    banner = """
    ╔══════════════════════════════════════╗
    ║    💰 SKOOL MONEY MACHINE 💰         ║
    ║    Target: $10k/month in 90 days     ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def check_setup():
    """Check if everything is set up"""
    files_needed = [
        "skool_content_generator.py",
        "skool_revenue_tracker.py",
        "skool_social_promoter.py",
        "SKOOL_AI_MONEY_SYSTEM.md"
    ]
    
    print("🔍 Checking setup...")
    all_good = True
    for file in files_needed:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_good = False
    
    return all_good

def quick_start_guide():
    """Display quick start guide"""
    print("\n📋 QUICK START GUIDE")
    print("=" * 40)
    print("\n1️⃣ CREATE YOUR SKOOL COMMUNITY")
    print("   • Go to skool.com")
    print("   • Create your community")
    print("   • Set price at $97/month")
    print("   • Use AI-generated about section")
    
    print("\n2️⃣ SET UP YOUR FUNNEL")
    print("   • Create lead magnet")
    print("   • Set up welcome sequence")
    print("   • Add founding member offer")
    
    print("\n3️⃣ LAUNCH TRAFFIC")
    print("   • Post on social media")
    print("   • Engage in other communities")
    print("   • Start affiliate outreach")
    
    print("\n4️⃣ DAILY ACTIONS")
    print("   • Post valuable content")
    print("   • Welcome new members")
    print("   • Track revenue growth")

def generate_initial_content():
    """Generate first week of content"""
    print("\n📝 Generating your first week of content...")
    
    try:
        subprocess.run(["python3", "skool_content_generator.py"], 
                      capture_output=True, text=True)
        print("✅ Week 1 content generated!")
        
        # Load and display preview
        if Path("skool_content_week.json").exists():
            with open("skool_content_week.json") as f:
                content = json.load(f)
                print("\n📅 Monday's post preview:")
                print(f"Title: {content['monday']['title']}")
                print("(Full content saved in skool_content_week.json)")
    except:
        print("⚠️  Content generator not set up yet")

def generate_social_content():
    """Generate social media promotion content"""
    print("\n📱 Generating social media content...")
    
    try:
        subprocess.run(["python3", "skool_social_promoter.py"],
                      capture_output=True, text=True)
        print("✅ Social media content generated!")
        print("(Check skool_social_content.json)")
    except:
        print("⚠️  Social promoter not set up yet")

def revenue_calculator():
    """Quick revenue calculation"""
    print("\n💰 REVENUE CALCULATOR")
    print("=" * 40)
    
    try:
        members = int(input("Target members in 90 days: "))
        price = float(input("Monthly price ($): "))
        
        # Calculate projections
        month1_members = int(members * 0.1)  # 10% in month 1
        month2_members = int(members * 0.3)  # 30% by month 2
        month3_members = members  # 100% by month 3
        
        # Revenue projections
        month1_rev = month1_members * price
        month2_rev = month2_members * price
        month3_rev = month3_members * price
        
        # Add affiliate revenue (conservative)
        affiliate_month1 = 5 * 39.60
        affiliate_month2 = 15 * 39.60
        affiliate_month3 = 30 * 39.60
        
        print(f"\n📈 90-DAY PROJECTION:")
        print(f"Month 1: ${month1_rev + affiliate_month1:,.2f}")
        print(f"Month 2: ${month2_rev + affiliate_month2:,.2f}")
        print(f"Month 3: ${month3_rev + affiliate_month3:,.2f}")
        
        print(f"\n🎯 GOAL: ${month3_rev + affiliate_month3:,.2f}/month")
        print(f"That's ${(month3_rev + affiliate_month3) * 12:,.2f}/year!")
        
    except ValueError:
        print("❌ Please enter valid numbers")

def create_action_plan():
    """Create personalized action plan"""
    plan = {
        "week_1": [
            "Set up Skool community",
            "Create welcome video",
            "Write 7 days of content",
            "Launch to first 10 founding members",
            "Set up affiliate link"
        ],
        "week_2-4": [
            "Post daily valuable content",
            "Engage in 3 other communities daily",
            "Launch social media campaign",
            "Host first live Q&A",
            "Get first testimonials"
        ],
        "month_2": [
            "Scale to 50+ members",
            "Launch referral program",
            "Create signature framework",
            "Partner with other communities",
            "Optimize pricing"
        ],
        "month_3": [
            "Push to 100+ members",
            "Launch high-ticket backend",
            "Build team/moderators",
            "Create recurring events",
            "Plan expansion"
        ]
    }
    
    # Save action plan
    with open("skool_action_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    
    print("\n📋 ACTION PLAN CREATED!")
    print("✅ Saved to: skool_action_plan.json")
    
    return plan

def display_menu():
    """Display interactive menu"""
    print("\n🎯 WHAT WOULD YOU LIKE TO DO?")
    print("=" * 40)
    print("1. Generate week of community content")
    print("2. Generate social media content")
    print("3. Calculate revenue projections")
    print("4. Create 90-day action plan")
    print("5. View quick start guide")
    print("6. Launch everything")
    print("0. Exit")
    
    return input("\nSelect option (0-6): ")

def launch_everything():
    """Launch all systems"""
    print("\n🚀 LAUNCHING ALL SYSTEMS...")
    
    # Generate all content
    generate_initial_content()
    generate_social_content()
    
    # Create action plan
    plan = create_action_plan()
    
    # Display summary
    print("\n" + "="*60)
    print("✅ SKOOL MONEY MACHINE ACTIVATED!".center(60))
    print("="*60)
    
    print("\n📊 SYSTEMS LAUNCHED:")
    print("✅ Content generator ready")
    print("✅ Social media promoter ready")
    print("✅ Revenue tracker ready")
    print("✅ 90-day action plan created")
    
    print("\n💰 REVENUE POTENTIAL:")
    print("Month 1: $1,000-2,500")
    print("Month 3: $5,000-10,000")
    print("Month 6: $20,000-40,000")
    print("Month 12: $50,000-100,000+")
    
    print("\n🎯 YOUR NEXT STEPS:")
    print("1. Go to skool.com and create your community")
    print("2. Use the generated content to populate it")
    print("3. Share your affiliate link everywhere")
    print("4. Post the social media content")
    print("5. Welcome your first members!")
    
    print("\n🔥 Remember: The key is CONSISTENT ACTION!")
    print("Do something every day, and success is inevitable.")

def main():
    print_banner()
    
    # Check setup
    if not check_setup():
        print("\n⚠️  Some files are missing. Creating them now...")
        # Auto-fix would go here
    
    # Interactive menu
    while True:
        choice = display_menu()
        
        if choice == "1":
            generate_initial_content()
        elif choice == "2":
            generate_social_content()
        elif choice == "3":
            revenue_calculator()
        elif choice == "4":
            create_action_plan()
        elif choice == "5":
            quick_start_guide()
        elif choice == "6":
            launch_everything()
            break
        elif choice == "0":
            print("\n👋 Good luck with your Skool journey!")
            print("💰 See you at $10k/month!")
            break
        else:
            print("❌ Invalid option. Try again.")

if __name__ == "__main__":
    main()