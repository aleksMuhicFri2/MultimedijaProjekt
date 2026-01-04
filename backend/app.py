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
from search_engine import CitySearchEngine

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

# Initialize search engine
search_engine = CitySearchEngine()

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
        logger.warning("Population API returned empty list")
    else:
        logger.info(f"Population API returned {len(pop_raw)} entries")
        logger.info(f"Sample population entry: {pop_raw[0] if pop_raw else 'None'}")
    
    # Load Meta and Weather History
    coords_df = pd.read_csv("data/municipality_coords.csv")
    coords_list = coords_df.to_dict('records')

    history_df = pd.read_csv("data/municipality_weather.csv")
    history_list = history_df.to_dict('records')

    # 5. Process & Merge
    logger.info("Merging data...")
    municipalities = init_municipalities()
    
    logger.info(f"Initialized {len(municipalities)} municipalities")
    
    process_population(pop_raw, municipalities)
    process_prices(prices_by_muni, rent_by_muni, municipalities)
    process_ioz(ioz_df, municipalities)
    process_lat_long(coords_list, municipalities)
    process_history(history_list, municipalities)

    # 6. Final Calculation
    logger.info("Calculating normalized weather scores...")
    calculate_weather_scores(municipalities)
    calculate_demographics(municipalities)
    
    # Log a sample municipality to verify data
    if municipalities:
        sample_code = list(municipalities.keys())[0]
        sample_muni = municipalities[sample_code]
        logger.info(f"Sample municipality {sample_code} ({sample_muni.name}):")
        logger.info(f"  Population Young: {sample_muni.population_young}")
        logger.info(f"  Population Working: {sample_muni.population_working}")
        logger.info(f"  Population Old: {sample_muni.population_old}")
        logger.info(f"  Population Total: {sample_muni.population_total}")
        logger.info(f"  Area: {sample_muni.area_km2} km²")
        logger.info(f"  Density: {sample_muni.population_density}")
        logger.info(f"  to_dict() area_km2: {sample_muni.to_dict().get('area_km2')}")
    
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

@app.route("/api/municipalities/all", methods=["GET"])
def get_all_municipalities():
    """Get all municipalities for dropdown selections."""
    try:
        result = es.search(
            index=INDEX,
            body={
                "query": {"match_all": {}},
                "size": 500,
                "_source": ["code", "name", "region"]
            }
        )
        
        cities = [hit["_source"] for hit in result["hits"]["hits"]]
        # Sort by name
        cities.sort(key=lambda x: x.get('name', ''))
        
        return jsonify({"cities": cities})
    except Exception as e:
        logger.error(f"Failed to fetch cities: {e}")
        return jsonify({"error": str(e)}), 500

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

# ------------------------------
# SEARCH & RANKING ENDPOINTS
# ------------------------------

def _norm_code(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    return s.zfill(3)

@app.route("/api/search", methods=["POST"])
def search_cities():
    """Search and rank cities based on user criteria."""
    try:
        criteria = request.get_json()
        
        if not criteria:
            return jsonify({"error": "No criteria provided"}), 400
        
        # Log search criteria for debugging
        logger.info(f"Search criteria: workplace={criteria.get('workplace_city_code')}, "
                   f"max_commute={criteria.get('max_commute_minutes')}, "
                   f"search_type={criteria.get('search_type')}, "
                   f"weights={criteria.get('weights')}")
        
        # Get all municipalities from Elasticsearch
        result = es.search(
            index=INDEX,
            body={"query": {"match_all": {}}, "size": 500}
        )
        
        cities = [hit["_source"] for hit in result["hits"]["hits"]]

        # Normalize workplace code
        workplace_code_raw = criteria.get("workplace_city_code")
        workplace_code = _norm_code(workplace_code_raw)

        # Check if commute filter was requested
        commute_requested = bool(workplace_code and criteria.get("max_commute_minutes"))

        # Find workplace city
        workplace = next(
            (c for c in cities if _norm_code(c.get("code")) == workplace_code),
            None
        ) if workplace_code else None
        
        workplace_found = workplace is not None

        # Run the search (now returns tuple with meta)
        ranked_cities, search_meta = search_engine.search_and_rank(
            cities, 
            {**criteria, "workplace_city_code": workplace_code or ""}
        )

        # Determine if commute filter was actually applied
        commute_applied = bool(commute_requested and workplace_found)

        raw_limit = criteria.get('limit', 10)
        try:
            limit = max(1, min(int(raw_limit), 100))
        except Exception:
            limit = 10

        results = ranked_cities[:limit]

        # Build suggestions if no results
        suggestions = []
        if len(ranked_cities) == 0:
            if search_meta.get("after_hard_filters", 0) == 0:
                suggestions.append("Try increasing your budget or reducing desired space (m²)")
                if commute_requested:
                    suggestions.append("Consider increasing max commute time or removing workplace filter")
            elif search_meta.get("after_score_filters", 0) == 0:
                # Cities passed hard filters but failed score thresholds
                score_stats = search_meta.get("score_filter_stats", {}).get("details", {})
                thresholds = search_meta.get("thresholds_applied", {})
                
                # Find which categories filtered out the most cities
                if score_stats:
                    sorted_filters = sorted(score_stats.items(), key=lambda x: x[1], reverse=True)
                    top_blockers = [cat for cat, count in sorted_filters[:3] if count > 0]
                    
                    category_names = {
                        "affordability": "Affordability",
                        "market_activity": "Market Activity",
                        "population_vitality": "Demographics",
                        "healthcare": "Healthcare",
                        "housing_diversity": "Housing Options",
                        "commute": "Commute"
                    }
                    
                    for blocker in top_blockers:
                        threshold = thresholds.get(blocker, 0)
                        name = category_names.get(blocker, blocker)
                        suggestions.append(f"Lower your {name} requirement (currently needs score ≥{threshold})")
                
                if not suggestions:
                    suggestions.append("Try lowering some of your priority weights")

        return jsonify({
            "total_matches": len(ranked_cities),
            "results": results,
            "meta": {
                "workplace_city_code": workplace_code,
                "workplace_city_code_raw": workplace_code_raw,
                "workplace_found": workplace_found,
                "workplace_name": workplace.get("name") if workplace else None,
                "commute_filter_requested": commute_requested,
                "commute_filter_applied": commute_applied,
                "google_maps_available": search_engine._gmaps_calls_this_search > 0 if hasattr(search_engine, '_gmaps_calls_this_search') else False,
                "total_cities": search_meta.get("total_input", 0),
                "after_budget_commute_filter": search_meta.get("after_hard_filters", 0),
                "after_score_filter": search_meta.get("after_score_filters", 0),
                "thresholds_applied": search_meta.get("thresholds_applied", {}),
                "filter_stats": search_meta.get("filter_stats", {}),
                "score_filter_stats": search_meta.get("score_filter_stats", {}),
            },
            "suggestions": suggestions
        })

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/api/search/life-stages", methods=["GET"])
def get_life_stages():
    """Get available life stage options."""
    return jsonify({
        "life_stages": list(search_engine.life_stage_profiles.keys())
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)