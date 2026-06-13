"""
Daily GoComics scraper — Nancy Classics.
Uses comicsrss.com (a third-party aggregator) to get today's strip,
bypassing GoComics' bot blocking.
Saves the image as today.jpg for Tasker to download.
"""

import re
import requests
from datetime import date
from xml.etree import ElementTree as ET

# comicsrss.com is a public third-party aggregator - not blocked like gocomics.com
RSS_URL = "https://comicsrss.com/rss/nancy-classics.rss"


def get_comic_image_url():
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    print(f"Fetching RSS feed from comicsrss.com for {today_str}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    resp = requests.get(RSS_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    print(f"RSS feed fetched ({len(resp.content):,} bytes)")

    root = ET.fromstring(resp.content)

    for item in root.iter("item"):
        # comicsrss.com puts the date in the title or pubDate
        title = item.findtext("title") or ""
        pub_date = item.findtext("pubDate") or ""
        desc = item.findtext("description") or ""

        print(f"  Item: {title[:60]} | {pub_date[:30]}")

        # Look for today's date in the title or pubDate
        if today_str in title or today.strftime("%b %d, %Y") in title or today_str in pub_date:
            print(f"Found today's comic: {title}")
            # Extract image URL from description HTML
            match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
            if match:
                src = match.group(1)
                print(f"Image URL: {src}")
                return src
            raise RuntimeError("Found today's item but could not extract image URL from description.")

    # Fall back to most recent item if today's not found yet
    print("Today's entry not found — using most recent entry.")
    for item in root.iter("item"):
        desc = item.findtext("description") or ""
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
        if match:
            src = match.group(1)
            print(f"Image URL (latest): {src}")
            return src

    raise RuntimeError("Could not find any comic image in the RSS feed.")


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
