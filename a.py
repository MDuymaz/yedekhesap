# a_all_channels_with_map_li7.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime, timedelta
import time, os, gzip, re

# --- AYARLAR ---
BASE_URL = "https://tvplus.com.tr/canli-tv/yayin-akisi"
LI_XPATH_TEMPLATE = "/html/body/div[1]/div/div[1]/div/main/div/div[2]/ul/li[{}]"
LEFT_BUTTON_XPATH  = "/html/body/div[1]/div/div[1]/div/main/div/div[2]/button[1]"
RIGHT_BUTTON_XPATH = "/html/body/div[1]/div/div[1]/div/main/div/div[2]/button[2]"

HEADLESS = True
DELAY = 0.6
MAX_SWIPES = 6
RETRY_PER_TARGET = 2
START_IDX = 7          # artık li taraması 7'den başlıyor
TOTAL_TARGETS = 5     # kaç li taranacak, 7’den sonrası için

OUTPUT_XML = "epg/kanal_epg.xml"
OUTPUT_GZ  = "epg/kanal_epg.gz"
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# 🌐 EPG map: sitedeki kanal adı -> birden fazla EPG ID
channel_map = {
    "EPIC DRAMA": ["4K TR: EPIC DRAMA"],
    "FX": ["4K TR: FX HD", "FX"],
    "tabii TV": ["TABII TV"],
    "SİNEMA YERLİ": ["4K TR: S NEMA YERL HD"],
    "SİNEMA TV": ["4K TR: S NEMA TV HD"],
    "SİNEMA TV AKSİYON": ["4K TR: S NEMA TV AKS YON HD"],
    "SİNEMA KOMEDİ": ["4K TR: S NEMA KOMED HD"],
    "SİNEMA AİLE": ["4K TR: S NEMA A LE HD"],
    "SİNEMA TV 1001": ["4K TR: S NEMA TV 1001 HD"],
    "SİNEMA YERLİ 2": ["4K TR: S NEMA YERL 2 HD"],
    "SİNEMA TV 2": ["4K TR: S NEMA TV 2 HD"],
    "SİNEMA AKSİYON 2": ["4K TR: S NEMA AKS YON 2 HD"],
    "SİNEMA AİLE 2": ["4K TR: S NEMA A LE 2 HD"],
    "SİNEMA TV 1002": ["4K TR: S NEMA TV 1002 HD"],
    "TRT1": ["TRT 1", "TRT 1 4K", "TRT 1 HD", "TRT 1 FHD", "TRT 1 HEVC", "TRT 1 RAW", "TRT 1 SD"],
    "KANAL D": ["4K TR: KANAL D HD", "KANAL D", "KANAL D FHD", "KANAL D HD", "KANAL D HEVC", "KANAL D RAW", "KANAL D SD"],
    "STAR TV": ["4K TR: STAR TV HD", "STAR TV", "STAR TV FHD", "STAR TV HD", "STAR TV HEVC", "STAR TV RAW"],
    "ATV": ["4K TR: ATV HD", "ATV", "ATV HD", "ATV HEVC", "ATV RAW", "ATV SD"],
    "SHOW TV": ["4K TR: SHOW TV HD", "SHOW TV", "SHOW TV FHD", "SHOW TV HD", "SHOW TV HEVC", "SHOW TV RAW","SHOW TV SD"],
    "NOW": ["4K TR: NOW HD", "NOW TV FHD", "NOW TV HD", "NOW TV"],
    "TV8": ["4K TR: TV8 HD", "TV 8", "TV 8 HD", "TV 8 HEVC", "TV 8 SD", "TV8 FHD", "TV8 RAW"],
    "360": ["360", "360 PLUS", "360 RAW", "4K TR: 360 HD"],
    "A2": ["4K TR: A2 HD", "A2", "A2 HD", "A2 HEVC", "A2 RAW", "A2 TV SD"],
    "TLC": ["TLC", "TLC TV"],
    "CNBC-E": ["CNBC-E"],
    "TEVE2": ["4K TR: TEVE2 HD", "TEVE2 RAW", "TEVE 2"], 
    "KANAL 7": ["4K TR: KANAL 7 HD", "KANAL 7", "KANAL 7 FHD", "KANAL 7 HD", "KANAL 7 HEVC", "KANAL 7 RAW"],
    "BEYAZ TV": ["4K TR: BEYAZ TV HD", "BEYAZ TV", "BEYAZ TV FHD", "BEYAZ TV HD", "BEYAZ TV HEVC", "BEYAZ TV RAW"],
    "TV100": ["4K TR: TV100", "TV100"],
    "DMAX": ["4K TR: DMAX HD", "DMAX", "DMAX HD", "DMAX HEVC"],
    "TV8,5": ["4K TR: TV8.5", "TV 8.5 FHD", "TV 8.5 HD", "TV 85", "TV8 5 RAW"],
    "TRT 2": ["4K TR: TRT 2 HD", "TRT 2", "TRT 2 UHD"],
    "TV 4": ["4K TR: TV 4", "TV 4"],
    "EKOL TV": ["4K TR: EKOL TV", "EKOL TV", "EKOL TV SD"],
    "CNN TÜRK": ["4K TR: CNN T RK HD", "CNN T RK HD+ SD", "CNN T RK HEVC", "CNN T RK RAW", "CNN TURK", "CNN TURK HD"],
    "NTV": ["4K TR: NTV HD", "NTV", "NTV HABER", "NTV HABER HD", "NTV HABER HEVC", "NTV HD","NTV RAW","NTV SD"],
    # ... diğer kanalları aynı şekilde ekleyebilirsiniz
}

