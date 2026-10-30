const initTheme = () => {
  const savedTheme = localStorage.getItem('theme');
  const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  
  if (savedTheme === 'light' || (!savedTheme && prefersLight)) {
    document.documentElement.setAttribute('data-theme', 'light');
    updateThemeIcon('light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
    updateThemeIcon('dark');
  }
  updateChartColors();
};

const toggleTheme = () => {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateThemeIcon(newTheme);
  updateChartColors();
};

const updateThemeIcon = (theme) => {
  const icon = document.getElementById('theme-toggle-icon');
  if (icon) {
    if (theme === 'light') {
      icon.className = 'ri-moon-line';
    } else {
      icon.className = 'ri-sun-line';
    }
  }
};

const updateChartColors = () => {
  if (typeof Chart === 'undefined') return;
  
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  const textColor = isLight ? '#64748b' : '#94a3b8';
  const gridColor = isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)';
  
  Chart.defaults.color = textColor;
  if (Chart.defaults.scale && Chart.defaults.scale.grid) {
      Chart.defaults.scale.grid.color = gridColor;
  }
  
  // Re-render any existing charts
  for (let id in Chart.instances) {
    Chart.instances[id].update();
  }
};

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  
  const toggleBtn = document.getElementById('theme-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', toggleTheme);
  }
});
