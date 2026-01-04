import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_weather(state):
    """Fetch weather using OpenWeatherMap based on destination."""
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        state.weather_summary = "Weather data unavailable (Missing API Key)."
        return state

    # 1. Get coordinates
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={state.destination}&limit=1&appid={api_key}"
        geo_data = requests.get(geo_url).json()
        
        if not geo_data:
            state.weather_summary = f"Could not find coordinates for {state.destination}."
            return state

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

    except Exception as e:
        print(f"Weather Geocoding Error: {e}")
        state.weather_summary = "Weather unavailable."
        return state

    # 2. Get forecast (5 day / 3 hour)
    # Using metric units for Celsius
    weather_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&units=metric&appid={api_key}"
    )

    try:
        data = requests.get(weather_url).json()
        
        if "list" not in data:
            state.weather_summary = "Weather data format error."
            return state

        # Process standard 5-day forecast (grouped by date)
        # OpenWeather returns list of 3-hour segments
        from collections import defaultdict
        from datetime import datetime
        
        daily_forecasts = defaultdict(lambda: {"temps": [], "weather": []})
        
        for item in data["list"]:
            dt_txt = item.get("dt_txt", "")
            if not dt_txt: continue
            
            # extract date YYYY-MM-DD
            date_str = dt_txt.split(" ")[0]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["main"] # e.g. Rain, Clouds, Clear
            
            daily_forecasts[date_str]["temps"].append(temp)
            daily_forecasts[date_str]["weather"].append(desc)
            
        # Build structured weather info
        processed_weather = []
        full_summary = []
        
        for date, info in sorted(daily_forecasts.items()):
            min_t = min(info["temps"])
            max_t = max(info["temps"])
            # Most common weather condition for that day
            main_weather = max(set(info["weather"]), key=info["weather"].count)
            
            # Format day
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
            "location": state.destination,
            "forecast": processed_weather
        }
        state.weather_summary = " | ".join(full_summary[:5]) # Keep summary for compatibility

    except Exception as e:
        print(f"Weather API Error: {e}")
        state.weather_summary = "Weather currently unavailable."

    return state