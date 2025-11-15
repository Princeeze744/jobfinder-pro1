"""
Location Detector Module
Auto-detects user location using IP geolocation
"""

import requests
from typing import Dict, Optional, Tuple
from src.logger import logger

class LocationDetector:
    """
    Detects user location using IP-based geolocation API
    """
    
    def __init__(self):
        """Initialize location detector"""
        self.current_location = None
        self.api_url = "https://ipwho.is/"
        logger.info("✅ LocationDetector initialized")
    
    def detect_location(self) -> Dict:
        """
        Auto-detect user location from IP address
        
        Returns:
            Dictionary with location data:
            {
                "city": "Lagos",
                "region": "Lagos",
                "country": "Nigeria",
                "country_code": "NG",
                "latitude": 6.5244,
                "longitude": 3.3792,
                "timezone": "Africa/Lagos",
                "ip": "user_ip"
            }
        """
        try:
            logger.info("🌍 Detecting user location from IP...")
            
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            location = {
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country_name", "Unknown"),
                "country_code": data.get("country_code", "XX"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone", "UTC"),
                "ip": data.get("ip", "Unknown")
            }
            
            self.current_location = location
            
            logger.info(f"✅ Location detected: {location['city']}, {location['country']}")
            return location
        
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Location detection timed out")
            return self._get_default_location()
        
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ No internet connection for location detection")
            return self._get_default_location()
        
        except Exception as e:
            logger.warning(f"⚠️ Error detecting location: {str(e)}")
            return self._get_default_location()
    
    def _get_default_location(self) -> Dict:
        """Get default location (when detection fails)"""
        return {
            "city": "Unknown",
            "region": "Unknown",
            "country": "Global",
            "country_code": "XX",
            "latitude": None,
            "longitude": None,
            "timezone": "UTC",
            "ip": "Unknown"
        }
    
    def get_display_string(self, location: Optional[Dict] = None) -> str:
        """
        Get user-friendly location string
        
        Args:
            location: Location dict (uses current if None)
            
        Returns:
            Formatted string like "Lagos, Nigeria"
        """
        if location is None:
            location = self.current_location or self._get_default_location()
        
        city = location.get("city", "")
        country = location.get("country", "")
        
        if city and city != "Unknown" and country and country != "Unknown":
            return f"📍 {city}, {country}"
        elif country and country != "Unknown":
            return f"📍 {country}"
        else:
            return "📍 Location Unknown"
    
    def get_current_location(self) -> Dict:
        """Get currently detected location"""
        if self.current_location is None:
            self.detect_location()
        return self.current_location or self._get_default_location()
    
    def is_location_detected(self) -> bool:
        """Check if location was successfully detected"""
        if not self.current_location:
            return False
        
        return (
            self.current_location.get("city") != "Unknown" and
            self.current_location.get("country") != "Unknown"
        )
    
    def get_coordinates(self, location: Optional[Dict] = None) -> Tuple[float, float]:
        """
        Get latitude and longitude
        
        Args:
            location: Location dict (uses current if None)
            
        Returns:
            Tuple of (latitude, longitude)
        """
        if location is None:
            location = self.current_location or self._get_default_location()
        
        lat = location.get("latitude")
        lon = location.get("longitude")
        
        if lat and lon:
            return (lat, lon)
        return (None, None)


# Example usage
def demo_location_detector():
    """Demo function"""
    detector = LocationDetector()
    location = detector.detect_location()
    print(f"\nDetected Location: {detector.get_display_string()}")
    print(f"Full data: {location}")
    return location


if __name__ == "__main__":
    demo_location_detector()