import os
import sys
from elasticsearch import Elasticsearch

# Add parent directory of indexer (backend) to path to import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import fetch_all_pages

# CONNECT TO ELASTICSEARCH
es_host = os.environ.get("ES_HOST", "http://localhost:9200")
es = Elasticsearch(es_host)

# FETCH DATA FROM SQLITE DATABASE
pages = fetch_all_pages()

print(f"\nFound {len(pages)} pages in database")

# INDEX NAME
INDEX_NAME = "webpages"

# INDEX DOCUMENTS
for page in pages:
    url, title, content = page

    document = {
        "url": url,
        "title": title,
        "content": content
    }

    # Index page
    response = es.index(
        index=INDEX_NAME,
        id=url,
        document=document
    )

    print("Indexed:", title.encode("ascii", errors="replace").decode("ascii"))

print("\nIndexing completed")