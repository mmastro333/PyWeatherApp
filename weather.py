import customtkinter as ctk
import requests
import json
import os
import sys
import threading
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem as item

# --- Configuration Management ---
CONFIG_FILE = "config.json"

class Config:
    def __init__(self):
        self.cities = []
        self.last_city = ""
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.cities = data.get("cities", [])
                    self.last_city = data.get("last_city", "")
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        data = {
            "cities": self.cities,
            "last_city": self.last_city
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_city(self, city):
        if city and city not in self.cities:
            self.cities.append(city)
            self.save()

    def remove_city(self, city):
        if city in self.cities:
            self.cities.remove(city)
            self.save()

# --- Weather Logic ---

def get_weather_description(code):
    weather_map = {
        0:  "clear skies", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
        45: "foggy", 48: "depositing rime fog",
        51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
        56: "light freezing drizzle", 57: "dense freezing drizzle",
        61: "slight rain", 63: "moderate rain", 65: "heavy rain",
        66: "light freezing rain", 67: "heavy freezing rain",
        71: "slight snow fall", 73: "moderate snow fall", 75: "heavy snow fall",
        77: "snow grains",
        80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
        85: "slight snow showers", 86: "heavy snow showers",
        95: "thunderstorms", 96: "thunderstorms with slight hail", 99: "thunderstorms with heavy hail"
    }
    return weather_map.get(code, "Unknown weather condition")

def get_icon_filename(code):
    if code in [0, 1]: return "clear_0_1.png"
    if code == 2: return "partly_cloudy_2.png"
    if code == 3: return "overcast_3.png"
    if code in [45, 48]: return "fog_45_48.png"
    if code in [51, 53, 55, 56, 57]: return "drizzle_51_53_55_56_57.png"
    if code in [61, 63, 65, 66, 67, 80, 81, 82]: return "rain_61_63_65_66_67_80_81_82.png"
    if code in [71, 73, 75, 77, 85, 86]: return "snow_71_73_75_77_85_86.png"
    if code in [95, 96, 99]: return "thunderstorm_95_96_99.png" 
    return "clear_0_1.png"

# US State abbreviations mapping
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia"
}

def fetch_weather_data(city: str):
    """Fetches raw weather data with improved geocoding."""
    try:
        search_city = city
        context_filter = None
        
        if "," in city:
            parts = [p.strip() for p in city.split(",")]
            search_city = parts[0]
            if len(parts) > 1:
                context_filter = parts[1].upper()
                if context_filter in US_STATES:
                    context_filter = US_STATES[context_filter].upper()
                if context_filter == "USA":
                    context_filter = "US"

        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_city}&count=10&language=en&format=json"
        
        try:
            geo_resp = requests.get(geo_url).json()
        except:
             return None, "Network error calling Geocoding API."

        if not geo_resp.get('results'):
            return None, f"Could not find coordinates for {search_city}."
        
        candidate = geo_resp['results'][0]
        
        if context_filter:
            for result in geo_resp['results']:
                r_country = (result.get('country') or "").upper()
                r_code = (result.get('country_code') or "").upper()
                r_admin1 = (result.get('admin1') or "").upper()
                
                if (context_filter in r_country) or \
                   (context_filter == r_code) or \
                   (context_filter in r_admin1):
                    candidate = result
                    break

        lat = candidate['latitude']
        lon = candidate['longitude']
        name = candidate['name']
        admin1 = candidate.get('admin1', '')
        country = candidate.get('country', '')

        weather_url = (
           f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}&"
           f"current=temperature_2m,weather_code,is_day&timezone=auto"
        )
        response = requests.get(weather_url).json()
        
        if 'error' in response:
             return None, f"Weather API Error: {response.get('reason', 'Unknown')}"

        temp_c = response["current"]["temperature_2m"]
        temp_f = (temp_c * 9/5) + 32
        code = response["current"]["weather_code"]
        
        # Determine strict display name for saving/UI consistency? 
        # For now, we return what was found, but the User searches what they search.
        
        return {
            "city": name,
            "region": admin1,
            "country": country,
            "temp_f": temp_f,
            "code": code,
            "description": get_weather_description(code)
        }, None
    except Exception as e:
        return None, str(e)


# --- System Tray ---

