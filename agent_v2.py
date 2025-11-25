"""
Autonomous Agent V2 - With integrated tools and function calling
"""
import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI

from state_manager import StateManager
from tools.file_tools import FileTools
from tools.command_tools import CommandTools


class AutonomousAgentV2:
    """LLM-first autonomous coding agent with full tool integration"""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/emergent"):
        self.workspace_path = workspace_path
        self.state_manager = StateManager(workspace_path)
        self.file_tools = FileTools(workspace_path)
        self.command_tools = CommandTools(workspace_path)
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"
        self.running = False
        
        # Define available tools for function calling
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Search for text in project files using ripgrep. Returns matches with file paths and line numbers.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The text to search for"
                            },
                            "file_pattern": {
                                "type": "string",
                                "description": "Optional file pattern (e.g., '*.py')",
                                "default": "*"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file. Returns the file content and metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file relative to project directory"
                            },
                            "start_line": {
                                "type": "integer",
                                "description": "Optional starting line number"
                            },
                            "end_line": {
                                "type": "integer",
                                "description": "Optional ending line number"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file (creates or overwrites). Use this to create new files or update existing ones.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file relative to project directory"
                            },
                            "content": {
                                "type": "string",
                                "description": "The complete content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files in a directory with metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory path relative to project (default: '.')",
                                "default": "."
                            },
                            "pattern": {
                                "type": "string",
                                "description": "File pattern to match (default: '*')",
                                "default": "*"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Run a shell command in the project directory. Returns structured output with error analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The shell command to execute"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_project_structure",
                    "description": "Get an overview of the project directory structure.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "max_depth": {
                                "type": "integer",
                                "description": "Maximum depth to traverse (default: 3)",
                                "default": 3
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_memory",
                    "description": "Update one of the memory files (goals, progress, decisions, blockers).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_type": {
                                "type": "string",
                                "enum": ["goals", "progress", "decisions", "blockers"],
                                "description": "Which memory file to update"
                            },
                            "content": {
                                "type": "string",
                                "description": "The new content for the memory file"
                            }
                        },
                        "required": ["file_type", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_goal",
                    "description": "Mark the current goal as complete and stop the agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Summary of what was accomplished"
                            }
                        },
                        "required": ["summary"]
                    }
                }
            }
        ]
    
    def run(self, initial_goal: Optional[str] = None, max_iterations: int = 100):
        """Main agent loop with function calling"""
        print("🤖 Autonomous Agent V2 Starting...")
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
        
        # Conversation history for context
        messages = []
        
        while self.running and iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"Iteration {iteration}/{max_iterations}")
            print(f"{'='*60}")
            
            try:
                # Check if reflection is needed
                if self.state_manager.should_reflect(state):
                    print("\n🔄 Reflection time...")
                    self._reflect(state, memory, messages)
                    state = self.state_manager.mark_reflection(state)
                    memory = self.state_manager.load_memory()
                
                # Build context
                context = self.state_manager.get_context_summary(state, memory)
                
                # Add context to messages if this is first iteration or after reflection
                if iteration == 1 or state["actions_since_reflection"] == 0:
                    messages = [
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": context}
                    ]
                
                # Get next action from LLM with function calling
                print("\n💭 Thinking...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools_schema,
                    tool_choice="auto",
                    temperature=0.7
                )
                
                assistant_message = response.choices[0].message
                messages.append(assistant_message)
                
                # Check if LLM wants to call a tool
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        print(f"\n🔧 Calling: {function_name}")
                        print(f"   Args: {json.dumps(function_args, indent=2)}")
                        
                        # Execute the tool
                        result = self._execute_tool(function_name, function_args)
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                        
                        # Update state
                        state = self.state_manager.add_action(
                            state,
                            f"{function_name}({json.dumps(function_args)})",
                            result
                        )
                        
                        # Print result
                        status = "✓" if result["success"] else "✗"
                        print(f"   {status} {result['summary']}")
                        
                        # Check if goal is complete
                        if function_name == "complete_goal":
                            print(f"\n✅ Goal Complete: {function_args['summary']}")
                            self.running = False
                            break
                
                else:
                    # LLM responded without tool call - just thinking
                    if assistant_message.content:
                        print(f"\n💭 {assistant_message.content}")
                
                # Save state after each iteration
                self.state_manager.save_state(state)
                
                # Limit message history to prevent context overflow
                if len(messages) > 20:
                    # Keep system prompt and recent messages
                    messages = [messages[0]] + messages[-15:]
                
            except KeyboardInterrupt:
                print("\n\n⏸️  Agent interrupted by user. Saving state...")
                self.state_manager.save_state(state)
                break
            
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
                # Log error and continue
                result = {
                    "success": False,
                    "summary": f"Error: {str(e)}"
                }
                state = self.state_manager.add_action(state, "error", result)
                self.state_manager.save_state(state)
        
        print("\n" + "=" * 60)
        print("🤖 Agent stopped.")
        print(f"📊 Total actions: {state['total_actions']}")
        print(f"📁 Workspace: {self.workspace_path}")
        
        return state
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are an autonomous coding agent working toward a goal.

