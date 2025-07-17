#!/usr/bin/env python3
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
    print("Goal: $300/day")
    print(f"Status: {today_revenue/300*100:.0f}%")
except:
    print("No revenue data yet. Run LAUNCH_REVENUE_ENGINE.py first!")
