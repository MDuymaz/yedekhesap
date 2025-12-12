import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
import re

url = "https://www.hdfilmcehennemi.ws/dizi/the-mighty-nein-3/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_imdb_poster(imdb_id):
    imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    try:
        res = requests.get(imdb_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        meta = soup.find("meta", property="og:image")
        if meta:
            return meta["content"]
    except Exception:
        pass
    return ""

async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()

async def fetch_episode_video(session, ep):
    link = ep['href']
    html = await fetch(session, link)
    soup = BeautifulSoup(html, "html.parser")

    # Video link
    iframe = soup.find("iframe", class_="rapidrame")
    video_link = iframe.get("data-src") if iframe else None

    # Bölüm başlığı
    title_tag = ep.find("h4", class_="mini-poster-title")
    title = title_tag.text.strip() if title_tag else "Bölüm Bilinmiyor"

    # Sezon ve bölüm numarası
    match = re.match(r"(\d+)\. Sezon (\d+)\. Bölüm", title)
    if match:
        season_num = int(match.group(1))
        episode_num = int(match.group(2))
    else:
        season_num = 0
        episode_num = 0

    # Dil bilgisi (Türkçe Altyazılı, Dublaj vs.)
    lang_tag = soup.find("button", class_="language-link")
    lang_text = lang_tag.text.strip() if lang_tag else "Bilinmiyor"

    # Dil metnini normalize et
    if "Türkçe Altyazılı" in lang_text:
        lang_text = "Türkçe Altyazı"
    elif lang_text.startswith("DUAL"):
        lang_text = "DUBLAJ & ALTYAZI"

    if video_link:  # Sadece video link varsa döndür
        return {
            "Bölüm Başlığı": title,
            "Video Link": video_link,
            "Season": season_num,
            "Episode": episode_num,
            "Language": lang_text
        }
    return None

async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")

        # Ana başlık
        h1 = soup.find("h1", class_="section-title")
        main_title = h1.contents[0].strip() if h1 else "Bilinmiyor"
        if main_title.lower().endswith(" izle"):
            main_title = main_title[:-5].strip()

        # Yıl
        year_tag = soup.select_one("div.post-info-year-country a")
        year = year_tag.text.strip() if year_tag else "Bilinmiyor"

        # IMDB ID
        imdb_tag = soup.select_one("div.post-info-imdb a")
        imdb_id = imdb_tag.get("data-id") if imdb_tag else "Bilinmiyor"

        # IMDB Puan
        rating_tag = soup.select_one("div.post-info-imdb-rating span")
        imdb_rating = rating_tag.contents[0].strip() if rating_tag else "Bilinmiyor"

        # IMDB Poster
        imdb_poster = get_imdb_poster(imdb_id) if imdb_id != "Bilinmiyor" else ""

        # Bölümler
        episodes = soup.find_all("a", class_="mini-poster without-image")
        tasks = [fetch_episode_video(session, ep) for ep in episodes]

        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]

        # EXTINF formatında yazdır
        for r in results:
            extinf = (
                f'#EXTINF:-1 tvg-id="{imdb_id}" '
                f'tvg-name="{main_title}({year}) S{r["Season"]:02}E{r["Episode"]:02}" '
                f'tvg-logo="{imdb_poster}" group-title="NETFLIX DİZİLERİ",'
                f'{main_title}({year}) {r["Bölüm Başlığı"]} (IMDb: {imdb_rating} | {r["Language"]} | YDIZIBOX)\n'
                f'/proxy/hdfilmcehennemi?url={r["Video Link"]}'
            )
            print(extinf)

asyncio.run(main())
