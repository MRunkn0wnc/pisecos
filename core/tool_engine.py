#!/usr/bin/env python3
"""
Updated Tool Engine with GitHub auto-download
"""

import json
import os
import shutil
from pathlib import Path

# Import new tool fetcher
from core.tool_fetcher import GitHubSearcher, ARMDownloader, ToolCache, ToolExecutor

class ToolEngine:
    """
    Main tool engine with auto-download capability
    """
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(self.script_dir, "..", "configs")
        self.tools_json = os.path.join(self.config_dir, "tools.json")
        
        # Initialize new components
        self.searcher = GitHubSearcher()
        self.downloader = ARMDownloader()
        self.cache = ToolCache()
        self.executor = ToolExecutor(self.cache)
        
        self.load_config()
    
    def load_config(self):
        """Load tools configuration"""
        try:
            with open(self.tools_json) as f:
                self.tools_config = json.load(f)
        except:
            self.tools_config = {}
    
    def tool_exists(self, tool_name):
        """Check if tool exists in system or cache"""
        # Check if in system PATH
        if shutil.which(tool_name):
            return True
        
        # Check cache
        return self.cache.tool_exists(tool_name)
    
    def get_tool_path(self, tool_name):
        """Get path to tool executable"""
        # Check system first
        system_path = shutil.which(tool_name)
        if system_path:
            return system_path
        
        # Check cache
        return self.cache.get_tool_path(tool_name)
    
    def ensure_tool(self, tool_name):
        """
        Ensure tool is available, download if not
        """
        if self.tool_exists(tool_name):
            return True
        
        print(f"[+] Tool {tool_name} not found locally")
        print(f"[+] Attempting to download from GitHub...")
        
        # Search GitHub
        tool_info = self.searcher.search_tool(tool_name)
        
        if not tool_info:
            print(f"[!] Could not find {tool_name} on GitHub")
            return False
        
        # Download tool
        tool_path = self.downloader.download_tool(tool_info)
        
        if not tool_path:
            print(f"[!] Failed to download {tool_name}")
            return False
        
        # Add to cache
        self.cache.add_tool(
            tool_name,
            tool_path,
            tool_info.get('url', 'github')
        )
        
        print(f"[+] {tool_name} ready for use")
        return True
    
    def run_tool(self, tool_name, target, args=None):
        """
        Run a tool against target
        Auto-downloads if needed
        """
        # Ensure tool is available
        if not self.ensure_tool(tool_name):
            return False
        
        # Check if tool is in config
        if tool_name in self.tools_config:
            # Use configured command
            cmd = self.tools_config[tool_name]["command"].replace("{target}", target)
            print(f"[+] Running: {cmd}")
            
            # Create output file
            scan_dir = f"/opt/pisecos/scans/{target}"
            Path(scan_dir).mkdir(exist_ok=True)
            output_file = f"{scan_dir}/{tool_name}.txt"
            
            with open(output_file, 'w') as f:
                os.system(f"{cmd} >> {output_file} 2>&1")
            
            return True
        else:
            # Use generic executor for downloaded tools
            return self.executor.run_tool(tool_name, target, args)

# Keep backward compatibility
def run_tool(tool, target):
    engine = ToolEngine()
    return engine.run_tool(tool, target)

def tool_exists(tool):
    engine = ToolEngine()
    return engine.tool_exists(tool)