class SystemTrayApp:
    def __init__(self, root_app):
        self.root_app = root_app
        self.running = False
        
        # Initialize icon immediately to avoid race conditions
        image = self.create_image()
        menu = (item('Open', self.show_window), item('Quit', self.quit_app))
        self.icon = pystray.Icon("weather_app", image, "Weather App", menu)

    def create_image(self, temp_text="--°"):
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((0, 0, width, height), fill=(33, 150, 243))
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        dc.text((width//2, height//2), f"{temp_text}", font=font, anchor="mm", fill="white")
        return image

    def run(self):
        self.running = True
        # icon is already created
        self.icon.run()

    def show_window(self, icon, item):
        self.root_app.deiconify()
        self.root_app.lift()
        self.root_app.focus_force()

    def update_icon(self, temp_str, weather_code, tooltip_text="Weather App"):
        if not self.icon:
            return
            
        # Update tooltip
        self.icon.title = tooltip_text
        
        filename = get_icon_filename(weather_code)
        path = os.path.join("weather_images", filename)
        
        if os.path.exists(path):
            base_img = Image.open(path).convert("RGBA")
            base_img = base_img.resize((64, 64))
            dc = ImageDraw.Draw(base_img)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            text = f"{temp_str}"
            x, y = 32, 50
            for adj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                dc.text((x+adj[0], y+adj[1]), text, font=font, anchor="mm", fill="black")
            dc.text((x, y), text, font=font, anchor="mm", fill="white")
            self.icon.icon = base_img
        else:
            self.icon.icon = self.create_image(temp_text=temp_str)

    def quit_app(self, icon, item):
        self.running = False
        self.icon.stop()
        self.root_app.quit()
        sys.exit()

# --- Main Application ---

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.tray = SystemTrayApp(self)
        
        self.title("Weather App")
        self.geometry("600x450")
        
        # Grid Layout: Col 0 = Sidebar (Fixed width), Col 1 = Main (Expand)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkScrollableFrame(self, label_text="Saved Cities", width=200)
        self.sidebar_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsew")
        
        # --- Main Content ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Input Area (Main Frame)
        self.input_frame_inner = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame_inner.pack(pady=20)
        
        self.input_label = ctk.CTkLabel(self.input_frame_inner, text="Enter City:")
        self.input_label.pack(side="left", padx=(0, 10))
        
        self.input_var = ctk.StringVar(value=self.config.last_city)
        self.city_entry = ctk.CTkEntry(self.input_frame_inner, placeholder_text="e.g. Bayonne, NJ", width=200, textvariable=self.input_var)
        self.city_entry.pack(side="left")
        
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(pady=5)

        self.submit_btn = ctk.CTkButton(self.btn_frame, text="Check Weather", command=self.submit_action)
        self.submit_btn.grid(row=0, column=0, padx=5)
        
        self.save_btn = ctk.CTkButton(self.btn_frame, text="Save City", command=self.save_city_action, fg_color="green")
        self.save_btn.grid(row=0, column=1, padx=5)

        self.about_btn = ctk.CTkButton(self.btn_frame, text="About", command=self.about_action, width=80)
        self.about_btn.grid(row=0, column=2, padx=5)

        # Weather Display
        self.icon_label = ctk.CTkLabel(self.main_frame, text="")
        self.icon_label.pack(pady=(20, 10))
        
        self.result_label = ctk.CTkLabel(self.main_frame, text="Enter a city to check weather.", wraplength=350, font=("Arial", 16))
        self.result_label.pack(pady=10)

        # Initialize Sidebar
        self.refresh_sidebar()
        
        # Load last city if available
        if self.config.last_city:
            self.submit_action()

        # Tray Setup
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        threading.Thread(target=self.tray.run, daemon=True).start()

        # Start Auto-Refresh Loop
        self.schedule_next_auto_refresh()

    def about_action(self):
        about_window = ctk.CTkToplevel(self)
        about_window.title("About")
        about_window.geometry("400x250")
        
        # Make modal (focus grab)
        about_window.grab_set()
        
        title_label = ctk.CTkLabel(about_window, text="PyWeatherApp", font=("Arial", 20, "bold"))
        title_label.pack(pady=(20, 5))
        
        ver_label = ctk.CTkLabel(about_window, text="Version 2.0", font=("Arial", 12))
        ver_label.pack(pady=(0, 20))
        
        text = ("Originally architected and hand-encoded by\n"
                "Michael Mastrogiacomo.\n\n"
                "Enhanced and 'vibe coded' with\n"
                "Google's AntiGravity.")
        
        info_label = ctk.CTkLabel(about_window, text=text, font=("Arial", 14), justify="center")
        info_label.pack(pady=10)
        
        ok_btn = ctk.CTkButton(about_window, text="OK", command=about_window.destroy, width=100)
        ok_btn.pack(pady=20)

    def schedule_next_auto_refresh(self):
        """Schedules the next refresh for a random time in the first 30min of the next hour."""
        now = datetime.now()
        # Calculate start of next hour
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        # Random delay between 0 and 30 minutes (in seconds)
        random_delay = random.randint(0, 30 * 60)
        target_time = next_hour + timedelta(seconds=random_delay)
        
        # Calculate wait time in ms
        wait_seconds = (target_time - now).total_seconds()
        wait_ms = int(wait_seconds * 1000)
        
        print(f"Next auto-refresh scheduled for {target_time.strftime('%H:%M:%S')} (in {wait_seconds/60:.1f} mins)")
        self.after(wait_ms, self.perform_auto_refresh)

    def perform_auto_refresh(self):
        """Background task to fetch weather and update UI."""
        city = self.input_var.get()
        if not city:
            self.schedule_next_auto_refresh()
            return
            
        def job():
            # Run fetch in background thread
            data, error = fetch_weather_data(city)
            if data and not error:
                # Update UI on main thread
                self.after(0, lambda: self.update_ui_from_data(data)) # Don't update input text, just visuals
        
        threading.Thread(target=job, daemon=True).start()
        
        # Schedule the NEXT one
        self.schedule_next_auto_refresh()

    def update_ui_from_data(self, data):
        """Updates labels and tray icon from weather data dict."""
        resolved_name = f"{data['city']}, {data['region']}"
        display_text = f"{resolved_name}\n{data['temp_f']:.1f}°F\n{data['description'].title()}"
        self.result_label.configure(text=display_text)
        
        self.update_gui_icon(data['code'])
        
        # Format Tooltip
        tooltip = f"PyWeatherApp - {resolved_name}  {data['temp_f']:.0f}F  & {data['description'].title()}"
        self.tray.update_icon(f"{int(data['temp_f'])}°", data['code'], tooltip_text=tooltip)

    def refresh_sidebar(self):
        # Clear existing
        for widget in self.sidebar_frame.winfo_children():
            widget.destroy()
            
        # Rebuild
        for city in self.config.cities:
            row_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            # City Label (Clickable)
            btn = ctk.CTkButton(
                row_frame, 
                text=city, 
                anchor="w", 
                fg_color="transparent", 
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda c=city: self.load_city_from_sidebar(c)
            )
            btn.pack(side="left", fill="x", expand=True)
            
            # Remove Button (X)
            del_btn = ctk.CTkButton(
                row_frame, 
                text="Remove", 
                width=50,
                height=24,
                corner_radius=2,
                fg_color="#ff6666", # Lighter red
                text_color="white",
                hover_color="#ff4444",
                font=("Arial", 11),
                command=lambda c=city: self.remove_city(c)
            )
            del_btn.pack(side="right", padx=(5, 0))

    def load_city_from_sidebar(self, city):
        self.input_var.set(city)
        self.submit_action()

    def remove_city(self, city):
        self.config.remove_city(city)
        self.refresh_sidebar()

    def save_city_action(self):
        city = self.input_var.get().strip()
        if city:
            self.config.add_city(city)
            # Update default startup city to the last saved one
            self.config.last_city = city
            self.config.save()
            self.refresh_sidebar()

    def submit_action(self):
        city = self.input_var.get()
        if not city:
            return

        self.result_label.configure(text=f"Fetching data for {city}...")
        self.update()

        data, error = fetch_weather_data(city)
        
        if error:
            self.result_label.configure(text=error)
            return
            
        # Use resolved name
        resolved_name = f"{data['city']}, {data['region']}"
        self.input_var.set(resolved_name)
        
        # NOTE: We do NOT update last_city here anymore, only on explicit Save.
        
        self.update_ui_from_data(data)

    def update_gui_icon(self, code):
        filename = get_icon_filename(code)
        path = os.path.join("weather_images", filename)
        if os.path.exists(path):
            img = ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=(100, 100))
            self.icon_label.configure(image=img)
        else:
            self.icon_label.configure(text="(No Icon)")

    def minimize_to_tray(self):
        self.withdraw()

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
