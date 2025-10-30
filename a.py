import requests

url = "https://dizipod.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://dizipod.com/"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    print("=== HTML Başarıyla Çekildi ===\n")
    print(response.text)
except requests.RequestException as e:
    print(f"HTML çekilirken hata oluştu: {e}")

