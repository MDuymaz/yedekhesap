import requests
import os

# 🔐 TOKENLER (direkt yazılı)
TOKENS = {
    "opitiopiti": os.getenv("GH_TOKEN"),
    "MDuymaz": os.getenv("YEDEKLEME_TOKENI")
}

# 👤 Kullanıcı → Repo listesi
USERS = {
    "opitiopiti": [
        "Py",
        "ordanburdansurdan",
        "m3u8file",
        "xtreamcode2",
        "xtreamsistemi",
        "iptv-proxy-worker",
        "domain"
    ],
    "MDuymaz": [
        "proxy",
        "yedekhesap",
        "deneme",
        "xtreamcode"
    ]
}

def download_repo(owner, repo, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # ✅ Default branch otomatik
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    zip_name = f"{owner}_{repo}.zip"

    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        with open(zip_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ {owner}/{repo} indirildi.")
    else:
        print(f"❌ {owner}/{repo} hata: {response.status_code}")

# 🔁 Tüm kullanıcı ve repolar
for owner, repos in USERS.items():
    token = TOKENS.get(owner)

    if not token:
        print(f"⚠️ Token yok: {owner}")
        continue

    for repo in repos:
        download_repo(owner, repo, token)
