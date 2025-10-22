# dizipal_episodes_selenium_m3u.py
# Gereksinimler:
# pip install selenium webdriver-manager beautifulsoup4

import time
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# -------------------------
# Ayarlar
# -------------------------
DOMAIN_URL = "https://raw.githubusercontent.com/zerodayip/domain/refs/heads/main/dizipal.txt"
JSON_FILE = "dizipal/diziler.json"
OUTPUT_FILE = "dizipalyerlidizi.m3u"

# Tarayıcı ve bekleme ayarları
INITIAL_PAGE_WAIT = 30       # Ana sayfa için sabit bekleme (isteğin üzerine)
PAGE_LOAD_MAX_WAIT = 30      # Her sayfa için maksimum bekleme (saniye)
HTML_PRINT_LIMIT = 2000      # Terminale yazdırılacak HTML uzunluğu (karakter)
RETRY_COUNT = 1              # Eğer istersen sayfa açmada retry koyabilirsin

# -------------------------
# Selenium başlatma (Chrome)
# -------------------------
def make_chrome_driver(headless=True):
    options = webdriver.ChromeOptions()
    # Headless kullanmak istersen True bırak, bazı siteler headless'i algılar; gerekirse False yap
    if headless:
        options.add_argument("--headless=new")  # chromium 109+ için yeni headless daha stabil
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    # Tarayıcı fingerprint azaltma
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Servisi oluştur (webdriver-manager ile)
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Navigator.webdriver özelliğini gizleme (CDP injection)
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.__selenium_forced_navigator_webdriver = undefined;
                """
            },
        )
    except Exception:
        pass

    return driver

# -------------------------
# Sayfa yükleme / bekleme
# -------------------------
def load_page_and_wait(driver, url, max_wait=PAGE_LOAD_MAX_WAIT, check_strings=None):
    """
    driver.get(url) yapar, sonra max_wait süresince sayfa kaynağını kontrol eder.
    check_strings: eğer verilen listede bir ifade sayfada bulunuyorsa 'başarılı' sayılır.
    Eğer check_strings None ise, "Just a moment" başlığı kalkana kadar bekler.
    Dönen: (page_source, status_ok_bool)
    """
    driver.get(url)

    # Windows / env koşullarında ilk render için küçük bekleme
    start = time.time()
    while True:
        page_source = driver.page_source
        title = driver.title or ""
        elapsed = time.time() - start

        # 1) Eğer sayfa title "Just a moment" içeriyorsa muhtemelen cloudflare challenge
        if check_strings:
            # eğer herhangi bir check_string bulunuyorsa başarılı kabul et
            for s in check_strings:
                if s.lower() in page_source.lower():
                    return page_source, True
        else:
            # default kontrol: title "Just a moment" değilse veya "Enable JavaScript" yoksa başarılı
            if "just a moment" not in title.lower() and "enable javascript" not in page_source.lower():
                # ayrıca sayfada episode-item gibi beklenen seçici varsa da başarılı
                if "episode-item" in page_source or re.search(r"IMDB\s*Puan", page_source, re.I):
                    return page_source, True
                # eğer challenge yazısı yok ama içerik değişmişse de kabul et
                if "checking your browser" not in page_source.lower():
                    return page_source, True

        if elapsed >= max_wait:
            return page_source, False

        time.sleep(1)

# -------------------------
# Scrape fonksiyonu (BeautifulSoup ile pars)
# -------------------------
def scrape_series_episodes_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    imdb_div = soup.find("div", class_="key", string=re.compile(r"IMDB", re.I))
    if imdb_div:
        value_div = imdb_div.find_next_sibling("div", class_="value")
        imdb_score = value_div.get_text(strip=True) if value_div else "-"
    else:
        imdb_score = "-"

    episodes = []
    for ep_div in soup.select("div.episode-item a[href]"):
        ep_href = ep_div.get("href")
        ep_title_div = ep_div.select_one("div.episode")
        ep_title = ep_title_div.get_text(strip=True) if ep_title_div else "-"
        episodes.append({"href": ep_href, "title": ep_title})

    # fallback: linkleri tarayıp 'bolum' gibi anahtar kelimeye göre al
    if not episodes:
        for a in soup.select("a[href]"):
            href = a.get("href")
            txt = a.get_text(strip=True) or ""
            if href and ("/bolum" in href.lower() or "bölüm" in txt.lower()):
                episodes.append({"href": href, "title": txt or href})

    return {"imdb": imdb_score, "episodes": episodes}

# -------------------------
# Ana akış
# -------------------------
def main():
    # 0) Chrome driver oluştur
    # Eğer Cloudflare çok sıkıysa headless=False dene (görünür tarayıcı).
    headless = True  # gerekirse False yap
    driver = None
    try:
        driver = make_chrome_driver(headless=headless)
    except WebDriverException as e:
        print("❌ Chrome driver başlatılamadı:", e)
        print("Chrome yüklü mü? Driver/Chrome sürüm uyuşmazlığı olabilir.")
        return

    try:
        # 1) DOMAIN_URL'den BASE_URL al
        print("🌍 Domain bilgisi alınıyor (tarayıcı ile)...")
        # Gitmek için direkt requests değil selenium kullanıyoruz (bazı ortamlar için GitHub raw sayfası açılmayabilir; burayı basit bir get olarak da bırakabilirsin)
        driver.get(DOMAIN_URL)
        time.sleep(1)
        domain_page = driver.page_source
        # raw içeriği body içinde düz metin olarak gelecektir; basit regex ile al
        m = re.search(r"https?://[^\s'\"<>]+", domain_page)
        if m:
            BASE_URL = m.group(0).strip()
            print(f"🌍 Kullanılan BASE_URL (bulundu): {BASE_URL}")
        else:
            # fallback: sayfayı direkt text olarak almayı dene
            text_only = re.sub(r"<[^>]+>", "", domain_page)
            BASE_URL = text_only.strip().splitlines()[0].strip()
            print(f"🌍 Kullanılan BASE_URL (fallback): {BASE_URL}")

        # 2) Ana sayfa için sabit bekleme
        print(f"⏳ Ana sayfa yükleniyor, {INITIAL_PAGE_WAIT} saniye bekleniyor...", flush=True)
        time.sleep(INITIAL_PAGE_WAIT)

        # 3) JSON oku
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            series_data = json.load(f)

        # 4) M3U dosyası aç
        with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u_file:
            print("#EXTM3U", flush=True, file=m3u_file)

            for series_href, info in series_data.items():
                group = info.get("group", "UNKNOWN")
                tvg_logo = info.get("tvg-logo", "")
                print(f"\n🎬 {group} bölümleri çekiliyor.", flush=True)

                # tam url
                target_url = f"{BASE_URL}{series_href}"

                # sayfayı headless tarayıcı ile aç ve bekle
                page_html, ok = load_page_and_wait(driver, target_url, max_wait=PAGE_LOAD_MAX_WAIT)

                # Debug: ilk kısmı yazdır
                print(f"\n📄 {target_url} HTML (ilk {HTML_PRINT_LIMIT} karakter):")
                if page_html:
                    print(page_html[:HTML_PRINT_LIMIT])
                else:
                    print("⚠️ HTML boş geldi.")

                if not ok:
                    print(f"⚠️ {group}: Sayfa yüklenemedi veya Cloudflare challenge kaldı (timeout).")
                    continue

                # Pars et
                try:
                    data = scrape_series_episodes_from_html(page_html)
                except Exception as e:
                    print(f"⚠️ {group} parsing hatası: {e}")
                    continue

                imdb_score = data.get("imdb", "-")
                episodes = data.get("episodes", [])

                if not episodes:
                    print(f"⚠️ {group}: Hiç bölüm bulunamadı.")
                    continue

                for ep in episodes:
                    ep_href = ep.get("href")
                    ep_title_full = (ep.get("title") or "").upper()

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

                    proxy_url = f"https://zerodayip.com/proxy/dizipal?url={BASE_URL}{ep_href}"

                    print(extinf_line, file=m3u_file, flush=True)
                    print(proxy_url, file=m3u_file, flush=True)

    finally:
        if driver:
            driver.quit()

    print(f"\n✅ Dizipal m3u dosyası hazırlandı: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
