#!/usr/bin/env python3
"""
Skool Social Media Promoter
Generate viral content to promote your Skool community
"""
import json
from datetime import datetime
import secrets

class SkoolSocialPromoter:
    def __init__(self, community_name="AI Automation Academy", community_url="skool.com/your-community"):
        self.community_name = community_name
        self.community_url = community_url
        self.platforms = ["twitter", "linkedin", "reddit", "facebook", "instagram"]
    
    def generate_twitter_thread(self):
        """Generate a viral Twitter/X thread"""
        threads = [
            {
                "hook": "I went from $0 to $10k/month in 90 days.\n\nHere's the exact system I used (steal this):",
                "tweets": [
                    "1/ First, I joined a community of like-minded people.\n\nSurrounding yourself with winners changes everything.\n\nYour network = your net worth.",
                    "2/ I followed a PROVEN system.\n\nNo guessing. No trial and error.\n\nJust copy what works.",
                    "3/ Daily accountability was KEY.\n\nPosting wins, getting feedback, staying motivated.\n\nCommunity > Solo grinding.",
                    "4/ I focused on ONE thing until it worked.\n\nNo shiny object syndrome.\n\nMaster one skill, then scale.",
                    f"5/ Want the exact blueprint?\n\nI'm sharing everything inside {self.community_name}.\n\n{self.community_url}\n\n(First 20 members get 50% off)"
                ]
            },
            {
                "hook": "Most people will never make $10k/month.\n\nHere's why (brutal truth):",
                "tweets": [
                    "1/ They consume instead of create.\n\nWatching YouTube ≠ Taking action\n\nReading books ≠ Implementing",
                    "2/ They go it alone.\n\nNo mentors. No community. No support.\n\nPride kills more dreams than failure.",
                    "3/ They lack systems.\n\nRandom efforts = Random results\n\nSystems create predictable success.",
                    "4/ They quit too early.\n\nSuccess happens right after you want to quit.\n\nConsistency > Intensity",
                    f"5/ Ready to be different?\n\nJoin {self.community_name} and actually WIN.\n\n{self.community_url}\n\nYour future self will thank you."
                ]
            }
        ]
        
        thread = secrets.choice(threads)
        return {
            "platform": "Twitter/X",
            "content": thread,
            "hashtags": ["entrepreneur", "makemoneyonline", "business", "success"]
        }
    
    def generate_linkedin_post(self):
        """Generate a professional LinkedIn post"""
        templates = [
            f"""🚀 From Employee to $10k/Month Entrepreneur in 90 Days

3 months ago, I was stuck in a job I hated.

Today? I run a thriving {self.community_name.split()[0]} business.

Here's what changed everything:

✅ Joined a high-level community
✅ Followed a proven system  
✅ Took massive action daily
✅ Never looked back

The difference? 

ENVIRONMENT.

When you're surrounded by people making $10k-100k/month, your standards change.

Your mindset shifts.

Your results explode.

Want to make the leap?

Comment "READY" and I'll share the exact community that changed my life.

#Entrepreneurship #BusinessGrowth #FinancialFreedom #Success""",

            f"""📊 The $50k/Month Reality Check

Everyone wants financial freedom.

Few are willing to do what it takes.

Here's the truth:

• 95% consume content
• 4% take some action  
• 1% join elite communities and WIN

Which group are you in?

I help ambitious professionals build 6-figure businesses through {self.community_name}.

No fluff. No theory.

Just proven systems and daily support.

DM me "START" if you're ready to join the 1%.

#BusinessStrategy #Entrepreneurship #ProfessionalDevelopment #Success"""
        ]
        
        return {
            "platform": "LinkedIn",
            "content": secrets.choice(templates),
            "best_time": "Tuesday-Thursday, 7-9 AM or 5-6 PM"
        }
    
    def generate_reddit_post(self):
        """Generate a value-first Reddit post"""
        subreddits = [
            "r/Entrepreneur",
            "r/startups", 
            "r/business",
            "r/sidehustle",
            "r/passive_income"
        ]
        
        posts = [
            {
                "title": "How I Went From $0 to $10k/Month in 90 Days (Full Breakdown)",
                "content": f"""Hey everyone,

3 months ago I was completely broke. Today I'm consistently hitting $10k/month.

Here's exactly what I did:

**Month 1: Foundation**
- Joined a high-level community for accountability
- Picked ONE business model (not 5)
- Committed to 90 days no matter what

**Month 2: Implementation**
- Followed the exact system that was working for others
- Posted daily progress for accountability
- Got feedback from people already at $50k+/month

**Month 3: Scale**
- Doubled down on what worked
- Automated repetitive tasks
- Raised prices (this was huge)

**Key Lessons:**
1. Community > Courses
2. Implementation > Information
3. Consistency > Perfection

The biggest game-changer was joining a paid community. When everyone around you is crushing it, you have no choice but to level up.

Happy to answer any questions!

Edit: Since many are asking, the community is {self.community_name}. Feel free to check it out: {self.community_url}"""
            }
        ]
        
        post = secrets.choice(posts)
        return {
            "platform": "Reddit",
            "subreddit": secrets.choice(subreddits),
            "title": post["title"],
            "content": post["content"]
        }
    
    def generate_facebook_post(self):
        """Generate an engaging Facebook post"""
        posts = [
            f"""💰 LIFE UPDATE: Just hit $10k/month! 🎉

3 months ago:
- Broke
- Lost
- Stressed

Today:
- $10k/month
- Clear path
- Living my dream

What changed? I joined {self.community_name}.

Instead of watching YouTube videos alone, I connected with people actually making money.

We share wins. We solve problems together. We grow together.

If you're tired of going solo, comment "INFO" below 👇

#EntrepreneurLife #SuccessStory #CommunityPower #FinancialFreedom""",

            f"""🤔 "How do I start making money online?"

I get this question 10x per day.

Here's the truth:

❌ You don't need another course
❌ You don't need perfect timing
❌ You don't need tons of money

✅ You need a COMMUNITY

When I joined {self.community_name}, everything clicked.

→ Daily accountability
→ Proven systems
→ Real support

Now I'm at $10k/month and growing.

Want in? Drop a "🚀" below!"""
        ]
        
        return {
            "platform": "Facebook",
            "content": secrets.choice(posts),
            "groups": [
                "Entrepreneur Mindset",
                "Online Business Owners",
                "Digital Nomad Community",
                "Passive Income Ideas"
            ]
        }
    
    def generate_instagram_carousel(self):
        """Generate Instagram carousel content"""
        carousels = [
            {
                "title": "0 to $10K in 90 Days",
                "slides": [
                    "From BROKE to $10K/month\nin just 90 days\n\n(swipe for the exact steps →)",
                    "Step 1: Join a PAID Community\n\nFree = No commitment\nPaid = Serious players only",
                    "Step 2: Pick ONE Business Model\n\nStop chasing shiny objects\nMaster one thing first",
                    "Step 3: Follow the PROVEN System\n\nDon't reinvent the wheel\nCopy what works",
                    "Step 4: Post DAILY Progress\n\nAccountability = Success\nNo hiding allowed",
                    "Step 5: Scale What Works\n\nDouble down on winners\nCut the losers fast",
                    f"Ready to start YOUR journey?\n\nJoin {self.community_name}\n\nLink in bio 🔗"
                ]
            }
        ]
        
        carousel = secrets.choice(carousels)
        return {
            "platform": "Instagram",
            "type": "carousel",
            "content": carousel,
            "hashtags": [
                "#entrepreneur", "#businessowner", "#makemoneyonline",
                "#financialfreedom", "#successmindset", "#onlinebusiness",
                "#passiveincome", "#digitalnomad", "#sidehustle", "#motivation"
            ]
        }
    
    def generate_weekly_content(self):
        """Generate content for entire week"""
        weekly_plan = {
            "monday": self.generate_twitter_thread(),
            "tuesday": self.generate_linkedin_post(),
            "wednesday": self.generate_reddit_post(),
            "thursday": self.generate_facebook_post(),
            "friday": self.generate_instagram_carousel(),
            "saturday": self.generate_twitter_thread(),
            "sunday": {
                "platform": "All",
                "content": "Weekly recap + testimonial share",
                "note": "Share a success story from your community"
            }
        }
        
        return weekly_plan

def main():
    # Initialize promoter
    promoter = SkoolSocialPromoter(
        community_name="AI Automation Academy",
        community_url="skool.com/ai-automation-academy"
    )
    
    print("🚀 Skool Social Media Content Generator")
    print("=" * 50)
    
    # Generate weekly content
    weekly_content = promoter.generate_weekly_content()
    
    # Save to file
    with open("skool_social_content.json", "w") as f:
        json.dump(weekly_content, f, indent=2)
    
    print("✅ Generated social media content for the week!")
    print("📁 Saved to: skool_social_content.json")
    
    # Display preview
    print("\n📅 Content Calendar:")
    for day, content in weekly_content.items():
        print(f"\n{day.upper()}:")
        print(f"Platform: {content['platform']}")
        if 'content' in content:
            if isinstance(content['content'], dict):
                print(f"Type: {content['content'].get('hook', 'Carousel')[:50]}...")
            else:
                print(f"Preview: {content['content'][:100]}...")

if __name__ == "__main__":
    main()
