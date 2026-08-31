#!/usr/bin/env python3
"""
generate_html.py

Reads data/news.json and renders it into a styled docs/index.html
using the Jinja2 template at templates/digest.html.

docs/index.html is the file GitHub Pages serves when Pages is
configured to build from the /docs folder on the main branch.

Run:
  python scripts/generate_html.py
"""

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader

DATA_PATH = os.path.join("data", "news.json")
TEMPLATE_DIR = "templates"
TEMPLATE_NAME = "digest.html"
OUTPUT_PATH = os.path.join("docs", "index.html")

IST = ZoneInfo("Asia/Kolkata")

# Category display config: icon + accent color + whether it should use the
# Telugu font stack for its headline text.
CATEGORY_META = {
    "Tech": {"icon": "💻", "color": "#4f9dff", "is_telugu": False},
    "Sports": {"icon": "🏆", "color": "#22c55e", "is_telugu": False},
    "Finance": {"icon": "💰", "color": "#f5a623", "is_telugu": False},
    "World Politics": {"icon": "🌍", "color": "#ef4444", "is_telugu": False},
    "India": {"icon": "🇮🇳", "color": "#ff8c42", "is_telugu": False},
    "Andhra Pradesh (English)": {"icon": "📍", "color": "#a855f7", "is_telugu": False},
    "Andhra Pradesh (Telugu)": {"icon": "📍", "color": "#ec4899", "is_telugu": True},
}


def load_news():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run scripts/fetch_news.py first."
        )
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_category_list(news_data):
    categories = []
    for name, headlines in news_data.get("categories", {}).items():
        meta = CATEGORY_META.get(name, {"icon": "📰", "color": "#4f9dff", "is_telugu": False})
        categories.append(
            {
                "name": name,
                "headlines": headlines,
                "icon": meta["icon"],
                "color": meta["color"],
                "is_telugu": meta["is_telugu"],
            }
        )
    return categories


def main():
    news_data = load_news()
    categories = build_category_list(news_data)

    now_ist = datetime.now(IST)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template(TEMPLATE_NAME)

    html = template.render(
        categories=categories,
        generated_date=now_ist.strftime("%d %B %Y"),
        generated_time=now_ist.strftime("%I:%M %p"),
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Rendered digest to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
