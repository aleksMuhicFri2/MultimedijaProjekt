import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import elasticsearch
from elasticsearch import helpers
import pandas as pd

# API and Utility Imports
from google_maps import gmaps
from municipality_codes import MUNICIPALITY_CODE_MAP
from region_mapping import OB_TO_REGION
from name_utils import normalize_name

# Data Processing Imports
from data_processor import (
    init_municipalities,
    process_population,
    process_prices,
    process_ioz,
    process_lat_long,
    process_history,
    calculate_weather_scores,
    calculate_demographics
)
from surs_api import get_population_per_obcina

# ------------------------------
# CONFIGURATION & SETUP
# ------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("app.py STARTING")
print("GOOGLE MAPS KEY LOADED:", bool(os.environ.get("GOOGLE_MAPS_API_KEY")))

app = Flask(__name__)
CORS(app)

# Elasticsearch Connection
es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])
INDEX = "municipalities"

# ------------------------------
# DATA LOADING LOGIC
# ------------------------------
def fetch_and_process_data():
    """
    Orchestrates the fetching and processing of all CSV and API data.
    Returns a dictionary of municipality objects.
    """
    logger.info("Reading CSV data...")
    
    # 1. Load Prices
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

    # 2. Load Rent
    rent_df = pd.read_csv("data/pricesRent.csv")
    rent_by_muni = {
        row["OBCINA"]: {
            "deals_count_rent": int(row["deals_count"]),
            "avg_rent_m2": float(row["avg_rent_m2"]),
            "median_rent_m2": float(row["median_rent_m2"])
        }
        for _, row in rent_df.iterrows()
    }

    # 3. Load IOZ
    ioz_df = pd.read_csv("data/ioz.csv")

    # 4. Load Population (API)
    logger.info("Fetching population data from SURS API...")
    pop_raw = get_population_per_obcina()
    if not pop_raw:
        raise RuntimeError("Population API returned nothing")
    
    # Load Meta and Weather History
    coords_df = pd.read_csv("data/municipality_coords.csv")
    coords_list = coords_df.to_dict('records')

    history_df = pd.read_csv("data/municipality_weather.csv") # <--- Ensure name matches your file
    history_list = history_df.to_dict('records')

    # 5. Process & Merge
    logger.info("Merging data...")
    municipalities = init_municipalities()
    
    process_population(pop_raw, municipalities)
    process_prices(prices_by_muni, rent_by_muni, municipalities)
    process_ioz(ioz_df, municipalities)
    process_lat_long(coords_list, municipalities)
    process_history(history_list, municipalities)

    # 6. Final Calculation (Weather Index)
    # This must happen LAST so that it has access to the merged history data
    logger.info("Calculating normalized weather scores...")
    calculate_weather_scores(municipalities)
    calculate_demographics(municipalities)
    
    return municipalities

def load_all_data():
    """
    Cleans the index and bulk loads new data.
    """
    logger.info("Starting data load procedure...")

    # 1. Ensure Index Exists (Recreate if needed)
    if es.indices.exists(index=INDEX):
        es.indices.delete(index=INDEX)
    es.indices.create(index=INDEX)

    # 2. Process Data
    municipalities = fetch_and_process_data()

    # 3. Bulk Index into Elasticsearch
    logger.info(f"Bulk indexing {len(municipalities)} municipalities...")
    
    actions = [
        {
            "_index": INDEX,
            "_id": code,
            "_source": muni.to_dict()
        }
        for code, muni in municipalities.items()
    ]

    success, failed = helpers.bulk(es, actions, stats_only=True)
    logger.info(f"Data Load Complete. Success: {success}, Failed: {failed}")
    return success

# ------------------------------
# INITIALIZATION CHECK
# ------------------------------
if not es.indices.exists(index=INDEX) or es.count(index=INDEX)["count"] == 0:
    try:
        load_all_data()
    except Exception as e:
        logger.error(f"Failed to load initial data: {e}")

# ------------------------------
# API ENDPOINTS
# ------------------------------

@app.route("/api/admin/reload-data", methods=["POST"])
def admin_reload_data():
    try:
        count = load_all_data()
        return jsonify({"status": "success", "message": f"Reloaded data for all municipalities"}), 200
    except Exception as e:
        logger.error(f"Reload failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/municipality/<code>")
def get_municipality(code):
    res = es.get(index=INDEX, id=code, ignore=[404])
    if not res or not res.get("found"):
        return jsonify({"error": "Municipality not found"}), 404
    return jsonify(res["_source"])

@app.route("/api/municipalities/regions")
def get_municipality_regions():
    region_by_code = {}
    for code, name in MUNICIPALITY_CODE_MAP.items():
        if code == "0":
            continue
        region = OB_TO_REGION.get(normalize_name(name))
        if region:
            region_by_code[code] = region
    return jsonify(region_by_code)

# ------------------------------
# GOOGLE MAPS ENDPOINTS
# ------------------------------
@app.route("/api/geocode")
def geocode():
    place = request.args.get("place")
    if not place:
        return {"error": "Missing place"}, 400

    try:
        result = gmaps.geocode(place)
        if not result:
            return {"error": "Not found"}, 404
        loc = result[0]["geometry"]["location"]
        return {"lat": loc["lat"], "lng": loc["lng"]}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/travel-time")
def travel_time():
    origin = request.args.get("from")
    destination = request.args.get("to")
    mode = request.args.get("mode", "driving")

    if not origin or not destination:
        return {"error": "Missing parameters"}, 400

    try:
        res = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode=mode
        )
        if not res["rows"] or not res["rows"][0]["elements"]:
             return {"error": "No routes found"}, 404
             
        element = res["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return {"error": "Route not found"}, 404

        return {
            "distance_m": element["distance"]["value"],
            "distance_text": element["distance"]["text"],
            "duration_s": element["duration"]["value"],
            "duration_text": element["duration"]["text"]
        }
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)