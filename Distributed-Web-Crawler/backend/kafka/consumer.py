import os
import sys
import json
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from confluent_kafka import Consumer, Producer

# Disable SSL warnings
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# Add parent directory of kafka (backend) to path to import database and url_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import save_page
from crawler.url_manager import normalize_url

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
# TRACK VISITED URLS
# ==============================

visited = set()

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
    # GET URL FROM KAFKA
    # ==============================

    data = json.loads(msg.value().decode('utf-8'))
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
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
            verify=False
        )

        print("Status:", response.status_code)

        if response.status_code != 200:
            continue

        # ==============================
        # PARSE HTML
        # ==============================

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.text.strip() if soup.title else "No Title"
        content = soup.get_text()

        print("Title:", title)

        # ==============================
        # STORE PAGE using shared database helper
        # ==============================

        if save_page(url, title, content):
            print("Saved to database")
        else:
            print("Skipped (already exists)")

        # ==============================
        # EXTRACT LINKS
        # ==============================

        links_added = 0

        for link in soup.find_all("a"):
            href = link.get("href")
            normalized_url = normalize_url(url, href)

            if not normalized_url:
                continue

            # Restrict to same domain
            if urlparse(normalized_url).netloc != urlparse(url).netloc:
                continue

            # Skip duplicates
            if normalized_url in visited:
                continue

            # ==============================
            # SEND NEW URL TO KAFKA
            # ==============================

            producer.produce(
                "crawler-topic",
                json.dumps({"url": normalized_url}).encode("utf-8")
            )
            producer.poll(0)

            links_added += 1
            print("Sent to Kafka:", normalized_url)

        print(f"Links Added: {links_added}")
        time.sleep(1)

    except Exception as e:
        print("Failed:", e)