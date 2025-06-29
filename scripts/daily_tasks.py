#!/usr/bin/env python3
"""
Daily AI Publishing Task Scheduler
This script schedules and runs routine AI-powered publishing tasks.
"""
import time

import schedule


def check_sales():
    """Check overnight book sales"""
    print("[08:00] Checking overnight book sales...")
    try:
        from scripts.api_manager import APIManager, APIProvider

        prompt = (
            "Provide a summary of overnight book sales for my KDP portfolio, "
            "including top-selling titles and quantities sold."
        )
        ai = APIManager()
        report = ai.generate_text(prompt, provider=APIProvider.OPENAI)
        print(report)
    except Exception as e:
        print(f"Error during sales check: {e}")


def generate_social_posts():
    """Generate social media posts from top-selling book"""
    print("[09:00] Generating 3 social media posts from top book...")
    try:
        from scripts.api_manager import APIManager, APIProvider

        prompt = (
            "Generate three engaging social media posts promoting my top-selling KDP book, "
            "each with a unique hook and relevant hashtags."
        )
        ai = APIManager()
        posts = ai.generate_text(prompt, provider=APIProvider.OPENAI)
        print(posts)
    except Exception as e:
        print(f"Error generating social posts: {e}")


def research_trending_topics():
    """Research trending topics in the niche"""
    print("[10:00] Researching trending topics in niche...")
    try:
        from scripts.api_manager import APIManager, APIProvider

        prompt = "List the top five trending topics in the puzzle book niche on Amazon and social media."
        ai = APIManager()
        trends = ai.generate_text(prompt, provider=APIProvider.OPENAI)
        print(trends)
    except Exception as e:
        print(f"Error researching trending topics: {e}")


def create_chapter_outline():
    """Create chapter outline for next book"""
    print("[14:00] Creating chapter outline for tomorrow...")
    try:
        from scripts.api_manager import APIManager, APIProvider

        prompt = (
            "Create a detailed chapter outline for a book on improving daily routines with AI. "
            "Include section titles and brief descriptions."
        )
        ai = APIManager()
        outline = ai.generate_text(prompt, provider=APIProvider.OPENAI)
        print(outline)
    except Exception as e:
        print(f"Error creating chapter outline: {e}")


def analyze_competitors():
    """Analyze competitor new releases"""
    print("[16:00] Analyzing competitor new releases...")
    try:
        from scripts.api_manager import APIManager, APIProvider

        prompt = (
            "Analyze recent puzzle book releases by competitors on Amazon, "
            "highlighting their strengths, pricing, and sales rank."
        )
        ai = APIManager()
        analysis = ai.generate_text(prompt, provider=APIProvider.OPENAI)
        print(analysis)
    except Exception as e:
        print(f"Error analyzing competitors: {e}")


def schedule_marketing():
    """Schedule next day's marketing tasks"""
    print("[18:00] Scheduling next day's marketing tasks...")
    try:
        from scripts.api_manager import APIManager, APIProvider

        prompt = (
            "Generate a marketing task schedule for the next day to promote my KDP book, "
            "including social posts, email snippets, and ad ideas."
        )
        ai = APIManager()
        schedule_plan = ai.generate_text(prompt, provider=APIProvider.OPENAI)
        print(schedule_plan)
    except Exception as e:
        print(f"Error scheduling marketing tasks: {e}")


def run_daily_tasks():
    """Configure and run the daily task scheduler"""
    schedule.every().day.at("08:00").do(check_sales)
    schedule.every().day.at("09:00").do(generate_social_posts)
    schedule.every().day.at("10:00").do(research_trending_topics)
    schedule.every().day.at("14:00").do(create_chapter_outline)
    schedule.every().day.at("16:00").do(analyze_competitors)
    schedule.every().day.at("18:00").do(schedule_marketing)

    print("Starting daily AI publishing task scheduler...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Daily task scheduler stopped.")


if __name__ == "__main__":
    run_daily_tasks()
