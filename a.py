from playwright.sync_api import sync_playwright
import requests
import time
import json
import os

DOMAIN_URL = "https://raw.githubusercontent.com/zerodayip/domain/refs/heads/main/dizipal.txt"
response = requests.get(DOMAIN_URL)
if response.status_code != 200:
    raise Exception(f"Domain alınamadı! Hata: {response.status_code}")

BASE_URL = response.text.strip()
print(f"🌍 Kullanılan BASE_URL: {BASE_URL}", flush=True)

LIST_URL = f"{BASE_URL}/diziler?kelime=&durum=&tur=24&type=&siralama="
OUTPUT_DIR = "dizipal"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "diziler.json")

def scroll_and_collect_series(url):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Gelen HTML'i yazdır
        html_content = page.content()
        print("📄 Gelen HTML:", html_content, flush=True)

        series_dict = {}
        last_count = 0
        stable_rounds = 0

        while True:
            lis = page.query_selector_all("article.movie-type-genres li")

            for li in lis:
                link_el = li.query_selector("a[data-date]")
                title_el = li.query_selector(".title")
                img_el = li.query_selector("img[src]")

                if link_el and title_el and img_el:
                    link = link_el.get_attribute("href")  # sadece /dizi/... kısmı
                    title = title_el.inner_text().strip()
                    img = img_el.get_attribute("src")

                    if link not in series_dict:
                        series_dict[link] = {
                            "group": title,
                            "tvg-logo": img
                        }
                        print(f"🎬 {title.upper()} bulundu.", flush=True)

            # Kaydır
            page.mouse.wheel(0, 4000)
            time.sleep(2)

            # Yeni eleman yoksa 3 tur bekle ve çık
            if len(series_dict) == last_count:
                stable_rounds += 1
            else:
                stable_rounds = 0

            if stable_rounds >= 3:
                break

            last_count = len(series_dict)

        # JSON dosyasına kaydet
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(series_dict, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Toplam {len(series_dict)} dizi bulundu ve '{OUTPUT_FILE}' dosyasına kaydedildi.", flush=True)
        browser.close()

if __name__ == "__main__":
    scroll_and_collect_series(LIST_URL)
