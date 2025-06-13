"""
Basic usage example for KindleMint Engine.

This script demonstrates how to use the KindleMint library to generate a book
and prepare it for publishing on KDP.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Configuration
    book_topic = "The Future of Artificial Intelligence"
    output_dir = Path("output") / "example_book"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating book about: {book_topic}")
    
    try:
        # Initialize the content generator
        from kindlemint import ContentGenerator, Book
        
        generator = ContentGenerator()
        
        # Generate book outline
        logger.info("Generating book outline...")
        outline = generator.generate_book_outline(
            topic=book_topic,
            num_chapters=5,
            style="professional"
        )
        
        # Save outline
        outline_path = output_dir / "outline.json"
        with open(outline_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(outline, f, indent=2)
        logger.info(f"Outline saved to: {outline_path}")
        
        # Create a book instance
        book = Book(
            title=book_topic,
            author="AI Author"
        )
        
        # Generate chapters
        logger.info("Generating chapters...")
        chapters_dir = output_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        for i, chapter in enumerate(outline, 1):
            chapter_title = chapter.get('title', f'Chapter {i}')
            logger.info(f"Generating: {chapter_title}")
            
            # Generate chapter content
            chapter_content = generator.generate_chapter(
                title=chapter_title,
                outline=chapter.get('summary', ''),
                style="professional",
                word_count=1000
            )
            
            # Save chapter to file
            from kindlemint.utils.text_processing import generate_slug
            chapter_slug = generate_slug(chapter_title)
            chapter_path = chapters_dir / f"chapter_{i:02d}_{chapter_slug}.md"
            
            with open(chapter_path, 'w', encoding='utf-8') as f:
                f.write(f"# {chapter_title}\n\n{chapter_content['content']}")
            
            logger.info(f"  → Saved to: {chapter_path}")
            
            # Add chapter to book
            book.content.add_chapter(chapter_title, chapter_content['content'])
        
        # Save book metadata
        metadata_path = output_dir / "metadata.json"
        book.save_metadata(metadata_path)
        logger.info(f"Book metadata saved to: {metadata_path}")
        
        # Example of how to publish (commented out for safety)
        # Uncomment and fill in your KDP credentials to test publishing
        """
        from kindlemint import KDPPublisher
        
        publisher = KDPPublisher(
            email=os.getenv("KDP_EMAIL"),
            password=os.getenv("KDP_PASSWORD")
        )
        
        if publisher.login():
            result = publisher.publish_book(book, draft=True)
            if result.get('success'):
                logger.info(f"Book published successfully! Book ID: {result.get('book_id')}")
            else:
                logger.error(f"Failed to publish book: {result.get('message')}")
        else:
            logger.error("Failed to log in to KDP")
        """
        
        logger.info("\n🎉 Book generation complete!")
        logger.info(f"Output directory: {output_dir.absolute()}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
