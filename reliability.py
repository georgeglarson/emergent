"""
Reliability Module - Loop detection, watchdog timers, and failure recovery
"""
import time
from typing import List, Dict, Any, Optional
from collections import deque


class ReliabilityMonitor:
    """Monitors agent behavior to prevent loops and wasted cycles"""
    
    def __init__(self):
        self.recent_actions = deque(maxlen=10)
        self.last_progress_time = time.time()
        self.total_tokens_since_progress = 0
        self.loop_threshold = 3  # Same action N times = loop
        self.watchdog_timeout = 1800  # 30 minutes without progress
        self.token_waste_threshold = 100000  # Too many tokens without progress
        
    def record_action(self, action: str, made_progress: bool = False, tokens_used: int = 0):
        """Record an action and update progress tracking"""
        self.recent_actions.append(action)
        self.total_tokens_since_progress += tokens_used
        
        if made_progress:
            self.last_progress_time = time.time()
            self.total_tokens_since_progress = 0
    
    def detect_loop(self) -> Optional[str]:
        """
        Detect if agent is stuck in a loop
        Returns the looping action if detected, None otherwise
        """
        if len(self.recent_actions) < self.loop_threshold:
            return None
        
        # Check if last N actions are identical
        recent = list(self.recent_actions)[-self.loop_threshold:]
        if len(set(recent)) == 1:
            return recent[0]
        
        # Check for alternating pattern (A-B-A-B-A-B)
        if len(recent) >= 4:
            if recent[0] == recent[2] and recent[1] == recent[3]:
                return f"alternating: {recent[0]} <-> {recent[1]}"
        
        return None
    
    def check_watchdog(self) -> bool:
        """
        Check if agent has made progress recently
        Returns True if watchdog timeout exceeded
        """
        time_since_progress = time.time() - self.last_progress_time
        return time_since_progress > self.watchdog_timeout
    
    def check_token_waste(self) -> bool:
        """
        Check if too many tokens used without progress
        Returns True if threshold exceeded
        """
        return self.total_tokens_since_progress > self.token_waste_threshold
    
    def should_restart(self) -> Dict[str, Any]:
        """
        Check all restart conditions
        Returns dict with restart decision and reason
        """
        # Check for loop
        loop = self.detect_loop()
        if loop:
            return {
                "should_restart": True,
                "reason": "loop_detected",
                "details": f"Agent stuck repeating: {loop}"
            }
        
        # Check watchdog
        if self.check_watchdog():
            time_since = int(time.time() - self.last_progress_time)
            return {
                "should_restart": True,
                "reason": "watchdog_timeout",
                "details": f"No progress for {time_since}s"
            }
        
        # Check token waste
        if self.check_token_waste():
            return {
                "should_restart": True,
                "reason": "token_waste",
                "details": f"Used {self.total_tokens_since_progress} tokens without progress"
            }
        
        return {
            "should_restart": False,
            "reason": None,
            "details": None
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        time_since_progress = int(time.time() - self.last_progress_time)
        
        return {
            "recent_actions": list(self.recent_actions),
            "time_since_progress": time_since_progress,
            "tokens_since_progress": self.total_tokens_since_progress,
            "loop_detected": self.detect_loop(),
            "watchdog_ok": not self.check_watchdog(),
            "token_usage_ok": not self.check_token_waste()
        }


class ProgressTracker:
    """Tracks meaningful progress to determine if agent is making headway"""
    
    def __init__(self):
        self.milestones = []
        self.files_created = set()
        self.files_modified = set()
        self.commands_run = []
        self.tests_passed = 0
        self.errors_encountered = 0
        
    def record_file_created(self, filepath: str):
        """Record that a file was created"""
        self.files_created.add(filepath)
        self.milestones.append({
            "type": "file_created",
            "file": filepath,
            "timestamp": time.time()
        })
    
    def record_file_modified(self, filepath: str):
        """Record that a file was modified"""
        self.files_modified.add(filepath)
        self.milestones.append({
            "type": "file_modified",
            "file": filepath,
            "timestamp": time.time()
        })
    
    def record_command_success(self, command: str, output: str):
        """Record successful command execution"""
        self.commands_run.append(command)
        
        # Check if it's a test
        if "test" in command.lower() or "pytest" in command.lower():
            self.tests_passed += 1
            self.milestones.append({
                "type": "test_passed",
                "command": command,
                "timestamp": time.time()
            })
        else:
            self.milestones.append({
                "type": "command_success",
                "command": command,
                "timestamp": time.time()
            })
    
    def record_error(self, error: str):
        """Record an error"""
        self.errors_encountered += 1
    
    def made_progress_recently(self, window: int = 600) -> bool:
        """
        Check if meaningful progress was made in the last N seconds
        """
        recent_time = time.time() - window
        recent_milestones = [
            m for m in self.milestones 
            if m["timestamp"] > recent_time
        ]
        return len(recent_milestones) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        return {
            "files_created": len(self.files_created),
            "files_modified": len(self.files_modified),
            "commands_run": len(self.commands_run),
            "tests_passed": self.tests_passed,
            "errors_encountered": self.errors_encountered,
            "total_milestones": len(self.milestones),
            "recent_progress": self.made_progress_recently()
        }
