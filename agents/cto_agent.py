"""
CTO Agent - Handles content creation and book generation
"""
import json
import time
from typing import Dict, Any
import google.generativeai as genai
import config
from utils.logger import MissionLogger
from utils.file_manager import FileManager

class CTOAgent:
    """CTO Agent responsible for content creation"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.logger = MissionLogger("CTO_Agent")
        self.file_manager = FileManager()
    
    def run_cto_tasks(self, topic: str) -> Dict[str, Any]:
        """Main CTO workflow"""
        start_time = time.time()
        self.logger.log_agent_start("CTO", f"Generating book content for '{topic}'")
        
        try:
            # Generate book outline
            self.logger.info("📖 Generating book outline...")
            outline = self._generate_book_outline(topic)
            
            # Generate chapters
            self.logger.info("📝 Generating chapter content...")
            chapters = self._generate_chapters(topic, outline)
            
            # Compile content
            content = {
                'topic': topic,
                'outline': outline,
                'chapters': chapters,
                'metadata': {
                    'generated_at': time.time(),
                    'total_chapters': len(chapters),
                    'estimated_word_count': sum(len(chapter.split()) for chapter in chapters)
                }
            }
            
            # Save content to multiple formats
            output_path = self.file_manager.save_book_content(topic, content)
            self.logger.log_file_operation("Save Book Content", output_path, "Success")
            
            # Generate .kpf file for KDP publishing
            kpf_path = self._generate_kpf_file(topic, outline, chapters)
            self.logger.log_file_operation("Save KPF File", kpf_path, "Success")
            
            duration = time.time() - start_time
            self.logger.log_agent_complete("CTO", f"Book generation for '{topic}'", duration)
            
            return {
                'success': True,
                'content': content,
                'output_path': output_path,
                'kpf_path': kpf_path,
                'duration': duration
            }
            
        except Exception as e:
            self.logger.log_agent_error("CTO", f"Book generation for '{topic}'", str(e))
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def _generate_book_outline(self, topic: str) -> Dict[str, Any]:
        """Generate book outline using OpenAI"""
        prompt = f"""
        Create a detailed book outline for a children's book titled: "{topic}"
        
        Please provide a JSON response with the following structure:
        {{
            "title": "Book Title",
            "target_age": "Age range (e.g., 6-10 years)",
            "genre": "Book genre",
            "summary": "Brief book summary",
            "chapters": [
                {{
                    "chapter_number": 1,
                    "title": "Chapter Title",
                    "summary": "Chapter summary",
                    "key_elements": ["element1", "element2"]
                }}
            ],
            "themes": ["theme1", "theme2"],
            "learning_objectives": ["objective1", "objective2"]
        }}
        
        Make it engaging, educational, and age-appropriate.
        """
        
        return self._make_gemini_request(prompt, "book outline")
    
    def _generate_chapters(self, topic: str, outline: Dict[str, Any]) -> list:
        """Generate chapter content based on outline"""
        chapters = []
        
        for chapter_info in outline.get('chapters', []):
            chapter_prompt = f"""
            Write a complete chapter for the children's book "{topic}".
            
            Chapter Details:
            - Number: {chapter_info.get('chapter_number', 1)}
            - Title: {chapter_info.get('title', 'Untitled')}
            - Summary: {chapter_info.get('summary', '')}
            - Key Elements: {', '.join(chapter_info.get('key_elements', []))}
            
            Book Context:
            - Target Age: {outline.get('target_age', '6-10 years')}
            - Themes: {', '.join(outline.get('themes', []))}
            
            Requirements:
            - Write in an engaging, age-appropriate style
            - Include dialogue and descriptive scenes
            - Aim for 800-1200 words
            - End with a hook for the next chapter (except final chapter)
            
            Please write the complete chapter content:
            """
            
            try:
                chapter_content = self._make_gemini_request(
                    chapter_prompt, 
                    f"chapter {chapter_info.get('chapter_number', 1)}",
                    json_response=False  # Plain text for chapters
                )
                chapters.append(chapter_content)
                self.logger.info(f"✅ Generated Chapter {chapter_info.get('chapter_number', len(chapters))}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to generate chapter {chapter_info.get('chapter_number', len(chapters) + 1)}: {e}")
                chapters.append(f"[Chapter content generation failed: {e}]")
        
        return chapters
    
    def _generate_kpf_file(self, topic: str, outline: Dict[str, Any], chapters: list) -> str:
        """Generate .kpf file for KDP publishing"""
        # Sanitize filename
        book_title = outline.get('title', topic)
        safe_title = book_title.replace(' ', '_').replace(':', '').replace("'", "").lower()
        kpf_path = f"./output/{safe_title}.kpf"
        
        # Create full book content in KPF format
        genre = outline.get('genre', "Children's Adventure")
        summary = outline.get('summary', 'An exciting adventure story for young readers.')
        themes = ', '.join(outline.get('themes', []))
        objectives = ', '.join(outline.get('learning_objectives', []))
        target_age = outline.get('target_age', '6-10 years')
        
        full_book_content = f"""TITLE: {book_title}
