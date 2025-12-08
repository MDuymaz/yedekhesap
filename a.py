import requests

# Hedef URL
url = "https://nl.pornhub.com/view_video.php?viewkey=67b090c219858"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": url
}

# Sayfayı çek
response = requests.get(url, headers=headers)
html = response.text

# HTML'i a.html dosyasına yaz
with open("a.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML içeriği a.html dosyasına yazıldı.")
