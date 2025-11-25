#!/usr/bin/env python3.11
"""
Emergent - Example Usage

This file demonstrates different ways to use Emergent.
"""

from agent_v2 import AutonomousAgentV2


def example_1_simple():
    """Simple usage - just provide a goal"""
    print("Example 1: Simple Usage")
    print("=" * 60)
    
    agent = AutonomousAgentV2()
    agent.run(
        initial_goal="Create a Python script that prints 'Hello, Emergent!'",
        max_iterations=20
    )


def example_2_web_project():
    """More complex - build a small web project"""
    print("\nExample 2: Web Project")
    print("=" * 60)
    
    agent = AutonomousAgentV2()
    agent.run(
        initial_goal="Create a simple Flask API with a /health endpoint that returns JSON",
        max_iterations=50
    )


def example_3_data_analysis():
    """Data analysis task"""
    print("\nExample 3: Data Analysis")
    print("=" * 60)
    
    agent = AutonomousAgentV2()
    agent.run(
        initial_goal="Create a Python script that generates random sales data and creates a visualization",
        max_iterations=50
    )


def example_4_long_running():
    """Long-running task with extended iterations"""
    print("\nExample 4: Long-Running Task")
    print("=" * 60)
    
    agent = AutonomousAgentV2()
    agent.run(
        initial_goal="Build a complete REST API for a todo list with CRUD operations and SQLite storage",
        max_iterations=200  # Allow extended operation
    )


def example_5_custom_workspace():
    """Use a custom workspace directory"""
    print("\nExample 5: Custom Workspace")
    print("=" * 60)
    
    agent = AutonomousAgentV2(workspace_path="/tmp/my-project")
    agent.run(
        initial_goal="Create a markdown document explaining Python decorators with examples",
        max_iterations=30
    )


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                       EMERGENT                            ║
║                                                           ║
║              The agent that builds itself                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Choose an example to run:

1. Simple Usage - Hello World
2. Web Project - Flask API
3. Data Analysis - Generate and visualize data
4. Long-Running - Complete REST API
5. Custom Workspace - Use different directory

Or press Ctrl+C to exit
""")
    
    try:
        choice = input("Enter choice (1-5): ").strip()
        
        examples = {
            "1": example_1_simple,
            "2": example_2_web_project,
            "3": example_3_data_analysis,
            "4": example_4_long_running,
            "5": example_5_custom_workspace
        }
        
        if choice in examples:
            examples[choice]()
        else:
            print("Invalid choice. Please run again and select 1-5.")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
