import requests
import re

# Hedef URL
url = "https://nl.pornhub.com/view_video.php?viewkey=67b090c219858"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": url
}

response = requests.get(url, headers=headers)
html = response.text

# HTML içinde tüm m3u8 linklerini ve çözünürlükleri regex ile bul
# format: 720P_4000K_xxx.mp4/master.m3u8? ...
pattern = re.compile(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', re.IGNORECASE)
m3u8_links = pattern.findall(html)

if not m3u8_links:
    print("m3u8 linki bulunamadı")
else:
    # Çözünürlük bilgisini link içinden alıp en yüksek olanı seçelim
    def get_height(link):
        match = re.search(r'(\d+)P', link)
        if match:
            return int(match.group(1))
        return 0

    highest_link = max(m3u8_links, key=get_height)
    print("En yüksek çözünürlüklü m3u8 linki:", highest_link)
