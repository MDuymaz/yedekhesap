import requests
import zstandard as zstd
import io
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# --- 1. Stream listesi al ---
url_list = "https://api.istplay.xyz/stream-list-v2/?tv=tv"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "tr-TR,tr;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
    "Origin": "https://istplay.xyz",
    "Referer": "https://istplay.xyz/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/141.0.0.0 Safari/537.36",
}

response = requests.get(url_list, headers=headers)

# --- 2. Zstandard sıkıştırmasını çöz ---
if response.headers.get("content-encoding") == "zstd":
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(io.BytesIO(response.content)) as reader:
        data = reader.read()
else:
    data = response.content

# --- 3. JSON parse ---
parsed = json.loads(data)

# --- 4. m3u8 linkini alma fonksiyonu ---
def get_m3u8(stream_id):
    try:
        url = f"https://istplay.xyz/tv/?stream_id={stream_id}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.headers.get("content-encoding") == "zstd":
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(io.BytesIO(response.content)) as reader:
                data = reader.read()
        else:
            data = response.content

        html_text = data.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html_text, "html.parser")
        source = soup.find("source", {"type": "application/x-mpegURL"})
        if source and source.get("src"):
            return stream_id, source["src"]
    except Exception as e:
        print(f"⚠️ Hata stream_id={stream_id}: {e}")
    return stream_id, None

# --- 5. Tüm stream_id’leri topla ---
all_events = []
for sport_name, sport_category in parsed.get("sports", {}).items():
    if not isinstance(sport_category, dict):
        continue

    events = sport_category.get("events", {})
    if isinstance(events, dict):
        iterable = events.items()
    elif isinstance(events, list):
        iterable = [(str(i), e) for i, e in enumerate(events)]
    else:
        continue

    for event_id, event_data in iterable:
        stream_id = event_data.get("stream_id")
        if stream_id:
            all_events.append((sport_name, event_id, event_data))

# --- 6. ThreadPool ile eş zamanlı m3u8 çek ---
with ThreadPoolExecutor(max_workers=20) as executor:
    future_to_event = {executor.submit(get_m3u8, ev[2]['stream_id']): ev for ev in all_events}
    for future in as_completed(future_to_event):
        sport_name, event_id, event_data = future_to_event[future]
        try:
            sid, m3u8_url = future.result()
            event_data["m3u8_url"] = m3u8_url
        except Exception as e:
            print(f"⚠️ Future hata: {e}")

# --- 7. Spor isimleri ve logolar ---
sport_translation = {
    "HORSE_RACING": {"name": "AT YARIŞI", "logo": "https://medya-cdn.tjk.org/haberftp/2022/ayyd12082022.jpg"},
    "FOOTBALL"    : {"name": "FUTBOL", "logo": "https://thepfsa.co.uk/wp-content/uploads/2022/06/Playing-Football.jpg"},
    "BASKETBALL"  : {"name": "BASKETBOL", "logo": "https://minio.yalispor.com.tr/sneakscloud/blog/basketbol-hakkinda-bilmen-gereken-kurallar_5e53ae3fdd3fc.jpg"},
    "TENNIS"      : {"name": "TENİS", "logo": "https://calista.com.tr/media/c2sl3pug/calista-resort-hotel-blog-tenis-banner.jpg"},
    "ICE_HOCKEY"  : {"name": "BUZ HOKEYİ", "logo": "https://istanbulbbsk.org/uploads/medias/public-4b3b1703-c744-4631-8c42-8bab9be542bc.jpg"},
    "TABLE_TENNIS": {"name": "MASA TENİSİ", "logo": "https://tossfed.gov.tr/storage/2022/03/1399486-masa-tenisinde-3-lig-2-nisan-da-baslayacak-60642719b43dd.jpg"},
    "VOLLEYBALL"  : {"name": "VOLEYBOL", "logo": "https://www.sidasturkiye.com/images/aktiviteler/alt-aktiviteler_voleybol4.jpg"},
    "BADMINTON"   : {"name": "BADMİNTON", "logo": "https://sporium.net/wp-content/uploads/2017/12/badminton-malatya-il-sampiyonasi-9178452_8314_o.jpg"},
    "CRICKET"     : {"name": "KRİKET", "logo": "https://storage.acerapps.io/app-1358/kriket-nedir-nasil-oynanir-kriket-kurallari-nelerdir-sporsepeti-sportsfly-spor-kutuphanesi.jpg"},
    "HANDBALL"    : {"name": "HENTBOL", "logo": "https://image.fanatik.com.tr/i/fanatik/75/0x410/6282949745d2a051587ed23b.jpg"},
    "BASEBALL"    : {"name": "BEYZBOL", "logo": "https://seyler.ekstat.com/img/max/800/d/dqOJz5N8jLORqVaA-636783298725804088.jpg"},
    "SNOOKER"     : {"name": "İNGİLTERE BİLARDOSU", "logo": "https://cdn.shopify.com/s/files/1/0644/5685/1685/files/pool-table-graphic-1.jpg"},
    "BILLIARDS"   : {"name": "BİLARDO", "logo": "https://www.bilardo.org.tr/image/be2a4809f1c796e4453b45ccf0d9740c.jpg"},
    "BICYCLE"     : {"name": "BİSİKLET YARIŞI", "logo": "https://www.gazetekadikoy.com.tr/Uploads/gazetekadikoy.com.tr/202204281854011-img.jpg"},
    "BOXING"      : {"name": "BOX", "logo": "https://www.sportsmith.co/wp-content/uploads/2023/04/Thumbnail-scaled.jpg"},
}

# --- 8. M3U formatlı çıktı üret ---
output_lines = ['#EXTM3U', '']  # #EXTM3U'nin altına tek boş satır
group_title = "DÜNYA SPORLARI"

for sport_name, sport_category in parsed.get("sports", {}).items():
    events = sport_category.get("events", {})
    if isinstance(events, dict):
        iterable = events.items()
    elif isinstance(events, list):
        iterable = [(str(i), e) for i, e in enumerate(events)]
    else:
        continue

    for event_id, event_data in iterable:
        league = event_data.get("league", "Bilinmiyor")
        competitors = event_data.get("competitiors", {})
        home = competitors.get("home", "").strip()
        away = competitors.get("away", "").strip()
        m3u8_url = event_data.get("m3u8_url", "Link yok")

        # Spor adı ve logo
        sport_info = sport_translation.get(sport_name.upper(), {"name": sport_name.upper(), "logo": ""})
        display_sport = sport_info["name"]
        logo_url = sport_info.get("logo", "")

        # HORSE_RACING özel durumu: vs yok
        if sport_name.upper() == "HORSE_RACING":
            display_title = f"{home.upper()} ({league.upper()})"
        else:
            display_title = f"{home.upper()} vs {away.upper()} ({league.upper()})"

        # M3U format satırları
        line = f'#EXTINF:-1 tvg-name="{display_sport}" tvg-logo="{logo_url}" group-title="{group_title}",{display_title}\n{m3u8_url}'
        output_lines.append(line)

# --- 9. Dosyaya yaz ---
output_filename = "all_world_sports.m3u"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"💾 M3U çıktısı '{output_filename}' dosyasına kaydedildi.")
