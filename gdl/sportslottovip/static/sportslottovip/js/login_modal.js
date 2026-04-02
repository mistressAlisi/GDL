document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('loginModal');
  const container = document.getElementById('loginContainer');
  const closeBtn = document.getElementById('closeLogin');
  const backdrop = modal.querySelector('.login-backdrop');

  // All triggers for opening the login modal
  const triggers = [
    document.getElementById('loginTrigger'),
    document.getElementById('startNowTrigger'),
    ...document.querySelectorAll('.start-btn')
  ];

  // Buttons that should redirect to /how-to-play
  const learnBtns = document.querySelectorAll('#learnMoreBtn');

  function loadWidget(theme) {
    const url = `/slv/login-widget/?theme=${theme}`;
    container.innerHTML = '<div class="loading-spinner">Loading...</div>';
    fetch(url)
      .then(res => res.text())
      .then(html => {
        container.innerHTML = html;
        container.querySelectorAll('script').forEach(script => {
          const s = document.createElement('script');
          if (script.type) s.type = script.type;
          if (script.src) s.src = script.src;
          else s.textContent = script.textContent;
          document.body.appendChild(s);
        });
      })
      .catch(() => {
        container.innerHTML = '<p>Error loading login widget.</p>';
      });
  }

  // Open modal when any trigger is clicked
  triggers.forEach(btn => {
    if (btn) {
      btn.addEventListener('click', e => {
        e.preventDefault();
        modal.classList.add('active');
        const theme = document.documentElement.getAttribute('data-theme') || 'dark';
        loadWidget(theme);
      });
    }
  });

  // Redirect Learn More buttons
  learnBtns.forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      window.location.href = '/how-to-play';
    });
  });

  // Close modal on backdrop or close button
  [closeBtn, backdrop].forEach(el => {
    el.addEventListener('click', () => {
      modal.classList.remove('active');
      container.innerHTML = '<div class="loading-spinner">Loading...</div>';
    });
  });

  // Reload widget on theme change
  new MutationObserver(() => {
    if (modal.classList.contains('active')) {
      const theme = document.documentElement.getAttribute('data-theme') || 'dark';
      loadWidget(theme);
    }
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
});
