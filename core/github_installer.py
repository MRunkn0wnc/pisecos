import os

TOOLS_DIR = "/opt/pisecos/tools"

def install_from_github(tool):

    path = f"{TOOLS_DIR}/{tool}"

    if os.path.exists(path):
        return

    print(f"[+] Searching GitHub for {tool}")

    repo = f"https://github.com/{tool}/{tool}.git"

    print(f"[+] Cloning {repo}")

    os.system(f"git clone {repo} {path}")

    if os.path.exists(f"{path}/requirements.txt"):
        os.system(f"pip3 install -r {path}/requirements.txt")
