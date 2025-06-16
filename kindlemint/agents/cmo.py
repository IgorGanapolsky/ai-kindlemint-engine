"""
CMO Agent - Adaptive Marketing with Memory-Driven Insights
Generates marketing content based on historical performance data.
"""

import logging
import os
from typing import Dict, List, Optional, Any
import openai

from ..memory import KDPMemory

logger = logging.getLogger(__name__)


class CMOAgent:
    """CMO Agent for memory-driven marketing content generation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        enable_memory: bool = True,
    ):
        """Initialize the CMO Agent.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
            model: The OpenAI model to use for generation.
            temperature: Controls randomness in generation (0-1).
            enable_memory: Whether to use memory-driven marketing insights.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
            )
        
        self.model = model
        self.temperature = temperature
        self.enable_memory = enable_memory
        openai.api_key = self.api_key
        
        # Initialize memory system if enabled
        if self.enable_memory:
            try:
                self.memory = KDPMemory()
                logger.info("Memory-driven marketing enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize memory system: {e}")
                self.enable_memory = False
    
    def generate_sales_copy(
        self,
        book_title: str,
        niche: str,
        target_audience: str = "general readers",
        copy_type: str = "amazon_description"
    ) -> Dict[str, str]:
        """Generate sales copy using historical marketing insights.
        
        Args:
            book_title: Title of the book
            niche: Book niche
            target_audience: Target audience description
            copy_type: Type of copy (amazon_description, gumroad_pitch, email_sequence)
            
        Returns:
            Dict with generated marketing copy and insights used
        """
        marketing_insights = {}
        proven_angles = []
        
        # Get memory-driven insights if available
        if self.enable_memory and hasattr(self, 'memory'):
            try:
                marketing_insights = self.memory.get_niche_marketing_insights(niche)
                
                if marketing_insights:
                    # Extract proven marketing angles
                    for campaign_type, data in marketing_insights.items():
                        if data['average_effectiveness'] > 0.6:  # 60% effectiveness threshold
                            proven_angles.append(campaign_type)
                    
                    logger.info(f"Found {len(proven_angles)} proven marketing angles for {niche}")
                else:
                    logger.info(f"No historical marketing data for niche: {niche}")
                    
            except Exception as e:
                logger.warning(f"Failed to get marketing insights: {e}")
        
        # Generate copy based on insights
        return self._generate_copy_with_insights(
            book_title=book_title,
            niche=niche,
            target_audience=target_audience,
            copy_type=copy_type,
            proven_angles=proven_angles,
            insights=marketing_insights
        )
    
    def _generate_copy_with_insights(
        self,
        book_title: str,
        niche: str,
        target_audience: str,
        copy_type: str,
        proven_angles: List[str],
        insights: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate marketing copy using proven angles and insights."""
        
        # Build context from proven angles
        proven_context = ""
        if proven_angles:
            proven_context = (
                f"\n\nPROVEN MARKETING ANGLES FOR {niche.upper()} NICHE:\n"
                f"Based on historical data, these approaches have been effective:\n"
            )
            for angle in proven_angles:
                effectiveness = insights.get(angle, {}).get('average_effectiveness', 0)
                proven_context += f"- {angle.replace('_', ' ').title()}: {effectiveness:.1%} effectiveness\n"
            
            proven_context += "\nIncorporate elements from these proven approaches in your copy.\n"
        
        # Build prompt based on copy type
        if copy_type == "amazon_description":
            prompt = self._build_amazon_description_prompt(
                book_title, niche, target_audience, proven_context
            )
        elif copy_type == "gumroad_pitch":
            prompt = self._build_gumroad_pitch_prompt(
                book_title, niche, target_audience, proven_context
            )
        elif copy_type == "email_sequence":
            prompt = self._build_email_sequence_prompt(
                book_title, niche, target_audience, proven_context
            )
        else:
            prompt = self._build_generic_copy_prompt(
                book_title, niche, target_audience, copy_type, proven_context
            )
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            generated_copy = response.choices[0].message.content.strip()
            
            return {
                'copy': generated_copy,
                'copy_type': copy_type,
                'niche': niche,
                'proven_angles_used': proven_angles,
                'insights_available': len(insights) > 0,
                'data_driven': self.enable_memory and len(proven_angles) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating sales copy: {str(e)}")
            raise
    
    def _build_amazon_description_prompt(
        self, book_title: str, niche: str, target_audience: str, proven_context: str
    ) -> str:
        """Build prompt for Amazon book description."""
        return f"""
Create a compelling Amazon KDP book description for:
Title: "{book_title}"
Niche: {niche}
Target Audience: {target_audience}

{proven_context}

The description should:
1. Hook readers immediately with a compelling opening
2. Clearly communicate the book's value proposition
3. Use emotional triggers relevant to the {niche} niche
4. Include social proof elements if appropriate
5. End with a strong call-to-action
6. Be optimized for Amazon's search algorithm
7. Be 150-250 words

Format: Write the description ready to paste into Amazon KDP.
"""
    
    def _build_gumroad_pitch_prompt(
        self, book_title: str, niche: str, target_audience: str, proven_context: str
    ) -> str:
        """Build prompt for Gumroad sales pitch."""
        return f"""
Create a high-converting Gumroad sales pitch for:
Title: "{book_title}"
Niche: {niche}
Target Audience: {target_audience}

{proven_context}

The pitch should:
1. Start with a strong headline that addresses pain points
2. Use the AIDA framework (Attention, Interest, Desire, Action)
3. Include specific benefits and outcomes
4. Address objections preemptively
5. Create urgency or scarcity
6. Include a money-back guarantee
7. End with a clear, compelling call-to-action

Format: Structure as a complete sales page with clear sections.
"""
    
    def _build_email_sequence_prompt(
        self, book_title: str, niche: str, target_audience: str, proven_context: str
    ) -> str:
        """Build prompt for email marketing sequence."""
        return f"""
Create a 3-email marketing sequence for:
Title: "{book_title}"
Niche: {niche}
Target Audience: {target_audience}

{proven_context}

Email 1 (Introduction/Value): Introduce the book and provide immediate value
Email 2 (Social Proof/Benefits): Share testimonials, case studies, or detailed benefits
Email 3 (Urgency/CTA): Create urgency and drive action

Each email should:
- Have a compelling subject line
- Be 150-200 words
- Include a clear call-to-action
- Build trust and authority
- Be conversational and engaging

Format: Provide all 3 emails with subject lines and clear structure.
"""
    
    def _build_generic_copy_prompt(
        self, book_title: str, niche: str, target_audience: str, copy_type: str, proven_context: str
    ) -> str:
        """Build generic marketing copy prompt."""
        return f"""
Create {copy_type} marketing copy for:
Title: "{book_title}"
Niche: {niche}
Target Audience: {target_audience}

{proven_context}

The copy should be compelling, benefit-focused, and appropriate for the {niche} niche.
Include emotional triggers and a clear call-to-action.
"""
    
    def update_campaign_effectiveness(
        self, book_id: str, campaign_type: str, effectiveness_score: float
    ) -> bool:
        """Update marketing campaign effectiveness in memory.
        
        Args:
            book_id: ID of the book
            campaign_type: Type of marketing campaign
            effectiveness_score: Effectiveness score (0.0 to 1.0)
            
        Returns:
            Success status
        """
        if self.enable_memory and hasattr(self, 'memory'):
            try:
                return self.memory.update_marketing_effectiveness(
                    book_id, campaign_type, effectiveness_score
                )
            except Exception as e:
                logger.error(f"Failed to update campaign effectiveness: {e}")
                return False
        return False
    
    def get_niche_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get marketing recommendations based on niche performance.
        
        Args:
            limit: Maximum number of recommendations
            
        Returns:
            List of niche recommendations with marketing insights
        """
        if not (self.enable_memory and hasattr(self, 'memory')):
            return []
        
        try:
            top_niches = self.memory.get_top_performing_niches(limit=limit)
            recommendations = []
            
            for niche_data in top_niches:
                niche = niche_data['niche']
                marketing_insights = self.memory.get_niche_marketing_insights(niche)
                
                # Find best performing marketing approaches
                best_approaches = []
                for campaign_type, data in marketing_insights.items():
                    if data['average_effectiveness'] > 0.5:
                        best_approaches.append({
                            'approach': campaign_type,
                            'effectiveness': data['average_effectiveness'],
                            'sample_size': data['sample_size']
                        })
                
                # Sort by effectiveness
                best_approaches.sort(key=lambda x: x['effectiveness'], reverse=True)
                
                recommendations.append({
                    'niche': niche,
                    'average_roi': niche_data['average_roi'],
                    'book_count': niche_data['book_count'],
                    'best_marketing_approaches': best_approaches[:3],  # Top 3
                    'recommendation_score': niche_data['average_roi'] * len(best_approaches)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get niche recommendations: {e}")
            return []