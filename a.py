# dizipal_episodes_m3u.py
# Gereksinim: pip install cloudscraper beautifulsoup4
import time
import json
import re
import cloudscraper
from bs4 import BeautifulSoup

# -------------------------
# Ayarlar / sabitler
# -------------------------
DOMAIN_URL = "https://raw.githubusercontent.com/zerodayip/domain/refs/heads/main/dizipal.txt"
JSON_FILE = "dizipal/diziler.json"
OUTPUT_FILE = "dizipalyerlidizi.m3u"

# Kaç karakter HTML'i yazdırmak istersin (çok uzunsa terminali doldurabilir)
HTML_PRINT_LIMIT = 2000

# Her sayfa isteği için en fazla kaç deneme yapılsın
MAX_RETRIES = 3
# İstek zaman aşımı (saniye)
REQUEST_TIMEOUT = 15

# Cloudscraper oluştur
scraper = cloudscraper.create_scraper()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    # Referer dinamik olarak BASE_URL olarak ayarlanacak
}

# -------------------------
# Yardımcı fonksiyonlar
# -------------------------
def fetch_text_with_retries(url, headers=None, timeout=REQUEST_TIMEOUT, max_retries=MAX_RETRIES):
    """
    Verilen URL'den cloudscraper ile GET yapar. Başarısız olursa birkaç kez tekrar dener.
    Dönen response.text'i ve status_code'u tuple olarak döndürür.
    """
    attempt = 0
    wait_seconds = 2
    last_resp = None

    while attempt < max_retries:
        attempt += 1
        try:
            resp = scraper.get(url, headers=headers or {}, timeout=timeout)
            last_resp = resp
            # Her denemede status code'u kontrol et; 200 gelirse RETURN et
            if resp.status_code == 200:
                return resp.text, resp.status_code
            else:
                # 403 veya 503 gibi durumlarda challenge sayfası gelebilir, HTML'i incelemek için döndürmeden önce loglayacağız
                print(f"⚠️ Deneme {attempt}/{max_retries}: HTTP {resp.status_code} döndü for {url}.")
                # Eğer halen deneme hakkı varsa bekle ve tekrar dene
                if attempt < max_retries:
                    time.sleep(wait_seconds)
                    wait_seconds *= 2
                else:
                    return resp.text, resp.status_code
        except Exception as e:
            print(f"⚠️ Deneme {attempt}/{max_retries} sırasında istisna oluştu: {e}")
            if attempt < max_retries:
                time.sleep(wait_seconds)
                wait_seconds *= 2
            else:
                raise

    # Eğer hiç dönemediysek son resp veya None dönebilir
    if last_resp:
        return last_resp.text, last_resp.status_code
    return None, None

def scrape_series_episodes(series_href, base_url, headers):
    """
    Tek bir dizi sayfasını çeker, HTML'i yazdırır ve bölüm listesini + IMDb puanını döndürür.
    """
    url = f"{base_url}{series_href}"
    html_text, status = fetch_text_with_retries(url, headers=headers)

    # Gelen HTML'i her durumda yazdır (kısmî)
    separator = "-" * 40
    print(f"\n📄 {url} sayfasının HTML (ilk {HTML_PRINT_LIMIT} karakter):\n{separator}")
    if html_text is None:
        print("⚠️ Hiçbir cevap alınamadı (html_text is None).")
    else:
        # Güvenlik: terminali aşırı doldurmamak için limitli yazdır
        print(html_text[:HTML_PRINT_LIMIT])
    print(f"\n{separator}\nHTTP status: {status}\n")

    # Eğer 200 değilse hata fırlat
    if status != 200:
        raise Exception(f"Sayfa açılamadı! HTTP {status}")

    soup = BeautifulSoup(html_text, "html.parser")

    # IMDb puanını al
    imdb_div = soup.find("div", class_="key", string=re.compile(r"IMDB", re.I))
    if imdb_div:
        value_div = imdb_div.find_next_sibling("div", class_="value")
        imdb_score = value_div.get_text(strip=True) if value_div else "-"
    else:
        imdb_score = "-"

    # Bölümleri al (site yapısına göre seçici)
    episodes = []
    # Eğer site farklı bir sınıf kullanıyorsa burayı değiştirebilirsin
    for ep_div in soup.select("div.episode-item a[href]"):
        ep_href = ep_div.get("href")
        ep_title_div = ep_div.select_one("div.episode")
        ep_title = ep_title_div.get_text(strip=True) if ep_title_div else "-"
        episodes.append({"href": ep_href, "title": ep_title})

    # Eğer yukarıdaki seçici boş dönerse alternatif olarak bağlantıları gözetleyelim
    if not episodes:
        for a in soup.select("a[href]"):
            # örnek: href içinde '/dizi/' ve 'bolum' gibi pattern'ler aranabilir
            href = a.get("href")
            txt = a.get_text(strip=True) or ""
            if href and "/bolum" in href.lower() or "bölüm" in txt.lower():
                episodes.append({"href": href, "title": txt or href})

    return {"imdb": imdb_score, "episodes": episodes}

