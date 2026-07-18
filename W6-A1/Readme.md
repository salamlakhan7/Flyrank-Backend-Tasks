# W6-A1 — The Polite Scraper

A scraper that collects book listings from a practice site, extracts and
cleans the useful fields, and saves structured records, while behaving
politely toward the site it's reading from.

## Target site

[books.toscrape.com](https://books.toscrape.com/) — a sandbox site built
specifically for practicing scraping, with no real user data or business
impact.

## Pipeline

Built in stages, each one testable on its own before moving to the next:

1. **Fetch** — request a page with a proper `User-Agent` identifying the
   scraper honestly, plus a request timeout.
2. **Parse** — turn the raw HTML into a navigable structure with
   BeautifulSoup.
3. **Extract** — pull the raw fields (title, price, availability,
   rating, detail link) out of each book's HTML block.
4. **Clean** — convert raw text into proper types: price becomes a
   float (stripping the site's encoding artifact on the currency
   symbol), availability becomes a boolean, and the site's word-based
   star rating ("Three") becomes an integer (`3`).
5. **Structure** — save everything as indented JSON with full URLs,
   ready to be read by another program (or, next week, a RAG pipeline).

## Politeness decisions

- **robots.txt** — checked first, before any scraping code ran. This
  site returns a 404 for `/robots.txt`, meaning no crawling rules are
  published. That is not the same as "no rules apply" — the scraper
  falls back to conservative behavior anyway rather than treating a
  missing file as unlimited permission.
- **Honest identification** — every request sends a `User-Agent`
  naming the scraper and a contact email, rather than pretending to be
  a browser.
- **Rate limiting** — a 1-second pause between page requests, so the
  scraper never fires requests faster than a human clicking through
  pages would.
- **Scope restraint** — the site has 50 pages of listings; this
  scraper takes 3 (60 books) by default. That's enough to prove the
  pipeline works without pulling more than the exercise needs, which is
  the same restraint that matters on a real, non-practice site.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Output is written to `books.json` in the same folder.

## Sample output

```json
{
  "title": "A Light in the Attic",
  "price": 51.77,
  "in_stock": true,
  "rating": 3,
  "detail_link": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
}
```

## Screenshots

1. First successful page fetch, confirming the connection and site identity before any parsing began.

   ![Fetch confirmed](./Screenshots/1%20fetch_confirmed.JPG)

2. Raw HTML structure of a single book, inspected before deciding what to extract.

   ![Parse structure](./Screenshots/2%20parse_structure.JPG)

3. Raw fields pulled from all 20 books on the first page.

   ![Extract fields](./Screenshots/3%20extract_fields.JPG)

4. The same fields after cleaning: price as a float, availability as a boolean, rating as an int.

   ![Clean data](./Screenshots/4%20clean_data.JPG)

5. The final structured JSON output.

   ![Structured JSON](./Screenshots/5%20structured_json.JPG)

6. The full run: robots.txt check, 3 pages fetched with a delay between each, 60 books saved.

   ![Multi-page polite run](./Screenshots/6%20multi_page_polite.JPG)

## Notes

- The site's price field decodes with a mangled currency symbol
  (`Â£` instead of `£`) due to a character encoding mismatch on the
  source page. Rather than special-case that exact sequence, the
  cleaning step strips anything that isn't a digit or decimal point,
  which handles this and any similar encoding issue the same way.
- `PAGES_TO_SCRAPE` and `REQUEST_DELAY_SECONDS` are both defined as
  constants at the top of `main.py`, so scope and pacing can be
  adjusted in one place without touching the scraping logic itself.