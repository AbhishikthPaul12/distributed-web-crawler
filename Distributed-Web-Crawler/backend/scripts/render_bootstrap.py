"""
One-time Render bootstrap: seed demo crawl data and index it into Elasticsearch.
Runs automatically via initialDeployHook on first backend deploy.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import fetch_all_pages, save_page

from es_client import create_es_client

DEMO_PAGES = [
    (
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "A Light in the Attic",
        "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary.",
    ),
    (
        "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
        "Tipping the Velvet",
        "Through the door of a little Lambeth house the reader is ushered into a nightmarish Victorian London where Dorothy Tipping begins her transformation from oyster girl to male impersonator.",
    ),
    (
        "https://books.toscrape.com/catalogue/soumission_998/index.html",
        "Soumission",
        "Dans une France assez proche de la notre, un homme s'engage dans la carriere universitaire. Peu motive par l'enseignement, il s'attend a une vie ennuyeuse mais calme.",
    ),
    (
        "https://books.toscrape.com/catalogue/sharp-objects_997/index.html",
        "Sharp Objects",
        "Fresh from a brief stay at a psych hospital, reporter Camille Preaker faces a troubling assignment: she must return to her tiny hometown to cover the murders of two preteen girls.",
    ),
    (
        "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
        "Sapiens: A Brief History of Humankind",
        "From a renowned historian comes a groundbreaking narrative of humanity's creation and evolution that explores the ways in which biology and history have defined us.",
    ),
    (
        "https://en.wikipedia.org/wiki/Distributed_computing",
        "Distributed computing - Wikipedia",
        "Distributed computing is a field of computer science that studies distributed systems. A distributed system is a system whose components are located on different networked computers.",
    ),
    (
        "https://en.wikipedia.org/wiki/Web_crawler",
        "Web crawler - Wikipedia",
        "A web crawler, spider, or search engine bot is an internet bot that systematically browses the World Wide Web, typically for the purpose of web indexing.",
    ),
    (
        "https://en.wikipedia.org/wiki/Elasticsearch",
        "Elasticsearch - Wikipedia",
        "Elasticsearch is a search engine based on the Lucene library. It provides a distributed, multitenant-capable full-text search engine with an HTTP web interface.",
    ),
]

INDEX_NAME = "webpages"


def wait_for_elasticsearch(es, retries: int = 30, delay: int = 5) -> None:
    for attempt in range(1, retries + 1):
        try:
            if es.ping():
                print(f"Elasticsearch is ready (attempt {attempt}).")
                return
        except Exception as exc:
            print(f"Waiting for Elasticsearch ({attempt}/{retries}): {exc}")
        time.sleep(delay)
    raise RuntimeError("Elasticsearch did not become ready in time.")


def seed_demo_pages() -> int:
    existing = fetch_all_pages()
    if existing:
        print(f"Database already has {len(existing)} pages — skipping seed.")
        return len(existing)

    print("Seeding demo pages into SQLite...")
    for url, title, content in DEMO_PAGES:
        save_page(url, title, content)
    pages = fetch_all_pages()
    print(f"Seeded {len(pages)} demo pages.")
    return len(pages)


def index_pages(es) -> None:
    pages = fetch_all_pages()
    print(f"Indexing {len(pages)} pages into Elasticsearch...")
    for url, title, content in pages:
        es.index(
            index=INDEX_NAME,
            id=url,
            body={"url": url, "title": title, "content": content},
        )
        print(f"  Indexed: {title}")
    print("Indexing completed.")


def index_is_empty(es) -> bool:
    try:
        if not es.indices.exists(index=INDEX_NAME):
            return True
        count = es.count(index=INDEX_NAME).get("count", 0)
        return count == 0
    except Exception:
        return True


def main() -> None:
    es = create_es_client()
    wait_for_elasticsearch(es)

    if not index_is_empty(es):
        print(f"Index '{INDEX_NAME}' already has documents — skipping bootstrap.")
        return

    page_count = seed_demo_pages()
    if page_count == 0:
        print("No pages to index.")
        return

    index_pages(es)


if __name__ == "__main__":
    main()
