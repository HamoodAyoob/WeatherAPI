# 🌤️ Advanced Weather App

A feature-rich weather application built with Flask and OpenMeteo API, offering real-time weather information, forecasts, and interactive visualizations.

## ✨ Features

### Core Features
- **Real-time Weather Data**: Current weather conditions for any city worldwide
- **5-Day Forecast**: Detailed daily forecasts with temperature, precipitation, wind, and UV index
- **24-Hour Forecast**: Hourly weather predictions for the next day
- **Geolocation Support**: Auto-detect weather for your current location
- **Search Autocomplete**: Smart city search with suggestions as you type

### Advanced Features
- **Unit Conversion**: Toggle between Celsius/Fahrenheit and km/h/mph
- **Dark Mode**: Eye-friendly dark theme with persistent preference
- **Recent Searches**: Quick access to previously searched cities
- **Interactive Charts**: Visual temperature and precipitation trends using Chart.js
- **Air Quality Index**: Real-time AQI data with health recommendations
- **UV Index**: Sun exposure risk levels
- **Extended Metrics**: Cloud cover, visibility, wind direction, and more

### Performance & Security
- **Response Caching**: 10-minute cache to reduce API calls
- **Rate Limiting**: Protection against abuse (50 requests/hour per IP)
- **Error Handling**: Comprehensive error messages for better UX
- **Responsive Design**: Mobile-friendly interface with smooth animations

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd weather-app

# Or download and extract the ZIP file
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Secret Key (Optional but Recommended)
For production, set a secure secret key:

```bash
# Windows
set SECRET_KEY=your-secure-random-key-here

# macOS/Linux
export SECRET_KEY=your-secure-random-key-here
```

### Step 5: Run the Application
```bash
python app.py
```

The app will start on `http://127.0.0.1:5000`

## 📁 Project Structure

```
weather-app/
│
├── app.py              # Flask backend with API endpoints
├── requirements.txt    # Python dependencies
├── README.md          # This file
│
└── templates/
    └── index.html     # Frontend with HTML, CSS, and JavaScript
```

## 🔧 Configuration

### Cache Settings
Edit `app.py` to modify cache timeout (default: 10 minutes):
```python
'CACHE_DEFAULT_TIMEOUT': 600  # seconds
```

### Rate Limiting
Adjust rate limits in `app.py`:
```python
default_limits=["200 per day", "50 per hour"]
```

### API Endpoints
The app uses OpenMeteo API (no API key required):
- Weather Data: `https://api.open-meteo.com/v1/forecast`
- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Air Quality: `https://api.open-meteo.com/v1/air-quality`

## 🎯 Usage

### Basic Search
1. Enter a city name in the search box
2. Select from autocomplete suggestions or press Enter
3. View current weather and forecasts

### Using Geolocation
1. Click the "📍 Use My Location" button
2. Allow location access when prompted
3. Weather for your current location will be displayed

### Switching Units
- Click "°C / °F" button to toggle temperature units
- Wind speed automatically converts between km/h and mph

### Dark Mode
- Click "🌙 Dark Mode" button to toggle theme
- Preference is saved in browser localStorage

### Viewing Forecasts
- **24-Hour Tab**: Scroll through hourly weather predictions
- **5-Day Tab**: View detailed daily forecasts
- **Charts Tab**: Interactive temperature and precipitation graphs

## 📱 Mobile Support

The app is fully responsive and works on:
- Smartphones (portrait and landscape)
- Tablets
- Desktop browsers

## 🛠️ API Endpoints

### Frontend Endpoints
- `GET /` - Main application page
- `POST /weather` - Get weather data for a city
- `POST /geocode` - Autocomplete city search
- `GET /recent-searches` - Get user's recent searches
- `POST /weather-by-coords` - Get weather by latitude/longitude

### Request Examples

#### Get Weather by City
```json
POST /weather
{
  "city": "London",
  "unit": "celsius"
}
```

#### Get Weather by Coordinates
```json
POST /weather-by-coords
{
  "latitude": 51.5074,
  "longitude": -0.1278,
  "unit": "celsius"
}
```

#### Autocomplete Search
```json
POST /geocode
{
  "query": "Lond"
}
```

## 🎨 Customization

### Changing Colors
Edit the CSS variables in `index.html`:
```css
:root {
    --primary-color: #0984e3;
    --secondary-color: #74b9ff;
    --dark-color: #2d3436;
    --error-color: #ff7675;
    --success-color: #00b894;
}
```

### Modifying Background
Change the gradient in the `body` selector:
```css
body {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
}
```

### Adding More Weather Metrics
OpenMeteo API supports many additional parameters. Edit the `params` in `get_weather_data()`:
```python
'current': [
    'temperature_2m',
    'relative_humidity_2m',
    # Add more parameters here
    'soil_temperature_0cm',
    'rain',
    'snowfall'
]
```

## 🔍 Troubleshooting

### Port Already in Use
If port 5000 is occupied, change it in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### API Rate Limiting
If you hit rate limits, the app will show an error. Wait a few minutes or adjust limits in `app.py`.

### Geolocation Not Working
- Ensure you're using HTTPS or localhost
- Check browser location permissions
- Some browsers block location on HTTP connections

### Charts Not Displaying
Make sure Chart.js is loading correctly. Check browser console for errors.

## 🚀 Deployment

### Heroku Deployment
1. Create a `Procfile`:
```
web: gunicorn app:app
```

2. Add gunicorn to requirements:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t weather-app .
docker run -p 5000:5000 weather-app
```

### Production Considerations
1. Set `debug=False` in app.py
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set a strong SECRET_KEY environment variable
4. Use Redis for caching instead of simple memory cache
5. Enable HTTPS
6. Set up proper logging

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Sanitizes user inputs
- **Error Handling**: Prevents information leakage
- **Session Security**: Uses secure session management
- **CORS Protection**: Built into Flask

## 📊 Data Sources

- **Weather Data**: [OpenMeteo API](https://open-meteo.com/)
- **Geocoding**: OpenMeteo Geocoding API
- **Air Quality**: OpenMeteo Air Quality API

All data is free and doesn't require API keys!

## 🤝 Contributing

Suggestions for improvements:
1. Add weather alerts/warnings
2. Implement favorite locations
3. Add weather radar maps
4. Include pollen count
5. Add historical weather data
6. Implement push notifications
7. Add weather comparison between cities
8. Create a mobile app version

## 📝 License

This project is open source and available for personal and commercial use.

## 🙏 Acknowledgments

- OpenMeteo for providing free weather API
- Chart.js for beautiful charts
- Flask community for the excellent framework

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review OpenMeteo API documentation
3. Check browser console for errors
4. Ensure all dependencies are installed

## 🔄 Updates & Changelog

### Version 2.0 (Current)
- ✅ Added 24-hour hourly forecast
- ✅ Implemented dark mode
- ✅ Added unit conversion (°C/°F)
- ✅ Geolocation support
- ✅ Search autocomplete
- ✅ Recent searches feature
- ✅ Interactive charts
- ✅ Air quality index
- ✅ UV index with risk levels
- ✅ Enhanced error handling
- ✅ Response caching
- ✅ Rate limiting
- ✅ Mobile responsive design
- ✅ Extended weather metrics

### Version 1.0 (Previous)
- Basic weather search
- 5-day forecast
- Current weather display

## 🎓 Learning Resources

If you want to learn more about the technologies used:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenMeteo API Docs](https://open-meteo.com/en/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [MDN Web Docs](https://developer.mozilla.org/) - for HTML/CSS/JavaScript

---

**Enjoy using the Weather App! ☀️🌧️⛈️❄️**