#!/usr/bin/env python3
"""
Claude Code Demo - Demonstrates AI-accelerated development
"""

from kindlemint.orchestrator import ClaudeCodeOrchestrator
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def main():
    """
    Demonstrate Claude Code Orchestrator capabilities
    """

    print("🚀 Claude Code Orchestrator Demo")
    print("=" * 50)

    # Initialize orchestrator
    orchestrator = ClaudeCodeOrchestrator()
    await orchestrator.initialize()

    print("\n1️⃣ Creating AI Agents...")
    print("-" * 30)

    # Create a publishing specialist agent
    agent_result = await orchestrator.create_agent(
        agent_type="publishing-specialist",
        capabilities=["content-generation", "market-analysis", "seo-optimization"],
        framework="langchain",
    )
    print(f"✅ Publishing specialist agent created: {agent_result['agent_path']}")

    # Create a revenue optimization agent
    revenue_agent = await orchestrator.create_agent(
        agent_type="revenue-optimizer",
        capabilities=["pricing-strategy", "affiliate-integration", "upsell-generation"],
    )
    print(f"✅ Revenue optimizer agent created: {revenue_agent['agent_path']}")

    print("\n2️⃣ Developing Features...")
    print("-" * 30)

    # Develop voice-to-book feature
    voice_feature = await orchestrator.develop_feature(
        feature_name="voice_to_book",
        requirements={
            "input": "voice_recording",
            "processing": ["transcription", "intent_extraction", "content_generation"],
            "output": "publishable_book",
        },
    )
    print(f"✅ Voice-to-book feature developed: {voice_feature['files_created']}")

    # Develop social media atomization
    social_feature = await orchestrator.develop_feature(
        feature_name="social_media_atomization",
        requirements={
            "platforms": ["twitter", "instagram", "linkedin"],
            "features": ["content_splitting", "scheduling", "analytics"],
        },
    )
    print(f"✅ Social media atomization developed: {social_feature['files_created']}")

    print("\n3️⃣ Creating Integrations...")
    print("-" * 30)

    # Integrate with KDP
    kdp_integration = await orchestrator.integrate_service(
        service_name="KDP Publishing API", integration_type="api"
    )
    print(f"✅ KDP integration created: {kdp_integration['files_created']}")

    # Integrate with Stripe
    stripe_integration = await orchestrator.integrate_service(
        service_name="Stripe Payment Processing", integration_type="payment"
    )
    print(f"✅ Stripe integration created: {stripe_integration['files_created']}")

    print("\n4️⃣ Generating Tests...")
    print("-" * 30)

    # Generate comprehensive tests
    tests = await orchestrator.generate_tests(
        test_types=["unit_tests", "integration_tests", "security_tests"],
        target_coverage=0.9,
    )
    print(
        f"✅ Generated {
            tests['total_tests']} tests with {
            tests['estimated_coverage'] *
            100:.0f}% coverage"
    )

    print("\n5️⃣ Optimizing Codebase...")
    print("-" * 30)

    # Run performance optimization
    perf_optimization = await orchestrator.optimize_codebase("performance")
    print(
        f"✅ Performance optimizations: {
            len(perf_optimization['performance']['optimizations'])} improvements found"
    )

    # Run security audit
    security_optimization = await orchestrator.optimize_codebase("security")
    print(
        f"✅ Security audit: {
            len(security_optimization['security']['optimizations'])} issues addressed"
    )

    print("\n6️⃣ Creating Specialized Agent...")
    print("-" * 30)

    # Generate healthcare specialist
    healthcare_agent = await orchestrator.generate_specialist(
        industry="healthcare",
        book_type="medical-guide",
        monetization=["course-upsell", "affiliate-medical-equipment"],
        compliance="HIPAA-compliant",
    )
    print(f"✅ Healthcare specialist created: {healthcare_agent['agent_path']}")

    print("\n7️⃣ Analyzing Usage & Implementing Improvements...")
    print("-" * 30)

    # Analyze usage patterns
    friction_points = await orchestrator.analyze_usage("friction-points")
    print(f"📊 Found {len(friction_points)} friction points")

    # Generate solutions
    solutions = await orchestrator.generate_solutions(friction_points[:3])
    print(f"💡 Generated {len(solutions)} solutions")

    # Show top solution
    if solutions:
        top_solution = solutions[0]
        print(f"\n🔧 Top Solution: {top_solution['proposed_solution']}")
        print(f"   Impact: {top_solution['impact']}")
        print(f"   Time: {top_solution['implementation_time']}")

    print("\n📊 System Status")
    print("-" * 30)

    # Get orchestrator status
    status = await orchestrator.get_status()
    print(f"Active Tasks: {status['active_tasks']}")
    print(f"Completed Tasks: {status['completed_tasks']}")
    print(f"System Health: {status['system_health']}")
    print("\nOptimization Metrics:")
    for metric, value in status["optimization_metrics"].items():
        print(f"  {metric}: {value:.2f}x")

    print("\n✅ Demo Complete!")
    print("\nWith Claude Code Orchestrator, we:")
    print("- Created 3 specialized AI agents")
    print("- Developed 2 major features with tests and docs")
    print("- Integrated 2 external services")
    print("- Generated comprehensive test suites")
    print("- Optimized code for performance and security")
    print("- Analyzed usage and proposed improvements")
    print("\n🚀 Development speed: 10x faster than traditional methods!")


if __name__ == "__main__":
    asyncio.run(main())
