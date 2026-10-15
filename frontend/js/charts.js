/**
 * AgriSense-AI: Vanilla SVG Chart & Data Visualization Utility
 * Zero external libraries: High performance, accessible, responsive SVG rendering.
 */

const AgriCharts = {
  /**
   * Renders a circular arc progress gauge.
   * @param {string} containerId - Target element ID
   * @param {number} value - Value between 0 and 100
   * @param {string} unit - Display unit e.g. "%" or "Score"
   * @param {string} label - Subtitle label
   * @param {string} color - Stroke color
   */
  renderCircularGauge(containerId, value, unit = "%", label = "", color = "#10b981") {
    const container = document.getElementById(containerId);
    if (!container) return;

    const clampedVal = Math.min(Math.max(value, 0), 100);
    const radius = 56;
    const strokeWidth = 9;
    const circumference = 2 * Math.PI * radius;
    // We render a 260-degree arc gauge
    const arcPercent = 0.75;
    const totalArc = circumference * arcPercent;
    const offset = totalArc - (clampedVal / 100) * totalArc;

    container.innerHTML = `
      <div class="gauge-card">
        <svg viewBox="0 0 140 140" class="gauge-svg" aria-label="${label}: ${value}${unit}">
          <circle
            cx="70" cy="70" r="${radius}"
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            stroke-width="${strokeWidth}"
            stroke-dasharray="${totalArc} ${circumference}"
            stroke-linecap="round"
            transform="rotate(135 70 70)"
          />
          <circle
            cx="70" cy="70" r="${radius}"
            fill="none"
            stroke="${color}"
            stroke-width="${strokeWidth}"
            stroke-dasharray="${totalArc} ${circumference}"
            stroke-dashoffset="${offset}"
            stroke-linecap="round"
            transform="rotate(135 70 70)"
            class="gauge-progress"
          />
        </svg>
        <div class="gauge-center-text">
          <div class="gauge-value" style="color: ${color};">${value}<span class="gauge-unit">${unit}</span></div>
          <div class="gauge-label">${label}</div>
        </div>
      </div>
    `;
  },

  /**
   * Renders a comparative bar chart for N, P, K against TNAU baselines.
   * @param {string} containerId
   * @param {Array<{nutrient: string, current: number, target: number, unit: string}>} data
   */
  renderNPKBarComparison(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let barsHtml = data.map(item => {
      const maxVal = Math.max(item.current, item.target) * 1.25 || 100;
      const currentPct = Math.min((item.current / maxVal) * 100, 100);
      const targetPct = Math.min((item.target / maxVal) * 100, 100);

      const diff = item.current - item.target;
      let statusColor = "#10b981"; // Balanced
      let statusBadge = "Balanced";
      if (diff < -15) {
        statusColor = "#f59e0b"; // Deficit
        statusBadge = "Deficit";
      } else if (diff > 25) {
        statusColor = "#3b82f6"; // Excess
        statusBadge = "Surplus";
      }

      return `
        <div class="npk-row">
          <div class="npk-info">
            <span class="npk-name">${item.nutrient}</span>
            <span class="npk-numbers">
              <strong>${item.current}</strong> / <span class="text-muted">${item.target} ${item.unit}</span>
            </span>
            <span class="npk-badge" style="background: ${statusColor}22; color: ${statusColor}; border: 1px solid ${statusColor}44;">
              ${statusBadge}
            </span>
          </div>
          <div class="npk-track-wrapper">
            <div class="npk-track">
              <!-- Current Level Bar -->
              <div class="npk-fill" style="width: ${currentPct}%; background: ${statusColor};"></div>
              <!-- TNAU Target Reference Marker -->
              <div class="npk-target-marker" style="left: ${targetPct}%;" title="TNAU Target: ${item.target} ${item.unit}"></div>
            </div>
            <div class="npk-markers-label">
              <span>0</span>
              <span class="target-flag" style="left: ${targetPct}%;">Target</span>
              <span>${Math.round(maxVal)} ${item.unit}</span>
            </div>
          </div>
        </div>
      `;
    }).join("");

    container.innerHTML = `
      <div class="npk-comparison-card">
        ${barsHtml}
      </div>
    `;
  },

  /**
   * Renders a 5-day temperature trend sparkline.
   * Handles dynamic API forecast structures and empty/unavailable states.
   * @param {string} containerId
   * @param {Array<{day?: string, high?: number, low?: number, temperature_max_c?: number, temperature_min_c?: number}>} forecast
   */
  renderWeatherSparkline(containerId, forecast) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!forecast || !Array.isArray(forecast) || forecast.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; color: var(--text-dim); font-size: 0.8rem; padding: 1.5rem 0;">
          📊 <em>Forecast trend visualization currently unavailable</em>
        </div>
      `;
      return;
    }

    const highs = forecast.map(f => Number(f.high ?? f.temperature_max_c ?? 30));
    const lows = forecast.map(f => Number(f.low ?? f.temperature_min_c ?? (f.high ? f.high - 6 : 24)));
    const minT = Math.min(...lows) - 2;
    const maxT = Math.max(...highs) + 2;
    const width = 300;
    const height = 90;
    const paddingX = 25;
    const paddingY = 20;

    const denom = maxT - minT === 0 ? 1 : maxT - minT;
    const stepX = forecast.length > 1 ? (width - paddingX * 2) / (forecast.length - 1) : 0;
    const points = highs.map((h, i) => {
      const x = paddingX + i * stepX;
      const y = height - paddingY - ((h - minT) / denom) * (height - paddingY * 2);
      const dayLabel = forecast[i].day || (forecast[i].date ? new Date(forecast[i].date).toLocaleDateString("en-US", { weekday: "short" }) : `D${i+1}`);
      return { x, y, temp: Math.round(h), day: dayLabel };
    });

    const pathD = points.reduce((acc, p, i) => `${acc} ${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`, "");

    const dots = points.map(p => `
      <circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="4.5" fill="#10b981" stroke="#0a110e" stroke-width="2" />
      <text x="${p.x.toFixed(1)}" y="${(p.y - 8).toFixed(1)}" font-size="10" fill="#f3f4f6" text-anchor="middle" font-weight="600">${p.temp}°</text>
      <text x="${p.x.toFixed(1)}" y="${height - 2}" font-size="9" fill="#9ca3af" text-anchor="middle">${p.day}</text>
    `).join("");

    container.innerHTML = `
      <div class="weather-trend-box">
        <svg viewBox="0 0 ${width} ${height}" class="sparkline-svg">
          <path d="${pathD}" fill="none" stroke="rgba(16, 185, 129, 0.7)" stroke-width="3" stroke-linecap="round" />
          ${dots}
        </svg>
      </div>
    `;
  }
};

window.AgriCharts = AgriCharts;

