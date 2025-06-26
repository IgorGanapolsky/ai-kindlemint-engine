#!/usr/bin/env python3
"""
Synthetic Market Research Module
Creates AI personas to evaluate book ideas and provide qualitative feedback
Implements the "Wisdom of the Agents" approach for market validation
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import random
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SyntheticMarketResearch')


class PersonaType(Enum):
    """Types of personas for different market segments"""
    BUSY_PARENT = "busy_parent"
    RETIREE = "retiree"
    PUZZLE_ENTHUSIAST = "puzzle_enthusiast"
    GIFT_BUYER = "gift_buyer"
    EDUCATOR = "educator"
    CASUAL_SOLVER = "casual_solver"
    COLLECTOR = "collector"
    THERAPIST = "therapist"  # For cognitive therapy use


@dataclass
class Persona:
    """Represents a synthetic market research persona"""
    name: str
    type: PersonaType
    age: int
    occupation: str
    interests: List[str]
    pain_points: List[str]
    buying_behavior: Dict[str, Any]
    puzzle_preferences: Dict[str, Any]
    
    def evaluate_book_idea(self, book_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a book idea from this persona's perspective"""
        score = 0
        feedback = []
        concerns = []
        
        # Evaluate based on puzzle type preference
        puzzle_type = book_spec.get("puzzle_type", "")
        if puzzle_type in self.puzzle_preferences.get("preferred_types", []):
            score += 30
            feedback.append(f"Love {puzzle_type} puzzles!")
        elif puzzle_type in self.puzzle_preferences.get("avoided_types", []):
            score -= 20
            concerns.append(f"Not a fan of {puzzle_type}")
        
        # Evaluate difficulty
        difficulty = book_spec.get("difficulty", "")
        preferred_difficulty = self.puzzle_preferences.get("difficulty_level", "medium")
        if difficulty == preferred_difficulty:
            score += 20
            feedback.append("Perfect difficulty level for me")
        elif difficulty == "mixed":
            score += 10
            feedback.append("Good variety of difficulties")
        
        # Evaluate theme relevance
        theme = book_spec.get("theme", "")
        if any(interest in theme.lower() for interest in self.interests):
            score += 25
            feedback.append(f"The {theme} theme really appeals to me")
        
        # Consider buying behavior
        price = book_spec.get("price", 9.99)
        if price <= self.buying_behavior.get("max_price", 12.99):
            score += 15
        else:
            concerns.append(f"${price} seems a bit high")
        
        # Format preferences
        format_type = book_spec.get("format", "paperback")
        if format_type in self.buying_behavior.get("preferred_formats", ["paperback"]):
            score += 10
            feedback.append(f"I prefer {format_type} format")
        
        # Generate recommendation
        would_buy = score >= 50
        recommendation = "buy" if would_buy else "pass"
        
        return {
            "persona": self.name,
            "score": min(100, max(0, score)),
            "would_buy": would_buy,
            "recommendation": recommendation,
            "positive_feedback": feedback,
            "concerns": concerns,
            "suggested_improvements": self._generate_suggestions(book_spec, score)
        }
    
    def _generate_suggestions(self, book_spec: Dict, score: int) -> List[str]:
        """Generate improvement suggestions based on persona preferences"""
        suggestions = []
        
        if score < 50:
            # Suggest improvements based on persona type
            if self.type == PersonaType.BUSY_PARENT:
                suggestions.append("Add time estimates for each puzzle")
                suggestions.append("Include 'quick solve' sections for busy moments")
            elif self.type == PersonaType.RETIREE:
                suggestions.append("Use larger print for better readability")
                suggestions.append("Include nostalgic themes")
            elif self.type == PersonaType.EDUCATOR:
                suggestions.append("Add educational facts with puzzles")
                suggestions.append("Include difficulty progression guide")
        
        return suggestions


