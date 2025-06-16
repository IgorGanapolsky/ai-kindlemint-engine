#!/usr/bin/env python3
"""
Memory-Driven Publishing Engine Demo
Demonstrates the core functionality of the memory system and agents.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kindlemint.memory import KDPMemory
from kindlemint.core.generator import ContentGenerator
from kindlemint.agents.cmo import CMOAgent
from kindlemint.agents.cfo import CFOAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_memory_operations():
    """Demonstrate basic memory operations."""
    print("\n" + "="*60)
    print("MEMORY-DRIVEN PUBLISHING ENGINE DEMO")
    print("="*60)
    
    try:
        # Initialize memory system
        print("\n1. Initializing Memory System...")
        memory = KDPMemory()
        print("✓ Memory system connected to DynamoDB")
        
        # Store some sample book records
        print("\n2. Storing Sample Book Records...")
        sample_books = [
            {
                'book_id': 'productivity_book_001',
                'topic': 'The 5 AM Success Formula: Transform Your Life with Early Morning Habits',
                'niche': 'productivity',
                'metadata': {'generation_method': 'demo', 'author': 'AI Generated'}
            },
            {
                'book_id': 'finance_book_001', 
                'topic': 'Passive Income Mastery: 7 Proven Streams to Financial Freedom',
                'niche': 'personal finance',
                'metadata': {'generation_method': 'demo', 'author': 'AI Generated'}
            },
            {
                'book_id': 'health_book_001',
                'topic': 'The Metabolic Reset: 30-Day Plan to Boost Energy and Burn Fat',
                'niche': 'health',
                'metadata': {'generation_method': 'demo', 'author': 'AI Generated'}
            }
        ]
        
        for book in sample_books:
            success = memory.store_book_record(**book)
            if success:
                print(f"✓ Stored: {book['topic'][:50]}...")
            else:
                print(f"✗ Failed to store: {book['book_id']}")
        
        # Simulate some sales data
        print("\n3. Updating Sales Data...")
        sales_updates = [
            ('productivity_book_001', 25, 1250),  # 25 sales, 1250 pages read
            ('finance_book_001', 42, 2800),       # 42 sales, 2800 pages read  
            ('health_book_001', 18, 950),         # 18 sales, 950 pages read
        ]
        
        for book_id, sales, pages in sales_updates:
            success = memory.update_sales_data(book_id, sales, pages)
            if success:
                print(f"✓ Updated sales for {book_id}: {sales} sales, {pages} pages read")
        
        # Get top performing niches
        print("\n4. Analyzing Top Performing Niches...")
        top_niches = memory.get_top_performing_niches(limit=5)
        
        if top_niches:
            for i, niche_data in enumerate(top_niches, 1):
                print(f"{i}. {niche_data['niche'].title()}: "
                      f"ROI {niche_data['average_roi']:.2%}, "
                      f"{niche_data['book_count']} books")
        else:
            print("No niche performance data available yet")
        
        return memory, top_niches
        
    except Exception as e:
        print(f"✗ Memory demo failed: {e}")
        return None, []


def demo_cto_agent(memory):
    """Demonstrate CTO Agent memory-driven topic generation."""
    print("\n" + "="*60)
    print("CTO AGENT - MEMORY-DRIVEN TOPIC GENERATION")
    print("="*60)
    
    try:
        # Check if OpenAI API key is available
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠ OpenAI API key not found. Skipping CTO Agent demo.")
            print("Set OPENAI_API_KEY environment variable to test this feature.")
            return
        
        print("\n1. Initializing CTO Agent...")
        cto_agent = ContentGenerator(enable_memory=True)
        print("✓ CTO Agent initialized with memory system")
        
        print("\n2. Generating Memory-Driven Book Topic...")
        topic_result = cto_agent.generate_profitable_book_topic()
        
        print(f"✓ Generated Topic: {topic_result['topic']}")
        print(f"  Niche: {topic_result['niche']}")
        print(f"  Book ID: {topic_result['book_id']}")
        print(f"  Reasoning: {topic_result['reasoning']}")
        
        return topic_result
        
    except Exception as e:
        print(f"✗ CTO Agent demo failed: {e}")
        return None


def demo_cmo_agent():
    """Demonstrate CMO Agent memory-driven marketing."""
    print("\n" + "="*60)
    print("CMO AGENT - MEMORY-DRIVEN MARKETING")
    print("="*60)
    
    try:
        # Check if OpenAI API key is available
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠ OpenAI API key not found. Skipping CMO Agent demo.")
            print("Set OPENAI_API_KEY environment variable to test this feature.")
            return
        
        print("\n1. Initializing CMO Agent...")
        cmo_agent = CMOAgent(enable_memory=True)
        print("✓ CMO Agent initialized with memory system")
        
        print("\n2. Getting Niche Marketing Recommendations...")
        recommendations = cmo_agent.get_niche_recommendations(limit=3)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['niche'].title()}")
                print(f"   ROI: {rec['average_roi']:.2%}")
                print(f"   Books: {rec['book_count']}")
                print(f"   Best Approaches: {[a['approach'] for a in rec['best_marketing_approaches'][:2]]}")
        else:
            print("No marketing recommendations available yet")
        
        # Generate sample sales copy
        print("\n3. Generating Memory-Driven Sales Copy...")
        sample_copy = cmo_agent.generate_sales_copy(
            book_title="The 5 AM Success Formula",
            niche="productivity",
            copy_type="amazon_description"
        )
        
        print(f"✓ Generated Amazon Description:")
        print(f"Data-Driven: {sample_copy['data_driven']}")
        print(f"Proven Angles Used: {sample_copy['proven_angles_used']}")
        print("\nGenerated Copy:")
        print("-" * 40)
        print(sample_copy['copy'][:200] + "..." if len(sample_copy['copy']) > 200 else sample_copy['copy'])
        
        return sample_copy
        
    except Exception as e:
        print(f"✗ CMO Agent demo failed: {e}")
        return None


def demo_cfo_agent():
    """Demonstrate CFO Agent financial analysis."""
    print("\n" + "="*60)
    print("CFO AGENT - FINANCIAL ANALYSIS")
    print("="*60)
    
    try:
        print("\n1. Initializing CFO Agent...")
        cfo_agent = CFOAgent()
        print("✓ CFO Agent initialized")
        
        print("\n2. Generating Financial Report...")
        report = cfo_agent.generate_financial_report(days=30)
        
        if report['success']:
            print(f"✓ Financial Report Generated:")
            print(f"  Total Books: {report['total_books']}")
            print(f"  Total Sales: {report['total_sales']}")
            print(f"  Total Pages Read: {report['total_pages_read']}")
            print(f"  Average ROI: {report['average_roi']:.2%}")
            
            if report['top_performing_books']:
                print(f"\n  Top Performing Books:")
                for book in report['top_performing_books'][:3]:
                    print(f"  • {book['topic'][:40]}... (ROI: {book['roi']:.2%})")
        
        print("\n3. Identifying Profitable Opportunities...")
        opportunities = cfo_agent.identify_profitable_opportunities()
        
        if opportunities['success'] and opportunities['opportunities']:
            print("✓ Opportunities Identified:")
            for opp in opportunities['opportunities'][:3]:
                print(f"  • {opp['niche'].title()}: {opp['recommendation']}")
        
        return report, opportunities
        
    except Exception as e:
        print(f"✗ CFO Agent demo failed: {e}")
        return None, None


def main():
    """Run the complete Memory-Driven Publishing Engine demo."""
    print("🚀 Starting Memory-Driven Publishing Engine Demo...")
    
    # Demo 1: Memory Operations
    memory, top_niches = demo_memory_operations()
    
    if not memory:
        print("\n❌ Cannot continue without memory system. Please check DynamoDB setup.")
        return
    
    # Demo 2: CTO Agent
    demo_cto_agent(memory)
    
    # Demo 3: CMO Agent
    demo_cmo_agent()
    
    # Demo 4: CFO Agent
    demo_cfo_agent()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\n✅ Memory-Driven Publishing Engine is operational!")
    print("\nNext Steps:")
    print("1. Set up KDP report ingestion (CFO Agent)")
    print("2. Integrate with book generation pipeline")
    print("3. Set up automated publishing workflow")
    print("4. Monitor performance and optimize")


if __name__ == "__main__":
    main()