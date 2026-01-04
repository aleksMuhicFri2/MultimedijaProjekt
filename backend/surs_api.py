import requests
import logging

logger = logging.getLogger(__name__)

SURS_BASE_URL = "https://pxweb.stat.si/SiStatData/api/v1/sl/Data"


def fetch_px(table_id, query=None):
<<<<<<< HEAD
    url = f"{SURS_BASE_URL}/{table_id}"
=======
    url = f"{BASE_URL}/{table_id}"
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881

    body = {
        "query": query or [],
        "response": {"format": "JSON"}
    }

    res = requests.post(url, json=body)

    if not res.ok:
        print("SURS API ERROR:", res.text)
        return None

    return res.json()


def get_population_per_obcina():
    """
    Fetch population by age groups and area data from SURS API.
    """
    logger.info("=" * 60)
    logger.info("FETCHING DATA FROM SURS API")
    logger.info("=" * 60)
    
    # Population by age groups endpoint
    pop_url = f"{SURS_BASE_URL}/05_prebivalstvo/05_prebivalstvo/05_05C10_prebivalstvo_obcine/05_05C20_prebivalstvo_obcine.px"
    
    try:
        # 1. Fetch population data by age groups
        logger.info("Step 1: Fetching population data...")
        pop_response = requests.post(
            pop_url,
            json={
                "query": [
                    {
                        "code": "Starostne skupine",
                        "selection": {
                            "filter": "item",
                            "values": ["0-14", "15-64", "65+"]
                        }
                    }
                ],
                "response": {"format": "json-stat2"}
            },
            timeout=30
        )
        pop_response.raise_for_status()
        pop_data = pop_response.json()
        
        logger.info("✓ Population data received")
        
        # Parse population data
        result = {}
        
        if "dimension" in pop_data and "value" in pop_data:
            dimensions = pop_data["dimension"]
            values = pop_data["value"]
            
            if "Občine" in dimensions:
                municipalities = dimensions["Občine"]["category"]
                muni_codes = list(municipalities["index"].keys())
                muni_labels = municipalities["label"]
                
                logger.info(f"✓ Found {len(muni_codes)} municipalities")
                
                if "Starostne skupine" in dimensions:
                    age_groups = dimensions["Starostne skupine"]["category"]
                    age_codes = list(age_groups["index"].keys())
                    
                    n_municipalities = len(muni_codes)
                    n_age_groups = len(age_codes)
                    
                    # Initialize result structure
                    for code in muni_codes:
                        result[code] = {
                            "code": code,
                            "name": muni_labels.get(code, ""),
                            "population_young": 0,
                            "population_working": 0,
                            "population_old": 0,
                            "area_km2": None
                        }
                    
                    # Parse values
                    for muni_idx, muni_code in enumerate(muni_codes):
                        for age_idx, age_code in enumerate(age_codes):
                            value_idx = age_idx * n_municipalities + muni_idx
                            
                            if value_idx < len(values) and values[value_idx] is not None:
                                pop_value = values[value_idx]
                                
                                if age_code == "0-14":
                                    result[muni_code]["population_young"] = int(pop_value)
                                elif age_code == "15-64":
                                    result[muni_code]["population_working"] = int(pop_value)
                                elif age_code == "65+":
                                    result[muni_code]["population_old"] = int(pop_value)
        
        logger.info("✓ Population data parsed")
        
        # 2. Fetch area data from SURS
        logger.info("Step 2: Fetching area data...")
        area_url = f"{SURS_BASE_URL}/02_prebivalstvo/02002_Prebivalstvo_regije_obcine/02002_prebivalstvo.px"
<<<<<<< HEAD

=======
        
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
        try:
            area_response = requests.post(
                area_url,
                json={
                    "query": [
                        {
                            "code": "MERITVE",
<<<<<<< HEAD
                            "selection": {"filter": "item", "values": ["1118"]}
=======
                            "selection": {
                                "filter": "item",
                                "values": ["1118"]  # Area in km2
                            }
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
                        }
                    ],
                    "response": {"format": "json-stat2"}
                },
                timeout=30
            )
<<<<<<< HEAD

=======
            
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
            if area_response.status_code == 200:
                area_data = area_response.json()
                
                if "dimension" in area_data and "value" in area_data:
                    if "Občine" in area_data["dimension"]:
                        area_municipalities = area_data["dimension"]["Občine"]["category"]
                        area_codes = list(area_municipalities["index"].keys())
                        area_values = area_data["value"]
                        
                        matched_areas = 0
                        for i, code in enumerate(area_codes):
                            if i < len(area_values) and area_values[i] is not None:
                                if code in result:
                                    result[code]["area_km2"] = float(area_values[i])
                                    matched_areas += 1
                                    if matched_areas <= 3:
                                        logger.info(f"  Set area for {code}: {result[code]['area_km2']} km²")
                        
                        logger.info(f"✓ Matched area for {matched_areas} municipalities from SURS")
            else:
                logger.warning(f"Area API returned status {area_response.status_code}")
<<<<<<< HEAD

        except Exception as e:
            logger.warning(f"Failed to fetch area from SURS: {e}")
            logger.warning("No static fallback area data will be used; area_km2 will remain null.")

=======
                
        except Exception as e:
            logger.warning(f"Failed to fetch area from SURS: {e}")
            
            # Fallback: Use hardcoded area data for major municipalities
            logger.info("Using fallback area data...")
            fallback_areas = {
                "061": 275.0,  # Ljubljana
                "070": 147.5,  # Maribor
                "085": 236.0,  # Novo mesto
                "050": 303.2,  # Koper
                "011": 94.9,   # Celje
                "052": 151.0,  # Kranj
                "143": 51.5,   # Zagorje ob Savi
                # Add more as needed
            }
            
            for code, area in fallback_areas.items():
                if code in result:
                    result[code]["area_km2"] = area
                    logger.info(f"  Set fallback area for {code}: {area} km²")
        
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
        result_list = list(result.values())
        
        # Final statistics
        with_area = sum(1 for r in result_list if r.get("area_km2") is not None)
        logger.info("=" * 60)
        logger.info(f"RESULT: {len(result_list)} municipalities")
        logger.info(f"  With population: {len(result_list)}")
        logger.info(f"  With area: {with_area}")
        logger.info("=" * 60)
        
        # Show samples
        for i, entry in enumerate(result_list[:3]):
            logger.info(f"Sample {i+1}: code={entry['code']}, pop_total={entry['population_young']+entry['population_working']+entry['population_old']}, area={entry['area_km2']}")
        
        return result_list
        
    except Exception as e:
        logger.error(f"Failed to fetch SURS data: {e}", exc_info=True)
        return []