# --- Yardımcı fonksiyonlar ---
def to_utc_str(dt):
    """Türkiye saati -> UTC +3 saat"""
    return (dt + timedelta(hours=3)).strftime("%Y%m%d%H%M%S")

def parse_time_hm(timestr):
    """HH:MM formatını tuple (hour, minute) olarak döner"""
    m = re.match(r"^(\d{1,2}):(\d{2})$", timestr.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))

def parse_program_time(start_s, end_s):
    """Programın Türkiye saatini alır, UTC’ye çevirir ve gece taşmasını kontrol eder"""
    today = datetime.now().date()
    parsed_start = parse_time_hm(start_s)
    parsed_end   = parse_time_hm(end_s)
    if not parsed_start or not parsed_end:
        return None, None

    start_dt = datetime.combine(today, datetime.min.time()).replace(hour=parsed_start[0], minute=parsed_start[1])
    end_dt = datetime.combine(today, datetime.min.time()).replace(hour=parsed_end[0], minute=parsed_end[1])
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)  # gece yarısı taşması

    return to_utc_str(start_dt), to_utc_str(end_dt)

def xpath_click_via_js(page, xpath):
    script = """
    (xp) => {
        const n = document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (!n) return false;
        try { if (typeof n.click === 'function') { n.click(); return true; } } catch(e){}
        try { const ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); n.dispatchEvent(ev); return true; } catch(e){ return false; }
    }
    """
    try:
        return page.evaluate(script, xpath)
    except Exception as e:
        print("evaluate error:", e)
        return False

def element_exists(page, xpath):
    script = "(xp) => !!document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    try:
        return page.evaluate(script, xpath)
    except Exception:
        return False

def click_with_swipes(page, target_xpath, right_xpath=RIGHT_BUTTON_XPATH, max_swipes=MAX_SWIPES, delay=DELAY):
    if element_exists(page, target_xpath):
        if xpath_click_via_js(page, target_xpath):
            time.sleep(delay)
            return True
    for swipe in range(1, max_swipes+1):
        if element_exists(page, right_xpath):
            xpath_click_via_js(page, right_xpath)
            time.sleep(delay)
        else:
            break
        if element_exists(page, target_xpath):
            if xpath_click_via_js(page, target_xpath):
                time.sleep(delay)
                return True
    return False

