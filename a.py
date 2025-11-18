import requests
import re

url = "https://www.youtube.com/watch?v=pfQeMtSBv_Y"

headers = {
    "referer": "https://www.youtube.com/@sifirtv/featured",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-arch": "x86",
    "sec-ch-ua-bitness": "64",
    "sec-ch-ua-form-factors": '"Desktop"',
    "sec-ch-ua-full-version": "141.0.7390.77",
    "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.77", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.77"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"10.0.0"',
    "sec-ch-ua-wow64": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Sayfa içinde m3u8 URL'lerini ara
    m3u8_links = re.findall(r'https?://[^\s"\']+\.m3u8', response.text)
    if m3u8_links:
        print("Bulunan m3u8 linkleri:\n")
        for link in m3u8_links:
            print(link)
    else:
        print("Herhangi bir .m3u8 linki bulunamadı.")
else:
    print(f"İstek başarısız oldu. Durum kodu: {response.status_code}")
