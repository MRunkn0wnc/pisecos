import json
import os
import shutil

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
TOOLS_DB = os.path.join(script_dir, "..", "configs", "tools.json")

def load_tools():
    with open(TOOLS_DB) as f:
        return json.load(f)

def tool_exists(tool):
    return shutil.which(tool) is not None

def run_tool(tool, target):

    tools = load_tools()

    if tool not in tools:
        print(f"[!] Tool {tool} not configured")
        return

    # install only if missing
    if not tool_exists(tool):

        print(f"[+] Tool {tool} not found")

        install_cmd = tools[tool]["install"]

        print(f"[+] Installing {tool}")

        os.system(install_cmd)

    cmd = tools[tool]["command"].replace("{target}", target)

    print(f"[+] Running: {cmd}")

    os.system(cmd)
