"""
Location Matcher Module
Filters companies by location (local/international/remote)
"""

from typing import List, Dict, Optional
from src.logger import logger

class LocationMatcher:
    """
    Matches companies by location preferences
    """
    
    def __init__(self):
        """Initialize location matcher"""
        logger.info("✅ LocationMatcher initialized")
        
        # Define regions and countries
        self.regions = {
            "Africa": {
                "countries": ["Nigeria", "Kenya", "South Africa", "Egypt", "Ghana", "Uganda", "Rwanda", "Ethiopia"],
                "hubs": ["Lagos", "Nairobi", "Johannesburg", "Cairo", "Accra"]
            },
            "Europe": {
                "countries": ["UK", "Germany", "France", "Netherlands", "Switzerland", "Sweden", "Poland"],
                "hubs": ["London", "Berlin", "Paris", "Amsterdam", "Zurich"]
            },
            "North America": {
                "countries": ["USA", "Canada"],
                "hubs": ["San Francisco", "New York", "Toronto", "Seattle", "Boston"]
            },
            "Asia": {
                "countries": ["India", "Singapore", "Japan", "China", "South Korea"],
                "hubs": ["Bangalore", "Singapore", "Tokyo", "Shanghai", "Seoul"]
            },
            "Remote": {
                "countries": ["Remote", "Distributed"],
                "hubs": ["Anywhere"]
            }
        }
    
    def filter_by_location(self, companies: List[Dict], 
                          preferred_location: str,
                          include_remote: bool = True) -> List[Dict]:
        """
        Filter companies by location preference
        
        Args:
            companies: List of companies
            preferred_location: User's preferred location/region
            include_remote: Whether to include remote jobs
            
        Returns:
            Filtered companies list
        """
        try:
            logger.info(f"🌍 Filtering companies for location: {preferred_location}")
            
            filtered = []
            
            for company in companies:
                # Always include if remote preference is on and company is remote
                if include_remote and self._is_remote_company(company):
                    filtered.append(company)
                    continue
                
                # Check if company location matches preference
                if self._location_matches(company, preferred_location):
                    filtered.append(company)
            
            logger.info(f"✅ Filtered {len(companies)} → {len(filtered)} companies")
            return filtered
        
        except Exception as e:
            logger.error(f"❌ Error filtering by location: {str(e)}")
            return companies
    
    def _is_remote_company(self, company: Dict) -> bool:
        """Check if company offers remote positions"""
        company_str = str(company).lower()
        remote_keywords = ["remote", "distributed", "work from home", "anywhere", "global"]
        return any(keyword in company_str for keyword in remote_keywords)
    
    def _location_matches(self, company: Dict, preferred_location: str) -> bool:
        """Check if company location matches preference"""
        company_str = str(company).lower()
        location_lower = preferred_location.lower()
        
        # Direct match
        if location_lower in company_str:
            return True
        
        # Check if location is in a region
        for region, data in self.regions.items():
            if location_lower == region.lower():
                # Check if company is in any country/hub of this region
                for country in data["countries"]:
                    if country.lower() in company_str:
                        return True
                for hub in data["hubs"]:
                    if hub.lower() in company_str:
                        return True
        
        return False
    
    def get_regions(self) -> Dict:
        """Get available regions"""
        return self.regions
    
    def add_location_to_company(self, company: Dict, location: str) -> Dict:
        """Add location metadata to company"""
        company['user_location'] = location
        company['location_match_score'] = self._calculate_match_score(company, location)
        return company
    
    def _calculate_match_score(self, company: Dict, preferred_location: str) -> float:
        """Calculate how well company matches location preference"""
        score = 0.0
        company_str = str(company).lower()
        location_lower = preferred_location.lower()
        
        # Direct match = 100%
        if location_lower in company_str:
            return 1.0
        
        # Partial match = 70%
        if any(part in company_str for part in location_lower.split()):
            return 0.7
        
        # Remote option = 50%
        if self._is_remote_company(company):
            return 0.5
        
        return 0.0
    
    def get_top_matches(self, companies: List[Dict], 
                       preferred_location: str,
                       limit: int = 10) -> List[Dict]:
        """
        Get top matching companies for a location
        
        Args:
            companies: List of companies
            preferred_location: User's preferred location
            limit: Max number to return
            
        Returns:
            Top matching companies sorted by relevance
        """
        # Add scores
        scored = []
        for company in companies:
            company_with_score = self.add_location_to_company(company.copy(), preferred_location)
            scored.append(company_with_score)
        
        # Sort by score (descending)
        sorted_companies = sorted(scored, key=lambda x: x['location_match_score'], reverse=True)
        
        logger.info(f"✅ Top {limit} matches for {preferred_location}")
        return sorted_companies[:limit]


# Example usage
def demo_location_matcher():
    """Demo function"""
    matcher = LocationMatcher()
    print(matcher.get_regions())


if __name__ == "__main__":
    demo_location_matcher()