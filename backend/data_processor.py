from municipality_codes import MUNICIPALITY_CODE_MAP
from municipality import Municipality
from region_mapping import OB_TO_REGION
from name_utils import normalize_name

# ------------------------------
# INIT MUNICIPALITIES
# ------------------------------
def init_municipalities():
    municipalities = {}

    for code, name in MUNICIPALITY_CODE_MAP.items():
        if code == "0":
            continue

        m = Municipality(code, name)
        m.region = OB_TO_REGION.get(normalize_name(name))
        if m.region is None:
            print(f"[MISSING REGION] {code}: {name} -> {normalize_name(name)}")
        municipalities[code] = m

    return municipalities


# ------------------------------
# POPULATION (SURS)
# ------------------------------
def process_population(raw_json, municipalities):
    for row in raw_json["data"]:
        muni_code = row["key"][0]
        age_code = row["key"][2]
        count = int(row["values"][0])

        if age_code == "999":
            continue

        m = municipalities.get(muni_code)
        if not m:
            continue

        age = int(age_code)
        if age <= 14:
            m.population_young += count
        elif age <= 64:
            m.population_working += count
        else:
            m.population_old += count


# ------------------------------
# PRICES + RENT
# ------------------------------
NAME_TO_CODE = {
    normalize_name(name): code
    for code, name in MUNICIPALITY_CODE_MAP.items()
    if code != "0"
}


def process_prices(prices_by_muni, rent_by_muni, municipalities):
    # Sale prices
    for muni_name, categories in prices_by_muni.items():
        code = NAME_TO_CODE.get(normalize_name(muni_name))
        if not code or code not in municipalities:
            continue

        m = municipalities[code]

        apt = categories.get("apartment")
        if apt:
            m.avg_price_m2_apartment = float(apt["avg_price_m2"])
            m.deals_sale_apartment = int(apt["deals_count"])

        house = categories.get("house")
        if house:
            m.avg_price_m2_house = float(house["avg_price_m2"])
            m.deals_sale_house = int(house["deals_count"])

    # Rent
    for muni_name, data in rent_by_muni.items():
        code = NAME_TO_CODE.get(normalize_name(muni_name))
        if not code or code not in municipalities:
            continue

        m = municipalities[code]
        m.avg_rent_m2 = float(data["avg_rent_m2"])
        m.deals_rent = int(data["deals_count_rent"])

def process_ioz(ioz_df, municipalities, year=2023):
    for _, row in ioz_df.iterrows():
        if int(row["year"]) != year:
            continue

        muni_name = row["municipality"]
        code = NAME_TO_CODE.get(normalize_name(muni_name))

        if not code or code not in municipalities:
            continue

        m = municipalities[code]

        m.ioz_ratio = float(row["iozRatio"])
        m.insured_total = int(row["insuredPeopleCount"])
        m.insured_with_ioz = int(row["insuredPeopleCountWithIOZ"])
        m.insured_without_ioz = int(row["insuredPeopleCountWithoutIOZ"])

def process_lat_long(coords_data, municipalities):
    """Updates municipalities with lat/long from a list of dictionaries."""
    for item in coords_data:
        # 1. Get the code and force it to be a 3-digit string (e.g., 61 -> "061")
        raw_code = item.get("code")
        code = str(raw_code).zfill(3) if raw_code is not None else None
        
        # 2. If code matching fails, fallback to name normalization
        if not code or code not in municipalities:
            name = item.get("municipality") or item.get("name")
            code = NAME_TO_CODE.get(normalize_name(name))
            
        # 3. If we found a valid municipality object, update its attributes
        if code and code in municipalities:
            m = municipalities[code]
            
            # Use a helper to safely convert to float, defaulting to 0.0 if missing
            def safe_float(key_list):
                for key in key_list:
                    val = item.get(key)
                    if val is not None and str(val).strip() != "" and str(val).lower() != 'nan':
                        return float(val)
                return 0.0

            m.latitude = safe_float(["lat", "latitude"])
            m.longitude = safe_float(["lon", "lng", "longitude"])

def process_history(history_data, municipalities):
    for item in history_data:
        code = str(item.get("code")).zfill(3)
        if code in municipalities:
            m = municipalities[code]
            m.history_sunny_days = int(item.get("sunny_days_count", 0))
            m.history_rainy_days = int(item.get("rainy_days_count", 0))
            m.history_foggy_days = int(item.get("foggy_days_count", 0))
            m.history_avg_aqi = float(item.get("avg_aqi", 0))
            m.history_avg_temp = float(item.get("avg_temp_yearly", 0))            
