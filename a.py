import cloudscraper

# --- Cloudflare korumalı scraper ---
scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

# --- Headers ---
scraper.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.6668.100 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://google.com/",
})

# --- URL ---
url = "https://filmhane.online/dizi/kaosun-anatomisi"

# --- HTML'i çek ---
response = scraper.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print(f"HTML alınamadı! Status code: {response.status_code}")
