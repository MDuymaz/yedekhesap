from yt_dlp import YoutubeDL

url = "https://www.youtube.com/watch?v=pfQeMtSBv_Y"

ydl_opts = {
    'quiet': False,
    'skip_download': True,
    'cookies_from_browser': ('chrome',),  # Chrome tarayıcı çerezlerini kullan
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    for f in info.get('formats', []):
        if f.get('protocol') in ['m3u8_native', 'm3u8_dash']:
            print(f"Format ID: {f['format_id']}")
            print("URL:", f['url'])
