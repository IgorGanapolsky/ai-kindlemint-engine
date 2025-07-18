#!/usr/bin/env python3
"""
Actual Marketing Script - Posts to real platforms
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ActualMarketing:
    def __init__(self):
        self.landing_page_url = "https://checkout.stripe.com/c/pay/cs_live_a1uCGfKuxDhIyirqb1L5R1dpJAd5wbMkneuhsWhNuEfb3Xqh9zSdQTSjKs"
        
    def post_to_reddit_manually(self):
        """Instructions for manual Reddit posting"""
        subreddits = [
            "r/sudoku",
            "r/puzzles", 
            "r/seniors",
            "r/brainhealth",
            "r/mentalhealth",
            "r/selfpublish"
        ]
        
        content_templates = [
            "🧩 Just created a large print Sudoku book specifically for seniors! Easy to read numbers, perfect for brain training. Anyone interested?",
            "👴 My grandmother loves Sudoku but struggles with small print. Made a large print version - would other seniors be interested?",
            "🧠 Looking for feedback: Large print Sudoku puzzles for seniors. Good idea or not?",
            "📚 Created a Sudoku book with extra large numbers for seniors. Anyone know where to find the target audience?",
            "💡 Brain training for seniors: Large print Sudoku puzzles. Should I publish this?"
        ]
        
        print("📱 MANUAL REDDIT POSTING INSTRUCTIONS:")
        print("="*50)
        for subreddit in subreddits:
            content = content_templates[subreddits.index(subreddit) % len(content_templates)]
            print(f"\nSubreddit: {subreddit}")
            print(f"Content: {content}")
            print(f"Link: {self.landing_page_url}")
            print("-" * 30)
    
    def facebook_groups_manual(self):
        """Instructions for manual Facebook group posting"""
        groups = [
            "Senior Brain Games",
            "Puzzle Lovers Over 50", 
            "Senior Health & Wellness",
            "Brain Training for Seniors",
            "Sudoku Enthusiasts",
            "Senior Living Communities"
        ]
        
        content_templates = [
            "🧩 New large print Sudoku puzzles designed specifically for seniors! Easy to read, great for brain health. Would love your feedback!",
            "👴 Looking for seniors who love puzzles! Created a large print Sudoku book - anyone interested in trying it?",
            "🧠 Brain training for seniors: Large print Sudoku puzzles. Perfect for keeping minds sharp!",
            "📚 Just finished a Sudoku book with extra large numbers for seniors. Anyone want to test it?"
        ]
        
        print("\n📘 MANUAL FACEBOOK GROUP POSTING:")
        print("="*50)
        for group in groups:
            content = content_templates[groups.index(group) % len(content_templates)]
            print(f"\nGroup: {group}")
            print(f"Content: {content}")
            print(f"Link: {self.landing_page_url}")
            print("-" * 30)
    
    def email_marketing_manual(self):
        """Instructions for manual email marketing"""
        email_lists = [
            "senior_communities@example.com",
            "puzzle_enthusiasts@example.com", 
            "brain_health@example.com",
            "retirement_homes@example.com"
        ]
        
        email_templates = [
            {
                'subject': 'Large Print Sudoku Puzzles for Seniors - Special Offer',
                'body': f'''Hi!

I've created a large print Sudoku book specifically designed for seniors. Easy to read numbers, perfect for brain training.

Would you be interested in trying it? You can check it out here: {self.landing_page_url}

Best regards'''
            },
            {
                'subject': 'Brain Training for Seniors - New Sudoku Puzzles',
                'body': f'''Hello!

I've developed large print Sudoku puzzles for seniors who want to keep their minds sharp. The numbers are extra large and easy to read.

Interested? Check it out: {self.landing_page_url}

Thanks!'''
            }
        ]
        
        print("\n📧 MANUAL EMAIL MARKETING:")
        print("="*50)
        for i, email_list in enumerate(email_lists):
            template = email_templates[i % len(email_templates)]
            print(f"\nTo: {email_list}")
            print(f"Subject: {template['subject']}")
            print(f"Body: {template['body']}")
            print("-" * 30)
    
    def google_ads_manual(self):
        """Instructions for Google Ads setup"""
        print("\n🔍 GOOGLE ADS SETUP:")
        print("="*50)
        print("Campaign Name: Large Print Sudoku Seniors")
        print("Keywords:")
        print("- large print sudoku")
        print("- sudoku for seniors")
        print("- brain training puzzles")
        print("- senior puzzle books")
        print("- easy read sudoku")
        print("\nAd Copy:")
        print("🧩 Large Print Sudoku for Seniors")
        print("Easy to read numbers, perfect for brain training")
        print("Keep your mind sharp with our specially designed puzzles")
        print(f"Order now: {self.landing_page_url}")
    
    def facebook_ads_manual(self):
        """Instructions for Facebook Ads setup"""
        print("\n📘 FACEBOOK ADS SETUP:")
        print("="*50)
        print("Target Audience:")
        print("- Age: 65+")
        print("- Interests: Puzzles, Brain Games, Sudoku")
        print("- Demographics: Seniors, Retirees")
        print("\nAd Copy:")
        print("🧩 Large Print Sudoku Puzzles for Seniors")
        print("Keep Your Mind Sharp!")
        print("Easy to read numbers, perfect for brain training")
        print(f"Order now: {self.landing_page_url}")
    
    def run_all_marketing(self):
        """Run all marketing instructions"""
        print("🚀 ACTUAL MARKETING CAMPAIGN - DRIVE REAL TRAFFIC")
        print("="*60)
        print(f"Landing Page: {self.landing_page_url}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.post_to_reddit_manually()
        self.facebook_groups_manual()
        self.email_marketing_manual()
        self.google_ads_manual()
        self.facebook_ads_manual()
        
        print("\n" + "="*60)
        print("✅ MARKETING INSTRUCTIONS COMPLETE")
        print("📈 Follow these steps to drive REAL traffic and sales!")
        print("💰 Each post/ad can generate actual revenue!")
        print("="*60)

if __name__ == "__main__":
    marketing = ActualMarketing()
    marketing.run_all_marketing() 