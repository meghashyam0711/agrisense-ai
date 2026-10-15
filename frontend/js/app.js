/**
 * AgriSense-AI: Main Application Controller & Frontend Integration (Phase 9)
 * Connects UI to FastAPI backend endpoints:
 * - Yield prediction (Random Forest inference)
 * - Agro-meteorological center (Open-Meteo live feed)
 * - Smart agronomic recommendations (TNAU expert rule engine)
 * - Historical audits & harvest tracking (SQLite database)
 * - Bilingual localization (English & Tamil) with persistence
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    currentLang: "en",
    activeTab: "dashboard",
    selectedDistrict: "Thanjavur",
    selectedSeason: "Samba",
    historyRecords: [],
    currentPrediction: null,
    lastRecommendations: null,
    soilNutrients: { N: 135, P: 45, K: 42, pH: 6.8, moisture: 74 },
    backendOnline: false
  };

  // Toast Notification System
  function showToast(message, icon = "✓") {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // --- 1. Language Localization Engine ---
  function applyLanguage(lang) {
    state.currentLang = lang;
    try {
      localStorage.setItem("agrisense_language", lang);
    } catch (e) {
      console.warn("Could not persist language to localStorage:", e);
    }
    document.documentElement.lang = lang;

    const dict = window.I18N_DICTIONARY ? window.I18N_DICTIONARY[lang] : null;
    if (!dict) return;

    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (dict[key]) {
        el.setAttribute("placeholder", dict[key]);
      }
    });

    // Update active state on toggle buttons
    const btnEn = document.getElementById("lang-en");
    const btnTa = document.getElementById("lang-ta");
    if (btnEn && btnTa) {
      if (lang === "en") {
        btnEn.classList.add("active");
        btnEn.setAttribute("aria-pressed", "true");
        btnTa.classList.remove("active");
        btnTa.setAttribute("aria-pressed", "false");
      } else {
        btnTa.classList.add("active");
        btnTa.setAttribute("aria-pressed", "true");
        btnEn.classList.remove("active");
        btnEn.setAttribute("aria-pressed", "false");
      }
    }

    // Refresh dynamic components that render localized data
    renderDashboard();
    renderWeatherPage();
    renderSoilAnalysis();
    renderRecommendations();
    renderHistoryTable();
  }

  // Language switch button bindings with localized toasts
  const btnEn = document.getElementById("lang-en");
  const btnTa = document.getElementById("lang-ta");
  if (btnEn) {
    btnEn.addEventListener("click", () => {
      applyLanguage("en");
      showToast(window.I18N_DICTIONARY?.en?.msg_lang_switched || "Language switched to English");
    });
  }
  if (btnTa) {
    btnTa.addEventListener("click", () => {
      applyLanguage("ta");
      showToast(window.I18N_DICTIONARY?.ta?.msg_lang_switched || "மொழி தமிழுக்கு மாற்றப்பட்டது");
    });
  }

  // --- 2. Navigation Tab Switcher ---
  function switchTab(tabId) {
    state.activeTab = tabId;

    document.querySelectorAll(".nav-tab-btn").forEach(btn => {
      if (btn.dataset.tab === tabId) {
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
      } else {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
      }
    });

    document.querySelectorAll(".tab-view").forEach(view => {
      if (view.id === `tab-${tabId}`) {
        view.classList.add("active");
      } else {
        view.classList.remove("active");
      }
    });

    if (tabId === "dashboard") renderDashboard();
    if (tabId === "weather") renderWeatherPage();
    if (tabId === "soil") renderSoilAnalysis();
    if (tabId === "recommendations") renderRecommendations();
    if (tabId === "history") renderHistoryTable();

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  document.querySelectorAll(".nav-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  const linkToPredict = document.getElementById("dash-btn-predict");
  if (linkToPredict) linkToPredict.addEventListener("click", () => switchTab("prediction"));

  const linkToRecom = document.getElementById("dash-btn-recom");
  if (linkToRecom) linkToRecom.addEventListener("click", () => switchTab("recommendations"));

  // Check Backend Connectivity
  async function verifyBackendHealth() {
    try {
      const health = await AgriApiClient.checkHealth();
      state.backendOnline = health.status === "healthy" || health.status === "operational";
      return health;
    } catch (e) {
      state.backendOnline = false;
      return null;
    }
  }

  // --- 3. Dashboard Component ---
  async function renderDashboard() {
    const dInfo = AGRI_DATA.districts[state.selectedDistrict] || AGRI_DATA.districts["Thanjavur"];

    const dashWeatherTemp = document.getElementById("dash-weather-temp");
    const dashWeatherCond = document.getElementById("dash-weather-cond");
    const dashWeatherDistrict = document.getElementById("dash-weather-district");

    if (dashWeatherDistrict) {
      dashWeatherDistrict.textContent = state.currentLang === "ta" ? dInfo.name_ta : state.selectedDistrict;
    }

    // Try fetching live weather for dashboard preview
    try {
      const liveWeather = await AgriApiClient.fetchCurrentWeather(state.selectedDistrict);
      if (dashWeatherTemp) dashWeatherTemp.textContent = `${liveWeather.temperature_c.toFixed(1)}°C`;
      if (dashWeatherCond) dashWeatherCond.textContent = liveWeather.weather_condition;
    } catch (_) {
      // Fallback to regional baseline
      if (dashWeatherTemp) dashWeatherTemp.textContent = `${dInfo.currentWeather.temp}°C`;
      if (dashWeatherCond) {
        dashWeatherCond.textContent = state.currentLang === "ta" ? dInfo.currentWeather.condition_ta : dInfo.currentWeather.condition;
      }
    }

    // Render Gauges
    AgriCharts.renderCircularGauge(
      "dash-moisture-gauge-container",
      state.soilNutrients.moisture,
      "%",
      state.currentLang === "ta" ? "மண் ஈரப்பதம்" : "Moisture Level",
      "#06b6d4"
    );

    AgriCharts.renderCircularGauge(
      "dash-yield-gauge-container",
      state.currentPrediction ? Math.min(Math.round((state.currentPrediction.predicted_yield_kg_per_hectare / 5200) * 100), 96) : 88,
      "/100",
      state.currentLang === "ta" ? "பயிர் ஆரோக்கியம்" : "Health Score",
      "#10b981"
    );
  }

  // --- 4. Weather Center Component ---
  async function renderWeatherPage() {
    const districtSelect = document.getElementById("weather-district-select");
    const dName = districtSelect ? districtSelect.value : state.selectedDistrict;
    const dFallback = AGRI_DATA.districts[dName] || AGRI_DATA.districts["Thanjavur"];

    const currentCard = document.getElementById("weather-current-display");
    const forecastList = document.getElementById("weather-forecast-list");
    const sparklineContainer = document.getElementById("weather-sparkline-container");

    if (currentCard) {
      currentCard.innerHTML = `
        <div class="glass-panel" style="padding: 2rem; text-align: center;">
          <div class="glass-spinner"></div>
          <div style="color: var(--accent-cyan); margin-top: 0.75rem; font-size: 0.85rem;">
            ${state.currentLang === "ta" ? "வானிலை தகவல் பெறப்படுகிறது..." : "Fetching live Open-Meteo weather data..."}
          </div>
        </div>
      `;
    }

    try {
      // Fetch live current conditions and 5-day forecast concurrently
      const [currWeather, forecastWeather] = await Promise.all([
        AgriApiClient.fetchCurrentWeather(dName),
        AgriApiClient.fetchForecast(dName, 5)
      ]);

      const distName = state.currentLang === "ta" ? (dFallback.name_ta || dName) : dName;
      const zoneName = state.currentLang === "ta" ? dFallback.zone_ta : dFallback.zone;

      if (currentCard) {
        currentCard.innerHTML = `
          <div class="weather-hero-card glass-panel">
            <div>
              <span class="badge badge-cyan">${zoneName}</span>
              <h3 style="font-size: 1.85rem; font-weight: 700; margin-top: 0.5rem; color: #ffffff;">${distName}</h3>
              <p style="color: var(--text-muted); font-size: 0.9rem;">${currWeather.weather_condition}</p>
            </div>
            <div style="text-align: right;">
              <div class="weather-hero-temp">${currWeather.temperature_c.toFixed(1)}°C</div>
              <div style="color: var(--text-muted); font-size: 0.8rem;">Observed: ${currWeather.observation_time || 'Live'}</div>
            </div>
          </div>

          <div class="weather-grid-4">
            <div class="weather-sub-item">
              <div class="title">${state.currentLang === "ta" ? "காற்று ஈரப்பதம்" : "Humidity"}</div>
              <div class="val">${currWeather.relative_humidity_pct.toFixed(0)}%</div>
            </div>
            <div class="weather-sub-item">
              <div class="title">${state.currentLang === "ta" ? "மழைப்பொழிவு" : "Precipitation"}</div>
              <div class="val">${currWeather.precipitation_mm.toFixed(1)} mm</div>
            </div>
            <div class="weather-sub-item">
              <div class="title">${state.currentLang === "ta" ? "காற்றின் வேகம்" : "Wind Speed"}</div>
              <div class="val">${currWeather.wind_speed_kmh.toFixed(1)} km/h</div>
            </div>
            <div class="weather-sub-item">
              <div class="title">${state.currentLang === "ta" ? "வானிலை நிலை" : "Condition"}</div>
              <div class="val" style="font-size: 0.95rem;">${currWeather.weather_condition}</div>
            </div>
          </div>
        `;
      }

      // Render Forecast List
      if (forecastList && forecastWeather.daily_forecast) {
        forecastList.innerHTML = forecastWeather.daily_forecast.map((item, idx) => {
          const dateObj = new Date(item.date);
          const dayName = dateObj.toLocaleDateString(state.currentLang === "ta" ? "ta-IN" : "en-US", { weekday: "short" });
          const rainProb = item.precipitation_probability_pct ?? 0;
          return `
            <div class="forecast-item">
              <div style="display: flex; align-items: center; gap: 0.75rem; width: 35%;">
                <span style="font-weight: 600; color: #ffffff; min-width: 45px;">${dayName}</span>
                <span style="font-size: 0.825rem; color: var(--text-muted);">${item.weather_condition}</span>
              </div>
              <div style="font-size: 0.825rem; color: var(--accent-leaf); width: 30%; text-align: center;">
                🌧️ ${rainProb}% rain (${item.precipitation_sum_mm.toFixed(1)}mm)
              </div>
              <div style="font-weight: 600; font-size: 0.9rem; color: #ffffff; width: 35%; text-align: right;">
                ${item.temperature_max_c.toFixed(0)}° / <span style="color: var(--text-muted); font-size: 0.8rem;">${item.temperature_min_c.toFixed(0)}°C</span>
              </div>
            </div>
          `;
        }).join("");

        // Render Sparkline with real forecast items
        const sparklineData = forecastWeather.daily_forecast.map(item => ({
          high: item.temperature_max_c,
          rainProb: item.precipitation_probability_pct || 0
        }));
        AgriCharts.renderWeatherSparkline("weather-sparkline-container", sparklineData);
      }

    } catch (err) {
      console.warn("Could not retrieve live weather, using regional fallback:", err);
      // Fallback to AGRI_DATA
      if (currentCard) {
        const cond = state.currentLang === "ta" ? dFallback.currentWeather.condition_ta : dFallback.currentWeather.condition;
        const distName = state.currentLang === "ta" ? dFallback.name_ta : dName;
        const zoneName = state.currentLang === "ta" ? dFallback.zone_ta : dFallback.zone;

        currentCard.innerHTML = `
          <div style="padding: 0.5rem 1rem; margin-bottom: 0.75rem; background: rgba(245, 158, 11, 0.15); border: 1px solid var(--accent-amber); border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--accent-amber); display: flex; justify-content: space-between; align-items: center;">
            <span>⚠️ Live weather service unreachable. Showing district climatological baseline.</span>
            <button id="btn-retry-weather" class="btn btn-secondary btn-sm" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;">Retry</button>
          </div>
          <div class="weather-hero-card glass-panel">
            <div>
              <span class="badge badge-cyan">${zoneName}</span>
              <h3 style="font-size: 1.85rem; font-weight: 700; margin-top: 0.5rem; color: #ffffff;">${distName}</h3>
              <p style="color: var(--text-muted); font-size: 0.9rem;">${cond}</p>
            </div>
            <div style="text-align: right;">
              <div class="weather-hero-temp">${dFallback.currentWeather.temp}°C</div>
              <div style="color: var(--text-muted); font-size: 0.8rem;">Dew Point: ${dFallback.currentWeather.dewPoint}°C</div>
            </div>
          </div>
        `;
        const retryBtn = document.getElementById("btn-retry-weather");
        if (retryBtn) retryBtn.addEventListener("click", renderWeatherPage);
      }
    }
  }

  const weatherDistrictSelect = document.getElementById("weather-district-select");
  if (weatherDistrictSelect) {
    weatherDistrictSelect.addEventListener("change", (e) => {
      state.selectedDistrict = e.target.value;
      renderWeatherPage();
    });
  }

  // --- 5. Yield Prediction Engine & Form Integration ---
  const autofillBtn = document.getElementById("btn-autofill-weather");
  if (autofillBtn) {
    autofillBtn.addEventListener("click", async () => {
      const districtEl = document.getElementById("pred-district");
      const dName = districtEl ? districtEl.value : state.selectedDistrict;
      const dFallback = AGRI_DATA.districts[dName] || AGRI_DATA.districts["Thanjavur"];

      const rainfallEl = document.getElementById("pred-rainfall");
      const tempEl = document.getElementById("pred-temp");
      const humidityEl = document.getElementById("pred-humidity");
      const moistureEl = document.getElementById("pred-moisture");
      const soilTypeEl = document.getElementById("pred-soil");

      if (rainfallEl) rainfallEl.value = dFallback.avgRainfall;
      if (moistureEl) moistureEl.value = 75;
      if (soilTypeEl) soilTypeEl.value = dFallback.typicalSoil;

      try {
        const liveWeather = await AgriApiClient.fetchCurrentWeather(dName);
        if (tempEl) tempEl.value = liveWeather.temperature_c.toFixed(1);
        if (humidityEl) humidityEl.value = liveWeather.relative_humidity_pct.toFixed(0);
        showToast(state.currentLang === "ta" 
          ? `${dName} நேரலை வானிலை விவரங்கள் தானாக நிரப்பப்பட்டன` 
          : `Auto-filled live weather for ${dName}`
        );
      } catch (_) {
        if (tempEl) tempEl.value = dFallback.currentWeather.temp;
        if (humidityEl) humidityEl.value = dFallback.currentWeather.humidity;
        showToast(`Auto-filled baseline weather for ${dName}`);
      }
    });
  }

  const predictForm = document.getElementById("prediction-form");
  if (predictForm) {
    predictForm.addEventListener("submit", (e) => {
      e.preventDefault();
      handleYieldPrediction();
    });
  }

  const resetFormBtn = document.getElementById("btn-reset-form");
  if (resetFormBtn) {
    resetFormBtn.addEventListener("click", () => {
      predictForm.reset();
      const outputArea = document.getElementById("prediction-results-area");
      if (outputArea) {
        outputArea.innerHTML = `
          <div class="glass-panel" style="min-height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2rem;">
            <div style="font-size: 2.75rem; margin-bottom: 1rem;">🌾</div>
            <h3 style="font-size: 1.15rem; color: #ffffff; margin-bottom: 0.5rem;" data-i18n="results_heading">
              ${state.currentLang === "ta" ? "கணிப்பு முடிவுகள் & அறுவடை நுண்ணறிவு" : "Prediction Results & Harvest Insights"}
            </h3>
            <p style="color: var(--text-muted); font-size: 0.85rem; max-width: 380px;">
              ${state.currentLang === "ta" ? "படிவத்தை நிரப்பி விளைச்சலைக் கணக்கிடுக" : "Fill in farm and soil parameters to compute Random Forest yield predictions."}
            </p>
          </div>
        `;
      }
      showToast(state.currentLang === "ta" ? "படிவம் மீட்டமைக்கப்பட்டது" : "Form reset");
    });
  }

  // Handle Real ML Inference & Recommendations
  async function handleYieldPrediction() {
    const district = document.getElementById("pred-district").value;
    const season = document.getElementById("pred-season").value;
    const soilType = document.getElementById("pred-soil").value;
    const area = parseFloat(document.getElementById("pred-area").value) || 1.0;
    const n = parseFloat(document.getElementById("pred-n").value);
    const p = parseFloat(document.getElementById("pred-p").value);
    const k = parseFloat(document.getElementById("pred-k").value);
    const ph = parseFloat(document.getElementById("pred-ph").value);
    const moisture = parseFloat(document.getElementById("pred-moisture").value);
    const rainfall = parseFloat(document.getElementById("pred-rainfall").value);
    const temp = parseFloat(document.getElementById("pred-temp").value);
    const humidity = parseFloat(document.getElementById("pred-humidity").value);
    const rawPrevYield = parseFloat(document.getElementById("pred-prev-yield").value) || 4000;

    // Convert previous yield to tonnes/ha if entered as kg/ha (e.g. 4200 -> 4.2)
    const prevYieldTonnes = rawPrevYield > 20 ? parseFloat((rawPrevYield / 1000).toFixed(2)) : rawPrevYield;

    // Client-side Validation Checks
    if (!district || !season || !soilType) {
      showToast(window.I18N_DICTIONARY?.[state.currentLang]?.val_required_district || "Please select district and season", "⚠️");
      return;
    }
    if (ph < 4.0 || ph > 9.5) {
      showToast(window.I18N_DICTIONARY?.[state.currentLang]?.val_ph_range || "Soil pH must be between 4.0 and 9.5", "⚠️");
      return;
    }
    if (moisture < 10.0 || moisture > 100.0) {
      showToast(window.I18N_DICTIONARY?.[state.currentLang]?.val_moisture_range || "Moisture must be between 10% and 100%", "⚠️");
      return;
    }

    state.selectedDistrict = district;
    state.selectedSeason = season;
    state.soilNutrients = { N: n, P: p, K: k, pH: ph, moisture: moisture };

    const outputArea = document.getElementById("prediction-results-area");
    if (!outputArea) return;

    outputArea.innerHTML = `
      <div class="glass-panel spinner-wrap">
        <div class="glass-spinner"></div>
        <div style="color: var(--accent-leaf); font-weight: 500; font-size: 0.9rem;" data-i18n="loading_predicting">
          ${state.currentLang === "ta" 
            ? "ரேண்டம் ஃபாரஸ்ட் இயந்திர கற்றல் மாதிரி விளைச்சலைக் கணக்கிடுகிறது..." 
            : "Computing Random Forest yield regression via FastAPI ML backend..."}
        </div>
      </div>
    `;

    const predictPayload = {
      district: district,
      season: season,
      soil_type: soilType,
      rainfall_mm: rainfall,
      temperature_c: temp,
      humidity_pct: humidity,
      soil_ph: ph,
      soil_moisture_pct: moisture,
      nitrogen_kg_ha: n,
      phosphorus_kg_ha: p,
      potassium_kg_ha: k,
      previous_yield_tonnes_per_hectare: prevYieldTonnes,
      area_hectares: area
    };

    try {
      // 1. Invoke Real ML Prediction Model
      const predResponse = await AgriApiClient.predictYield(predictPayload);

      // 2. Fetch Smart Agronomic Recommendations concurrently
      let recResponse = null;
      try {
        const recPayload = {
          district: district,
          season: season,
          growth_stage: "vegetative_tillering",
          soil_type: soilType,
          soil_ph: ph,
          soil_moisture_pct: moisture,
          nitrogen_kg_ha: n,
          phosphorus_kg_ha: p,
          potassium_kg_ha: k,
          temperature_c: temp,
          humidity_pct: humidity,
          rainfall_mm: rainfall
        };
        recResponse = await AgriApiClient.getRecommendations(recPayload);
        state.lastRecommendations = recResponse;
      } catch (recErr) {
        console.warn("Recommendations fetch encountered non-fatal error:", recErr);
      }

      // 3. Save Record to SQLite Persistence
      try {
        const savePayload = {
          district: district,
          season: season,
          soil_type: soilType,
          area_hectares: area,
          rainfall_mm: rainfall,
          temperature_c: temp,
          humidity_pct: humidity,
          soil_ph: ph,
          soil_moisture_pct: moisture,
          nitrogen_kg_ha: n,
          phosphorus_kg_ha: p,
          potassium_kg_ha: k,
          previous_yield_tonnes_per_hectare: prevYieldTonnes,
          predicted_yield_tonnes_per_hectare: predResponse.predicted_yield_tonnes_per_hectare,
          predicted_yield_quintals_per_hectare: predResponse.predicted_yield_quintals_per_hectare,
          predicted_yield_kg_per_hectare: predResponse.predicted_yield_kg_per_hectare,
          confidence_lower_tonnes: predResponse.confidence_interval_90?.lower_bound_tonnes,
          confidence_upper_tonnes: predResponse.confidence_interval_90?.upper_bound_tonnes,
          model_name: predResponse.model_name || "RandomForestRegressor",
          model_version: predResponse.model_version || "1.0.0"
        };
        await AgriApiClient.savePrediction(savePayload);
      } catch (saveErr) {
        console.warn("Could not auto-save prediction to database:", saveErr);
      }

      state.currentPrediction = predResponse;

      // Render Dynamic Results
      renderPredictionResult(predResponse, area);
      showToast(state.currentLang === "ta" ? "விளைச்சல் வெற்றிகரமாகக் கணக்கிடப்பட்டது!" : "Real ML Yield Prediction Computed!");

      // Update recommendations and soil gauges
      if (recResponse) renderRecommendations();
      renderSoilAnalysis();

    } catch (err) {
      console.error("Prediction API failed:", err);
      outputArea.innerHTML = `
        <div class="glass-panel" style="border-left: 3px solid var(--accent-rose); padding: 1.5rem;">
          <h3 style="color: #ffffff; font-size: 1.1rem; margin-bottom: 0.5rem;">
            ⚠️ ${state.currentLang === "ta" ? "விளைச்சல் கணக்கீட்டில் பிழை" : "Prediction Request Failed"}
          </h3>
          <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1rem;">
            ${err.message || "Failed to communicate with the FastAPI backend service. Ensure backend server is running on port 8000."}
          </p>
          <div style="display: flex; gap: 0.75rem;">
            <button id="btn-retry-predict" class="btn btn-primary btn-sm">
              ${state.currentLang === "ta" ? "மீண்டும் முயற்சிக்குக" : "Retry Prediction"}
            </button>
            <button id="btn-check-backend" class="btn btn-secondary btn-sm">
              ${state.currentLang === "ta" ? "சேவையக நிலை" : "Check Health"}
            </button>
          </div>
        </div>
      `;
      const retryBtn = document.getElementById("btn-retry-predict");
      if (retryBtn) retryBtn.addEventListener("click", handleYieldPrediction);

      const healthBtn = document.getElementById("btn-check-backend");
      if (healthBtn) {
        healthBtn.addEventListener("click", async () => {
          const h = await verifyBackendHealth();
          showToast(h ? `Backend is ${h.status}` : "Backend is offline", h ? "✓" : "⚠️");
        });
      }
    }
  }

  function renderPredictionResult(pred, area) {
    const outputArea = document.getElementById("prediction-results-area");
    if (!outputArea) return;

    const qHa = pred.predicted_yield_quintals_per_hectare.toFixed(1);
    const kgHa = Math.round(pred.predicted_yield_kg_per_hectare);
    const totalQuintals = (pred.predicted_yield_quintals_per_hectare * area).toFixed(1);

    const stateAvg = 38.5; // Quintals/ha
    const vsStatePercent = Math.round(((pred.predicted_yield_quintals_per_hectare - stateAvg) / stateAvg) * 100);
    const vsStateSign = vsStatePercent >= 0 ? `+${vsStatePercent}%` : `${vsStatePercent}%`;
    const potentialPct = Math.min(Math.round((pred.predicted_yield_quintals_per_hectare / 54.0) * 100), 100);

    const confLow = pred.confidence_interval_90?.lower_bound_tonnes
      ? (pred.confidence_interval_90.lower_bound_tonnes * 10).toFixed(1)
      : (pred.predicted_yield_quintals_per_hectare * 0.92).toFixed(1);

    const confHigh = pred.confidence_interval_90?.upper_bound_tonnes
      ? (pred.confidence_interval_90.upper_bound_tonnes * 10).toFixed(1)
      : (pred.predicted_yield_quintals_per_hectare * 1.08).toFixed(1);

    outputArea.innerHTML = `
      <div class="glass-panel pred-result-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <h3 style="font-size: 1.25rem; font-weight: 700; color: #ffffff;" data-i18n="results_heading">
            ${state.currentLang === "ta" ? "கணிப்பு முடிவுகள் & அறுவடை நுண்ணறிவு" : "Prediction Results & Harvest Insights"}
          </h3>
          <span class="badge badge-green">${pred.model_name || 'Random Forest'} v${pred.model_version || '1.0'}</span>
        </div>

        <div class="yield-hero">
          <div class="yield-number-wrap">
            <span>${state.currentLang === "ta" ? "மதிப்பிடப்பட்ட விளைச்சல்" : "Estimated Harvest Yield"}</span>
            <h3>${qHa} <span style="font-size: 1.25rem; color: var(--accent-leaf);">Q/ha</span></h3>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem;">
              (${kgHa} kg / hectare) &bull; ${pred.predicted_yield_tonnes_per_hectare.toFixed(2)} tonnes/ha
            </p>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 0.8rem; color: var(--text-muted);">${state.currentLang === "ta" ? "மொத்த விளைச்சல்" : "Total Production on Plot"}</div>
            <div style="font-size: 1.65rem; font-weight: 800; color: #ffffff;">${totalQuintals} <span style="font-size: 0.9rem; color: var(--accent-leaf);">Quintals</span></div>
            <div style="font-size: 0.775rem; color: var(--text-dim);">${area} Hectares Cultivated</div>
          </div>
        </div>

        <!-- Benchmarks -->
        <div class="benchmark-row">
          <div class="benchmark-info">
            <span>${state.currentLang === "ta" ? "தமிழக சராசரியுடன் ஒப்பீடு" : "vs TN State Average (38.5 Q/ha)"}</span>
            <span style="color: var(--accent-leaf); font-weight: 600;">${vsStateSign}</span>
          </div>
          <div class="benchmark-bar-track">
            <div class="benchmark-bar-fill" style="width: ${potentialPct}%; background: linear-gradient(90deg, #10b981, #34d399);"></div>
          </div>
        </div>

        <div class="benchmark-row" style="margin-top: 0.75rem;">
          <div class="benchmark-info">
            <span>${state.currentLang === "ta" ? "நம்பகத்தன்மை வரம்பு (90%)" : "90% Confidence Interval"}</span>
            <span style="color: var(--accent-cyan); font-weight: 600;">${confLow} - ${confHigh} Q/ha</span>
          </div>
        </div>

        <div style="display: flex; gap: 0.75rem; margin-top: 1.25rem;">
          <button id="btn-download-report" class="btn btn-secondary btn-sm" type="button">
            📥 ${state.currentLang === "ta" ? "அறிக்கையைப் பதிவிறக்குக" : "Download Prediction Report"}
          </button>
          <button id="btn-view-recom-from-pred" class="btn btn-primary btn-sm" type="button">
            💡 ${state.currentLang === "ta" ? "பரிந்துரைகளைக் காண்க" : "View Recommendations"}
          </button>
        </div>

        <div style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); font-size: 0.75rem; color: var(--text-dim);">
          ${state.currentLang === "ta" 
            ? "மறுப்புரை: இயந்திர கற்றல் கணிப்புகள் தமிழ்நாடு வேளாண் பல்கலைக்கழக வழிகாட்டுதல்களின் அடிப்படையில் அமைந்தவை. உண்மையான விளைச்சல் மாறுபடலாம்." 
            : "Advisory Disclaimer: ML predictions are grounded in TNAU benchmarks and statistical regression. Actual field harvest depends on weather variations and field management."}
        </div>
      </div>
    `;

    // Download Report Action
    const downloadBtn = document.getElementById("btn-download-report");
    if (downloadBtn) {
      downloadBtn.addEventListener("click", () => {
        const textContent = `====================================================
AgriSense-AI: Paddy Crop Yield Prediction Report
====================================================
District:           ${pred.district || state.selectedDistrict}
Cropping Season:    ${pred.season || state.selectedSeason}
Soil Classification:${pred.soil_type || 'Alluvial'}
Cultivated Area:    ${area} Hectares

PREDICTION OUTCOMES:
----------------------------------------------------
Predicted Yield:    ${qHa} Quintals / Hectare
                    ${kgHa} kg / Hectare
                    ${pred.predicted_yield_tonnes_per_hectare.toFixed(2)} Tonnes / Hectare
Estimated Total:    ${totalQuintals} Quintals across plot
90% Confidence:     ${confLow} - ${confHigh} Q/ha
Model:              ${pred.model_name || 'Random Forest'} v${pred.model_version || '1.0'}
Generated At:       ${new Date().toISOString()}

AUTHORITATIVE BENCHMARK:
Tamil Nadu Agricultural University (TNAU) Agritech Portal
====================================================`;

        const blob = new Blob([textContent], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `agrisense_prediction_${state.selectedDistrict}_${new Date().toISOString().split("T")[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast(state.currentLang === "ta" ? "அறிக்கை பதிவிறக்கப்பட்டது!" : "Prediction report downloaded!");
      });
    }

    const viewRecomBtn = document.getElementById("btn-view-recom-from-pred");
    if (viewRecomBtn) {
      viewRecomBtn.addEventListener("click", () => switchTab("recommendations"));
    }
  }

  // --- 6. Soil Analysis Component ---
  function renderSoilAnalysis() {
    const baseline = AGRI_DATA.tnauBaselines[state.selectedSeason] || AGRI_DATA.tnauBaselines["Samba"];
    const container = document.getElementById("soil-npk-comparison-container");

    if (container) {
      const nutrients = [
        { name: state.currentLang === "ta" ? "தழைச்சத்து (N)" : "Nitrogen (N)", val: state.soilNutrients.N, target: baseline.N, color: "#10b981" },
        { name: state.currentLang === "ta" ? "மணிச்சத்து (P)" : "Phosphorus (P)", val: state.soilNutrients.P, target: baseline.P, color: "#06b6d4" },
        { name: state.currentLang === "ta" ? "சாம்பல் சத்து (K)" : "Potassium (K)", val: state.soilNutrients.K, target: baseline.K, color: "#f59e0b" },
      ];

      container.innerHTML = nutrients.map(nut => {
        const pct = Math.min(Math.round((nut.val / (nut.target * 1.5)) * 100), 100);
        const status = nut.val < nut.target * 0.85 
          ? (state.currentLang === "ta" ? "பற்றாக்குறை" : "Deficit")
          : (nut.val > nut.target * 1.25 
            ? (state.currentLang === "ta" ? "அதிகப்படியானது" : "Excess") 
            : (state.currentLang === "ta" ? "சமச்சீர்" : "Balanced"));
        const badgeColor = status.includes("Deficit") || status.includes("பற்றாக்குறை") ? "badge-amber" : "badge-green";

        return `
          <div class="soil-track-wrap">
            <div class="soil-track-meta">
              <span style="font-weight: 600; color: #ffffff;">${nut.name}</span>
              <span><strong>${nut.val}</strong> / ${nut.target} kg/ha <span class="badge ${badgeColor}" style="margin-left: 0.5rem;">${status}</span></span>
            </div>
            <div class="soil-progress-track">
              <div class="soil-progress-fill" style="width: ${pct}%; background: ${nut.color};"></div>
            </div>
          </div>
        `;
      }).join("");
    }

    // Compute Dynamic Soil Score
    const nDiff = Math.abs(state.soilNutrients.N - baseline.N);
    const pDiff = Math.abs(state.soilNutrients.P - baseline.P);
    const kDiff = Math.abs(state.soilNutrients.K - baseline.K);
    const penalty = Math.min((nDiff + pDiff + kDiff) * 0.35, 30);
    const soilScore = Math.round(95 - penalty);

    AgriCharts.renderCircularGauge(
      "soil-health-gauge-container",
      soilScore,
      "/100",
      state.currentLang === "ta" ? "மண் வளக் குறியீடு" : "Soil Health Index",
      soilScore > 80 ? "#10b981" : "#f59e0b"
    );

    const phVal = document.getElementById("soil-prop-ph-val");
    if (phVal) phVal.textContent = state.soilNutrients.pH.toFixed(1);

    const moistVal = document.getElementById("soil-prop-moisture-val");
    if (moistVal) moistVal.textContent = `${state.soilNutrients.moisture}%`;
  }

  // --- 7. Recommendations Component ---
  async function renderRecommendations() {
    const fertContainer = document.getElementById("subtab-fertilizer");
    const irriContainer = document.getElementById("subtab-irrigation");
    const pestContainer = document.getElementById("recom-pest-list");

    // If recommendations have not been retrieved from API, fetch now
    if (!state.lastRecommendations) {
      try {
        const recPayload = {
          district: state.selectedDistrict,
          season: state.selectedSeason,
          growth_stage: "vegetative_tillering",
          soil_type: "Alluvial",
          soil_ph: state.soilNutrients.pH,
          soil_moisture_pct: state.soilNutrients.moisture,
          nitrogen_kg_ha: state.soilNutrients.N,
          phosphorus_kg_ha: state.soilNutrients.P,
          potassium_kg_ha: state.soilNutrients.K
        };
        state.lastRecommendations = await AgriApiClient.getRecommendations(recPayload);
      } catch (e) {
        console.warn("Could not fetch recommendations from API, using static template:", e);
      }
    }

    const recs = state.lastRecommendations;

    // Render Fertilizer & Soil Health Advisories
    if (fertContainer && recs && recs.fertilizer_advisory) {
      const items = [...recs.fertilizer_advisory, ...(recs.soil_health_advisory || [])];
      fertContainer.innerHTML = `
        <div class="glass-panel">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
            <h3 style="font-size: 1.15rem; color: #ffffff;" data-i18n="fert_schedule_title">
              ${state.currentLang === "ta" ? "TNAU நெல் உரமிடுதல் மற்றும் மண்வள வழிகாட்டுதல்" : "TNAU Split Application Plan & Soil Health"}
            </h3>
            <span class="badge badge-green">TNAU Expert Engine</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            ${items.map((item, idx) => {
              const urgencyClass = item.urgency === "warning" || item.urgency === "critical" ? "badge-amber" : "badge-green";
              return `
                <div class="recom-card">
                  <h4>
                    <span>${item.title}</span>
                    <span class="badge ${urgencyClass}">${item.urgency.toUpperCase()}</span>
                  </h4>
                  <p><strong>Action:</strong> ${item.action}</p>
                  <p style="margin-top: 0.35rem; font-size: 0.85rem; color: var(--text-muted);"><strong>Reason:</strong> ${item.reason}</p>
                  ${item.warnings ? `<p style="margin-top: 0.35rem; font-size: 0.8rem; color: var(--accent-amber);">⚠️ ${item.warnings}</p>` : ''}
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;
    }

    // Render Irrigation Guidance
    if (irriContainer && recs && recs.irrigation_advisory) {
      irriContainer.innerHTML = `
        <div class="glass-panel">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="font-size: 1.15rem; color: #ffffff;" data-i18n="irri_awd_title">
              ${state.currentLang === "ta" ? "காய்ச்சலும் பாய்ச்சலுமான பாசன முறை (AWD)" : "Alternate Wetting and Drying (AWD) Water Regimen"}
            </h3>
            <span class="badge badge-cyan">Water Saving Protocol</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            ${recs.irrigation_advisory.map(item => `
              <div class="recom-card">
                <h4>
                  <span>${item.title}</span>
                  <span class="badge ${item.urgency === 'critical' ? 'badge-rose' : 'badge-green'}">${item.urgency.toUpperCase()}</span>
                </h4>
                <p><strong>Action:</strong> ${item.action}</p>
                <p style="margin-top: 0.35rem; font-size: 0.85rem; color: var(--text-muted);"><strong>Reason:</strong> ${item.reason}</p>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }

    // Render Pest & Disease Monitoring
    if (pestContainer && recs && recs.pest_monitoring_alerts) {
      pestContainer.innerHTML = recs.pest_monitoring_alerts.map(item => {
        const badgeColor = item.urgency === "warning" ? "badge-amber" : "badge-green";
        return `
          <div class="recom-card">
            <h4>
              <span>${item.title}</span>
              <span class="badge ${badgeColor}">${item.urgency.toUpperCase()}</span>
            </h4>
            <p><strong>Management Action:</strong> ${item.action}</p>
            <p style="margin-top: 0.4rem; font-size: 0.85rem; color: var(--text-muted);"><strong>Risk Factors:</strong> ${item.reason}</p>
            ${item.warnings ? `<p style="margin-top: 0.4rem; font-size: 0.8rem; color: var(--accent-rose);">⚠️ ${item.warnings}</p>` : ''}
          </div>
        `;
      }).join("");
    } else if (pestContainer) {
      // Fallback to AGRI_DATA pests if not yet fetched
      pestContainer.innerHTML = AGRI_DATA.pestAdvisory.map(pest => `
        <div class="recom-card">
          <h4>
            <span>${state.currentLang === "ta" ? pest.name_ta : pest.name}</span>
            <span class="badge ${pest.risk === 'High' ? 'badge-amber' : 'badge-green'}">${pest.risk}</span>
          </h4>
          <p><strong>Symptoms:</strong> ${state.currentLang === "ta" ? pest.symptoms_ta : pest.symptoms}</p>
          <p style="margin-top: 0.4rem; color: var(--accent-leaf);"><strong>Treatment:</strong> ${state.currentLang === "ta" ? pest.organicAction_ta : pest.organicAction}</p>
        </div>
      `).join("");
    }
  }

  // Sub-tabs in Recommendations
  document.querySelectorAll(".sub-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".sub-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const targetSub = btn.dataset.subtab;
      document.querySelectorAll(".recom-subtab-content").forEach(c => {
        c.style.display = c.id === `subtab-${targetSub}` ? "block" : "none";
      });
    });
  });

  // --- 8. History Audit Component (Connected to SQLite API) ---
  async function renderHistoryTable() {
    const tbody = document.getElementById("history-table-body");
    const searchInput = document.getElementById("history-search");
    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

    if (!tbody) return;

    tbody.innerHTML = `
      <tr>
        <td colspan="10" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          <div class="glass-spinner" style="margin: 0 auto 0.75rem auto;"></div>
          ${state.currentLang === "ta" ? "தரவுத்தளத்தில் இருந்து வரலாறு பெறப்படுகிறது..." : "Loading prediction history from SQLite..."}
        </td>
      </tr>
    `;

    try {
      const logs = await AgriApiClient.fetchHistoryLogs({ limit: 50 });
      state.historyRecords = logs;

      const filtered = logs.filter(rec => {
        if (!query) return true;
        return (
          rec.district.toLowerCase().includes(query) ||
          rec.season.toLowerCase().includes(query) ||
          String(rec.id).includes(query)
        );
      });

      if (filtered.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="10" style="text-align: center; padding: 2.5rem; color: var(--text-muted);" data-i18n="empty_history">
              ${state.currentLang === "ta" ? "தேடலுக்குரிய பதிவுகள் ஏதும் கிடைக்கவில்லை." : "No historical records found in database."}
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = filtered.map(item => {
        const dateStr = item.created_at ? item.created_at.split("T")[0] : "-";
        const qYield = item.predicted_yield_quintals_per_hectare ? item.predicted_yield_quintals_per_hectare.toFixed(1) : "-";
        const actYield = item.harvest_result ? `${item.harvest_result.actual_yield_quintals_per_hectare} Q/ha` : "-";
        return `
          <tr>
            <td><code>#${item.id}</code></td>
            <td>${dateStr}</td>
            <td><strong>${item.district}</strong></td>
            <td>${item.season}</td>
            <td>${item.soil_type}</td>
            <td>${item.area_hectares}</td>
            <td><strong style="color: var(--accent-leaf);">${qYield}</strong></td>
            <td>${actYield}</td>
            <td><span class="badge badge-green">90% Bound</span></td>
            <td><span class="badge badge-cyan">${item.model_name || 'Active'}</span></td>
          </tr>
        `;
      }).join("");

    } catch (err) {
      console.warn("Could not retrieve history logs from API, falling back:", err);
      // Fallback display
      tbody.innerHTML = `
        <tr>
          <td colspan="10" style="text-align: center; padding: 2rem; color: var(--accent-amber);">
            ⚠️ SQLite history endpoint unreachable. Ensure FastAPI backend is running.
            <div style="margin-top: 0.5rem;">
              <button id="btn-retry-history" class="btn btn-secondary btn-sm">Retry</button>
            </div>
          </td>
        </tr>
      `;
      const retryBtn = document.getElementById("btn-retry-history");
      if (retryBtn) retryBtn.addEventListener("click", renderHistoryTable);
    }
  }

  const histSearch = document.getElementById("history-search");
  if (histSearch) histSearch.addEventListener("input", renderHistoryTable);

  const exportBtn = document.getElementById("btn-export-history");
  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      let csv = "ID,Date,District,Season,SoilType,Area_Ha,Predicted_Q_Ha,Actual_Q_Ha,Status\n";
      state.historyRecords.forEach(r => {
        const d = r.created_at ? r.created_at.split("T")[0] : "-";
        const act = r.harvest_result ? r.harvest_result.actual_yield_quintals_per_hectare : "-";
        csv += `${r.id},${d},${r.district},${r.season},${r.soil_type},${r.area_hectares},${r.predicted_yield_quintals_per_hectare},${act},${r.model_name}\n`;
      });
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `agrisense_history_${new Date().toISOString().split("T")[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast(state.currentLang === "ta" ? "CSV கோப்பு பதிவிறக்கம் செய்யப்பட்டது" : "History exported as CSV file");
    });
  }

  // --- Initial App Initialization ---
  const savedLang = (function() {
    try {
      const stored = localStorage.getItem("agrisense_language");
      return (stored === "ta" || stored === "en") ? stored : "en";
    } catch (e) {
      return "en";
    }
  })();

  applyLanguage(savedLang);
  verifyBackendHealth();
  renderDashboard();
});