class PersonaFactory:
    """Factory for creating diverse personas"""
    
    @staticmethod
    def create_persona(persona_type: PersonaType) -> Persona:
        """Create a persona of the specified type"""
        
        if persona_type == PersonaType.BUSY_PARENT:
            return Persona(
                name="Sarah Chen",
                type=PersonaType.BUSY_PARENT,
                age=38,
                occupation="Marketing Manager",
                interests=["family time", "quick entertainment", "education", "mindfulness"],
                pain_points=["limited free time", "need mental breaks", "finding quality family activities"],
                buying_behavior={
                    "frequency": "monthly",
                    "max_price": 12.99,
                    "preferred_formats": ["paperback", "kindle"],
                    "buying_triggers": ["stress relief", "family bonding", "travel entertainment"]
                },
                puzzle_preferences={
                    "preferred_types": ["crossword", "word_search"],
                    "avoided_types": ["cryptic"],
                    "difficulty_level": "easy",
                    "time_per_puzzle": "10-15 minutes",
                    "features_wanted": ["clear instructions", "answer key", "portable size"]
                }
            )
            
        elif persona_type == PersonaType.RETIREE:
            return Persona(
                name="Robert Thompson",
                type=PersonaType.RETIREE,
                age=68,
                occupation=
                interests=["reading", "gardening", "history", "mental fitness"],
                pain_points=["cognitive health concerns", "filling time meaningfully", "vision issues"],
                buying_behavior={
                    "frequency": "weekly",
                    "max_price": 15.99,
                    "preferred_formats": ["paperback", "hardcover"],
                    "buying_triggers": ["mental exercise", "gift for friends", "collection building"]
                },
                puzzle_preferences={
                    "preferred_types": ["crossword", "sudoku"],
                    "avoided_types": ["word_search"],
                    "difficulty_level": "medium",
                    "time_per_puzzle": "30-45 minutes",
                    "features_wanted": ["large print", "quality paper", "classic themes"]
                }
            )
            
        elif persona_type == PersonaType.PUZZLE_ENTHUSIAST:
            return Persona(
                name="Alex Rivera",
                type=PersonaType.PUZZLE_ENTHUSIAST,
                age=29,
                occupation="Software Developer",
                interests=["puzzles", "gaming", "challenges", "competitions"],
                pain_points=["finding challenging content", "repetitive puzzles", "poor quality"],
                buying_behavior={
                    "frequency": "bi-weekly",
                    "max_price": 19.99,
                    "preferred_formats": ["paperback"],
                    "buying_triggers": ["new challenges", "unique puzzles", "series completion"]
                },
                puzzle_preferences={
                    "preferred_types": ["crossword", "cryptic", "variety"],
                    "avoided_types": [],
                    "difficulty_level": "hard",
                    "time_per_puzzle": "45-60 minutes",
                    "features_wanted": ["innovative formats", "themed collections", "no errors"]
                }
            )
            
        elif persona_type == PersonaType.GIFT_BUYER:
            return Persona(
                name="Jennifer Martinez",
                type=PersonaType.GIFT_BUYER,
                age=45,
                occupation="HR Director",
                interests=["gift giving", "relationships", "quality products"],
                pain_points=["finding appropriate gifts", "quality concerns", "recipient satisfaction"],
                buying_behavior={
                    "frequency": "seasonal",
                    "max_price": 24.99,
                    "preferred_formats": ["hardcover", "gift sets"],
                    "buying_triggers": ["holidays", "birthdays", "get well gifts"]
                },
                puzzle_preferences={
                    "preferred_types": ["variety", "crossword"],
                    "avoided_types": ["too difficult"],
                    "difficulty_level": "mixed",
                    "time_per_puzzle": "varies",
                    "features_wanted": ["attractive cover", "gift-worthy quality", "universal appeal"]
                }
            )
            
        else:  # Default/Casual Solver
            return Persona(
                name="Mike Johnson",
                type=PersonaType.CASUAL_SOLVER,
                age=42,
                occupation="Sales Representative",
                interests=["travel", "coffee breaks", "light entertainment"],
                pain_points=["boredom during travel", "waiting times", "screen fatigue"],
                buying_behavior={
                    "frequency": "occasional",
                    "max_price": 9.99,
                    "preferred_formats": ["paperback"],
                    "buying_triggers": ["travel", "impulse buy", "recommendations"]
                },
                puzzle_preferences={
                    "preferred_types": ["word_search", "easy_crossword"],
                    "avoided_types": ["complex_puzzles"],
                    "difficulty_level": "easy",
                    "time_per_puzzle": "5-10 minutes",
                    "features_wanted": ["portable", "pencil-friendly", "clear layout"]
                }
            )


