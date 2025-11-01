import os
import time
import re
import gzip
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

# TV+ ana sayfa yayın akışı listesi
BASE_URL = "https://tvplus.com.tr"
LIST_URL = f"{BASE_URL}/canli-tv/yayin-akisi"

LI_XPATH_TEMPLATE = "/html/body/div[1]/div/div[1]/div/main/div/div[2]/ul/li[{}]"
RIGHT_BUTTON_XPATH = "/html/body/div[1]/div/div[1]/div/main/div/div[2]/button[2]"

HEADLESS = True
DELAY = 0.5
START_IDX = 7
TOTAL_TARGETS = 6

TR_MONTHS = {
    "Oca": "Jan", "Şub": "Feb", "Mar": "Mar", "Nis": "Apr",
    "May": "May", "Haz": "Jun", "Tem": "Jul", "Ağu": "Aug",
    "Eyl": "Sep", "Eki": "Oct", "Kas": "Nov", "Ara": "Dec"
}

EPG_MAP = {
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
    "HABERTÜRK": ["4K TR: HABERT RK HD", "HABERTURK HD", "HABERTURK RAW", "HABER TÜRK", "HABER T RK HD+ SD", "HABER TURK","HABER TURK HD","HABER TURK HEVC"],
    "A HABER": ["4K TR: A HABER HD", "A HABER", "A HABER HD", "A HABER HEVC", "A HABER RAW"],
    "TRT HABER": ["4K TR: TRT HABER HD", "TRT HABER", "TRT HABER HD", "TRT HABER HEVC", "TRT HABER RAW"],
    "24": ["24", "24 HABER HD+ SD", "24 RAW", "4K TR: 24 HD"],
    "BLOOMBERG HT": ["4K TR: BLOOMBERG HT HD", "BLOOMBERG HT", "BLOOMBERG HT HD", "BLOOMBERG HT HD+ SD", "BLOOMBERG"],
    "A PARA": ["A PARA", "A PARA RAW"],
    "HALK TV": ["4K TR: HALK TV", "HALK TV", "HALK TV HD", "HALK TV SD"],
    "TELE1": ["4K TR: TELE1", "TELE 1"],
    "HABER GLOBAL": ["4K TR: HABER GLOBAL HD", "HABER GLOBAL", "HABER GLOBAL HD", "HABER GLOBAL HD+ SD"],
    "EKOTÜRK": ["EKOTURK", "EKOTURK HD"],
    "ÜLKE TV": ["ÜLKE TV", "4K TR: LKE TV HD", "ULKE TV", "ULKE TV HD", "ULKETV HD"],
    "TGRT HABER": ["4K TR: TGRT HABER HD", "TGRT HABER", "TGRT HABER HD", "TGRT HABER HEVC", "TGRT HABER UHD"],
    "TVNET": ["4K TR: TVNET HD", "TVNET", "TVNET HD"],
    "AKİT TV": ["4K TR: AK T TV HD", "AKIT TV"],
    "BENGÜTÜRK": ["4K TR: BENG T RK", "BENGUTURK"],
    "ULUSAL KANAL": ["ULUSAL KANAL", "ULUSAL KANAL SD"],
    "KRT TV": ["4K TR: KRT TV", "KRT HD+ SD", "KRT TV HD"],
    "SÖZCÜ TV": ["S ZC SZC TV", "4K TR: SOZCU TV", "SOZCU SZC TV SD", "SÖZCÜ TV"],
    "TRT SPOR": ["4K TR: TRT SPOR HD", "TRT SPOR", "TRT SPOR FHD", "TRT SPOR HD", "TRT SPOR RAW"],
    "TRT SPOR YILDIZ": ["4K TR: TRT SPOR YILDIZ", "TRT SPOR YILDIZ", "TRT SPOR YILDIZ HD", "TRT SPOR YILDIZ HEVC", "TRT SPOR YILDIZ RAW"],
    "A SPOR": ["4K TR: A SPOR HD", "A SPOR", "A SPOR FHD", "A SPOR HD", "A SPOR HEVC", "A SPOR RAW"],
    "HT SPOR": ["HT SPOR HD", "HT SPOR"],
    "FB TV": ["4K TR: FB TV", "FB TV"],
    "tabii spor": ["TABII SPOR 1 4K", "TABII SPOR 1 720P", "TABII SPOR 1 UHD", "TABII SPOR HD", "TABII SPOR SD", "TABII SPOR", "TABII SPOR 1"],
    "S SPORT": ["4K TR: S SPORT", "S SPORT", "SARAN SPORT 1"],
    "S SPORT 2": ["SARAN SPORT 2", "S SPORT 2", "4K TR: S SPORT 2"],
    "EUROSPORT 1": ["EUROSPORT 1", "4K TR: EUROSPORT 1 HD", "EUROSPORT1 HD"],
    "EUROSPORT 2": ["4K TR: EUROSPORT 2 HD", "EUROSPORT2 HD", "EUROSPORT 2 [LIVE DURING EVENTS ONLY]"],
    "SPORTS TV": ["4K TR: SPORTS TV HD", "SPORTSTV HD", "SPORTS TV"],
    "TRT BELGESEL": ["4K TR: TRT BELGESEL HD", "TRT BELGESEL", "TRT BELGESEL HD+", "TRT BELGESEL HEVC", "TRT BELGESEL RAW"],
    "NATIONAL GEOGRAPHIC": ["4K TR: NATIONAL GEOGRAPHIC HD", "NATIONAL GEOGRAPHIC HD+", "NAT GEO"],
    "VIASAT HISTORY": ["4K TR: VIASAT HISTORY HD", "VIASAT HISTORY", "VIASAT HISTORY HD+", "VIASAT HISTORY HEVC"],
    "DISCOVERY CHANNEL": ["4K TR: DISCOVERY CHANNEL HD", "DISCOVERY CHANNEL", "DISCOVERY CHANNEL HD+"],
    "NATIONAL GEOGRAPHIC WILD": ["4K TR: NATIONAL GEOGRAPHIC WILD HD", "NAT GEO WILD", "NAT GEO WILD HD", "NAT GEO WILD HD+"],
    "LOVE NATURE": ["4K TR: LOVE NATURE HD", "LOVE NATURE", "LOVE NATURE HD", "LOVE NATURE HD+"],
    "ENGLISH CLUB TV": ["4K TR: ENGLISH CLUB TV"],
    "BABYTV": ["4K TR: BABYTV", "BABY TV", "BABY TV HD"],
    "DUCK TV": ["4K TR: DUCK TV HD"],
    "DISNEY JUNIOR": ["4K TR: DISNEY JUNIOR", "DISNEY JR", "DISNEY JR HD", "DISNEY JR HD+"],
    "Nick JR": ["NICK JR", "NICK JR HD HD", "NICK JR HD", "DISNEY JR HD+"],
    "NICKELODEON": ["NICKELODEON", "NICKELODEON HD"],
    "DA VINCI": ["4K TR: DA VINCI", "DA VINCI LEARNING"],
    "CARTOON NETWORK": ["4K TR: CARTOON NETWORK", "CARTOON NETWORK","CARTOON NETWORK HD"],
    "TRT ÇOCUK": ["TRT COCUK", "TRT COCUK RAW","TRT ÇOCUK"],
    "MİNİKA ÇOCUK": ["MİNİKA ÇOCUK"],
    "MİNİKA GO": ["MİNİKA GO"],
    "TRT DIYANET COCUK": ["TRT DIYANET COCUK", "TRT DİYANET ÇOCUK"],
    "A NEWS": ["A NEWS", "A NEWS HD", "A NEWS RAW"],
    "TRT World": ["TRT WORLD", "TRT WORLD HEVC", "TRT WORLD RAW"],
    "NUMBER1 TV": ["4K TR: NUMBER1 TV HD"],
    "POWER TV": ["4K TR: POWER TV HD"],
}

