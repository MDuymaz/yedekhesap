import requests
from bs4 import BeautifulSoup
import re

url = "https://diziyo.to/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Referer": "https://diziyo.to/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", id="load-episode-container")

    if ul:
        items = ul.find_all("li")
        results = []

        for li in items:
            a_tag = li.find("a", href=True)
            title_tag = li.find("h3")

            if a_tag and title_tag:
                full_link = a_tag["href"]  # örn: /dizi/elsbeth/sezon-3/bolum-2
                # sadece /dizi/elsbeth kısmını al:
                match = re.match(r"(/dizi/[^/]+)", full_link)
                short_link = match.group(1) if match else full_link

                title = title_tag.get_text(strip=True)
                results.append((title, short_link))

        # Sonuçları yazdır
        if results:
            for name, link in results:
                print(f"{name} --> {link}")
        else:
            print("❌ Hiç dizi bulunamadı.")
    else:
        print("❌ <ul id='load-episode-container'> bulunamadı.")
else:
    print(f"❌ İstek başarısız. Status code: {response.status_code}")
