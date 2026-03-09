#!/usr/bin/env python3
"""
PiSecOS Boot Launcher
Location: pisecos/core/launcher.py
"""

import os
import sys
import logging
from pathlib import Path

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

# Setup logging
log_dir = "/var/log/pisecos"
Path(log_dir).mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=f"{log_dir}/boot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class BootLauncher:

    def __init__(self):
        self.repo_root = repo_root
        self.tools_dir = os.path.join(repo_root, "tools")
        self.scans_dir = os.path.join(repo_root, "scans")
        self.reports_dir = os.path.join(repo_root, "reports")

    def setup(self):
        """Ensure directories exist"""
        Path(self.tools_dir).mkdir(exist_ok=True)
        Path(self.scans_dir).mkdir(exist_ok=True)
        Path(self.reports_dir).mkdir(exist_ok=True)
        logging.info("Directories verified")

    def launch(self):
    """Launch lightweight GUI"""

    logging.info("Launching PiSecOS Compact GUI")

    try:
        os.system(f"python3 {self.repo_root}/gui/main_gui.py")

    except Exception as e:

        logging.error(f"GUI launch failed: {e}")

        print("Failed to start GUI")

    def run(self):
        logging.info("PiSecOS starting")
        self.setup()
        self.launch()


if __name__ == "__main__":
    launcher = BootLauncher()
    launcher.run()