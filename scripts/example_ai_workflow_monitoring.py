#!/usr/bin/env python3
"""
Example: AI Workflow with Sentry Agent Monitoring
Demonstrates how to integrate agent monitoring into existing workflows
"""

import os
import sys
import json
import time
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.api_manager_enhanced import EnhancedAPIManager, with_ai_monitoring
from scripts.sentry_agent_monitoring import get_agent_monitor, AgentContext
from scripts.crossword_clue_generator import CrosswordClueGenerator

# Set up environment (for testing - in production use .env file)
if not os.getenv('SENTRY_DSN'):
    print("⚠️  No SENTRY_DSN found. Set it to enable monitoring.")
    print("   Example: export SENTRY_DSN='your-sentry-dsn-here'")


class MonitoredCrosswordWorkflow:
    """Example workflow showing AI monitoring integration"""
    
    def __init__(self):
        self.api_manager = EnhancedAPIManager()
        self.clue_generator = CrosswordClueGenerator()
        self.monitor = get_agent_monitor()
    
    def generate_crossword_with_ai(self, words: List[str], difficulty: str = "medium"):
        """
        Generate crossword clues using AI with full monitoring.
        Shows how monitoring helps debug AI workflows.
        """
        
        # Create main workflow context
        context = AgentContext(
            agent_id=f"crossword_workflow_{int(time.time() * 1000)}",
            agent_type="workflow",
            task_name="generate_crossword_clues",
            model="gpt-4",
            metadata={
                "word_count": len(words),
                "difficulty": difficulty
            }
        )
        
        with self.monitor.start_agent(context) as transaction:
            results = []
            
            # Step 1: Generate clues for each word
            for word in words:
                try:
                    # First try local database
                    local_clues = self.clue_generator.clue_database.get(word.upper(), [])
                    
                    if local_clues:
                        # Track that we used cached clues
                        self.monitor.track_tool_call(
                            agent_id=context.agent_id,
                            tool_name="local_clue_database",
                            tool_input={"word": word},
                            tool_output={"clue_count": len(local_clues)}
                        )
                        
                        results.append({
                            "word": word,
                            "clues": local_clues[:3],  # Top 3 clues
                            "source": "database"
                        })
                    else:
                        # Use AI to generate new clues
                        prompt = self._build_clue_prompt(word, difficulty)
                        
                        ai_result = self.api_manager.generate_text(
                            prompt=prompt,
                            task_name=f"clue_generation_{word}",
                            temperature=0.8,
                            max_tokens=200,
                            system_prompt="You are an expert crossword puzzle creator. Generate creative and appropriate clues."
                        )
                        
                        # Parse AI response
                        clues = self._parse_ai_clues(ai_result['text'])
                        
                        results.append({
                            "word": word,
                            "clues": clues,
                            "source": "ai_generated",
                            "tokens_used": ai_result['usage']['total_tokens']
                        })
                        
                except Exception as e:
                    # Track individual word failures
                    self.monitor.capture_ai_error(
                        context.agent_id,
                        e,
                        {"word": word, "step": "clue_generation"}
                    )
                    
                    results.append({
                        "word": word,
                        "error": str(e),
                        "source": "error"
                    })
            
            # Step 2: Validate all generated clues
            validation_results = self._validate_clues(results)
            
            # Track validation
            self.monitor.track_tool_call(
                agent_id=context.agent_id,
                tool_name="clue_validator",
                tool_input={"clue_count": len(results)},
                tool_output=validation_results
            )
            
            # Summary tracking
            transaction.track_prompt(
                prompt=f"Generate clues for {len(words)} words",
                response=f"Generated {len([r for r in results if 'clues' in r])} successful clues",
                tokens=sum(r.get('tokens_used', 0) for r in results)
            )
            
            return {
                "results": results,
                "validation": validation_results,
                "stats": self._calculate_stats(results)
            }
    
    def _build_clue_prompt(self, word: str, difficulty: str) -> str:
        """Build prompt for clue generation"""
        difficulty_guidelines = {
            "easy": "simple, straightforward, commonly known",
            "medium": "moderately challenging, some wordplay allowed",
            "hard": "cryptic, clever wordplay, obscure references allowed"
        }
        
        return f"""Generate 3 crossword clues for the word "{word.upper()}".
        
Difficulty level: {difficulty} ({difficulty_guidelines.get(difficulty, 'medium')})
Word length: {len(word)} letters

Format each clue on a new line, numbered 1-3.
Make clues varied in style (definition, fill-in-blank, wordplay).
"""
    
    def _parse_ai_clues(self, ai_response: str) -> List[str]:
        """Parse clues from AI response"""
        lines = ai_response.strip().split('\n')
        clues = []
        
        for line in lines:
            # Remove numbering and clean up
            cleaned = line.strip()
            if cleaned and len(cleaned) > 5:  # Basic validation
                # Remove common prefixes
                for prefix in ['1.', '2.', '3.', '-', '*', '•']:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):].strip()
                        break
                
                if cleaned:
                    clues.append(cleaned)
        
        return clues[:3]  # Maximum 3 clues
    
    def _validate_clues(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate generated clues"""
        validation = {
            "total_words": len(results),
            "successful": 0,
            "failed": 0,
            "issues": []
        }
        
        for result in results:
            if "error" in result:
                validation["failed"] += 1
                validation["issues"].append(f"{result['word']}: {result['error']}")
            elif "clues" in result:
                if len(result["clues"]) >= 1:
                    validation["successful"] += 1
                else:
                    validation["failed"] += 1
                    validation["issues"].append(f"{result['word']}: No clues generated")
        
        validation["success_rate"] = validation["successful"] / validation["total_words"] if validation["total_words"] > 0 else 0
        
        return validation
    
    def _calculate_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate workflow statistics"""
        stats = {
            "total_words": len(results),
            "ai_generated": len([r for r in results if r.get("source") == "ai_generated"]),
            "database_hits": len([r for r in results if r.get("source") == "database"]),
            "errors": len([r for r in results if r.get("source") == "error"]),
            "total_tokens": sum(r.get("tokens_used", 0) for r in results),
            "estimated_cost": sum(r.get("tokens_used", 0) for r in results) * 0.00003  # Example rate
        }
        
        return stats


def demonstrate_error_scenarios():
    """Demonstrate how monitoring helps with common AI errors"""
    
    api_manager = EnhancedAPIManager()
    monitor = get_agent_monitor()
    
    print("\n=== Demonstrating Error Scenarios ===\n")
    
    # Scenario 1: Token limit error
    print("1. Testing token limit error handling...")
    try:
        result = api_manager.generate_text(
            prompt="Write a very long story " * 100,  # Intentionally long prompt
            task_name="token_limit_test",
            max_tokens=10  # Very low limit
        )
    except Exception as e:
        print(f"   ✓ Caught expected error: {type(e).__name__}")
    
    # Scenario 2: Invalid JSON parsing
    print("\n2. Testing JSON parsing error...")
    
    context = AgentContext(
        agent_id="json_test",
        agent_type="test",
        task_name="json_parsing_test",
        model="gpt-4"
    )
    
    with monitor.start_agent(context) as transaction:
        try:
            # Simulate receiving invalid JSON from AI
            invalid_json = '{"incomplete": '
            json.loads(invalid_json)  # This will fail
        except json.JSONDecodeError as e:
            monitor.capture_ai_error(
                context.agent_id,
                e,
                {"raw_response": invalid_json, "step": "parsing_ai_response"}
            )
            print(f"   ✓ Caught JSON error and sent to Sentry")
    
    # Scenario 3: Tool failure
    print("\n3. Testing tool failure tracking...")
    
    monitor.track_tool_call(
        agent_id="tool_test",
        tool_name="validate_crossword",
        tool_input={"grid": "invalid_data"},
        error=ValueError("Invalid crossword grid format")
    )
    print("   ✓ Tool failure tracked")


def main():
    """Main example workflow"""
    
    print("=== AI Workflow Monitoring Example ===")
    print("This demonstrates Sentry Agent Monitoring for AI workflows\n")
    
    # Initialize workflow
    workflow = MonitoredCrosswordWorkflow()
    
    # Test words
    test_words = ["CAT", "DOG", "SUN", "MOON", "STAR", "UNKNOWN_WORD_XYZ"]
    
    print(f"Generating crossword clues for {len(test_words)} words...")
    print(f"Words: {', '.join(test_words)}\n")
    
    # Run workflow with monitoring
    result = workflow.generate_crossword_with_ai(
        words=test_words,
        difficulty="medium"
    )
    
    # Display results
    print("\n=== Results ===")
    for word_result in result["results"]:
        word = word_result["word"]
        if "error" in word_result:
            print(f"\n{word}: ❌ Error - {word_result['error']}")
        else:
            print(f"\n{word}: ✓ {word_result['source']}")
            for i, clue in enumerate(word_result.get("clues", [])[:3], 1):
                print(f"  {i}. {clue}")
    
    # Display validation
    print("\n=== Validation Results ===")
    validation = result["validation"]
    print(f"Success rate: {validation['success_rate']:.1%}")
    print(f"Successful: {validation['successful']}/{validation['total_words']}")
    
    if validation["issues"]:
        print("\nIssues found:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    # Display statistics
    print("\n=== Statistics ===")
    stats = result["stats"]
    print(f"AI Generated: {stats['ai_generated']} words")
    print(f"Database Hits: {stats['database_hits']} words")
    print(f"Errors: {stats['errors']} words")
    print(f"Total Tokens: {stats['total_tokens']}")
    print(f"Estimated Cost: ${stats['estimated_cost']:.4f}")
    
    # Demonstrate error scenarios
    demonstrate_error_scenarios()
    
    print("\n✅ Workflow completed with full monitoring!")
    print("\nCheck your Sentry dashboard at Insights → Agents to see:")
    print("- Complete prompt/response traces")
    print("- Tool usage patterns")
    print("- Error debugging with full context")
    print("- Performance metrics and token usage")


if __name__ == "__main__":
    main()