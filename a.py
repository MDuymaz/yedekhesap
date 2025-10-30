import requests
import re

# 1️⃣ Bölüm sayfası
episode_url = "https://www.trdiziizle.vip/kurulus-orhan-1-bolum-full-izle-tek-parca/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0.5993.90 Safari/537.36",
    "Referer": "https://www.trdiziizle.vip/"
}

# Bölüm sayfasını çekiyoruz
response = requests.get(episode_url, headers=headers)
if response.status_code != 200:
    print(f"Sayfa yüklenemedi. Status code: {response.status_code}")
    exit()

html_content = response.text

# 2️⃣ iframe src değerini çekiyoruz
iframe_match = re.search(r'<iframe src="([^"]+)"', html_content)
if not iframe_match:
    print("iframe bulunamadı.")
    exit()

iframe_src = iframe_match.group(1)
player_url = "https://www.trdiziizle.vip" + iframe_src
print("Player URL:", player_url)

# 3️⃣ Player sayfasını çekip video file URL’sini buluyoruz
player_response = requests.get(player_url, headers=headers)
if player_response.status_code != 200:
    print(f"Player sayfası yüklenemedi. Status code: {player_response.status_code}")
    exit()

player_html = player_response.text

# Regex ile sources içindeki file değerini çekiyoruz
file_match = re.search(r'file:"(https://[^"]+\.m3u8[^"]*)"', player_html)
if file_match:
    file_url = file_match.group(1)
    print("Video URL:", file_url)
else:
    print("Video URL bulunamadı.")
