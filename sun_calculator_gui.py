import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from sun_calculator import SunCalculator
from cities_db import CitiesDatabase
import pytz

class SunCalculatorGUI:
    """GUI interface for the sun calculator application."""
    
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI window and components."""
        self.root = root
        self.root.title("Sun Calculator")
        self.calculator = SunCalculator()
        self.cities_db = CitiesDatabase()
        
        # Configure main window
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # City selection
        ttk.Label(main_frame, text="Select City:").grid(row=0, column=0, sticky=tk.W)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(main_frame, textvariable=self.city_var)
        self.city_combo['values'] = ['Custom Location'] + self.cities_db.list_cities()
        self.city_combo.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))
        self.city_combo.set('Custom Location')
        self.city_combo.bind('<<ComboboxSelected>>', self.on_city_select)
        
        # Location inputs
        ttk.Label(main_frame, text="Location Name:").grid(row=1, column=0, sticky=tk.W)
        self.location_name = ttk.Entry(main_frame)
        self.location_name.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        self.location_name.insert(0, "My Location")
        
        ttk.Label(main_frame, text="Latitude:").grid(row=2, column=0, sticky=tk.W)
        self.latitude = ttk.Entry(main_frame)
        self.latitude.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="Longitude:").grid(row=3, column=0, sticky=tk.W)
        self.longitude = ttk.Entry(main_frame)
        self.longitude.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        # Timezone selection
        ttk.Label(main_frame, text="Timezone:").grid(row=4, column=0, sticky=tk.W)
        self.timezone_var = tk.StringVar(value="UTC")
        self.timezone_combo = ttk.Combobox(main_frame, textvariable=self.timezone_var)
        self.timezone_combo['values'] = ['UTC'] + sorted(pytz.all_timezones)
        self.timezone_combo.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        # Date input
        ttk.Label(main_frame, text="Date (YYYY-MM-DD):").grid(row=5, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(main_frame)
        self.date_entry.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Calculate button
        ttk.Button(main_frame, text="Calculate", command=self.calculate).grid(row=6, column=0, columnspan=3, pady=10)
        
        # Results display
        self.result_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        self.result_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.coordinates_label = ttk.Label(self.result_frame, text="Coordinates: ")
        self.coordinates_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        ttk.Label(self.result_frame, text="Time Zone:").grid(row=1, column=0, sticky=tk.W)
        self.timezone_label = ttk.Label(self.result_frame, text="")
        self.timezone_label.grid(row=1, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Label(self.result_frame, text="Sunrise (UTC):").grid(row=2, column=0, sticky=tk.W)
        self.sunrise_utc_label = ttk.Label(self.result_frame, text="")
        self.sunrise_utc_label.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Label(self.result_frame, text="Sunrise (Local):").grid(row=3, column=0, sticky=tk.W)
        self.sunrise_local_label = ttk.Label(self.result_frame, text="")
        self.sunrise_local_label.grid(row=3, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Label(self.result_frame, text="Sunset (UTC):").grid(row=4, column=0, sticky=tk.W)
        self.sunset_utc_label = ttk.Label(self.result_frame, text="")
        self.sunset_utc_label.grid(row=4, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Label(self.result_frame, text="Sunset (Local):").grid(row=5, column=0, sticky=tk.W)
        self.sunset_local_label = ttk.Label(self.result_frame, text="")
        self.sunset_local_label.grid(row=5, column=1, columnspan=2, sticky=tk.W)
        
        # Cities list display
        cities_frame = ttk.LabelFrame(main_frame, text="Available Cities", padding="5")
        cities_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        cities_text = tk.Text(cities_frame, height=12, width=60)
        cities_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        cities_text.insert('1.0', self.cities_db.format_cities_list())
        cities_text.config(state='disabled')
        
        # Add scrollbar to cities list
        scrollbar = ttk.Scrollbar(cities_frame, orient='vertical', command=cities_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        cities_text['yscrollcommand'] = scrollbar.set
        
    def on_city_select(self, event=None) -> None:
        """Handle city selection from dropdown."""
        selected = self.city_var.get()
        if selected != 'Custom Location':
            try:
                city_info = self.cities_db.get_city_info(selected)
                self.location_name.delete(0, tk.END)
                self.location_name.insert(0, selected)
                self.latitude.delete(0, tk.END)
                self.latitude.insert(0, str(city_info.latitude))
                self.longitude.delete(0, tk.END)
                self.longitude.insert(0, str(city_info.longitude))
                self.timezone_var.set(city_info.timezone)
            except KeyError:
                messagebox.showerror("Error", "City not found in database")
    
    def format_time(self, dt: datetime, timezone: str) -> tuple[str, str]:
        """Format datetime in both UTC and local time."""
        utc_time = dt.strftime('%H:%M:%S UTC')
        if timezone != "UTC":
            local_dt = dt.astimezone(pytz.timezone(timezone))
            local_time = f"{local_dt.strftime('%H:%M:%S')} {local_dt.tzname()}"
        else:
            local_time = utc_time
        return utc_time, local_time
        
    def calculate(self) -> None:
        """Calculate and display sunrise/sunset times."""
        try:
            # Parse inputs
            lat = float(self.latitude.get())
            lon = float(self.longitude.get())
            name = self.location_name.get()
            date_str = self.date_entry.get()
            calc_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            timezone = self.timezone_var.get()
            
            # Set location and calculate
            self.calculator.set_location(name, lat, lon)
            sunrise, sunset = self.calculator.get_sun_times(calc_date)
            
            # Format times
            sunrise_utc, sunrise_local = self.format_time(sunrise, timezone)
            sunset_utc, sunset_local = self.format_time(sunset, timezone)
            
            # Update display
            self.coordinates_label.config(text=f"Coordinates: {lat:.4f}°, {lon:.4f}°")
            self.timezone_label.config(text=timezone)
            self.sunrise_utc_label.config(text=sunrise_utc)
            self.sunrise_local_label.config(text=sunrise_local)
            self.sunset_utc_label.config(text=sunset_utc)
            self.sunset_local_label.config(text=sunset_local)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main() -> None:
    """Launch the sun calculator application."""
    root = tk.Tk()
    app = SunCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()