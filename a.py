#!/usr/bin/env python3
# fetch_dizipod.py
import sys
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

# Gerçekçi User-Agent listesi (çeşitli modern tarayıcılar)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

def build_headers(url):
    ua = random.choice(USER_AGENTS)
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    headers = {
        "User-Agent": ua,
        "Referer": origin + "/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Connection": "keep-alive",
        "Origin": origin,
        # bazı sunucular için ek başlıklar faydalı olabilir
        "Upgrade-Insecure-Requests": "1",
    }
    return headers

def create_session(retries=3, backoff_factor=0.3, status_forcelist=(429, 500, 502, 503, 504)):
    s = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'HEAD'])
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

def fetch_html(url, timeout=15):
    headers = build_headers(url)
    sess = create_session()
    try:
        resp = sess.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        print(f"[*] Başarılı: {resp.status_code}\n")
        print(resp.text)
        return resp.text
    except requests.exceptions.HTTPError as e:
        # 403 düzenli olarak dönebilir; durumu göster
        status = getattr(e.response, "status_code", "N/A")
        print(f"[!] HTTP Hatası: {status} - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[!] İstek hatası: {e}")
    return None

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://dizipod.com/"
    fetch_html(target)
