import os

def install_dependencies(path):

    if os.path.exists(f"{path}/requirements.txt"):
        os.system(f"pip3 install -r {path}/requirements.txt")

    if os.path.exists(f"{path}/go.mod"):
        os.system(f"cd {path} && go build")

    if os.path.exists(f"{path}/package.json"):
        os.system(f"cd {path} && npm install")
