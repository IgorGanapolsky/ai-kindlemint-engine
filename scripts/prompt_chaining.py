#!/usr/bin/env python3
"""
Prompt Chaining Utility
Breaks complex tasks into multiple focused prompts for better results
Implements structured prompt workflows for content generation
"""

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptChaining")


class ChainStep(Enum):
    """Types of steps in a prompt chain"""

    GENERATE = "generate"
    EVALUATE = "evaluate"
    REFINE = "refine"
    SELECT = "select"
    COMBINE = "combine"
    VALIDATE = "validate"


@dataclass
class PromptStep:
    """Represents a single step in a prompt chain"""

    name: str
    step_type: ChainStep
    prompt_template: str
    input_keys: List[str]
    output_key: str
    validator: Optional[Callable] = None
    max_retries: int = 3
    temperature: float = 0.7

    def format_prompt(self, context: Dict[str, Any]) -> str:
        """Format the prompt template with context values"""
        try:
            return self.prompt_template.format(
                **{k: context.get(k, "") for k in self.input_keys}
            )
        except KeyError as e:
            logger.error(f"Missing key in context: {e}")
            raise


@dataclass
class ChainResult:
    """Result of executing a prompt chain"""

    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    steps_completed: int = 0
    errors: List[str] = field(default_factory=list)


class PromptChain:
    """Manages execution of chained prompts"""

    def __init__(self, name: str, steps: List[PromptStep]):
        self.name = name
        self.steps = steps
        self.context = {}

    def execute(self, initial_context: Dict[str, Any]) -> ChainResult:
        """Execute the prompt chain with given initial context"""
        logger.info(f"Executing prompt chain: {self.name}")
        start_time = time.time()

        self.context = initial_context.copy()
        result = ChainResult(success=True)

        for i, step in enumerate(self.steps):
            logger.info(
                f"Executing step {i + 1}/{len(self.steps)}: {step.name}")

            try:
                step_output = self._execute_step(step)
                self.context[step.output_key] = step_output
                result.outputs[step.output_key] = step_output
                result.steps_completed += 1

            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                result.success = False
                result.errors.append(f"Step {step.name}: {str(e)}")
                break

        result.execution_time = time.time() - start_time
        logger.info(f"Chain completed in {result.execution_time:.2f}s")

        return result

    def _execute_step(self, step: PromptStep) -> Any:
        """Execute a single step in the chain"""
        # Format the prompt
        prompt = step.format_prompt(self.context)

        # Simulate LLM call (in production, this would call actual LLM)
        # For now, we'll implement mock responses for demonstration
        response = self._mock_llm_call(step, prompt)

        # Validate response if validator provided
        if step.validator and not step.validator(response):
            raise ValueError(f"Validation failed for step {step.name}")

        return response

    def _mock_llm_call(self, step: PromptStep, prompt: str) -> Any:
        """Mock LLM call for demonstration"""
        # In production, this would integrate with OpenAI, Claude, etc.

        mock_responses = {
            ChainStep.GENERATE: self._mock_generate,
            ChainStep.EVALUATE: self._mock_evaluate,
            ChainStep.REFINE: self._mock_refine,
            ChainStep.SELECT: self._mock_select,
            ChainStep.COMBINE: self._mock_combine,
            ChainStep.VALIDATE: self._mock_validate,
        }

        handler = mock_responses.get(step.step_type, self._mock_generate)
        return handler(step, prompt)

    def _mock_generate(self, step: PromptStep, prompt: str) -> Any:
        """Mock generation response"""
        if "title" in step.output_key:
            return [
                "Mind-Bending Crosswords: Volume 1",
                "Daily Brain Teasers: Crossword Edition",
                "The Ultimate Crossword Challenge",
                "Relaxing Crosswords for Coffee Breaks",
                "Family Fun Crossword Collection",
            ]
        elif "description" in step.output_key:
            return "Challenge your mind with 50 expertly crafted crossword puzzles..."
        else:
            return f"Generated content for {step.name}"

    def _mock_evaluate(self, step: PromptStep, prompt: str) -> Any:
        """Mock evaluation response"""
        return {
            "scores": [85, 72, 90, 78, 83],
            "feedback": [
                "Good variety",
                "Appeals to target audience",
                "Clear value prop",
            ],
        }

    def _mock_refine(self, step: PromptStep, prompt: str) -> Any:
        """Mock refinement response"""
        return "Enhanced: " + self.context.get("selected_title", "Title")

    def _mock_select(self, step: PromptStep, prompt: str) -> Any:
        """Mock selection response"""
        titles = self.context.get("title_options", [])
        return titles[0] if titles else "Default Title"

    def _mock_combine(self, step: PromptStep, prompt: str) -> Any:
        """Mock combination response"""
        return {"combined": True, "result": "Combined output"}

    def _mock_validate(self, step: PromptStep, prompt: str) -> Any:
        """Mock validation response"""
        return {"valid": True, "issues": []}


