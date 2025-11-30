from flask import Flask, request, jsonify
from flask_cors import CORS
import elasticsearch
import pandas as pd

from data_processor import (
    init_region_data,
    process_population,
    process_prices,
    normalize_region_data
)

from surs_api import get_population_per_obcina

from region_mapping import OB_TO_REGION


print("app.py STARTING")

app = Flask(__name__)
CORS(app)

es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])
INDEX = "regions"

# ------------------------------
# Load sale prices (Houses + Apartments)
# ------------------------------
prices_df = pd.read_csv("data/pricesHouses.csv")
prices_by_muni = {}

for _, row in prices_df.iterrows():
    muni = row["OBCINA"]

    if muni not in prices_by_muni:
        prices_by_muni[muni] = {}

    cat = row["category"]  # 'apartment' or 'house'
    prices_by_muni[muni][cat] = {
        "deals_count": int(row["deals_count"]),
        "avg_price_m2": float(row["avg_price_m2"]),
        "median_price_m2": float(row["median_price_m2"])
    }

# ------------------------------
# Load rental prices (per m2)
# ------------------------------
rent_df = pd.read_csv("data/pricesRent.csv")
rent_by_muni = {}

for _, row in rent_df.iterrows():
    muni = row["OBCINA"]

    rent_by_muni[muni] = {
        "deals_count_rent": int(row["deals_count"]),
        "avg_rent_m2": float(row["avg_rent_m2"]),
        "median_rent_m2": float(row["median_rent_m2"])
    }


# Ensure index exists
if not es.indices.exists(index=INDEX):
    es.indices.create(index=INDEX)


# ------------------------------
#       API ENDPOINTS
# ------------------------------

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


@app.route("/api/update-data")
def update_data():
    print("Updating data from SURS...")

    pop_raw = get_population_per_obcina()
    if pop_raw is None:
        return {"error": "Population API returned nothing"}, 500

    region_data = init_region_data()

    # uses static MUNICIPALITY_CODE_MAP internally
    process_population(pop_raw, region_data)

    process_prices(prices_by_muni, rent_by_muni, region_data)

    for region, metrics in region_data.items():
        body = {"region": region, **metrics}
        es.index(index=INDEX, document=body)

    return {"message": "Updated successfully", "regions": region_data}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
