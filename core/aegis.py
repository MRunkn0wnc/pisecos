#!/usr/bin/env python3
"""
AEGIS Command Executor
Enhanced with AI explanations
"""

import subprocess
import os
from ai_engine import AEGIS

# Initialize AEGIS for explanations
aegis = AEGIS()

def execute(command):
    """
    Execute AEGIS commands with AI explanations
    """
    parts = command.split()
    
    if len(parts) == 0:
        return "[AEGIS] No command entered"
    
    cmd = parts[0].lower()
    
    # Get AI explanation for what we're doing
    if len(parts) > 1:
        explanation = aegis.explain_action(cmd, parts[1])
        print(f"\n[AEGIS] {explanation}\n")
    
    # Command execution (your original logic)
    if cmd == "scan":
        if len(parts) < 2:
            return "[AEGIS] Usage: scan <target>"
        target = parts[1]
        subprocess.Popen(
            ["python3", "/opt/pisecos/core/recon_engine.py", target]
        )
        return f"[AEGIS] Starting reconnaissance scan on {target}"
    
    elif cmd == "subdomains":
        if len(parts) < 2:
            return "[AEGIS] Usage: subdomains <target>"
        target = parts[1]
        subprocess.Popen(["subfinder", "-d", target])
        return f"[AEGIS] Finding subdomains for {target}"
    
    elif cmd == "ports":
        if len(parts) < 2:
            return "[AEGIS] Usage: ports <target>"
        target = parts[1]
        subprocess.Popen(["nmap", "-sV", target])
        return f"[AEGIS] Running port scan on {target}"
    
    elif cmd == "ask":
        # Direct AI question
        question = " ".join(parts[1:])
        response = aegis.model(f"User: {question}\nAEGIS:", max_tokens=200)
        return f"\n[AEGIS] {response['choices'][0]['text'].strip()}\n"
    
    else:
        # Try AI understanding for unknown commands
        understood = aegis.understand_command(command)
        if understood['intent']:
            return execute(f"{understood['intent']} {understood['target']}")
        else:
            return "[AEGIS] Unknown command. Try: scan, subdomains, ports, ask"