/* Keep page positions separate without replaying entrances on widget updates. */
function createPageMemory() {
  const positions = new Map();
  let active = null, pending = null, restoring = false;
  return {
    begin(page, top) {
      if (pending === page) return false;
      if (page === active && pending === null) return false;
      if (active && pending === null && !restoring) positions.set(active, top);
      pending = page;
      return true;
    },
    enter(page) {
      if (active === page && pending === null) return null;
      active = page;
      pending = null;
      restoring = true;
      return positions.get(page) ?? 0;
    },
    remember(top) {
      if (active && pending === null && !restoring) positions.set(active, top);
    },
    restored() { restoring = false; },
    get active() { return active; },
  };
}

function entranceFor(page, trigger) {
  if (trigger === 'navigate' && ['cohort', 'clinical-docs', 'architecture'].includes(page)) return null;
  return page === 'heart-explorer' ? 'heart' : 'arterio';
}

if (typeof module !== 'undefined') module.exports = {createPageMemory, entranceFor};

function installPageNavigation(config, openingCSS) {
  const host = document, scope = window;
  const styleId = 'arterio-opening-style';
  let style = host.getElementById(styleId);
  if (!style) {
    style = host.createElement('style');
    style.id = styleId;
    host.head.appendChild(style);
  }
  style.textContent = openingCSS;

  function createRuntime() {
    const memory = createPageMemory();
    const reduced = scope.matchMedia('(prefers-reduced-motion: reduce)');
    let scroll = null, overlay = null, openingTimer = null, restoreTimer = null;
    let resize = null, restoreFrame = null, startedPage = null;
    const pages = config.pages;
    // A fresh document replays its entrance, including browser refreshes.
    scope.history.scrollRestoration = 'manual';

    function positionOpening() {
      if (!overlay) return;
      if (!overlay.classList.contains('arterio-opening--heart')) {
        overlay.style.top = '0px';
        return;
      }
      const navigation = host.querySelector('.st-key-site_navigation');
      const bounds = navigation ? [navigation, ...navigation.querySelectorAll('[data-testid="stRadio"]')] : [];
      const bottom = Math.max(0, ...bounds.map(node => node.getBoundingClientRect().bottom));
      overlay.style.top = `${Math.min(bottom + 16, scope.innerHeight * .45)}px`;
    }

    function finishOpening() {
      scope.clearTimeout(openingTimer);
      overlay?.remove();
      overlay = null;
    }

    function playOpening(page, trigger = 'load') {
      finishOpening();
      const entrance = entranceFor(page, trigger);
      if (!entrance || reduced.matches) return;
      const heart = entrance === 'heart';
      overlay = host.createElement('div');
      overlay.id = 'arterio-opening';
      overlay.className = `arterio-opening${heart ? ' arterio-opening--heart' : ''}`;
      overlay.setAttribute('role', 'status');
      overlay.setAttribute('aria-label', heart ? 'Heart Explorer opening' : 'ARTERIO opening');
      const symbol = heart
        ? '<path pathLength="1" d="M56 96 C48 89 13 64 13 36 C13 10 44 8 56 30 C68 8 99 10 99 36 C99 64 64 89 56 96 Z"/><path class="arterio-crossbar" pathLength="1" d="M24 53 H41 L49 39 L60 69 L69 53 H88"/>'
        : '<path pathLength="1" d="M15 103 L56 9 L97 103"/><path class="arterio-crossbar" pathLength="1" d="M26 76 H44 L51 64 L59 87 L67 76 H86"/>';
      overlay.innerHTML = `<div class="arterio-opening__identity"><svg class="arterio-opening__symbol" viewBox="0 0 112 112" aria-hidden="true">${symbol}</svg><div class="arterio-opening__word"><p class="arterio-opening__name">${heart ? 'Heart Explorer' : 'ARTERIO.'}</p><span class="arterio-opening__descriptor">${heart ? 'EXPLORE THE HUMAN HEART' : 'THE SCIENCE BEHIND THE PULSE'}</span></div></div>`;
      overlay.addEventListener('wheel', event => event.preventDefault(), {passive: false});
      overlay.addEventListener('touchmove', event => event.preventDefault(), {passive: false});
      host.body.appendChild(overlay);
      positionOpening();
      openingTimer = scope.setTimeout(finishOpening, 2800);
    }

    function stopRestoring() {
      scope.clearTimeout(restoreTimer);
      if (restoreFrame !== null) scope.cancelAnimationFrame(restoreFrame);
      restoreFrame = null;
      resize?.disconnect();
      resize = null;
      memory.restored();
    }

    function restorePosition(page, top) {
      scope.clearTimeout(restoreTimer);
      resize?.disconnect();
      if (restoreFrame !== null) scope.cancelAnimationFrame(restoreFrame);
      const root = host.querySelector(`.st-key-page_${page}`);
      function apply() {
        if (memory.active !== page || !root?.isConnected) return;
        scroll.scrollTo({top, left: 0, behavior: 'instant'});
        // Heart chapters and the architecture progress dot follow the host scroll.
        scroll.dispatchEvent(new scope.Event('scroll'));
      }
      apply();
      restoreFrame = scope.requestAnimationFrame(() => {
        apply();
        restoreFrame = scope.requestAnimationFrame(apply);
      });
      if (root) {
        resize = new scope.ResizeObserver(apply);
        resize.observe(root);
      }
      restoreTimer = scope.setTimeout(stopRestoring, 600);
    }

    function navigate(page) {
      if (!scroll || !memory.begin(page, scroll.scrollTop)) return;
      startedPage = page;
      playOpening(page, 'navigate');
    }

    // Capture before React replaces the outgoing view or clamps its scroll height.
    host.addEventListener('click', event => {
      if (event.target.closest('[data-replay-intro]')) {
        playOpening(memory.active || 'telemetry');
        return;
      }
      const option = event.target.closest('.st-key-site_navigation label[data-testid="stRadioOption"]');
      const page = option && pages[option.textContent.trim()];
      if (page) navigate(page);
    }, true);
    host.addEventListener('change', event => {
      if (event.target.closest('.st-key-site_navigation')) {
        const page = pages[event.target.value];
        if (page) navigate(page);
      }
    }, true);
    host.addEventListener('keydown', event => {
      if (event.key === 'Escape' && overlay) finishOpening();
    });
    scope.addEventListener('resize', positionOpening, {passive: true});
    reduced.addEventListener('change', () => { if (reduced.matches) finishOpening(); });

    return {
      enter(page) {
        const surface = host.querySelector('[data-testid="stMain"]');
        if (!surface) return;
        if (scroll !== surface) {
          scroll = surface;
          scroll.addEventListener('scroll', () => memory.remember(scroll.scrollTop), {passive: true});
        }
        const initial = memory.active === null;
        const top = memory.enter(page);
        if (top === null) return;
        restorePosition(page, top);
        if (startedPage !== page) playOpening(page, initial ? 'load' : 'navigate');
        startedPage = null;
      },
    };
  }

  // The runtime lives in the document, not sessionStorage: a reload starts afresh.
  scope.__arterioPages ??= createRuntime();
  scope.__arterioPages.enter(config.page);
}
