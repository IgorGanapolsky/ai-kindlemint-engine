#!/usr/bin/env python3
"""
Quick script to run the code hygiene orchestrator
"""
import os
import subprocess
import sys

def main():
    print("🧹 Running Code Hygiene Orchestrator")
    print("=" * 50)
    
    # First run analysis
    print("\n📊 Running analysis...")
    subprocess.run(["python", "agents/code_hygiene_orchestrator.py", "analyze"], check=True)
    
    # Ask if user wants to clean
    response = input("\n🤔 Do you want to clean the codebase? (y/n): ").lower()
    if response == 'y':
        print("\n🧹 Cleaning codebase...")
        subprocess.run(["python", "agents/code_hygiene_orchestrator.py", "clean"], check=True)
        print("\n✅ Cleanup complete!")
    else:
        print("\n❌ Cleanup skipped.")
    
    print("\n🔍 To run specific cleanup rules, use:")
    print("python agents/code_hygiene_orchestrator.py clean --interactive")

if __name__ == "__main__":
    main()