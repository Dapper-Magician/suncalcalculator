from fastapi import FastAPI, HTTPException
from datetime import datetime
import uvicorn
from pydantic import BaseModel
import sys
import os

# Add parent directory to path to import sun_calculator
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sun_calculator import SunCalculator

app = FastAPI()
calculator = SunCalculator()

class LocationInput(BaseModel):
    name: str
    latitude: float
    longitude: float
    date: str

class SunTimes(BaseModel):
    sunrise_utc: str
    sunset_utc: str

@app.post("/calculate", response_model=SunTimes)
async def calculate_sun_times(location: LocationInput):
    try:
        # Parse date
        calc_date = datetime.strptime(location.date, "%Y-%m-%d").date()
        
        # Calculate sun times
        calculator.set_location(location.name, location.latitude, location.longitude)
        sunrise, sunset = calculator.get_sun_times(calc_date)
        
        return {
            "sunrise_utc": sunrise.strftime("%H:%M:%S UTC"),
            "sunset_utc": sunset.strftime("%H:%M:%S UTC")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)