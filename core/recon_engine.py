import sys
from tool_engine import run_tool

target = sys.argv[1]

print(f"[+] Target: {target}")

run_tool("subfinder", target)
run_tool("httpx", target)
run_tool("nmap", target)
run_tool("nuclei", target)

print("[+] Recon Completed")
