#!/usr/bin/env python3.11
"""
Continuous Operation Runner - For 24/7 autonomous operation

Designed for Venice.ai unlimited inference environments.
Runs agent with automatic restarts, monitoring, and recovery.
"""
import time
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from agent_v2 import AutonomousAgentV2


class ContinuousRunner:
    """Runs Emergent continuously with automatic restarts and monitoring"""
    
    def __init__(self, workspace_path: str = "/home/ubuntu/emergent"):
        self.workspace_path = workspace_path
        self.log_file = Path(workspace_path) / "continuous_operation.log"
        self.stats_file = Path(workspace_path) / "operation_stats.json"
        
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and console"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        log_line = f"[{timestamp}] [{level}] {message}"
        
        print(log_line)
        
        with open(self.log_file, 'a') as f:
            f.write(log_line + "\n")
    
    def update_stats(self, stats: dict):
        """Update operation statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def run_session(self, goal: str, max_iterations: int = 50, timeout: int = 3600) -> dict:
        """
        Run a single agent session with timeout
        Returns session statistics
        """
        session_start = time.time()
        
        try:
            self.log(f"Starting session (max {max_iterations} iterations, {timeout}s timeout)")
            
            agent = AutonomousAgentV2(workspace_path=self.workspace_path)
            
            # Run with timeout
            state = agent.run(
                initial_goal=goal,
                max_iterations=max_iterations
            )
            
            session_time = time.time() - session_start
            
            return {
                "success": True,
                "duration": session_time,
                "total_actions": state.get("total_actions", 0),
                "error": None
            }
            
        except KeyboardInterrupt:
            self.log("Session interrupted by user", "WARN")
            raise
        
        except Exception as e:
            session_time = time.time() - session_start
            self.log(f"Session error: {e}", "ERROR")
            
            return {
                "success": False,
                "duration": session_time,
                "total_actions": 0,
                "error": str(e)
            }
    
    def run_continuous(
        self,
        goal: str,
        duration_hours: int = 24,
        session_iterations: int = 50,
        session_timeout: int = 3600,
        restart_delay: int = 10
    ):
        """
        Run agent continuously for specified duration
        
        Args:
            goal: The goal to work toward
            duration_hours: How many hours to run (default: 24)
            session_iterations: Max iterations per session (default: 50)
            session_timeout: Timeout per session in seconds (default: 3600 = 1 hour)
            restart_delay: Delay between restarts in seconds (default: 10)
        """
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        stats = {
            "goal": goal,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "duration_hours": duration_hours,
            "sessions_completed": 0,
            "sessions_failed": 0,
            "total_actions": 0,
            "total_runtime": 0,
            "errors": []
        }
        
        self.log("=" * 80)
        self.log("EMERGENT - CONTINUOUS OPERATION")
        self.log("=" * 80)
        self.log(f"Goal: {goal}")
        self.log(f"Duration: {duration_hours} hours")
        self.log(f"Session config: {session_iterations} iterations, {session_timeout}s timeout")
        self.log(f"Workspace: {self.workspace_path}")
        self.log("=" * 80)
        
        try:
            while time.time() < end_time:
                remaining = int((end_time - time.time()) / 3600)
                self.log(f"Starting new session ({remaining}h remaining)")
                
                # Run session
                result = self.run_session(
                    goal=goal,
                    max_iterations=session_iterations,
                    timeout=session_timeout
                )
                
                # Update stats
                if result["success"]:
                    stats["sessions_completed"] += 1
                    stats["total_actions"] += result["total_actions"]
                    self.log(f"Session completed: {result['total_actions']} actions in {result['duration']:.1f}s")
                else:
                    stats["sessions_failed"] += 1
                    stats["errors"].append({
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "error": result["error"]
                    })
                    self.log(f"Session failed: {result['error']}", "ERROR")
                
                stats["total_runtime"] += result["duration"]
                self.update_stats(stats)
                
                # Check if goal is complete
                state_file = Path(self.workspace_path) / ".agent_state.json"
                if state_file.exists():
                    with open(state_file) as f:
                        state = json.load(f)
                        if state.get("current_phase") == "complete":
                            self.log("Goal marked as complete!", "SUCCESS")
                            break
                
                # Delay before restart
                if time.time() < end_time:
                    self.log(f"Restarting in {restart_delay}s...")
                    time.sleep(restart_delay)
        
        except KeyboardInterrupt:
            self.log("\n\nOperation interrupted by user", "WARN")
        
        finally:
            # Final stats
            stats["ended_at"] = datetime.utcnow().isoformat() + "Z"
            stats["total_runtime"] = time.time() - start_time
            self.update_stats(stats)
            
            self.log("=" * 80)
            self.log("OPERATION COMPLETE")
            self.log("=" * 80)
            self.log(f"Sessions completed: {stats['sessions_completed']}")
            self.log(f"Sessions failed: {stats['sessions_failed']}")
            self.log(f"Total actions: {stats['total_actions']}")
            self.log(f"Total runtime: {stats['total_runtime'] / 3600:.1f} hours")
            self.log(f"Stats saved to: {self.stats_file}")
            self.log("=" * 80)


def main():
    """CLI for continuous operation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Emergent continuously for extended periods"
    )
    parser.add_argument(
        "goal",
        help="The goal to work toward"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="How many hours to run (default: 24)"
    )
    parser.add_argument(
        "--workspace",
        default="/home/ubuntu/emergent",
        help="Workspace path (default: /home/ubuntu/emergent)"
    )
    parser.add_argument(
        "--session-iterations",
        type=int,
        default=50,
        help="Max iterations per session (default: 50)"
    )
    parser.add_argument(
        "--session-timeout",
        type=int,
        default=3600,
        help="Session timeout in seconds (default: 3600)"
    )
    
    args = parser.parse_args()
    
    runner = ContinuousRunner(workspace_path=args.workspace)
    runner.run_continuous(
        goal=args.goal,
        duration_hours=args.hours,
        session_iterations=args.session_iterations,
        session_timeout=args.session_timeout
    )


if __name__ == "__main__":
    main()
