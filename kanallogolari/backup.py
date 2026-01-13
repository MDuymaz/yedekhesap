import os
import requests

GITHUB_TOKEN = os.getenv("GH_TOKEN")
OWNER = "opitiopiti"

REPOS = [
    "Py",
    "ordanburdansurdan",
    "m3u8file",
    "xtreamcode2",
    "xtreamsistemi",
    "iptv-proxy-worker",
    "domain"
]

BRANCH = "main"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

for repo in REPOS:
    url = f"https://api.github.com/repos/{OWNER}/{repo}/zipball/{BRANCH}"
    zip_name = f"{repo}.zip"

    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        with open(zip_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ {repo} indirildi.")
    else:
        print(f"❌ {repo} hata:", response.status_code)
