import os

from elasticsearch import Elasticsearch

# Bonsai sandbox clusters run Elasticsearch 7.x. elasticsearch-py 8 sends
# compatible-with=8 headers by default, which ES 7 rejects with HTTP 406.
# ES 7 compatibility headers also work against local Elasticsearch 8.
ES7_COMPAT_HEADERS = {
    "accept": "application/vnd.elasticsearch+json; compatible-with=7",
    "content-type": "application/vnd.elasticsearch+json; compatible-with=7",
}


def create_es_client(host=None, **kwargs):
    es_host = host or os.environ.get("ES_HOST", "http://localhost:9200")
    options = {
        "request_timeout": 30.0,
        "retry_on_timeout": True,
        "max_retries": 3,
        "headers": ES7_COMPAT_HEADERS,
    }
    options.update(kwargs)
    return Elasticsearch(es_host, **options)
