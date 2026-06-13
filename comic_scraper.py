"""
Daily GoComics scraper — Nancy Classics.
Uses the GoComics RSS feed to find today's comic image,
then saves it as today.jpg for Tasker to download.
"""

import re
import requests
from datetime import date
from xml.etree import ElementTree as ET

COMIC_SLUG = "nancy-classics"
RSS_URL = f"https://www.gocomics.com/feeds/comics/{COMIC_SLUG}"


def get_comic_image_url():
    today = date.today()
    today_str = today.strftime("%Y/%m/%d")
    print(f"Fetching RSS feed: {RSS_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    resp = requests.get(RSS_URL, headers=headers, timeout=15)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    ns = {"media": "http://search.yahoo.com/mrss/"}

    for item in root.iter("item"):
        link = item.findtext("link") or ""
        if today_str in link:
            print(f"Found today's comic: {link}")

            # Try media:content first (clean image URL)
            media = item.find("media:content", ns)
            if media is not None:
                src = media.get("url")
                if src:
                    print(f"Image URL (media:content): {src}")
                    return src

            # Fall back to parsing <img> tag in description
            desc = item.findtext("description") or ""
            match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
            if match:
                src = match.group(1)
                print(f"Image URL (description img): {src}")
                return src

            raise RuntimeError("Found today's item in RSS but could not extract image URL.")

    # If today's entry isn't in the feed yet, use the most recent entry
    print("Today's entry not found in feed — using most recent entry.")
    for item in root.iter("item"):
        media = item.find("media:content", ns)
        if media is not None:
            src = media.get("url")
            if src:
                print(f"Image URL (latest entry): {src}")
                return src
        desc = item.findtext("description") or ""
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
        if match:
            return match.group(1)

    raise RuntimeError("Could not find any comic image in RSS feed.")


def download_image(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.content


def main():
    image_url = get_comic_image_url()
    image_bytes = download_image(image_url)

    output_path = "today.jpg"
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Saved {len(image_bytes):,} bytes to {output_path}")


if __name__ == "__main__":
    main()
