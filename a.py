import requests

url = "https://tvplus.com.tr/canli-tv/yayin-akisi/atv-hd--124"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print(response.text)
