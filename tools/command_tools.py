"""
Command Tools - Execute commands with structured feedback
"""
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List


class CommandTools:
    """Tools for running commands and parsing output"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.project_dir = self.workspace / "project"
    
    def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a shell command and return structured output
        Parses common patterns (errors, warnings, test results)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            # Parse output for common patterns
            analysis = self._analyze_output(stdout, stderr, command)
            
            return {
                "success": success,
                "summary": self._generate_summary(success, analysis, command),
                "data": {
                    "exit_code": result.returncode,
                    "stdout": stdout[:1000],  # Limit output
                    "stderr": stderr[:1000],
                    "analysis": analysis
                },
                "next_suggestions": self._suggest_next_steps(success, analysis, command)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "summary": f"Command timed out after {timeout}s: {command}",
                "data": {},
                "next_suggestions": [
                    "Try with a longer timeout",
                    "Check if command is hanging"
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "summary": f"Failed to run command: {str(e)}",
                "data": {},
                "next_suggestions": ["Check command syntax"]
            }
    
    def _analyze_output(self, stdout: str, stderr: str, command: str) -> Dict[str, Any]:
        """Analyze command output for patterns"""
        analysis = {
            "type": self._detect_command_type(command),
            "errors": [],
            "warnings": [],
            "test_results": None,
            "files_mentioned": []
        }
        
        combined = stdout + "\n" + stderr
        
        # Extract errors
        error_patterns = [
            r"error:?\s+(.+)",
            r"Error:?\s+(.+)",
            r"ERROR:?\s+(.+)",
            r"Exception:?\s+(.+)",
            r"Traceback.*",
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, combined, re.IGNORECASE)
            analysis["errors"].extend(matches[:5])  # Limit to 5 errors
        
        # Extract warnings
        warning_patterns = [
            r"warning:?\s+(.+)",
            r"Warning:?\s+(.+)",
            r"WARN:?\s+(.+)",
        ]
        
        for pattern in warning_patterns:
            matches = re.findall(pattern, combined, re.IGNORECASE)
            analysis["warnings"].extend(matches[:5])
        
        # Parse test results
        if analysis["type"] == "test":
            analysis["test_results"] = self._parse_test_output(combined)
        
        # Extract file paths mentioned
        file_pattern = r'[\w/.-]+\.(py|js|ts|rs|go|java|cpp|c|h)\b'
        files = re.findall(file_pattern, combined)
        analysis["files_mentioned"] = list(set(files))[:10]
        
        return analysis
    
    def _detect_command_type(self, command: str) -> str:
        """Detect what type of command this is"""
        cmd_lower = command.lower()
        
        if any(x in cmd_lower for x in ["pytest", "test", "jest", "cargo test"]):
            return "test"
        elif any(x in cmd_lower for x in ["build", "compile", "make"]):
            return "build"
        elif any(x in cmd_lower for x in ["run", "execute", "python", "node"]):
            return "run"
        elif any(x in cmd_lower for x in ["install", "pip", "npm", "cargo"]):
            return "install"
        else:
            return "other"
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse test output for results"""
        results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # Pytest pattern
        pytest_match = re.search(r'(\d+) passed.*?(\d+) failed', output)
        if pytest_match:
            results["passed"] = int(pytest_match.group(1))
            results["failed"] = int(pytest_match.group(2))
            results["total"] = results["passed"] + results["failed"]
            return results
        
        # Jest pattern
        jest_match = re.search(r'Tests:\s+(\d+) failed.*?(\d+) passed.*?(\d+) total', output)
        if jest_match:
            results["failed"] = int(jest_match.group(1))
            results["passed"] = int(jest_match.group(2))
            results["total"] = int(jest_match.group(3))
            return results
        
        # Generic pass/fail
        passed = len(re.findall(r'\bpass(ed)?\b', output, re.IGNORECASE))
        failed = len(re.findall(r'\bfail(ed)?\b', output, re.IGNORECASE))
        
        if passed > 0 or failed > 0:
            results["passed"] = passed
            results["failed"] = failed
            results["total"] = passed + failed
        
        return results
    
    def _generate_summary(self, success: bool, analysis: Dict, command: str) -> str:
        """Generate a human-readable summary"""
        cmd_type = analysis["type"]
        
        if not success:
            if analysis["errors"]:
                return f"{cmd_type.title()} failed with {len(analysis['errors'])} error(s)"
            return f"{cmd_type.title()} failed (exit code non-zero)"
        
        if cmd_type == "test" and analysis["test_results"]:
            results = analysis["test_results"]
            if results["failed"] > 0:
                return f"Tests completed: {results['passed']} passed, {results['failed']} failed"
            return f"All tests passed ({results['passed']} total)"
        
        return f"{cmd_type.title()} completed successfully"
    
    def _suggest_next_steps(self, success: bool, analysis: Dict, command: str) -> List[str]:
        """Suggest what to do next based on results"""
        suggestions = []
        
        if not success:
            if analysis["errors"]:
                suggestions.append("Read error messages to understand what failed")
                if analysis["files_mentioned"]:
                    suggestions.append(f"Check files: {', '.join(analysis['files_mentioned'][:3])}")
            suggestions.append("Fix the errors and try again")
            return suggestions
        
        if analysis["type"] == "test":
            results = analysis.get("test_results")
            if results and results["failed"] > 0:
                suggestions.append("Fix failing tests")
                if analysis["files_mentioned"]:
                    suggestions.append(f"Check test files: {', '.join(analysis['files_mentioned'][:3])}")
            else:
                suggestions.append("Tests passing - continue with next task")
        
        elif analysis["type"] == "build":
            suggestions.append("Build successful - try running the program")
        
        elif analysis["type"] == "run":
            suggestions.append("Program ran successfully")
            if analysis["warnings"]:
                suggestions.append(f"Address {len(analysis['warnings'])} warning(s)")
        
        if not suggestions:
            suggestions.append("Command completed - continue with next step")
        
        return suggestions
    
    def run_tests(self, test_path: str = "") -> Dict[str, Any]:
        """
        Run tests with automatic detection of test framework
        """
        # Try to detect test framework
        project_files = list(self.project_dir.rglob("*"))
        
        # Check for pytest
        if any("pytest" in str(f) or "test_" in f.name for f in project_files):
            cmd = f"python -m pytest {test_path} -v"
            return self.run_command(cmd)
        
        # Check for Jest/Node
        if any("jest" in str(f) or "package.json" in f.name for f in project_files):
            cmd = f"npm test {test_path}"
            return self.run_command(cmd)
        
        # Check for Cargo/Rust
        if any("Cargo.toml" in f.name for f in project_files):
            cmd = f"cargo test {test_path}"
            return self.run_command(cmd)
        
        return {
            "success": False,
            "summary": "Could not detect test framework",
            "data": {},
            "next_suggestions": [
                "Specify test command manually",
                "Check if tests are set up"
            ]
        }
