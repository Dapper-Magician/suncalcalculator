from datetime import datetime
from sun_calculator import SunCalculator
from cities_db import CitiesDatabase
import pytz

def get_location_input(cities_db: CitiesDatabase) -> tuple[str, float, float, str]:
    """
    Get location input from user with support for preset cities.
    
    Args:
        cities_db: Database of cities and their coordinates
        
    Returns:
        Tuple of (location_name, latitude, longitude, timezone)
    """
    while True:
        print("\nLocation Input Options:")
        print("1. Choose from preset cities")
        print("2. Enter custom coordinates")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == "1":
            print("\nAvailable Cities:")
            print(cities_db.format_cities_list())
            while True:
                city = input("\nEnter city name from the list: ")
                try:
                    city_info = cities_db.get_city_info(city)
                    return city, city_info.latitude, city_info.longitude, city_info.timezone
                except KeyError:
                    print("City not found. Please try again.")
        
        elif choice == "2":
            name = input("\nEnter location name: ")
            try:
                lat = float(input("Enter latitude (-90 to 90): "))
                lon = float(input("Enter longitude (-180 to 180): "))
                print("\nTimezone Options:")
                print("1. Use UTC")
                print("2. Enter custom timezone")
                tz_choice = input("Enter your choice (1 or 2): ")
                
                if tz_choice == "1":
                    timezone = "UTC"
                elif tz_choice == "2":
                    print("\nExample timezones: America/New_York, Europe/London, Asia/Tokyo")
                    timezone = input("Enter timezone (from IANA timezone database): ")
                    # Validate timezone
                    try:
                        pytz.timezone(timezone)
                    except pytz.exceptions.UnknownTimeZoneError:
                        print("Invalid timezone. Defaulting to UTC.")
                        timezone = "UTC"
                else:
                    print("Invalid choice. Defaulting to UTC.")
                    timezone = "UTC"
                    
                return name, lat, lon, timezone
            except ValueError:
                print("Invalid coordinates. Please enter numeric values.")
                continue
        
        else:
            print("Invalid choice. Please enter 1 or 2.")

def format_time(dt: datetime, timezone: str) -> tuple[str, str]:
    """
    Format datetime in both UTC and local time.
    
    Args:
        dt: Datetime object
        timezone: Timezone string
        
    Returns:
        Tuple of (UTC time string, local time string)
    """
    utc_time = dt.strftime('%H:%M:%S UTC')
    if timezone != "UTC":
        local_dt = dt.astimezone(pytz.timezone(timezone))
        local_time = f"{local_dt.strftime('%H:%M:%S')} {local_dt.tzname()}"
    else:
        local_time = utc_time
    return utc_time, local_time

def main() -> None:
    """Command line interface for sun calculator."""
    calculator = SunCalculator()
    cities_db = CitiesDatabase()
    
    print("Sun Calculator")
    print("-" * 30)
    
    try:
        # Get location details
        name, lat, lon, timezone = get_location_input(cities_db)
        
        # Get date
        date_str = input("\nEnter date (YYYY-MM-DD) or press enter for today: ").strip()
        if date_str:
            calc_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            calc_date = datetime.now().date()
        
        # Calculate sun times
        calculator.set_location(name, lat, lon)
        sunrise, sunset = calculator.get_sun_times(calc_date)
        
        # Format times in UTC and local timezone
        sunrise_utc, sunrise_local = format_time(sunrise, timezone)
        sunset_utc, sunset_local = format_time(sunset, timezone)
        
        # Display results
        print("\nResults for", name)
        print(f"Coordinates: {lat:.4f}°, {lon:.4f}°")
        print(f"Date: {calc_date}")
        print(f"Timezone: {timezone}")
        print(f"Sunrise: {sunrise_utc}")
        print(f"        {sunrise_local}")
        print(f"Sunset:  {sunset_utc}")
        print(f"        {sunset_local}")
        
    except ValueError as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()