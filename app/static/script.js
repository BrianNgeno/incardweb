// InCAD Website JS

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });

  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  const tabSections = document.querySelectorAll('.tab-list');
  tabSections.forEach(tabList => {
    tabList.addEventListener('click', event => {
      const button = event.target.closest('.tab');
      if (!button) return;
      const tabs = Array.from(tabList.querySelectorAll('.tab'));
      const panels = document.querySelectorAll('.tab-panel');
      const target = button.dataset.tab;
      tabs.forEach(tab => tab.classList.toggle('active', tab === button));
      panels.forEach(panel => panel.classList.toggle('active', panel.id === 'tab-' + target));
    });
  });

  const modalTriggers = document.querySelectorAll('[data-modal]');
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const modal = document.getElementById(trigger.dataset.modal);
      if (modal) modal.setAttribute('aria-hidden', 'false');
    });
  });

  const modalClosers = document.querySelectorAll('[data-modal-close]');
  modalClosers.forEach(closeEl => {
    closeEl.addEventListener('click', () => {
      const modal = closeEl.closest('.modal');
      if (modal) modal.setAttribute('aria-hidden', 'true');
    });
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      document.querySelectorAll('.modal[aria-hidden="false"]').forEach(modal => modal.setAttribute('aria-hidden', 'true'));
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const track = document.querySelector('.programs-carousel .slider-track');
  const slides = track ? Array.from(track.children) : [];
  const prev = document.querySelector('.programs-carousel .slider-control.prev');
  const next = document.querySelector('.programs-carousel .slider-control.next');
  if (!track || slides.length === 0 || !prev || !next) return;

  let currentIndex = 0;

  const updateSlider = index => {
    currentIndex = (index + slides.length) % slides.length;
    track.style.transform = `translateX(-${currentIndex * 100}%)`;
  };

  prev.addEventListener('click', () => updateSlider(currentIndex - 1));
  next.addEventListener('click', () => updateSlider(currentIndex + 1));

  let startX = 0;
  let isDragging = false;

  track.addEventListener('pointerdown', event => {
    isDragging = true;
    startX = event.clientX;
    track.style.transition = 'none';
  });

  track.addEventListener('pointermove', event => {
    if (!isDragging) return;
    const delta = event.clientX - startX;
    track.style.transform = `translateX(calc(-${currentIndex * 100}% + ${delta}px))`;
  });

  const stopDrag = event => {
    if (!isDragging) return;
    isDragging = false;
    const delta = event.clientX - startX;
    track.style.transition = '';
    if (delta < -60) updateSlider(currentIndex + 1);
    else if (delta > 60) updateSlider(currentIndex - 1);
    else updateSlider(currentIndex);
  };

  track.addEventListener('pointerup', stopDrag);
  track.addEventListener('pointerleave', stopDrag);
});
