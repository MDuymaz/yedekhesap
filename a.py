import requests
import re
import json

# Hedef URL
url = "https://nl.pornhub.com/view_video.php?viewkey=67b090c219858"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": url
}

# Sayfayı çek
response = requests.get(url, headers=headers)
html = response.text

# <script> içindeki flashvars_464592005 kısmını regex ile bul
match = re.search(r'var flashvars_\d+\s*=\s*({.*?});\s*\n', html, re.DOTALL)
if match:
    flashvars_str = match.group(1)
    
    # JSON formatına uygun hale getirmek için bazı düzeltmeler
    flashvars_str = flashvars_str.replace('false', 'false').replace('true', 'true').replace('null', 'None')
    
    # Python dict'e çevir
    try:
        flashvars = eval(flashvars_str)
        media_defs = flashvars.get('mediaDefinitions', [])
        
        print("Bulunan m3u8 linkleri:")
        for media in media_defs:
            video_url = media.get('videoUrl', '')
            if '.m3u8' in video_url:
                print(video_url)
    except Exception as e:
        print("Flashvars parsing hatası:", e)
else:
    print("flashvars bulunamadı.")
