let emotionChartInstance = null;
let intentChartInstance = null;
let timelineChartInstance = null;
let analyticsEmotionChartInstance = null;

class ChartRenderer {
  static getTextColor() {
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';
    return theme === 'light' ? '#334155' : '#cbd5e1';
  }

  static getGridColor() {
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';
    return theme === 'light' ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.08)';
  }

  static renderEmotionChart(canvasId, distribution) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (emotionChartInstance) {
      emotionChartInstance.destroy();
    }

    const labels = Object.keys(distribution).map(l => l.charAt(0).toUpperCase() + l.slice(1));
    const data = Object.values(distribution);

    const colors = [
      '#ef4444', // Anger - red
      '#3b82f6', // Sadness - blue
      '#f59e0b', // Fear - amber
      '#10b981', // Joy - emerald
      '#8b5cf6', // Surprise - purple
      '#ec4899', // Disgust - pink
      '#64748b'  // Neutral - slate
    ];

    const textColor = ChartRenderer.getTextColor();

    emotionChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: document.documentElement.getAttribute('data-theme') === 'light' ? '#ffffff' : '#111827'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' } }
          }
        },
        cutout: '68%'
      }
    });
  }

  static renderTimelineChart(canvasId, timelineData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (timelineChartInstance) {
      timelineChartInstance.destroy();
    }

    const labels = timelineData.map(t => t.phase);
    const sentimentScores = timelineData.map(t => t.sentiment_score);
    const positivePcts = timelineData.map(t => t.positive_pct);
    const negativePcts = timelineData.map(t => t.negative_pct);

    const textColor = ChartRenderer.getTextColor();
    const gridColor = ChartRenderer.getGridColor();

    timelineChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Sentiment Trajectory (-1.0 to +1.0)',
            data: sentimentScores,
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.15)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#ec4899',
            pointRadius: 6
          },
          {
            label: 'Positive %',
            data: positivePcts,
            borderColor: '#10b981',
            borderWidth: 2,
            borderDash: [5, 5],
            tension: 0.3,
            pointRadius: 3
          },
          {
            label: 'Negative %',
            data: negativePcts,
            borderColor: '#ef4444',
            borderWidth: 2,
            borderDash: [5, 5],
            tension: 0.3,
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { weight: '600' } }
          },
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { weight: '600' } }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' } }
          }
        }
      }
    });
  }

  static renderAnalyticsCharts(analyticsData) {
    const ctxEmotion = document.getElementById('analyticsEmotionChart');
    if (ctxEmotion && analyticsData.emotion_distribution) {
      if (analyticsEmotionChartInstance) analyticsEmotionChartInstance.destroy();
      
      const labels = Object.keys(analyticsData.emotion_distribution);
      const data = Object.values(analyticsData.emotion_distribution);
      const textColor = ChartRenderer.getTextColor();
      const gridColor = ChartRenderer.getGridColor();

      analyticsEmotionChartInstance = new Chart(ctxEmotion, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Document Count',
            data: data,
            backgroundColor: 'rgba(139, 92, 246, 0.7)',
            borderColor: '#8b5cf6',
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { grid: { color: gridColor }, ticks: { color: textColor, font: { weight: '600' } } },
            x: { grid: { color: gridColor }, ticks: { color: textColor, font: { weight: '600' } } }
          },
          plugins: { legend: { display: false } }
        }
      });
    }
  }
}

window.ChartRenderer = ChartRenderer;
