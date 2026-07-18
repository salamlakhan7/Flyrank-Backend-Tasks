import requests

BASE_URL = "https://books.toscrape.com/"

# Identifying ourselves honestly is part of being a polite scraper -
# a real site owner should be able to see who's hitting their server and why.
HEADERS = {
    "User-Agent": "FlyRankInternPracticeBot/1.0 (Educational scraping exercise; contact: salamlakhan7@gmail.com)"
}


def fetch_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    html = fetch_page(BASE_URL)
    print(f"Fetched {len(html)} characters")
    print(html[:500])