def get_channel_links(page):
    script = """
    () => Array.from(document.querySelectorAll('a.multirow-channel-carousel__item')).map(a => a.href)
    """
    try:
        return page.evaluate(script)
    except Exception as e:
        print("Link alma hatası:", e)
        return []

# --- Tek kanal için EPG çek ---
def run_channel_epg(page, channel_url):
    programmes = []

    try:
        page.goto(channel_url, wait_until="domcontentloaded", timeout=45000)
    except PlaywrightTimeoutError:
        print("DOM yüklenmesinde timeout, devam ediliyor.")
    except Exception as e:
        print("Sayfa açılamadı:", e)
        return programmes

    time.sleep(1.0)

    try:
        h1_title = page.locator("h1.epg-container__title").text_content().strip()
        channel_name = h1_title.replace(" Yayın Akışı", "").upper()
    except Exception as e:
        print("Kanal adı alınamadı:", e)
        channel_name = ""

    channel_key = None
    for k in channel_map.keys():
        if k.upper() == channel_name:
            channel_key = k
            break
    if not channel_key:
        channel_key = channel_name

    epg_ids = channel_map.get(channel_key, [channel_key])
    print("Kanal map key:", channel_key)
    print("EPG ID listesi:", epg_ids)

    for idx in range(START_IDX, START_IDX + TOTAL_TARGETS):
        target_xpath = LI_XPATH_TEMPLATE.format(idx)

        clicked = False
        for attempt in range(1, RETRY_PER_TARGET + 1):
            if click_with_swipes(page, target_xpath, max_swipes=MAX_SWIPES, delay=DELAY):
                clicked = True
                break

        if not clicked and element_exists(page, RIGHT_BUTTON_XPATH):
            xpath_click_via_js(page, RIGHT_BUTTON_XPATH)
            time.sleep(DELAY)

        try:
            page.wait_for_selector("h3.epg-card__title", state="attached", timeout=4000)
        except:
            pass

        titles = page.locator("h3.epg-card__title")
        times  = page.locator("p.epg-card__time")
        cnt = min(titles.count(), times.count())

        for i in range(cnt):
            title = titles.nth(i).text_content().strip()
            time_text = times.nth(i).text_content().strip()
            if " - " not in time_text:
                continue
            start_s, end_s = [x.strip() for x in time_text.split(" - ", 1)]
            start_utc, end_utc = parse_program_time(start_s, end_s)
            if not start_utc or not end_utc:
                continue

            for epg_id in epg_ids:
                programmes.append({
                    "channel": epg_id,
                    "day_index": idx,
                    "start": start_utc,
                    "stop": end_utc,
                    "title": title
                })

        time.sleep(DELAY)

    return programmes

# --- Tüm kanallar için --- 
def run_all_channels_epg():
    programmes_all = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=45000)
        except PlaywrightTimeoutError:
            print("Ana sayfa DOM timeout, devam ediliyor.")
        except Exception as e:
            print("Ana sayfa açılamadı:", e)
            browser.close()
            return

        time.sleep(1)
        links = get_channel_links(page)
        print(f"{len(links)} kanal bulundu.")

        for link in links:
            programmes_all.extend(run_channel_epg(page, link))

        browser.close()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'
    channels = sorted({p["channel"] for p in programmes_all})
    for ch in channels:
        xml += f'  <channel id="{ch}">\n'
        xml += f'    <display-name>{ch}</display-name>\n'
        xml += f'  </channel>\n\n'

    for p in programmes_all:
        xml += f'  <programme start="{p["start"]} +0000" stop="{p["stop"]} +0000" channel="{p["channel"]}">\n'
        xml += f'    <title>{p["title"]}</title>\n'
        xml += f'  </programme>\n'

    xml += "</tv>"

    with open(OUTPUT_XML, "w", encoding="utf-8") as f:
        f.write(xml)
    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as f:
        f.write(xml)

    print(f"\n✅ Çıktı kaydedildi: {OUTPUT_XML} (ve {OUTPUT_GZ})")
    print(f"Toplam programme satırı: {len(programmes_all)}")

if __name__ == "__main__":
    run_all_channels_epg()
