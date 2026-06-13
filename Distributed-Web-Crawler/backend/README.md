# AetherSearch Backend: Crawler & Search API Pipeline

This directory contains the backend pipeline for **AetherSearch**, featuring multi-threaded/distributed crawlers, a SQLite relational storage layer, an Apache Kafka messaging system, an Elasticsearch indexer, and a Flask search API.

##  Technology Stack
- **Languages**: Python 3.10+
- **Frameworks**: Flask (API runtime), Flask-CORS
- **Databases**: SQLite (Relational raw storage), Elasticsearch (Full-text search engine)
- **Streaming & Messaging**: Apache Kafka (Distributed URL queue)
- **Libraries**: `requests` (HTTP client), `beautifulsoup4` (DOM parser), `elasticsearch` (ES client)
- **Server**: Gunicorn (WSGI HTTP server for production)

##  Directory Structure
```text
backend/
├── Dockerfile                  # Container definition for API runtime
├── start.sh                    # Gunicorn production startup script
├── api/
│   └── app.py                  # Flask search and autocomplete endpoints
├── crawler/
│   ├── url_manager.py          # URL normalization and absolute resolving
│   ├── basic_crawler.py        # Single-threaded web crawler
│   └── threaded_crawler.py     # Multi-threaded concurrent web crawler
├── database/
│   ├── database.py             # SQLite database initialization & migrations
│   ├── view_db.py              # CLI utility to inspect crawl records
│   └── crawler.db              # Local SQLite database file (ignored)
├── indexer/
│   └── elasticsearch_indexer.py# Bulk database-to-Elasticsearch indexer
├── scripts/
│   └── render_bootstrap.py     # Bootstrap script for cloud-tier database & index setup
└── kafka/
    ├── producer.py             # Kafka crawler seed dispatcher
    └── consumer.py             # Kafka distributed crawler worker node
```

##  Service Roles

1. **Flask API (`api/app.py`)**: Intermediates search query requests from the React client. Executes fuzzy, highlighted, and sorted matches, and provides debounced type-ahead autocomplete suggestions via Elasticsearch queries.
2. **Relational Crawlers (`crawler/`)**:
   - `basic_crawler.py`: Crawls recursively inside a domain up to a maximum depth.
   - `threaded_crawler.py`: Uses a thread pool and thread-safe scheduler tracking to scrape sites concurrently.
3. **Database Layer (`database/database.py`)**: Establishes schema and tables (`pages`) with unique constraints on URLs to avoid duplicates.
4. **Elasticsearch Indexer (`indexer/elasticsearch_indexer.py`)**: Extracts rows from SQLite and loads them into the Elasticsearch `webpages` index, setting the document ID equal to the page URL to guarantee index deduplication.
5. **Kafka Pipeline (`kafka/`)**: Dispatches seed URLs into Kafka partitions, allowing multiple independent consumer workers to pull, parse, and queue new URLs concurrently.

##  Local Development Setup

### Prerequisite
Ensure [Python 3.10+](https://www.python.org/) is installed.

### Installation
From the root of the project, install dependencies:
```bash
pip install -r Distributed-Web-Crawler/requirements.txt
```

### 1. Database Initialization
Create the database and schema:
```bash
python database/database.py
```

### 2. Run Crawlers
To crawl a site locally:
```bash
python crawler/threaded_crawler.py
```

### 3. Index Crawled Data
Export relational data to Elasticsearch:
```bash
python indexer/elasticsearch_indexer.py
```
*(Make sure your local Elasticsearch instance is running at http://localhost:9200)*

### 4. Start Flask Search API
```bash
python api/app.py
```
The search API runs on [http://localhost:5000](http://localhost:5000).

---