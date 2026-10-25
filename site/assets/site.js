(() => {
  'use strict';
  const tabs = [...document.querySelectorAll('[role="tab"][data-tab]')];
  function activate(tab, focus = false) {
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
    });
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); activate(tabs[next], true); }
    });
  });
  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const code = document.getElementById(button.dataset.copy).querySelector('pre code');
      const old = button.textContent;
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.textContent = 'Copied';
        document.querySelector('.copy-status').textContent = 'Example copied to clipboard.';
      } catch {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(code); selection.removeAllRanges(); selection.addRange(range);
        button.textContent = 'Select & copy';
        document.querySelector('.copy-status').textContent = 'Clipboard unavailable. Example selected; copy it manually.';
      }
      window.setTimeout(() => { button.textContent = old; }, 2400);
    });
  });
  const guideMenu = document.querySelector('.guide-menu');
  if (guideMenu) guideMenu.open = !window.matchMedia('(max-width:760px)').matches;
  const filter = document.querySelector('.doc-search');
  if (filter) filter.addEventListener('input', () => {
    const value = filter.value.trim().toLowerCase();
    const links = [...document.querySelectorAll('.doc-sidebar nav a')];
    links.forEach(link => { link.hidden = !link.textContent.toLowerCase().includes(value); });
    document.querySelector('.search-empty').hidden = links.some(link => !link.hidden);
  });
})();
