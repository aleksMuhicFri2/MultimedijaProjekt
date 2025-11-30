from region_mapping import OB_TO_REGION
import unicodedata
from municipality_codes import MUNICIPALITY_CODE_MAP


# ------------------------------------------
# NORMALIZATION HELPERS
# ------------------------------------------

def normalize_name(name: str):
    if not name:
        return None

    name = name.split("/")[0].strip().lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )


def get_region_for_obcina(name):
    return OB_TO_REGION.get(normalize_name(name))


# ------------------------------------------
# REGION DATA STRUCTURE
# ------------------------------------------

def init_region_data():
    regions = [
        "gorenjska", "goriska", "obalno-kraska", "notranjsko-kraska",
        "osrednjeslovenska", "zasavska", "savinjska", "koroska",
        "podravska", "pomurska", "posavska", "jugovzhodna"
    ]

    return {
        r: {
            "population_young": 0,
            "population_working": 0,
            "population_old": 0,
            "avg_price_m2": 0,
            "avg_rent_m2": 0,
        }
        for r in regions
    }

# ------------------------------------------
# POPULATION PROCESSING
# ------------------------------------------

def process_population(raw_json, region_data):

    for row in raw_json["data"]:
        muni_code = row["key"][0]
        age_code  = row["key"][2]
        count     = int(row["values"][0])

        if age_code == "999":
            continue

        muni_name = MUNICIPALITY_CODE_MAP.get(muni_code)
        if not muni_name:
            continue

        region = get_region_for_obcina(muni_name)
        if not region:
            continue

        age = int(age_code)
        if age <= 14:
            region_data[region]["population_young"] += count
        elif age <= 64:
            region_data[region]["population_working"] += count
        else:
            region_data[region]["population_old"] += count


# ------------------------------------------
# PRICES + RENT
# ------------------------------------------

def process_prices(prices_by_muni, rent_by_muni, region_data):

    tmp = {
        region: {
            "sum_price": 0,
            "count_price": 0,
            "sum_rent": 0,
            "count_rent": 0
        }
        for region in region_data
    }

    for muni, categories in prices_by_muni.items():
        region = get_region_for_obcina(muni)
        if not region:
            continue

        for data in categories.values():
            tmp[region]["sum_price"] += data["avg_price_m2"]
            tmp[region]["count_price"] += 1

    for muni, data in rent_by_muni.items():
        region = get_region_for_obcina(muni)
        if not region:
            continue

        tmp[region]["sum_rent"] += data["avg_rent_m2"]
        tmp[region]["count_rent"] += 1

    for region in region_data:
        c = tmp[region]
        if c["count_price"] > 0:
            region_data[region]["avg_price_m2"] = c["sum_price"] / c["count_price"]
        if c["count_rent"] > 0:
            region_data[region]["avg_rent_m2"] = c["sum_rent"] / c["count_rent"]


# ------------------------------------------
# NORMALIZATION
# ------------------------------------------

def normalize_region_data(region_data):

    metrics = [
        "population_young",
        "population_working",
        "population_old"
    ]

    max_values = {m: max(region[m] for region in region_data.values()) for m in metrics}

    normalized = {}

    for region_name, region in region_data.items():
        normalized[region_name] = {}
        for m in metrics:
            max_val = max_values[m]
            normalized[region_name][m] = region[m] / max_val if max_val else 0

    return normalized
