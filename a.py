import requests

url = "https://www.hdfilmcehennemi.ws/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

try:
    response = requests.get(url, headers=headers, timeout=10)

    # Sunucu hata döndürdüyse exception fırlat
    response.raise_for_status()

    # HTML içeriğini yazdır
    print(response.text)

except requests.exceptions.RequestException as e:
    print("Bir hata oluştu:", e)
