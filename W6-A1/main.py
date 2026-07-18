import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "FlyRankInternPracticeBot/1.0 (Educational scraping exercise; contact: salamlakhan7@gmail.com)"
}


def fetch_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


def parse_book_listing(html: str):
    soup = BeautifulSoup(html, "html.parser")
    books = soup.find_all("article", class_="product_pod")
    return books


if __name__ == "__main__":
    html = fetch_page(BASE_URL)
    books = parse_book_listing(html)
    print(f"Found {len(books)} books on this page")

    first_book = books[0]
    print(first_book.prettify())