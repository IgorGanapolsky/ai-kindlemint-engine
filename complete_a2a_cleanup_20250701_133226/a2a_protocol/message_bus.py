#!/usr/bin/env python3
"""
A2A Message Bus - Central communication hub for agents
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional

from .base_agent import A2AMessage, A2ARegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AMessageBus:
    """Central message bus for A2A communication"""

    def __init__(self, registry: A2ARegistry):
        self.registry = registry
        self.message_queue = asyncio.Queue()
        self.message_history: List[A2AMessage] = []
        self.response_callbacks: Dict[str, asyncio.Future] = {}
        self.running = False
        logger.info("A2A Message Bus initialized")

    async def start(self):
        """Start the message bus"""
        self.running = True
        logger.info("Message bus started")

        # Start message processing loop
        asyncio.create_task(self._process_messages())

    async def stop(self):
        """Stop the message bus"""
        self.running = False
        logger.info("Message bus stopped")

    async def send_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Send a message through the bus"""
        # Add to history
        self.message_history.append(message)

        # Put in queue for processing
        await self.message_queue.put(message)

        # If it's a request, wait for response
        if message.message_type == "request":
            # Create a future for the response
            response_future = asyncio.Future()
            self.response_callbacks[message.message_id] = response_future

            try:
                # Wait for response with timeout
                response = await asyncio.wait_for(response_future, timeout=30.0)
                return response
            except asyncio.TimeoutError:
                logger.error(
                    f"Timeout waiting for response to message {message.message_id}"
                )
                del self.response_callbacks[message.message_id]
                return None

        return None

    async def _process_messages(self):
        """Process messages from the queue"""
        while self.running:
            try:
                # Get message from queue
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)

                # Find the target agent
                agent = self.registry.get_agent(message.receiver_id)
                if not agent:
                    logger.error(f"Agent not found: {message.receiver_id}")
                    # Send error response if it's a request
                    if message.message_type == "request":
                        error_response = message.create_error(
                            "message-bus", f"Agent {message.receiver_id} not found"
                        )
                        await self._deliver_response(error_response)
                    continue

                # Process message in the agent
                try:
                    response = agent.process_message(message)

                    # If it's a response to a request, deliver it
                    if response.message_type in ["response", "error"]:
                        await self._deliver_response(response)

                except Exception as e:
                    logger.error(f"Error processing message in agent: {e}")
                    if message.message_type == "request":
                        error_response = message.create_error(
                            message.receiver_id, f"Processing error: {str(e)}"
                        )
                        await self._deliver_response(error_response)

            except asyncio.TimeoutError:
                # No messages in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")

    async def _deliver_response(self, response: A2AMessage):
        """Deliver a response to the waiting sender"""
        if response.correlation_id in self.response_callbacks:
            future = self.response_callbacks[response.correlation_id]
            future.set_result(response)
            del self.response_callbacks[response.correlation_id]
        else:
            logger.warning(f"No callback found for response {response.correlation_id}")

    def get_message_history(self, limit: int = 100) -> List[Dict]:
        """Get recent message history"""
        return [
            {
                "message_id": msg.message_id,
                "timestamp": msg.timestamp,
                "sender": msg.sender_id,
                "receiver": msg.receiver_id,
                "action": msg.action,
                "type": msg.message_type,
            }
            for msg in self.message_history[-limit:]
        ]


class A2AOrchestrator:
    """Orchestrator for coordinating A2A agents"""

        """  Init  """