class SyntheticMarketResearch:
    """
    Conducts synthetic market research using AI personas
    Provides qualitative feedback on book ideas before production
    """
    
    def __init__(self):
        self.personas = self._initialize_personas()
        self.research_history = []
        
    def _initialize_personas(self) -> List[Persona]:
        """Initialize a diverse set of personas"""
        personas = []
        
        # Create multiple personas of each type for diversity
        for persona_type in PersonaType:
            # Create 1-2 personas per type
            personas.append(PersonaFactory.create_persona(persona_type))
        
        logger.info(f"Initialized {len(personas)} personas for market research")
        return personas
    
    def evaluate_book_idea(
        self, 
        book_spec: Dict[str, Any],
        target_personas: Optional[List[PersonaType]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a book idea across all or selected personas
        Returns aggregated feedback and market viability score
        """
        
        # Select personas to evaluate
        if target_personas:
            evaluating_personas = [p for p in self.personas if p.type in target_personas]
        else:
            evaluating_personas = self.personas
        
        logger.info(f"Evaluating book idea with {len(evaluating_personas)} personas")
        
        # Collect evaluations
        evaluations = []
        for persona in evaluating_personas:
            evaluation = persona.evaluate_book_idea(book_spec)
            evaluations.append(evaluation)
        
        # Aggregate results
        total_score = sum(e["score"] for e in evaluations)
        avg_score = total_score / len(evaluations) if evaluations else 0
        
        would_buy_count = sum(1 for e in evaluations if e["would_buy"])
        buy_rate = would_buy_count / len(evaluations) if evaluations else 0
        
        # Collect all feedback
        all_positive = []
        all_concerns = []
        all_suggestions = []
        
        for evaluation in evaluations:
            all_positive.extend(evaluation["positive_feedback"])
            all_concerns.extend(evaluation["concerns"])
            all_suggestions.extend(evaluation["suggested_improvements"])
        
        # Remove duplicates while preserving order
        all_positive = list(dict.fromkeys(all_positive))
        all_concerns = list(dict.fromkeys(all_concerns))
        all_suggestions = list(dict.fromkeys(all_suggestions))
        
        # Determine market viability
        viability = self._calculate_viability(avg_score, buy_rate)
        
        # Generate executive summary
        summary = self._generate_summary(book_spec, viability, evaluations)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "book_spec": book_spec,
            "personas_evaluated": len(evaluating_personas),
            "average_score": round(avg_score, 1),
            "buy_rate": round(buy_rate * 100, 1),
            "would_buy_count": would_buy_count,
            "market_viability": viability,
            "executive_summary": summary,
            "positive_feedback": all_positive[:5],  # Top 5
            "main_concerns": all_concerns[:5],  # Top 5
            "improvement_suggestions": all_suggestions[:5],  # Top 5
            "individual_evaluations": evaluations,
            "recommendation": self._generate_recommendation(viability, avg_score)
        }
        
        # Store in history
        self.research_history.append(result)
        
        return result
    
    def _calculate_viability(self, avg_score: float, buy_rate: float) -> str:
        """Calculate market viability rating"""
        if avg_score >= 70 and buy_rate >= 0.6:
            return "HIGH"
        elif avg_score >= 50 and buy_rate >= 0.4:
            return "MEDIUM"
        elif avg_score >= 30 and buy_rate >= 0.2:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _generate_summary(
        self, 
        book_spec: Dict[str, Any], 
        viability: str,
        evaluations: List[Dict]
    ) -> str:
        """Generate executive summary of research findings"""
        
        title = book_spec.get("title", "Untitled")
        puzzle_type = book_spec.get("puzzle_type", "puzzle")
        
        summaries = {
            "HIGH": f"'{title}' shows strong market potential. The {puzzle_type} format resonates well across multiple personas with high purchase intent.",
            "MEDIUM": f"'{title}' has moderate market potential. Some personas show interest, but improvements could broaden appeal.",
            "LOW": f"'{title}' faces market challenges. Limited persona interest suggests need for significant concept revision.",
            "VERY_LOW": f"'{title}' is not recommended for production. Minimal market interest across evaluated personas."
        }
        
        return summaries.get(viability, "Market research inconclusive.")
    
    def _generate_recommendation(self, viability: str, score: float) -> Dict[str, Any]:
        """Generate actionable recommendation"""
        
        recommendations = {
            "HIGH": {
                "action": "PROCEED",
                "priority": "high",
                "next_steps": [
                    "Move to production immediately",
                    "Consider premium formats",
                    "Plan marketing campaign"
                ]
            },
            "MEDIUM": {
                "action": "REFINE",
                "priority": "medium",
                "next_steps": [
                    "Implement suggested improvements",
                    "Re-test with target personas",
                    "Consider A/B testing covers"
                ]
            },
            "LOW": {
                "action": "PIVOT",
                "priority": "low",
                "next_steps": [
                    "Reconsider core concept",
                    "Test alternative themes",
                    "Narrow target audience"
                ]
            },
            "VERY_LOW": {
                "action": "ABANDON",
                "priority": "none",
                "next_steps": [
                    "Archive concept",
                    "Focus on higher-scoring ideas",
                    "Analyze why it failed"
                ]
            }
        }
        
        return recommendations.get(viability, recommendations["LOW"])
    
    def generate_market_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate comprehensive market research report"""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_research_sessions": len(self.research_history),
            "personas_available": len(self.personas),
            "recent_evaluations": self.research_history[-5:],  # Last 5
            "market_insights": self._extract_market_insights()
        }
        
        if not output_path:
            output_path = Path("research") / f"market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Market research report saved to: {output_path}")
        return output_path
    
    def _extract_market_insights(self) -> Dict[str, Any]:
        """Extract insights from research history"""
        
        if not self.research_history:
            return {"status": "No research conducted yet"}
        
        # Analyze trends
        high_viability_count = sum(1 for r in self.research_history if r["market_viability"] == "HIGH")
        avg_scores = [r["average_score"] for r in self.research_history]
        
        return {
            "total_ideas_tested": len(self.research_history),
            "high_viability_ideas": high_viability_count,
            "average_market_score": round(sum(avg_scores) / len(avg_scores), 1),
            "most_requested_features": self._get_common_suggestions(),
            "most_common_concerns": self._get_common_concerns()
        }
    
    def _get_common_suggestions(self) -> List[str]:
        """Extract most common improvement suggestions"""
        all_suggestions = []
        for research in self.research_history:
            all_suggestions.extend(research.get("improvement_suggestions", []))
        
        # Count and return top 3
        from collections import Counter
        counts = Counter(all_suggestions)
        return [item for item, _ in counts.most_common(3)]
    
    def _get_common_concerns(self) -> List[str]:
        """Extract most common concerns"""
        all_concerns = []
        for research in self.research_history:
            all_concerns.extend(research.get("main_concerns", []))
        
        from collections import Counter
        counts = Counter(all_concerns)
        return [item for item, _ in counts.most_common(3)]


