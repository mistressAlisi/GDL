import accordionItems from './_accordionData.js';

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('infoAccordion');
  if (!container) return;

  accordionItems.forEach(item => {
    container.insertAdjacentHTML('beforeend', `
      <div class="accordion-item info-card mb-3">
        <h2 class="accordion-header">
          <button
            class="accordion-button collapsed d-flex align-items-center gap-3"
            type="button"
            aria-expanded="false"
            aria-controls="${item.id}">
            <span class="icon">${item.icon}</span>
            <span class="accordion-title-text">${item.title}</span>
          </button>
        </h2>

        <div id="${item.id}" class="accordion-collapse collapse">
          <div class="accordion-body">
            ${item.body}
          </div>
        </div>
      </div>
    `);

    const collapseEl = document.getElementById(item.id);
    const button = container.querySelector(
      `button[aria-controls="${item.id}"]`
    );

    const collapse = new window.bootstrap.Collapse(collapseEl, {
      toggle: false
    });

    // 🔁 Sync arrow with actual collapse state
    collapseEl.addEventListener('shown.bs.collapse', () => {
      button.classList.remove('collapsed');
      button.setAttribute('aria-expanded', 'true');
    });

    collapseEl.addEventListener('hidden.bs.collapse', () => {
      button.classList.add('collapsed');
      button.setAttribute('aria-expanded', 'false');
    });

    // Toggle collapse on click
    button.addEventListener('click', () => {
      collapse.toggle();
    });
  });

});
