from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# OpenMeteo API configuration (no API key required!)
BASE_URL = 'https://api.open-meteo.com/v1'
GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'

def get_coordinates(city):
    """Get coordinates for a city using OpenMeteo Geocoding API"""
    try:
        params = {
            'name': city,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(GEOCODING_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            return None
            
        location = data['results'][0]
        return {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'name': location['name'],
            'country': location.get('country', ''),
            'admin1': location.get('admin1', '')  # State/Province
        }
        
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def get_weather_code_description(code):
    """Convert weather code to description"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")

def get_weather_icon(code, is_day=True):
    """Get weather icon based on weather code"""
    # Mapping weather codes to simple icon representations
    day_icons = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌦️",
        56: "🌨️", 57: "🌨️",
        61: "🌧️", 63: "🌧️", 65: "⛈️",
        66: "🌨️", 67: "🌨️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
        80: "🌦️", 81: "🌧️", 82: "⛈️",
        85: "🌨️", 86: "🌨️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    
    night_icons = {
        0: "🌙", 1: "🌙", 2: "☁️", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌦️",
        56: "🌨️", 57: "🌨️",
        61: "🌧️", 63: "🌧️", 65: "⛈️",
        66: "🌨️", 67: "🌨️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
        80: "🌦️", 81: "🌧️", 82: "⛈️",
        85: "🌨️", 86: "🌨️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    
    icons = day_icons if is_day else night_icons
    return icons.get(code, "❓")

def get_weather_data(city):
    """Fetch current weather data for a city using OpenMeteo API"""
    try:
        # First, get coordinates for the city
        location = get_coordinates(city)
        if not location:
            return {'success': False, 'error': f'City "{city}" not found'}
        
        # Get current weather and forecast
        weather_url = f"{BASE_URL}/forecast"
        params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'current': ['temperature_2m', 'relative_humidity_2m', 'apparent_temperature', 'is_day', 'precipitation', 'weather_code', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m'],
            'daily': ['weather_code', 'temperature_2m_max', 'temperature_2m_min', 'sunrise', 'sunset', 'precipitation_sum', 'wind_speed_10m_max'],
            'timezone': 'auto',
            'forecast_days': 7
        }
        
        response = requests.get(weather_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Debug: Print the response structure
        print("API Response keys:", data.keys())
        if 'current' in data:
            print("Current data keys:", data['current'].keys())
        if 'daily' in data:
            print("Daily data keys:", data['daily'].keys())
        
        current = data['current']
        daily = data['daily']
        
        # Process current weather
        current_weather = {
            'city': location['name'],
            'country': location['country'],
            'admin1': location.get('admin1', ''),
            'temperature': round(current['temperature_2m']),
            'feels_like': round(current['apparent_temperature']),
            'description': get_weather_code_description(current['weather_code']),
            'icon': get_weather_icon(current['weather_code'], current['is_day']),
            'humidity': current['relative_humidity_2m'],
            'pressure': round(current['surface_pressure']),
            'wind_speed': round(current['wind_speed_10m'], 1),
            'wind_direction': round(current['wind_direction_10m']),
            'precipitation': current.get('precipitation', 0),
            'sunrise': daily['sunrise'][0].split('T')[1][:5] if daily.get('sunrise') and daily['sunrise'][0] else 'N/A',
            'sunset': daily['sunset'][0].split('T')[1][:5] if daily.get('sunset') and daily['sunset'][0] else 'N/A'
        }
        
        # Process forecast (skip today, get next 5 days)
        daily_forecasts = []
        for i in range(1, min(6, len(daily['time']))):
            date_str = daily['time'][i]
            date_obj = datetime.fromisoformat(date_str)
            
            daily_forecasts.append({
                'date': date_obj.strftime('%A, %B %d'),
                'temperature_max': round(daily['temperature_2m_max'][i]),
                'temperature_min': round(daily['temperature_2m_min'][i]),
                'description': get_weather_code_description(daily['weather_code'][i]),
                'icon': get_weather_icon(daily['weather_code'][i], True),
                'precipitation': daily['precipitation_sum'][i],
                'wind_speed': round(daily['wind_speed_10m_max'][i], 1)
            })
        
        return {
            'success': True,
            'current': current_weather,
            'forecast': daily_forecasts
        }
        
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'API request failed: {str(e)}'}
    except KeyError as e:
        return {'success': False, 'error': f'Invalid API response: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'An error occurred: {str(e)}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    city = data.get('city', '').strip()
    
    if not city:
        return jsonify({'success': False, 'error': 'City name is required'})
    
    weather_data = get_weather_data(city)
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True)