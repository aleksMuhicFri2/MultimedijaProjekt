from flask import Flask, request, jsonify
from flask_cors import CORS
import elasticsearch

print("app.py STARTING")

app = Flask(__name__)
CORS(app)

es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])
INDEX = "regions"

# Ensure index exists
if not es.indices.exists(index=INDEX):
    es.indices.create(index=INDEX)

@app.route("/api/region/<name>")
def get_region(name):
    res = es.search(index=INDEX, body={"query": {"match": {"region": name}}})
    if not res["hits"]["hits"]:
        return jsonify({"error": "Region not found"}), 404
    return jsonify(res["hits"]["hits"][0]["_source"])

@app.route("/api/score", methods=["POST"])
def score_regions():
    weights = request.json

    res = es.search(index=INDEX, size=1000, body={"query": {"match_all": {}}})
    docs = [hit["_source"] for hit in res["hits"]["hits"]]

    def compute_score(region):
        score = 0
        for metric, w in weights.items():
            if metric in region:
                score += float(region[metric]) * float(w)
        return score

    ranked = sorted(docs, key=lambda x: compute_score(x), reverse=True)

    return jsonify({
        "ranking": ranked,
        "best": ranked[0] if ranked else None
    })

@app.route("/api/load")
def load_fake():
    """Example placeholder dataset"""
    data = [
        {"region": "gorenjska", "salary": 1750, "housing": 2400, "pollution": 32, "health": 7},
        {"region": "primorska", "salary": 1800, "housing": 3100, "pollution": 30, "health": 8},
        {"region": "stajerska", "salary": 1600, "housing": 2000, "pollution": 45, "health": 6}
    ]

    for entry in data:
        es.index(index=INDEX, document=entry)

    return {"message": "Loaded dummy data"}

if __name__ == "__main__":
    app.run(port=5000, debug=True)