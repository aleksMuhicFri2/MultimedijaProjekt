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
