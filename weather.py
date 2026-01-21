
from langchain.tools import tool
from langchain.agents import create_agent
import requests
from langchain.tools import tool
import customtkinter as ctk

def get_weather_description(code):
    """
    Translates Open-Meteo (WMO) integer codes into human-readable strings.
    """
    weather_map = {
        0:  "clear skies",
        1:  "mainly clear",
        2:  "partly cloudy",
        3:  "overcast",
        45: "foggy",
        48: "foggy",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        56: "light freezing drizzle",
        57: "dense freezing drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        66: "light freezing rain",
        67: "heavy freezing rain",
        71: "slight snow fall",
        73: "moderate snow fall",
        75: "heavy snow fall",
        77: "snowing",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        85: "slight snow showers",
        86: "heavy snow showers",
        95: "thunderstorms",
        96: "thunderstorms with slight hail",
        99: "thunderstorms with heavy hail"
    }
    
    # .get() allows us to provide a fallback if a code is unknown
    return weather_map.get(code, "Unknown weather condition")


@tool
def get_current_weather(city: str):
    """Get the current temperature in Fahrenheit for a city using the Open-Meteo free API."""
    
    # 1. Geocoding: Turn city name into coordinates
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_data = requests.get(geo_url).json()
    
    if not geo_data.get('results'):
        return f"Could not find coordinates for {city}."
    
    lat = geo_data['results'][0]['latitude']
    lon = geo_data['results'][0]['longitude']

    # 2. Weather: Use the dynamic lat/lon to get the temperature
    weather_url = (
       f"https://api.open-meteo.com/v1/forecast?"
       f"latitude={lat}&"
       f"longitude={lon}&"
       f"current=temperature_2m,weather_code,is_day&timezone=auto"
    )

    response = requests.get(weather_url).json()

    temp_celcius = response["current"]["temperature_2m"]
    temp_fahrenheit = (temp_celcius * 9/5) + 32 
  
    conditions = get_weather_description(response['current']['weather_code'])
        
    return f"{city} is currently {temp_fahrenheit:.1f}°F and {conditions}."



def submit_action():
    city = entry.get()  # This gets the text from the box
    label.configure(text=f"Fetching weather data ...")
    app.update() # update the GUI

    # Initialize the agent
    agent = create_agent(
     model="gemini-2.0-flash", # Or "gpt-4o", "gemini-2.0-flash", "claude-3-5-sonnet", etc.
     tools=[get_current_weather],
     system_prompt="You are a helpful assistant that can check the weather.  You print out city names with first letter capitalized and the rest lower case, followed by the state abbreviation after a comma."
    )

    # Invoke the agent
    response = agent.invoke({
     "messages": [{"role": "user", "content": f"What's the weather like in {city}?"}]
    })

    final_answer = response["messages"][-1].content

    label.configure(text = final_answer)


# 1. Setup the window
app = ctk.CTk()
app.geometry("400x200")
app.title("Weather App")

# 2. Add a label
label = ctk.CTkLabel(app, text="", wraplength=350)
label.pack(pady=10)

# 3. Add the input box (Entry)
entry = ctk.CTkEntry(app, placeholder_text="Trenton, NJ", width=300)
entry.pack(pady=10)
city = entry.get()

# 4. Add the submit button
button = ctk.CTkButton(app, text="Submit", command=submit_action)
button.pack(pady=10)


app.mainloop()