# -------------------------
# Ana akış
# -------------------------
def main():
    # 1) Github üzerinden domain al
    print("🌍 Domain bilgisi alınıyor...")
    domain_text, domain_status = fetch_text_with_retries(DOMAIN_URL, headers=HEADERS)
    if domain_text is None or domain_status != 200:
        raise Exception(f"Domain alınamadı! HTTP {domain_status}")

    BASE_URL = domain_text.strip()
    print(f"🌍 Kullanılan BASE_URL: {BASE_URL}")

    # Referer header'ını BASE_URL olarak güncelle
    HEADERS["Referer"] = BASE_URL

    # 2) Ana sayfa yüklenmesi için bekleme
    print("⏳ Ana sayfa yükleniyor, 30 saniye bekleniyor...", flush=True)
    time.sleep(30)

    # 3) JSON dosyasını oku
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        series_data = json.load(f)

    # 4) m3u dosyasını oluştur
    with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u_file:
        print("#EXTM3U", flush=True, file=m3u_file)

        for series_href, info in series_data.items():
            # group değişkenini try dışında tanımlıyoruz (hata sırasında da kullanılabilsin)
            group = info.get("group", "UNKNOWN")
            tvg_logo = info.get("tvg-logo", "")
            print(f"🎬 {group} bölümleri çekiliyor.", flush=True)

            try:
                data = scrape_series_episodes(series_href, BASE_URL, HEADERS)
                imdb_score = data.get("imdb", "-")

                for ep in data.get("episodes", []):
                    ep_href = ep.get("href")
                    ep_title_full = (ep.get("title") or "").upper()

                    # Sezon ve bölüm numarasını ayıkla
                    season_match = re.search(r"(\d+)\.\s*SEZON", ep_title_full)
                    episode_match = re.search(r"(\d+)\.\s*BÖLÜM", ep_title_full)
                    season = season_match.group(1).zfill(2) if season_match else "01"
                    episode = episode_match.group(1).zfill(2) if episode_match else "01"

                    tvg_name = f"{group.upper()} S{season}E{episode}"
                    extinf_line = (
                        f'#EXTINF:-1 tvg-id="" tvg-name="{tvg_name.upper()}" '
                        f'tvg-logo="{tvg_logo}" group-title="{group.upper()}", '
                        f'{group.upper()} {season}. SEZON {episode} (IMDb: {imdb_score} | YERLİ DİZİ | DIZIPAL)'
                    )

                    # proxy url (eski mantığınla aynı)
                    proxy_url = f"https://zerodayip.com/proxy/dizipal?url={BASE_URL}{ep_href}"

                    # Dosyaya yaz
                    print(extinf_line, file=m3u_file, flush=True)
                    print(proxy_url, file=m3u_file, flush=True)

            except Exception as e:
                # Hata mesajında group kullanımı güvenli (try dışında tanımlı)
                print(f"⚠️ {group} için hata: {e}", flush=True)

    print(f"\n✅ Dizipal m3u dosyası hazırlandı: {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    main()
