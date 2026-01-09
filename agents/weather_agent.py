import requests
import json
import os
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()

def fetch_weather(state):
    """Fetch weather using OpenWeatherMap based on destination."""
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        state.weather_summary = "Weather data unavailable (Missing API Key)."
        return state

    # 1. Get coordinates
    try:
        # Prioritize destination_city (e.g. "San Francisco") over destination (e.g. "SFO Airport")
        geo_query = state.destination_city or state.destination
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={geo_query}&limit=1&appid={api_key}"
        logger.info(f"📍 GEOCODING PARAMS: {geo_query}")
        
        resp = requests.get(geo_url)
        geo_data = resp.json()
        
        logger.info(f"📍 RAW GEO DATA: {json.dumps(geo_data, indent=2)}")
        
        if not geo_data:
            state.weather_summary = f"Could not find coordinates for {state.destination}."
            return state

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

    except Exception as e:
        logger.error(f"❌ Weather Geocoding Error: {e}")
        state.weather_summary = "Weather unavailable."
        return state

    # 2. Get forecast (5 day / 3 hour)
    weather_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&units=metric&appid={api_key}"
    )

    try:
        logger.info(f"🌤️ WEATHER PARAMS: lat={lat}, lon={lon}")
        resp = requests.get(weather_url)
        data = resp.json()
        
        logger.info(f"🌤️ RAW WEATHER DATA: {json.dumps(data, indent=2)}")
        
        if "list" not in data:
            state.weather_summary = "Weather data format error."
            return state

        # ... (rest of processing remains same) ...
        from collections import defaultdict
        from datetime import datetime
        
        daily_forecasts = defaultdict(lambda: {"temps": [], "weather": []})
        
        for item in data["list"]:
            dt_txt = item.get("dt_txt", "")
            if not dt_txt: continue
            
            date_str = dt_txt.split(" ")[0]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["main"]
            
            daily_forecasts[date_str]["temps"].append(temp)
            daily_forecasts[date_str]["weather"].append(desc)
            
        processed_weather = []
        full_summary = []
        
        for date, info in sorted(daily_forecasts.items()):
            min_t = min(info["temps"])
            max_t = max(info["temps"])
            main_weather = max(set(info["weather"]), key=info["weather"].count)
            
            try:
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %b %d")
            except:
                day_name = date

            processed_weather.append({
                "date": date,
                "day": day_name,
                "min_temp": round(min_t, 1),
                "max_temp": round(max_t, 1),
                "condition": main_weather,
                "avg_temp": round(sum(info["temps"])/len(info["temps"]), 1)
            })
            
            full_summary.append(f"{day_name}: {main_weather}, {min_t:.0f}-{max_t:.0f}°C")

        state.weather_info = {
            "location": state.destination_city,
            "forecast": processed_weather
        }
        state.weather_summary = " | ".join(full_summary[:5])

    except Exception as e:
        logger.error(f"❌ Weather API Error: {e}")
        state.weather_summary = "Weather currently unavailable."

    return state