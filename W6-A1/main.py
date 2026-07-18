import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "FlyRankInternPracticeBot/1.0 (Educational scraping exercise; contact: salamlakhan7@gmail.com)"
}

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

OUTPUT_FILE = "books.json"


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
        "detail_link": BASE_URL + raw_book["detail_link"],
    }


def save_books(books: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    html = fetch_page(BASE_URL)
    books = parse_book_listing(html)
    print(f"Found {len(books)} books on this page")

    extracted = [extract_book(book) for book in books]
    cleaned = [clean_book(book) for book in extracted]

    save_books(cleaned, OUTPUT_FILE)
    print(f"Saved {len(cleaned)} books to {OUTPUT_FILE}")