<<<<<<< HEAD
"""
Slovenian Real Estate Search Engine

This module provides:
1. Multi-criteria search and filtering
2. Weighted scoring algorithm with adjustable weights
3. Distance/commute calculations using Google Maps API (with Haversine fallback)
4. Percentile-based rankings
5. Data normalization for spider graph visualization

All scores are normalized to 0-100 scale for fair comparison.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import math
import time

logger = logging.getLogger(__name__)

# Try to import Google Maps client
try:
    from google_maps import gmaps
    GOOGLE_MAPS_AVAILABLE = True
    logger.info("Google Maps API client loaded successfully")
except ImportError:
    GOOGLE_MAPS_AVAILABLE = False
    gmaps = None
    logger.warning("Google Maps API client not available, using Haversine fallback")


class CitySearchEngine:
    """
    Advanced city search and ranking system for Slovenian municipalities.
    
    Scoring Categories:
    1. Affordability - Lower prices = higher score
    2. Market Activity - More deals = higher score (indicates liquid market)
    3. Population Vitality - Higher working-age % = higher score
    4. Healthcare Coverage - Higher IOZ ratio = higher score
    5. Commute Score - Shorter commute = higher score (when workplace set)
    6. Housing Diversity - More property types available = higher score
    
    All scores use min-max normalization to 0-100 scale:
    score = ((value - min) / (max - min)) * 100
    
    For inverse metrics (lower is better like price):
    score = ((max - value) / (max - min)) * 100
    """
    
    # Major Slovenian cities for commute calculations (lat, lng)
    MAJOR_CITIES = {
        "Ljubljana": (46.0569, 14.5058),
        "Maribor": (46.5547, 15.6459),
        "Celje": (46.2397, 15.2677),
        "Kranj": (46.2428, 14.3555),
        "Koper": (45.5480, 13.7302),
        "Novo mesto": (45.8011, 15.1710),
        "Nova Gorica": (45.9550, 13.6493),
        "Murska Sobota": (46.6581, 16.1610),
    }
    
    # Life stage profiles for demographic matching
    LIFE_STAGE_PROFILES = {
        'student': {
            'ideal_demographics': {'young': 0.20, 'working': 0.70, 'old': 0.10},
            'priority_weights': {'affordability': 15, 'market_activity': 5, 'healthcare': 3}
        },
        'young_professional': {
            'ideal_demographics': {'young': 0.15, 'working': 0.70, 'old': 0.15},
            'priority_weights': {'affordability': 10, 'market_activity': 8, 'healthcare': 5}
        },
        'young_family': {
            'ideal_demographics': {'young': 0.20, 'working': 0.65, 'old': 0.15},
            'priority_weights': {'affordability': 8, 'market_activity': 7, 'healthcare': 10}
        },
        'established_family': {
            'ideal_demographics': {'young': 0.18, 'working': 0.60, 'old': 0.22},
            'priority_weights': {'affordability': 6, 'market_activity': 6, 'healthcare': 8}
        },
        'retiree': {
            'ideal_demographics': {'young': 0.10, 'working': 0.50, 'old': 0.40},
            'priority_weights': {'affordability': 8, 'market_activity': 4, 'healthcare': 15}
        }
    }
    
    # Default scoring weights (sum = 100 for easy percentage interpretation)
    DEFAULT_WEIGHTS = {
        'affordability': 25,      # Price affordability
        'market_activity': 15,    # Number of deals (liquidity)
        'population_vitality': 10, # Working-age population %
        'healthcare': 15,         # IOZ coverage
        'commute': 20,            # Distance to workplace (if set)
        'housing_diversity': 15,  # Variety of property types
    }
    
    # Rush hour multipliers for realistic commute estimates
    RUSH_HOUR_MULTIPLIER = 1.35  # 35% longer during rush hour
    
    # Rate limiting for Google Maps API
    GMAPS_CALLS_PER_SEARCH = 10  # Max API calls per search to preserve credits
    GMAPS_DELAY_SECONDS = 0.1   # Delay between API calls
    
    def __init__(self):
        self.life_stage_profiles = self.LIFE_STAGE_PROFILES
        self._stats_cache = {}
        self._commute_cache = {}  # Cache for Google Maps commute results
        self._gmaps_calls_this_search = 0  # Track API calls per search
    
    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def _num(self, v) -> Optional[float]:
        """Safely convert to float, return None for invalid values."""
        if v is None:
            return None
        try:
            n = float(v)
            return n if math.isfinite(n) else None
        except (ValueError, TypeError):
            return None
    
    def _code3(self, v) -> Optional[str]:
        """Normalize municipality code to 3-digit format (e.g., '61' -> '061')."""
        if v is None:
            return None
        s = str(v).strip()
        return s.zfill(3) if s else None
    
    def _clamp(self, value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Clamp value to specified range."""
        return max(min_val, min(max_val, value))
    
    def _get_coords(self, city: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract coordinates from city dict, supporting multiple field names."""
        lat = self._num(city.get("latitude")) or self._num(city.get("lat"))
        lon = self._num(city.get("longitude")) or self._num(city.get("lon")) or self._num(city.get("lng"))
        return lat, lon
    
    # =========================================================================
    # DISTANCE & COMMUTE CALCULATIONS (with Google Maps API)
    # =========================================================================
    
    def _reset_gmaps_counter(self):
        """Reset the API call counter at the start of each search."""
        self._gmaps_calls_this_search = 0
    
    def _can_call_gmaps(self) -> bool:
        """Check if we can make another Google Maps API call."""
        return (
            GOOGLE_MAPS_AVAILABLE and 
            gmaps is not None and 
            self._gmaps_calls_this_search < self.GMAPS_CALLS_PER_SEARCH
        )
    
    def _get_commute_cache_key(self, origin_code: str, dest_code: str, has_car: bool) -> str:
        """Generate cache key for commute calculations."""
        mode = "driving" if has_car else "transit"
        return f"{origin_code}_{dest_code}_{mode}"
    
    def calculate_commute_google_maps(self, origin_name: str, dest_name: str, 
                                       has_car: bool) -> Optional[Dict]:
        """
        Calculate commute using Google Maps Distance Matrix API.
        Rate-limited to preserve API credits.
        """
        if not self._can_call_gmaps():
            logger.debug(f"Skipping Google Maps API call (limit reached or unavailable)")
            return None
        
        try:
            mode = "driving" if has_car else "transit"
            
            # Add ", Slovenia" suffix for better geocoding
            origin_query = f"{origin_name}, Slovenia" if "Slovenia" not in origin_name else origin_name
            dest_query = f"{dest_name}, Slovenia" if "Slovenia" not in dest_name else dest_name
            
            # Rate limiting delay
            time.sleep(self.GMAPS_DELAY_SECONDS)
            
            self._gmaps_calls_this_search += 1
            logger.info(f"Google Maps API call #{self._gmaps_calls_this_search}: {origin_name} -> {dest_name}")
            
            result = gmaps.distance_matrix(
                origins=[origin_query],
                destinations=[dest_query],
                mode=mode
            )
            
            if not result or not result.get("rows"):
                return None
            
            element = result["rows"][0]["elements"][0]
            
            if element.get("status") != "OK":
                logger.warning(f"Google Maps returned status {element.get('status')} for {origin_name} -> {dest_name}")
                return None
            
            distance_m = element["distance"]["value"]
            duration_s = element["duration"]["value"]
            
            # Add rush hour buffer (15% for driving, 10% for transit)
            rush_hour_factor = 1.15 if has_car else 1.10
            adjusted_duration = duration_s * rush_hour_factor
            
            return {
                "distance_km": round(distance_m / 1000, 2),
                "commute_minutes": round(adjusted_duration / 60, 1),
                "source": "google_maps",
                "mode": mode
            }
            
        except Exception as e:
            logger.error(f"Google Maps API error for {origin_name} -> {dest_name}: {e}")
            return None
    
    def calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate straight-line distance using Haversine formula."""
        R = 6371.0  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def estimate_driving_distance_km(self, straight_line_km: float) -> float:
        """Estimate actual driving distance from straight-line distance."""
        if straight_line_km < 10:
            return straight_line_km * 1.3
        elif straight_line_km < 50:
            return straight_line_km * 1.4
        else:
            return straight_line_km * 1.5
    
    def estimate_commute_time_minutes(self, distance_km: float, has_car: bool, rush_hour: bool = True) -> float:
        """Estimate commute time based on distance and transport mode."""
        if distance_km <= 0:
            return 5.0
        
        if has_car:
            if distance_km < 10:
                avg_speed = 35
                overhead = 5
            elif distance_km < 30:
                avg_speed = 50
                overhead = 5
            elif distance_km < 60:
                avg_speed = 65
                overhead = 5
            else:
                avg_speed = 80
                overhead = 10
            
            base_time = (distance_km / avg_speed) * 60 + overhead
        else:
            if distance_km < 10:
                avg_speed = 20
                overhead = 15
            elif distance_km < 30:
                avg_speed = 30
                overhead = 25
            elif distance_km < 60:
                avg_speed = 45
                overhead = 30
            else:
                avg_speed = 55
                overhead = 40
            
            base_time = (distance_km / avg_speed) * 60 + overhead
            if distance_km > 30:
                base_time *= 1.2
        
        if rush_hour:
            base_time *= self.RUSH_HOUR_MULTIPLIER
        
        return round(base_time, 1)
    
    def calculate_commute_to_city(self, city: Dict, workplace_city: Dict, has_car: bool, 
                                   use_gmaps: bool = True) -> Optional[Dict]:
        """
        Calculate complete commute information between two municipalities.
        Uses Google Maps API if available and allowed, falls back to Haversine.
        """
        city_code = self._code3(city.get("code"))
        workplace_code = self._code3(workplace_city.get("code"))
        city_name = city.get("name", "")
        workplace_name = workplace_city.get("name", "")
        
        # Same city check
        if city_code == workplace_code:
            return {
                "straight_line_km": 0,
                "distance_km": 0,
                "commute_minutes": 5,
                "daily_commute": 10,
                "one_way_time": 5,
                "daily_time": 10,
                "workplace_name": workplace_name,
                "is_same_city": True,
                "source": "same_city"
            }
        
        # Check cache first
        cache_key = self._get_commute_cache_key(city_code or "", workplace_code or "", has_car)
        if cache_key in self._commute_cache:
            cached = self._commute_cache[cache_key].copy()
            cached["workplace_name"] = workplace_name
            return cached
        
        # Try Google Maps API first (only if allowed and we have city names)
        if use_gmaps and city_name and workplace_name and self._can_call_gmaps():
            gmaps_result = self.calculate_commute_google_maps(city_name, workplace_name, has_car)
            
            if gmaps_result:
                result = {
                    "distance_km": gmaps_result["distance_km"],
                    "commute_minutes": gmaps_result["commute_minutes"],
                    "daily_commute": round(gmaps_result["commute_minutes"] * 2, 1),
                    "one_way_time": gmaps_result["commute_minutes"],
                    "daily_time": round(gmaps_result["commute_minutes"] * 2, 1),
                    "workplace_name": workplace_name,
                    "is_same_city": False,
                    "source": "google_maps"
                }
                
                # Cache the result
                cache_entry = result.copy()
                del cache_entry["workplace_name"]
                self._commute_cache[cache_key] = cache_entry
                
                return result
        
        # Fallback to Haversine calculation
        clat, clon = self._get_coords(city)
        wlat, wlon = self._get_coords(workplace_city)
        
        if None in (clat, clon, wlat, wlon):
            # If no coordinates AND no Google Maps, we can still estimate using city names
            # But for now, return a default estimate based on typical distances
            logger.warning(f"Missing coordinates for {city_name} or {workplace_name}, using default estimate")
            
            # Default estimate: 30km, 35 minutes (average for Slovenia)
            default_distance = 30.0
            default_commute = 35.0 if has_car else 55.0
            
            return {
                "distance_km": default_distance,
                "commute_minutes": default_commute,
                "daily_commute": round(default_commute * 2, 1),
                "one_way_time": default_commute,
                "daily_time": round(default_commute * 2, 1),
                "workplace_name": workplace_name,
                "is_same_city": False,
                "source": "default_estimate"
            }
        
        straight_line = self.calculate_distance_km(clat, clon, wlat, wlon)
        driving_distance = self.estimate_driving_distance_km(straight_line)
        commute_time = self.estimate_commute_time_minutes(driving_distance, has_car)
        
        result = {
            "straight_line_km": round(straight_line, 2),
            "distance_km": round(driving_distance, 2),
            "commute_minutes": round(commute_time, 1),
            "daily_commute": round(commute_time * 2, 1),
            "one_way_time": round(commute_time, 1),
            "daily_time": round(commute_time * 2, 1),
            "workplace_name": workplace_name,
            "is_same_city": False,
            "source": "haversine_estimate"
        }
        
        # Cache the result
        cache_entry = result.copy()
        del cache_entry["workplace_name"]
        self._commute_cache[cache_key] = cache_entry
        
        return result
    
    # =========================================================================
    # DATA EXTRACTION HELPERS
    # =========================================================================
    
    def _get_rent_m2(self, city: Dict) -> Optional[float]:
        """Get rent price per m², supporting nested and flat structures."""
        # Nested: city["rent"]["avg_rent_m2"]
        rent = city.get("rent") or {}
        v = self._num(rent.get("avg_rent_m2"))
        if v is not None:
            return v
        # Flat: city["avg_rent_m2"]
        return self._num(city.get("avg_rent_m2"))
    
    def _get_rent_deals(self, city: Dict) -> int:
        """Get number of rent deals."""
        rent = city.get("rent") or {}
        v = self._num(rent.get("deals_count_rent"))
        if v is not None:
            return int(v)
        v = self._num(city.get("deals_rent"))
        return int(v) if v else 0
    
    def _get_price_m2(self, city: Dict, property_type: str) -> Optional[float]:
        """Get purchase price per m² for given property type."""
        # Nested structure
        prices = city.get("prices") or {}
        if property_type in prices:
            v = self._num(prices[property_type].get("avg_price_m2"))
            if v is not None:
                return v
        
        # Flat structure
        if property_type == "apartment":
            return self._num(city.get("avg_price_m2_apartment"))
        elif property_type == "house":
            return self._num(city.get("avgPrice_m2_house"))
        return None
    
    def _get_sale_deals(self, city: Dict, property_type: str) -> int:
        """Get number of sales for given property type."""
        prices = city.get("prices") or {}
        if property_type in prices:
            v = self._num(prices[property_type].get("deals_count"))
            if v is not None:
                return int(v)
        
        if property_type == "apartment":
            v = self._num(city.get("deals_sale_apartment"))
        elif property_type == "house":
            v = self._num(city.get("deals_sale_house"))
        else:
            v = None
        return int(v) if v else 0
    
    def _get_total_deals(self, city: Dict) -> int:
        """Get total number of real estate deals (rent + sales)."""
        return (
            self._get_rent_deals(city) +
            self._get_sale_deals(city, "apartment") +
            self._get_sale_deals(city, "house")
        )
    
    def _get_population_stats(self, city: Dict) -> Dict:
        """Extract population statistics."""
        young = self._num(city.get("population_young")) or 0
        working = self._num(city.get("population_working")) or 0
        old = self._num(city.get("population_old")) or 0
        total = young + working + old
        
        if total <= 0:
            return {"total": 0, "young": 0, "working": 0, "old": 0, 
                    "young_pct": 0, "working_pct": 0, "old_pct": 0}
        
        return {
            "total": total,
            "young": young,
            "working": working,
            "old": old,
            "young_pct": round((young / total) * 100, 1),
            "working_pct": round((working / total) * 100, 1),
            "old_pct": round((old / total) * 100, 1)
        }
    
    def _get_ioz_ratio(self, city: Dict) -> Optional[float]:
        """Get IOZ (healthcare) coverage ratio (0-1 scale)."""
        ratio = self._num(city.get("ioz_ratio"))
        if ratio is not None:
            # Ensure it's in 0-1 range
            return self._clamp(ratio, 0, 1)
        return None
    
    # =========================================================================
    # STATISTICS CALCULATION FOR NORMALIZATION
    # =========================================================================
    
    def _calculate_dataset_stats(self, cities: List[Dict], criteria: Dict) -> Dict:
        """
        Calculate min/max/avg statistics for normalization.
        
        This pre-computes bounds for all scoring metrics so individual
        city scores can be normalized to 0-100 scale.
        """
        stats = {
            "rent_m2": {"values": [], "min": None, "max": None},
            "apt_price_m2": {"values": [], "min": None, "max": None},
            "house_price_m2": {"values": [], "min": None, "max": None},
            "total_deals": {"values": [], "min": None, "max": None},
            "population": {"values": [], "min": None, "max": None},
            "working_pct": {"values": [], "min": None, "max": None},
            "ioz_ratio": {"values": [], "min": None, "max": None},
            "commute": {"values": [], "min": None, "max": None},
        }
        
        # Get workplace for commute calculations
        workplace_city = None
        workplace_code = self._code3(criteria.get("workplace_city_code"))
        if workplace_code:
            workplace_city = next(
                (c for c in cities if self._code3(c.get("code")) == workplace_code), None
            )
        
        has_car = bool(criteria.get("has_car", False))
        
        for city in cities:
            # Price metrics
            rent = self._get_rent_m2(city)
            if rent: stats["rent_m2"]["values"].append(rent)
            
            apt = self._get_price_m2(city, "apartment")
            if apt: stats["apt_price_m2"]["values"].append(apt)
            
            house = self._get_price_m2(city, "house")
            if house: stats["house_price_m2"]["values"].append(house)
            
            # Market activity
            deals = self._get_total_deals(city)
            if deals > 0: stats["total_deals"]["values"].append(deals)
            
            # Population
            pop_stats = self._get_population_stats(city)
            if pop_stats["total"] > 0:
                stats["population"]["values"].append(pop_stats["total"])
                stats["working_pct"]["values"].append(pop_stats["working_pct"])
            
            # Healthcare
            ioz = self._get_ioz_ratio(city)
            if ioz is not None: stats["ioz_ratio"]["values"].append(ioz)
            
            # Commute (if workplace set)
            if workplace_city:
                commute_info = self.calculate_commute_to_city(city, workplace_city, has_car)
                if commute_info:
                    stats["commute"]["values"].append(commute_info["commute_minutes"])
        
        # Calculate min/max for each metric
        for key, data in stats.items():
            if data["values"]:
                data["min"] = min(data["values"])
                data["max"] = max(data["values"])
                data["avg"] = sum(data["values"]) / len(data["values"])
        
        return stats
    
    # =========================================================================
    # NORMALIZATION FUNCTIONS
    # =========================================================================
    
    def _normalize_score(self, value: float, min_val: float, max_val: float, 
                         inverse: bool = False) -> float:
        """
        Normalize a value to 0-100 scale using min-max normalization.
        
        Formula (normal): score = ((value - min) / (max - min)) * 100
        Formula (inverse): score = ((max - value) / (max - min)) * 100
        
        Args:
            value: The value to normalize
            min_val: Minimum value in dataset
            max_val: Maximum value in dataset
            inverse: If True, lower values get higher scores
            
        Returns:
            Normalized score between 0 and 100
        """
        if max_val == min_val:
            return 50.0  # No variance, return middle score
        
        if inverse:
            score = ((max_val - value) / (max_val - min_val)) * 100
        else:
            score = ((value - min_val) / (max_val - min_val)) * 100
        
        return self._clamp(score, 0, 100)
    
    def _normalize_with_percentile(self, value: float, values: List[float], 
                                   inverse: bool = False) -> float:
        """
        Normalize using percentile ranking (more robust to outliers).
        
        Formula: percentile = (count of values <= target) / total count * 100
        
        Args:
            value: The value to find percentile for
            values: All values in the dataset
            inverse: If True, lower values get higher scores
        """
        if not values:
            return 50.0
        
        sorted_vals = sorted(values)
        count_below = sum(1 for v in sorted_vals if v <= value)
        percentile = (count_below / len(sorted_vals)) * 100
        
        return (100 - percentile) if inverse else percentile
    
    # =========================================================================
    # INDIVIDUAL SCORING FUNCTIONS
    # =========================================================================
    
    def score_affordability(self, city: Dict, criteria: Dict, stats: Dict) -> Optional[float]:
        """
        Calculate affordability score (0-100, higher = more affordable).
        
        Logic:
        1. Get relevant price based on search_type (rent vs purchase)
        2. Calculate estimated total cost = price_m2 * desired_m2
        3. Compare to budget and dataset range
        4. Lower prices relative to budget and market = higher score
        
        Formula: 
        - Base score from market position (percentile, inverse)
        - Bonus for being under budget
        """
        search_type = criteria.get("search_type", "rent")
        desired_m2 = criteria.get("desired_m2", 60)
        
        if search_type == "rent":
            price_m2 = self._get_rent_m2(city)
            stat_key = "rent_m2"
            budget = self._num(criteria.get("max_monthly_rent"))
        else:
            property_type = criteria.get("property_type", "apartment")
            price_m2 = self._get_price_m2(city, property_type)
            stat_key = "apt_price_m2" if property_type == "apartment" else "house_price_m2"
            budget = self._num(criteria.get("max_purchase_price"))
        
        if price_m2 is None:
            return None
        
        # Get market stats
        stat = stats.get(stat_key, {})
        if not stat.get("values"):
            return None
        
        # Calculate percentile score (lower price = higher score)
        market_score = self._normalize_with_percentile(price_m2, stat["values"], inverse=True)
        
        # Budget bonus (up to 20 points if well under budget)
        if budget:
            total_cost = price_m2 * desired_m2
            if total_cost <= budget:
                budget_ratio = total_cost / budget
                budget_bonus = (1 - budget_ratio) * 20  # 0-20 points bonus
                market_score = min(100, market_score + budget_bonus)
        
        return round(market_score, 2)
    
    def score_market_activity(self, city: Dict, stats: Dict) -> Optional[float]:
        """
        Calculate market activity score (0-100, higher = more active market).
        
        Logic: More deals indicates:
        - Higher liquidity (easier to buy/sell/rent)
        - More options to choose from
        - Market confidence in the area
        
        Uses percentile ranking for robustness against outliers (Ljubljana).
        """
        total_deals = self._get_total_deals(city)
        
        stat = stats.get("total_deals", {})
        if not stat.get("values"):
            return None
        
        if total_deals == 0:
            return 0.0
        
        return round(self._normalize_with_percentile(total_deals, stat["values"]), 2)
    
    def score_population_vitality(self, city: Dict, criteria: Dict, stats: Dict) -> Optional[float]:
        """
        Calculate population vitality score (0-100).
        
        Factors:
        1. Working-age population percentage (main factor)
        2. Match to life stage preferences (if specified)
        3. Population size (slight bonus for larger communities)
        
        Life stage matching: Compare actual demographics to ideal distribution
        for the selected life stage using L1 distance (lower = better match).
        """
        pop_stats = self._get_population_stats(city)
        if pop_stats["total"] == 0:
            return None
        
        stat = stats.get("working_pct", {})
        
        # Base score from working population percentage
        working_pct = pop_stats["working_pct"]
        if stat.get("values"):
            base_score = self._normalize_with_percentile(working_pct, stat["values"])
        else:
            # Fallback: assume 60% is average, 50-70% normal range
            base_score = self._normalize_score(working_pct, 45, 75, inverse=False)
        
        # Life stage matching bonus (up to 15 points)
        life_stage = criteria.get("life_stage")
        if life_stage and life_stage in self.LIFE_STAGE_PROFILES:
            ideal = self.LIFE_STAGE_PROFILES[life_stage]["ideal_demographics"]
            actual = {
                "young": pop_stats["young_pct"] / 100,
                "working": pop_stats["working_pct"] / 100,
                "old": pop_stats["old_pct"] / 100
            }
            
            # L1 distance (0 = perfect match, 2 = worst case)
            distance = sum(abs(actual[k] - ideal[k]) for k in ["young", "working", "old"])
            match_score = (1 - distance / 2) * 15  # 0-15 bonus
            
            base_score = min(100, base_score + match_score)
        
        return round(base_score, 2)
    
    def score_healthcare(self, city: Dict, stats: Dict) -> Optional[float]:
        """
        Calculate healthcare access score (0-100).
        
        Primary metric: IOZ (Izbrani osebni zdravnik) coverage ratio
        - This indicates % of population with assigned personal doctor
        - Higher coverage = better primary healthcare access
        
        Fallback: Use population size as proxy (larger = more facilities)
        """
        ioz = self._get_ioz_ratio(city)
        
        if ioz is not None:
            # IOZ is already 0-1, convert to 0-100
            return round(ioz * 100, 2)
        
        # Fallback to population-based estimate
        pop_stats = self._get_population_stats(city)
        stat = stats.get("population", {})
        
        if pop_stats["total"] > 0 and stat.get("values"):
            return round(self._normalize_with_percentile(pop_stats["total"], stat["values"]), 2)
        
        return None
    
    def score_commute(self, city: Dict, criteria: Dict, stats: Dict, 
                      workplace_city: Dict = None) -> Optional[float]:
        """
        Calculate commute score (0-100, shorter = better).
        
        Logic:
        1. Calculate estimated commute time to workplace
        2. Compare to max acceptable commute (hard filter already applied)
        3. Score relative to other options and max commute
        
        Scoring tiers:
        - 0-15 min: 100-90 (excellent)
        - 15-30 min: 90-70 (good)
        - 30-45 min: 70-40 (acceptable)
        - 45-60 min: 40-10 (long)
        - 60+ min: 10-0 (very long)
        """
        if not workplace_city:
            return None
        
        has_car = bool(criteria.get("has_car", False))
        commute_info = self.calculate_commute_to_city(city, workplace_city, has_car)
        
        if not commute_info:
            return None
        
        commute_min = commute_info["commute_minutes"]
        max_commute = self._num(criteria.get("max_commute_minutes")) or 60
        
        # Tier-based scoring for more intuitive results
        if commute_min <= 15:
            score = 100 - (commute_min / 15) * 10  # 100-90
        elif commute_min <= 30:
            score = 90 - ((commute_min - 15) / 15) * 20  # 90-70
        elif commute_min <= 45:
            score = 70 - ((commute_min - 30) / 15) * 30  # 70-40
        elif commute_min <= 60:
            score = 40 - ((commute_min - 45) / 15) * 30  # 40-10
        else:
            score = max(0, 10 - ((commute_min - 60) / 30) * 10)  # 10-0
        
        return round(self._clamp(score, 0, 100), 2)
    
    def score_housing_diversity(self, city: Dict) -> float:
        """
        Calculate housing diversity score (0-100).
        
        Measures availability of different property types:
        - Has apartment data: +30 points
        - Has house data: +30 points
        - Has rental data: +30 points
        - Has market activity (>10 deals total): +10 points
        """
        score = 0
        
        if self._get_price_m2(city, "apartment") is not None:
            score += 30
        if self._get_price_m2(city, "house") is not None:
            score += 30
        if self._get_rent_m2(city) is not None:
            score += 30
        if self._get_total_deals(city) >= 10:
            score += 10
        
        return float(score)
    
    # =========================================================================
    # MAIN SCORING FUNCTION
    # =========================================================================
    
    def calculate_all_scores(self, city: Dict, criteria: Dict, stats: Dict,
                             workplace_city: Dict = None) -> Dict[str, Optional[float]]:
        """
        Calculate all category scores for a city.
        
        Returns dict with keys:
        - affordability
        - market_activity
        - population_vitality
        - healthcare
        - commute (None if no workplace)
        - housing_diversity
        """
        return {
            "affordability": self.score_affordability(city, criteria, stats),
            "market_activity": self.score_market_activity(city, stats),
            "population_vitality": self.score_population_vitality(city, criteria, stats),
            "healthcare": self.score_healthcare(city, stats),
            "commute": self.score_commute(city, criteria, stats, workplace_city),
            "housing_diversity": self.score_housing_diversity(city),
        }
    
    def calculate_final_score(self, category_scores: Dict, criteria: Dict) -> float:
        """
        Calculate weighted final score.
        
        Formula: final_score = Σ(score_i * weight_i) / Σ(weight_i)
        
        Only categories with non-None scores contribute.
        User weights override defaults where provided.
        """
        user_weights = criteria.get("weights", {}) or {}
        
        # Start with defaults, override with user weights
        weights = {**self.DEFAULT_WEIGHTS}
        
        # Map old weight names to new ones
        weight_mapping = {
            "affordability": "affordability",
            "demographics": "population_vitality",
            "transportation": "commute",
            "healthcare": "healthcare",
            "price_diversity": "housing_diversity",
            "market_liquidity": "market_activity",
        }
        
        for old_key, new_key in weight_mapping.items():
            if old_key in user_weights:
                weights[new_key] = self._num(user_weights[old_key]) or 0
        
        # If workplace is set, ensure commute has meaningful weight
        if criteria.get("workplace_city_code"):
            weights["commute"] = max(weights.get("commute", 0), 20)
        else:
            weights["commute"] = 0  # No commute score without workplace
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for category, score in category_scores.items():
            if score is None:
                continue
            weight = self._num(weights.get(category, 0)) or 0
            if weight <= 0:
                continue
            
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight <= 0:
            return 0.0
        
        return round(weighted_sum / total_weight, 2)
    
    def calculate_percentile_rank(self, score: float, all_scores: List[float]) -> Dict:
        """
        Calculate percentile rank for a score.
        
        Returns:
            {
                "percentile": 85.5,  # Top X%
                "rank": 15,          # Position
                "total": 100,        # Total cities
                "tier": "top_25"     # Category label
            }
        """
        if not all_scores:
            return {"percentile": 0, "rank": 0, "total": 0, "tier": "unknown"}
        
        sorted_scores = sorted(all_scores, reverse=True)
        rank = sorted_scores.index(score) + 1 if score in sorted_scores else len(sorted_scores)
        percentile = ((len(sorted_scores) - rank + 1) / len(sorted_scores)) * 100
        
        if percentile >= 90:
            tier = "top_10"
        elif percentile >= 75:
            tier = "top_25"
        elif percentile >= 50:
            tier = "top_50"
        else:
            tier = "bottom_50"
        
        return {
            "percentile": round(percentile, 1),
            "rank": rank,
            "total": len(sorted_scores),
            "tier": tier
        }
    
    # =========================================================================
    # FILTERING
    # =========================================================================
    
    def filter_cities(self, cities: List[Dict], criteria: Dict) -> Tuple[List[Dict], Dict]:
        """
        Apply hard filters to cities.
        Now works with Google Maps API (doesn't require coordinates).
        """
        filtered = []
        filter_stats = {
            "total_input": len(cities),
            "filtered_budget": 0,
            "filtered_commute": 0,
            "filtered_population": 0,
            "filtered_region": 0,
        }
        
        # Get workplace for commute filtering
        workplace_city = None
        workplace_code = self._code3(criteria.get("workplace_city_code"))
        
        if workplace_code:
            workplace_city = next(
                (c for c in cities if self._code3(c.get("code")) == workplace_code), None
            )
            if workplace_city:
                logger.info(f"Found workplace: {workplace_city.get('name')} (code: {workplace_code})")
            else:
                logger.warning(f"Workplace with code {workplace_code} not found in cities list")
        
        search_type = criteria.get("search_type", "rent")
        max_commute = self._num(criteria.get("max_commute_minutes"))
        has_car = bool(criteria.get("has_car", False))
        min_population = self._num(criteria.get("min_population"))
        allowed_regions = criteria.get("regions")
        
        for city in cities:
            # Budget filter
            if search_type == "rent":
                budget = self._num(criteria.get("max_monthly_rent"))
                desired_m2 = criteria.get("desired_m2", 60)
                price_m2 = self._get_rent_m2(city)
                
                if budget and price_m2:
                    if price_m2 * desired_m2 > budget:
                        filter_stats["filtered_budget"] += 1
                        continue
            else:
                budget = self._num(criteria.get("max_purchase_price"))
                desired_m2 = criteria.get("desired_m2", 70)
                property_type = criteria.get("property_type", "apartment")
                price_m2 = self._get_price_m2(city, property_type)
                
                if budget and price_m2:
                    if price_m2 * desired_m2 > budget:
                        filter_stats["filtered_budget"] += 1
                        continue
            
            # Commute filter - now works without coordinates (uses city names)
            if workplace_city and max_commute and max_commute > 0:
                # Don't use Google Maps for filtering (too many API calls)
                # Use Haversine or default estimate instead
                commute_info = self.calculate_commute_to_city(city, workplace_city, has_car, use_gmaps=False)
                
                if commute_info:
                    city["_commute_time"] = commute_info["commute_minutes"]
                    city["_commute_source"] = commute_info["source"]
                    
                    if commute_info["commute_minutes"] > max_commute:
                        filter_stats["filtered_commute"] += 1
                        continue
                # If no commute info at all, still include the city
            
            # Population filter
            if min_population:
                pop_stats = self._get_population_stats(city)
                if pop_stats["total"] < min_population:
                    filter_stats["filtered_population"] += 1
                    continue
            
            # Region filter
            if allowed_regions and isinstance(allowed_regions, list):
                city_region = city.get("region", "").lower()
                if city_region and city_region not in [r.lower() for r in allowed_regions]:
                    filter_stats["filtered_region"] += 1
                    continue
            
            filtered.append(city)
        
        filter_stats["passed"] = len(filtered)
        return filtered, filter_stats
    
    # =========================================================================
    # MAIN SEARCH FUNCTION (with rate limiting)
    # =========================================================================
    
    def search_and_rank(self, cities: List[Dict], criteria: Dict) -> List[Dict]:
        """
        Main search function with rate-limited Google Maps API calls.
        """
        logger.info(f"Starting search with {len(cities)} cities")
        
        # Reset Google Maps API counter for this search
        self._reset_gmaps_counter()
        
        # Step 1: Filter (uses Haversine, not Google Maps)
        filtered_cities, filter_stats = self.filter_cities(cities, criteria)
        logger.info(f"After filtering: {len(filtered_cities)} cities")
        logger.info(f"Filter stats: {filter_stats}")
        
        if not filtered_cities:
            return []
        
        # Step 2: Get workplace city
        workplace_city = None
        workplace_code = self._code3(criteria.get("workplace_city_code"))
        if workplace_code:
            workplace_city = next(
                (c for c in cities if self._code3(c.get("code")) == workplace_code), None
            )
        
        # Step 3: Calculate statistics for normalization
        stats = self._calculate_dataset_stats(filtered_cities, criteria)
        
        # Step 4: Score all cities
        scored_cities = []
        for city in filtered_cities:
            try:
                scores = self.calculate_all_scores(city, criteria, stats, workplace_city)
                final_score = self.calculate_final_score(scores, criteria)
                
                # Calculate commute info for display
                # Only use Google Maps for top candidates (after initial scoring)
                commute_info = None
                if workplace_city:
                    has_car = bool(criteria.get("has_car", False))
                    # Use cached commute time from filtering, don't call Google Maps yet
                    commute_info = self.calculate_commute_to_city(city, workplace_city, has_car, use_gmaps=False)
                
                scored_cities.append({
                    "city": city,
                    "final_score": final_score,
                    "category_scores": scores,
                    "commute_info": commute_info
                })
            except Exception as e:
                logger.error(f"Error scoring city {city.get('name')}: {e}")
                continue
        
        # Step 5: Sort by final score
        scored_cities.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Step 6: Use Google Maps API only for top 5 results (to save credits)
        if workplace_city and GOOGLE_MAPS_AVAILABLE:
            has_car = bool(criteria.get("has_car", False))
            for result in scored_cities[:5]:
                city = result["city"]
                # Try Google Maps for accurate commute time
                commute_info = self.calculate_commute_to_city(city, workplace_city, has_car, use_gmaps=True)
                if commute_info:
                    result["commute_info"] = commute_info
                    # Update commute score with accurate time
                    if commute_info["source"] == "google_maps":
                        result["category_scores"]["commute"] = self.score_commute(
                            city, criteria, stats, workplace_city
                        )
        
        # Step 7: Add percentile rankings
        all_scores = [c["final_score"] for c in scored_cities]
        for result in scored_cities:
            result["ranking"] = self.calculate_percentile_rank(result["final_score"], all_scores)
        
        logger.info(f"Returning {len(scored_cities)} scored cities (Google Maps calls: {self._gmaps_calls_this_search})")
        return scored_cities
    
    # =========================================================================
    # SPIDER GRAPH DATA GENERATION
    # =========================================================================
    
    def generate_spider_graph_data(self, scored_cities: List[Dict], 
                                   max_cities: int = 5) -> Dict:
        """
        Generate data structure for spider/radar graph visualization.
        
        Returns:
            {
                "labels": ["Affordability", "Market Activity", ...],
                "datasets": [
                    {
                        "label": "Ljubljana",
                        "data": [85, 92, 78, ...],
                        "color": "#10B981"
                    },
                    ...
                ]
            }
        """
        labels = [
            "Affordability",
            "Market Activity", 
            "Population Vitality",
            "Healthcare",
            "Housing Diversity"
        ]
        
        # Check if any city has commute score
        has_commute = any(
            c.get("category_scores", {}).get("commute") is not None 
            for c in scored_cities[:max_cities]
        )
        if has_commute:
            labels.append("Commute")
        
        colors = ["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6", "#EC4899"]
        
        datasets = []
        for i, result in enumerate(scored_cities[:max_cities]):
            scores = result.get("category_scores", {})
            data = [
                scores.get("affordability") or 0,
                scores.get("market_activity") or 0,
                scores.get("population_vitality") or 0,
                scores.get("healthcare") or 0,
                scores.get("housing_diversity") or 0,
            ]
            if has_commute:
                data.append(scores.get("commute") or 0)
            
            datasets.append({
                "label": result.get("city", {}).get("name", f"City {i+1}"),
                "data": data,
                "color": colors[i % len(colors)]
            })
        
        return {
            "labels": labels,
            "datasets": datasets
        }
=======
import logging
from typing import List, Dict, Any, Optional
import math

logger = logging.getLogger(__name__)

class CitySearchEngine:
    """
    Advanced city search and ranking system.
    """
    
    def __init__(self):
        self.life_stage_profiles = {
            'student': {
                'demographics_weights': {'young': 0.7, 'working': 0.3, 'old': 0.0},
                'education_importance': 0.8,
                'affordability_importance': 1.0,
                'healthcare_importance': 0.3
            },
            'young_professional': {
                'demographics_weights': {'young': 0.3, 'working': 0.7, 'old': 0.0},
                'education_importance': 0.3,
                'affordability_importance': 0.8,
                'healthcare_importance': 0.5
            },
            'young_family': {
                'demographics_weights': {'young': 0.4, 'working': 0.5, 'old': 0.1},
                'education_importance': 1.0,
                'affordability_importance': 0.7,
                'healthcare_importance': 0.8
            },
            'established_family': {
                'demographics_weights': {'young': 0.3, 'working': 0.5, 'old': 0.2},
                'education_importance': 0.8,
                'affordability_importance': 0.6,
                'healthcare_importance': 0.7
            },
            'retiree': {
                'demographics_weights': {'young': 0.0, 'working': 0.2, 'old': 0.8},
                'education_importance': 0.2,
                'affordability_importance': 0.7,
                'healthcare_importance': 1.0
            }
        }
    
    def calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula."""
        try:
            R = 6371.0
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            distance = R * c
            return distance
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return 0
    
    def estimate_commute_time_minutes(self, distance_km: float, has_car: bool) -> float:
        """
        Estimate realistic commute time based on distance.
        This accounts for:
        - Actual road routes (not straight line)
        - Traffic conditions
        - Public transport inefficiencies
        """
        try:
            if distance_km == 0:
                return 5  # Same city, assume some internal travel
            
            # Adjust for actual road distance (typically 1.3-1.5x straight line)
            actual_road_distance = distance_km * 1.4
            
            if has_car:
                # Car travel - realistic speeds
                if actual_road_distance < 10:
                    avg_speed = 40  # City/suburban traffic
                elif actual_road_distance < 30:
                    avg_speed = 55  # Mix of roads
                elif actual_road_distance < 60:
                    avg_speed = 70  # Highway
                else:
                    avg_speed = 80  # Long highway
                
                # Add 5 min overhead for parking, leaving, etc.
                commute_time = (actual_road_distance / avg_speed) * 60 + 5
            
            else:
                # Public transport - much slower and includes waiting
                if actual_road_distance < 10:
                    avg_speed = 25  # Local bus
                    overhead = 15  # Waiting + walking
                elif actual_road_distance < 30:
                    avg_speed = 35  # Regional bus/train
                    overhead = 20  # More waiting time
                elif actual_road_distance < 60:
                    avg_speed = 50  # Intercity train
                    overhead = 25  # Station access + transfers
                else:
                    avg_speed = 60  # Long distance train
                    overhead = 30  # Complex journey
                
                # Many small towns have no good public transport
                if actual_road_distance > 40:
                    overhead += 20  # Limited frequency penalty
                
                commute_time = (actual_road_distance / avg_speed) * 60 + overhead
            
            return round(commute_time, 1)
        
        except Exception as e:
            logger.error(f"Error calculating commute time: {e}")
            return 999
    
    def search_and_rank(self, cities: List[Dict], criteria: Dict) -> List[Dict]:
        """Main search function."""
        try:
            # Step 1: Filter cities
            filtered_cities = self._filter_cities(cities, criteria)
            
            if not filtered_cities:
                logger.warning("No cities matched the filter criteria")
                return []
            
            # Get workplace city if specified
            workplace_city = None
            if criteria.get('workplace_city_code'):
                workplace_city = next(
                    (c for c in cities if c.get('code') == criteria['workplace_city_code']), 
                    None
                )
                if workplace_city:
                    logger.info(f"Workplace: {workplace_city.get('name')} "
                               f"at ({workplace_city.get('latitude')}, {workplace_city.get('longitude')})")
            
            # Step 2: Score all filtered cities
            scored_cities = []
            for city in filtered_cities:
                try:
                    scores = self._calculate_category_scores(city, criteria, filtered_cities, workplace_city)
                    final_score = self._calculate_final_score(scores, criteria)
                    
                    commute_info = None
                    if workplace_city:
                        commute_info = self._calculate_commute_info(city, criteria, [workplace_city])
                    
                    scored_cities.append({
                        'city': city,
                        'final_score': final_score,
                        'category_scores': scores,
                        'commute_info': commute_info
                    })
                except Exception as e:
                    logger.error(f"Error scoring city {city.get('name')}: {e}")
                    continue
            
            # Step 3: Sort by score
            scored_cities.sort(key=lambda x: x['final_score'], reverse=True)
            
            return scored_cities
        
        except Exception as e:
            logger.error(f"Search and rank failed: {e}", exc_info=True)
            return []
    
    def _calculate_category_scores(self, city: Dict, criteria: Dict, all_cities: List[Dict], workplace_city: Dict = None) -> Dict:
        """Calculate scores for all categories."""
        scores = {}
        
        try:
            scores['affordability'] = self._score_affordability(city, criteria)
            scores['demographics'] = self._score_demographics(city, criteria)
            scores['transportation'] = self._score_transportation(city, criteria, workplace_city)
            scores['healthcare'] = self._score_healthcare(city, criteria, all_cities)
            scores['education'] = self._score_education(city, criteria, all_cities)
            scores['weather'] = self._score_weather(city)
            scores['price_diversity'] = self._score_price_diversity(city, all_cities)
            scores['market_liquidity'] = self._score_market_liquidity(city, all_cities)
        except Exception as e:
            logger.error(f"Error calculating category scores for {city.get('name')}: {e}")
        
        return scores

    def _score_transportation(self, city: Dict, criteria: Dict, workplace_city: Dict = None) -> Optional[float]:
        """Score based on commute - use pre-calculated time if available."""
        try:
            has_car = criteria.get('has_car', False)
            
            if workplace_city:
                # Use pre-calculated commute time from filtering stage
                commute_minutes = city.get('_commute_time')
                
                if commute_minutes is None:
                    # Calculate if not already done
                    if city.get('code') == workplace_city.get('code'):
                        commute_minutes = 5
                    else:
                        city_lat = city.get('latitude')
                        city_lon = city.get('longitude')
                        work_lat = workplace_city.get('latitude')
                        work_lon = workplace_city.get('longitude')
                        
                        if not all([city_lat, city_lon, work_lat, work_lon]):
                            return 40
                        
                        distance_km = self.calculate_distance_km(city_lat, city_lon, work_lat, work_lon)
                        commute_minutes = self.estimate_commute_time_minutes(distance_km, has_car)
                
                logger.debug(f"{city.get('name')}: {commute_minutes:.0f}min commute")
                
                # Score based on commute time
                max_acceptable = criteria.get('max_commute_minutes', 60)
                
                if commute_minutes <= 10:
                    score = 100  # Excellent - walking distance
                elif commute_minutes <= 20:
                    score = 95 - ((commute_minutes - 10) * 1.5)  # 95-80
                elif commute_minutes <= 30:
                    score = 80 - ((commute_minutes - 20) * 2)  # 80-60
                elif commute_minutes <= 45:
                    score = 60 - ((commute_minutes - 30) * 2)  # 60-30
                elif commute_minutes <= max_acceptable:
                    score = 30 - ((commute_minutes - 45) * 2)  # 30-0
                else:
                    # This shouldn't happen if filtering works correctly
                    score = 0
                
                logger.debug(f"{city.get('name')}: Transport score = {score:.1f}")
                return round(max(0, min(100, score)), 2)
            
            # No workplace - base on density
            density = city.get('population_density', 0)
            
            if has_car:
                if density < 50:
                    return 100
                elif density < 150:
                    return 80
                elif density < 500:
                    return 60
                else:
                    return 40
            else:
                if density > 500:
                    return 100
                elif density > 150:
                    return 80
                elif density > 50:
                    return 60
                else:
                    return 40
        
        except Exception as e:
            logger.error(f"Error in transportation scoring: {e}")
            return 50

    def _filter_cities(self, cities: List[Dict], criteria: Dict) -> List[Dict]:
        """Filter based on hard constraints."""
        filtered = []
        filtered_out_commute = 0
        
        workplace_city = None
        if criteria.get('workplace_city_code'):
            workplace_city = next(
                (c for c in cities if c.get('code') == criteria['workplace_city_code']), 
                None
            )
            if workplace_city:
                logger.info(f"Filtering for workplace: {workplace_city.get('name')}")
        
        for city in cities:
            try:
                # Budget filters
                if criteria.get('max_monthly_rent'):
                    desired_m2 = criteria.get('desired_m2', 50)
                    city_rent = city.get('avg_rent_m2')
                    
                    if city_rent and city_rent * desired_m2 > criteria['max_monthly_rent']:
                        continue
                
                # Purchase filter
                if criteria.get('max_purchase_price'):
                    desired_m2 = criteria.get('desired_m2', 70)
                    property_type = criteria.get('property_type', 'apartment')
                    
                    price_m2 = city.get('avg_price_m2_apartment') if property_type == 'apartment' else city.get('avg_price_m2_house')
                    
                    if price_m2 and price_m2 * desired_m2 > criteria['max_purchase_price']:
                        continue
                
                # COMMUTE FILTER - STRICT ENFORCEMENT
                if workplace_city and criteria.get('max_commute_minutes'):
                    max_commute = criteria['max_commute_minutes']
                    
                    # Same city as workplace - minimal commute
                    if city.get('code') == workplace_city.get('code'):
                        city['_commute_time'] = 5  # Store for later use
                        filtered.append(city)
                        continue
                    
                    city_lat = city.get('latitude')
                    city_lon = city.get('longitude')
                    work_lat = workplace_city.get('latitude')
                    work_lon = workplace_city.get('longitude')
                    
                    if all([city_lat, city_lon, work_lat, work_lon]):
                        # Calculate straight-line distance
                        distance_km = self.calculate_distance_km(city_lat, city_lon, work_lat, work_lon)
                        
                        # Estimate realistic commute time
                        has_car = criteria.get('has_car', False)
                        commute_minutes = self.estimate_commute_time_minutes(distance_km, has_car)
                        
                        # Store commute time for later use in scoring
                        city['_commute_time'] = commute_minutes
                        
                        # STRICT FILTER: exclude if over max
                        if commute_minutes > max_commute:
                            logger.debug(f"FILTERED OUT: {city.get('name')} - "
                                       f"{distance_km:.1f}km = {commute_minutes:.0f}min "
                                       f"(max: {max_commute}min, car: {has_car})")
                            filtered_out_commute += 1
                            continue
                        else:
                            logger.debug(f"INCLUDED: {city.get('name')} - "
                                       f"{distance_km:.1f}km = {commute_minutes:.0f}min "
                                       f"(max: {max_commute}min, car: {has_car})")
                    else:
                        # No coordinates - be conservative and exclude
                        logger.debug(f"FILTERED OUT: {city.get('name')} - no coordinates")
                        filtered_out_commute += 1
                        continue
                
                filtered.append(city)
            
            except Exception as e:
                logger.error(f"Error filtering city {city.get('name', 'unknown')}: {e}")
                continue
        
        if workplace_city:
            logger.info(f"✓ Commute filter: {len(filtered)} cities within {criteria.get('max_commute_minutes')}min")
            logger.info(f"✗ Filtered out: {filtered_out_commute} cities due to commute distance")
        
        logger.info(f"Total filtered: {len(filtered)} cities from {len(cities)} total")
        return filtered
    
    def _calculate_commute_info(self, city: Dict, criteria: Dict, workplace_cities: List[Dict]) -> Optional[Dict]:
        """Calculate commute details."""
        if not workplace_cities:
            return None
        
        try:
            workplace_city = workplace_cities[0]
            
            city_lat = city.get('latitude')
            city_lon = city.get('longitude')
            work_lat = workplace_city.get('latitude')
            work_lon = workplace_city.get('longitude')
            
            if not all([city_lat, city_lon, work_lat, work_lon]):
                return None
            
            distance_km = self.calculate_distance_km(city_lat, city_lon, work_lat, work_lon)
            has_car = criteria.get('has_car', False)
            commute_minutes = self.estimate_commute_time_minutes(distance_km, has_car)
            
            return {
                'distance_km': round(distance_km, 2),
                'commute_minutes': round(commute_minutes, 1),
                'workplace_name': workplace_city.get('name'),
                'one_way_time': round(commute_minutes, 1),
                'daily_time': round(commute_minutes * 2, 1)
            }
        except Exception as e:
            logger.error(f"Error calculating commute info: {e}")
            return None

    # Add all other scoring methods with try/except blocks
    def _score_affordability(self, city: Dict, criteria: Dict) -> Optional[float]:
        """Score affordability."""
        try:
            if criteria.get('search_type') == 'rent':
                budget = criteria.get('max_monthly_rent')
                desired_m2 = criteria.get('desired_m2', 50)
                rent_m2 = city.get('avg_rent_m2')
                
                if not budget or not rent_m2:
                    return None
                
                actual_cost = rent_m2 * desired_m2
                score = max(0, min(100, (1 - (actual_cost / budget)) * 200))
                return round(score, 2)
            
            elif criteria.get('search_type') == 'purchase':
                budget = criteria.get('max_purchase_price')
                desired_m2 = criteria.get('desired_m2', 70)
                property_type = criteria.get('property_type', 'apartment')
                
                price_m2 = city.get('avg_price_m2_apartment') if property_type == 'apartment' else city.get('avg_price_m2_house')
                
                if not budget or not price_m2:
                    return None
                
                actual_cost = price_m2 * desired_m2
                score = max(0, min(100, (1 - (actual_cost / budget)) * 200))
                return round(score, 2)
            
            return None
        except Exception as e:
            logger.error(f"Error in affordability scoring: {e}")
            return None

    # Add stubs for other scoring methods to prevent crashes
    def _score_demographics(self, city, criteria):
        return 50
    
    def _score_healthcare(self, city, criteria, all_cities):
        return 50
    
    def _score_education(self, city, criteria, all_cities):
        return 50
    
    def _score_weather(self, city):
        return city.get('weather_score', 50)
    
    def _score_price_diversity(self, city, all_cities):
        return 50
    
    def _score_market_liquidity(self, city, all_cities):
        return 50
    
    def _calculate_final_score(self, category_scores: Dict, criteria: Dict) -> float:
        """Calculate final weighted score."""
        try:
            weights = criteria.get('weights', {})
            
            default_weights = {
                'affordability': 10,
                'demographics': 5,
                'transportation': 5,
                'healthcare': 5,
                'education': 5,
                'weather': 3,
                'price_diversity': 7,
                'market_liquidity': 5
            }
            
            if criteria.get('workplace_city_code'):
                default_weights['transportation'] = 25
            
            total_weight = 0
            weighted_sum = 0
            
            for category, score in category_scores.items():
                if score is not None:
                    weight = weights.get(category, default_weights.get(category, 5))
                    weighted_sum += score * weight
                    total_weight += weight
            
            if total_weight == 0:
                return 0
            
            final_score = (weighted_sum / total_weight)
            return round(final_score, 2)
        except Exception as e:
            logger.error(f"Error calculating final score: {e}")
            return 0
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
