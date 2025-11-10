import requests

url = "https://www.tranimeizle.io/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Hata oluştu: {e}")