def main():
    """CLI interface for synthetic market research"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Synthetic Market Research")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--type", required=True, choices=["crossword", "sudoku", "word_search"])
    parser.add_argument("--difficulty", default="medium", choices=["easy", "medium", "hard", "mixed"])
    parser.add_argument("--theme", help="Book theme")
    parser.add_argument("--price", type=float, default=9.99, help="Planned price")
    parser.add_argument("--format", default="paperback", choices=["paperback", "hardcover", "kindle"])
    parser.add_argument("--target-personas", nargs="+", help="Specific personas to target")
    parser.add_argument("--output", help="Output path for report")
    
    args = parser.parse_args()
    
    # Create book specification
    book_spec = {
        "title": args.title,
        "puzzle_type": args.type,
        "difficulty": args.difficulty,
        "theme": args.theme or "General",
        "price": args.price,
        "format": args.format
    }
    
    # Run research
    researcher = SyntheticMarketResearch()
    
    # Parse target personas if specified
    target_personas = None
    if args.target_personas:
        target_personas = [PersonaType(p) for p in args.target_personas]
    
    result = researcher.evaluate_book_idea(book_spec, target_personas)
    
    # Display results
    print(f"\n📊 SYNTHETIC MARKET RESEARCH RESULTS")
    print(f"{'=' * 50}")
    print(f"📚 Book: {result['book_spec']['title']}")
    print(f"🎯 Market Score: {result['average_score']}/100")
    print(f"💰 Buy Rate: {result['buy_rate']}%")
    print(f"📈 Market Viability: {result['market_viability']}")
    print(f"\n📝 Executive Summary:")
    print(f"   {result['executive_summary']}")
    
    print(f"\n✅ Positive Feedback:")
    for feedback in result['positive_feedback']:
        print(f"   • {feedback}")
    
    if result['main_concerns']:
        print(f"\n⚠️  Main Concerns:")
        for concern in result['main_concerns']:
            print(f"   • {concern}")
    
    print(f"\n💡 Recommendation: {result['recommendation']['action']}")
    print(f"📋 Next Steps:")
    for step in result['recommendation']['next_steps']:
        print(f"   • {step}")
    
    # Save detailed report if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📄 Detailed report saved to: {output_path}")


if __name__ == "__main__":
    main()