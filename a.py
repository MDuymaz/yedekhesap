import asyncio
from playwright.async_api import async_playwright
import re

async def wait_until_ready(page):
    while True:
        html = await page.content()
        if re.search(r"wait|\bsaniye\b|\bseconds\b", html, re.I):
            print("Bekleme ekranı algılandı. Sayfa yenileniyor...")
            await asyncio.sleep(1)
            await page.reload()
        else:
            print("Bekleme ekranı bitti.")
            break


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-gpu"
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="Europe/Istanbul"
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = await context.new_page()
        await page.goto("https://sezonlukdizi8.com/player/link.asp")

        await wait_until_ready(page)

        xpath = "/html/body/div/div/a[1]"
        await page.wait_for_selector(f"xpath={xpath}")

        async with page.expect_popup() as popup_info:
            await page.click(f"xpath={xpath}")

        new_page = await popup_info.value

        print("Yeni sayfa açıldı, DOM yüklenmesi bekleniyor...")
        await new_page.wait_for_load_state("domcontentloaded")

        print("HTML içeriği kontrol ediliyor...")

        # 🔥 HTML hazır olana kadar deneme (network idle yok)
        html = ""
        for _ in range(30):   # en fazla 3 saniye (30 x 0.1s)
            html = await new_page.content()

            # Head tag doldu mu kontrol et
            if "<head>" in html and "</head>" in html:
                print("HTML yeterince yüklendi.")
                break
            
            await asyncio.sleep(0.1)

        print("\n----- HTML BAŞLANGIÇ -----\n")
        print(html[:2000])    # İstersen tümünü yazdırabilirim
        print("\n---------------------------\n")

        await browser.close()

asyncio.run(main())
