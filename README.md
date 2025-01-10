# Sun Calculator

A Python-based calculator for determining sunrise and sunset times for any location and date, featuring an extensive database of global cities and timezone support. Available in both command-line (CLI) and graphical user interfaces (GUI).

## Features

- Calculate sunrise and sunset times for any global location
- Extensive database of 32 major cities worldwide with coordinates
- Timezone support with local time conversion
- Support for custom coordinates and timezone input
- UTC time display for all calculations
- Support for any date input
- Latitude/longitude validation
- Simple, user-friendly interfaces
- Error handling and input validation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/suncalcalculator.git
cd suncalcalculator
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface (CLI)

Run the CLI version:
```bash
python sun_calculator_cli.py
```

The program will present two options:

1. Choose from preset cities
   - Displays a list of available cities with their coordinates and timezones
   - Simply enter the city name exactly as shown
   - Times will be displayed in both UTC and the city's local timezone

2. Enter custom coordinates
   - Enter location name
   - Enter latitude (-90 to 90)
   - Enter longitude (-180 to 180)
   - Choose timezone:
     * Use UTC
     * Enter custom timezone (e.g., America/New_York, Europe/London)

After selecting a location, enter the date:
- Press Enter for today's date
- Or enter a specific date in YYYY-MM-DD format (e.g., 2024-01-15)

### Graphical User Interface (GUI)

If you have a display server available, run the GUI version:
```bash
python sun_calculator_gui.py
```

The GUI provides:
- Dropdown menu for selecting preset cities
- Option for custom location input
- Timezone selection dropdown
- Input fields for location details
- Date input field
- Scrollable list of all available cities with coordinates
- Results display showing:
  * Coordinates
  * UTC times
  * Local timezone times

## Built-in Cities

The calculator includes coordinates and timezone data for 32 major cities worldwide:

### North America
- New York, Chicago, Los Angeles
- Toronto, Vancouver
- Mexico City
- San Francisco, Miami

### Europe
- London, Paris, Berlin
- Rome, Madrid, Amsterdam
- Moscow, Stockholm

### Asia
- Tokyo, Beijing, Singapore
- Dubai, Hong Kong, Seoul
- Mumbai, Bangkok

### Australia/Pacific
- Sydney, Melbourne
- Auckland, Perth

### South America
- Rio de Janeiro, Buenos Aires
- Santiago, Lima

## Timezone Support

- All calculations are performed in UTC
- Results are displayed in both UTC and local time
- Support for all IANA timezone database entries
- Automatic timezone selection for preset cities
- Custom timezone input for manual coordinates

## Error Messages

The calculator includes validation and will show error messages if:
- Latitude is not between -90 and 90 degrees
- Longitude is not between -180 and 180 degrees
- Date format is incorrect (should be YYYY-MM-DD)
- Invalid numeric inputs
- City name not found in database
- Invalid timezone specified

## Project Structure

- `sun_calculator.py`: Core calculation module using the astral library
- `cities_db.py`: Database of major cities with coordinates and timezones
- `sun_calculator_cli.py`: Command-line interface with timezone support
- `sun_calculator_gui.py`: Graphical interface with timezone selection
- `requirements.txt`: Required dependencies

## Dependencies

- Python 3.8+
- astral>=3.2
- pytz>=2023.3
- tkinter (included with Python, for GUI version)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
