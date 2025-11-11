// Simple client-side sorter for the publication list
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const list = document.querySelector('.publication-list');
    if (!list) return;

    const controls = document.getElementById('sort-controls');
    const buttons = controls ? Array.from(controls.querySelectorAll('.btn-sort')) : [];
    const originalItems = Array.from(list.querySelectorAll('.publication-item'));

    // Default: sort by year DESC on load
    let currentKey = 'year';
    let ascending = false;
    sortAndRender(currentKey, ascending);

    // Wire up buttons
    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const key = btn.dataset.sort;

        // Toggle order if clicking the same key; otherwise pick default order
        if (currentKey === key) {
          ascending = !ascending;
        } else {
          currentKey = key;
          // sensible defaults
          ascending = key === 'year' ? false : true;
        }

        // Visual state
        buttons.forEach((b) => {
          b.classList.remove('ring-2', 'ring-indigo-500', 'bg-gray-50');
          b.setAttribute('aria-pressed', 'false');
          const arr = b.querySelector('.sort-arrow');
          if (arr) arr.remove();
        });
        btn.classList.add('ring-2', 'ring-indigo-500', 'bg-gray-50');
        btn.setAttribute('aria-pressed', 'true');
        const arrow = document.createElement('span');
        arrow.className = 'sort-arrow ml-1';
        arrow.textContent = ascending ? '↑' : '↓';
        btn.appendChild(arrow);

        sortAndRender(currentKey, ascending);
      });
    });

    function sortAndRender(key, asc) {
      const items = Array.from(list.querySelectorAll('.publication-item'));
      const sorted = items.sort((a, b) => compare(a, b, key, asc));
      // Re-append in new order
      sorted.forEach((el) => list.appendChild(el));
    }

    function compare(aEl, bEl, key, asc) {
      let a = aEl.dataset[key] ?? '';
      let b = bEl.dataset[key] ?? '';

      if (key === 'year') {
        const ai = parseInt(a, 10) || 0;
        const bi = parseInt(b, 10) || 0;
        return asc ? ai - bi : bi - ai;
      }

      // locale-aware string compare for type/title
      const cmp = a.localeCompare(b, undefined, { sensitivity: 'base' });
      return asc ? cmp : -cmp;
    }
  });
})();
