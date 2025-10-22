import cloudscraper
import time
from bs4 import BeautifulSoup
import json
import re

# Github üzerinden domain alma
DOMAIN_URL = "https://raw.githubusercontent.com/zerodayip/domain/refs/heads/main/dizipal.txt"
scraper = cloudscraper.create_scraper()

response = scraper.get(DOMAIN_URL)
if response.status_code != 200:
    raise Exception(f"Domain alınamadı! Hata: {response.status_code}")
BASE_URL = response.text.strip()
print(f"🌍 Kullanılan BASE_URL: {BASE_URL}", flush=True)

# Ana sayfa için 30 saniye bekle
print("⏳ Ana sayfa yükleniyor, 30 saniye bekleniyor...", flush=True)
time.sleep(30)

# JSON dosyasından dizileri oku
JSON_FILE = "dizipal/diziler.json"
with open(JSON_FILE, "r", encoding="utf-8") as f:
    series_data = json.load(f)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

OUTPUT_FILE = "dizipalyerlidizi.m3u"

def scrape_series_episodes(series_href):
    url = f"{BASE_URL}{series_href}"
    resp = scraper.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # IMDb puanını al
    imdb_div = soup.find("div", class_="key", string="IMDB Puanı")
    if imdb_div:
        value_div = imdb_div.find_next_sibling("div", class_="value")
        imdb_score = value_div.get_text(strip=True) if value_div else "-"
    else:
        imdb_score = "-"

    # Bölümleri al
    episodes = []
    for ep_div in soup.select("div.episode-item a[href]"):
        ep_href = ep_div.get("href")
        ep_title_div = ep_div.select_one("div.episode")
        ep_title = ep_title_div.get_text(strip=True) if ep_title_div else "-"
        episodes.append({"href": ep_href, "title": ep_title})

    return {"imdb": imdb_score, "episodes": episodes}

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u_file:
        print("#EXTM3U", flush=True, file=m3u_file)

        for series_href, info in series_data.items():
            print(f"🎬 {info['group']} bölümleri çekiliyor.", flush=True)

            try:
                data = scrape_series_episodes(series_href)
                imdb_score = data["imdb"]
                tvg_logo = info["tvg-logo"]
                group = info["group"]

                for ep in data["episodes"]:
                    ep_href = ep["href"]
                    ep_title_full = ep["title"].upper()

                    season_match = re.search(r"(\d+)\.\s*SEZON", ep_title_full)
                    episode_match = re.search(r"(\d+)\.\s*BÖLÜM", ep_title_full)
                    season = season_match.group(1).zfill(2) if season_match else "01"
                    episode = episode_match.group(1).zfill(2) if episode_match else "01"

                    tvg_name = f"{group.upper()} S{season}E{episode}"
                    extinf_line = f'#EXTINF:-1 tvg-id="" tvg-name="{tvg_name.upper()}" tvg-logo="{tvg_logo}" group-title="{group.upper()}", {group.upper()} {season}. SEZON {episode} (IMDb: {imdb_score} | YERLİ DİZİ | DIZIPAL)'
                    proxy_url = f"https://zerodayip.com/proxy/dizipal?url={BASE_URL}{ep_href}"

                    print(extinf_line, file=m3u_file, flush=True)
                    print(proxy_url, file=m3u_file, flush=True)

            except Exception as e:
                print(f"⚠️ {group} için hata: {e}", flush=True)

    print(f"\n✅ Dizipal m3u dosyası hazırlandı.", flush=True)

if __name__ == "__main__":
    main()
