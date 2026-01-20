
from langchain.tools import tool
from langchain.agents import create_agent
import requests
from langchain.tools import tool
import customtkinter as ctk

@tool
def get_weather(city: str):
    """Get the current temperature in Fahrenheit for a city using the Open-Meteo free API."""
    # This is a simplified version; real apps usually convert city name to lat/long first
    # Example for Philly; provides AI with a schema
    url = f"https://api.open-meteo.com/v1/forecast?latitude=39.95&longitude=-75.16&current=temperature_2m" 
    data = requests.get(url).json()
    temp = data['current']['temperature_2m']
    temp = (temp * 9/5) + 32 # convert to Fahrenheit
    return f"{city}: {temp}°F."


# START WORK

def submit_action():
    city = entry.get()  # This gets the text from the box
    label.configure(text=f"Agent says: Processing {city}...")
    app.update() # update the GUI

    # Initialize the agent
    agent = create_agent(
     model="gemini-2.0-flash", # Or "gpt-4o", "gemini-2.0-flash", "claude-3-5-sonnet", etc.
     tools=[get_weather],
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
label = ctk.CTkLabel(app, text="")
label.pack(pady=10)

# 3. Add the input box (Entry)
entry = ctk.CTkEntry(app, placeholder_text="Trenton, NJ", width=300)
entry.pack(pady=10)
city = entry.get()

# 4. Add the submit button
button = ctk.CTkButton(app, text="Submit", command=submit_action)
button.pack(pady=10)



app.mainloop()


#####
