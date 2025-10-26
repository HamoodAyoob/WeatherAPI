let currentUnit = "celsius";
let isDarkMode = false;
let autocompleteTimeout;
let currentWeatherData = null;
let tempChart = null;
let precipChart = null;

// Initialize
window.addEventListener("load", () => {
  loadRecentSearches();
  checkDarkModePreference();
  document.getElementById("cityInput").value = "London";
  searchWeather();
});

function checkDarkModePreference() {
  const savedMode = localStorage.getItem("darkMode");
  if (savedMode === "true") {
    isDarkMode = true;
    document.body.classList.add("dark-mode");
    document.getElementById("darkModeBtn").textContent = "☀️ Light Mode";
  }
}

function toggleDarkMode() {
  isDarkMode = !isDarkMode;
  document.body.classList.toggle("dark-mode");
  const btn = document.getElementById("darkModeBtn");
  btn.textContent = isDarkMode ? "☀️ Light Mode" : "🌙 Dark Mode";
  localStorage.setItem("darkMode", isDarkMode);
}

function toggleUnits() {
  currentUnit = currentUnit === "celsius" ? "fahrenheit" : "celsius";
  const btn = document.getElementById("unitBtn");
  btn.textContent = currentUnit === "celsius" ? "°F" : "°C";

  const cityInput = document.getElementById("cityInput");
  if (cityInput.value.trim()) {
    searchWeather();
  }
}

async function handleAutocomplete() {
  const input = document.getElementById("cityInput");
  const query = input.value.trim();
  const dropdown = document.getElementById("autocompleteDropdown");

  if (query.length < 2) {
    dropdown.classList.remove("show");
    return;
  }

  clearTimeout(autocompleteTimeout);
  autocompleteTimeout = setTimeout(async () => {
    try {
      const response = await fetch("/geocode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (data.success && data.results.length > 0) {
        dropdown.innerHTML = "";
        data.results.forEach((result) => {
          const item = document.createElement("div");
          item.className = "autocomplete-item";
          item.textContent = result.display;
          item.onclick = () => {
            input.value = result.name;
            dropdown.classList.remove("show");
            searchWeather();
          };
          dropdown.appendChild(item);
        });
        dropdown.classList.add("show");
      } else {
        dropdown.classList.remove("show");
      }
    } catch (error) {
      console.error("Autocomplete error:", error);
    }
  }, 300);
}

document.addEventListener("click", (e) => {
  const dropdown = document.getElementById("autocompleteDropdown");
  const input = document.getElementById("cityInput");
  if (e.target !== input && e.target !== dropdown) {
    dropdown.classList.remove("show");
  }
});

async function loadRecentSearches() {
  try {
    const response = await fetch("/recent-searches");
    const data = await response.json();

    if (data.success && data.searches.length > 0) {
      const container = document.getElementById("recentSearches");
      const chipsContainer = document.getElementById("recentChips");
      chipsContainer.innerHTML = "";

      data.searches.forEach((city) => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = city;
        chip.onclick = () => {
          document.getElementById("cityInput").value = city;
          searchWeather();
        };
        chipsContainer.appendChild(chip);
      });

      container.classList.remove("hidden");
    }
  } catch (error) {
    console.error("Error loading recent searches:", error);
  }
}

async function getLocationWeather() {
  if (!navigator.geolocation) {
    showError("Geolocation is not supported by your browser");
    return;
  }

  showLoading(true);
  hideError();

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const response = await fetch("/weather-by-coords", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            unit: currentUnit,
          }),
        });

        const data = await response.json();

        if (data.success) {
          document.getElementById("cityInput").value = data.current.city;
          displayWeatherData(data);
          showWeatherContent();
          loadRecentSearches();
        } else {
          showError(data.error || "Failed to fetch weather data");
        }
      } catch (error) {
        showError("Error fetching location weather");
        console.error("Error:", error);
      } finally {
        showLoading(false);
      }
    },
    (error) => {
      showLoading(false);
      showError(
        "Unable to get your location. Please enable location services."
      );
    }
  );
}

async function searchWeather() {
  const cityInput = document.getElementById("cityInput");
  const city = cityInput.value.trim();

  if (!city) {
    showError("Please enter a city name");
    return;
  }

  showLoading(true);
  hideError();
  hideWeatherContent();

  try {
    const response = await fetch("/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city, unit: currentUnit }),
    });

    const data = await response.json();

    if (data.success) {
      currentWeatherData = data;
      displayWeatherData(data);
      showWeatherContent();
      loadRecentSearches();
    } else {
      showError(data.error || "Failed to fetch weather data");
    }
  } catch (error) {
    showError("Network error. Please check your connection and try again.");
    console.error("Error:", error);
  } finally {
    showLoading(false);
  }
}

