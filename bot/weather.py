import requests
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def get_current_weather(city="Helsinki"):

    try:

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": os.getenv("OPENWEATHER_API_KEY"),
            "units": "metric"
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code != 200:
            return "moderate"
        
        weather_map = {
            "Clear": "sunny",
            "Rain": "rainy",
            "Snow": "snowy",
            "Clouds": "cloudy",
            "Extreme": "stormy"
        }
        
        main_weather = data["weather"][0]["main"]
        return weather_map.get(main_weather, "moderate")
    
    except Exception as e:
        print(f"Weather API error: {e}")
        return "moderate"