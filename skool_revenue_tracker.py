#!/usr/bin/env python3
"""
Skool Revenue Tracker & Calculator
Track your community growth and calculate revenue projections
"""
import json
import datetime
from pathlib import Path

class SkoolRevenueTracker:
    def __init__(self):
        self.data_file = Path("skool_revenue_data.json")
        self.load_data()
    
    def load_data(self):
        """Load existing data or create new"""
        if self.data_file.exists():
            with open(self.data_file) as f:
                self.data = json.load(f)
        else:
            self.data = {
                "community": {
                    "name": "",
                    "price_per_month": 97,
                    "members": 0,
                    "launch_date": str(datetime.date.today())
                },
                "affiliates": {
                    "skool_referrals": 0,
                    "member_communities": 0
                },
                "revenue": {
                    "community_monthly": 0,
                    "affiliate_monthly": 0,
                    "total_monthly": 0,
                    "total_lifetime": 0
                },
                "growth": []
            }
    
    def save_data(self):
        """Save data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def update_community(self, members, price):
        """Update community stats"""
        self.data["community"]["members"] = members
        self.data["community"]["price_per_month"] = price
        self.calculate_revenue()
        self.save_data()
    
    def update_affiliates(self, skool_refs, member_communities):
        """Update affiliate stats"""
        self.data["affiliates"]["skool_referrals"] = skool_refs
        self.data["affiliates"]["member_communities"] = member_communities
        self.calculate_revenue()
        self.save_data()
    
    def calculate_revenue(self):
        """Calculate all revenue streams"""
        # Community revenue
        community_revenue = (
            self.data["community"]["members"] * 
            self.data["community"]["price_per_month"]
        )
        
        # Affiliate revenue (40% of $99 Skool subscription)
        skool_affiliate = self.data["affiliates"]["skool_referrals"] * 39.60
        member_affiliate = self.data["affiliates"]["member_communities"] * 39.60
        total_affiliate = skool_affiliate + member_affiliate
        
        # Update revenue data
        self.data["revenue"]["community_monthly"] = community_revenue
        self.data["revenue"]["affiliate_monthly"] = total_affiliate
        self.data["revenue"]["total_monthly"] = community_revenue + total_affiliate
    
    def project_revenue(self, months=12):
        """Project future revenue based on growth"""
        projections = []
        
        # Current stats
        current_members = self.data["community"]["members"]
        current_price = self.data["community"]["price_per_month"]
        current_affiliates = self.data["affiliates"]["skool_referrals"]
        
        # Growth rates (conservative)
        member_growth_rate = 1.5  # 50% monthly growth
        affiliate_growth_rate = 1.3  # 30% monthly growth
        
        for month in range(1, months + 1):
            # Calculate projected numbers
            projected_members = int(current_members * (member_growth_rate ** month))
            projected_affiliates = int(current_affiliates * (affiliate_growth_rate ** month))
            
            # Calculate revenue
            community_rev = projected_members * current_price
            affiliate_rev = projected_affiliates * 39.60
            total_rev = community_rev + affiliate_rev
            
            projections.append({
                "month": month,
                "members": projected_members,
                "affiliates": projected_affiliates,
                "community_revenue": community_rev,
                "affiliate_revenue": affiliate_rev,
                "total_revenue": total_rev
            })
        
        return projections
    
    def display_dashboard(self):
        """Display revenue dashboard"""
        print("\n" + "="*60)
        print("💰 SKOOL REVENUE DASHBOARD 💰".center(60))
        print("="*60)
        
        print(f"\n📊 CURRENT STATS:")
        print(f"Community Members: {self.data['community']['members']}")
        print(f"Price per Month: ${self.data['community']['price_per_month']}")
        print(f"Skool Referrals: {self.data['affiliates']['skool_referrals']}")
        print(f"Member Communities: {self.data['affiliates']['member_communities']}")
        
        print(f"\n💵 MONTHLY REVENUE:")
        print(f"Community Revenue: ${self.data['revenue']['community_monthly']:,.2f}")
        print(f"Affiliate Revenue: ${self.data['revenue']['affiliate_monthly']:,.2f}")
        print(f"TOTAL MONTHLY: ${self.data['revenue']['total_monthly']:,.2f}")
        
        print(f"\n📈 12-MONTH PROJECTIONS:")
        projections = self.project_revenue(12)
        for p in [projections[2], projections[5], projections[11]]:  # Month 3, 6, 12
            print(f"Month {p['month']}: ${p['total_revenue']:,.2f} ({p['members']} members)")
        
        print(f"\n🎯 TO REACH $10K/MONTH:")
        members_needed = int(10000 / self.data['community']['price_per_month'])
        print(f"You need {members_needed} members at ${self.data['community']['price_per_month']}/month")
        print(f"OR {int(10000/39.60)} Skool referrals")
        print(f"OR a combination of both!")
        
        print("\n" + "="*60)

def interactive_update():
    """Interactive revenue update"""
    tracker = SkoolRevenueTracker()
    
    print("🚀 Skool Revenue Tracker")
    print("=" * 40)
    
    # Get current stats
    try:
        members = int(input("\nCurrent community members: "))
        price = float(input("Monthly price per member ($): "))
        skool_refs = int(input("Skool referrals (people using Skool): "))
        member_comms = int(input("Member-created communities: "))
        
        # Update tracker
        tracker.update_community(members, price)
        tracker.update_affiliates(skool_refs, member_comms)
        
        # Display dashboard
        tracker.display_dashboard()
        
        # Save growth data
        growth_entry = {
            "date": str(datetime.date.today()),
            "members": members,
            "revenue": tracker.data["revenue"]["total_monthly"]
        }
        tracker.data["growth"].append(growth_entry)
        tracker.save_data()
        
        print("\n✅ Revenue data updated and saved!")
        
    except ValueError:
        print("❌ Please enter valid numbers")

def quick_calculator():
    """Quick revenue calculator"""
    print("\n💰 SKOOL REVENUE CALCULATOR")
    print("=" * 40)
    
    try:
        members = int(input("How many members at what price?\nMembers: "))
        price = float(input("Price per month ($): "))
        
        community_revenue = members * price
        
        print(f"\n📊 REVENUE BREAKDOWN:")
        print(f"Community Revenue: ${community_revenue:,.2f}/month")
        print(f"Annual Revenue: ${community_revenue * 12:,.2f}")
        
        # Add affiliates
        affiliates = int(input("\nExpected Skool referrals: "))
        affiliate_revenue = affiliates * 39.60
        
        total_monthly = community_revenue + affiliate_revenue
        
        print(f"\n💵 TOTAL REVENUE:")
        print(f"Monthly: ${total_monthly:,.2f}")
        print(f"Annual: ${total_monthly * 12:,.2f}")
        
        print(f"\n🎯 AT THIS RATE:")
        print(f"$10k/month in {int(10000/total_monthly * members)} members")
        print(f"$100k/month in {int(100000/total_monthly * members)} members")
        
    except ValueError:
        print("❌ Please enter valid numbers")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "calc":
        quick_calculator()
    else:
        interactive_update()