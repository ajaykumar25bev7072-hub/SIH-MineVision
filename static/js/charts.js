/**
 * MineBoard CAS — Chart.js Configurations (charts.js)
 * Manages Risk Distribution Donut & Speed/Distance History Trends.
 */

let riskDonutChart = null;
let trendLineChart = null;

window.MineBoardCharts = {
  // Initialize Donut Chart
  initDonut: function(summary) {
    const canvas = document.getElementById('riskDonutChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const data = [
      summary?.DANGER || 0,
      summary?.CAUTION || 0,
      summary?.NOMINAL || 0
    ];

    riskDonutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['DANGER', 'CAUTION', 'NOMINAL'],
        datasets: [{
          data: data,
          backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
          borderColor: '#0f172a',
          borderWidth: 3,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#020617',
            borderColor: '#1e293b',
            borderWidth: 1,
            titleFont: { family: 'JetBrains Mono', size: 11 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 8,
            boxPadding: 4
          }
        }
      }
    });
  },

  // Update Donut Chart
  updateDonut: function(summary) {
    if (!riskDonutChart) {
      this.initDonut(summary);
      return;
    }
    riskDonutChart.data.datasets[0].data = [
      summary?.DANGER || 0,
      summary?.CAUTION || 0,
      summary?.NOMINAL || 0
    ];
    riskDonutChart.update();
  },

  // Initialize History Trend Line Chart
  initTrend: function(historyData) {
    const canvas = document.getElementById('trendLineChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const labels = historyData.map(h => `T+${h.step * 2}s`);
    
    // Truck A distance and speed
    const distA = historyData.map(h => h.trucks?.['Truck A']?.distance_m ?? 0);
    const speedA = historyData.map(h => h.trucks?.['Truck A']?.speed_kmh ?? 0);

    // Truck C gas (scaled to 100 max)
    const gasC = historyData.map(h => (h.trucks?.['Truck C']?.gas_ppm ?? 0) / 10.0);

    trendLineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Truck A: Forward Distance (m)',
            data: distA,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.05)',
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 2,
            fill: true
          },
          {
            label: 'Truck A: Speed (km/h)',
            data: speedA,
            borderColor: '#38bdf8',
            borderWidth: 2,
            borderDash: [4, 4],
            tension: 0.3,
            pointRadius: 1,
            fill: false
          },
          {
            label: 'Truck C: Gas PPM (/10)',
            data: gasC,
            borderColor: '#f59e0b',
            borderWidth: 1.5,
            tension: 0.3,
            pointRadius: 1,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#64748b',
              font: { family: 'JetBrains Mono', size: 10 },
              maxTicksLimit: 10
            }
          },
          y: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#64748b',
              font: { family: 'JetBrains Mono', size: 10 }
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#94a3b8',
              font: { family: 'JetBrains Mono', size: 11 },
              boxWidth: 12,
              usePointStyle: true
            }
          },
          tooltip: {
            backgroundColor: '#020617',
            borderColor: '#1e293b',
            borderWidth: 1,
            titleFont: { family: 'JetBrains Mono', size: 11 },
            bodyFont: { family: 'JetBrains Mono', size: 11 }
          }
        }
      }
    });
  },

  // Update Trend Line Chart
  updateTrend: function(historyData) {
    if (!trendLineChart) {
      this.initTrend(historyData);
      return;
    }
    trendLineChart.data.labels = historyData.map(h => `T+${h.step * 2}s`);
    trendLineChart.data.datasets[0].data = historyData.map(h => h.trucks?.['Truck A']?.distance_m ?? 0);
    trendLineChart.data.datasets[1].data = historyData.map(h => h.trucks?.['Truck A']?.speed_kmh ?? 0);
    trendLineChart.data.datasets[2].data = historyData.map(h => (h.trucks?.['Truck C']?.gas_ppm ?? 0) / 10.0);
    trendLineChart.update();
  }
};
