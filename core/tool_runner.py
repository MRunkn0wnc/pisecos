import os
from tool_downloader import download_tool
from dependency_installer import install_dependencies

def run_tool(tool, target):

    path = download_tool(tool)

    if path is None:
        return

    install_dependencies(path)

    print(f"[+] Searching executable in {path}")

    # check python tools
    for file in os.listdir(path):
        if file.endswith(".py"):
            cmd = f"python3 {path}/{file} {target}"
            print(f"[+] Running {cmd}")
            os.system(cmd)
            return

    # check compiled binaries
    binary = f"{path}/{tool}"

    if os.path.exists(binary):
        cmd = f"{binary} {target}"
        print(f"[+] Running {cmd}")
        os.system(cmd)
        return

    print("[!] No executable detected")
