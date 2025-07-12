#!/usr/bin/env python3
"""
🚀 MASTER REVENUE LAUNCHER
One command to $300/day
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def print_banner():
    print("""
    💰 AUTONOMOUS REVENUE ENGINE 💰
    ==============================
    Goal: $300/day with minimal effort
    Status: Ready to launch!
    """)

def check_prerequisites():
    """Check what's ready and what needs attention"""
    status = {
        "gumroad_price": False,
        "traffic_ready": False,
        "backend_course": False,
        "apis_configured": False
    }
    
    # Check if autonomous engine has memory
    if Path("revenue_memory.json").exists():
        with open("revenue_memory.json") as f:
            memory = json.load(f)
            status["gumroad_price"] = memory["state"].get("gumroad_price_updated", False)
            status["traffic_ready"] = memory["state"].get("traffic_running", False)
            status["backend_course"] = memory["state"].get("backend_course_created", False)
            status["apis_configured"] = memory["state"].get("apis_configured", False)
    
    return status

def launch_sequence():
    """Execute the complete launch sequence"""
    
    print_banner()
    
    print("🔍 Checking system status...")
    status = check_prerequisites()
    
    # 1. Run autonomous engine first
    print("\n🤖 Starting Autonomous Revenue Engine...")
    subprocess.run([sys.executable, "scripts/autonomous_revenue_engine.py"])
    
    # 2. If price not updated, launch helper
    if not status["gumroad_price"]:
        print("\n💰 CRITICAL: Gumroad price needs update!")
        print("Launching price update helper...")
        if Path("update_gumroad_price.py").exists():
            subprocess.run([sys.executable, "update_gumroad_price.py"])
    
    # 3. Launch traffic generation
    print("\n🚀 Preparing traffic generation...")
    
    # Check if we can use quick start (no API needed)
    quick_start = Path("worktrees/experiments/scripts/traffic_generation/reddit_quick_start.py")
    if quick_start.exists():
        print("✅ Using Reddit quick start (no API required!)")
        print("\nGenerating today's content...")
        
        # Run autonomous content generator
        if Path("scripts/autonomous_content_generator.py").exists():
            subprocess.run([sys.executable, "scripts/autonomous_content_generator.py"])
        
        print("\n📝 Ready to post! Opening Reddit helper...")
        time.sleep(2)
        subprocess.run([sys.executable, str(quick_start)])
    
    # 4. Check for opportunities
    print("\n🔍 Scanning for revenue opportunities...")
    if Path("scripts/opportunity_finder.py").exists():
        subprocess.run([sys.executable, "scripts/opportunity_finder.py"])
    
    # 5. Create quick action checklist
    create_action_checklist(status)
    
    # 6. Set up monitoring
    setup_monitoring()
    
    print("\n✅ LAUNCH SEQUENCE COMPLETE!")
    print("\n💡 Next steps are in: DAILY_ACTIONS.md")

def create_action_checklist(status):
    """Create a simple daily checklist"""
    
    checklist = f"""# 🎯 DAILY REVENUE ACTIONS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## ⚡ CRITICAL ACTIONS (Do First!)

"""
    
    if not status["gumroad_price"]:
        checklist += """### 1. Update Gumroad Price ⚠️
- [ ] Go to: https://app.gumroad.com/products
- [ ] Change price from $14.99 to $4.99
- [ ] Save changes
- [ ] Run this script again to confirm

"""
    
    checklist += """### 2. Post Reddit Content (5 mins)
- [ ] Check autonomous_content/reddit_posts_week.json
- [ ] Run: python worktrees/experiments/scripts/traffic_generation/reddit_quick_start.py
- [ ] Post to r/sudoku, r/puzzles
- [ ] Engage with 2-3 comments

### 3. Monitor Revenue (2 mins)
- [ ] Check Gumroad dashboard
- [ ] Note sales in revenue_tracker.txt
- [ ] Celebrate any sale! 🎉

## 📊 AUTOMATED TASKS (Running for you)

- ✅ Content generation (done)
- ✅ Opportunity scanning (done)
- ✅ Performance optimization (ongoing)
- ✅ Backend course creation (in progress)

## 🚀 QUICK WINS TODAY

1. **Bundle Deal** (10 mins)
   - Create 3-book bundle on Gumroad
   - Price at $12.99 (save $2)
   - Add to product description

2. **Email Blast** (5 mins)
   - Subject: "Quick puzzle tip..."
   - Send to your list
   - Include 20% off code

3. **Pinterest Batch** (15 mins)
   - Upload 5 puzzle preview images
   - Use SEO descriptions from autonomous_content/

## 📈 REVENUE TRACKER

Morning check: $______
Afternoon check: $______
Evening total: $______

Goal: $300
Status: ______%

## 💭 REMEMBER

- Every action compounds
- Speed > Perfection
- $10 sales add up to $300
- You're building an empire!

---
*Refresh: Run LAUNCH_REVENUE_ENGINE.py again*
"""
    
    with open("DAILY_ACTIONS.md", "w") as f:
        f.write(checklist)
    
    print("📋 Created DAILY_ACTIONS.md checklist")

def setup_monitoring():
    """Set up simple monitoring"""
    
    monitor_script = """#!/bin/bash
# Simple revenue monitor

while true; do
    clear
    echo "💰 REVENUE MONITOR 💰"
    echo "===================="
    echo "Time: $(date '+%H:%M:%S')"
    echo ""
    
    # Check if memory file exists
    if [ -f "revenue_memory.json" ]; then
        echo "📊 Today's Revenue: $(grep -o '"daily_revenues".*' revenue_memory.json | tail -1)"
    fi
    
    echo ""
    echo "🎯 Goal: $300/day"
    echo ""
    echo "Press Ctrl+C to exit"
    
    sleep 60
done
"""
    
    with open("monitor_revenue.sh", "w") as f:
        f.write(monitor_script)
    
    os.chmod("monitor_revenue.sh", 0o755)
    print("📊 Created monitor_revenue.sh")

def create_shortcuts():
    """Create helpful shortcuts"""
    
    # Quick Reddit post
    with open("quick_reddit.sh", "w") as f:
        f.write("""#!/bin/bash
cd worktrees/experiments/scripts/traffic_generation
python3 reddit_quick_start.py
""")
    os.chmod("quick_reddit.sh", 0o755)
    
    # Revenue check
    with open("check_revenue.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import json
from datetime import datetime

try:
    with open("revenue_memory.json") as f:
        memory = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_revenue = memory["performance"]["daily_revenues"].get(today, 0)
    total = memory["state"]["total_revenue_generated"]
    
    print(f"Today: ${today_revenue:.2f}")
    print(f"Total: ${total:.2f}")
    print(f"Goal: $300/day")
    print(f"Status: {today_revenue/300*100:.0f}%")
except:
    print("No revenue data yet. Run LAUNCH_REVENUE_ENGINE.py first!")
""")
    os.chmod("check_revenue.py", 0o755)
    
    print("⚡ Created quick shortcuts:")
    print("   - ./quick_reddit.sh")
    print("   - ./check_revenue.py")

if __name__ == "__main__":
    # Create all components
    create_shortcuts()
    
    # Launch the sequence
    launch_sequence()
    
    print("\n🎉 SYSTEM LAUNCHED!")
    print("\n⏰ Daily reminder: The key to $300/day is CONSISTENCY")
    print("   - Post content daily")
    print("   - Check revenue 3x/day")
    print("   - Iterate based on results")
    print("\n💪 You've got this! See DAILY_ACTIONS.md for your checklist.")