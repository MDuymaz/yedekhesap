import requests
from bs4 import BeautifulSoup

base_url = "https://hdfilmsite.net/filmizle/yabanci-filmler-izle-hd"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://hdfilmsite.net/",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

# Ana sayfa
response = requests.get(base_url, headers=headers)
response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, "html.parser")

movie_boxes = soup.find_all("div", class_="movie_box")

for movie in movie_boxes:
    a_tag = movie.find("a", class_="image")
    if not a_tag:
        continue

    # Tip filtresi: Dizi atla
    type_tag = a_tag.find("span", class_="box type")
    type_ = type_tag.get_text(strip=True) if type_tag else "Bilinmiyor"
    if type_ == "Dizi":
        continue

    # Başlık ve film linki
    title = a_tag.get("title", "Bilinmiyor")
    film_link = a_tag.get("href", "Bilinmiyor")

    # Yıl
    year_tag = a_tag.find("span", class_="box year")
    year = year_tag.get_text(strip=True) if year_tag else "Bilinmiyor"

    # IMDb (sayfa içinden)
    film_response = requests.get(film_link, headers=headers)
    film_response.encoding = film_response.apparent_encoding
    film_soup = BeautifulSoup(film_response.text, "html.parser")
    imdb_tag = film_soup.find("a", class_="imdb")
    imdb_link = imdb_tag.get("href") if imdb_tag else "Bilinmiyor"

    print(f"Başlık: {title}")
    print(f"Tip: {type_}")
    print(f"Yıl: {year}")
    print(f"Link: {film_link}")
    print(f"IMDb Link: {imdb_link}")
    print("-" * 50)
