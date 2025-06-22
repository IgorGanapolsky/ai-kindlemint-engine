#!/usr/bin/env python3
"""
Daily Production Runner - Automated Content Factory
Runs daily series generation and organizes output for easy publishing
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_daily_production():
    """Run daily series generation and organize for publishing"""
    
    print("🏭" * 50)
    print("📚 DAILY BOOK PRODUCTION FACTORY")
    print("🏭" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Mission: Generate profitable book series daily")
    print("🏭" * 50)
    
    # Run the daily series generator
    print("\n🔄 Starting daily series generation...")
    
    try:
        result = subprocess.run([
            sys.executable, 
            "scripts/daily_series_generator.py"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Daily series generation completed successfully!")
            print("\n📋 Generation Output:")
            print(result.stdout)
            
            # Find today's output directory
            today = datetime.now().strftime('%Y%m%d')
            output_dir = Path(f"output/daily_production/{today}")
            
            if output_dir.exists():
                print(f"\n📁 Today's production saved to: {output_dir}")
                
                # List generated series
                series_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
                
                for series_dir in series_dirs:
                    print(f"\n📚 Generated Series: {series_dir.name}")
                    
                    # Count volumes
                    volume_dirs = [d for d in series_dir.iterdir() if d.is_dir() and d.name.startswith('volume_')]
                    print(f"   📖 Volumes: {len(volume_dirs)}")
                    
                    # Show key files
                    key_files = [
                        "PUBLISHING_MASTER_GUIDE.txt",
                        "MARKETING_STRATEGY.txt", 
                        "cover_design_brief.txt"
                    ]
                    
                    for file in key_files:
                        if (series_dir / file).exists():
                            print(f"   ✓ {file}")
                
                print(f"\n🎯 NEXT STEPS:")
                print(f"1. Navigate to: {output_dir}")
                print(f"2. Create covers using the cover prompts")
                print(f"3. Follow the publishing guides to get books live")
                print(f"4. Set up Amazon advertising")
                print(f"5. Track sales and iterate")
                
                print(f"\n💰 BUSINESS IMPACT:")
                print(f"• Daily content generation = consistent publishing pipeline")
                print(f"• Multiple series = diversified revenue streams") 
                print(f"• Detailed guides = faster time to market")
                print(f"• Professional content = higher sales potential")
                
            else:
                print(f"⚠️ Output directory not found: {output_dir}")
                
        else:
            print("❌ Daily series generation failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running daily production: {e}")
        return False
    
    print("\n🏭" * 50)
    print("✅ DAILY PRODUCTION COMPLETE!")
    print("🚀 Time to publish and make money!")
    print("🏭" * 50)
    
    return True

def setup_daily_automation():
    """Help set up automated daily runs"""
    
    print("\n🤖 AUTOMATION SETUP OPTIONS:")
    print("\n1. MANUAL DAILY RUN:")
    print("   python scripts/run_daily_production.py")
    
    print("\n2. CRON JOB (Linux/Mac):")
    print("   # Run daily at 9 AM")
    print("   0 9 * * * cd /path/to/ai-kindlemint-engine && python scripts/run_daily_production.py")
    
    print("\n3. GITHUB ACTIONS (Automated):")
    print("   # Set up workflow_dispatch trigger")
    print("   # Run on schedule or manual trigger")
    print("   # Commit results back to repo")
    
    print("\n4. LOCAL SCHEDULER:")
    print("   # Use Task Scheduler (Windows) or Automator (Mac)")
    print("   # Set to run this script daily")
    
    print("\n🎯 RECOMMENDED WORKFLOW:")
    print("1. Run manually for first week")
    print("2. Set up automation once proven")
    print("3. Focus on publishing and marketing")
    print("4. Let automation feed your publishing pipeline")

def main():
    """Main automation runner"""
    
    # Check if we're in the right directory
    if not Path("scripts/daily_series_generator.py").exists():
        print("❌ Please run from the project root directory")
        print("   (The directory containing scripts/daily_series_generator.py)")
        sys.exit(1)
    
    # Run daily production
    success = run_daily_production()
    
    if not success:
        print("❌ Daily production failed!")
        sys.exit(1)
    
    # Show automation options
    setup_daily_automation()
    
    print("\n💡 FOUNDER WISDOM:")
    print("• Consistency beats perfection")
    print("• Daily content = compound growth")
    print("• Publishing speed = competitive advantage")
    print("• Automation frees you to focus on marketing")
    
    return 0

if __name__ == "__main__":
    exit(main())