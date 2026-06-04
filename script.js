document.addEventListener('DOMContentLoaded', () => {

  // --- ハンバーガーメニュー ---
  const hamburger = document.getElementById('hamburger');
  const nav       = document.getElementById('nav');
  const overlay   = document.getElementById('nav-overlay');

  const openNav = () => {
    hamburger.classList.add('open');
    nav.classList.add('open');
    overlay.classList.add('active');
    hamburger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  };
  const closeNav = () => {
    hamburger.classList.remove('open');
    nav.classList.remove('open');
    overlay.classList.remove('active');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  };

  if (hamburger) hamburger.addEventListener('click', () => {
    nav.classList.contains('open') ? closeNav() : openNav();
  });
  if (overlay) overlay.addEventListener('click', closeNav);
  nav && nav.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', closeNav);
  });

  // --- スムーズスクロール ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const id = this.getAttribute('href');
      if (id === '#' || !id.startsWith('#')) return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const headerH = document.querySelector('.header')?.offsetHeight || 0;
      const top = target.getBoundingClientRect().top + window.pageYOffset - headerH - 20;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // --- スクロールフェードイン ---
  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

  // --- ヘッダー スクロールで背景を強調 ---
  const header = document.getElementById('header');
  window.addEventListener('scroll', () => {
    header?.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });

  // --- お問い合わせフォーム (Web3Forms) ---
  const form      = document.getElementById('contact-form');
  const resultEl  = document.getElementById('form-result');
  const submitBtn = document.getElementById('submit-btn');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const json = JSON.stringify(Object.fromEntries(new FormData(form)));

      resultEl.style.display = 'block';
      resultEl.style.color   = 'var(--accent)';
      resultEl.textContent   = '送信中…';
      submitBtn.disabled     = true;

      try {
        const res  = await fetch('https://formspree.io/f/xlgkdnok', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: json,
        });
        const data = await res.json();
        if (res.ok) {
          resultEl.style.color = '#4caf50';
          resultEl.textContent = 'お便りが届きました。お返事まで少々お待ちください。';
          form.reset();
        } else {
          throw new Error(data.error || '送信に失敗しました。');
        }
      } catch (err) {
        resultEl.style.color = '#e53935';
        resultEl.textContent = err.message || '送信に失敗しました。通信環境をご確認ください。';
      } finally {
        submitBtn.disabled = false;
        setTimeout(() => { resultEl.style.display = 'none'; }, 8000);
      }
    });
  }

});
