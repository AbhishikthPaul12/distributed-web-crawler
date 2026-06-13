import os
import re

from elasticsearch import Elasticsearch


def _parse_bonsai_url(es_host: str):
    """Parse a Bonsai-style URL (https://user:pass@host:port) into ES 7.x kwargs."""
    match = re.search(r"https?://([^:]+):([^@]+)@(.+)", es_host)
    if not match:
        return None

    username, password, remainder = match.group(1), match.group(2), match.group(3).rstrip("/")
    port_match = re.search(r":(\d+)$", remainder)

    if port_match:
        port = int(port_match.group(1))
        host = remainder[: port_match.start()]
    else:
        port = 443 if es_host.startswith("https") else 9200
        host = remainder

    use_ssl = es_host.startswith("https")
    return {
        "hosts": [{"host": host, "port": port, "use_ssl": use_ssl}],
        "http_auth": (username, password),
        "verify_certs": use_ssl,
    }


def create_es_client(host=None, **kwargs):
    es_host = host or os.environ.get("ES_HOST", "http://localhost:9200")

    timeout = kwargs.pop("request_timeout", kwargs.pop("timeout", 30))
    max_retries = kwargs.pop("max_retries", 3)
    retry_on_timeout = kwargs.pop("retry_on_timeout", True)
    # elasticsearch 8-only; ignore if passed by older call sites
    kwargs.pop("connections_per_node", None)

    transport = {
        "timeout": timeout,
        "max_retries": max_retries,
        "retry_on_timeout": retry_on_timeout,
    }

    bonsai = _parse_bonsai_url(es_host)
    if bonsai:
        return Elasticsearch(**bonsai, **transport, **kwargs)

    return Elasticsearch([es_host], **transport, **kwargs)
