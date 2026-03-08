#!/usr/bin/env python3
"""
Updated recon engine with auto-tool download
"""

import sys
from tool_engine import ToolEngine

def run_recon(target):
    """
    Run reconnaissance against target
    Auto-downloads tools as needed
    """
    if not target:
        print("[!] No target specified")
        return False
    
    print(f"\n[+] Starting reconnaissance on: {target}")
    print("[+] Tools will be auto-downloaded if not present\n")
    
    # Initialize tool engine
    engine = ToolEngine()
    
    # Define recon phases
    phases = [
        {
            'name': 'Subdomain Discovery',
            'tools': ['subfinder', 'assetfinder']
        },
        {
            'name': 'Port Scanning',
            'tools': ['nmap']
        },
        {
            'name': 'Web Enumeration',
            'tools': ['gobuster', 'ffuf', 'nikto']
        },
        {
            'name': 'Vulnerability Scanning',
            'tools': ['nuclei']
        },
        {
            'name': 'SQL Injection Testing',
            'tools': ['sqlmap']
        }
    ]
    
    results = {}
    
    for phase in phases:
        print(f"\n{'='*50}")
        print(f"PHASE: {phase['name']}")
        print(f"{'='*50}")
        
        for tool in phase['tools']:
            print(f"\n[+] Running {tool}...")
            
            # Auto-download and run
            success = engine.run_tool(tool, target)
            results[tool] = success
    
    # Summary
    print(f"\n{'='*50}")
    print("RECONNAISSANCE COMPLETE")
    print(f"{'='*50}")
    
    for tool, success in results.items():
        status = "✓" if success else "✗"
        print(f"[{status}] {tool}")
    
    # Generate report
    try:
        from report_engine import generate_report
        generate_report(target)
    except Exception as e:
        print(f"[!] Report generation failed: {e}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: recon_engine.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    run_recon(target)