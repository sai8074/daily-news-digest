#!/usr/bin/env python3
"""
screenshot.py

Uses Playwright (Chromium) to take a full-page screenshot of the
rendered docs/index.html and save it as digest.png in the repo root.

Requires:
  pip install playwright
  playwright install --with-deps chromium

Run:
  python scripts/screenshot.py
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = REPO_ROOT / "docs" / "index.html"
OUTPUT_PATH = REPO_ROOT / "digest.png"

VIEWPORT_WIDTH = 1000


def main():
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"{HTML_PATH} not found. Run scripts/generate_html.py first."
        )

    file_url = HTML_PATH.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": VIEWPORT_WIDTH, "height": 800})
        page.goto(file_url, wait_until="networkidle")
        # Give web fonts a brief moment to finish loading before capture.
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUTPUT_PATH), full_page=True)
        browser.close()

    print(f"Saved screenshot to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
