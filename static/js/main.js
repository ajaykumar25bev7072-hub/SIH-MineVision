/**
 * MineBoard CAS — Main Client Application Logic (main.js)
 * Asynchronous step/reset API calls, keyboard navigation, and live UI updates.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Bind Step & Reset Buttons
  const stepBtn = document.getElementById('btn-step-forward');
  const resetBtn = document.getElementById('btn-reset-demo');

  if (stepBtn) {
    stepBtn.addEventListener('click', () => advanceStep());
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', () => resetDemo());
  }

  // Keyboard Shortcuts (Space or ArrowRight = Step, 'R' = Reset)
  window.addEventListener('keydown', (e) => {
    // Ignore keystrokes inside input/textarea if any
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

    if (e.code === 'Space' || e.code === 'ArrowRight') {
      e.preventDefault();
      advanceStep();
    } else if (e.code === 'KeyR') {
      e.preventDefault();
      resetDemo();
    }
  });

  // Initial fetch of current step data to initialize charts and map
  fetchTelemetry();
});

// Step Forward API Call
async function advanceStep() {
  try {
    const res = await fetch('/api/step', { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
    const data = await res.json();
    applyTelemetryUpdate(data);
  } catch (err) {
    console.error('Failed to advance step:', err);
  }
}

// Reset Simulation API Call
async function resetDemo() {
  try {
    const res = await fetch('/api/reset', { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
    const data = await res.json();
    applyTelemetryUpdate(data);
  } catch (err) {
    console.error('Failed to reset demo:', err);
  }
}

// Fetch Current Telemetry Data Slice
async function fetchTelemetry() {
  try {
    const res = await fetch('/api/telemetry');
    if (!res.ok) return;
    const data = await res.json();
    applyTelemetryUpdate(data, true);
  } catch (err) {
    console.error('Failed to fetch telemetry:', err);
  }
}

// Update DOM elements on both Fleet Controller & Driver In-Cab pages
function applyTelemetryUpdate(data, isInitial = false) {
  if (!data) return;

  const currentStep = data.step;
  const currentTrucks = data.trucks || {};
  const kpis = data.kpis || {};
  const riskSummary = data.risk_summary || {};
  const history = data.history || [];

  // Update Top Navbar Indicators
  const navStep = document.getElementById('nav-step-counter');
  const navTime = document.getElementById('nav-timestamp');
  if (navStep) navStep.textContent = currentStep + 1;
  if (navTime) navTime.textContent = data.timestamp || `T+${currentStep * 2}s`;

  // ========================================================
  // PAGE 1: FLEET CONTROLLER UPDATES
  // ========================================================
  const tableBody = document.getElementById('telemetry-table-body');
  if (tableBody) {
    // 1. Update KPI Row
    const kpiActive = document.getElementById('kpi-active-units');
    const kpiSpeed = document.getElementById('kpi-avg-speed');
    const kpiDanger = document.getElementById('kpi-danger-alerts');
    const kpiCaution = document.getElementById('kpi-caution-alerts');
    const kpiAlertText = document.getElementById('kpi-alert-status-text');

    if (kpiActive) kpiActive.textContent = kpis.active_units ?? 4;
    if (kpiSpeed) kpiSpeed.textContent = kpis.fleet_avg_speed ?? 0;
    if (kpiDanger) kpiDanger.textContent = kpis.collision_alerts ?? 0;
    if (kpiCaution) kpiCaution.textContent = kpis.caution_alerts ?? 0;
    if (kpiAlertText) {
      kpiAlertText.textContent = (kpis.collision_alerts > 0)
        ? 'Immediate Intervention Active'
        : 'Nominal Separation Buffer';
    }

    // 2. Update Risk Donut Counts & Chart
    const countDanger = document.getElementById('legend-danger-count');
    const countCaution = document.getElementById('legend-caution-count');
    const countNominal = document.getElementById('legend-nominal-count');
    if (countDanger) countDanger.textContent = riskSummary.DANGER || 0;
    if (countCaution) countCaution.textContent = riskSummary.CAUTION || 0;
    if (countNominal) countNominal.textContent = riskSummary.NOMINAL || 0;

    if (window.MineBoardCharts) {
      if (isInitial) {
        window.MineBoardCharts.initDonut(riskSummary);
        window.MineBoardCharts.initTrend(history);
      } else {
        window.MineBoardCharts.updateDonut(riskSummary);
        window.MineBoardCharts.updateTrend(history);
      }
    }

    // 3. Update 2D Live Position Map Blips
    if (window.MineBoardRadar) {
      window.MineBoardRadar.updateBlips(currentTrucks);
    }

    // 4. Update Trend Chart Step Subtitle
    const trendStep = document.getElementById('trend-current-step');
    if (trendStep) trendStep.textContent = currentStep + 1;

    // 5. Update Full Telemetry Table Rows
    Object.keys(currentTrucks).forEach(tid => {
      const t = currentTrucks[tid];
      const rowId = `row-${tid.replace(/\s+/g, '-')}`;
      const row = document.getElementById(rowId);
      if (!row) return;

      const isDanger = t.risk === 'DANGER';
      const isCaution = t.risk === 'CAUTION';

      // Badge HTML
      let badgeHtml = '';
      if (isDanger) {
        badgeHtml = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
          <span class="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span> DANGER
        </span>`;
      } else if (isCaution) {
        badgeHtml = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span> CAUTION
        </span>`;
      } else {
        badgeHtml = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> NOMINAL
        </span>`;
      }

      // Traffic Signal HTML
      const chipHtml = `
        <span class="traffic-signal-chip" title="CAS Status: ${t.risk}">
          <span class="traffic-dot red ${isDanger ? 'active' : 'dimmed'}"></span>
          <span class="traffic-dot amber ${isCaution ? 'active' : 'dimmed'}"></span>
          <span class="traffic-dot green ${(!isDanger && !isCaution) ? 'active' : 'dimmed'}"></span>
        </span>
      `;

      // Surface HTML
      const surfaceHtml = t.rain 
        ? `<span class="text-amber-400 font-semibold flex items-center gap-1"><i data-lucide="cloud-rain" class="w-3.5 h-3.5"></i> Wet / Rain</span>`
        : `<span class="text-slate-400 flex items-center gap-1"><i data-lucide="sun" class="w-3.5 h-3.5"></i> Dry</span>`;

      // Blind Spot HTML
      const blindHtml = t.motion
        ? `<span class="text-rose-400 font-semibold flex items-center gap-1 animate-pulse"><i data-lucide="user-x" class="w-3.5 h-3.5"></i> Motion (${t.blindspot_dist_m}m)</span>`
        : `<span class="text-slate-500">Clear</span>`;

      // TTC HTML
      const ttcHtml = t.ttc_s < 900
        ? `<span class="font-bold ${t.ttc_s < 2.5 ? 'text-rose-400' : (t.ttc_s < 5.0 ? 'text-amber-400' : 'text-emerald-400')}">${t.ttc_s}s</span>`
        : `<span class="text-slate-500">CLEAR</span>`;

      row.innerHTML = `
        <td class="py-3 px-3 font-semibold text-white whitespace-nowrap">
          <a href="/truck/${encodeURIComponent(tid)}" class="flex items-center gap-2 hover:text-sky-400 transition-colors">
            <span>${tid}</span>
            ${chipHtml}
          </a>
        </td>
        <td class="py-3 px-3 whitespace-nowrap">${badgeHtml}</td>
        <td class="py-3 px-3 whitespace-nowrap">
          <span class="font-bold ${t.speed_kmh > 20 ? 'text-rose-400' : 'text-slate-200'}">${t.speed_kmh}</span>
          <span class="text-[10px] text-slate-500">km/h</span>
        </td>
        <td class="py-3 px-3 whitespace-nowrap">
          <span class="font-bold ${t.distance_m < 15 ? 'text-rose-400' : (t.distance_m < 22 ? 'text-amber-400' : 'text-slate-200')}">${t.distance_m}m</span>
          <span class="text-[10px] text-slate-400 block truncate max-w-[130px]" title="${t.obstacle_target}">${t.obstacle_target}</span>
        </td>
        <td class="py-3 px-3 whitespace-nowrap">${ttcHtml}</td>
        <td class="py-3 px-3 whitespace-nowrap">
          <span class="font-bold ${t.gas_ppm >= 500 ? 'text-rose-400' : (t.gas_ppm >= 300 ? 'text-amber-400' : 'text-slate-300')}">${t.gas_ppm}</span>
          <span class="text-[10px] text-slate-500">PPM</span>
        </td>
        <td class="py-3 px-3 whitespace-nowrap">
          <span class="text-slate-300">${t.temp_c}&deg;C</span>
          <span class="text-slate-500">&bull;</span>
          <span class="${t.humidity >= 80 ? 'text-amber-400 font-semibold' : 'text-slate-400'}">${t.humidity}%</span>
        </td>
        <td class="py-3 px-3 whitespace-nowrap">${surfaceHtml}</td>
        <td class="py-3 px-3 whitespace-nowrap">${blindHtml}</td>
        <td class="py-3 px-3 text-right whitespace-nowrap">
          <span class="inline-flex items-center gap-1 text-emerald-400 font-bold" title="All 6 Sensors Online">
            <i data-lucide="check" class="w-3.5 h-3.5"></i>
            <span>6/6 OK</span>
          </span>
        </td>
      `;
    });
  }

  // ========================================================
  // PAGE 2: DRIVER IN-CAB VIEW UPDATES
  // ========================================================
  const currentTruckId = getActiveTruckIdFromPath();
  if (currentTruckId && currentTrucks[currentTruckId]) {
    const t = currentTrucks[currentTruckId];
    const isDanger = t.risk === 'DANGER';
    const isCaution = t.risk === 'CAUTION';
    const riskColor = isDanger ? '#ef4444' : (isCaution ? '#f59e0b' : '#10b981');

    // 1. Hazard State Banner
    const banner = document.getElementById('cockpit-hazard-banner');
    const stateTitle = document.getElementById('hazard-state-title');
    const headline = document.getElementById('hazard-headline');
    const action = document.getElementById('hazard-action');

    if (banner) {
      banner.className = `p-5 rounded-xl border flex flex-col sm:flex-row items-center justify-between gap-6 transition-all ${
        isDanger ? 'bg-rose-950/25 border-rose-500/50 shadow-[0_0_20px_rgba(239,68,68,0.15)] alert-pulse-danger' 
        : (isCaution ? 'bg-amber-950/20 border-amber-500/40 shadow-[0_0_16px_rgba(245,158,11,0.12)]' 
        : 'bg-emerald-950/20 border-emerald-500/40')
      }`;
    }

    if (stateTitle) {
      stateTitle.style.color = riskColor;
      if (isDanger) {
        stateTitle.innerHTML = `<span class="flex items-center justify-center sm:justify-start gap-2"><i data-lucide="shield-alert" class="w-7 h-7 animate-bounce"></i> DANGER</span>`;
      } else if (isCaution) {
        stateTitle.innerHTML = `<span class="flex items-center justify-center sm:justify-start gap-2"><i data-lucide="alert-triangle" class="w-7 h-7"></i> CAUTION</span>`;
      } else {
        stateTitle.innerHTML = `<span class="flex items-center justify-center sm:justify-start gap-2"><i data-lucide="shield-check" class="w-7 h-7"></i> NOMINAL</span>`;
      }
    }

    if (headline) headline.textContent = t.risk_headline;
    if (action) action.textContent = t.risk_action;

    // 2. Radial TTC Progress Ring
    const progressBar = document.getElementById('radial-progress-bar');
    const ttcVal = document.getElementById('radial-ttc-value');
    if (progressBar && ttcVal) {
      const rawTtc = t.ttc_s < 900 ? t.ttc_s : 10.0;
      const pct = Math.min(1.0, rawTtc / 8.0);
      const strokeDash = 251.3; // 2 * PI * 40
      const offset = strokeDash * (1 - pct);

      progressBar.setAttribute('stroke', riskColor);
      progressBar.setAttribute('stroke-dashoffset', offset.toFixed(1));

      ttcVal.style.color = riskColor;
      ttcVal.innerHTML = t.ttc_s < 900 ? `${t.ttc_s}<span class="text-xs font-normal">s</span>` : '&infin;';
    }

    // 3. AI Camera Bounding Box & HUD
    const bbox = document.getElementById('ai-bounding-box');
    const targetLabel = document.getElementById('ai-target-label');
    const targetDist = document.getElementById('ai-target-dist');
    const detSource = document.getElementById('ai-detection-source');

    if (bbox) {
      const dist = Math.max(1.0, t.distance_m);
      let boxW = Math.min(200, Math.max(65, Math.floor(230 / Math.sqrt(dist))));
      let boxH = Math.floor(boxW * 0.7);
      bbox.style.width = `${boxW}px`;
      bbox.style.height = `${boxH}px`;
      bbox.className = `cam-target-bbox ${isDanger ? 'danger' : (isCaution ? 'caution' : 'safe')}`;

      const tag = bbox.querySelector('div');
      if (tag) tag.style.backgroundColor = riskColor;
    }
    if (targetLabel) targetLabel.textContent = (t.obstacle_target || 'TARGET').substring(0, 18);
    if (targetDist) targetDist.textContent = `${t.distance_m}m`;
    if (detSource) detSource.textContent = t.detection_source || 'AI SENSOR MESH';

    // 4. Sensor Icon Tooltips
    const tipDist = document.getElementById('tooltip-dist');
    const tipGas = document.getElementById('tooltip-gas');
    const tipClimate = document.getElementById('tooltip-climate');
    const tipRain = document.getElementById('tooltip-rain');
    const tipPir = document.getElementById('tooltip-pir');
    const tipGps = document.getElementById('tooltip-gps');

    if (tipDist) tipDist.textContent = `FORWARD: ${t.distance_m} m`;
    if (tipGas) tipGas.textContent = `GAS: ${t.gas_ppm} PPM`;
    if (tipClimate) tipClimate.innerHTML = `${t.temp_c}&deg;C &bull; ${t.humidity}% RH`;
    if (tipRain) tipRain.textContent = `SURFACE: ${t.rain ? 'SLICK / RAIN' : 'DRY ROAD'}`;
    if (tipPir) tipPir.textContent = `PIR: ${t.motion ? `PERSONNEL DETECTED (${t.blindspot_dist_m}m)` : 'BLIND SPOT CLEAR'}`;
    if (tipGps) tipGps.textContent = `GPS: (${t.x}, ${t.y}) &bull; ${t.speed_kmh} km/h`;

    // 5. Quick Metrics Strip
    const stripSpeed = document.getElementById('strip-speed');
    const stripDist = document.getElementById('strip-distance');
    const stripClosing = document.getElementById('strip-closing');
    if (stripSpeed) stripSpeed.textContent = t.speed_kmh;
    if (stripDist) stripDist.textContent = t.distance_m;
    if (stripClosing) stripClosing.textContent = t.speed_ms;
  }

  // Re-run Lucide icon parser for updated DOM nodes
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Helper to determine active truck from URL
function getActiveTruckIdFromPath() {
  const parts = window.location.pathname.split('/');
  if (parts.length >= 3 && parts[1] === 'truck') {
    return decodeURIComponent(parts[2]);
  }
  return null;
}