def __init__(self, registry: A2ARegistry, message_bus: A2AMessageBus):
        self.registry = registry
        self.message_bus = message_bus
        self.agent_id = "orchestrator-001"
        logger.info("A2A Orchestrator initialized")

    async def generate_and_validate_puzzle(self, difficulty: str = "medium") -> Dict:
        """Orchestrate puzzle generation and validation"""
        logger.info(f"Starting puzzle generation workflow for {difficulty} difficulty")

        # For this demo, we'll simulate puzzle generation
        # In the full implementation, this would call the PuzzleGeneratorAgent

        # Simulate a generated puzzle
        test_puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]

        test_solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

        # Step 1: Validate the puzzle
        validation_message = A2AMessage.create_request(
            sender_id=self.agent_id,
            receiver_id="puzzle-validator-001",
            action="validate_puzzle",
            payload={"puzzle_grid": test_puzzle, "solution_grid": test_solution},
        )

        validation_response = await self.message_bus.send_message(validation_message)

        if not validation_response:
            return {"error": "Validation timeout"}

        validation_result = validation_response.payload

        # Step 2: Check puzzle quality
        quality_message = A2AMessage.create_request(
            sender_id=self.agent_id,
            receiver_id="puzzle-validator-001",
            action="check_puzzle_quality",
            payload={"puzzle_grid": test_puzzle, "difficulty": difficulty},
        )

        quality_response = await self.message_bus.send_message(quality_message)

        if not quality_response:
            return {"error": "Quality check timeout"}

        quality_result = quality_response.payload

        # Combine results
        return {
            "puzzle_id": "demo-001",
            "difficulty": difficulty,
            "validation": validation_result,
            "quality": quality_result,
            "workflow_status": "completed",
        }

    async def validate_book_puzzles(self, puzzles: List[Dict]) -> Dict:
        """Validate all puzzles for a book"""
        logger.info(f"Starting batch validation for {len(puzzles)} puzzles")

        # Send batch validation request
        batch_message = A2AMessage.create_request(
            sender_id=self.agent_id,
            receiver_id="puzzle-validator-001",
            action="validate_batch",
            payload={"puzzles": puzzles},
        )

        batch_response = await self.message_bus.send_message(batch_message)

        if not batch_response:
            return {"error": "Batch validation timeout"}

        return batch_response.payload


# Demo script
async     """Demo A2A System"""
def demo_a2a_system():
    """Demonstrate the A2A system in action"""
    print("🚀 Starting A2A Protocol Demo")
    print("=" * 60)

    # Create registry and message bus
    registry = A2ARegistry()
    message_bus = A2AMessageBus(registry)

    # Start message bus
    await message_bus.start()

    # Create and register agents
    from puzzle_validator_agent import PuzzleValidatorAgent

    validator = PuzzleValidatorAgent()
    registry.register(validator)

    print(f"✅ Registered {len(registry.agents)} agents")
    print(f"📋 Available capabilities: {list(registry.capabilities_index.keys())}")

    # Create orchestrator
    orchestrator = A2AOrchestrator(registry, message_bus)

    # Run a workflow
    print("\n🔄 Running puzzle generation and validation workflow...")
    result = await orchestrator.generate_and_validate_puzzle("easy")

    print("\n📊 Workflow Result:")
    print(json.dumps(result, indent=2))

    # Show message history
    print(f"\n📨 Message History ({len(message_bus.message_history)} messages):")
    for msg in message_bus.get_message_history(limit=5):
        print(
            f"  - {msg['timestamp']}: {msg['sender']
                                       } -> {msg['receiver']} ({msg['action']})"
        )

    # Test with a blank puzzle (should fail)
    print("\n🔄 Testing with blank puzzle...")
    blank_puzzle = [[0] * 9 for __var in range(9)]

    blank_message = A2AMessage.create_request(
        sender_id="test-client",
        receiver_id="puzzle-validator-001",
        action="validate_puzzle",
        payload={
            "puzzle_grid": blank_puzzle,
            "solution_grid": [[1, 2, 3, 4, 5, 6, 7, 8, 9]] * 9,  # Invalid solution
        },
    )

    blank_response = await message_bus.send_message(blank_message)
    if blank_response:
        print("❌ Blank puzzle validation result:")
        print(json.dumps(blank_response.payload, indent=2))

    # Stop message bus
    await message_bus.stop()

    print("\n✅ A2A Protocol Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_a2a_system())