function displayWeatherData(data) {
  try {
    const current = data.current;
    const unitSymbol = current.unit === "celsius" ? "°C" : "°F";
    const windUnit = current.unit === "celsius" ? "km/h" : "mph";

    const cityDisplay = current.admin1
      ? `${current.city}, ${current.admin1}, ${current.country}`
      : `${current.city}, ${current.country}`;

    document.getElementById("cityName").textContent = cityDisplay;
    document.getElementById("weatherIcon").textContent = current.icon;
    document.getElementById(
      "temperature"
    ).textContent = `${current.temperature}${unitSymbol}`;
    document.getElementById("description").textContent = current.description;
    document.getElementById(
      "feelsLike"
    ).textContent = `${current.feels_like}${unitSymbol}`;
    document.getElementById("humidity").textContent = `${current.humidity}%`;
    document.getElementById(
      "precipitation"
    ).textContent = `${current.precipitation} mm`;
    document.getElementById(
      "windSpeed"
    ).textContent = `${current.wind_speed} ${windUnit}`;
    document.getElementById(
      "windDirection"
    ).textContent = `${current.wind_direction}°`;
    document.getElementById("pressure").textContent = `${current.pressure} hPa`;
    document.getElementById(
      "cloudCover"
    ).textContent = `${current.cloud_cover}%`;
    document.getElementById(
      "visibility"
    ).textContent = `${current.visibility} km`;

    const uvElement = document.getElementById("uvIndex");
    uvElement.textContent = `${current.uv_index} (${current.uv_level})`;

    const aqElement = document.getElementById("airQuality");
    const aqi = current.air_quality.aqi;
    let aqiClass = "aqi-good";
    if (aqi !== "N/A") {
      if (aqi > 150) aqiClass = "aqi-very-unhealthy";
      else if (aqi > 100) aqiClass = "aqi-unhealthy";
      else if (aqi > 50) aqiClass = "aqi-moderate";
    }
    aqElement.innerHTML = `<span class="${aqiClass}">${aqi}</span>`;

    document.getElementById("sunrise").textContent = current.sunrise;
    document.getElementById("sunset").textContent = current.sunset;

    const hourlyContainer = document.getElementById("hourlyForecast");
    hourlyContainer.innerHTML = "";

    data.hourly.forEach((hour) => {
      const card = document.createElement("div");
      card.className = "hourly-card";
      card.innerHTML = `
                        <div class="hourly-time">${hour.time}</div>
                        <div class="hourly-icon">${hour.icon}</div>
                        <div class="hourly-temp">${hour.temperature}${unitSymbol}</div>
                        <div class="hourly-precip">💧 ${hour.precipitation_prob}%</div>
                    `;
      hourlyContainer.appendChild(card);
    });

    const forecastGrid = document.getElementById("forecastGrid");
    forecastGrid.innerHTML = "";

    data.forecast.forEach((day) => {
      const card = document.createElement("div");
      card.className = "forecast-card";
      card.innerHTML = `
                        <div class="forecast-date">${day.date}</div>
                        <div class="forecast-icon">${day.icon}</div>
                        <div class="forecast-temp">${day.temperature_max}°/${day.temperature_min}${unitSymbol}</div>
                        <div class="forecast-desc">${day.description}</div>
                        <div class="forecast-desc">💧 ${day.precipitation}mm (${day.precipitation_prob}%)</div>
                        <div class="forecast-desc">💨 ${day.wind_speed}${windUnit}</div>
                        <div class="forecast-desc">☀️ UV: ${day.uv_index}</div>
                    `;
      forecastGrid.appendChild(card);
    });

    createCharts(data);
  } catch (error) {
    console.error("Error displaying weather data:", error);
    showError("Error displaying weather data");
  }
}

function createCharts(data) {
  const unitSymbol = data.current.unit === "celsius" ? "°C" : "°F";

  if (tempChart) tempChart.destroy();
  if (precipChart) precipChart.destroy();

  const tempCtx = document.getElementById("tempChart").getContext("2d");
  const hourlyLabels = data.hourly.map((h) => h.time);
  const hourlyTemps = data.hourly.map((h) => h.temperature);

  tempChart = new Chart(tempCtx, {
    type: "line",
    data: {
      labels: hourlyLabels,
      datasets: [
        {
          label: `Temperature (${unitSymbol})`,
          data: hourlyTemps,
          borderColor: "#0984e3",
          backgroundColor: "rgba(9, 132, 227, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "24-Hour Temperature Trend",
          font: { size: 16 },
        },
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    },
  });

  const precipCtx = document.getElementById("precipChart").getContext("2d");
  const dailyLabels = data.forecast.map((d) => d.date.split(",")[0]);
  const dailyPrecip = data.forecast.map((d) => d.precipitation);
  const dailyPrecipProb = data.forecast.map((d) => d.precipitation_prob);

  precipChart = new Chart(precipCtx, {
    type: "bar",
    data: {
      labels: dailyLabels,
      datasets: [
        {
          label: "Precipitation (mm)",
          data: dailyPrecip,
          backgroundColor: "rgba(9, 132, 227, 0.6)",
          yAxisID: "y",
        },
        {
          label: "Probability (%)",
          data: dailyPrecipProb,
          type: "line",
          borderColor: "#00b894",
          backgroundColor: "rgba(0, 184, 148, 0.1)",
          yAxisID: "y1",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "5-Day Precipitation Forecast",
          font: { size: 16 },
        },
      },
      scales: {
        y: {
          type: "linear",
          display: true,
          position: "left",
          title: {
            display: true,
            text: "Precipitation (mm)",
          },
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          title: {
            display: true,
            text: "Probability (%)",
          },
          grid: {
            drawOnChartArea: false,
          },
          max: 100,
        },
      },
    },
  });
}

function showTab(tabName) {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("active");
  });
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.remove("active");
  });

  event.target.classList.add("active");
  document.getElementById(tabName + "Tab").classList.add("active");
}

function showLoading(show) {
  const loading = document.getElementById("loading");
  if (show) {
    loading.classList.remove("hidden");
  } else {
    loading.classList.add("hidden");
  }
}

function showError(message) {
  const error = document.getElementById("error");
  error.textContent = message;
  error.classList.remove("hidden");
}

function hideError() {
  const error = document.getElementById("error");
  error.classList.add("hidden");
}

function showWeatherContent() {
  const content = document.getElementById("weatherContent");
  content.classList.remove("hidden");
}

function hideWeatherContent() {
  const content = document.getElementById("weatherContent");
  content.classList.add("hidden");
}
