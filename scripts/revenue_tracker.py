#!/usr/bin/env python3
"""
Revenue Tracker - Monitor and report revenue generation
"""

import json
import urllib.request
from datetime import datetime, timedelta

class RevenueTracker:
    def __init__(self):
        self.landing_page = "https://dvdyff0b2oove.cloudfront.net"
        self.data_file = "revenue_data.json"
        self.load_data()
    
    def load_data(self):
        """Load existing revenue data"""
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                "start_date": datetime.now().isoformat(),
                "total_revenue": 0,
                "daily_tracking": {},
                "reddit_posts": [],
                "email_signups": 0,
                "conversions": []
            }
            self.save_data()
    
    def save_data(self):
        """Save revenue data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def check_landing_page_status(self):
        """Check if landing page is accessible"""
        try:
            response = urllib.request.urlopen(self.landing_page, timeout=10)
            return response.getcode() == 200
        except:
            return False
    
    def log_reddit_post(self, subreddit, title, expected_visitors=None):
        """Log a Reddit post for tracking"""
        post_data = {
            "timestamp": datetime.now().isoformat(),
            "subreddit": subreddit,
            "title": title,
            "expected_visitors": expected_visitors or 100,
            "status": "posted"
        }
        self.data["reddit_posts"].append(post_data)
        self.save_data()
        print(f"✅ Logged Reddit post: r/{subreddit}")
    
    def update_revenue(self, amount, source="gumroad"):
        """Update revenue tracking"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.data["daily_tracking"]:
            self.data["daily_tracking"][today] = {
                "revenue": 0,
                "visitors": 0,
                "signups": 0,
                "conversions": 0
            }
        
        self.data["daily_tracking"][today]["revenue"] += amount
        self.data["total_revenue"] += amount
        
        conversion = {
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "source": source
        }
        self.data["conversions"].append(conversion)
        self.save_data()
        print(f"💰 Revenue updated: +${amount} (Total: ${self.data['total_revenue']})")
    
    def generate_report(self):
        """Generate current revenue report"""
        today = datetime.now().strftime('%Y-%m-%d')
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Landing page status
        landing_status = "✅ LIVE" if self.check_landing_page_status() else "❌ DOWN"
        
        # Today's stats
        today_stats = self.data["daily_tracking"].get(today, {
            "revenue": 0, "visitors": 0, "signups": 0, "conversions": 0
        })
        
        # Recent Reddit posts
        recent_posts = [p for p in self.data["reddit_posts"] 
                       if p["timestamp"] >= (datetime.now() - timedelta(hours=24)).isoformat()]
        
        report = f"""
🎯 REVENUE TRACKER REPORT
========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 REVENUE SUMMARY
==================
Total Revenue: ${self.data['total_revenue']:.2f}
Today's Revenue: ${today_stats['revenue']:.2f}
Total Conversions: {len(self.data['conversions'])}

📊 TODAY'S METRICS
==================
Visitors: {today_stats['visitors']}
Email Signups: {today_stats['signups']}
Sales: {today_stats['conversions']}
Conversion Rate: {(today_stats['conversions']/max(today_stats['visitors'], 1)*100):.1f}%

🌐 SYSTEM STATUS
================
Landing Page: {landing_status}
Reddit Posts (24h): {len(recent_posts)}
Traffic Generation: {'✅ ACTIVE' if recent_posts else '❌ INACTIVE'}

📱 RECENT REDDIT POSTS
======================"""

        for post in recent_posts[-3:]:  # Last 3 posts
            report += f"""
- r/{post['subreddit']}: {post['title'][:50]}...
  Expected: {post['expected_visitors']} visitors"""

        if not recent_posts:
            report += "\n- No posts in last 24 hours"

        report += """

🎯 NEXT ACTIONS
==============="""

        if self.data['total_revenue'] == 0:
            report += """
1. 🚀 POST IMMEDIATE CONTENT: Use IMMEDIATE_REVENUE_POSTS.md
2. 📊 Track first visitors and signups
3. 💰 Monitor for first sales"""
        elif self.data['total_revenue'] < 50:
            report += """
1. 📈 Scale Reddit posting (2-3 posts/day)
2. 🎯 Test different subreddits
3. 💡 Optimize post titles and content"""
        else:
            report += """
1. 🚀 Add Pinterest traffic generation  
2. 📱 Add Facebook group engagement
3. 🎯 Launch backend course sales"""

        report += f"""

💡 REVENUE TRACKING TIPS
========================
- Manual revenue updates: python3 scripts/revenue_tracker.py --add-sale 4.99
- Check email signups: Open landing page → F12 → Console → localStorage
- Monitor Gumroad: Check your Gumroad dashboard for sales

📈 PROJECTIONS
==============
At current rate: ${(self.data['total_revenue'] * 30):.2f}/month
Goal ($300/day): {((300 * 30) / max(self.data['total_revenue'] * 30, 1)):.1f}x growth needed
"""

        return report
    
    def quick_status(self):
        """Quick status check"""
        total = self.data['total_revenue']
        recent_posts = len([p for p in self.data["reddit_posts"] 
                           if p["timestamp"] >= (datetime.now() - timedelta(hours=24)).isoformat()])
        
        status = "🚀 LAUNCHING" if total == 0 and recent_posts == 0 else \
                "📈 ACTIVE" if recent_posts > 0 else \
                "💰 EARNING" if total > 0 else "⏸️ IDLE"
        
        return f"{status} | ${total:.2f} total | {recent_posts} posts (24h)"

if __name__ == "__main__":
    import sys
    
    tracker = RevenueTracker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add-sale" and len(sys.argv) > 2:
            amount = float(sys.argv[2])
            tracker.update_revenue(amount)
        elif sys.argv[1] == "--reddit-post" and len(sys.argv) > 3:
            subreddit = sys.argv[2]
            title = sys.argv[3]
            tracker.log_reddit_post(subreddit, title)
        elif sys.argv[1] == "--status":
            print(tracker.quick_status())
        else:
            print("Usage: python3 revenue_tracker.py [--add-sale AMOUNT] [--reddit-post SUBREDDIT TITLE] [--status]")
    else:
        print(tracker.generate_report())