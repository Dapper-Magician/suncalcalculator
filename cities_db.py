from typing import Dict, Tuple, List, NamedTuple
from datetime import datetime
import pytz

class CityInfo(NamedTuple):
    """Container for city information."""
    latitude: float
    longitude: float
    timezone: str

class CitiesDatabase:
    """Database of major cities with their coordinates and timezones."""
    
    def __init__(self) -> None:
        """Initialize the cities database with predefined locations."""
        self.cities: Dict[str, CityInfo] = {
            # North America
            "New York": CityInfo(40.7128, -74.0060, "America/New_York"),
            "Chicago": CityInfo(41.8781, -87.6298, "America/Chicago"),
            "Los Angeles": CityInfo(34.0522, -118.2437, "America/Los_Angeles"),
            "Toronto": CityInfo(43.6532, -79.3832, "America/Toronto"),
            "Vancouver": CityInfo(49.2827, -123.1207, "America/Vancouver"),
            "Mexico City": CityInfo(19.4326, -99.1332, "America/Mexico_City"),
            "San Francisco": CityInfo(37.7749, -122.4194, "America/Los_Angeles"),
            "Miami": CityInfo(25.7617, -80.1918, "America/New_York"),
            
            # Europe
            "London": CityInfo(51.5074, -0.1278, "Europe/London"),
            "Paris": CityInfo(48.8566, 2.3522, "Europe/Paris"),
            "Berlin": CityInfo(52.5200, 13.4050, "Europe/Berlin"),
            "Rome": CityInfo(41.9028, 12.4964, "Europe/Rome"),
            "Madrid": CityInfo(40.4168, -3.7038, "Europe/Madrid"),
            "Amsterdam": CityInfo(52.3676, 4.9041, "Europe/Amsterdam"),
            "Moscow": CityInfo(55.7558, 37.6173, "Europe/Moscow"),
            "Stockholm": CityInfo(59.3293, 18.0686, "Europe/Stockholm"),
            
            # Asia
            "Tokyo": CityInfo(35.6762, 139.6503, "Asia/Tokyo"),
            "Beijing": CityInfo(39.9042, 116.4074, "Asia/Shanghai"),
            "Singapore": CityInfo(1.3521, 103.8198, "Asia/Singapore"),
            "Dubai": CityInfo(25.2048, 55.2708, "Asia/Dubai"),
            "Hong Kong": CityInfo(22.3193, 114.1694, "Asia/Hong_Kong"),
            "Seoul": CityInfo(37.5665, 126.9780, "Asia/Seoul"),
            "Mumbai": CityInfo(19.0760, 72.8777, "Asia/Kolkata"),
            "Bangkok": CityInfo(13.7563, 100.5018, "Asia/Bangkok"),
            
            # Australia/Pacific
            "Sydney": CityInfo(-33.8688, 151.2093, "Australia/Sydney"),
            "Melbourne": CityInfo(-37.8136, 144.9631, "Australia/Melbourne"),
            "Auckland": CityInfo(-36.8509, 174.7645, "Pacific/Auckland"),
            "Perth": CityInfo(-31.9505, 115.8605, "Australia/Perth"),
            
            # South America
            "Rio de Janeiro": CityInfo(-22.9068, -43.1729, "America/Sao_Paulo"),
            "Buenos Aires": CityInfo(-34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
            "Santiago": CityInfo(-33.4489, -70.6693, "America/Santiago"),
            "Lima": CityInfo(-12.0464, -77.0428, "America/Lima"),
        }
    
    def get_city_info(self, city: str) -> CityInfo:
        """
        Get information for a given city.
        
        Args:
            city: Name of the city
            
        Returns:
            CityInfo containing latitude, longitude, and timezone
            
        Raises:
            KeyError: If city is not in database
        """
        return self.cities[city]
    
    def list_cities(self) -> List[str]:
        """
        Get list of all available cities.
        
        Returns:
            List of city names
        """
        return sorted(self.cities.keys())
    
    def format_cities_list(self) -> str:
        """
        Get formatted string of all cities with their coordinates.
        
        Returns:
            Formatted string with city names and coordinates
        """
        result = []
        for city in sorted(self.cities.keys()):
            info = self.cities[city]
            result.append(f"{city}: {info.latitude:.4f}°, {info.longitude:.4f}° ({info.timezone})")
        return "\n".join(result)
    
    def get_local_time(self, city: str, utc_time: datetime) -> datetime:
        """
        Convert UTC time to city's local time.
        
        Args:
            city: Name of the city
            utc_time: UTC datetime
            
        Returns:
            Local time as datetime
            
        Raises:
            KeyError: If city is not in database
        """
        city_info = self.cities[city]
        local_tz = pytz.timezone(city_info.timezone)
        return utc_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)