"""
Daily GoComics scraper — Nancy Classics.
Fetches today's strip and saves it as today.jpg in the repo.
GitHub Actions commits and pushes it so Tasker can download it at a stable URL.
"""

import os
import requests
from datetime import date
from bs4 import BeautifulSoup

COMIC_SLUG = "nancy-classics"
GOCOMICS_URL = f"https://www.gocomics.com/{COMIC_SLUG}"


def get_comic_image_url():
    today = date.today()
    url = f"{GOCOMICS_URL}/{today.strftime('%Y/%m/%d')}"
    print(f"Fetching comic from: {url}")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; ComicBot/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    img = soup.select_one("picture.item-comic-image img") or \
          soup.select_one("img.img-fluid")

    if not img:
        raise RuntimeError("Could not find comic image — GoComics may have changed their layout.")

    src = img.get("src") or img.get("data-src")
    if not src:
        raise RuntimeError("Image tag found but no src attribute.")

    print(f"Comic image URL: {src}")
    return src


def download_image(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ComicBot/1.0)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.content


def main():
    image_url = get_comic_image_url()
    image_bytes = download_image(image_url)

    # Save as today.jpg — Tasker always fetches this same filename
    output_path = "today.jpg"
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Saved {len(image_bytes):,} bytes to {output_path}")


if __name__ == "__main__":
    main()
