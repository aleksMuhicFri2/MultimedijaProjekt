import unicodedata
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
