/**
 * AgriSense-AI: Frontend API Client.
 * Connects the Vanilla JavaScript frontend to the FastAPI REST backend.
 * Handles environment-aware URL configuration, timeouts, error extraction,
 * and graceful network degradation.
 */

(function () {
  // Resolve Backend Base URL dynamically
  function resolveApiBaseUrl() {
    // 1. Explicit window-level configuration (e.g. from environment or meta tag)
    if (window.AGRISENSE_CONFIG && window.AGRISENSE_CONFIG.API_URL) {
      return window.AGRISENSE_CONFIG.API_URL.replace(/\/+$/, "");
    }
    // 2. Local storage override if developer customized
    try {
      const stored = localStorage.getItem("agrisense_api_url");
      if (stored) return stored.replace(/\/+$/, "");
    } catch (_) {}

    // 3. Fallback based on browser location
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;

    if (protocol === "file:" || hostname === "localhost" || hostname === "127.0.0.1") {
      // Local development server on port 8000
      return "http://127.0.0.1:8000/api/v1";
    }

    // Production relative reverse-proxy path
    return "/api/v1";
  }

  const API_BASE_URL = resolveApiBaseUrl();
  const ROOT_URL = API_BASE_URL.replace(/\/api\/v1\/?$/, "");

  /**
   * Helper for robust JSON requests with timeout and structured error extraction.
   */
  async function request(url, options = {}, timeoutMs = 8000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const defaultHeaders = {
      "Accept": "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: { ...defaultHeaders, ...(options.headers || {}) },
        signal: controller.signal
      });

      clearTimeout(timer);

      if (!response.ok) {
        let errorMsg = `Server error (${response.status})`;
        try {
          const errData = await response.json();
          if (errData.detail) {
            errorMsg = Array.isArray(errData.detail)
              ? errData.detail.map(d => `${d.loc ? d.loc.join('.') : ''}: ${d.msg}`).join("; ")
              : errData.detail;
          } else if (errData.error) {
            errorMsg = errData.details ? `${errData.error}: ${errData.details.join(", ")}` : errData.error;
          }
        } catch (_) {}
        const err = new Error(errorMsg);
        err.status = response.status;
        throw err;
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timer);
      if (err.name === "AbortError") {
        const timeoutErr = new Error("Request timed out. Please verify backend service is running.");
        timeoutErr.status = 504;
        throw timeoutErr;
      }
      throw err;
    }
  }

  const AgriApiClient = {
    baseUrl: API_BASE_URL,
    rootUrl: ROOT_URL,

    /**
     * Health check to verify backend operational readiness.
     */
    async checkHealth() {
      return await request(`${ROOT_URL}/health`, { method: "GET" }, 4000);
    },

    /**
     * Fetch live current agro-meteorological conditions for a Tamil Nadu district.
     */
    async fetchCurrentWeather(district) {
      const url = `${API_BASE_URL}/weather/current?district=${encodeURIComponent(district)}`;
      return await request(url, { method: "GET" }, 6000);
    },

    /**
     * Fetch daily forecast for a Tamil Nadu district.
     */
    async fetchForecast(district, days = 5) {
      const url = `${API_BASE_URL}/weather/forecast?district=${encodeURIComponent(district)}&forecast_days=${days}`;
      return await request(url, { method: "GET" }, 6000);
    },

    /**
     * Submit farm inputs to obtain yield prediction from the Random Forest model.
     */
    async predictYield(payload) {
      // Primary v1 endpoint: /api/v1/crop/predict (or root /predict)
      try {
        return await request(`${API_BASE_URL}/crop/predict`, {
          method: "POST",
          body: JSON.stringify(payload)
        }, 10000);
      } catch (err) {
        // Fallback to root /predict if v1 route differs
        if (err.status === 404) {
          return await request(`${ROOT_URL}/predict`, {
            method: "POST",
            body: JSON.stringify(payload)
          }, 10000);
        }
        throw err;
      }
    },

    /**
     * Request smart agronomic recommendations based on TNAU rule engine.
     */
    async getRecommendations(payload) {
      try {
        return await request(`${API_BASE_URL}/recommendations/`, {
          method: "POST",
          body: JSON.stringify(payload)
        }, 8000);
      } catch (err) {
        if (err.status === 404) {
          return await request(`${ROOT_URL}/recommendations`, {
            method: "POST",
            body: JSON.stringify(payload)
          }, 8000);
        }
        throw err;
      }
    },

    /**
     * Fetch prediction history logs from SQLite database.
     */
    async fetchHistoryLogs(params = {}) {
      const query = new URLSearchParams();
      if (params.district) query.append("district", params.district);
      if (params.season) query.append("season", params.season);
      if (params.limit) query.append("limit", params.limit);
      if (params.offset) query.append("offset", params.offset);

      const qs = query.toString();
      const url = `${API_BASE_URL}/history/logs${qs ? '?' + qs : ''}`;
      return await request(url, { method: "GET" }, 6000);
    },

    /**
     * Persist a completed prediction record to SQLite.
     */
    async savePrediction(payload) {
      return await request(`${API_BASE_URL}/history/predictions`, {
        method: "POST",
        body: JSON.stringify(payload)
      }, 6000);
    },

    /**
     * Record actual harvest outcome in SQLite.
     */
    async recordHarvest(payload) {
      return await request(`${API_BASE_URL}/history/harvest`, {
        method: "POST",
        body: JSON.stringify(payload)
      }, 6000);
    },

    /**
     * Fetch registered farm profiles.
     */
    async fetchFarms(district = null) {
      const qs = district ? `?district=${encodeURIComponent(district)}` : "";
      return await request(`${API_BASE_URL}/farms/${qs}`, { method: "GET" }, 6000);
    },

    /**
     * Fetch server-side translation dictionary for given language code.
     */
    async fetchTranslations(lang) {
      return await request(`${API_BASE_URL}/i18n/${encodeURIComponent(lang)}`, { method: "GET" }, 4000);
    }
  };

  window.AgriApiClient = AgriApiClient;
})();
