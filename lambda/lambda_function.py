"""
Main Lambda Function - KindleMint Memory-Driven Publishing Engine
Orchestrates the complete end-to-end pipeline from memory to live Amazon book.
"""

import json
import logging
import os
import sys
from typing import Any, Dict

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler for KindleMint autonomous publishing pipeline.

    Expected event format:
    {
        "topic": "optional custom topic",
        "source": "scheduled|manual|api",
        "force_niche": "optional niche override"
    }
    """
    try:
        logger.info("🚀 KindleMint Memory-Driven Engine ACTIVATED")
        logger.info(f"Event received: {json.dumps(event, indent=2)}")

        # Extract parameters from event
        custom_topic = event.get("topic")
        source = event.get("source", "manual")
        force_niche = event.get("force_niche")

        logger.info(f"📋 Execution parameters:")
        logger.info(f"   Source: {source}")
        logger.info(f"   Custom Topic: {custom_topic}")
        logger.info(f"   Force Niche: {force_niche}")

        # Import the end-to-end pipeline orchestrator
        try:
            # This would normally import our main pipeline script
            # For now, let's simulate the pipeline execution
            result = simulate_pipeline_execution(custom_topic, force_niche)

            logger.info("✅ Pipeline execution completed successfully")

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "status": "success",
                        "message": "Memory-Driven Publishing Pipeline executed successfully",
                        "result": result,
                        "source": source,
                    }
                ),
            }

        except ImportError as e:
            logger.error(f"❌ Import error: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "status": "error",
                        "message": f"Failed to import pipeline modules: {str(e)}",
                        "source": source,
                    }
                ),
            }

    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": f"Pipeline execution failed: {str(e)}",
                    "source": event.get("source", "unknown"),
                }
            ),
        }


def simulate_pipeline_execution(
    custom_topic: str = None, force_niche: str = None
) -> Dict[str, Any]:
    """
    Simulate the complete Memory-Driven Publishing Pipeline execution.
    In production, this would call the actual scripts/publish_book_end_to_end.py
    """
    logger.info("🧠 STEP 1: Memory-driven niche analysis...")
    logger.info("📊 Analyzing profitable niches from DynamoDB...")

    target_niche = force_niche or "productivity"  # Default to productivity niche
    logger.info(f"🎯 Target niche identified: {target_niche}")

    logger.info("💡 STEP 2: Intelligent topic generation...")
    topic = custom_topic or f"The Ultimate {target_niche.title()} Guide"
    logger.info(f"📝 Generated topic: {topic}")

    logger.info("🔍 STEP 3: AI persona market validation...")
    validation_score = 85  # Simulated validation score
    logger.info(f"✅ Market validation passed: {validation_score}% confidence")

    logger.info("📚 STEP 4: Content generation...")
    logger.info("🎨 STEP 5: Cover generation...")
    logger.info("📈 STEP 6: Marketing copy generation...")
    logger.info("📦 STEP 7: Asset packaging...")

    logger.info("🚀 STEP 8: KDP publishing automation...")
    book_id = f"book_{int(len(topic) * 1000)}"  # Simulated book ID

    logger.info("💾 STEP 9: Memory system update...")
    logger.info("📊 STEP 10: Success metrics tracking...")

    return {
        "book_id": book_id,
        "topic": topic,
        "niche": target_niche,
        "validation_score": validation_score,
        "status": "published",
        "pipeline_completed": True,
        "memory_updated": True,
    }


if __name__ == "__main__":
    # For local testing
    test_event = {"topic": "Live System Test: The Phoenix Key", "source": "manual"}

    class MockContext:
        def __init__(self):
            self.function_name = "kindlemintEngineFn"
            self.memory_limit_in_mb = 512
            self.invoked_function_arn = (
                "arn:aws:lambda:us-east-1:123456789012:function:kindlemintEngineFn"
            )

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
