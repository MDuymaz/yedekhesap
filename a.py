from yt_dlp import YoutubeDL

# YouTube video URL
url = "https://www.youtube.com/watch?v=pfQeMtSBv_Y"

# yt-dlp ayarları
ydl_opts = {
    'quiet': False,                  # Daha fazla çıktı almak için False
    'skip_download': True,           # Video indirmeye gerek yok
    'cookies_from_browser': ('chrome',),  # Chrome tarayıcı çerezlerini kullan
    'force_generic_extractor': False,
}

with YoutubeDL(ydl_opts) as ydl:
    try:
        info = ydl.extract_info(url, download=False)
        print(f"Video Başlığı: {info.get('title')}\n")
        
        # .m3u8 / HLS linklerini listele
        hls_found = False
        for f in info.get('formats', []):
            if f.get('protocol') in ['m3u8_native', 'm3u8_dash']:
                hls_found = True
                print(f"Format ID: {f['format_id']}")
                print(f"Resolution: {f.get('height')}x{f.get('width')}")
                print(f"URL: {f['url']}")
                print("-" * 50)
        
        if not hls_found:
            print("Herhangi bir .m3u8 (HLS) linki bulunamadı.")

    except Exception as e:
        print("Hata oluştu:", e)
