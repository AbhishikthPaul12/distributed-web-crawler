import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from es_client import create_es_client

# CREATE FLASK APP

app = Flask(__name__)

# CORS
CORS(app)

# CONNECT TO ELASTICSEARCH

es = create_es_client(
    connections_per_node=25,
    request_timeout=15.0,
)


INDEX_NAME = "webpages"

# HOME ROUTE

@app.route("/")
def home():
    return {
        "message": "Distributed Search Engine API Running"
    }

# SEARCH ROUTE

@app.route("/search")
def search():
    # Get query parameter
    query = request.args.get("q")
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)

    if not query:
        return jsonify({
            "error": "Query parameter missing"
        }), 400

    if page < 1:
        page = 1
    if size < 1:
        size = 10

    from_ = (page - 1) * size

    # ELASTICSEARCH QUERY WITH HIGHLIGHTING, PAGINATION AND SORTING
    try:
        sort_by = request.args.get("sort", default="relevance")
        sort_query = [{"_score": "desc"}]
        if sort_by == "title":
            sort_query = [{"title.keyword": {"order": "asc", "unmapped_type": "keyword"}}]
        elif sort_by == "url":
            sort_query = [{"url.keyword": {"order": "asc", "unmapped_type": "keyword"}}]

        response = es.search(
            index=INDEX_NAME,
            from_=from_,
            size=size,
            query={
                "bool": {
                    "should": [
                        {
                            "simple_query_string": {
                                "query": query,
                                "fields": ["title^3", "content"],
                                "default_operator": "and",
                                "boost": 2.0
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content"],
                                "fuzziness": "AUTO",
                                "boost": 1.0
                            }
                        }
                    ]
                }
            },
            sort=sort_query,
            highlight={
                "fields": {
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 1
                    }
                }
            }
        )

        # FORMAT RESULTS
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            
            # Get highlight snippet or fallback to first 150 chars of content
            highlight = hit.get("highlight", {})
            snippet_list = highlight.get("content", [])
            snippet = snippet_list[0] if snippet_list else (source.get("content", "")[:150] + "...")

            results.append({
                "url": source["url"],
                "title": source["title"],
                "score": hit["_score"],
                "snippet": snippet
            })

        total = response["hits"]["total"]["value"] if isinstance(response["hits"]["total"], dict) else response["hits"]["total"]

        return jsonify({
            "results": results,
            "total": total,
            "page": page,
            "size": size
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# AUTOCOMPLETE ROUTE

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])

    try:
        response = es.search(
            index=INDEX_NAME,
            query={
                "match_phrase_prefix": {
                    "title": {
                        "query": query
                    }
                }
            },
            size=6
        )

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "title": source.get("title", ""),
                "url": source.get("url", "")
            })
        return jsonify(results)
    except Exception as e:
        return jsonify([])

# START SERVER

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=5000)