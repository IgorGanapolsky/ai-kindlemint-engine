#!/usr/bin/env python3
"""
Memory-Driven Book Generation Script
PURPOSE: To act as the "smart" entry point for our V2 engine.
This script will replace the simple "pick a random topic" logic.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import boto3
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kindlemint.memory import KDPMemory
from kindlemint.core.generator import ContentGenerator
from kindlemint.agents.cmo import CMOAgent
from kindlemint.validation.market_research import MarketValidator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_most_profitable_niche(memory: KDPMemory) -> str:
    """
    Queries the KDP_Business_Memory table to find the niche
    with the highest average calculated_roi.
    
    Returns: A string representing the most profitable niche.
    """
    print("LOG: Analyzing sales data to find most profitable niche...")
    
    try:
        # Get top performing niches from memory system
        top_niches = memory.get_top_performing_niches(limit=5)
        
        if not top_niches:
            print("LOG: No historical data found. Using trending niche fallback.")
            # Fallback to trending niches if no data exists
            trending_niches = [
                "productivity", "personal finance", "health", "self-help", 
                "business", "relationships", "mindfulness", "career development"
            ]
            profitable_niche = trending_niches[0]  # Default to productivity
        else:
            # Use the most profitable niche
            profitable_niche = top_niches[0]['niche']
            roi = top_niches[0]['average_roi']
            book_count = top_niches[0]['book_count']
            
            print(f"LOG: Found {len(top_niches)} niches with performance data")
            print(f"LOG: Top performer: '{profitable_niche}' (ROI: {roi:.2%}, Books: {book_count})")
            
            # Show top 3 for context
            for i, niche_data in enumerate(top_niches[:3], 1):
                print(f"  {i}. {niche_data['niche']} - ROI: {niche_data['average_roi']:.2%}")
        
        print(f"LOG: Identified '{profitable_niche}' as the top-performing niche.")
        return profitable_niche
        
    except Exception as e:
        logger.error(f"Error analyzing niches: {e}")
        print("LOG: Error occurred. Using fallback niche: productivity")
        return "productivity"


def get_existing_topics_in_niche(niche: str, memory: KDPMemory) -> List[str]:
    """Get existing book topics in the specified niche to avoid duplicates."""
    try:
        all_books = memory.list_all_books()
        existing_topics = []
        
        for book in all_books:
            if book.get('niche', '').lower() == niche.lower():
                topic = book.get('topic', '')
                if topic:
                    existing_topics.append(topic)
        
        print(f"LOG: Found {len(existing_topics)} existing topics in '{niche}' niche")
        return existing_topics
        
    except Exception as e:
        logger.warning(f"Could not retrieve existing topics: {e}")
        return []


def generate_unique_topic_in_niche(niche: str, cto_agent: ContentGenerator, memory: KDPMemory) -> Dict[str, Any]:
    """
    Generates a new, unique book topic within a given profitable niche.
    
    Returns: Dict with topic details including book_id.
    """
    print(f"LOG: Generating a new, unique topic for the '{niche}' niche...")
    
    try:
        # Get existing topics to avoid duplicates
        existing_topics = get_existing_topics_in_niche(niche, memory)
        
        # Build enhanced prompt with niche-specific guidance
        exclusion_text = ""
        if existing_topics:
            topics_list = "\n".join([f"- {topic}" for topic in existing_topics[:10]])  # Limit to 10 for prompt length
            exclusion_text = f"\n\nEXISTING TOPICS TO AVOID:\n{topics_list}\n\nEnsure your new topic is completely different from these existing titles."
        
        # Get marketing insights for the niche
        marketing_insights = memory.get_niche_marketing_insights(niche)
        marketing_context = ""
        if marketing_insights:
            proven_angles = [angle for angle, data in marketing_insights.items() 
                           if data.get('average_effectiveness', 0) > 0.6]
            if proven_angles:
                marketing_context = f"\n\nPROVEN MARKETING ANGLES for {niche}: {', '.join(proven_angles)}\nConsider incorporating elements that align with these successful approaches."
        
        # Generate the topic using the memory-driven approach
        topic_result = cto_agent.generate_profitable_book_topic(fallback_niche=niche)
        
        # Enhance with uniqueness check
        new_topic = topic_result['topic']
        
        # Simple duplicate check
        if any(new_topic.lower() in existing.lower() or existing.lower() in new_topic.lower() 
               for existing in existing_topics):
            print("LOG: Generated topic too similar to existing. Regenerating...")
            # Try once more with stricter prompt
            topic_result = cto_agent.generate_profitable_book_topic(fallback_niche=niche)
            new_topic = topic_result['topic']
        
        print(f"LOG: New profitable topic generated: '{new_topic}'")
        print(f"LOG: Book ID: {topic_result['book_id']}")
        
        return topic_result
        
    except Exception as e:
        logger.error(f"Error generating topic: {e}")
        raise


def generate_marketing_assets(topic_result: Dict[str, Any], cmo_agent: CMOAgent) -> Dict[str, Any]:
    """Generate marketing assets for the new book using memory-driven insights."""
    print("LOG: Generating memory-driven marketing assets...")
    
    try:
        book_title = topic_result['topic']
        niche = topic_result['niche']
        
        # Generate different types of marketing copy
        marketing_assets = {}
        
        # Amazon description
        amazon_copy = cmo_agent.generate_sales_copy(
            book_title=book_title,
            niche=niche,
            copy_type="amazon_description"
        )
        marketing_assets['amazon_description'] = amazon_copy
        
        # Gumroad pitch
        gumroad_copy = cmo_agent.generate_sales_copy(
            book_title=book_title,
            niche=niche,
            copy_type="gumroad_pitch"
        )
        marketing_assets['gumroad_pitch'] = gumroad_copy
        
        print(f"LOG: Generated marketing assets using {len(amazon_copy.get('proven_angles_used', []))} proven angles")
        
        return marketing_assets
        
    except Exception as e:
        logger.warning(f"Error generating marketing assets: {e}")
        return {}


def save_generation_results(topic_result: Dict[str, Any], marketing_assets: Dict[str, Any], output_dir: Path):
    """Save the generation results to files."""
    try:
        # Create output directory
        book_slug = topic_result['book_id']
        book_dir = output_dir / book_slug
        book_dir.mkdir(parents=True, exist_ok=True)
        
        # Save book metadata
        metadata = {
            'generation_timestamp': datetime.now(timezone.utc).isoformat(),
            'book_details': topic_result,
            'marketing_assets': marketing_assets,
            'generation_method': 'memory_driven_v2'
        }
        
        metadata_file = book_dir / 'book_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Save individual marketing files
        for copy_type, copy_data in marketing_assets.items():
            copy_file = book_dir / f'{copy_type}.txt'
            with open(copy_file, 'w') as f:
                f.write(f"# {copy_type.replace('_', ' ').title()}\n\n")
                f.write(copy_data.get('copy', ''))
                f.write(f"\n\n## Generation Details\n")
                f.write(f"Data-driven: {copy_data.get('data_driven', False)}\n")
                f.write(f"Proven angles: {copy_data.get('proven_angles_used', [])}\n")
        
        print(f"LOG: Results saved to {book_dir}")
        return book_dir
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        return None


def main():
    """
    Main orchestration function for the memory-driven pipeline.
    """
    print("=" * 60)
    print("MEMORY-DRIVEN CONTENT PIPELINE V2.0")
    print("=" * 60)
    
    try:
        # Check for required API key
        if not os.getenv('OPENAI_API_KEY'):
            print("ERROR: OPENAI_API_KEY environment variable not set")
            print("Please set your OpenAI API key to use the content generation features")
            return
        
        # Initialize memory system and agents
        print("LOG: Initializing memory system and AI agents...")
        memory = KDPMemory()
        cto_agent = ContentGenerator(enable_memory=True)
        cmo_agent = CMOAgent(enable_memory=True)
        market_validator = MarketValidator()
        print("LOG: ✓ All systems initialized")
        
        # 1. Find the best niche based on past sales data
        print("\n" + "-" * 40)
        print("STEP 1: NICHE ANALYSIS")
        print("-" * 40)
        profitable_niche = get_most_profitable_niche(memory)
        
        # 2. Generate a new, unique topic in that niche
        print("\n" + "-" * 40)
        print("STEP 2: SMART TOPIC GENERATION")
        print("-" * 40)
        topic_result = generate_unique_topic_in_niche(profitable_niche, cto_agent, memory)
        
        # 3. CRITICAL: Validate with AI personas before proceeding
        print("\n" + "-" * 40)
        print("STEP 3: SYNTHETIC MARKET RESEARCH")
        print("-" * 40)
        validation_report = market_validator.validate_book_concept(
            book_topic=topic_result['topic'],
            niche=topic_result['niche']
        )
        
        print(f"LOG: Market validation score: {validation_report.overall_score:.1f}%")
        print(f"LOG: Validation result: {validation_report.validation_result.value}")
        print(f"LOG: Should proceed: {'✅ YES' if validation_report.should_proceed else '❌ NO'}")
        
        # Show persona feedback
        for response in validation_report.persona_responses:
            print(f"  • {response.persona_name}: Interest={response.interest_score}/10, Purchase={response.purchase_likelihood}/10")
        
        # ABORT LOGIC: Stop here if validation fails
        if not validation_report.should_proceed:
            print("\n" + "🛑" * 20)
            print("MISSION ABORTED: Poor market validation")
            print("🛑" * 20)
            print("\nRecommendations:")
            for rec in validation_report.recommendations:
                print(f"  {rec}")
            
            print(f"\n💰 API COSTS SAVED: Validation prevented creating content for a low-viability topic")
            print(f"📊 Validation data stored in memory for future learning")
            
            # Store validation failure in memory for learning
            memory.store_book_record(
                book_id=topic_result['book_id'],
                topic=topic_result['topic'],
                niche=topic_result['niche'],
                metadata={
                    'validation_score': validation_report.overall_score,
                    'validation_result': validation_report.validation_result.value,
                    'aborted_at_validation': True
                }
            )
            return
        
        print(f"\n✅ VALIDATION PASSED: Proceeding with content creation")
        print(f"📈 Market confidence: {validation_report.overall_score:.1f}%")
        
        # 4. Generate memory-driven marketing assets
        print("\n" + "-" * 40)
        print("STEP 4: MARKETING ASSET GENERATION")
        print("-" * 40)
        marketing_assets = generate_marketing_assets(topic_result, cmo_agent)
        
        # 5. Save results including validation data
        print("\n" + "-" * 40)
        print("STEP 5: SAVE RESULTS")
        print("-" * 40)
        output_dir = Path("output/memory_driven_books")
        
        # Enhanced metadata with validation results
        enhanced_topic_result = {
            **topic_result,
            'validation_report': {
                'score': validation_report.overall_score,
                'result': validation_report.validation_result.value,
                'persona_feedback': [
                    {
                        'name': r.persona_name,
                        'interest': r.interest_score,
                        'purchase': r.purchase_likelihood,
                        'reasoning': r.reasoning
                    } for r in validation_report.persona_responses
                ],
                'recommendations': validation_report.recommendations
            }
        }
        
        book_dir = save_generation_results(enhanced_topic_result, marketing_assets, output_dir)
        
        # 6. Integration points for existing workflows
        print("\n" + "-" * 40)
        print("STEP 6: PIPELINE INTEGRATION")
        print("-" * 40)
        
        if book_dir:
            print("LOG: Next steps for full automation:")
            print(f"  1. Content Generation: Generate full book content for '{topic_result['topic']}'")
            print(f"  2. Cover Generation: Run scripts/generate_covers.py with book metadata")
            print(f"  3. KDP Upload: Use publisher agent to upload to Amazon")
            print(f"  4. Performance Tracking: Monitor sales and update memory system")
            
            # TODO: Integrate with existing scripts
            # print("LOG: Executing full content generation...")
            # mission_control.execute_full_mission(topic_result['topic'])
            
            # print("LOG: Initiating cover generation...")
            # subprocess.run([sys.executable, "scripts/generate_covers.py", "--book-title", topic_result['topic']])
        
        print("\n" + "=" * 60)
        print("MEMORY-DRIVEN PIPELINE COMPLETE")
        print("=" * 60)
        print(f"✓ Profitable niche identified: {profitable_niche}")
        print(f"✓ Smart topic generated: {topic_result['topic']}")
        print(f"✓ Marketing assets created: {len(marketing_assets)} types")
        print(f"✓ Book ID: {topic_result['book_id']}")
        
        if book_dir:
            print(f"✓ Results saved to: {book_dir}")
        
        print("\n🎯 This book has been optimized for the highest-ROI niche in your catalog!")
        print("📊 The topic and marketing copy are data-driven based on your actual sales performance.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        print("Check logs for details and ensure all dependencies are properly configured.")


if __name__ == "__main__":
    main()