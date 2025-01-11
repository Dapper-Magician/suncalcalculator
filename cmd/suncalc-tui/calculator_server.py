"""
FastAPI server for sun calculations.
Provides endpoints for calculating sunrise and sunset times in UTC and GMT formats.
"""

from fastapi import FastAPI, HTTPException
from datetime import datetime
import uvicorn
from pydantic import BaseModel
import sys
import os
import pytz
from typing import Dict, Union

# Add parent directory to path to import sun_calculator
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sun_calculator import SunCalculator

app = FastAPI(
    title="Sun Calculator API",
    description="API for calculating sunrise and sunset times",
    version="1.0.0"
)

# Helper functions for validation and calculations
def get_calculator() -> SunCalculator:
    """Get or create a SunCalculator instance."""
    if not hasattr(get_calculator, "_calculator"):
        get_calculator._calculator = SunCalculator()
    return get_calculator._calculator

def validate_date(date_str: str) -> datetime:
    """Validate and parse date string."""
    try:
        calc_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        min_date = today.replace(year=today.year - 1)
        max_date = today.replace(year=today.year + 1)
        
        if calc_date < min_date:
            raise HTTPException(status_code=400, detail="Date too far in past: maximum 1 year ago")
        if calc_date > max_date:
            raise HTTPException(status_code=400, detail="Date too far in future: maximum 1 year ahead")
        return calc_date
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format: use YYYY-MM-DD")

def validate_coordinates(lat: float, lon: float) -> None:
    """Validate latitude and longitude values."""
    if not -90 <= lat <= 90:
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90 degrees")
    if not -180 <= lon <= 180:
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180 degrees")

def get_timezone(tz_str: str | None) -> tuple[str, pytz.timezone]:
    """Get timezone object and string representation."""
    gmt = pytz.timezone('GMT')
    if not tz_str:
        return "GMT", gmt
    try:
        tz = pytz.timezone(tz_str)
        return str(tz), tz
    except pytz.exceptions.UnknownTimeZoneError:
        return "GMT", gmt

class LocationInput(BaseModel):
    """Input model for location and time data."""
    name: str
    latitude: float
    longitude: float
    date: str
    timezone: str | None = None  # Optional timezone, defaults to None (will use GMT)

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "name": "New York",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "date": "2024-01-01",
                "timezone": "America/New_York"
            }
        }

class SunTimes(BaseModel):
    """Output model for sun calculation results."""
    sunrise_utc: str
    sunset_utc: str
    sunrise_gmt: str
    sunset_gmt: str
    timezone: str

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "sunrise_utc": "11:35:24 UTC",
                "sunset_utc": "21:45:12 UTC",
                "sunrise_gmt": "11:35:24 GMT",
                "sunset_gmt": "21:45:12 GMT",
                "timezone": "America/New_York"
            }
        }

@app.post("/calculate", response_model=SunTimes,
         summary="Calculate sunrise and sunset times",
         description="Calculate sunrise and sunset times for a given location and date")
async def calculate_sun_times(location: LocationInput) -> SunTimes:
    """
    Calculate sunrise and sunset times for a given location.
    
    Args:
        location: LocationInput model containing location and date information
        
    Returns:
        SunTimes model containing sunrise and sunset times in UTC and GMT
        
    Raises:
        HTTPException: For invalid input or calculation errors
    """
    try:
        # Validate inputs
        calc_date = validate_date(location.date)
        validate_coordinates(location.latitude, location.longitude)
        timezone_str, tz = get_timezone(location.timezone)

        # Calculate sun times
        calculator = get_calculator()
        calculator.set_location(location.name, location.latitude, location.longitude)
        sunrise, sunset = calculator.get_sun_times(calc_date)
        
        # Format times
        gmt = pytz.timezone('GMT')
        return SunTimes(
            sunrise_utc=sunrise.strftime("%H:%M:%S UTC"),
            sunset_utc=sunset.strftime("%H:%M:%S UTC"),
            sunrise_gmt=sunrise.astimezone(gmt).strftime("%H:%M:%S GMT"),
            sunset_gmt=sunset.astimezone(gmt).strftime("%H:%M:%S GMT"),
            timezone=timezone_str
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)