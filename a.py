from playwright.sync_api import sync_playwright

url = "https://dizipod.com/"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,  # BOT gibi görünmemek için
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ]
    )

    context = browser.new_context(
        viewport={"width": 1400, "height": 900},
        locale="tr-TR",
        timezone_id="Europe/Istanbul",
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"),
    )

    page = context.new_page()
    page.goto(url, wait_until="networkidle")

    # Basit “insan davranışı”
    page.mouse.move(200, 200)
    page.wait_for_timeout(800)
    page.keyboard.press("PageDown")
    page.wait_for_timeout(1000)

    html = page.content()
    print(html)

    browser.close()