OUTPUT_FILE_XML = "epg/tum_kanallar.xml"
OUTPUT_FILE_GZ = "epg/tum_kanallar.gz"
os.makedirs(os.path.dirname(OUTPUT_FILE_XML), exist_ok=True)

def to_utc(dt):
    """Türkiye saati → UTC"""
    return (dt - timedelta(hours=3)).strftime("%Y%m%d%H%M%S")

def xpath_click_via_js(page, xpath):
    script = """
    (xp) => {
        const n = document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (!n) return false;
        try { n.click(); return true; } catch(e){}
        try { const ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window }); n.dispatchEvent(ev); return true; } catch(e){ return false; }
    }
    """
    return page.evaluate(script, xpath)

def element_exists(page, xpath):
    script = "(xp) => !!document.evaluate(xp, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    return page.evaluate(script, xpath)

def click_with_swipes(page, target_xpath, right_xpath=RIGHT_BUTTON_XPATH, max_swipes=5, delay=0.5):
    for _ in range(max_swipes):
        if element_exists(page, target_xpath):
            if xpath_click_via_js(page, target_xpath):
                time.sleep(delay)
                return True
        if element_exists(page, right_xpath):
            xpath_click_via_js(page, right_xpath)
            time.sleep(delay)
    return False

def parse_day_string(day_str):
    today = datetime.now()
    if day_str == "Dün":
        return today - timedelta(days=1)
    elif day_str == "Bugün":
        return today
    elif day_str == "Yarın":
        return today + timedelta(days=1)
    else:
        m = re.match(r"(\d{1,2}) (\w+)", day_str)
        if not m:
            return today
        day_num, month_tr = m.groups()
        month_en = TR_MONTHS.get(month_tr, month_tr)
        return datetime.strptime(f"{day_num} {month_en} {today.year}", "%d %b %Y")

