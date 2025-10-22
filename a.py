# file: dizipal_scraper.py

from playwright.sync_api import sync_playwright
import time

URL = "https://dizipal1212.com/diziler?kelime=&durum=&tur=24&type=&siralama="

def scroll_and_collect_series(url):
    with sync_playwright() as p:
        # Headless modda tarayıcı aç
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        known_titles = set()
        last_count = 0
        stable_rounds = 0

        while True:
            # Sayfadaki tüm <li> elemanlarını al
            lis = page.query_selector_all("article.movie-type-genres li")

            for li in lis:
                title_el = li.query_selector(".title")
                if title_el:
                    title = title_el.inner_text().strip()
                    if title not in known_titles:
                        known_titles.add(title)
                        img_el = li.query_selector("img[src]")
                        img = img_el.get_attribute("src") if img_el else "-"
                        print(f"🎬 {title}")
                        print(f"🖼️ Görsel: {img}")
                        print("-" * 60)

            # En alta doğru kaydır
            page.mouse.wheel(0, 4000)
            time.sleep(2)

            # Yeni dizi gelmiyorsa 3 tur sonra döngüden çık
            if len(known_titles) == last_count:
                stable_rounds += 1
            else:
                stable_rounds = 0

            if stable_rounds >= 3:
                break

            last_count = len(known_titles)

        print(f"\n✅ Toplam {len(known_titles)} dizi bulundu.")
        browser.close()

if __name__ == "__main__":
    scroll_and_collect_series(URL)