TARGET_AGE: {target_age}
GENRE: {genre}
AUTHOR: AI Mission Control
SUMMARY: {summary}

THEMES: {themes}
LEARNING_OBJECTIVES: {objectives}

==========================================
FULL BOOK CONTENT
==========================================

"""
        
        # Add each chapter
        for i, chapter in enumerate(chapters, 1):
            chapter_info = outline.get('chapters', [{}])[i-1] if i-1 < len(outline.get('chapters', [])) else {}
            chapter_title = chapter_info.get('title', f'Chapter {i}')
            
            full_book_content += f"""

CHAPTER {i}: {chapter_title}
{'=' * 50}

{chapter}

"""
        
        # Add publication metadata
        full_book_content += f"""

==========================================
PUBLICATION METADATA
==========================================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total Chapters: {len(chapters)}
Estimated Word Count: {sum(len(chapter.split()) for chapter in chapters)}
Ready for KDP Upload: YES
"""
        
        # Save KPF file
        with open(kpf_path, "w", encoding='utf-8') as f:
            f.write(full_book_content)
        
        return kpf_path
    
    def _make_gemini_request(self, prompt: str, task_name: str, json_response: bool = True) -> Any:
        """Make API request to Gemini with retry logic"""
        for attempt in range(config.MAX_RETRIES):
            try:
                self.logger.log_api_call("Gemini", f"generate_content ({task_name})", "Attempting")
                
                if json_response:
                    full_prompt = f"{prompt}\n\nIMPORTANT: Respond with valid JSON only. No markdown formatting, no code blocks, no additional text. Start directly with {{ and end with }}."
                else:
                    full_prompt = prompt
                
                response = self.model.generate_content(full_prompt)
                content = response.text.strip()
                
                # Clean up markdown formatting if present
                if json_response and content.startswith('```'):
                    lines = content.split('\n')
                    # Remove first and last lines if they contain ```
                    if lines[0].strip().startswith('```'):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]
                    content = '\n'.join(lines).strip()
                
                if json_response:
                    try:
                        result = json.loads(content)
                        self.logger.log_api_call("Gemini", f"generate_content ({task_name})", "Success (JSON)")
                        return result
                    except json.JSONDecodeError:
                        # Try to fix common issues with the JSON
                        content = content.replace('\\"', '"').replace("\\n", "")
                        result = json.loads(content)
                        self.logger.log_api_call("Gemini", f"generate_content ({task_name})", "Success (JSON - Fixed)")
                        return result
                else:
                    self.logger.log_api_call("Gemini", f"generate_content ({task_name})", "Success (Text)")
                    return content
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == config.MAX_RETRIES - 1:
                    raise Exception(f"Failed to parse JSON response after {config.MAX_RETRIES} attempts")
                
            except Exception as e:
                self.logger.warning(f"API request failed on attempt {attempt + 1}: {e}")
                if attempt == config.MAX_RETRIES - 1:
                    raise Exception(f"Gemini API request failed after {config.MAX_RETRIES} attempts: {e}")
                
                time.sleep(config.RETRY_DELAY * (attempt + 1))
        
        raise Exception("Unexpected error in Gemini request")
    
    def generate_standalone_content(self, topic: str, content_type: str) -> str:
        """Generate standalone content for specific purposes"""
        prompts = {
            'summary': f"Write a compelling 2-paragraph summary for the book '{topic}' suitable for marketing purposes.",
            'synopsis': f"Create a detailed synopsis for the children's book '{topic}' including main characters, plot, and key themes.",
            'character_descriptions': f"Describe the main characters in the book '{topic}' with their personalities, appearances, and roles in the story."
        }
        
        if content_type not in prompts:
            raise ValueError(f"Unknown content type: {content_type}")
        
        return self._make_gemini_request(
            prompts[content_type], 
            f"standalone {content_type}",
            json_response=False
        )
