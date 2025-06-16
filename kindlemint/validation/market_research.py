"""
Synthetic Market Research - AI Persona Validation System
Validates book concepts using AI personas before content creation to de-risk investments.
"""

import logging
import os
from typing import Dict, List, Optional, Any
import openai
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Market validation results."""
    STRONG_PASS = "strong_pass"      # 80%+ validation score
    WEAK_PASS = "weak_pass"          # 60-79% validation score  
    WEAK_FAIL = "weak_fail"          # 40-59% validation score
    STRONG_FAIL = "strong_fail"      # <40% validation score


@dataclass
class PersonaResponse:
    """Response from an AI persona during validation."""
    persona_name: str
    interest_score: int  # 1-10 scale
    purchase_likelihood: int  # 1-10 scale
    reasoning: str
    concerns: List[str]
    suggestions: List[str]


@dataclass
class ValidationReport:
    """Complete market validation report."""
    book_topic: str
    niche: str
    overall_score: float  # 0-100 scale
    validation_result: ValidationResult
    persona_responses: List[PersonaResponse]
    market_insights: Dict[str, Any]
    recommendations: List[str]
    validation_timestamp: str
    should_proceed: bool


class PersonaValidator:
    """Validates book concepts using AI personas representing target customers."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize the persona validator."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.model = model
        openai.api_key = self.api_key
    
    def validate_with_persona(
        self, 
        book_topic: str, 
        niche: str, 
        persona_description: str, 
        persona_name: str
    ) -> PersonaResponse:
        """Validate a book topic with a specific AI persona."""
        
        validation_prompt = f"""
You are {persona_name}, a real customer in the {niche} market. You have the following characteristics:
{persona_description}

You are browsing Amazon and come across this book:
Title: "{book_topic}"
Category: {niche}

As {persona_name}, please evaluate this book honestly and provide:

1. Interest Score (1-10): How interested are you in this topic?
2. Purchase Likelihood (1-10): How likely are you to buy this book?
3. Reasoning: Why does this book appeal to you or not? Be specific about your motivations.
4. Concerns: What makes you hesitant about this book? List 2-3 specific concerns.
5. Suggestions: How could this book be improved to better appeal to you? List 2-3 suggestions.

Respond in this exact format:
INTEREST_SCORE: [1-10]
PURCHASE_LIKELIHOOD: [1-10]
REASONING: [Your detailed reasoning]
CONCERNS: [Concern 1] | [Concern 2] | [Concern 3]
SUGGESTIONS: [Suggestion 1] | [Suggestion 2] | [Suggestion 3]

Be honest and critical. Only give high scores if you would genuinely be excited about this book.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": validation_prompt}],
                temperature=0.3,  # Lower temperature for more consistent persona responses
                max_tokens=800
            )
            
            return self._parse_persona_response(
                response.choices[0].message.content, 
                persona_name
            )
            
        except Exception as e:
            logger.error(f"Error validating with persona {persona_name}: {e}")
            # Return default low-scoring response on error
            return PersonaResponse(
                persona_name=persona_name,
                interest_score=3,
                purchase_likelihood=2,
                reasoning=f"Validation failed due to error: {str(e)}",
                concerns=["Validation system error"],
                suggestions=["Retry validation"]
            )
    
    def _parse_persona_response(self, response_text: str, persona_name: str) -> PersonaResponse:
        """Parse the structured response from the AI persona."""
        try:
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            interest_score = 5  # defaults
            purchase_likelihood = 5
            reasoning = "No reasoning provided"
            concerns = []
            suggestions = []
            
            for line in lines:
                if line.startswith("INTEREST_SCORE:"):
                    interest_score = int(line.split(":")[1].strip())
                elif line.startswith("PURCHASE_LIKELIHOOD:"):
                    purchase_likelihood = int(line.split(":")[1].strip())
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
                elif line.startswith("CONCERNS:"):
                    concerns_text = line.split(":", 1)[1].strip()
                    concerns = [c.strip() for c in concerns_text.split("|") if c.strip()]
                elif line.startswith("SUGGESTIONS:"):
                    suggestions_text = line.split(":", 1)[1].strip()
                    suggestions = [s.strip() for s in suggestions_text.split("|") if s.strip()]
            
            return PersonaResponse(
                persona_name=persona_name,
                interest_score=max(1, min(10, interest_score)),  # Clamp to 1-10
                purchase_likelihood=max(1, min(10, purchase_likelihood)),
                reasoning=reasoning,
                concerns=concerns[:3],  # Limit to 3 concerns
                suggestions=suggestions[:3]  # Limit to 3 suggestions
            )
            
        except Exception as e:
            logger.warning(f"Error parsing persona response: {e}")
            return PersonaResponse(
                persona_name=persona_name,
                interest_score=3,
                purchase_likelihood=3,
                reasoning="Failed to parse validation response",
                concerns=["Response parsing error"],
                suggestions=["Improve validation format"]
            )


class MarketValidator:
    """Main market validation system using multiple AI personas."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize the market validator."""
        self.persona_validator = PersonaValidator(api_key, model)
        self.niche_personas = self._load_niche_personas()
    
    def _load_niche_personas(self) -> Dict[str, List[Dict[str, str]]]:
        """Load predefined personas for different niches."""
        return {
            "productivity": [
                {
                    "name": "Sarah the Overwhelmed Manager",
                    "description": "Sarah is a 32-year-old project manager at a tech company. She works 50+ hours per week, struggles with work-life balance, and is constantly looking for ways to be more efficient. She buys productivity books hoping to find systems that actually work in her chaotic environment. She's skeptical of overly theoretical advice and wants practical, immediately actionable strategies."
                },
                {
                    "name": "Mike the Ambitious Entrepreneur", 
                    "description": "Mike is a 28-year-old startup founder who bootstrapped his company. He's obsessed with optimization and peak performance. He reads voraciously about productivity systems, time management, and business efficiency. He's willing to experiment with new methods but gets frustrated with generic advice that doesn't apply to the entrepreneurial lifestyle."
                },
                {
                    "name": "Jennifer the Working Mom",
                    "description": "Jennifer is a 35-year-old marketing director with two young children. She's constantly juggling work deadlines, school pickups, and household management. She desperately wants productivity systems that work with an unpredictable schedule and frequent interruptions. She values quick wins and strategies that don't require perfect conditions to implement."
                }
            ],
            "personal finance": [
                {
                    "name": "David the Debt-Stressed Millennial",
                    "description": "David is a 29-year-old software developer with $45K in student loans and credit card debt. He makes decent money but feels like he's always behind financially. He's overwhelmed by conflicting financial advice and wants a clear, step-by-step plan to get out of debt and start building wealth. He's skeptical of get-rich-quick schemes but hungry for practical guidance."
                },
                {
                    "name": "Lisa the Retirement Worrier",
                    "description": "Lisa is a 42-year-old teacher who realized she's behind on retirement savings. She has some money in a 401k but doesn't understand investing and is paralyzed by the complexity of financial planning. She wants straightforward, jargon-free advice on catching up on retirement and building passive income streams without taking excessive risks."
                },
                {
                    "name": "Carlos the Side-Hustle Seeker",
                    "description": "Carlos is a 26-year-old graphic designer who wants to escape the 9-to-5 grind. He's interested in building multiple income streams and achieving financial independence. He's willing to work hard and learn new skills but needs guidance on which opportunities are legitimate and how to scale side businesses into full-time income."
                }
            ],
            "health": [
                {
                    "name": "Amanda the Burnout Recovery Seeker",
                    "description": "Amanda is a 34-year-old nurse who's been struggling with chronic fatigue and stress-related health issues. She's tried various diets and wellness trends but nothing seems to stick long-term. She's looking for sustainable, science-based approaches to rebuilding her energy and health that fit into a demanding work schedule."
                },
                {
                    "name": "Robert the Fitness Comeback",
                    "description": "Robert is a 45-year-old accountant who used to be athletic but has gained 40 pounds over the past decade. He's been through multiple failed diet attempts and gym memberships. He wants a realistic, sustainable approach to getting back in shape that acknowledges his age, busy schedule, and past failures."
                },
                {
                    "name": "Michelle the Wellness Optimizer",
                    "description": "Michelle is a 31-year-old wellness coach who's already health-conscious but always looking to optimize her performance. She's interested in cutting-edge health strategies, biohacking techniques, and evidence-based wellness practices. She's willing to invest time and money in her health but wants scientifically-backed approaches, not fads."
                }
            ],
            "self-help": [
                {
                    "name": "Tom the Confidence Builder",
                    "description": "Tom is a 27-year-old accountant who struggles with social anxiety and low self-confidence. He avoids networking events and speaking up in meetings, which is hurting his career progression. He's read some self-help books but finds them either too 'rah-rah' motivational or too abstract. He wants practical, step-by-step strategies for building genuine confidence."
                },
                {
                    "name": "Rachel the Life Transition Navigator",
                    "description": "Rachel is a 36-year-old who recently went through a divorce and is rebuilding her life. She's questioning her career path, struggling with single motherhood, and trying to rediscover her identity. She needs guidance on making major life changes, building resilience, and creating a fulfilling life after a major setback."
                },
                {
                    "name": "Kevin the Purpose Seeker",
                    "description": "Kevin is a 31-year-old consultant who feels successful on paper but empty inside. He makes good money but feels like his work has no meaning. He's interested in finding his life purpose, aligning his career with his values, and building a more fulfilling existence. He's skeptical of overly spiritual approaches but open to practical wisdom."
                }
            ]
        }
    
    def validate_book_concept(
        self, 
        book_topic: str, 
        niche: str, 
        custom_personas: Optional[List[Dict[str, str]]] = None
    ) -> ValidationReport:
        """Validate a book concept using AI personas for the given niche."""
        
        logger.info(f"Starting market validation for: {book_topic} (niche: {niche})")
        
        # Get personas for this niche
        personas = custom_personas or self.niche_personas.get(niche.lower(), [])
        
        if not personas:
            # Fallback: create generic personas for unknown niches
            personas = self._create_generic_personas(niche)
        
        # Validate with each persona
        persona_responses = []
        for persona in personas:
            response = self.persona_validator.validate_with_persona(
                book_topic=book_topic,
                niche=niche,
                persona_description=persona["description"],
                persona_name=persona["name"]
            )
            persona_responses.append(response)
            logger.info(f"Persona {persona['name']}: Interest={response.interest_score}, Purchase={response.purchase_likelihood}")
        
        # Calculate overall validation score
        overall_score = self._calculate_overall_score(persona_responses)
        validation_result = self._determine_validation_result(overall_score)
        
        # Generate market insights and recommendations
        market_insights = self._generate_market_insights(persona_responses)
        recommendations = self._generate_recommendations(persona_responses, validation_result)
        
        # Determine if we should proceed
        should_proceed = validation_result in [ValidationResult.STRONG_PASS, ValidationResult.WEAK_PASS]
        
        report = ValidationReport(
            book_topic=book_topic,
            niche=niche,
            overall_score=overall_score,
            validation_result=validation_result,
            persona_responses=persona_responses,
            market_insights=market_insights,
            recommendations=recommendations,
            validation_timestamp=datetime.now(timezone.utc).isoformat(),
            should_proceed=should_proceed
        )
        
        logger.info(f"Validation complete. Score: {overall_score:.1f}%, Result: {validation_result.value}, Proceed: {should_proceed}")
        return report
    
    def _create_generic_personas(self, niche: str) -> List[Dict[str, str]]:
        """Create generic personas for unknown niches."""
        return [
            {
                "name": f"Alex the {niche.title()} Beginner",
                "description": f"Alex is new to {niche} and looking for beginner-friendly guidance. They want practical, actionable advice that's easy to understand and implement."
            },
            {
                "name": f"Sam the {niche.title()} Enthusiast", 
                "description": f"Sam has some experience with {niche} and is looking to deepen their knowledge. They want intermediate-level content that goes beyond the basics."
            },
            {
                "name": f"Jordan the {niche.title()} Expert",
                "description": f"Jordan is experienced in {niche} and looking for advanced strategies or fresh perspectives. They're skeptical of generic advice and want cutting-edge insights."
            }
        ]
    
    def _calculate_overall_score(self, persona_responses: List[PersonaResponse]) -> float:
        """Calculate overall validation score from persona responses."""
        if not persona_responses:
            return 0.0
        
        total_score = 0
        for response in persona_responses:
            # Weight interest and purchase likelihood equally
            persona_score = (response.interest_score + response.purchase_likelihood) / 2
            # Convert to 0-100 scale
            total_score += (persona_score / 10) * 100
        
        return total_score / len(persona_responses)
    
    def _determine_validation_result(self, overall_score: float) -> ValidationResult:
        """Determine validation result based on overall score."""
        if overall_score >= 80:
            return ValidationResult.STRONG_PASS
        elif overall_score >= 60:
            return ValidationResult.WEAK_PASS
        elif overall_score >= 40:
            return ValidationResult.WEAK_FAIL
        else:
            return ValidationResult.STRONG_FAIL
    
    def _generate_market_insights(self, persona_responses: List[PersonaResponse]) -> Dict[str, Any]:
        """Generate market insights from persona responses."""
        total_interest = sum(r.interest_score for r in persona_responses)
        total_purchase = sum(r.purchase_likelihood for r in persona_responses)
        
        all_concerns = []
        all_suggestions = []
        
        for response in persona_responses:
            all_concerns.extend(response.concerns)
            all_suggestions.extend(response.suggestions)
        
        return {
            "average_interest": total_interest / len(persona_responses) if persona_responses else 0,
            "average_purchase_likelihood": total_purchase / len(persona_responses) if persona_responses else 0,
            "common_concerns": list(set(all_concerns)),  # Remove duplicates
            "improvement_suggestions": list(set(all_suggestions)),
            "persona_count": len(persona_responses)
        }
    
    def _generate_recommendations(
        self, 
        persona_responses: List[PersonaResponse], 
        validation_result: ValidationResult
    ) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        if validation_result == ValidationResult.STRONG_PASS:
            recommendations.append("✅ PROCEED: Strong market validation. This topic shows excellent potential.")
            recommendations.append("💡 Focus on the specific benefits mentioned by personas in your marketing copy.")
            
        elif validation_result == ValidationResult.WEAK_PASS:
            recommendations.append("⚠️ PROCEED WITH CAUTION: Moderate validation. Consider incorporating persona suggestions.")
            
            # Add specific suggestions from personas
            all_suggestions = []
            for response in persona_responses:
                all_suggestions.extend(response.suggestions)
            
            unique_suggestions = list(set(all_suggestions))[:3]  # Top 3 unique suggestions
            for suggestion in unique_suggestions:
                recommendations.append(f"💡 Consider: {suggestion}")
                
        elif validation_result == ValidationResult.WEAK_FAIL:
            recommendations.append("❌ RECONSIDER: Weak market validation. Major improvements needed.")
            recommendations.append("🔄 Recommendation: Pivot the topic or target a different niche.")
            
        else:  # STRONG_FAIL
            recommendations.append("🛑 ABORT: Poor market validation. Do not proceed with this topic.")
            recommendations.append("🔄 Recommendation: Generate a completely different topic in a different niche.")
        
        return recommendations


def run_market_validation_demo():
    """Demo function to test the market validation system."""
    try:
        validator = MarketValidator()
        
        # Test topics
        test_cases = [
            ("The 5 AM Success Formula: Transform Your Life with Early Morning Habits", "productivity"),
            ("Passive Income Mastery: 7 Proven Streams to Financial Freedom", "personal finance"),
            ("The Ultimate Guide to Collecting Vintage Bottle Caps", "hobbies")  # Should fail
        ]
        
        for topic, niche in test_cases:
            print(f"\n{'='*60}")
            print(f"VALIDATING: {topic}")
            print(f"NICHE: {niche}")
            print('='*60)
            
            report = validator.validate_book_concept(topic, niche)
            
            print(f"Overall Score: {report.overall_score:.1f}%")
            print(f"Result: {report.validation_result.value}")
            print(f"Should Proceed: {'✅ YES' if report.should_proceed else '❌ NO'}")
            
            print(f"\nPersona Responses:")
            for response in report.persona_responses:
                print(f"  • {response.persona_name}: Interest={response.interest_score}/10, Purchase={response.purchase_likelihood}/10")
            
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  {rec}")
                
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    run_market_validation_demo()