class PromptChainLibrary:
    """Library of pre-built prompt chains for common tasks"""

    @staticmethod
    def book_metadata_chain() -> PromptChain:
        """Chain for generating comprehensive book metadata"""
        steps = [
            # Step 1: Generate title options
            PromptStep(
                name="generate_titles",
                step_type=ChainStep.GENERATE,
                prompt_template="""Generate 5 compelling book titles for a {puzzle_type} puzzle book.
                Target audience: {target_audience}
                Difficulty: {difficulty}
                Theme: {theme}

                Requirements:
                - Titles should be clear and appealing
                - Include the puzzle type
                - Convey the difficulty/audience
                - Be unique and memorable

                Format: Return as a JSON list of strings.""",
                input_keys=["puzzle_type", "target_audience",
                            "difficulty", "theme"],
                output_key="title_options",
            ),
            # Step 2: Evaluate titles
            PromptStep(
                name="evaluate_titles",
                step_type=ChainStep.EVALUATE,
                prompt_template="""Evaluate these book titles for market appeal:
                {title_options}

                Target audience: {target_audience}

                For each title, provide:
                1. Market appeal score (0-100)
                2. Strengths
                3. Potential concerns

                Format: Return as JSON with scores and feedback.""",
                input_keys=["title_options", "target_audience"],
                output_key="title_evaluation",
            ),
            # Step 3: Select best title
            PromptStep(
                name="select_title",
                step_type=ChainStep.SELECT,
                prompt_template="""Based on these evaluations:
                {title_evaluation}

                Select the best title from: {title_options}

                Return the selected title as a string.""",
                input_keys=["title_evaluation", "title_options"],
                output_key="selected_title",
            ),
            # Step 4: Generate subtitle
            PromptStep(
                name="generate_subtitle",
                step_type=ChainStep.GENERATE,
                prompt_template="""Create a compelling subtitle for this book:
                Title: {selected_title}
                Type: {puzzle_type}

                The subtitle should:
                - Highlight the value proposition
                - Mention the number of puzzles
                - Appeal to {target_audience}

                Return as a single string.""",
                input_keys=["selected_title",
                            "puzzle_type", "target_audience"],
                output_key="subtitle",
            ),
            # Step 5: Generate description
            PromptStep(
                name="generate_description",
                step_type=ChainStep.GENERATE,
                prompt_template="""Write a compelling book description:
                Title: {selected_title}
                Subtitle: {subtitle}
                Type: {puzzle_type}
                Difficulty: {difficulty}

                Requirements:
                - 150-200 words
                - Highlight benefits
                - Include features
                - Call to action

                Return as formatted text.""",
                input_keys=["selected_title", "subtitle",
                            "puzzle_type", "difficulty"],
                output_key="description",
            ),
            # Step 6: Generate keywords
            PromptStep(
                name="generate_keywords",
                step_type=ChainStep.GENERATE,
                prompt_template="""Generate 7 relevant keywords for:
                Title: {selected_title}
                Description: {description}

                Keywords should be:
                - Relevant for Amazon KDP
                - Mix of broad and specific
                - Include puzzle type variations

                Return as JSON list.""",
                input_keys=["selected_title", "description"],
                output_key="keywords",
            ),
        ]

        return PromptChain("book_metadata", steps)

    @staticmethod
    def puzzle_theme_chain() -> PromptChain:
        """Chain for developing puzzle themes"""
        steps = [
            # Generate theme ideas
            PromptStep(
                name="generate_themes",
                step_type=ChainStep.GENERATE,
                prompt_template="""Generate 10 unique theme ideas for {puzzle_type} puzzles.
                Target audience: {target_audience}
                Season/Occasion: {season}

                Themes should be:
                - Engaging and relevant
                - Appropriate for the audience
                - Feasible for puzzle creation

                Return as JSON list with theme name and brief description.""",
                input_keys=["puzzle_type", "target_audience", "season"],
                output_key="theme_ideas",
            ),
            # Evaluate themes
            PromptStep(
                name="evaluate_themes",
                step_type=ChainStep.EVALUATE,
                prompt_template="""Evaluate these puzzle themes:
                {theme_ideas}

                Criteria:
                - Market appeal
                - Content availability
                - Uniqueness
                - Target audience fit

                Return evaluation scores and feedback as JSON.""",
                input_keys=["theme_ideas"],
                output_key="theme_evaluation",
            ),
            # Select and refine
            PromptStep(
                name="refine_theme",
                step_type=ChainStep.REFINE,
                prompt_template="""Based on evaluation:
                {theme_evaluation}

                Select and refine the best theme.
                Add specific subcategories and content ideas.

                Return as detailed theme specification.""",
                input_keys=["theme_evaluation"],
                output_key="refined_theme",
            ),
        ]

        return PromptChain("puzzle_theme", steps)

    @staticmethod
    def content_optimization_chain() -> PromptChain:
        """Chain for optimizing puzzle content based on QA feedback"""
        steps = [
            # Analyze issues
            PromptStep(
                name="analyze_issues",
                step_type=ChainStep.EVALUATE,
                prompt_template="""Analyze these QA issues:
                {qa_issues}

                Categorize by:
                - Severity
                - Fix complexity
                - Root cause

                Return analysis as structured JSON.""",
                input_keys=["qa_issues"],
                output_key="issue_analysis",
            ),
            # Generate fixes
            PromptStep(
                name="generate_fixes",
                step_type=ChainStep.GENERATE,
                prompt_template="""Based on analysis:
                {issue_analysis}

                Generate specific fixes for each issue.
                Include:
                - Action steps
                - Expected outcome
                - Implementation priority

                Return as actionable fix list.""",
                input_keys=["issue_analysis"],
                output_key="fix_proposals",
            ),
            # Validate fixes
            PromptStep(
                name="validate_fixes",
                step_type=ChainStep.VALIDATE,
                prompt_template="""Validate proposed fixes:
                {fix_proposals}

                Check for:
                - Completeness
                - Feasibility
                - Side effects

                Return validation results.""",
                input_keys=["fix_proposals"],
                output_key="validated_fixes",
            ),
        ]

        return PromptChain("content_optimization", steps)


