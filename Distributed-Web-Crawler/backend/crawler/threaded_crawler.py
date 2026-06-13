import os
import sys
import requests
from bs4 import BeautifulSoup
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import threading
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# Add parent directory of crawler (backend) to path to import database and url_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import save_page
from crawler.url_manager import normalize_url

# CONFIGURATION
SEED_URLS = [
    "https://books.toscrape.com",
    "https://quotes.toscrape.com",
    "https://scrapethissite.com/pages/",
    "https://news.ycombinator.com/",
    "https://en.wikipedia.org/wiki/Main_Page",
    "https://httpbin.org/"
]

MAX_PAGES = 250
MAX_THREADS = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# SHARED STRUCTURES
queue = deque()
visited = set()
queued = set()
lock = threading.Lock()
active_workers = 0  # Track active crawling threads

# Add initial seed URLs
for url in SEED_URLS:
    queue.append(url)
    queued.add(url)

# Extract allowed domains
allowed_domains = {urlparse(url).netloc for url in SEED_URLS}

# CRAWLER FUNCTION
def crawl():
    global active_workers

    while True:
        # GET URL SAFELY
        with lock:
            # Stop if enough pages crawled
            if len(visited) >= MAX_PAGES:
                return

            # Wait if queue is temporarily empty but other threads are still active
            while not queue:
                if active_workers == 0:
                    # No active threads and queue is empty -> crawl completed
                    return
                
                # Release lock, sleep to let other threads add URLs, then re-acquire lock
                lock.release()
                time.sleep(0.1)
                lock.acquire()

                # Recheck max page limit after sleep
                if len(visited) >= MAX_PAGES:
                    return

            url = queue.popleft()

            # Skip duplicates
            if url in visited:
                continue

            visited.add(url)
            active_workers += 1

        print(f"\n[{threading.current_thread().name}] Crawling: {url}")

        try:
            # DOWNLOAD PAGE
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=5,
                verify=False
            )

            print(f"[{threading.current_thread().name}] Status Code: {response.status_code}")

            if response.status_code != 200:
                continue

            # PARSE HTML
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.text.strip() if soup.title else "No Title"
            content = soup.get_text()

            # SAVE PAGE using shared database helper
            if save_page(url, title, content):
                print(f"Saved: {title}")
            else:
                print(f"Skipped (already exists): {title}")

            # EXTRACT LINKS
            links_found = 0

            for link in soup.find_all("a"):
                href = link.get("href")
                normalized_url = normalize_url(url, href)

                if not normalized_url:
                    continue

                # Restrict to allowed domains
                if urlparse(normalized_url).netloc not in allowed_domains:
                    continue

                with lock:
                    if normalized_url not in visited and normalized_url not in queued:
                        queue.append(normalized_url)
                        queued.add(normalized_url)
                        links_found += 1

            print(f"[{threading.current_thread().name}] Links Added: {links_found}")

            # Crawl delay
            time.sleep(1)

        except Exception as e:
            print(f"[{threading.current_thread().name}] Failed: {e}")

        finally:
            with lock:
                active_workers -= 1

# START THREADS
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(crawl) for _ in range(MAX_THREADS)]
    for future in futures:
        future.result()

# FINISHED
print("\nCrawling Finished")
print(f"Total Pages Crawled: {len(visited)}")