#!/usr/bin/env python3
"""
GitHub Tool Searcher
Searches GitHub for pentesting tools when user types their name
"""

import requests
import json
import time
from pathlib import Path
import os

class GitHubSearcher:
    """
    Searches GitHub for tools based on name
    Auto-discovers best match for pentesting tools
    """
    
    def __init__(self):
        self.cache_file = Path("/opt/pisecos/tool_cache.json")
        self.cache = self.load_cache()
        self.last_request = 0
        self.rate_limit = 2  # Seconds between requests
        
    def load_cache(self):
        """Load search cache to avoid repeated API calls"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save search results to cache"""
        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def search_tool(self, tool_name):
        """
        Search GitHub for a tool
        
        Args:
            tool_name: Name of tool (e.g., 'nmap', 'sqlmap', 'hydra')
            
        Returns:
            dict with tool info or None
        """
        # Check cache first
        if tool_name in self.cache:
            cache_time = self.cache[tool_name].get('timestamp', 0)
            # Cache valid for 7 days
            if time.time() - cache_time < 604800:
                print(f"[+] Found {tool_name} in cache")
                return self.cache[tool_name]
        
        # Rate limiting
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        
        print(f"[+] Searching GitHub for {tool_name}...")
        
        # Search query - look for pentest tools
        query = f"{tool_name}+pentest+security"
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars"
        
        try:
            response = requests.get(url, timeout=10)
            self.last_request = time.time()
            
            if response.status_code == 403:
                print("[!] GitHub API rate limit exceeded")
                return self.get_fallback_tool(tool_name)
            
            if response.status_code != 200:
                print(f"[!] GitHub API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('items'):
                # Try without pentest suffix
                url = f"https://api.github.com/search/repositories?q={tool_name}&sort=stars"
                response = requests.get(url, timeout=10)
                data = response.json()
            
            if data.get('items'):
                # Get the best match
                best = data['items'][0]
                
                tool_info = {
                    'name': tool_name,
                    'repo': best['full_name'],
                    'url': best['clone_url'],
                    'stars': best['stargazers_count'],
                    'description': best['description'],
                    'timestamp': time.time()
                }
                
                # Cache the result
                self.cache[tool_name] = tool_info
                self.save_cache()
                
                print(f"[+] Found: {best['full_name']} ({best['stargazers_count']} stars)")
                return tool_info
            
        except Exception as e:
            print(f"[!] Search error: {e}")
        
        return self.get_fallback_tool(tool_name)
    
    def get_fallback_tool(self, tool_name):
        """Return known fallback URLs for common tools"""
        fallbacks = {
            'nmap': {
                'name': 'nmap',
                'url': 'https://github.com/nmap/nmap.git',
                'fallback': True
            },
            'sqlmap': {
                'name': 'sqlmap',
                'url': 'https://github.com/sqlmapproject/sqlmap.git',
                'fallback': True
            },
            'hydra': {
                'name': 'hydra',
                'url': 'https://github.com/vanhauser-thc/thc-hydra.git',
                'fallback': True
            },
            'john': {
                'name': 'john',
                'url': 'https://github.com/openwall/john.git',
                'fallback': True
            },
            'metasploit': {
                'name': 'metasploit',
                'url': 'https://github.com/rapid7/metasploit-framework.git',
                'fallback': True
            }
        }
        
        return fallbacks.get(tool_name.lower())