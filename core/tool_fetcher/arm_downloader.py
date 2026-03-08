#!/usr/bin/env python3
"""
ARMv7 Downloader
Handles downloading and building tools for Raspberry Pi
"""

import os
import subprocess
import platform
import shutil
from pathlib import Path

class ARMDownloader:
    """
    Downloads tools with ARMv7 compatibility
    """
    
    def __init__(self, tools_dir="/opt/pisecos/tools"):
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.arch = self.detect_arch()
        
    def detect_arch(self):
        """Detect system architecture"""
        machine = platform.machine()
        if machine == 'armv7l':
            return 'armv7'
        elif machine == 'aarch64':
            return 'arm64'
        elif machine == 'x86_64':
            return 'amd64'
        return machine
    
    def download_tool(self, tool_info):
        """
        Download a tool from GitHub
        
        Args:
            tool_info: Dict with 'url' and 'name'
            
        Returns:
            Path to downloaded tool or None
        """
        tool_name = tool_info['name']
        repo_url = tool_info['url']
        
        tool_path = self.tools_dir / tool_name
        
        # Check if already downloaded
        if tool_path.exists():
            print(f"[+] {tool_name} already exists at {tool_path}")
            return tool_path
        
        print(f"[+] Downloading {tool_name} from {repo_url}")
        
        try:
            # Clone the repository
            result = subprocess.run(
                f"git clone --depth 1 {repo_url} {tool_path}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"[!] Git clone failed: {result.stderr[:200]}")
                return None
            
            print(f"[+] Downloaded to {tool_path}")
            
            # Check for ARM compatibility
            self.check_arm_compatibility(tool_path, tool_name)
            
            return tool_path
            
        except Exception as e:
            print(f"[!] Download error: {e}")
            return None
    
    def check_arm_compatibility(self, tool_path, tool_name):
        """Check if tool has ARM support and build if needed"""
        
        # Look for ARM binaries
        arm_binaries = list(tool_path.glob(f"**/*arm*"))
        if arm_binaries:
            print(f"[+] Found ARM binary: {arm_binaries[0].name}")
            return
        
        # Check for Makefile
        if (tool_path / "Makefile").exists() or (tool_path / "makefile").exists():
            print(f"[+] Makefile found, attempting to build for {self.arch}...")
            self.build_from_source(tool_path)
        
        # Check for setup.py (Python tools usually work on ARM)
        elif (tool_path / "setup.py").exists():
            print(f"[+] Python tool detected, should work on ARM")
        
        # Check for go.mod (Go tools need ARM build)
        elif (tool_path / "go.mod").exists():
            print(f"[+] Go tool detected, checking ARM support...")
    
    def build_from_source(self, tool_path):
        """Attempt to build tool from source"""
        try:
            # Try make
            result = subprocess.run(
                f"cd {tool_path} && make",
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                print(f"[+] Build successful")
                
                # Look for created binary
                for f in tool_path.iterdir():
                    if f.is_file() and os.access(f, os.X_OK):
                        if 'arm' in f.name.lower() or 'arm' in str(f).lower():
                            print(f"[+] ARM binary created: {f.name}")
                            return
                
                print(f"[+] Binary created but ARM compatibility unknown")
            else:
                print(f"[!] Build failed: {result.stderr[:200]}")
                
        except Exception as e:
            print(f"[!] Build error: {e}")