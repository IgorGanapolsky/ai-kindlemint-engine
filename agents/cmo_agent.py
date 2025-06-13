"""
CMO Agent - Handles marketing content creation and distribution
"""
import json
import time
import requests
from typing import Dict, Any, List
import google.generativeai as genai
import config
from utils.logger import MissionLogger
from utils.file_manager import FileManager

class CMOAgent:
    """CMO Agent responsible for marketing content creation and distribution"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.logger = MissionLogger("CMO_Agent")
        self.file_manager = FileManager()
    
    def run_cmo_tasks(self, topic: str) -> Dict[str, Any]:
        """Main CMO workflow"""
        start_time = time.time()
        self.logger.log_agent_start("CMO", f"Generating marketing content for '{topic}'")
        
        try:
            # Generate marketing strategy
            self.logger.info("📊 Generating marketing strategy...")
            strategy = self._generate_marketing_strategy(topic)
            
            # Generate blog posts
            self.logger.info("📝 Generating blog posts...")
            blog_posts = self._generate_blog_posts(topic, strategy)
            
            # Generate social media content
            self.logger.info("📱 Generating social media content...")
            social_posts = self._generate_social_media_content(topic, strategy)
            
            # Compile marketing content
            content = {
                'topic': topic,
                'strategy': strategy,
                'blog_posts': blog_posts,
                'social_posts': social_posts,
                'metadata': {
                    'generated_at': time.time(),
                    'total_blog_posts': len(blog_posts),
                    'social_platforms': list(social_posts.keys())
                }
            }
            
            # Save content
            output_path = self.file_manager.save_marketing_content(topic, content)
            self.logger.log_file_operation("Save Marketing Content", output_path, "Success")
            
            # Attempt to distribute content (if APIs are configured)
            distribution_results = self._distribute_content(content)
            
            duration = time.time() - start_time
            self.logger.log_agent_complete("CMO", f"Marketing content for '{topic}'", duration)
            
            return {
                'success': True,
                'content': content,
                'output_path': output_path,
                'distribution_results': distribution_results,
                'duration': duration
            }
            
        except Exception as e:
            self.logger.log_agent_error("CMO", f"Marketing content for '{topic}'", str(e))
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def _generate_marketing_strategy(self, topic: str) -> str:
        """Generate comprehensive marketing strategy"""
        prompt = f"""
        Create a comprehensive marketing strategy for the children's book "{topic}".
        
        Include the following sections:
        1. Target Audience Analysis
        2. Key Marketing Messages
        3. Content Marketing Approach
        4. Social Media Strategy
        5. Launch Timeline
        6. Success Metrics
        7. Budget Considerations
        8. Partnership Opportunities
        
        Make it practical and actionable for a children's book launch.
        """
        
        return self._make_gemini_request(prompt, "marketing strategy", json_response=False)
    
    def _generate_blog_posts(self, topic: str, strategy: str) -> List[str]:
        """Generate blog posts for content marketing"""
        blog_topics = [
            f"The Inspiration Behind '{topic}': A Journey into Children's Literature",
            f"Why '{topic}' is Perfect for Young Readers: Educational Benefits and Fun",
            f"Behind the Scenes: Creating '{topic}' - The Writing Process",
            f"Reading Together: How '{topic}' Brings Families Closer",
            f"The Magic of Adventure: What Makes '{topic}' Special"
        ]
        
        blog_posts = []
        
        for blog_topic in blog_topics:
            prompt = f"""
            Write a engaging blog post with the title: "{blog_topic}"
            
            Context: This is for promoting the children's book "{topic}"
            Marketing Strategy Context: {strategy[:500]}...
            
            Requirements:
            - 800-1000 words
            - Engaging and informative tone
            - Include call-to-action
            - SEO-friendly
            - Appeal to parents and educators
            - Include relevant keywords naturally
            
            Please write the complete blog post:
            """
            
            try:
                blog_post = self._make_gemini_request(prompt, f"blog post", json_response=False)
                blog_posts.append(blog_post)
                self.logger.info(f"✅ Generated blog post: {blog_topic[:50]}...")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to generate blog post '{blog_topic}': {e}")
                blog_posts.append(f"[Blog post generation failed: {e}]")
        
        return blog_posts
    
    def _generate_social_media_content(self, topic: str, strategy: str) -> Dict[str, List[str]]:
        """Generate social media content for different platforms"""
        platforms = {
            'twitter': {
                'char_limit': 280,
                'post_count': 10,
                'style': 'concise, engaging with hashtags'
            },
            'facebook': {
                'char_limit': 500,
                'post_count': 8,
                'style': 'friendly, community-focused'
            },
            'instagram': {
                'char_limit': 300,
                'post_count': 8,
                'style': 'visual-focused, inspiring with hashtags'
            },
            'linkedin': {
                'char_limit': 400,
                'post_count': 5,
                'style': 'professional, educational value'
            }
        }
        
        social_posts = {}
        
        for platform, config_data in platforms.items():
            prompt = f"""
            Create {config_data['post_count']} social media posts for {platform.capitalize()} to promote the children's book "{topic}".
            
            Platform Guidelines:
            - Character limit: {config_data['char_limit']}
            - Style: {config_data['style']}
            
            Marketing Context: {strategy[:300]}...
            
            Please provide the posts in JSON format:
            {{
                "posts": [
                    "Post 1 content...",
                    "Post 2 content...",
                    ...
                ]
            }}
            
            Make each post unique, engaging, and platform-appropriate.
            """
            
            try:
                response = self._make_gemini_request(prompt, f"{platform} posts")
                posts = response.get('posts', [])
                social_posts[platform] = posts
                self.logger.info(f"✅ Generated {len(posts)} posts for {platform.capitalize()}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to generate {platform} posts: {e}")
                social_posts[platform] = [f"[{platform} post generation failed: {e}]"]
        
        return social_posts
    
    def _distribute_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to distribute content to various platforms"""
        distribution_results = {
            'wordpress': {'status': 'skipped', 'reason': 'API not configured'},
            'buffer': {'status': 'skipped', 'reason': 'API not configured'},
            'attempted': False
        }
        
        # WordPress distribution
        if config.WORDPRESS_API_URL and config.WORDPRESS_USERNAME:
            try:
                self.logger.info("🌐 Attempting WordPress distribution...")
                wp_result = self._post_to_wordpress(content['blog_posts'][0] if content['blog_posts'] else "No content")
                distribution_results['wordpress'] = wp_result
                distribution_results['attempted'] = True
            except Exception as e:
                distribution_results['wordpress'] = {'status': 'failed', 'error': str(e)}
        
        # Buffer distribution
        if config.BUFFER_ACCESS_TOKEN:
            try:
                self.logger.info("📱 Attempting Buffer distribution...")
                buffer_result = self._post_to_buffer(content['social_posts'])
                distribution_results['buffer'] = buffer_result
                distribution_results['attempted'] = True
            except Exception as e:
                distribution_results['buffer'] = {'status': 'failed', 'error': str(e)}
        
        return distribution_results
    
    def _post_to_wordpress(self, content: str) -> Dict[str, Any]:
        """Post content to WordPress blog"""
        if not config.WORDPRESS_API_URL:
            return {'status': 'skipped', 'reason': 'WordPress API URL not configured'}
        
        # This is a simplified WordPress API call
        # In practice, you'd need proper authentication and formatting
        try:
            # Placeholder for WordPress API implementation
            self.logger.info("WordPress posting would happen here with proper API setup")
            return {'status': 'simulated', 'message': 'WordPress API integration ready'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _post_to_buffer(self, social_posts: Dict[str, List[str]]) -> Dict[str, Any]:
        """Post content to Buffer for social media scheduling"""
        if not config.BUFFER_ACCESS_TOKEN:
            return {'status': 'skipped', 'reason': 'Buffer access token not configured'}
        
        try:
            # Placeholder for Buffer API implementation
            self.logger.info("Buffer posting would happen here with proper API setup")
            return {'status': 'simulated', 'message': 'Buffer API integration ready'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
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
                        # Enhanced JSON cleaning for Gemini responses
                        cleaned_content = content.strip()
                        
                        # Remove markdown code blocks if present
                        if cleaned_content.startswith('```json'):
                            cleaned_content = cleaned_content[7:]
                        if cleaned_content.startswith('```'):
                            cleaned_content = cleaned_content[3:]
                        if cleaned_content.endswith('```'):
                            cleaned_content = cleaned_content[:-3]
                        
                        # Fix common escape issues
                        cleaned_content = cleaned_content.replace('\\"', '"').replace('\\n', '\\n').replace('\\t', '\\t')
                        
                        # Try to extract JSON from response if embedded in text
                        start_idx = cleaned_content.find('{')
                        end_idx = cleaned_content.rfind('}')
                        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                            cleaned_content = cleaned_content[start_idx:end_idx+1]
                        
                        result = json.loads(cleaned_content)
                        self.logger.log_api_call("Gemini", f"generate_content ({task_name})", "Success (JSON - Cleaned)")
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
