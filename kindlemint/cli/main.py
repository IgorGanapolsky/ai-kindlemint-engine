"""Command-line interface for KindleMint Engine."""
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

from ..core.book import Book, BookContent
from ..core.generator import ContentGenerator
from ..core.publisher import KDPPublisher, KDPAuthenticationError, KDPPublishError
from ..utils.text_processing import clean_text, generate_slug

logger = logging.getLogger(__name__)

class KindleMintCLI:
    """Command-line interface for KindleMint Engine."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.parser = self._create_parser()
        self.args = None
        self.generator = None
        self.publisher = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="KindleMint Engine - Automate Your KDP Publishing Workflow",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Global arguments
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest="command",
            required=True,
            help="Command to execute"
        )
        
        # Generate command
        generate_parser = subparsers.add_parser(
            "generate",
            help="Generate book content"
        )
        generate_parser.add_argument(
            "topic",
            help="Book topic or title"
        )
        generate_parser.add_argument(
            "--output-dir",
            type=Path,
            default=Path("output"),
            help="Output directory for generated content"
        )
        generate_parser.add_argument(
            "--chapters",
            type=int,
            default=10,
            help="Number of chapters to generate"
        )
        generate_parser.add_argument(
            "--style",
            default="professional",
            help="Writing style (e.g., professional, conversational, academic)"
        )
        generate_parser.add_argument(
            "--words-per-chapter",
            type=int,
            default=1500,
            help="Target word count per chapter"
        )
        
        # Publish command
        publish_parser = subparsers.add_parser(
            "publish",
            help="Publish a book to KDP"
        )
        publish_parser.add_argument(
            "book_dir",
            type=Path,
            help="Directory containing book files (metadata.json, content/, cover.jpg)"
        )
        publish_parser.add_argument(
            "--draft",
            action="store_true",
            help="Save as draft instead of publishing immediately"
        )
        publish_parser.add_argument(
            "--email",
            help="KDP account email (or set KDP_EMAIL environment variable)"
        )
        publish_parser.add_argument(
            "--password",
            help="KDP account password (or set KDP_PASSWORD environment variable)"
        )
        
        # Config command
        config_parser = subparsers.add_parser(
            "config",
            help="Configure KindleMint"
        )
        config_parser.add_argument(
            "--set",
            nargs=2,
            metavar=("KEY", "VALUE"),
            help="Set a configuration value"
        )
        config_parser.add_argument(
            "--get",
            metavar="KEY",
            help="Get a configuration value"
        )
        
        return parser
    
    def run(self, args=None) -> int:
        """Run the CLI.
        
        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        self.args = self.parser.parse_args(args)
        
        # Configure logging
        log_level = logging.DEBUG if self.args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        try:
            # Initialize generator if needed
            if self.args.command == "generate":
                self.generator = ContentGenerator()
            
            # Route to appropriate command handler
            if self.args.command == "generate":
                return self.handle_generate()
            elif self.args.command == "publish":
                return self.handle_publish()
            elif self.args.command == "config":
                return self.handle_config()
            else:
                self.parser.print_help()
                return 1
                
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=self.args.verbose)
            return 1
    
    def handle_generate(self) -> int:
        """Handle the generate command."""
        output_dir = self.args.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating book about: {self.args.topic}")
        logger.info(f"Output directory: {output_dir.absolute()}")
        
        # Generate book outline
        logger.info("Generating book outline...")
        outline = self.generator.generate_book_outline(
            topic=self.args.topic,
            num_chapters=self.args.chapters,
            style=self.args.style
        )
        
        # Save outline
        outline_path = output_dir / "outline.json"
        with open(outline_path, 'w', encoding='utf-8') as f:
            json.dump(outline, f, indent=2, ensure_ascii=False)
        logger.info(f"Outline saved to: {outline_path}")
        
        # Generate content for each chapter
        book = Book(
            title=self.args.topic.title(),
            author="AI Author"  # Default author, can be customized
        )
        
        content_dir = output_dir / "content"
        content_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating {len(outline)} chapters...")
        for i, chapter in enumerate(outline, 1):
            chapter_title = chapter.get('title', f'Chapter {i}')
            logger.info(f"Generating chapter {i}: {chapter_title}")
            
            try:
                chapter_content = self.generator.generate_chapter(
                    title=chapter_title,
                    outline=chapter.get('summary', ''),
                    style=self.args.style,
                    word_count=self.args.words_per_chapter
                )
                
                # Save chapter to file
                chapter_slug = generate_slug(chapter_title)
                chapter_path = content_dir / f"chapter_{i:03d}_{chapter_slug}.md"
                with open(chapter_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {chapter_title}\n\n{chapter_content['content']}")
                
                # Add to book content
                book.content.add_chapter(chapter_title, chapter_content['content'])
                
            except Exception as e:
                logger.error(f"Error generating chapter {i}: {str(e)}")
                continue
        
        # Save book metadata
        metadata_path = output_dir / "metadata.json"
        book.save_metadata(metadata_path)
        logger.info(f"Book metadata saved to: {metadata_path}")
        
        logger.info(f"\n🎉 Book generation complete!")
        logger.info(f"Output directory: {output_dir.absolute()}")
        return 0
    
    def handle_publish(self) -> int:
        """Handle the publish command."""
        book_dir = self.args.book_dir
        if not book_dir.exists() or not book_dir.is_dir():
            logger.error(f"Book directory not found: {book_dir}")
            return 1
        
        # Load book metadata
        metadata_path = book_dir / "metadata.json"
        if not metadata_path.exists():
            logger.error(f"Metadata file not found: {metadata_path}")
            return 1
        
        try:
            # Initialize publisher
            self.publisher = KDPPublisher(
                email=self.args.email or os.getenv("KDP_EMAIL"),
                password=self.args.password or os.getenv("KDP_PASSWORD"),
                headless=not self.args.verbose
            )
            
            # Load book
            book = Book("Temporary Title", "Temporary Author")
            book.load_metadata(metadata_path)
            
            # Set manuscript and cover paths if they exist
            manuscript_path = book_dir / "manuscript.epub"  # or other formats
            if manuscript_path.exists():
                book.manuscript_path = manuscript_path
            
            cover_path = book_dir / "cover.jpg"  # or other image formats
            if cover_path.exists():
                book.set_cover(cover_path)
            
            # Login and publish
            logger.info("Logging in to KDP...")
            if not self.publisher.login():
                logger.error("Failed to log in to KDP")
                return 1
            
            logger.info(f"Publishing book: {book.title}")
            result = self.publisher.publish_book(book, draft=self.args.draft)
            
            if result.get('success'):
                logger.info(f"✅ Success! {result.get('message')}")
                if 'book_id' in result:
                    logger.info(f"Book ID: {result['book_id']}")
                return 0
            else:
                logger.error(f"Failed to publish book: {result.get('message', 'Unknown error')}")
                return 1
                
        except KDPAuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            return 1
        except KDPPublishError as e:
            logger.error(f"Publishing error: {str(e)}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=self.args.verbose)
            return 1
        finally:
            if self.publisher:
                self.publisher.close()
    
    def handle_config(self) -> int:
        """Handle the config command."""
        if self.args.set:
            key, value = self.args.set
            # In a real implementation, save this to a config file
            logger.info(f"Would set {key} = {value}")
            return 0
        elif self.args.get:
            # In a real implementation, read from config file
            logger.info(f"Would get value for {self.args.get}")
            return 0
        else:
            # Show current configuration
            logger.info("Current configuration:")
            # In a real implementation, show actual config
            logger.info("No configuration set (using defaults and environment variables)")
            return 0

def main():
    """Main entry point for the CLI."""
    cli = KindleMintCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()
