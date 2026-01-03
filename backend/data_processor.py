import logging
import pandas as pd
from municipality_codes import MUNICIPALITY_CODE_MAP
from name_utils import normalize_name

logger = logging.getLogger(__name__)

class Municipality:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.region = None
        
        # Population data - three age segments
        self.population_young = None
        self.population_working = None
        self.population_old = None
        self.population_total = None
        self.population_density = None
        self.area_km2 = None
        
        # Price data
        self.prices = {}
        self.rent = {}
        
        # IOZ data
        self.ioz_data = {}
        
        # Location
        self.latitude = None
        self.longitude = None
        
        # Weather history
        self.weather_history = []
        self.weather_score = None
        
        # Demographics
        self.demographics = {}

    def to_dict(self):
        # Extract flattened price data
        result = {
            "code": self.code,
            "name": self.name,
            "region": self.region,
            "population_young": self.population_young,
            "population_working": self.population_working,
            "population_old": self.population_old,
            "population_total": self.population_total,
            "population_density": self.population_density,
            "area_km2": self.area_km2,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "weather_history": self.weather_history,
            "weather_score": self.weather_score,
            "demographics": self.demographics
        }
        
        # Flatten prices
        if self.prices:
            if 'apartment' in self.prices:
                result['avg_price_m2_apartment'] = self.prices['apartment'].get('avg_price_m2')
                result['median_price_m2_apartment'] = self.prices['apartment'].get('median_price_m2')
                result['deals_sale_apartment'] = self.prices['apartment'].get('deals_count')
            
            if 'house' in self.prices:
                result['avg_price_m2_house'] = self.prices['house'].get('avg_price_m2')
                result['median_price_m2_house'] = self.prices['house'].get('median_price_m2')
                result['deals_sale_house'] = self.prices['house'].get('deals_count')
        
        # Flatten rent
        if self.rent:
            result['avg_rent_m2'] = self.rent.get('avg_rent_m2')
            result['median_rent_m2'] = self.rent.get('median_rent_m2')
            result['deals_rent'] = self.rent.get('deals_count_rent')
        
        # Flatten IOZ
        if self.ioz_data:
            result['insured_total'] = self.ioz_data.get('total_insured')
            result['insured_with_ioz'] = self.ioz_data.get('with_ioz')
            result['insured_without_ioz'] = self.ioz_data.get('without_ioz')
            result['ioz_ratio'] = self.ioz_data.get('ioz_coverage')
        
        return result

def init_municipalities():
    """Initialize municipality objects from code map."""
    municipalities = {}
    for code, name in MUNICIPALITY_CODE_MAP.items():
        if code == "0":
            continue
        municipalities[code] = Municipality(code, name)
    return municipalities

def process_population(pop_data, municipalities):
    """
    Process population data from SURS API.
    Expected format: list of dicts with 'code', 'population_young', 'population_working', 'population_old', 'area_km2'
    """
    logger.info("Processing population data...")
    matched = 0
    area_count = 0
    
    for entry in pop_data:
        code = str(entry.get("code", "")).strip()
        
        if code in municipalities:
            muni = municipalities[code]
            
            # Set age segment populations
            try:
                muni.population_young = int(entry.get("population_young", 0) or 0)
                muni.population_working = int(entry.get("population_working", 0) or 0)
                muni.population_old = int(entry.get("population_old", 0) or 0)
                
                # Calculate total population
                muni.population_total = muni.population_young + muni.population_working + muni.population_old
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid population data for {code}: {e}")
            
            # Set area
            area_km2 = entry.get("area_km2")
            if area_km2 is not None:
                try:
                    muni.area_km2 = float(area_km2)
                    area_count += 1
                    if area_count <= 3:  # Log first 3 for debugging
                        logger.info(f"  Set area for {code} ({muni.name}): {muni.area_km2} km²")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid area for {code}: {area_km2}")
            
            # Calculate density
            if muni.population_total and muni.area_km2 and muni.area_km2 > 0:
                muni.population_density = round(muni.population_total / muni.area_km2, 2)
            
            matched += 1
        else:
            logger.debug(f"Population data for unknown code: {code}")
    
    logger.info(f"Matched population data for {matched}/{len(municipalities)} municipalities")
    logger.info(f"Got area data for {area_count} municipalities from SURS")

def process_prices(prices_by_muni, rent_by_muni, municipalities):
    """Process real estate price data."""
    logger.info("Processing price data...")
    
    prices_matched = 0
    rent_matched = 0
    
    for code, muni in municipalities.items():
        name_norm = normalize_name(muni.name)
        
        # Match prices
        if name_norm in prices_by_muni:
            muni.prices = prices_by_muni[name_norm]
            prices_matched += 1
            if prices_matched <= 3:  # Log first 3
                logger.info(f"  Matched prices for {muni.name}: {list(muni.prices.keys())}")
        
        # Match rent
        if name_norm in rent_by_muni:
            muni.rent = rent_by_muni[name_norm]
            rent_matched += 1
            if rent_matched <= 3:  # Log first 3
                logger.info(f"  Matched rent for {muni.name}: {muni.rent}")
    
    logger.info(f"Matched prices for {prices_matched} municipalities")
    logger.info(f"Matched rent for {rent_matched} municipalities")

