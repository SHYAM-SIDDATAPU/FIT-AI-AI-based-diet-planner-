/**
 * dashboard.js — Sidebar, water tracker, Chart.js charts
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Sidebar toggle (mobile) ────────────────── */
  const hamburger = document.getElementById('hamburgerBtn');
  const sidebar   = document.getElementById('sidebar');
  const overlay   = document.getElementById('sidebarOverlay');

  function openSidebar()  {
    sidebar?.classList.add('open');
    overlay?.classList.add('visible');
  }
  function closeSidebar() {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('visible');
  }

  hamburger?.addEventListener('click', openSidebar);
  overlay?.addEventListener('click', closeSidebar);

  /* ── Water circles ──────────────────────────── */
  document.querySelectorAll('.water-circle').forEach((el, i, arr) => {
    el.addEventListener('click', () => {
      const filled = el.classList.contains('filled');
      // fill / unfill up to clicked index
      arr.forEach((c, j) => {
        if (!filled) {
          c.classList.toggle('filled', j <= i);
        } else {
          c.classList.toggle('filled', j < i);
        }
      });
    });
  });

  /* ── Charts (progress page) ─────────────────── */
  function parseData(id) {
    const el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : [];
  }

  // Weight chart
  const weightCtx = document.getElementById('weightChart');
  if (weightCtx) {
    const labels  = parseData('chartDates');
    const weights = parseData('chartWeights');
    new Chart(weightCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Weight (kg)',
          data: weights,
          borderColor: '#2563EB',
          backgroundColor: 'rgba(37,99,235,.08)',
          borderWidth: 2.5,
          pointBackgroundColor: '#2563EB',
          pointRadius: 4,
          fill: true,
          tension: 0.4,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: {
          y: { grid: { color: '#F1F5F9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // BMI chart
  const bmiCtx = document.getElementById('bmiChart');
  if (bmiCtx) {
    const labels = parseData('chartDates');
    const bmis   = parseData('chartBmis');
    new Chart(bmiCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'BMI',
          data: bmis,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16,185,129,.08)',
          borderWidth: 2.5,
          pointBackgroundColor: '#10B981',
          pointRadius: 4,
          fill: true,
          tension: 0.4,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: {
          y: { min: 10, max: 45, grid: { color: '#F1F5F9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // Calories chart
  const calCtx = document.getElementById('calChart');
  if (calCtx) {
    const labels   = parseData('chartDates');
    const calories = parseData('chartCalories');
    new Chart(calCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Calories Consumed',
          data: calories,
          backgroundColor: 'rgba(124,58,237,.65)',
          borderColor: '#7C3AED',
          borderWidth: 1.5,
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: {
          y: { grid: { color: '#F1F5F9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  /* ── BMI donut on dashboard ─────────────────── */
  const bmiRing = document.getElementById('bmiRingCanvas');
  if (bmiRing) {
    const bmi = parseFloat(bmiRing.dataset.bmi || 0);
    let colour = '#10B981';
    if      (bmi < 18.5) colour = '#F59E0B';
    else if (bmi >= 30)  colour = '#EF4444';
    else if (bmi >= 25)  colour = '#F97316';

    new Chart(bmiRing, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [bmi, 45 - bmi],
          backgroundColor: [colour, '#F1F5F9'],
          borderWidth: 0,
        }]
      },
      options: {
        cutout: '72%',
        responsive: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } }
      }
    });
  }

  /* ── Confirm delete (admin) ─────────────────── */
  document.querySelectorAll('.btn-delete-confirm').forEach(btn => {
    btn.addEventListener('click', e => {
      if (!confirm('Are you sure you want to delete this user? This cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  /* ── Fade-up on scroll ───────────────────────── */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        en.target.style.animationPlayState = 'running';
        observer.unobserve(en.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-up').forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
  });
});