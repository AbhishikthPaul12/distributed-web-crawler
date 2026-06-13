import os
import sys
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlparse
import time

# Add parent directory of crawler (backend) to path to import database and url_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import save_page
from crawler.url_manager import normalize_url

# Queue for URLs
queue = deque()

# Set for visited URLs
visited = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Seed URLs
seed_urls = [
    "https://books.toscrape.com",
    "https://quotes.toscrape.com",
    "https://scrapethissite.com/pages/",
    "https://news.ycombinator.com/",
    "https://en.wikipedia.org/wiki/Main_Page",
    "https://httpbin.org/"
]

allowed_domains = {urlparse(url).netloc for url in seed_urls}

queued = set()

for url in seed_urls:
    queue.append(url)
    queued.add(url)

# Crawl limit
MAX_PAGES = 250

count = 0

while queue and count < MAX_PAGES:
    # Get next URL
    url = queue.popleft()

    # Skip already visited URLs
    if url in visited:
        continue

    # Mark visited
    visited.add(url)

    print("\nCrawling:", url)

    try:
        # Download page
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            continue

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Get page title
        title = soup.title.text.strip() if soup.title else "No Title"

        # Get body content text
        content = soup.get_text()

        # Save page using database helper
        if save_page(url, title, content):
            print("Saved to database")
        else:
            print("Already exists in database / skipped")

        # Extract links
        for link in soup.find_all("a"):
            href = link.get("href")

            # Check valid link
            normalized_url = normalize_url(url, href)

            if not normalized_url:
                continue

            # Restrict to allowed domains
            if urlparse(normalized_url).netloc not in allowed_domains:
                continue

            # Avoid duplicates
            if normalized_url not in queued:
                queue.append(normalized_url)
                queued.add(normalized_url)

        count += 1

    except Exception as e:
        print("Failed:", e)
    
    time.sleep(1)

print("\nCrawling Finished")