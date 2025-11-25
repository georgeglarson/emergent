"""
State Manager - Handles persistent agent state and memory
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class StateManager:
    """Manages agent state and memory files"""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/emergent"):
        self.workspace = Path(workspace_path)
        self.state_file = self.workspace / ".agent_state.json"
        self.memory_dir = self.workspace / "memory"
        
        # Memory file paths
        self.goals_file = self.memory_dir / "goals.md"
        self.progress_file = self.memory_dir / "progress.md"
        self.decisions_file = self.memory_dir / "decisions.md"
        self.blockers_file = self.memory_dir / "blockers.md"
    
    def load_state(self) -> Dict[str, Any]:
        """Load current agent state"""
        if not self.state_file.exists():
            return self._create_initial_state()
        
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save agent state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _create_initial_state(self) -> Dict[str, Any]:
        """Create initial state structure"""
        return {
            "version": "0.1.0",
            "initialized_at": datetime.utcnow().isoformat() + "Z",
            "current_working_directory": str(self.workspace / "project"),
            "files_in_context": [],
            "recent_actions": [],
            "current_phase": "initialization",
            "actions_since_reflection": 0,
            "last_reflection": None,
            "total_actions": 0,
            "session_start": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "goal_set": False,
                "project_initialized": False
            }
        }
    
    def add_action(self, state: Dict[str, Any], action: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add an action to the state history"""
        action_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "success": result.get("success", False),
            "summary": result.get("summary", "")
        }
        
        state["recent_actions"].append(action_entry)
        
        # Keep only last 20 actions
        if len(state["recent_actions"]) > 20:
            state["recent_actions"] = state["recent_actions"][-20:]
        
        state["total_actions"] += 1
        state["actions_since_reflection"] += 1
        
        return state
    
    def load_memory(self) -> Dict[str, str]:
        """Load all memory files"""
        memory = {}
        
        if self.goals_file.exists():
            with open(self.goals_file, 'r') as f:
                memory["goals"] = f.read()
        
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                memory["progress"] = f.read()
        
        if self.decisions_file.exists():
            with open(self.decisions_file, 'r') as f:
                memory["decisions"] = f.read()
        
        if self.blockers_file.exists():
            with open(self.blockers_file, 'r') as f:
                memory["blockers"] = f.read()
        
        return memory
    
    def update_memory_file(self, file_type: str, content: str) -> None:
        """Update a specific memory file"""
        file_map = {
            "goals": self.goals_file,
            "progress": self.progress_file,
            "decisions": self.decisions_file,
            "blockers": self.blockers_file
        }
        
        if file_type not in file_map:
            raise ValueError(f"Unknown memory file type: {file_type}")
        
        with open(file_map[file_type], 'w') as f:
            f.write(content)
    
    def should_reflect(self, state: Dict[str, Any]) -> bool:
        """Check if it's time for a reflection"""
        return state["actions_since_reflection"] >= 10
    
    def mark_reflection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mark that a reflection has occurred"""
        state["last_reflection"] = datetime.utcnow().isoformat() + "Z"
        state["actions_since_reflection"] = 0
        return state
    
    def get_context_summary(self, state: Dict[str, Any], memory: Dict[str, str]) -> str:
        """Generate a summary of current context for the LLM"""
        summary = f"""# Agent Context

## Current State
- Working Directory: {state['current_working_directory']}
- Current Phase: {state['current_phase']}
- Total Actions: {state['total_actions']}
- Actions Since Last Reflection: {state['actions_since_reflection']}

## Files in Context
{', '.join(state['files_in_context']) if state['files_in_context'] else 'None'}

## Recent Actions (Last 5)
"""
        
        recent = state['recent_actions'][-5:] if state['recent_actions'] else []
        for action in recent:
            status = "✓" if action['success'] else "✗"
            summary += f"{status} {action['action']}: {action['summary']}\n"
        
        summary += f"\n## Memory\n\n### Goals\n{memory.get('goals', 'Not set')}\n"
        summary += f"\n### Progress\n{memory.get('progress', 'None')}\n"
        summary += f"\n### Blockers\n{memory.get('blockers', 'None')}\n"
        
        return summary
