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

def calculate_demographics(municipalities):
    """
    Calculates the national average ratios and identifies the 
    most significant demographic outlier for each municipality.
    """
    m_list = [m for m in municipalities.values() if (m.population_young + m.population_working + m.population_old) > 0]
    count = len(m_list)
    if count == 0: return

    # Pass 1: Global Average Ratios
    avg_y = sum(m.population_young / (m.population_young + m.population_working + m.population_old) for m in m_list) / count
    avg_w = sum(m.population_working / (m.population_young + m.population_working + m.population_old) for m in m_list) / count
    avg_o = sum(m.population_old / (m.population_young + m.population_working + m.population_old) for m in m_list) / count

    # Pass 2: Identify Outliers
    for m in m_list:
        total = m.population_young + m.population_working + m.population_old
        ry, rw, ro = m.population_young/total, m.population_working/total, m.population_old/total

        # Compare local ratio to global average
        diffs = {
            "Mlado Prebivalstvo": (ry - avg_y) / avg_y,
            "Delavno Prebivalstvo": (rw - avg_w) / avg_w,
            "Staro Prebivalstvo": (ro - avg_o) / avg_o
        }

        # The key with the highest positive deviation is our tag
        m.main_demographic = max(diffs, key=diffs.get)


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
        raw_code = item.get("code")
        code = str(raw_code).zfill(3) if raw_code is not None else None
        
        if not code or code not in municipalities:
            name = item.get("municipality") or item.get("name")
            code = NAME_TO_CODE.get(normalize_name(name))
            
        if code and code in municipalities:
            m = municipalities[code]
            
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

# ------------------------------
# WEATHER SCORING (INDEX)
# ------------------------------
def calculate_weather_scores(municipalities):
    """
    Calculates a weather quality index from 1-10.
    Formula: (diff_temp * 10) + (diff_sun * 5) - (diff_aqi * 5) - (diff_rain * 2)
    """
    m_list = list(municipalities.values())
    count = len(m_list)
    if count == 0:
        return

    # Pass 1: Calculate Global Averages
    avg_temp = sum(m.history_avg_temp for m in m_list) / count
    avg_sun  = sum(m.history_sunny_days for m in m_list) / count
    avg_aqi  = sum(m.history_avg_aqi for m in m_list) / count
    avg_rain = sum(m.history_rainy_days for m in m_list) / count

    # Pass 2: Calculate Raw Scores
    raw_scores = []
    for m in m_list:
        score = (
            (m.history_avg_temp - avg_temp) * 10 +
            (m.history_sunny_days - avg_sun) * 5 -
            (m.history_avg_aqi - avg_aqi) * 5 -
            (m.history_rainy_days - avg_rain) * 1.5
        )
        # Store raw score temporarily on the object to use in normalization pass
        m._raw_weather_score = score
        raw_scores.append(score)

    # Pass 3: Normalize to 1-10 Scale
    min_score = min(raw_scores)
    max_score = max(raw_scores)

    for m in m_list:
        if max_score == min_score:
            m.weather_index = 5.0  # Avoid division by zero
        else:
            # Scale from 1 to 10
            # formula: 1 + (x - min) / (max - min) * (10 - 1)
            normalized = 1 + ((m._raw_weather_score - min_score) / (max_score - min_score) * 9)
            m.weather_index = round(normalized, 2)
        
        # Cleanup temporary attribute
        if hasattr(m, '_raw_weather_score'):
            del m._raw_weather_score