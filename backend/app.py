

from flask import Flask, jsonify
from flask_cors import CORS
import elasticsearch

from municipality_codes import MUNICIPALITY_CODE_MAP
from region_mapping import OB_TO_REGION
from name_utils import normalize_name
import pandas as pd

from data_processor import (
    init_municipalities,
    process_population,
    process_prices,
    process_ioz
)
from surs_api import get_population_per_obcina

app = Flask(__name__)
CORS(app)

es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])
INDEX = "municipalities"


print("app.py STARTING")

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

ioz_df = pd.read_csv("data/ioz.csv")    


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
    process_ioz(ioz_df, municipalities)
    

    for code, muni in municipalities.items():
        es.index(index=INDEX, id=code, document=muni.to_dict())

    print(f"Loaded {len(municipalities)} municipalities")


def municipalities_exist():
    if not es.indices.exists(index=INDEX):
        return False

    res = es.count(index=INDEX)
    return res["count"] > 0


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


# -----------------------------------------
# RETURN REGIONS KEYED BY MUNICIPALITY CODE
# -----------------------------------------
@app.route("/api/municipalities/regions")
def get_municipality_regions():
    region_by_code = {}

    for code, name in MUNICIPALITY_CODE_MAP.items():
        if code == "0":
            continue

        normalized = normalize_name(name)
        region = OB_TO_REGION.get(normalized)

        if region:
            region_by_code[code] = region

    return jsonify(region_by_code)



if __name__ == "__main__":
    app.run(port=5000, debug=True)
