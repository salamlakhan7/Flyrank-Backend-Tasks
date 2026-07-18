import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "FlyRankInternPracticeBot/1.0 (Educational scraping exercise; contact: salamlakhan7@gmail.com)"
}

# The site encodes star ratings as a CSS class name instead of a number.
# We map the word to an int so our structured data is actually usable.
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


def parse_book_listing(html: str):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("article", class_="product_pod")


def extract_book(book_element) -> dict:
    title = book_element.h3.a["title"]

    price_raw = book_element.find("p", class_="price_color").text

    availability = book_element.find("p", class_="instock availability").text.strip()

    # The rating classes look like "star-rating Three" - the word is the second class.
    rating_classes = book_element.find("p", class_="star-rating")["class"]
    rating_word = rating_classes[1] if len(rating_classes) > 1 else None

    detail_link = book_element.h3.a["href"]

    return {
        "title": title,
        "price_raw": price_raw,
        "availability_raw": availability,
        "rating_word": rating_word,
        "detail_link": detail_link,
    }


if __name__ == "__main__":
    html = fetch_page(BASE_URL)
    books = parse_book_listing(html)
    print(f"Found {len(books)} books on this page\n")

    extracted = [extract_book(book) for book in books]

    for item in extracted[:3]:
        print(item)