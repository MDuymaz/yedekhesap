from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "https://dizipod.com/"

def fetch_html(url: str, headless: bool = True) -> str:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent=ua,
            viewport={"width": 1280, "height": 800},
            locale="tr-TR",
            extra_http_headers={
                "Referer": origin + "/",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timezone_id="Europe/Istanbul"
        )

        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()
        return html

if __name__ == "__main__":
    try:
        html = fetch_html(TARGET, headless=True)
        print("=== HTML Başarıyla Alındı ===\n")
        print(html)
    except Exception as e:
        print(f"HTML çekilirken hata oluştu: {e}")