def process_ioz(ioz_df, municipalities):
    """Process IOZ (infrastructure) data."""
    logger.info("Processing IOZ data...")
    
    for _, row in ioz_df.iterrows():
        obcina = normalize_name(str(row.get("OBCINA", "")))
        
        # Find matching municipality
        for code, muni in municipalities.items():
            if normalize_name(muni.name) == obcina:
                muni.ioz_data = {
                    k: v for k, v in row.to_dict().items() 
                    if k != "OBCINA" and pd.notna(v)
                }
                break

def process_lat_long(coords_list, municipalities):
    """Process latitude/longitude coordinates."""
    logger.info("Processing coordinates...")
    
    matched_coords = 0
    
    # Log first entry to see structure
    if coords_list:
        logger.info(f"Sample coords entry: {coords_list[0]}")
        logger.info(f"Coords columns available: {list(coords_list[0].keys())}")
    
    for entry in coords_list:
        code = str(entry.get("code", "")).strip()
        
        if code in municipalities:
            muni = municipalities[code]
            
            # Set coordinates (CSV has 'lat' and 'lng', not 'latitude' and 'longitude')
            if entry.get("lat"):
                muni.latitude = float(entry.get("lat"))
                matched_coords += 1
            if entry.get("lng"):
                muni.longitude = float(entry.get("lng"))
    
    logger.info(f"Matched coordinates for {matched_coords} municipalities")

def process_history(history_list, municipalities):
    """Process historical weather data."""
    logger.info("Processing weather history...")
    
    for entry in history_list:
        code = str(entry.get("code", "")).strip()
        
        if code in municipalities:
            muni = municipalities[code]
            
            # Remove code from entry before storing
            history_entry = {k: v for k, v in entry.items() if k != "code"}
            muni.weather_history.append(history_entry)

def calculate_weather_scores(municipalities):
    """Calculate normalized weather scores."""
    logger.info("Calculating weather scores...")
    
    all_temps = []
    all_precips = []
    
    # Collect all values for normalization
    for muni in municipalities.values():
        if muni.weather_history:
            for record in muni.weather_history:
                if "temperature" in record:
                    all_temps.append(record["temperature"])
                if "precipitation" in record:
                    all_precips.append(record["precipitation"])
    
    if not all_temps or not all_precips:
        logger.warning("No weather data available for scoring")
        return
    
    temp_min, temp_max = min(all_temps), max(all_temps)
    precip_min, precip_max = min(all_precips), max(all_precips)
    
    # Calculate scores
    for muni in municipalities.values():
        if not muni.weather_history:
            continue
        
        scores = []
        for record in muni.weather_history:
            temp = record.get("temperature")
            precip = record.get("precipitation")
            
            if temp is not None and precip is not None:
                # Normalize (higher temp = better, lower precip = better)
                temp_score = (temp - temp_min) / (temp_max - temp_min) if temp_max > temp_min else 0.5
                precip_score = 1 - ((precip - precip_min) / (precip_max - precip_min)) if precip_max > precip_min else 0.5
                
                # Weighted average
                scores.append(0.6 * temp_score + 0.4 * precip_score)
        
        if scores:
            muni.weather_score = round(sum(scores) / len(scores) * 100, 2)

def calculate_demographics(municipalities):
    """Calculate demographic statistics."""
    logger.info("Calculating demographics...")
    
    for muni in municipalities.values():
        if muni.population_total and muni.area_km2:
            # Calculate percentages
            young_pct = round((muni.population_young / muni.population_total) * 100, 1) if muni.population_total else 0
            working_pct = round((muni.population_working / muni.population_total) * 100, 1) if muni.population_total else 0
            old_pct = round((muni.population_old / muni.population_total) * 100, 1) if muni.population_total else 0
            
            muni.demographics = {
                "population_total": muni.population_total,
                "population_young": muni.population_young,
                "population_working": muni.population_working,
                "population_old": muni.population_old,
                "young_percentage": young_pct,
                "working_percentage": working_pct,
                "old_percentage": old_pct,
                "area_km2": muni.area_km2,
                "density": muni.population_density,
                "classification": classify_density(muni.population_density) if muni.population_density else "Unknown"
            }

def classify_density(density):
    """Classify municipality by population density."""
    if density < 50:
        return "Rural"
    elif density < 150:
        return "Semi-rural"
    elif density < 500:
        return "Urban"
    else:
        return "Highly Urban"