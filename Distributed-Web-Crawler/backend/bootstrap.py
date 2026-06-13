import os
import sys
import threading
import time

BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from database.database import fetch_all_pages, save_page
from es_client import create_es_client

INDEX_NAME = "webpages"

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

INDEX_MAPPINGS = {
    "mappings": {
        "properties": {
            "url": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}},
            "title": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}},
            "content": {"type": "text"},
        }
    }
}

_lock = threading.Lock()
_ready = False


def wait_for_elasticsearch(es, retries=12, delay=5):
    for attempt in range(1, retries + 1):
        try:
            if es.ping():
                print(f"Elasticsearch is ready (attempt {attempt}).", flush=True)
                return
        except Exception as exc:
            print(f"Waiting for Elasticsearch ({attempt}/{retries}): {exc}", flush=True)
        time.sleep(delay)
    raise RuntimeError("Elasticsearch did not become ready in time.")


def ensure_index(es):
    if not es.indices.exists(index=INDEX_NAME):
        print(f"Creating index '{INDEX_NAME}'...", flush=True)
        es.indices.create(index=INDEX_NAME, body=INDEX_MAPPINGS)


def index_is_empty(es):
    try:
        if not es.indices.exists(index=INDEX_NAME):
            return True
        return es.count(index=INDEX_NAME).get("count", 0) == 0
    except Exception:
        return True


def seed_demo_pages():
    existing = fetch_all_pages()
    if existing:
        print(f"Database already has {len(existing)} pages — skipping seed.", flush=True)
        return len(existing)

    print("Seeding demo pages into SQLite...", flush=True)
    for url, title, content in DEMO_PAGES:
        save_page(url, title, content)
    pages = fetch_all_pages()
    print(f"Seeded {len(pages)} demo pages.", flush=True)
    return len(pages)


def index_pages(es):
    pages = fetch_all_pages()
    print(f"Indexing {len(pages)} pages into Elasticsearch...", flush=True)
    for url, title, content in pages:
        es.index(
            index=INDEX_NAME,
            id=url,
            body={"url": url, "title": title, "content": content},
        )
        print(f"  Indexed: {title}", flush=True)
    print("Indexing completed.", flush=True)


def run_bootstrap(es=None):
    client = es or create_es_client()
    wait_for_elasticsearch(client)
    ensure_index(client)

    if not index_is_empty(client):
        print(f"Index '{INDEX_NAME}' already has documents.", flush=True)
        return

    page_count = seed_demo_pages()
    if page_count == 0:
        print("No pages to index.", flush=True)
        return

    index_pages(client)


def ensure_search_ready(es, force=False):
    """Seed and index demo data the first time search is needed."""
    global _ready
    if _ready and not force:
        return

    with _lock:
        if _ready and not force:
            return
        run_bootstrap(es)
        _ready = True


def reset_ready_state():
    global _ready
    _ready = False
