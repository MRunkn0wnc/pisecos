#!/usr/bin/env python3

import sys
from core.tool_engine import ToolEngine


def run_recon(target):

    if not target:
        print("[!] No target specified")
        return False

    print(f"\n[+] Starting reconnaissance on {target}")

    engine = ToolEngine()

    phases = [

        ("Subdomain Discovery", ["subfinder"]),

        ("Port Scanning", ["nmap"]),

        ("Web Enumeration", ["gobuster", "ffuf", "nikto"]),

        ("Vulnerability Scanning", ["nuclei"]),

        ("SQL Injection Testing", ["sqlmap"])
    ]

    for phase, tools in phases:

        print("\n" + "="*50)
        print(f"PHASE: {phase}")
        print("="*50)

        for tool in tools:

            engine.run_tool(tool, target)

    print("\n[+] Recon complete")

    try:

        from core.report_engine import generate_report
        generate_report(target)

    except Exception as e:

        print(f"[!] Report generation failed: {e}")


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Usage: recon_engine.py <target>")
        sys.exit(1)

    run_recon(sys.argv[1])