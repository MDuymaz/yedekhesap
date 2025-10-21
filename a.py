import requests

url = "https://dizipal1066.com/"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://dizipal1066.com/",
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    print(response.text)  # HTML içeriğini ekrana basar
except requests.exceptions.RequestException as e:
    print("Hata oluştu:", e)
