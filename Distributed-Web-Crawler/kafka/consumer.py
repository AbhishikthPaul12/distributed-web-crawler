from confluent_kafka import Consumer, Producer
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
import requests
import sqlite3
import json
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# ==============================
# KAFKA CONFIG
# ==============================

consumer_config = {
    'bootstrap.servers': '127.0.0.1:9092',

    'group.id': 'crawler-group',

    'auto.offset.reset': 'earliest'
}

producer_config = {
    'bootstrap.servers': '127.0.0.1:9092'
}

# ==============================
# CREATE CONSUMER + PRODUCER
# ==============================

consumer = Consumer(consumer_config)

producer = Producer(producer_config)

# Subscribe to topic
consumer.subscribe(['crawler-topic'])

# ==============================
# DATABASE
# ==============================

conn = sqlite3.connect(
    "../database/crawler.db"
)

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

# ==============================
# TRACK VISITED URLS
# ==============================

visited = set()

# ==============================
# URL NORMALIZATION
# ==============================

def normalize_url(base_url, link):

    if not link:
        return None

    if link.startswith("javascript:"):
        return None

    if link.startswith("mailto:"):
        return None

    absolute_url = urljoin(
        base_url,
        link
    )

    parsed = urlparse(absolute_url)

    cleaned_url = (
        parsed.scheme
        + "://"
        + parsed.netloc
        + parsed.path
    )

    return cleaned_url

# ==============================
# START CONSUMER
# ==============================

print("Distributed crawler started...\n")

while True:

    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        print("Kafka Error:", msg.error())
        continue

    # ==============================
    # GET URL
    # ==============================

    data = json.loads(
        msg.value().decode('utf-8')
    )

    url = data["url"]

    # Skip duplicates
    if url in visited:
        continue

    visited.add(url)

    print("\nCrawling:", url)

    try:

        # ==============================
        # DOWNLOAD PAGE
        # ==============================

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0"
                )
            },
            timeout=5,
            verify=False
        )

        print("Status:", response.status_code)

        if response.status_code != 200:
            continue

        # ==============================
        # PARSE HTML
        # ==============================

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

        print("Title:", title)

        # ==============================
        # STORE PAGE
        # ==============================

        cursor.execute("""
        INSERT OR IGNORE INTO pages(
            url,
            title,
            content
        )
        VALUES (?, ?, ?)
        """, (
            url,
            title,
            content
        ))

        conn.commit()

        print("Saved to database")

        # ==============================
        # EXTRACT LINKS
        # ==============================

        links_added = 0

        for link in soup.find_all("a"):

            href = link.get("href")

            normalized_url = normalize_url(
                url,
                href
            )

            if not normalized_url:
                continue

            # Restrict domain
            if (
                urlparse(normalized_url).netloc
                != urlparse(url).netloc
            ):
                continue

            # Skip duplicates
            if normalized_url in visited:
                continue

            # ==============================
            # SEND NEW URL TO KAFKA
            # ==============================

            producer.produce(
                "crawler-topic",

                json.dumps({
                    "url": normalized_url
                }).encode("utf-8")
            )

            producer.poll(0)

            links_added += 1

            print(
                "Sent to Kafka:",
                normalized_url
            )

        print(
            f"Links Added: {links_added}"
        )

        time.sleep(1)

    except Exception as e:

        print("Failed:", e)