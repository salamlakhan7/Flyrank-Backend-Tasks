import json
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
PAGE_URL_TEMPLATE = "https://books.toscrape.com/catalogue/page-{}.html"

# How many pages to scrape. The full site has 50; we take a handful to
# prove the pipeline works without hammering a server unnecessarily -
# the same restraint you'd want on a real, non-practice site.
PAGES_TO_SCRAPE = 3

# Being a polite scraper means waiting between requests instead of firing
# them as fast as the network allows. One second is a common, safe default.
REQUEST_DELAY_SECONDS = 1

HEADERS = {
    "User-Agent": "FlyRankInternPracticeBot/1.0 (Educational scraping exercise; contact: salamlakhan7@gmail.com)"
}

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

OUTPUT_FILE = "books.json"


def check_robots_txt() -> None:
    """Look for robots.txt and report what we find. This site returns a 404
    for it, meaning there are no published crawling rules - but we still
    check, because assuming permission without looking is exactly the
    habit a polite scraper should not have."""
    robots_url = BASE_URL + "robots.txt"
    response = requests.get(robots_url, headers=HEADERS, timeout=10)
    if response.status_code == 404:
        print(f"No robots.txt found at {robots_url} (404). "
              f"Proceeding with conservative rate limiting as a fallback.")
    else:
        print(f"robots.txt found:\n{response.text}")


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


def clean_price(price_raw: str) -> float:
    digits_only = re.sub(r"[^\d.]", "", price_raw)
    return float(digits_only)


def clean_availability(availability_raw: str) -> bool:
    return "in stock" in availability_raw.lower()


def clean_rating(rating_word: str) -> int:
    return RATING_WORDS.get(rating_word, 0)


def clean_book(raw_book: dict) -> dict:
    return {
        "title": raw_book["title"],
        "price": clean_price(raw_book["price_raw"]),
        "in_stock": clean_availability(raw_book["availability_raw"]),
        "rating": clean_rating(raw_book["rating_word"]),
        "detail_link": "https://books.toscrape.com/catalogue/" + raw_book["detail_link"].removeprefix("catalogue/"),
    }


def save_books(books: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)


def scrape_pages(num_pages: int) -> list[dict]:
    all_books = []

    for page_num in range(1, num_pages + 1):
        url = BASE_URL if page_num == 1 else PAGE_URL_TEMPLATE.format(page_num)
        print(f"Fetching page {page_num}: {url}")

        html = fetch_page(url)
        books_on_page = parse_book_listing(html)
        extracted = [extract_book(book) for book in books_on_page]
        cleaned = [clean_book(book) for book in extracted]
        all_books.extend(cleaned)

        print(f"  -> {len(cleaned)} books extracted")

        if page_num < num_pages:
            time.sleep(REQUEST_DELAY_SECONDS)

    return all_books


if __name__ == "__main__":
    check_robots_txt()
    print()

    all_books = scrape_pages(PAGES_TO_SCRAPE)
    print(f"\nTotal books scraped: {len(all_books)}")

    save_books(all_books, OUTPUT_FILE)
    print(f"Saved to {OUTPUT_FILE}")