from playwright.sync_api import sync_playwright
import re

url = "https://www.youtube.com/watch?v=pfQeMtSBv_Y"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # headless=False yaparsanız tarayıcıyı görürsünüz
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto(url)

    # Sayfanın tamamen yüklenmesini bekleyin
    page.wait_for_timeout(5000)

    # Sayfa kaynağını alın
    html_content = page.content()

    # .m3u8 linklerini ara
    m3u8_links = re.findall(r'https?://[^\s"\']+\.m3u8', html_content)
    if m3u8_links:
        print("Bulunan m3u8 linkleri:\n")
        for link in m3u8_links:
            print(link)
    else:
        print("Herhangi bir .m3u8 linki bulunamadı.")

    browser.close()
