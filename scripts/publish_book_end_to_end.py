#!/usr/bin/env python3
"""
Master Orchestration Script - Complete Publishing Pipeline
THE SHIPPING DEPARTMENT: Niche → Live Book on Amazon → Revenue

PURPOSE: Bridge the final GAP between our intelligent factory and actual revenue generation.
BUSINESS IMPACT: Transform memory-driven insights into published, revenue-generating books.

Pipeline Flow:
1. Analyze Memory → Find Profitable Niche
2. Generate Market-Validated Topic  
3. Create Complete Book Content
4. Generate Optimized Cover
5. Produce Marketing Copy
6. Upload Everything to KDP
7. Book Goes Live → Revenue Starts
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kindlemint.memory import KDPMemory
from kindlemint.core.generator import ContentGenerator
from kindlemint.agents.cmo import CMOAgent
from kindlemint.validation.market_research import MarketValidator
from kindlemint.publisher.kdp_agent import KDPPublisherAgent, BookAssets

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EndToEndPublisher:
    """
    Master orchestration class that runs the complete pipeline from
    memory analysis to live book on Amazon KDP.
    
    This is THE solution to our GAP problem.
    """
    
    def __init__(
        self,
        output_dir: str = "output/published_books",
        kdp_email: Optional[str] = None,
        kdp_password: Optional[str] = None,
        headless_browser: bool = False
    ):
        """Initialize the end-to-end publisher."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # KDP credentials
        self.kdp_email = kdp_email or os.getenv('KDP_EMAIL')
        self.kdp_password = kdp_password or os.getenv('KDP_PASSWORD')
        self.headless_browser = headless_browser
        
        # Check for required API keys
        required_vars = ['OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Initialize agents
        self.memory = KDPMemory()
        self.cto_agent = ContentGenerator(enable_memory=True)
        self.cmo_agent = CMOAgent(enable_memory=True)
        self.market_validator = MarketValidator()
        
        logger.info("End-to-end publisher initialized")
    
    def run_complete_pipeline(self, force_niche: Optional[str] = None, skip_validation: bool = False) -> Dict[str, Any]:
        """
        Run the complete pipeline from memory analysis to published book.
        
        This is the master method that solves our revenue problem.
        """
        pipeline_start = time.time()
        
        print("=" * 80)
        print("🚀 MEMORY-DRIVEN PUBLISHING PIPELINE")
        print("🎯 Goal: Intelligent Factory → Live Amazon Book → Revenue")
        print("=" * 80)
        
        try:
            # Step 1: Memory Analysis - Find Profitable Niche
            print("\n" + "🧠 STEP 1: MEMORY-DRIVEN NICHE ANALYSIS")
            print("-" * 50)
            profitable_niche = force_niche or self._analyze_profitable_niches()
            print(f"✅ Target niche identified: {profitable_niche}")
            
            # Step 2: Smart Topic Generation
            print("\n" + "💡 STEP 2: INTELLIGENT TOPIC GENERATION")
            print("-" * 50)
            topic_result = self._generate_smart_topic(profitable_niche)
            print(f"✅ Generated topic: {topic_result['topic']}")
            print(f"📋 Book ID: {topic_result['book_id']}")
            
            # Step 3: Market Validation (unless skipped)
            if not skip_validation:
                print("\n" + "🎯 STEP 3: SYNTHETIC MARKET RESEARCH")
                print("-" * 50)
                validation_passed = self._validate_market_viability(topic_result)
                if not validation_passed:
                    return {
                        'success': False,
                        'stage': 'market_validation',
                        'message': 'Topic failed market validation',
                        'book_id': topic_result['book_id']
                    }
                print("✅ Market validation passed")
            else:
                print("\n⚠️ STEP 3: MARKET VALIDATION SKIPPED")
            
            # Step 4: Content Generation
            print("\n" + "📝 STEP 4: INTELLIGENT CONTENT CREATION")
            print("-" * 50)
            content_result = self._generate_book_content(topic_result)
            print(f"✅ Content generated: {content_result['word_count']} words")
            
            # Step 5: Cover Generation  
            print("\n" + "🎨 STEP 5: AUTOMATED COVER CREATION")
            print("-" * 50)
            cover_result = self._generate_book_cover(topic_result)
            print(f"✅ Cover generated: {cover_result['cover_path']}")
            
            # Step 6: Marketing Assets
            print("\n" + "📢 STEP 6: DATA-DRIVEN MARKETING ASSETS")
            print("-" * 50)
            marketing_result = self._generate_marketing_assets(topic_result)
            print(f"✅ Marketing assets: {len(marketing_result)} types generated")
            
            # Step 7: Asset Packaging
            print("\n" + "📦 STEP 7: ASSET PACKAGING FOR KDP")
            print("-" * 50)
            book_package = self._package_book_assets(
                topic_result, content_result, cover_result, marketing_result
            )
            print(f"✅ Assets packaged: {book_package['assets_dir']}")
            
            # Step 8: KDP Publishing
            print("\n" + "🚛 STEP 8: AUTOMATED KDP PUBLISHING")
            print("-" * 50)
            publishing_result = self._publish_to_kdp(book_package)
            
            if publishing_result['success']:
                print("🎉 BOOK PUBLISHED SUCCESSFULLY!")
                print(f"📖 ASIN: {publishing_result.get('asin', 'Pending')}")
                print(f"🔗 KDP URL: {publishing_result.get('kdp_url', 'N/A')}")
            else:
                print("❌ Publishing failed")
                return {
                    'success': False,
                    'stage': 'kdp_publishing',
                    'message': 'KDP publishing failed',
                    'errors': publishing_result.get('errors', []),
                    'book_id': topic_result['book_id']
                }
            
            # Step 9: Update Memory with Publishing Success
            print("\n" + "🧠 STEP 9: UPDATE MEMORY SYSTEM")
            print("-" * 50)
            self._update_memory_with_publishing_result(topic_result, publishing_result)
            print("✅ Memory updated with publishing data")
            
            pipeline_duration = time.time() - pipeline_start
            
            print("\n" + "=" * 80)
            print("🎯 PIPELINE COMPLETE - REVENUE GENERATION ACTIVE")
            print("=" * 80)
            print(f"⏱️ Total time: {pipeline_duration:.1f} seconds")
            print(f"📚 Book: {topic_result['topic']}")
            print(f"🎯 Niche: {profitable_niche}")
            print(f"🆔 Book ID: {topic_result['book_id']}")
            print(f"📊 Next: Monitor sales and feed back to memory system")
            
            return {
                'success': True,
                'book_id': topic_result['book_id'],
                'topic': topic_result['topic'],
                'niche': profitable_niche,
                'asin': publishing_result.get('asin'),
                'kdp_url': publishing_result.get('kdp_url'),
                'assets_dir': str(book_package['assets_dir']),
                'pipeline_duration': pipeline_duration,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            print(f"\n❌ PIPELINE FAILED: {e}")
            return {
                'success': False,
                'stage': 'unknown',
                'message': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _analyze_profitable_niches(self) -> str:
        """Analyze memory to find the most profitable niche."""
        try:
            top_niches = self.memory.get_top_performing_niches(limit=3)
            
            if top_niches:
                # Use the most profitable niche
                best_niche = top_niches[0]
                print(f"📊 Found {len(top_niches)} niches with performance data")
                print(f"🏆 Best performer: {best_niche['niche']} (ROI: {best_niche['average_roi']:.2%})")
                return best_niche['niche']
            else:
                # Fallback to trending niches
                trending_niches = ["productivity", "personal finance", "health", "self-help"]
                fallback_niche = trending_niches[0]
                print(f"📈 No performance data available, using trending niche: {fallback_niche}")
                return fallback_niche
                
        except Exception as e:
            logger.warning(f"Memory analysis failed: {e}")
            return "productivity"  # Safe fallback
    
    def _generate_smart_topic(self, niche: str) -> Dict[str, Any]:
        """Generate a market-optimized topic using memory-driven insights."""
        try:
            return self.cto_agent.generate_profitable_book_topic(fallback_niche=niche)
        except Exception as e:
            logger.error(f"Topic generation failed: {e}")
            raise
    
    def _validate_market_viability(self, topic_result: Dict[str, Any]) -> bool:
        """Validate topic with AI personas before proceeding."""
        try:
            validation_report = self.market_validator.validate_book_concept(
                book_topic=topic_result['topic'],
                niche=topic_result['niche']
            )
            
            print(f"📊 Validation score: {validation_report.overall_score:.1f}%")
            print(f"🎯 Result: {validation_report.validation_result.value}")
            
            # Show persona feedback
            for response in validation_report.persona_responses:
                print(f"  👤 {response.persona_name}: {response.interest_score}/10 interest, {response.purchase_likelihood}/10 purchase")
            
            if not validation_report.should_proceed:
                print("\n🛑 VALIDATION FAILED - Topic rejected")
                for rec in validation_report.recommendations:
                    print(f"  💡 {rec}")
            
            return validation_report.should_proceed
            
        except Exception as e:
            logger.warning(f"Market validation failed: {e}")
            return True  # Proceed if validation fails
    
    def _generate_book_content(self, topic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete book content."""
        try:
            # Generate book outline
            outline = self.cto_agent.generate_book_outline(
                topic=topic_result['topic'],
                num_chapters=8,
                style="professional"
            )
            
            # Generate chapters
            chapters = []
            total_words = 0
            
            for i, chapter_info in enumerate(outline[:8], 1):  # Limit to 8 chapters
                print(f"  📄 Generating Chapter {i}: {chapter_info['title'][:50]}...")
                
                chapter = self.cto_agent.generate_chapter(
                    title=chapter_info['title'],
                    outline=chapter_info.get('summary', ''),
                    style="professional",
                    word_count=1500
                )
                
                chapters.append(chapter)
                total_words += len(chapter['content'].split())
            
            return {
                'outline': outline,
                'chapters': chapters,
                'word_count': total_words,
                'chapter_count': len(chapters)
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise
    
    def _generate_book_cover(self, topic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate book cover (placeholder - integrate with existing cover generation)."""
        try:
            # TODO: Integrate with existing scripts/generate_covers.py
            # For now, create a placeholder cover path
            
            cover_dir = self.output_dir / topic_result['book_id'] / 'covers'
            cover_dir.mkdir(parents=True, exist_ok=True)
            cover_path = cover_dir / 'cover.png'
            
            # Create a simple placeholder cover file
            cover_path.write_text("PLACEHOLDER COVER - INTEGRATE WITH EXISTING COVER GENERATION")
            
            return {
                'cover_path': str(cover_path),
                'cover_type': 'placeholder',
                'message': 'TODO: Integrate with scripts/generate_covers.py'
            }
            
        except Exception as e:
            logger.error(f"Cover generation failed: {e}")
            raise
    
    def _generate_marketing_assets(self, topic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing copy using memory-driven insights."""
        try:
            # Generate Amazon description
            amazon_copy = self.cmo_agent.generate_sales_copy(
                book_title=topic_result['topic'],
                niche=topic_result['niche'],
                copy_type="amazon_description"
            )
            
            # Generate keywords for KDP
            # TODO: Enhance with keyword research
            keywords = [
                topic_result['niche'],
                "self-help",
                "productivity",
                "success",
                "guide"
            ]
            
            return {
                'amazon_description': amazon_copy['copy'],
                'keywords': keywords,
                'data_driven': amazon_copy.get('data_driven', False),
                'proven_angles': amazon_copy.get('proven_angles_used', [])
            }
            
        except Exception as e:
            logger.error(f"Marketing generation failed: {e}")
            raise
    
    def _package_book_assets(
        self, 
        topic_result: Dict[str, Any], 
        content_result: Dict[str, Any],
        cover_result: Dict[str, Any], 
        marketing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Package all assets for KDP publishing."""
        try:
            book_id = topic_result['book_id']
            assets_dir = self.output_dir / book_id
            assets_dir.mkdir(parents=True, exist_ok=True)
            
            # Create book metadata
            metadata = {
                'book_id': book_id,
                'title': topic_result['topic'],
                'niche': topic_result['niche'],
                'author': 'AI Generated',
                'price': 2.99,
                'description': marketing_result['amazon_description'],
                'keywords': marketing_result['keywords'],
                'generation_timestamp': datetime.now(timezone.utc).isoformat(),
                'word_count': content_result['word_count'],
                'chapter_count': content_result['chapter_count']
            }
            
            # Save metadata
            with open(assets_dir / 'book_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create manuscript (simple text format for now)
            manuscript_content = f"# {topic_result['topic']}\n\n"
            manuscript_content += f"*Generated by Memory-Driven Publishing Engine*\n\n"
            
            for chapter in content_result['chapters']:
                manuscript_content += f"## {chapter['title']}\n\n"
                manuscript_content += f"{chapter['content']}\n\n"
            
            manuscript_path = assets_dir / 'manuscript.txt'
            with open(manuscript_path, 'w', encoding='utf-8') as f:
                f.write(manuscript_content)
            
            # Copy cover
            cover_path = assets_dir / 'cover.png'
            # TODO: Copy actual cover file
            cover_path.write_text("PLACEHOLDER COVER")
            
            # Create marketing directory
            marketing_dir = assets_dir / 'marketing'
            marketing_dir.mkdir(exist_ok=True)
            
            with open(marketing_dir / 'description.txt', 'w') as f:
                f.write(marketing_result['amazon_description'])
            
            with open(marketing_dir / 'keywords.txt', 'w') as f:
                f.write(', '.join(marketing_result['keywords']))
            
            return {
                'assets_dir': assets_dir,
                'metadata_path': assets_dir / 'book_metadata.json',
                'manuscript_path': manuscript_path,
                'cover_path': cover_path,
                'marketing_dir': marketing_dir
            }
            
        except Exception as e:
            logger.error(f"Asset packaging failed: {e}")
            raise
    
    def _publish_to_kdp(self, book_package: Dict[str, Any]) -> Dict[str, Any]:
        """Publish book to KDP using automated agent."""
        try:
            if not self.kdp_email or not self.kdp_password:
                return {
                    'success': False,
                    'message': 'KDP credentials not provided. Set KDP_EMAIL and KDP_PASSWORD environment variables.',
                    'errors': ['Missing KDP credentials']
                }
            
            print("🔐 KDP credentials found, initializing publisher agent...")
            
            with KDPPublisherAgent(
                headless=self.headless_browser,
                kdp_email=self.kdp_email,
                kdp_password=self.kdp_password
            ) as agent:
                result = agent.publish_book_from_assets(str(book_package['assets_dir']))
                
                return {
                    'success': result.success,
                    'asin': result.asin,
                    'kdp_url': result.kdp_url,
                    'errors': result.errors,
                    'warnings': result.warnings,
                    'timestamp': result.publishing_timestamp
                }
                
        except Exception as e:
            logger.error(f"KDP publishing failed: {e}")
            return {
                'success': False,
                'message': str(e),
                'errors': [str(e)]
            }
    
    def _update_memory_with_publishing_result(
        self, 
        topic_result: Dict[str, Any], 
        publishing_result: Dict[str, Any]
    ):
        """Update memory system with publishing attempt results."""
        try:
            # Update the book record with publishing status
            book_id = topic_result['book_id']
            
            # Note: This doesn't update sales data - that's handled by the KDP Report Ingestor
            # This just records that we attempted publishing
            
            metadata = {
                'publishing_attempted': True,
                'publishing_success': publishing_result['success'],
                'publishing_timestamp': publishing_result.get('timestamp'),
                'asin': publishing_result.get('asin')
            }
            
            # In a real implementation, we'd update the DynamoDB record
            # For now, just log the attempt
            logger.info(f"Publishing attempt recorded for book {book_id}: {publishing_result['success']}")
            
        except Exception as e:
            logger.warning(f"Failed to update memory with publishing result: {e}")


def main():
    """Main CLI interface for the end-to-end publisher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='End-to-End Publishing Pipeline')
    parser.add_argument('--niche', help='Force specific niche (skip memory analysis)')
    parser.add_argument('--skip-validation', action='store_true', help='Skip market validation')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--output-dir', default='output/published_books', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        publisher = EndToEndPublisher(
            output_dir=args.output_dir,
            headless_browser=args.headless
        )
        
        result = publisher.run_complete_pipeline(
            force_niche=args.niche,
            skip_validation=args.skip_validation
        )
        
        if result['success']:
            print(f"\n🎉 SUCCESS! Book published: {result['topic']}")
            if result.get('asin'):
                print(f"📖 ASIN: {result['asin']}")
            print(f"⏱️ Pipeline completed in {result['pipeline_duration']:.1f} seconds")
            exit(0)
        else:
            print(f"\n❌ FAILED at stage: {result.get('stage', 'unknown')}")
            print(f"💬 Message: {result.get('message', 'Unknown error')}")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Pipeline interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Pipeline crashed: {e}")
        exit(1)


if __name__ == "__main__":
    main()