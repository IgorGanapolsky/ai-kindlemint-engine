#!/usr/bin/env python3
"""
Integration helper for adding Sentry Agent Monitoring to existing scripts
"""

import os
import sys


def integrate_monitoring():
    """
    Guide for integrating Sentry Agent Monitoring into existing scripts
    """

    print("=== Sentry Agent Monitoring Integration Guide ===\n")

    print("1. Update your imports:")
    print("   Replace:")
    print("     from scripts.api_manager import APIManager")
    print("   With:")
    print("     from scripts.api_manager_enhanced import EnhancedAPIManager")
    print()

    print("2. Update initialization:")
    print("   Replace:")
    print("     api_manager = APIManager()")
    print("   With:")
    print("     api_manager = EnhancedAPIManager()")
    print()

    print("3. Add task names to API calls:")
    print("   Replace:")
    print("     api_manager.generate_text(prompt='...')")
    print("   With:")
    print("     api_manager.generate_text(prompt='...', task_name='descriptive_name')")
    print()

    print("4. For complex workflows, add monitoring context:")
    print(
        """
    from scripts.sentry_agent_monitoring import get_agent_monitor, AgentContext
    
    monitor = get_agent_monitor()
    context = AgentContext(
        agent_id="unique_id",
        agent_type="openai",
        task_name="your_workflow",
        model="gpt-4"
    )
    
    with monitor.start_agent(context) as transaction:
        # Your workflow code here
        pass
    """
    )

    print("\n5. Set environment variables:")
    print("   export SENTRY_DSN='your-sentry-dsn'")
    print("   export OPENAI_API_KEY='your-openai-key'")
    print()

    print("6. Install updated dependencies:")
    print("   pip install -r requirements.txt")
    print()

    print("=== Quick Integration Examples ===\n")

    # Show examples for common patterns in the codebase
    show_integration_examples()


def show_integration_examples():
    """Show specific integration examples for common patterns"""

    print("Example 1: Crossword Generation")
    print("-" * 40)
    print(
        """
# Before:
def generate_crossword_clues(word):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Generate clue for {word}"}]
    )
    return response.choices[0].message.content

# After:
def generate_crossword_clues(word):
    api_manager = EnhancedAPIManager()
    result = api_manager.generate_text(
        prompt=f"Generate clue for {word}",
        task_name=f"crossword_clue_{word}",
        model="gpt-4"
    )
    return result['text']
"""
    )

    print("\nExample 2: Batch Processing")
    print("-" * 40)
    print(
        """
# Before:
def process_multiple_prompts(prompts):
    results = []
    for prompt in prompts:
        response = openai.ChatCompletion.create(...)
        results.append(response)
    return results

# After:
def process_multiple_prompts(prompts):
    api_manager = EnhancedAPIManager()
    return api_manager.batch_generate(
        prompts=prompts,
        task_name="batch_processing"
    )
"""
    )

    print("\nExample 3: Error Handling")
    print("-" * 40)
    print(
        """
# Before:
try:
    response = openai.ChatCompletion.create(...)
except Exception as e:
    logger.error(f"OpenAI error: {e}")
    raise

# After:
try:
    result = api_manager.generate_text(
        prompt=prompt,
        task_name="my_task"
    )
except Exception as e:
    # Error automatically sent to Sentry with full context
    # Including prompts, tokens used, and workflow state
    raise
"""
    )


def check_environment():
    """Check if environment is properly configured"""
    print("\n=== Environment Check ===\n")

    checks = {
        "SENTRY_DSN": os.getenv("SENTRY_DSN"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
    }

    all_good = True
    for key, value in checks.items():
        if value:
            print(f"✅ {key}: Set")
        else:
            print(f"❌ {key}: Not set")
            all_good = False

    if all_good:
        print("\n✅ Environment is properly configured!")
    else:
        print("\n⚠️  Some environment variables are missing.")
        print("   Set them in your .env file or export them.")

    return all_good


def list_scripts_to_update():
    """List scripts that could benefit from monitoring"""
    print("\n=== Scripts That Could Use Monitoring ===\n")

    scripts_using_ai = [
        "scripts/batch_processor.py - Batch processing workflows",
        "scripts/crossword_engine_v3_fixed.py - Crossword generation",
        "scripts/generate_crossword_volume.py - Volume generation",
        "scripts/create_professional_crossword_pdf.py - PDF generation with AI",
        "scripts/enhanced_qa_validator.py - QA validation with AI",
        "scripts/market_research_csv_output.py - Market research with AI",
        "scripts/sentry_enhanced_market_research.py - Enhanced market research",
    ]

    print("Scripts that use AI and could benefit from monitoring:")
    for script in scripts_using_ai:
        print(f"  - {script}")

    print("\nTo update a script:")
    print("1. Import EnhancedAPIManager instead of APIManager")
    print("2. Add task_name to all AI calls")
    print("3. Optionally add workflow monitoring for complex operations")


if __name__ == "__main__":
    integrate_monitoring()
    check_environment()
    list_scripts_to_update()

    print("\n✅ Integration guide complete!")
    print("\nNext steps:")
    print("1. Set up your Sentry account at https://sentry.io")
    print("2. Get your DSN from Project Settings → Client Keys")
    print("3. Update your .env file with SENTRY_DSN")
    print("4. Run: python scripts/example_ai_workflow_monitoring.py")
    print("5. Check Sentry dashboard at Insights → Agents")
