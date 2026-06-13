import os
from urllib.parse import unquote, urlparse

from elasticsearch import Elasticsearch


def _parse_bonsai_url(es_host: str):
    """Parse a Bonsai URL into the connection format recommended by Bonsai docs."""
    parsed = urlparse(es_host)
    if not parsed.username or not parsed.password or not parsed.hostname:
        return None

    port = parsed.port or (443 if parsed.scheme == "https" else 9200)
    use_ssl = parsed.scheme == "https"

    return [{
        "host": parsed.hostname,
        "port": port,
        "use_ssl": use_ssl,
        "http_auth": (unquote(parsed.username), unquote(parsed.password)),
    }]


def create_es_client(host=None, **kwargs):
    es_host = host or os.environ.get("ES_HOST", "http://localhost:9200")

    timeout = kwargs.pop("request_timeout", kwargs.pop("timeout", 30))
    max_retries = kwargs.pop("max_retries", 3)
    retry_on_timeout = kwargs.pop("retry_on_timeout", True)
    kwargs.pop("connections_per_node", None)

    transport = {
        "timeout": timeout,
        "max_retries": max_retries,
        "retry_on_timeout": retry_on_timeout,
    }

    bonsai_hosts = _parse_bonsai_url(es_host)
    if bonsai_hosts:
        return Elasticsearch(bonsai_hosts, **transport, **kwargs)

    return Elasticsearch([es_host], **transport, **kwargs)
