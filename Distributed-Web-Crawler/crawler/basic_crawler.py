# Single page crawler
# import requests
# from bs4 import BeautifulSoup

# # Website to crawl
# url = "https://example.com"

# try:
#     # Send HTTP GET request
#     response = requests.get(url)

#     # Print status code
#     print("Status Code:", response.status_code)

#     # Parse HTML content
#     soup = BeautifulSoup(response.text, "html.parser")

#     # Print page title
#     print("\nPage Title:")
#     print(soup.title.text)

#     # Extract all links
#     print("\nLinks Found:")

#     for link in soup.find_all("a"):
#         href = link.get("href")

#         if href:
#             print(href)

# except Exception as e:
#     print("Error:", e)


# Multi page crawler
import requests
from bs4 import BeautifulSoup
from collections import deque
import sqlite3
from url_manager import normalize_url
from urllib.parse import urlparse
import time

conn = sqlite3.connect("../database/crawler.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    content TEXT
)
""")

conn.commit()
# Queue for URLs
queue = deque()

# Set for visited URLs
visited = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Starting URL
start_url = "https://example.com"

domain = urlparse(start_url).netloc

queue.append(start_url)

queued = set()

queued.add(start_url)

# Crawl limit
MAX_PAGES = 10

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

        # Print title
        title = soup.title.text if soup.title else "No Title"

        content = soup.get_text()

        cursor.execute("""
        INSERT OR IGNORE INTO pages(url, title, content)
        VALUES (?, ?, ?)
        """, (url, title, content))

        conn.commit()

        print("Saved to database")


        # Extract links
        for link in soup.find_all("a"):

            href = link.get("href")

            # Check valid link
            normalized_url = normalize_url(url, href)

            if not normalized_url:
                continue

            # Restrict to same domain
            if urlparse(normalized_url).netloc != domain:
                continue

            # Avoid duplicates
            if normalized_url not in queued:
                queue.append(normalized_url)
                queued.add(normalized_url)

        count += 1

    except Exception as e:
        print("Failed:", e)
    
    time.sleep(1)
    conn.close()

print("\nCrawling Finished")