def parse_time_with_day(time_str, day_dt):
    hour, minute = map(int, time_str.split(":"))
    return day_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

def get_channel_links():
    """TV+ ana sayfasından tüm kanal linklerini al"""
    r = requests.get(LIST_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.select("a.multirow-channel-carousel__item"):
        href = a.get("href")
        name = a.get_text(strip=True)
        if href and name:
            links.append((name, BASE_URL + href))
    print(f"📺 Toplam kanal sayısı: {len(links)}", flush=True)
    return links

def run_epg():
    all_programmes = []
    all_channels = {}

    channel_links = get_channel_links()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page()

        for channel_name, link in channel_links:
            print(f"{channel_name} işleniyor.", flush=True)  # Terminal çıktısı
            page.goto(link, wait_until="domcontentloaded")
            time.sleep(1)

            epg_ids = EPG_MAP.get(channel_name, [channel_name.lower().replace(" ", "_")])
            all_channels[channel_name] = epg_ids

            # Programları al
            for idx in range(START_IDX, START_IDX + TOTAL_TARGETS):
                li_xpath = LI_XPATH_TEMPLATE.format(idx)
                clicked = click_with_swipes(page, li_xpath, max_swipes=5, delay=DELAY)
                if not clicked:
                    continue

                try:
                    active_day_str = page.locator("li.epg-container__day-item--active span.epg-container__day-name").text_content().strip()
                    active_day_dt = parse_day_string(active_day_str)
                except:
                    active_day_dt = datetime.now()

                try:
                    titles = page.locator("h3.epg-card__title")
                    times  = page.locator("p.epg-card__time")
                    descriptions = page.locator("p.epg-card__description-desktop")
                    cnt = min(titles.count(), times.count(), descriptions.count())
                    for i in range(cnt):
                        title = titles.nth(i).text_content().strip()
                        description = descriptions.nth(i).text_content().strip() or "Açıklama yok"
                        time_text = times.nth(i).text_content().strip()
                        if " - " not in time_text:
                            continue
                        start_str, end_str = [x.strip() for x in time_text.split(" - ",1)]
                        start_dt = parse_time_with_day(start_str, active_day_dt)
                        end_dt = parse_time_with_day(end_str, active_day_dt)
                        if end_dt <= start_dt:
                            end_dt += timedelta(days=1)

                        all_programmes.append({
                            "title": title,
                            "description": description,
                            "start": to_utc(start_dt),
                            "stop": to_utc(end_dt),
                            "channel": channel_name
                        })
                except Exception as e:
                    print(f"Veri alınamadı {channel_name}: {e}", flush=True)

        browser.close()

    # XML oluşturma
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'

    # Kanalları ekle
    for channel_name, epg_ids in all_channels.items():
        for epg_id in epg_ids:
            xml += f'  <channel id="{epg_id}">\n'
            xml += f'    <display-name>{channel_name}</display-name>\n'
            xml += f'  </channel>\n'

    # Programları ekle
    for p in all_programmes:
        for epg_id in all_channels[p["channel"]]:
            xml += f'  <programme start="{p["start"]} +0000" stop="{p["stop"]} +0000" channel="{epg_id}">\n'
            xml += f'    <title lang="tr">{p["title"]}</title>\n'
            xml += f'    <desc lang="tr">{p["description"]}</desc>\n'
            xml += f'  </programme>\n'

    xml += "</tv>"

    # XML kaydet
    with open(OUTPUT_FILE_XML, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"🎉 XML olarak kaydedildi → {OUTPUT_FILE_XML}", flush=True)

    # Gzip kaydet
    with gzip.open(OUTPUT_FILE_GZ, "wt", encoding="utf-8") as f:
        f.write(xml)
    print(f"🎉 Gzip olarak kaydedildi → {OUTPUT_FILE_GZ}", flush=True)

if __name__ == "__main__":
    run_epg()
