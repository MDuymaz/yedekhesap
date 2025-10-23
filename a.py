import requests

def fetch_full_html(url: str, referer: str = "https://www.google.com/") -> str:
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/117.0.0.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": referer,
        "Connection": "keep-alive",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        if resp.encoding is None or resp.encoding.lower() == 'iso-8859-1':
            resp.encoding = resp.apparent_encoding
        return resp.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"İstek başarısız: {e}") from e

if __name__ == "__main__":
    url = "https://diziyo.to/"
    try:
        html = fetch_full_html(url, referer="https://www.google.com/")
        print(html)  # Tam HTML'i direkt ekrana yazdırır
    except Exception as err:
        print("Hata:", err)
