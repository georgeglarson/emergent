"""
File Tools - LLM-optimized file operations
All tools return structured JSON for easy LLM parsing
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class FileTools:
    """Tools for file operations optimized for LLM consumption"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.project_dir = self.workspace / "project"
    
    def search_files(self, query: str, file_pattern: str = "*") -> Dict[str, Any]:
        """
        Search for text in files using ripgrep
        Returns structured results with context
        """
        try:
            # Use ripgrep for fast searching
            cmd = [
                "rg",
                "--json",
                "--context", "2",
                "--max-count", "10",  # Limit results per file
                query,
                str(self.project_dir)
            ]
            
            if file_pattern != "*":
                cmd.extend(["--glob", file_pattern])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse ripgrep JSON output
            matches = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = eval(line)  # ripgrep outputs JSON lines
                    if data.get('type') == 'match':
                        match_data = data['data']
                        matches.append({
                            "file": match_data['path']['text'],
                            "line": match_data['line_number'],
                            "content": match_data['lines']['text'].strip(),
                            "context": "available"
                        })
                except:
                    continue
            
            if not matches:
                return {
                    "success": True,
                    "summary": f"No matches found for '{query}'",
                    "data": {"matches": []},
                    "next_suggestions": [
                        "Try a different search term",
                        "Check if files exist in project directory"
                    ]
                }
            
            return {
                "success": True,
                "summary": f"Found {len(matches)} matches for '{query}'",
                "data": {"matches": matches},
                "next_suggestions": [
                    f"Read {matches[0]['file']} to see full context",
                    "Search for related terms"
                ]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "summary": "Search timed out",
                "data": {},
                "next_suggestions": ["Try a more specific search"]
            }
        except Exception as e:
            return {
                "success": False,
                "summary": f"Search failed: {str(e)}",
                "data": {},
                "next_suggestions": ["Check if ripgrep is installed"]
            }
    
    def read_file(self, file_path: str, start_line: Optional[int] = None, 
                  end_line: Optional[int] = None) -> Dict[str, Any]:
        """
        Read a file with optional line range
        Returns structured content with metadata
        """
        try:
            full_path = self.project_dir / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "summary": f"File not found: {file_path}",
                    "data": {},
                    "next_suggestions": [
                        "Check file path spelling",
                        "List directory contents"
                    ]
                }
            
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Handle line range
            if start_line is not None or end_line is not None:
                start = (start_line or 1) - 1
                end = end_line or total_lines
                content_lines = lines[start:end]
                content = ''.join(content_lines)
                line_range = f"lines {start_line or 1}-{end_line or total_lines}"
            else:
                content = ''.join(lines)
                line_range = "full file"
            
            # Get file extension for syntax info
            extension = full_path.suffix
            
            return {
                "success": True,
                "summary": f"Read {file_path} ({line_range}, {total_lines} total lines)",
                "data": {
                    "content": content,
                    "total_lines": total_lines,
                    "extension": extension,
                    "path": file_path
                },
                "next_suggestions": [
                    "Edit this file if changes needed",
                    "Search for related files"
                ]
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "summary": f"Cannot read {file_path} - binary file",
                "data": {},
                "next_suggestions": ["Skip binary files"]
            }
        except Exception as e:
            return {
                "success": False,
                "summary": f"Failed to read {file_path}: {str(e)}",
                "data": {},
                "next_suggestions": ["Check file permissions"]
            }
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file (creates or overwrites)
        """
        try:
            full_path = self.project_dir / file_path
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            lines = len(content.split('\n'))
            
            return {
                "success": True,
                "summary": f"Wrote {file_path} ({lines} lines)",
                "data": {
                    "path": file_path,
                    "lines": lines
                },
                "next_suggestions": [
                    "Read the file to verify",
                    "Run tests to check if it works"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "summary": f"Failed to write {file_path}: {str(e)}",
                "data": {},
                "next_suggestions": ["Check file path and permissions"]
            }
    
    def list_files(self, directory: str = ".", pattern: str = "*") -> Dict[str, Any]:
        """
        List files in a directory
        Returns structured file list with metadata
        """
        try:
            dir_path = self.project_dir / directory
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "summary": f"Directory not found: {directory}",
                    "data": {},
                    "next_suggestions": ["Check directory path"]
                }
            
            # Get all files matching pattern
            if pattern == "*":
                files = list(dir_path.rglob("*"))
            else:
                files = list(dir_path.rglob(pattern))
            
            # Filter out directories and hidden files
            files = [f for f in files if f.is_file() and not f.name.startswith('.')]
            
            # Sort by modification time (most recent first)
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            file_list = []
            for f in files[:50]:  # Limit to 50 files
                rel_path = f.relative_to(self.project_dir)
                file_list.append({
                    "path": str(rel_path),
                    "size": f.stat().st_size,
                    "extension": f.suffix
                })
            
            return {
                "success": True,
                "summary": f"Found {len(file_list)} files in {directory}",
                "data": {
                    "files": file_list,
                    "total": len(files)
                },
                "next_suggestions": [
                    "Read specific files to understand structure",
                    "Search for specific content"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "summary": f"Failed to list files: {str(e)}",
                "data": {},
                "next_suggestions": ["Check directory path"]
            }
    
    def get_project_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get an overview of project structure using tree
        """
        try:
            cmd = [
                "tree",
                "-L", str(max_depth),
                "-I", "__pycache__|*.pyc|.git|node_modules",
                "--dirsfirst",
                str(self.project_dir)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Fallback to simple ls
                result = subprocess.run(
                    ["ls", "-la", str(self.project_dir)],
                    capture_output=True,
                    text=True
                )
            
            return {
                "success": True,
                "summary": "Project structure retrieved",
                "data": {
                    "structure": result.stdout
                },
                "next_suggestions": [
                    "Read key files to understand the project",
                    "Search for specific functionality"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "summary": f"Failed to get structure: {str(e)}",
                "data": {},
                "next_suggestions": ["Try listing files instead"]
            }
