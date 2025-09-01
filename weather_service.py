import httpx
import os
from typing import Dict, Any, Optional

class WeatherService:
    def __init__(self):
        # Weather Union API (no key required for basic usage)
        self.weather_union_url = "https://www.weatherunion.com/api/v1"
        
        # IMD APIs (no key required)
        self.imd_current_url = "https://mausam.imd.gov.in/api/current_wx_api.php"
        self.imd_forecast_url = "https://city.imd.gov.in/api/cityweather.php"
        
        # Fallback: Open-Meteo (no key required)
        self.open_meteo_url = "https://api.open-meteo.com/v1"
    
    async def get_weather_data(self, city: str, state: str = "") -> Dict[str, Any]:
        """Get current weather data for Indian location using multiple sources"""
        try:
            location = f"{city},{state}" if state else city
            
            async with httpx.AsyncClient() as client:
                # Try Weather Union first (best for India)
                try:
                    weather_union_data = await self._get_weather_union_data(client, city, state)
                    if weather_union_data and "error" not in weather_union_data:
                        return weather_union_data
                except Exception as e:
                    print(f"Weather Union failed: {e}")
                
                # Fallback to IMD APIs
                try:
                    imd_data = await self._get_imd_data(client, city)
                    if imd_data and "error" not in imd_data:
                        return imd_data
                except Exception as e:
                    print(f"IMD API failed: {e}")
                
                # Final fallback to Open-Meteo
                try:
                    open_meteo_data = await self._get_open_meteo_data(client, city, state)
                    if open_meteo_data and "error" not in open_meteo_data:
                        return open_meteo_data
                except Exception as e:
                    print(f"Open-Meteo failed: {e}")
                
                # If all fail, return mock data
                return {
                    "current": self._get_mock_weather_data(city),
                    "forecast": self._get_mock_forecast_data(),
                    "location": location,
                    "source": "mock_data"
                }
                
        except Exception as e:
            return {"error": str(e), "location": location}
    
    async def _get_weather_union_data(self, client: httpx.AsyncClient, city: str, state: str) -> Dict[str, Any]:
        """Get data from Weather Union API"""
        # Note: You'll need to check Weather Union documentation for exact endpoints
        # This is a placeholder structure
        url = f"{self.weather_union_url}/current"
        params = {"city": city, "state": state}
        
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "current": {
                    "temp": data.get("temperature"),
                    "humidity": data.get("humidity"),
                    "pressure": data.get("pressure"),
                    "weather": [{"main": data.get("weather_condition", "Clear")}],
                    "wind": {"speed": data.get("wind_speed", 0)},
                    "rain": {"1h": data.get("rainfall", 0)}
                },
                "location": f"{city}, {state}",
                "source": "weather_union"
            }
        return {"error": "Weather Union API failed"}
    
    async def _get_imd_data(self, client: httpx.AsyncClient, city: str) -> Dict[str, Any]:
        """Get data from IMD APIs"""
        # Current weather from IMD
        current_response = await client.get(f"{self.imd_current_url}?city={city}")
        forecast_response = await client.get(f"{self.imd_forecast_url}?city={city}")
        
        if current_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json() if forecast_response.status_code == 200 else {}
            
            return {
                "current": {
                    "temp": current_data.get("temperature"),
                    "humidity": current_data.get("humidity"),
                    "pressure": current_data.get("pressure"),
                    "weather": [{"main": current_data.get("weather", "Clear")}],
                    "wind": {"speed": current_data.get("wind_speed", 0)},
                    "rain": {"1h": current_data.get("rainfall", 0)}
                },
                "forecast": forecast_data,
                "location": city,
                "source": "imd_official"
            }
        return {"error": "IMD API failed"}
    
    async def _get_open_meteo_data(self, client: httpx.AsyncClient, city: str, state: str) -> Dict[str, Any]:
        """Get data from Open-Meteo (requires lat/lon)"""
        # You'd need to geocode city to lat/lon first
        # For major Indian cities, you can hardcode coordinates
        city_coords = {
            "delhi": {"lat": 28.6139, "lon": 77.2090},
            "mumbai": {"lat": 19.0760, "lon": 72.8777},
            "bangalore": {"lat": 12.9716, "lon": 77.5946},
            "chennai": {"lat": 13.0827, "lon": 80.2707},
            "kolkata": {"lat": 22.5726, "lon": 88.3639},
            "hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "pune": {"lat": 18.5204, "lon": 73.8567},
            "ahmedabad": {"lat": 23.0225, "lon": 72.5714}
        }
        
        coords = city_coords.get(city.lower())
        if not coords:
            return {"error": f"Coordinates not found for {city}"}
        
        url = f"{self.open_meteo_url}/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation",
            "timezone": "Asia/Kolkata"
        }
        
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            
            return {
                "current": {
                    "temp": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "weather": [{"main": "Clear"}],
                    "wind": {"speed": current.get("wind_speed_10m", 0)},
                    "rain": {"1h": current.get("precipitation", 0)}
                },
                "forecast": data.get("hourly", {}),
                "location": f"{city}, {state}",
                "source": "open_meteo"
            }
        return {"error": "Open-Meteo API failed"}
    
    def _get_mock_weather_data(self, city: str) -> Dict[str, Any]:
        """Mock weather data for demonstration"""
        return {
            "temp": 28.5,
            "humidity": 75,
            "pressure": 1013,
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 3.2},
            "rain": {"1h": 0},
            "name": city
        }
    
    def _get_mock_forecast_data(self) -> Dict[str, Any]:
        """Mock forecast data for demonstration"""
        return {
            "list": [
                {
                    "main": {"temp": 29, "humidity": 70},
                    "weather": [{"main": "Clouds", "description": "few clouds"}],
                    "dt_txt": "2025-09-03 12:00:00"
                }
            ]
        }
    
    def get_irrigation_recommendation(self, weather_data: Dict[str, Any], crop: str) -> str:
        """Generate irrigation recommendations based on weather"""
        try:
            current = weather_data.get("current", {})
            temp = current.get("temp", 25)
            humidity = current.get("humidity", 60)
            rain = current.get("rain", {}).get("1h", 0)
            
            if rain > 5:
                return "🌧️ बारिश के कारण सिंचाई की आवश्यकता नहीं। Due to rain, no irrigation needed today."
            elif humidity < 40 and temp > 35:
                return "🔥 अत्यधिक गर्मी - तुरंत सिंचाई करें। Extreme heat - irrigate immediately."
            elif humidity < 60 and temp > 30:
                return "☀️ गर्म मौसम - शाम को सिंचाई करें। Hot weather - irrigate in evening."
            else:
                return "🌤️ मौसम अनुकूल है - नियमित सिंचाई करें। Weather is favorable - regular irrigation."
                
        except Exception:
            return "मौसम डेटा उपलब्ध नहीं। Weather data not available - follow regular irrigation schedule."
