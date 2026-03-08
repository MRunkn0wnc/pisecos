import requests

def search_github(tool):

    url = f"https://api.github.com/search/repositories?q={tool}+pentest&sort=stars"

    r = requests.get(url)

    data = r.json()

    if "items" not in data:
        return None

    repo = data["items"][0]["clone_url"]

    return repo
