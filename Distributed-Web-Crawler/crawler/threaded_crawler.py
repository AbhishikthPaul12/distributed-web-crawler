import requests
from bs4 import BeautifulSoup
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from url_manager import normalize_url
import sqlite3
import threading
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# CONFIGURATION
START_URL = "https://books.toscrape.com"

MAX_PAGES = 10

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

# Add initial URL
queue.append(START_URL)

queued.add(START_URL)

# Extract allowed domain
domain = urlparse(START_URL).netloc

# CRAWLER FUNCTION

def crawl():

    # Separate DB connection per thread
    conn = sqlite3.connect(
        "../database/crawler.db",
        check_same_thread=False
    )

    cursor = conn.cursor()

    while True:

        # GET URL SAFELY

        with lock:

            # Stop if enough pages crawled
            if len(visited) >= MAX_PAGES:
                return

            # Stop if queue empty
            if not queue:
                return

            url = queue.popleft()

            # Skip duplicates
            if url in visited:
                continue

            visited.add(url)

        print(f"\n[{threading.current_thread().name}] Crawling: {url}")

        try:

            # DOWNLOAD PAGE

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=5,
                verify=False
            )

            print("Status Code:", response.status_code)

            if response.status_code != 200:
                continue

            # PARSE HTML

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            title = (
                soup.title.text.strip()
                if soup.title
                else "No Title"
            )

            content = soup.get_text()

            # CREATE TABLE

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT
            )
            """)

            # SAVE PAGE

            cursor.execute("""
            INSERT OR IGNORE INTO pages(url, title, content)
            VALUES (?, ?, ?)
            """, (url, title, content))

            conn.commit()

            print(f"Saved: {title}")

            # EXTRACT LINKS

            links_found = 0

            for link in soup.find_all("a"):

                href = link.get("href")

                normalized_url = normalize_url(
                    url,
                    href
                )

                if not normalized_url:
                    continue

                # Restrict to same domain
                if urlparse(normalized_url).netloc != domain:
                    continue

                with lock:

                    if (
                        normalized_url not in visited
                        and normalized_url not in queued
                    ):

                        queue.append(normalized_url)

                        queued.add(normalized_url)

                        links_found += 1

                        print("Added to queue:", normalized_url)

            print(f"Links Added: {links_found}")

            # Crawl delay
            time.sleep(1)

        except Exception as e:

            print("Failed:", e)

    conn.close()

# START THREADS

with ThreadPoolExecutor(
    max_workers=MAX_THREADS
) as executor:

    futures = []

    for _ in range(MAX_THREADS):

        futures.append(
            executor.submit(crawl)
        )

    for future in futures:
        future.result()

# FINISHED
print("\nCrawling Finished")
print(f"Total Pages Crawled: {len(visited)}")