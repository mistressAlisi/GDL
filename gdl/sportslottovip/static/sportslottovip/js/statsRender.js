import statsItems from './_statsData.js';

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById("statsRow");

  statsItems.forEach(stat => {
    const html = `
      <div class="col-md-4 stat-item">
        <h3>${stat.value}</h3>
        <p>${stat.label}</p>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
  });
});
