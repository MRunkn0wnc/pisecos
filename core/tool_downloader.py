import os
from tool_discovery import search_github

TOOLS_DIR = "/opt/pisecos/tools"

def download_tool(tool):

    repo = search_github(tool)

    if repo is None:
        print("Tool not found online")
        return None

    path = f"{TOOLS_DIR}/{tool}"

    if os.path.exists(path):
        print("Tool already downloaded")
        return path

    print(f"[+] Downloading {repo}")

    os.system(f"git clone {repo} {path}")

    return path
