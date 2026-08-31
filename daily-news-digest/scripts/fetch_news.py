#!/usr/bin/env python3
"""
fetch_news.py

Pulls the top 5 headlines for each configured category and writes the
combined result to data/news.json.

Sources:
  - Most categories: Google News RSS search feeds
      https://news.google.com/rss/search?q=<query>&hl=<lang>&gl=IN&ceid=IN:<lang>
  - Tech also blends in TechCrunch's own feed (techcrunch.com/feed/)
  - Sports also blends in BBC Sport's feed (feeds.bbci.co.uk/sport/rss.xml)
  - Andhra Pradesh (Telugu) uses hl=te&gl=IN&ceid=IN:te

Run:
  python scripts/fetch_news.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from urllib.parse import quote

import feedparser

# Number of headlines to keep per category
HEADLINES_PER_CATEGORY = 5

# Output path (relative to repo root)
OUTPUT_PATH = os.path.join("data", "news.json")


def google_news_url(query: str, hl: str = "en", gl: str = "IN", ceid: str = "IN:en") -> str:
    """Build a Google News RSS search URL for a given query/locale."""
    encoded_query = quote(query)
    return (
        f"https://news.google.com/rss/search?q={encoded_query}"
        f"&hl={hl}&gl={gl}&ceid={ceid}"
    )


# Each category maps to a list of RSS feed URLs. Headlines are pulled from
# each feed in order and merged (deduplicated by title) until we hit the
# per-category cap.
CATEGORIES = {
    "Tech": [
        google_news_url("technology", hl="en", gl="IN", ceid="IN:en"),
        "https://techcrunch.com/feed/",
    ],
    "Sports": [
        google_news_url("sports", hl="en", gl="IN", ceid="IN:en"),
        "https://feeds.bbci.co.uk/sport/rss.xml",
    ],
    "Finance": [
        google_news_url("finance OR markets OR economy", hl="en", gl="IN", ceid="IN:en"),
    ],
    "World Politics": [
        google_news_url("world politics", hl="en", gl="IN", ceid="IN:en"),
    ],
    "India": [
        google_news_url("India", hl="en", gl="IN", ceid="IN:en"),
    ],
    "Andhra Pradesh (English)": [
        google_news_url("Andhra Pradesh", hl="en", gl="IN", ceid="IN:en"),
    ],
    "Andhra Pradesh (Telugu)": [
        google_news_url("ఆంధ్రప్రదేశ్", hl="te", gl="IN", ceid="IN:te"),
    ],
}


def fetch_category(feed_urls, limit=HEADLINES_PER_CATEGORY):
    """Fetch and merge headlines from one or more feed URLs for a category."""
    items = []
    seen_titles = set()

    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
        except Exception as exc:  # noqa: BLE001 - keep the workflow resilient
            print(f"  ! Failed to parse feed {url}: {exc}", file=sys.stderr)
            continue

        if getattr(parsed, "bozo", False) and not parsed.entries:
            print(f"  ! Feed returned no entries: {url}", file=sys.stderr)

        for entry in parsed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()

            if not title or not link:
                continue
            if title in seen_titles:
                continue

            source = ""
            if hasattr(entry, "source") and getattr(entry.source, "title", None):
                source = entry.source.title
            elif hasattr(entry, "publisher"):
                source = entry.publisher

            published = getattr(entry, "published", "") or getattr(entry, "updated", "")

            items.append(
                {
                    "title": title,
                    "link": link,
                    "source": source,
                    "published": published,
                }
            )
            seen_titles.add(title)

            if len(items) >= limit:
                return items

        if len(items) >= limit:
            break

    return items[:limit]


def main():
    print("Fetching daily news digest...")
    digest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "categories": {},
    }

    for category, feed_urls in CATEGORIES.items():
        print(f"  Fetching: {category}")
        headlines = fetch_category(feed_urls)
        print(f"    -> {len(headlines)} headlines")
        digest["categories"][category] = headlines

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)

    print(f"Saved digest to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
