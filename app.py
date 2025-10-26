from flask import Flask, render_template, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import requests
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure caching
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 600  # 10 minutes
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# OpenMeteo API configuration
BASE_URL = 'https://api.open-meteo.com/v1'
GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'

def get_coordinates(city):
    """Get coordinates for a city using OpenMeteo Geocoding API"""
    try:
        params = {
            'name': city,
            'count': 5,  # Get top 5 results for autocomplete
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
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
            'admin1': location.get('admin1', '')
        }
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout. Please try again.'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Network connection error. Please check your internet.'}
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def get_weather_code_description(code):
    """Convert weather code to description"""
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
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

def get_uv_index_level(uv):
    """Get UV index risk level"""
    if uv < 3:
        return "Low"
    elif uv < 6:
        return "Moderate"
    elif uv < 8:
        return "High"
    elif uv < 11:
        return "Very High"
    else:
        return "Extreme"

@cache.memoize(timeout=600)
def get_weather_data(city, unit='celsius'):
    """Fetch weather data with caching"""
    try:
        location = get_coordinates(city)
        if not location:
            return {'success': False, 'error': f'City "{city}" not found'}
        
        if 'error' in location:
            return {'success': False, 'error': location['error']}
        
        # Temperature unit
        temp_unit = 'celsius' if unit == 'celsius' else 'fahrenheit'
        wind_unit = 'kmh' if unit == 'celsius' else 'mph'
        
        # Get current weather, hourly, and daily forecast
        weather_url = f"{BASE_URL}/forecast"
        params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'current': [
                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature', 
                'is_day', 'precipitation', 'weather_code', 'surface_pressure', 
                'wind_speed_10m', 'wind_direction_10m', 'cloud_cover', 
                'visibility', 'uv_index'
            ],
            'hourly': [
                'temperature_2m', 'weather_code', 'precipitation_probability',
                'precipitation', 'wind_speed_10m'
            ],
            'daily': [
                'weather_code', 'temperature_2m_max', 'temperature_2m_min', 
                'sunrise', 'sunset', 'precipitation_sum', 'wind_speed_10m_max',
                'precipitation_probability_max', 'uv_index_max'
            ],
            'temperature_unit': temp_unit,
            'wind_speed_unit': wind_unit,
            'timezone': 'auto',
            'forecast_days': 7
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        daily = data['daily']
        hourly = data['hourly']
        
        # Get air quality data
        air_quality_url = f"{BASE_URL}/air-quality"
        aq_params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'current': ['us_aqi', 'pm10', 'pm2_5']
        }
        
        try:
            aq_response = requests.get(air_quality_url, params=aq_params, timeout=5)
            aq_data = aq_response.json()
            air_quality = {
                'aqi': aq_data['current'].get('us_aqi', 'N/A'),
                'pm10': aq_data['current'].get('pm10', 'N/A'),
                'pm25': aq_data['current'].get('pm2_5', 'N/A')
            }
        except:
            air_quality = {'aqi': 'N/A', 'pm10': 'N/A', 'pm25': 'N/A'}
        
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
            'cloud_cover': current.get('cloud_cover', 'N/A'),
            'visibility': round(current.get('visibility', 0) / 1000, 1) if current.get('visibility') else 'N/A',
            'uv_index': current.get('uv_index', 'N/A'),
            'uv_level': get_uv_index_level(current.get('uv_index', 0)) if current.get('uv_index') else 'N/A',
            'sunrise': daily['sunrise'][0].split('T')[1][:5] if daily.get('sunrise') else 'N/A',
            'sunset': daily['sunset'][0].split('T')[1][:5] if daily.get('sunset') else 'N/A',
            'air_quality': air_quality,
            'unit': unit
        }
        
        # Process 24-hour hourly forecast
        hourly_forecasts = []
        current_hour = datetime.now().hour
        for i in range(24):
            hour_data = {
                'time': hourly['time'][i].split('T')[1][:5],
                'temperature': round(hourly['temperature_2m'][i]),
                'icon': get_weather_icon(hourly['weather_code'][i], True),
                'precipitation_prob': hourly['precipitation_probability'][i],
                'precipitation': hourly['precipitation'][i],
                'wind_speed': round(hourly['wind_speed_10m'][i], 1)
            }
            hourly_forecasts.append(hour_data)
        
        # Process 5-day forecast
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
                'precipitation_prob': daily['precipitation_probability_max'][i],
                'wind_speed': round(daily['wind_speed_10m_max'][i], 1),
                'uv_index': daily['uv_index_max'][i]
            })
        
        return {
            'success': True,
            'current': current_weather,
            'hourly': hourly_forecasts,
            'forecast': daily_forecasts
        }
        
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timeout. Please try again.'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Network connection error.'}
    except KeyError as e:
        return {'success': False, 'error': f'Invalid API response: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'An error occurred: {str(e)}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
@limiter.limit("30 per minute")
def get_weather():
    data = request.get_json()
    city = data.get('city', '').strip()
    unit = data.get('unit', 'celsius')
    
    if not city:
        return jsonify({'success': False, 'error': 'City name is required'})
    
    # Store in recent searches
    if 'recent_searches' not in session:
        session['recent_searches'] = []
    
    if city not in session['recent_searches']:
        session['recent_searches'].insert(0, city)
        session['recent_searches'] = session['recent_searches'][:5]
        session.modified = True
    
    weather_data = get_weather_data(city, unit)
    return jsonify(weather_data)

@app.route('/geocode', methods=['POST'])
@limiter.limit("60 per minute")
def geocode():
    """Autocomplete endpoint for city search"""
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify({'success': True, 'results': []})
    
    try:
        params = {
            'name': query,
            'count': 5,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(GEOCODING_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if data.get('results'):
            for loc in data['results']:
                results.append({
                    'name': loc['name'],
                    'country': loc.get('country', ''),
                    'admin1': loc.get('admin1', ''),
                    'display': f"{loc['name']}, {loc.get('admin1', '')}, {loc.get('country', '')}" if loc.get('admin1') else f"{loc['name']}, {loc.get('country', '')}"
                })
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/recent-searches', methods=['GET'])
def get_recent_searches():
    """Get recent searches from session"""
    return jsonify({
        'success': True,
        'searches': session.get('recent_searches', [])
    })

@app.route('/weather-by-coords', methods=['POST'])
@limiter.limit("30 per minute")
def get_weather_by_coords():
    """Get weather by coordinates (for geolocation)"""
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')
    unit = data.get('unit', 'celsius')
    
    if not lat or not lon:
        return jsonify({'success': False, 'error': 'Coordinates required'})
    
    try:
        # Reverse geocode to get city name
        params = {
            'latitude': lat,
            'longitude': lon,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get('results'):
            city = data['results'][0]['name']
            weather_data = get_weather_data(city, unit)
            return jsonify(weather_data)
        else:
            return jsonify({'success': False, 'error': 'Location not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)