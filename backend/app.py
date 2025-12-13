from flask import Flask, jsonify
from flask_cors import CORS
import elasticsearch
import pandas as pd

from data_processor import (
    init_municipalities,
    process_population,
    process_prices
)
from surs_api import get_population_per_obcina

print("app.py STARTING")

app = Flask(__name__)
CORS(app)

es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])
INDEX = "municipalities"


# ------------------------------
# LOAD CSV DATA (FIRST!)
# ------------------------------
prices_df = pd.read_csv("data/pricesHouses.csv")
prices_by_muni = {}

for _, row in prices_df.iterrows():
    muni = row["OBCINA"]
    prices_by_muni.setdefault(muni, {})

    prices_by_muni[muni][row["category"]] = {
        "deals_count": int(row["deals_count"]),
        "avg_price_m2": float(row["avg_price_m2"]),
        "median_price_m2": float(row["median_price_m2"])
    }

rent_df = pd.read_csv("data/pricesRent.csv")
rent_by_muni = {}

for _, row in rent_df.iterrows():
    rent_by_muni[row["OBCINA"]] = {
        "deals_count_rent": int(row["deals_count"]),
        "avg_rent_m2": float(row["avg_rent_m2"]),
        "median_rent_m2": float(row["median_rent_m2"])
    }


# ------------------------------
# ENSURE INDEX
# ------------------------------
if not es.indices.exists(index=INDEX):
    es.indices.create(index=INDEX)


# ------------------------------
# DATA LOADING LOGIC
# ------------------------------
def load_all_data():
    print("Loading municipality data...")

    pop_raw = get_population_per_obcina()
    if pop_raw is None:
        raise RuntimeError("Population API returned nothing")

    municipalities = init_municipalities()

    process_population(pop_raw, municipalities)
    process_prices(prices_by_muni, rent_by_muni, municipalities)

    for code, muni in municipalities.items():
        es.index(index=INDEX, id=code, document=muni.to_dict())

    print(f"Loaded {len(municipalities)} municipalities")


def municipalities_exist():
    try:
        res = es.count(index=INDEX)
        return res["count"] > 0
    except Exception:
        return False


# ------------------------------
# AUTO-LOAD DATA ON STARTUP
# ------------------------------
if not municipalities_exist():
    print("No municipality data found. Loading...")
    load_all_data()
else:
    print("Municipality data already present. Skipping load.")


# ------------------------------
# API ENDPOINTS
# ------------------------------
@app.route("/api/update-data")
def update_data():
    load_all_data()
    return {"message": "Updated successfully"}


@app.route("/api/municipality/<code>")
def get_municipality(code):
    res = es.get(index=INDEX, id=code, ignore=[404])
    if not res or not res.get("found"):
        return jsonify({"error": "Municipality not found"}), 404
    return jsonify(res["_source"])


if __name__ == "__main__":
    app.run(port=5000, debug=True)
