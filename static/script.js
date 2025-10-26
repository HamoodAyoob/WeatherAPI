        async function searchWeather() {
            const cityInput = document.getElementById('cityInput');
            const city = cityInput.value.trim();
            
            if (!city) {
                showError('Please enter a city name');
                return;
            }
            
            showLoading(true);
            hideError();
            hideWeatherContent();
            
            try {
                const response = await fetch('/weather', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ city: city })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayWeatherData(data);
                    showWeatherContent();
                } else {
                    showError(data.error || 'Failed to fetch weather data');
                }
            } catch (error) {
                showError('Network error. Please check your connection and try again.');
                console.error('Error:', error);
            } finally {
                showLoading(false);
            }
        }
        
        function displayWeatherData(data) {
            const current = data.current;
            
            // Current weather
            const cityDisplay = current.admin1 ? 
                `${current.city}, ${current.admin1}, ${current.country}` : 
                `${current.city}, ${current.country}`;
            
            document.getElementById('cityName').textContent = cityDisplay;
            document.getElementById('weatherIcon').textContent = current.icon;
            document.getElementById('temperature').textContent = `${current.temperature}°C`;
            document.getElementById('description').textContent = current.description;
            document.getElementById('feelsLike').textContent = `${current.feels_like}°C`;
            document.getElementById('humidity').textContent = `${current.humidity}%`;
            document.getElementById('precipitation').textContent = `${current.precipitation} mm`;
            document.getElementById('wind').textContent = `${current.wind_speed} m/s`;
            document.getElementById('pressure').textContent = `${current.pressure} hPa`;
            document.getElementById('sunTimes').textContent = `${current.sunrise} / ${current.sunset}`;
            
            // Forecast
            const forecastGrid = document.getElementById('forecastGrid');
            forecastGrid.innerHTML = '';
            
            data.forecast.forEach(day => {
                const forecastCard = document.createElement('div');
                forecastCard.className = 'forecast-card';
                forecastCard.innerHTML = `
                    <div class="forecast-date">${day.date}</div>
                    <div class="forecast-icon">${day.icon}</div>
                    <div class="forecast-temp">${day.temperature_max}°/${day.temperature_min}°C</div>
                    <div class="forecast-desc">${day.description}</div>
                    <div class="forecast-desc">💧 ${day.precipitation}mm</div>
                `;
                forecastGrid.appendChild(forecastCard);
            });
        }
        
        function showLoading(show) {
            const loading = document.getElementById('loading');
            if (show) {
                loading.classList.remove('hidden');
            } else {
                loading.classList.add('hidden');
            }
        }
        
        function showError(message) {
            const error = document.getElementById('error');
            error.textContent = message;
            error.classList.remove('hidden');
        }
        
        function hideError() {
            const error = document.getElementById('error');
            error.classList.add('hidden');
        }
        
        function showWeatherContent() {
            const content = document.getElementById('weatherContent');
            content.classList.remove('hidden');
        }
        
        function hideWeatherContent() {
            const content = document.getElementById('weatherContent');
            content.classList.add('hidden');
        }
        
        // Load default city on page load
        window.addEventListener('load', () => {
            document.getElementById('cityInput').value = 'London';
            searchWeather();
        });