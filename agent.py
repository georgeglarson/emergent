"""
Autonomous Agent - Main loop and orchestration
"""
import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI

from state_manager import StateManager


class AutonomousAgent:
    """LLM-first autonomous coding agent"""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/emergent"):
        self.state_manager = StateManager(workspace_path)
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"  # Using available model
        self.tools = []  # Will be populated by tool modules
        self.running = False
    
    def run(self, initial_goal: Optional[str] = None, max_iterations: int = 100):
        """Main agent loop"""
        print("🤖 Autonomous Agent Starting...")
        print("=" * 60)
        
        # Load state and memory
        state = self.state_manager.load_state()
        memory = self.state_manager.load_memory()
        
        # Set initial goal if provided
        if initial_goal:
            self._set_goal(initial_goal)
            memory = self.state_manager.load_memory()
            state["metadata"]["goal_set"] = True
        
        self.running = True
        iteration = 0
        
        while self.running and iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            try:
                # Check if reflection is needed
                if self.state_manager.should_reflect(state):
                    print("🔄 Reflection time...")
                    self._reflect(state, memory)
                    state = self.state_manager.mark_reflection(state)
                    memory = self.state_manager.load_memory()
                
                # Build context for LLM
                context = self.state_manager.get_context_summary(state, memory)
                
                # Get next action from LLM
                action_result = self._decide_next_action(context, state, memory)
                
                if action_result["action"] == "complete":
                    print("✅ Goal achieved! Agent stopping.")
                    self.running = False
                    break
                
                if action_result["action"] == "wait_for_input":
                    print("⏸️  Agent needs input. Pausing.")
                    self.running = False
                    break
                
                # Execute the action
                result = self._execute_action(action_result)
                
                # Update state
                state = self.state_manager.add_action(
                    state, 
                    action_result["action"],
                    result
                )
                self.state_manager.save_state(state)
                
                # Print result
                status = "✓" if result["success"] else "✗"
                print(f"{status} {action_result['action']}: {result['summary']}")
                
            except KeyboardInterrupt:
                print("\n⏸️  Agent interrupted by user. Saving state...")
                self.state_manager.save_state(state)
                break
            
            except Exception as e:
                print(f"❌ Error: {e}")
                # Log error and continue
                result = {
                    "success": False,
                    "summary": f"Error: {str(e)}"
                }
                state = self.state_manager.add_action(state, "error", result)
                self.state_manager.save_state(state)
        
        print("\n" + "=" * 60)
        print("🤖 Agent stopped.")
        print(f"Total actions: {state['total_actions']}")
        
        return state
    
    def _set_goal(self, goal: str):
        """Set the initial goal"""
        goals_content = f"""# Goals

## Primary Objective
{goal}

## Success Criteria
- [ ] Goal clearly understood
- [ ] Approach identified
- [ ] Implementation complete
- [ ] Tests passing

## Constraints
- Work within the project directory
- Use available tools
- Document decisions

## Current Focus
Understanding the goal and planning approach
"""
        self.state_manager.update_memory_file("goals", goals_content)
        print(f"🎯 Goal set: {goal}")
    
    def _decide_next_action(self, context: str, state: Dict, memory: Dict) -> Dict[str, Any]:
        """Use LLM to decide the next action"""
        
        system_prompt = """You are an autonomous coding agent. You work independently toward goals using available tools.

Your memory and current state are provided in the context. Use this to maintain continuity across actions.

You have access to tools for:
- Searching code (search_files)
- Reading files (read_file)
- Editing files (edit_file)
- Running commands (run_command)
- Updating memory (update_memory)

Think step by step:
1. What is my current goal?
2. What have I done so far?
3. What is the next logical action?
4. Which tool should I use?

When you've achieved the goal, use the "complete" action.
If you need human input, use the "wait_for_input" action.

Always provide clear reasoning for your decisions."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context},
            {"role": "user", "content": "What should I do next? Provide your reasoning and the action to take."}
        ]
        
        # For now, return a simple structure (we'll add function calling next)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        # Parse response
        content = response.choices[0].message.content
        
        # Simple parsing for now - we'll improve this with function calling
        return {
            "action": "think",
            "reasoning": content,
            "details": {}
        }
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action using the appropriate tool"""
        
        action_type = action["action"]
        
        # For now, just return the reasoning as output
        if action_type == "think":
            print(f"\n💭 Agent reasoning:\n{action['reasoning']}\n")
            return {
                "success": True,
                "summary": "Reasoning complete"
            }
        
        # Placeholder for other actions
        return {
            "success": False,
            "summary": f"Action {action_type} not yet implemented"
        }
    
    def _reflect(self, state: Dict, memory: Dict):
        """Perform a reflection on recent actions"""
        
        recent_actions = state["recent_actions"][-10:] if state["recent_actions"] else []
        
        reflection_prompt = f"""Review your recent actions and current state:

## Recent Actions
{json.dumps(recent_actions, indent=2)}

## Current Memory
### Goals
{memory.get('goals', 'Not set')}

### Progress
{memory.get('progress', 'None')}

### Blockers
{memory.get('blockers', 'None')}

Reflect on:
1. Am I making progress toward my goal?
2. What's working well?
3. What's not working?
4. Should I change my approach?
5. What should I update in my memory?

Provide a brief reflection and any memory updates needed."""

        messages = [
            {"role": "system", "content": "You are reflecting on your recent work. Be honest and critical."},
            {"role": "user", "content": reflection_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        reflection = response.choices[0].message.content
        print(f"\n🔄 Reflection:\n{reflection}\n")
        
        # TODO: Parse reflection and update memory files accordingly


if __name__ == "__main__":
    agent = AutonomousAgent()
    
    # Example: Run with a simple goal
    goal = "Create a simple Python script that prints 'Hello, World!'"
    agent.run(initial_goal=goal, max_iterations=20)
