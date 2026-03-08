#!/usr/bin/env python3
"""
Tool Executor
Runs downloaded tools with proper arguments
"""

import subprocess
import os
import shlex
from pathlib import Path

class ToolExecutor:
    """
    Executes downloaded tools
    """
    
    def __init__(self, tool_cache):
        self.tool_cache = tool_cache
    
    def find_executable(self, tool_path, tool_name):
        """
        Find the main executable in the tool directory
        """
        path = Path(tool_path)
        
        # Look for common executable names
        possible_names = [
            tool_name,
            f"{tool_name}.py",
            f"{tool_name}.sh",
            "main.py",
            "run.py",
            tool_name.lower(),
            tool_name.upper()
        ]
        
        # Check for exact matches first
        for name in possible_names:
            exe = path / name
            if exe.exists():
                if os.access(exe, os.X_OK) or name.endswith('.py'):
                    return exe
        
        # Look for any executable files
        for f in path.iterdir():
            if f.is_file():
                if os.access(f, os.X_OK):
                    return f
                if f.name.endswith('.py'):
                    return f
        
        return None
    
    def run_tool(self, tool_name, target, args=None):
        """
        Run a downloaded tool against target
        
        Args:
            tool_name: Name of tool to run
            target: Target host/domain
            args: Additional arguments for tool
            
        Returns:
            Command output or None
        """
        # Get tool path from cache
        tool_path = self.tool_cache.get_tool_path(tool_name)
        if not tool_path:
            print(f"[!] Tool {tool_name} not found in cache")
            return None
        
        # Find executable
        executable = self.find_executable(tool_path, tool_name)
        if not executable:
            print(f"[!] Could not find executable in {tool_path}")
            return None
        
        # Build command
        cmd = [str(executable)]
        
        if executable.name.endswith('.py'):
            cmd = ['python3', str(executable)]
        
        # Add target
        cmd.append(target)
        
        # Add any additional args
        if args:
            if isinstance(args, list):
                cmd.extend(args)
            else:
                cmd.append(args)
        
        # Create output directory
        scan_dir = f"/opt/pisecos/scans/{target}"
        Path(scan_dir).mkdir(parents=True, exist_ok=True)
        
        output_file = f"{scan_dir}/{tool_name}.txt"
        
        print(f"[+] Running: {' '.join(cmd)}")
        print(f"[+] Output: {output_file}")
        
        try:
            with open(output_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=600,
                    text=True
                )
            
            # Record usage
            self.tool_cache.record_use(tool_name)
            
            if result.returncode == 0:
                print(f"[+] {tool_name} completed")
                return output_file
            else:
                print(f"[!] {tool_name} returned error code {result.returncode}")
                return output_file
                
        except subprocess.TimeoutExpired:
            print(f"[!] {tool_name} timed out after 10 minutes")
            return None
        except Exception as e:
            print(f"[!] Error running {tool_name}: {e}")
            return None