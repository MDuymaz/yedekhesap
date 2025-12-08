import requests
import re
import json

# Hedef URL
url = ""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": url
}

# Sayfayı çek
response = requests.get(url, headers=headers)
html = response.text

# HTML içinde m3u8 linklerini bulmak için regex
# videoUrl":"https:\/\/...\.m3u8
m3u8_links = re.findall(r'"videoUrl":"(https:\\/\\/.*?\.m3u8.*?)"', html)

# Bağlantıları terminale yazdır
for link in m3u8_links:
    # Escape karakterleri temizle
    clean_link = link.replace("\\/", "/")
    print(clean_link)
