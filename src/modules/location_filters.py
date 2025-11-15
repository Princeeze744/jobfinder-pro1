"""
Location Filters Module
Advanced filtering by city, region, country, and job type (on-site/remote/hybrid)
"""

from typing import List, Dict, Tuple
import math
from src.logger import logger

class LocationFilters:
    """
    Advanced location-based filtering for job opportunities
    """
    
    def __init__(self):
        """Initialize location filters"""
        self.job_types = {
            "ON_SITE": "On-Site",
            "REMOTE": "Remote",
            "HYBRID": "Hybrid"
        }
        
        self.location_tiers = {
            "LOCAL": 1,      # Same city
            "REGIONAL": 2,   # Same country
            "GLOBAL": 3      # Worldwide
        }
        
        logger.info("✅ LocationFilters initialized")
    
    def filter_by_job_type(self, companies: List[Dict], 
                          job_type: str) -> List[Dict]:
        """
        Filter companies by job type (on-site, remote, hybrid)
        
        Args:
            companies: List of companies
            job_type: "on-site", "remote", or "hybrid"
            
        Returns:
            Filtered companies
        """
        try:
            logger.info(f"🔍 Filtering by job type: {job_type}")
            
            filtered = []
            job_type_lower = job_type.lower()
            
            for company in companies:
                company_str = str(company).lower()
                
                if job_type_lower == "remote":
                    if self._is_remote_job(company_str):
                        filtered.append(company)
                
                elif job_type_lower == "on-site":
                    if not self._is_remote_job(company_str) and not self._is_hybrid_job(company_str):
                        filtered.append(company)
                
                elif job_type_lower == "hybrid":
                    if self._is_hybrid_job(company_str):
                        filtered.append(company)
            
            logger.info(f"✅ Filtered to {len(filtered)} {job_type} opportunities")
            return filtered
        
        except Exception as e:
            logger.error(f"❌ Error filtering by job type: {str(e)}")
            return companies
    
    def filter_by_location(self, companies: List[Dict],
                          user_city: str, user_country: str,
                          location_tier: str = "GLOBAL") -> List[Dict]:
        """
        Filter companies by location tier
        
        Args:
            companies: List of companies
            user_city: User's city
            user_country: User's country
            location_tier: "LOCAL", "REGIONAL", or "GLOBAL"
            
        Returns:
            Filtered companies
        """
        try:
            logger.info(f"🌍 Filtering by location tier: {location_tier}")
            logger.info(f"   User location: {user_city}, {user_country}")
            
            filtered = []
            
            for company in companies:
                company_str = str(company).lower()
                
                if location_tier.upper() == "LOCAL":
                    # Same city + remote
                    if self._matches_city(company_str, user_city) or self._is_remote_job(company_str):
                        filtered.append(company)
                
                elif location_tier.upper() == "REGIONAL":
                    # Same country + remote
                    if self._matches_country(company_str, user_country) or self._is_remote_job(company_str):
                        filtered.append(company)
                
                elif location_tier.upper() == "GLOBAL":
                    # All companies
                    filtered.append(company)
            
            logger.info(f"✅ Filtered to {len(filtered)} companies for {location_tier} tier")
            return filtered
        
        except Exception as e:
            logger.error(f"❌ Error filtering by location: {str(e)}")
            return companies
    
    def filter_by_distance(self, companies: List[Dict],
                          user_lat: float, user_lon: float,
                          radius_km: float = 50) -> List[Dict]:
        """
        Filter companies within a distance radius
        
        Args:
            companies: List of companies with location data
            user_lat: User latitude
            user_lon: User longitude
            radius_km: Search radius in kilometers
            
        Returns:
            Filtered companies within radius
        """
        try:
            logger.info(f"📍 Filtering by distance: {radius_km}km radius")
            
            filtered = []
            
            for company in companies:
                # Check if company has coordinates
                if 'latitude' in company and 'longitude' in company:
                    company_lat = company.get('latitude')
                    company_lon = company.get('longitude')
                    
                    if company_lat and company_lon:
                        distance = self._calculate_distance(
                            user_lat, user_lon,
                            company_lat, company_lon
                        )
                        
                        if distance <= radius_km:
                            company['distance_km'] = round(distance, 2)
                            filtered.append(company)
                else:
                    # If no coordinates, include (could be remote)
                    filtered.append(company)
            
            logger.info(f"✅ Found {len(filtered)} companies within {radius_km}km")
            return filtered
        
        except Exception as e:
            logger.error(f"❌ Error filtering by distance: {str(e)}")
            return companies
    
    def combine_filters(self, companies: List[Dict],
                       user_city: str, user_country: str,
                       user_lat: float, user_lon: float,
                       job_type: str = "all",
                       location_tier: str = "GLOBAL",
                       radius_km: float = 50) -> List[Dict]:
        """
        Apply multiple filters at once
        
        Args:
            companies: List of companies
            user_city: User's city
            user_country: User's country
            user_lat: User's latitude
            user_lon: User's longitude
            job_type: "on-site", "remote", "hybrid", or "all"
            location_tier: "LOCAL", "REGIONAL", or "GLOBAL"
            radius_km: Search radius in km
            
        Returns:
            Filtered companies
        """
        try:
            logger.info(f"🔍 Applying combined filters...")
            
            result = companies.copy()
            
            # Apply job type filter
            if job_type.lower() != "all":
                result = self.filter_by_job_type(result, job_type)
            
            # Apply location filter
            result = self.filter_by_location(
                result, user_city, user_country, location_tier
            )
            
            # Apply distance filter if coordinates available
            if user_lat and user_lon and location_tier.upper() == "LOCAL":
                result = self.filter_by_distance(result, user_lat, user_lon, radius_km)
            
            logger.info(f"✅ Combined filters result: {len(result)} companies")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error in combined filters: {str(e)}")
            return companies
    
    def _is_remote_job(self, company_str: str) -> bool:
        """Check if job is remote"""
        remote_keywords = ["remote", "work from home", "distributed", "anywhere", "wfh"]
        return any(kw in company_str for kw in remote_keywords)
    
    def _is_hybrid_job(self, company_str: str) -> bool:
        """Check if job is hybrid"""
        hybrid_keywords = ["hybrid", "flexible", "part time remote"]
        return any(kw in company_str for kw in hybrid_keywords)
    
    def _matches_city(self, company_str: str, user_city: str) -> bool:
        """Check if company is in user's city"""
        return user_city.lower() in company_str
    
    def _matches_country(self, company_str: str, user_country: str) -> bool:
        """Check if company is in user's country"""
        return user_country.lower() in company_str
    
    def _calculate_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Returns:
            Distance in kilometers
        """
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_filter_recommendations(self, detected_location: Dict) -> Dict:
        """
        Get filter recommendations based on detected location
        
        Args:
            detected_location: Auto-detected location data
            
        Returns:
            Recommended filter settings
        """
        return {
            "city": detected_location.get("city"),
            "country": detected_location.get("country"),
            "latitude": detected_location.get("latitude"),
            "longitude": detected_location.get("longitude"),
            "recommended_radius_km": 50,
            "recommended_job_types": ["remote", "hybrid", "on-site"],
            "recommended_tiers": ["LOCAL", "REGIONAL", "GLOBAL"]
        }


if __name__ == "__main__":
    filters = LocationFilters()
    print("✅ LocationFilters initialized")