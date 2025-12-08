import requests
from bs4 import BeautifulSoup

# Hedef URL (buraya güvenli bir site koyabilirsiniz)
url = "https://nl.pornhub.com/view_video.php?viewkey=67b090c219858"

# Headers eklemek (tarayıcı gibi davranmak için)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://nl.pornhub.com/"
}

# Sayfayı çekme
response = requests.get(url, headers=headers)
html_content = response.text

# BeautifulSoup ile parse etme
soup = BeautifulSoup(html_content, "html.parser")

# Tüm <link> etiketlerini bulma
links = soup.find_all("link", rel="alternate")

# Her linkin href ve hreflang değerlerini yazdırma
for link in links:
    href = link.get("href")
    hreflang = link.get("hreflang")
    print(f"hreflang: {hreflang}, href: {href}")