def example_usage():
    """Demonstrate prompt chaining usage"""

    # Example 1: Generate book metadata
    print("Example 1: Generating Book Metadata")
    print("-" * 50)

    metadata_chain = PromptChainLibrary.book_metadata_chain()

    initial_context = {
        "puzzle_type": "crossword",
        "target_audience": "adults seeking mental stimulation",
        "difficulty": "medium",
        "theme": "World Travel",
    }

    result = metadata_chain.execute(initial_context)

    if result.success:
        print(f"✅ Metadata generation successful!")
        print(f"📚 Title: {result.outputs.get('selected_title')}")
        print(f"📝 Subtitle: {result.outputs.get('subtitle')}")
        print(f"🔑 Keywords: {result.outputs.get('keywords')}")
    else:
        print(f"❌ Generation failed: {result.errors}")

    # Example 2: Develop puzzle theme
    print("\n\nExample 2: Developing Puzzle Theme")
    print("-" * 50)

    theme_chain = PromptChainLibrary.puzzle_theme_chain()

    theme_context = {
        "puzzle_type": "word_search",
        "target_audience": "children aged 8-12",
        "season": "summer vacation",
    }

    theme_result = theme_chain.execute(theme_context)

    if theme_result.success:
        print(f"✅ Theme development successful!")
        print(f"🎨 Refined theme: {theme_result.outputs.get('refined_theme')}")
    else:
        print(f"❌ Theme development failed: {theme_result.errors}")


def main():
    """CLI interface for prompt chaining"""
    import argparse

    parser = argparse.ArgumentParser(description="Prompt Chaining Utility")
    parser.add_argument(
        "chain", choices=["metadata", "theme", "optimize"], help="Chain type to execute"
    )
    parser.add_argument("--puzzle-type", help="Type of puzzle")
    parser.add_argument("--audience", help="Target audience")
    parser.add_argument("--difficulty", help="Difficulty level")
    parser.add_argument("--theme", help="Puzzle theme")
    parser.add_argument("--input", help="JSON file with input context")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    # Load context
    if args.input:
        with open(args.input) as f:
            context = json.load(f)
    else:
        context = {
            "puzzle_type": args.puzzle_type or "crossword",
            "target_audience": args.audience or "general audience",
            "difficulty": args.difficulty or "medium",
            "theme": args.theme or "general",
        }

    # Select and execute chain
    chains = {
        "metadata": PromptChainLibrary.book_metadata_chain(),
        "theme": PromptChainLibrary.puzzle_theme_chain(),
        "optimize": PromptChainLibrary.content_optimization_chain(),
    }

    chain = chains[args.chain]
    result = chain.execute(context)

    # Display results
    print(f"\n📊 PROMPT CHAIN RESULTS")
    print(f"{'=' * 50}")
    print(f"⛓️  Chain: {chain.name}")
    print(f"✅ Success: {result.success}")
    print(f"⏱️  Time: {result.execution_time:.2f}s")
    print(f"📝 Steps: {result.steps_completed}/{len(chain.steps)}")

    if result.success:
        print(f"\n📤 Outputs:")
        for key, value in result.outputs.items():
            print(f"  {key}: {value}")
    else:
        print(f"\n❌ Errors:")
        for error in result.errors:
            print(f"  • {error}")

    # Save results if requested
    if args.output:
        output_data = {
            "chain": chain.name,
            "context": context,
            "result": {
                "success": result.success,
                "outputs": result.outputs,
                "errors": result.errors,
                "execution_time": result.execution_time,
            },
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Results saved to: {args.output}")


if __name__ == "__main__":
    # Run example if no arguments provided
    if len(sys.argv) == 1:
        example_usage()
    else:
        main()
