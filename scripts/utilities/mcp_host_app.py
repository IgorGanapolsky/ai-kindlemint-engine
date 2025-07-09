#!/usr/bin/env python3
"""
MCP Host Application
Accepts natural language prompts and routes them to appropriate MCP tools
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import httpx
import openai

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class KindlemintMCPHost:
    """Host application that routes LLM requests to MCP tools"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:8011"):
        self.mcp_server_url = mcp_server_url
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Available MCP tools with descriptions
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_sudoku_book",
                    "description": "Generate a complete Sudoku puzzle book ready for KDP publishing",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Book title"},
                            "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "description": "Puzzle difficulty"},
                            "puzzle_count": {"type": "integer", "description": "Number of puzzles"},
                            "large_print": {"type": "boolean", "description": "Use large print format"},
                            "include_solutions": {"type": "boolean", "description": "Include solution pages"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "generate_crossword_book",
                    "description": "Generate a crossword puzzle book for KDP",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Book title"},
                            "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                            "puzzle_count": {"type": "integer", "description": "Number of crosswords"},
                            "theme": {"type": "string", "description": "Optional theme like 'Animals' or 'Travel'"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_lead_magnet", 
                    "description": "Generate a free puzzle sampler for lead generation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "puzzle_type": {"type": "string", "enum": ["sudoku", "crossword"]},
                            "count": {"type": "integer", "description": "Number of sample puzzles"},
                            "title": {"type": "string", "description": "Lead magnet title"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_book_stats",
                    "description": "Get statistics about generated books",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    async def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/tools/{tool_name}",
                    json=params,
                    timeout=300.0  # 5 minutes for book generation
                )
                return response.json()
        except Exception as e:
            return {"error": f"Failed to call MCP tool {tool_name}: {str(e)}"}

    async def process_prompt(self, user_prompt: str) -> str:
        """Process a user prompt and generate appropriate response"""
        try:
            # Use OpenAI to determine which tool(s) to call
            messages = [
                {
                    "role": "system", 
                    "content": """You are a helpful assistant that creates puzzle books for Kindle Direct Publishing (KDP). 
                    
You have access to tools that can generate:
- Sudoku books (various difficulties, large print options)
- Crossword books (themed or general)
- Lead magnets (free puzzle samplers for email capture)
- Book statistics

When a user asks to create a book, choose appropriate parameters and call the right tool.
Always suggest realistic parameters like 50-100 puzzles for full books, 10-20 for samplers.
For titles, suggest professional book names that would sell well on Amazon KDP."""
                },
                {"role": "user", "content": user_prompt}
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.available_tools,
                tool_choice="auto"
            )

            # Check if AI wants to call tools
            if response.choices[0].message.tool_calls:
                results = []
                
                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    params = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Calling tool: {tool_name}")
                    print(f"📋 Parameters: {params}")
                    
                    # Call the MCP tool
                    result = await self.call_mcp_tool(tool_name, params)
                    results.append({
                        "tool": tool_name,
                        "params": params,
                        "result": result
                    })

                # Format response based on results
                response_parts = []
                for r in results:
                    if r["result"].get("status") == "success":
                        if r["tool"] == "generate_sudoku_book":
                            response_parts.append(
                                f"✅ **Sudoku Book Created Successfully!**\n"
                                f"📖 Title: {r['result']['title']}\n"
                                f"📄 PDF: `{r['result']['pdf_path']}`\n"
                                f"🧩 Puzzles: {r['result']['puzzle_count']} ({r['result']['difficulty']} difficulty)\n"
                                f"📏 Format: {'Large Print' if r['result']['large_print'] else 'Standard'}\n"
                                f"💾 Size: {r['result']['file_size_mb']} MB\n"
                                f"🚀 Ready for KDP upload!"
                            )
                        elif r["tool"] == "generate_crossword_book":
                            response_parts.append(
                                f"✅ **Crossword Book Created Successfully!**\n"
                                f"📖 Title: {r['result']['title']}\n"
                                f"📄 PDF: `{r['result']['pdf_path']}`\n"
                                f"🎯 Puzzles: {r['result']['puzzle_count']} ({r['result']['difficulty']} difficulty)\n"
                                f"🎨 Theme: {r['result'].get('theme', 'General')}\n"
                                f"🚀 Ready for KDP upload!"
                            )
                        elif r["tool"] == "create_lead_magnet":
                            response_parts.append(
                                f"🎁 **Lead Magnet Created Successfully!**\n"
                                f"📖 Title: {r['result']['title']}\n"
                                f"📄 PDF: `{r['result']['pdf_path']}`\n"
                                f"🧩 Type: {r['result']['puzzle_type']} ({r['result']['count']} puzzles)\n"
                                f"🔗 Download URL: {r['result']['download_url']}\n"
                                f"📧 Perfect for email capture!"
                            )
                        elif r["tool"] == "get_book_stats":
                            books = r["result"]["books"]
                            response_parts.append(
                                f"📊 **Book Statistics**\n"
                                f"📚 Total Books: {r['result']['total_books']}\n"
                                + (f"\n📖 Recent Books:\n" + "\n".join([
                                    f"  • {book['title']} ({book['size_mb']} MB)"
                                    for book in books[:5]
                                ]) if books else "")
                            )
                    else:
                        response_parts.append(
                            f"❌ **Error with {r['tool']}**\n"
                            f"Error: {r['result'].get('error', 'Unknown error')}"
                        )

                return "\n\n".join(response_parts)
            
            else:
                # AI didn't call tools, return its text response
                return response.choices[0].message.content

        except Exception as e:
            return f"❌ Error processing prompt: {str(e)}"

    async def interactive_mode(self):
        """Run interactive mode for testing"""
        print("🤖 Kindlemint MCP Host - Interactive Mode")
        print("Type 'quit' to exit, 'help' for examples")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                    
                if user_input.lower() == 'help':
                    print("""
🔤 Example prompts:
• "Create a large print Sudoku book with 100 medium puzzles called 'Brain Teasers Volume 3'"
• "Generate a crossword book about animals with 50 puzzles"  
• "Make a free Sudoku sampler with 15 puzzles for lead generation"
• "Show me stats on all my generated books"
• "Create a hard difficulty Sudoku book for advanced players"
                    """)
                    continue
                
                print("🤔 Processing...")
                response = await self.process_prompt(user_input)
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point"""
    host = KindlemintMCPHost()
    
    if len(sys.argv) > 1:
        # Process single prompt from command line
        prompt = " ".join(sys.argv[1:])
        response = await host.process_prompt(prompt)
        print(response)
    else:
        # Interactive mode
        await host.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())