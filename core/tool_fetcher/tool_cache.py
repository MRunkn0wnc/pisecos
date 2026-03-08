#!/usr/bin/env python3
"""
Tool Cache Manager
Tracks downloaded tools and their status
"""

import json
import time
import os
from pathlib import Path

class ToolCache:
    """
    Manages cache of downloaded tools
    """
    
    def __init__(self, cache_file="/opt/pisecos/tools_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self.load()
    
    def load(self):
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        """Save cache to file"""
        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def add_tool(self, tool_name, tool_path, source):
        """Add a tool to cache"""
        self.cache[tool_name] = {
            'path': str(tool_path),
            'source': source,
            'downloaded': time.time(),
            'last_used': time.time(),
            'uses': 0
        }
        self.save()
    
    def tool_exists(self, tool_name):
        """Check if tool is in cache and exists on disk"""
        if tool_name not in self.cache:
            return False
        
        info = self.cache[tool_name]
        path = Path(info['path'])
        
        if not path.exists():
            del self.cache[tool_name]
            self.save()
            return False
        
        return True
    
    def get_tool_path(self, tool_name):
        """Get path to downloaded tool"""
        if self.tool_exists(tool_name):
            info = self.cache[tool_name]
            info['last_used'] = time.time()
            info['uses'] = info.get('uses', 0) + 1
            self.save()
            return info['path']
        return None
    
    def record_use(self, tool_name):
        """Record that a tool was used"""
        if tool_name in self.cache:
            self.cache[tool_name]['last_used'] = time.time()
            self.cache[tool_name]['uses'] = self.cache[tool_name].get('uses', 0) + 1
            self.save()
    
    def list_tools(self):
        """List all cached tools"""
        return list(self.cache.keys())
    
    def get_stats(self):
        """Get cache statistics"""
        total = len(self.cache)
        total_uses = sum(t.get('uses', 0) for t in self.cache.values())
        
        return {
            'total_tools': total,
            'total_uses': total_uses,
            'tools': self.cache
        }