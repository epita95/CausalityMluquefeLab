/* Progressive enhancement. Content and navigation work without JavaScript. */
(() => {
  document.documentElement.classList.add('js');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  if (toggle && nav) {
    const close = () => {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
    };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', e => { if (e.target.closest('a')) close(); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        close();
        toggle.focus();
      }
    });
    document.addEventListener('click', e => {
      if (!nav.contains(e.target) && !toggle.contains(e.target)) close();
    });
    matchMedia('(min-width: 1051px)').addEventListener('change', close);
  }

  document.querySelectorAll('[data-research-selector]').forEach(section => {
    const grid = section.querySelector('.research-grid');
    const cards = [...section.querySelectorAll('[data-research-select]')];
    const panels = [...section.querySelectorAll('[data-research-panel]')];
    const container = section.querySelector('[data-research-panels]');
    const marker = document.createComment('research panel position');
    container.before(marker);
    const position = card => {
      if (!card || section.dataset.researchPlacement === 'end') return marker.after(container);
      const columns = getComputedStyle(grid).gridTemplateColumns.split(' ').length;
      const last = Math.min(cards.length - 1, (Math.floor(cards.indexOf(card) / columns) + 1) * columns - 1);
      cards[last].after(container);
    };
    const activate = id => {
      const selected = panels.find(panel => panel.id === id);
      const selectedCard = cards.find(card => card.getAttribute('aria-controls') === id);
      cards.forEach(card => {
        const active = card.getAttribute('aria-controls') === id && Boolean(selected);
        card.classList.toggle('is-selected', active);
        card.setAttribute('aria-expanded', String(active));
      });
      position(selectedCard);
      panels.forEach(panel => { panel.hidden = panel !== selected; });
      container.hidden = !selected;
    };
    cards.forEach(card => card.addEventListener('click', event => {
      event.preventDefault();
      const id = card.getAttribute('aria-controls');
      const cardTop = card.getBoundingClientRect().top;
      if (location.hash !== `#${id}`) history.pushState(null, '', `#${id}`);
      activate(id);
      const shift = card.getBoundingClientRect().top - cardTop;
      if (Math.abs(shift) > 1) window.scrollBy({ top: shift, behavior: 'instant' });
    }));
    const syncSelection = () => {
      const id = location.hash.slice(1);
      const fallback = section.dataset.researchDefault || id;
      activate(panels.some(panel => panel.id === id) ? id : fallback);
    };
    window.addEventListener('hashchange', syncSelection);
    window.addEventListener('popstate', syncSelection);
    for (const query of ['(max-width: 1200px)', '(max-width: 760px)', '(max-width: 430px)']) {
      matchMedia(query).addEventListener('change', () => position(cards.find(card => card.classList.contains('is-selected'))));
    }
    syncSelection();
  });

  const normalize = text => text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  document.querySelectorAll('[data-catalog]').forEach(catalog => {
    const items = [...catalog.querySelectorAll('[data-item]')];
    const buttons = [...catalog.querySelectorAll('[data-filter]')];
    const search = catalog.querySelector('input[type="search"]');
    const count = catalog.querySelector('[data-count]');
    const empty = catalog.querySelector('[data-empty]');
    let filter = 'all';
    const update = () => {
      const query = normalize(search?.value.trim() || '');
      let visible = 0;
      for (const item of items) {
        const matches = (filter === 'all' || item.dataset.kind === filter) && normalize(item.dataset.search || item.textContent).includes(query);
        item.hidden = !matches;
        visible += Number(matches);
      }
      if (count) count.textContent = `${visible} ${count.dataset.label}`;
      if (empty) empty.hidden = visible !== 0;
    };
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        filter = button.dataset.filter;
        buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
        update();
      });
    });
    search?.addEventListener('input', update);
    catalog.querySelector('[data-reset]')?.addEventListener('click', () => {
      filter = 'all';
      if (search) search.value = '';
      buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === 'all')));
      update();
      search?.focus();
    });
    catalog.querySelectorAll('[data-enhance]').forEach(el => { el.hidden = false; });
    update();
  });

  document.querySelectorAll('[data-output-tabs]').forEach(section => {
    const tabs = [...section.querySelectorAll('[data-output-tab]')];
    const panels = [...section.querySelectorAll('[data-output-panel]')];
    const pubTabs = [...section.querySelectorAll('[data-publication-view]')];
    const pubViews = [...section.querySelectorAll('[data-publication-panel]')];
    const search = section.querySelector('[data-output-search]');
    const count = section.querySelector('[data-output-count]');
    const normalize = text => text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    const activate = id => {
      const tab = tabs.find(button => button.dataset.outputTab === id);
      if (!tab) return;
      tabs.forEach(button => {
        const selected = button === tab;
        button.setAttribute('aria-selected', String(selected));
        button.tabIndex = selected ? 0 : -1;
      });
      panels.forEach(panel => { panel.hidden = panel.id !== tab.getAttribute('aria-controls'); });
    };

    tabs.forEach((button, index) => {
      button.addEventListener('click', () => activate(button.dataset.outputTab));
      button.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
          : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
        tabs[next].focus();
        activate(tabs[next].dataset.outputTab);
      });
    });

    const updatePublications = () => {
      const query = normalize(search?.value.trim() || '');
      for (const item of section.querySelectorAll('[data-output-item]')) {
        item.hidden = !normalize(item.dataset.search || item.textContent).includes(query);
      }
      for (const group of section.querySelectorAll('[data-output-group]')) {
        group.hidden = !group.querySelector('[data-output-item]:not([hidden])');
      }
      const activeView = pubViews.find(view => !view.hidden);
      const visibleCount = activeView?.querySelectorAll('[data-output-item]:not([hidden])').length || 0;
      if (count) count.textContent = `${visibleCount} ${count.dataset.suffix || ''}`.trim();
    };

    pubTabs.forEach((button, index) => {
      button.addEventListener('click', () => {
        pubTabs.forEach(tab => {
          const selected = tab === button;
          tab.setAttribute('aria-selected', String(selected));
          tab.tabIndex = selected ? 0 : -1;
        });
        pubViews.forEach(view => { view.hidden = view.id !== button.getAttribute('aria-controls'); });
        updatePublications();
      });
      button.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        const next = (index + (event.key === 'ArrowRight' ? 1 : -1) + pubTabs.length) % pubTabs.length;
        pubTabs[next].focus();
        pubTabs[next].click();
      });
    });
    search?.addEventListener('input', updatePublications);
    updatePublications();

    const syncHash = () => {
      const id = location.hash.slice(1);
      if (tabs.some(button => button.dataset.outputTab === id)) activate(id);
    };
    nav?.querySelectorAll('a[href*="#"]').forEach(link => {
      const destination = new URL(link.href);
      const id = destination.hash.slice(1);
      if (destination.pathname !== location.pathname || !tabs.some(button => button.dataset.outputTab === id)) return;
      link.addEventListener('click', () => activate(id));
    });
    window.addEventListener('hashchange', syncHash);
    syncHash();
  });
})();
