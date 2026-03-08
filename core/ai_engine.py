import json
import os
from tool_engine import run_tool
from recon_engine import run_recon

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
INTENT_FILE = os.path.join(script_dir, "..", "configs", "intent_map.json")

def load_intents():
    with open(INTENT_FILE) as f:
        return json.load(f)

def handle_command(cmd):

    if cmd.startswith("recon"):

        parts = cmd.split()

        if len(parts) < 2:
            print("Usage: recon <target>")
            return

        target = parts[1]

        run_recon(target)

        return

    intents = load_intents()
    text = cmd.lower()
    parts = cmd.split()

    if len(parts) < 2:
        print("Usage: <command> <target>")
        return

    target = parts[-1]

    for intent in intents:
        if intent in text:

            print(f"[+] Intent detected: {intent}")

            tools = intents[intent]

            for tool in tools:
                run_tool(tool, target)

            return

    print("[!] Intent not recognized")
