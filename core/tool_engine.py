#!/usr/bin/env python3
"""
Stable Tool Engine for Raspberry Pi
"""

import shutil
import subprocess
from pathlib import Path


class ToolEngine:

    def __init__(self):
        self.scan_dir = "/opt/pisecos/scans"
        Path(self.scan_dir).mkdir(parents=True, exist_ok=True)

    def tool_exists(self, tool):

        if shutil.which(tool):
            return True

        print(f"[!] Tool {tool} not installed")
        print(f"[!] Install using: sudo apt install {tool}")
        return False

    def run_tool(self, tool, target, args=None):

        if not self.tool_exists(tool):
            return False

        cmd = [tool]

        if args:
            cmd += args

        cmd.append(target)

        scan_dir = f"{self.scan_dir}/{target}"
        Path(scan_dir).mkdir(parents=True, exist_ok=True)

        output_file = f"{scan_dir}/{tool}.txt"

        print(f"[+] Running {tool} on {target}")

        try:

            with open(output_file, "w") as f:
                subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT
                )

            print(f"[+] Output saved: {output_file}")
            return True

        except Exception as e:

            print(f"[!] Tool execution failed: {e}")
            return False