Your memory and state are provided in the context. Use them to maintain continuity.

You have tools for:
- Searching files (search_files)
- Reading files (read_file)
- Writing files (write_file)
- Listing files (list_files)
- Running commands (run_command)
- Getting project structure (get_project_structure)
- Updating memory (update_memory)
- Completing goal (complete_goal)

Work step by step:
1. Understand the current goal from memory
2. Check what you've done (recent actions)
3. Decide the next logical action
4. Use tools to make progress
5. Update memory with important findings

When you achieve the goal, call complete_goal with a summary.

Be autonomous - don't ask for permission, just do what's needed.
Document your decisions in memory files.
Run tests to verify your work.
"""
    
    def _execute_tool(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return structured result"""
        
        try:
            if function_name == "search_files":
                return self.file_tools.search_files(
                    args["query"],
                    args.get("file_pattern", "*")
                )
            
            elif function_name == "read_file":
                return self.file_tools.read_file(
                    args["file_path"],
                    args.get("start_line"),
                    args.get("end_line")
                )
            
            elif function_name == "write_file":
                return self.file_tools.write_file(
                    args["file_path"],
                    args["content"]
                )
            
            elif function_name == "list_files":
                return self.file_tools.list_files(
                    args.get("directory", "."),
                    args.get("pattern", "*")
                )
            
            elif function_name == "run_command":
                return self.command_tools.run_command(
                    args["command"],
                    args.get("timeout", 30)
                )
            
            elif function_name == "get_project_structure":
                return self.file_tools.get_project_structure(
                    args.get("max_depth", 3)
                )
            
            elif function_name == "update_memory":
                self.state_manager.update_memory_file(
                    args["file_type"],
                    args["content"]
                )
                return {
                    "success": True,
                    "summary": f"Updated {args['file_type']} memory",
                    "data": {},
                    "next_suggestions": ["Continue with next task"]
                }
            
            elif function_name == "complete_goal":
                return {
                    "success": True,
                    "summary": args["summary"],
                    "data": {},
                    "next_suggestions": []
                }
            
            else:
                return {
                    "success": False,
                    "summary": f"Unknown tool: {function_name}",
                    "data": {},
                    "next_suggestions": []
                }
        
        except Exception as e:
            return {
                "success": False,
                "summary": f"Tool execution failed: {str(e)}",
                "data": {},
                "next_suggestions": ["Try a different approach"]
            }
    
    def _set_goal(self, goal: str):
        """Set the initial goal"""
        goals_content = f"""# Goals

## Primary Objective
{goal}

## Success Criteria
- [ ] Goal clearly understood
- [ ] Approach identified
- [ ] Implementation complete
- [ ] Verification done

## Constraints
- Work within the project directory
- Use available tools
- Document decisions

## Current Focus
Starting work on the goal
"""
        self.state_manager.update_memory_file("goals", goals_content)
        print(f"🎯 Goal set: {goal}")
    
    def _reflect(self, state: Dict, memory: Dict, messages: List):
        """Perform reflection on recent work"""
        
        recent_actions = state["recent_actions"][-10:] if state["recent_actions"] else []
        
        reflection_prompt = f"""Time to reflect on your recent work.

## Recent Actions (last 10)
{json.dumps(recent_actions, indent=2)}

## Current Memory

### Goals
{memory.get('goals', 'Not set')}

### Progress
{memory.get('progress', 'None')}

### Blockers
{memory.get('blockers', 'None')}

Reflect honestly:
1. Am I making progress toward the goal?
2. What's working well?
3. What's not working?
4. Should I change my approach?
5. What should I update in memory?

Provide a brief reflection and update memory files if needed using the update_memory tool."""

        # Add reflection prompt to conversation
        messages.append({
            "role": "user",
            "content": reflection_prompt
        })
        
        print("🔄 Reflecting on recent work...")


if __name__ == "__main__":
    agent = AutonomousAgentV2()
    
    # Example goal
    goal = input("Enter a goal for the agent: ").strip()
    if not goal:
        goal = "Create a simple Python script called hello.py that prints 'Hello, World!'"
    
    agent.run(initial_goal=goal, max_iterations=20)
