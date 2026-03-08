#!/usr/bin/env python3
"""
PiSecOS Boot Launcher
Location: pisecos/core/launcher.py
"""

import os
import sys
import logging
from pathlib import Path

# Add repo root to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

# Setup logging
logging.basicConfig(
    filename='/var/log/pisecos/boot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BootLauncher:
    def __init__(self):
        self.repo_root = repo_root
        self.tools_dir = os.path.join(repo_root, 'tools')
        self.scans_dir = os.path.join(repo_root, 'scans')
        self.configs_dir = os.path.join(repo_root, 'configs')
        
    def setup(self):
        """Ensure directories exist"""
        Path(self.tools_dir).mkdir(exist_ok=True)
        Path(self.scans_dir).mkdir(exist_ok=True)
        logging.info("Directories verified")
        
    def launch(self):
        """Launch appropriate interface"""
        has_display = os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
        
        if has_display:
            try:
                from gui.dashboard import main
                main()
            except:
                os.system(f"python3 {self.repo_root}/gui/main_gui.py")
        else:
            from core.controller import main
            main()
    
    def run(self):
        logging.info("PiSecOS starting")
        self.setup()
        self.launch()

if __name__ == "__main__":
    launcher = BootLauncher()
    launcher.run()