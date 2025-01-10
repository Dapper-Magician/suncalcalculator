from datetime import datetime, date
from typing import Tuple, Optional
from astral import LocationInfo
from astral.sun import sun
import pytz

class SunCalculator:
    """Handles sunrise and sunset calculations for given locations and dates."""
    
    def __init__(self) -> None:
        """Initialize the SunCalculator."""
        self.location: Optional[LocationInfo] = None
        
    def set_location(self, name: str, latitude: float, longitude: float) -> None:
        """
        Set the location for sun calculations.
        
        Args:
            name: Location name
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
            
        Raises:
            ValueError: If coordinates are out of valid ranges
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
            
        self.location = LocationInfo(name=name, latitude=latitude, longitude=longitude)
    
    def get_sun_times(self, date_input: date) -> Tuple[datetime, datetime]:
        """
        Calculate sunrise and sunset times for a given date.
        
        Args:
            date_input: Date to calculate sun times for
            
        Returns:
            Tuple containing (sunrise, sunset) times as datetime objects
            
        Raises:
            ValueError: If location is not set
        """
        if not self.location:
            raise ValueError("Location must be set before calculating sun times")
            
        s = sun(self.location.observer, date=date_input)
        return s["sunrise"], s["sunset"]