/**
 * validation.js — Client-side form validation
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss flash messages ──────────────
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 4500);
  });

  // ── Register form ────────────────────────────
  const regForm = document.getElementById('registerForm');
  if (regForm) {
    regForm.addEventListener('submit', e => {
      let valid = true;
      clearErrors(regForm);

      const name     = regForm.querySelector('#name');
      const email    = regForm.querySelector('#email');
      const password = regForm.querySelector('#password');
      const confirm  = regForm.querySelector('#confirm_password');

      if (!name.value.trim()) {
        showError(name, 'Name is required.'); valid = false;
      }
      if (!email.value.trim() || !email.value.includes('@')) {
        showError(email, 'Valid email address is required.'); valid = false;
      }
      if (password.value.length < 6) {
        showError(password, 'Password must be at least 6 characters.'); valid = false;
      }
      if (password.value !== confirm.value) {
        showError(confirm, 'Passwords do not match.'); valid = false;
      }

      if (!valid) e.preventDefault();
    });
  }

  // ── Login form ───────────────────────────────
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', e => {
      let valid = true;
      clearErrors(loginForm);

      const email    = loginForm.querySelector('#email');
      const password = loginForm.querySelector('#password');

      if (!email.value.trim() || !email.value.includes('@')) {
        showError(email, 'Valid email is required.'); valid = false;
      }
      if (!password.value) {
        showError(password, 'Password is required.'); valid = false;
      }

      if (!valid) e.preventDefault();
    });
  }

  // ── Profile form ─────────────────────────────
  const profileForm = document.getElementById('profileForm');
  if (profileForm) {
    // Live BMI calculation
    const heightInput = profileForm.querySelector('#height');
    const weightInput = profileForm.querySelector('#weight');
    const bmiDisplay  = document.getElementById('bmiPreview');

    function updateBMI() {
      const h = parseFloat(heightInput?.value);
      const w = parseFloat(weightInput?.value);
      if (h > 0 && w > 0 && bmiDisplay) {
        const hm  = h / 100;
        const bmi = (w / (hm * hm)).toFixed(1);
        let cat = '';
        if      (bmi < 18.5) cat = 'Underweight';
        else if (bmi < 25)   cat = 'Normal';
        else if (bmi < 30)   cat = 'Overweight';
        else                 cat = 'Obese';

        bmiDisplay.innerHTML = `
          <span class="fw-700" style="font-size:1.1rem;">${bmi}</span>
          <span class="badge ${bmiClass(bmi)} ms-2">${cat}</span>
        `;
      }
    }

    heightInput?.addEventListener('input', updateBMI);
    weightInput?.addEventListener('input', updateBMI);
    updateBMI();

    profileForm.addEventListener('submit', e => {
      let valid = true;
      clearErrors(profileForm);

      const name  = profileForm.querySelector('#name');
      const age   = profileForm.querySelector('#age');
      const h     = profileForm.querySelector('#height');
      const w     = profileForm.querySelector('#weight');

      if (name && !name.value.trim()) { showError(name, 'Name is required.'); valid = false; }

      if (age) {
        const av = parseInt(age.value);
        if (isNaN(av) || av < 10 || av > 120) { showError(age, 'Age must be 10–120.'); valid = false; }
      }
      if (h) {
        const hv = parseFloat(h.value);
        if (isNaN(hv) || hv < 50 || hv > 250) { showError(h, 'Height must be 50–250 cm.'); valid = false; }
      }
      if (w) {
        const wv = parseFloat(w.value);
        if (isNaN(wv) || wv < 20 || wv > 300) { showError(w, 'Weight must be 20–300 kg.'); valid = false; }
      }

      if (!valid) e.preventDefault();
    });
  }

  // ── Progress form ─────────────────────────────
  const progressForm = document.getElementById('progressForm');
  if (progressForm) {
    progressForm.addEventListener('submit', e => {
      let valid = true;
      clearErrors(progressForm);

      const weight = progressForm.querySelector('#weight');
      const water  = progressForm.querySelector('#water');

      if (weight && weight.value) {
        const wv = parseFloat(weight.value);
        if (isNaN(wv) || wv < 20 || wv > 300) { showError(weight, 'Weight must be 20–300 kg.'); valid = false; }
      }
      if (water && water.value) {
        const wv = parseFloat(water.value);
        if (isNaN(wv) || wv < 0 || wv > 20) { showError(water, 'Water must be 0–20 litres.'); valid = false; }
      }

      if (!valid) e.preventDefault();
    });
  }

  // ── Helpers ──────────────────────────────────
  function showError(input, msg) {
    input.classList.add('is-invalid');
    const err = document.createElement('div');
    err.className = 'form-error';
    err.textContent = msg;
    input.parentNode.appendChild(err);
  }

  function clearErrors(form) {
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.form-error').forEach(el => el.remove());
  }

  function bmiClass(bmi) {
    if (bmi < 18.5) return 'badge-warning';
    if (bmi < 25)   return 'badge-success';
    if (bmi < 30)   return 'badge-warning';
    return 'badge-danger';
  }
});