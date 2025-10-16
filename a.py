import requests

url = "https://hdfilmsite.net/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://hdfilmsite.net/",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding  # Türkçe karakterler için

print(response.text)
