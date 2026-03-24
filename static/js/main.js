/* ═══════════════════════════════════════════════
   YOVO — Main JavaScript
   Your Old, Valued Once More.
═══════════════════════════════════════════════ */

'use strict';

// ─── Theme ─────────────────────────────────────
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

const savedTheme = localStorage.getItem('yovo-theme') || 'light';
html.setAttribute('data-theme', savedTheme);

themeToggle?.addEventListener('click', () => {
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('yovo-theme', next);
});

// ─── Navbar scroll effect ──────────────────────
const navbar = document.getElementById('navbar');
const handleScroll = () => {
  if (window.scrollY > 20) {
    navbar?.classList.add('scrolled');
  } else {
    navbar?.classList.remove('scrolled');
  }
};
window.addEventListener('scroll', handleScroll, { passive: true });

// ─── Hamburger menu ────────────────────────────
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
hamburger?.addEventListener('click', () => {
  mobileMenu.classList.toggle('open');
  const spans = hamburger.querySelectorAll('span');
  if (mobileMenu.classList.contains('open')) {
    spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
    spans[1].style.opacity = '0';
    spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
  } else {
    spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
  }
});

// ─── User dropdown ─────────────────────────────
const userMenuBtn = document.getElementById('userMenuBtn');
const userDropdown = document.getElementById('userDropdown');
userMenuBtn?.addEventListener('click', (e) => {
  e.stopPropagation();
  userDropdown.classList.toggle('open');
});
document.addEventListener('click', () => {
  userDropdown?.classList.remove('open');
});

// ─── Scroll Reveal (Intersection Observer) ─────
const revealElements = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Stagger adjacent reveals
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, i * 60);
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
);
revealElements.forEach(el => revealObserver.observe(el));

// ─── Toast auto-dismiss ─────────────────────────
document.querySelectorAll('.toast').forEach(toast => {
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(40px)';
    toast.style.transition = '0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 4500);
});

// ─── Smooth anchor scroll ──────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ─── File input label update ───────────────────
document.querySelectorAll('input[type="file"]').forEach(input => {
  input.addEventListener('change', () => {
    if (input.files.length > 0) {
      const name = input.files[0].name;
      const hint = input.parentElement.querySelector('.form-hint');
      if (hint) hint.textContent = `Selected: ${name}`;
    }
  });
});

// ─── Page transition ───────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.3s ease';
  requestAnimationFrame(() => {
    document.body.style.opacity = '1';
  });
});
