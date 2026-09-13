/**
 * MineBoard CAS — 2D Live Position Map Logic (radar.js)
 * Updates truck dot coordinates, pulsing risk rings, and hover tooltips.
 */

window.MineBoardRadar = {
  updateBlips: function(trucks) {
    if (!trucks) return;

    Object.keys(trucks).forEach(tid => {
      const t = trucks[tid];
      const blipId = `blip-${tid.replace(/\s+/g, '-')}`;
      const el = document.getElementById(blipId);
      if (!el) return;

      // Update position (x% and 100 - y%)
      el.style.left = `${t.x}%`;
      el.style.top = `${100 - t.y}%`;

      // Update risk class for pulsing colors
      el.classList.remove('danger', 'caution', 'safe');
      const riskCls = t.risk === 'DANGER' ? 'danger' : (t.risk === 'CAUTION' ? 'caution' : 'safe');
      el.classList.add(riskCls);

      // Update tooltip contents
      const tooltip = el.querySelector('.truck-tooltip');
      if (tooltip) {
        const headlineColor = t.risk === 'DANGER' ? 'text-rose-400' : (t.risk === 'CAUTION' ? 'text-amber-400' : 'text-emerald-400');
        tooltip.innerHTML = `
          <div class="font-bold text-white flex items-center gap-1.5">
            <span>${tid}</span>
            <span class="traffic-signal-chip" title="CAS Status: ${t.risk}">
              <span class="traffic-dot red ${t.risk === 'DANGER' ? 'active' : 'dimmed'}"></span>
              <span class="traffic-dot amber ${t.risk === 'CAUTION' ? 'active' : 'dimmed'}"></span>
              <span class="traffic-dot green ${t.risk === 'NOMINAL' ? 'active' : 'dimmed'}"></span>
            </span>
          </div>
          <div class="text-[10px] text-slate-400">
            (${t.x}, ${t.y}) &bull; ${t.speed_kmh} km/h
          </div>
          <div class="text-[9px] ${headlineColor} font-semibold">
            ${t.risk_headline || ''}
          </div>
        `;
      }
    });
  }
};
