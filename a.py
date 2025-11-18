from yt_dlp import YoutubeDL

url = "https://www.youtube.com/watch?v=pfQeMtSBv_Y"

ydl_opts = {
    'quiet': True,
    'force_generic_extractor': False,
    'skip_download': True,  # Video indirmeye gerek yok
    'simulate': True
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    
    print("Video Başlığı:", info.get('title'))
    print("M3U8 / Stream URL'leri:\n")
    
    # formatları listele
    for f in info.get('formats', []):
        if f.get('protocol') in ['m3u8_native', 'm3u8_dash']:
            print(f"Format ID: {f['format_id']}")
            print("URL:", f['url'])
            print("Resolution:", f.get('height'), "x", f.get('width'))
            print("-"*40)
