"""
File management utilities for Mission Control system
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import config

class FileManager:
    """Handles file operations for the Mission Control system"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_book_content(self, topic: str, content: Dict[str, Any]) -> str:
        """Save book content to organized files"""
        try:
            # Create topic-specific directory
            topic_dir = config.BOOK_OUTPUT_DIR / self._sanitize_filename(topic)
            topic_dir.mkdir(exist_ok=True)
            
            # Save outline
            outline_file = topic_dir / f"outline_{self.timestamp}.json"
            with open(outline_file, 'w', encoding='utf-8') as f:
                json.dump(content.get('outline', {}), f, indent=2, ensure_ascii=False)
            
            # Save chapters
            chapters_dir = topic_dir / "chapters"
            chapters_dir.mkdir(exist_ok=True)
            
            for i, chapter in enumerate(content.get('chapters', []), 1):
                chapter_file = chapters_dir / f"chapter_{i:02d}_{self.timestamp}.txt"
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    f.write(chapter)
            
            # Save summary file
            summary_file = topic_dir / f"summary_{self.timestamp}.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"Book Topic: {topic}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Total Chapters: {len(content.get('chapters', []))}\n")
                f.write(f"Files Location: {topic_dir}\n")
            
            return str(topic_dir)
            
        except Exception as e:
            raise Exception(f"Failed to save book content: {e}")
    
    def save_marketing_content(self, topic: str, content: Dict[str, Any]) -> str:
        """Save marketing content to organized files"""
        try:
            # Create topic-specific directory
            topic_dir = config.MARKETING_OUTPUT_DIR / self._sanitize_filename(topic)
            topic_dir.mkdir(exist_ok=True)
            
            # Save blog posts
            if 'blog_posts' in content:
                blog_dir = topic_dir / "blog_posts"
                blog_dir.mkdir(exist_ok=True)
                
                for i, post in enumerate(content['blog_posts'], 1):
                    post_file = blog_dir / f"blog_post_{i:02d}_{self.timestamp}.txt"
                    with open(post_file, 'w', encoding='utf-8') as f:
                        f.write(post)
            
            # Save social media posts
            if 'social_posts' in content:
                social_dir = topic_dir / "social_media"
                social_dir.mkdir(exist_ok=True)
                
                for platform, posts in content['social_posts'].items():
                    platform_file = social_dir / f"{platform}_{self.timestamp}.txt"
                    with open(platform_file, 'w', encoding='utf-8') as f:
                        for i, post in enumerate(posts, 1):
                            f.write(f"Post {i}:\n{post}\n\n---\n\n")
            
            # Save marketing strategy
            if 'strategy' in content:
                strategy_file = topic_dir / f"marketing_strategy_{self.timestamp}.txt"
                with open(strategy_file, 'w', encoding='utf-8') as f:
                    f.write(content['strategy'])
            
            return str(topic_dir)
            
        except Exception as e:
            raise Exception(f"Failed to save marketing content: {e}")
    
    def save_activity_log(self, activity: str, details: Dict[str, Any]) -> str:
        """Save activity log entry"""
        try:
            log_file = config.LOGS_OUTPUT_DIR / f"activity_log_{datetime.now().strftime('%Y%m%d')}.txt"
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'activity': activity,
                'details': details
            }
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(log_entry, indent=2)}\n")
                f.write("-" * 50 + "\n")
            
            return str(log_file)
            
        except Exception as e:
            raise Exception(f"Failed to save activity log: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system operations"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length and strip whitespace
        return filename.strip()[:100]
    
    def get_output_summary(self) -> Dict[str, Any]:
        """Get summary of all output files"""
        try:
            summary = {
                'books': [],
                'marketing': [],
                'logs': [],
                'total_files': 0
            }
            
            # Count book files
            if config.BOOK_OUTPUT_DIR.exists():
                for topic_dir in config.BOOK_OUTPUT_DIR.iterdir():
                    if topic_dir.is_dir():
                        file_count = sum(1 for _ in topic_dir.rglob('*') if _.is_file())
                        summary['books'].append({
                            'topic': topic_dir.name,
                            'files': file_count
                        })
                        summary['total_files'] += file_count
            
            # Count marketing files
            if config.MARKETING_OUTPUT_DIR.exists():
                for topic_dir in config.MARKETING_OUTPUT_DIR.iterdir():
                    if topic_dir.is_dir():
                        file_count = sum(1 for _ in topic_dir.rglob('*') if _.is_file())
                        summary['marketing'].append({
                            'topic': topic_dir.name,
                            'files': file_count
                        })
                        summary['total_files'] += file_count
            
            # Count log files
            if config.LOGS_OUTPUT_DIR.exists():
                log_files = [f.name for f in config.LOGS_OUTPUT_DIR.iterdir() if f.is_file()]
                summary['logs'] = log_files
                summary['total_files'] += len(log_files)
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
