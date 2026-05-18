/*!
 * tax-acronyms.js — Drop-in tooltip helper for TaxPreparerTools.com
 *
 * Loads /assets/data/acronyms.json and provides:
 *   - Programmatic lookup API: TaxAcronyms.lookup('QBI'), .all(), .byCategory()
 *   - Optional auto-tooltip on hover/focus: TaxAcronyms.init()
 *
 * Quickest integration on any page:
 *   <script src="/assets/js/tax-acronyms.js"></script>
 *   <script>TaxAcronyms.init();</script>
 *
 * Matches only purely alphabetic acronyms (AGI, QBI, SSTB, MeF, etc.).
 * Numeric/symbol entries (1031, §179, 401(k)) are excluded from auto-tooltip
 * scanning but remain available via .lookup() and the full /acronyms page.
 *
 * Case-sensitive: only wraps text that matches an acronym's exact canonical case.
 * Only wraps the FIRST occurrence per text node to avoid visual noise.
 */
(function (global) {
  'use strict';

  let data = null;
  let lookup = {};            // 'AGI' → entry
  const lookupById = {};      // 'agi' → entry

  function buildLookups(entries) {
    lookup = {};
    entries.forEach(function (e) {
      lookupById[e.id] = e;
      // Only alphabetic acronyms participate in auto-tooltip matching
      if (/^[A-Za-z]+$/.test(e.acronym)) {
        const key = e.acronym.toUpperCase();
        if (!lookup[key]) lookup[key] = e;  // first occurrence wins on duplicates (LLC)
      }
    });
  }

  function escapeRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  async function loadFrom(url) {
    if (data) return data;
    const res = await fetch(url);
    if (!res.ok) throw new Error('tax-acronyms: failed to load ' + url);
    const payload = await res.json();
    data = payload.acronyms || payload;
    buildLookups(data);
    return data;
  }

  // ─────────────────────────────────────────────────────────────────────
  // Tooltip popover (injected once on init)
  // ─────────────────────────────────────────────────────────────────────
  let popover = null;
  let activeTarget = null;
  let baseUrlForLinks = '/acronyms';

  function injectStyles() {
    if (document.getElementById('tax-acronyms-styles')) return;
    const style = document.createElement('style');
    style.id = 'tax-acronyms-styles';
    style.textContent = [
      '.tax-acronym{border-bottom:1px dotted rgba(200,168,75,.5);cursor:help;color:inherit;}',
      '.tax-acronym:hover,.tax-acronym:focus{border-bottom-color:#c8a84b;outline:none;}',
      '.tax-acronym-popover{position:absolute;z-index:9999;background:#0f1f3d;border:1px solid rgba(200,168,75,.3);border-radius:10px;padding:14px 16px;max-width:320px;font-family:"DM Sans",sans-serif;color:#dde4f0;box-shadow:0 10px 30px rgba(0,0,0,.4);opacity:0;transform:translateY(-4px);transition:opacity .15s,transform .15s;}',
      '.tax-acronym-popover.show{opacity:1;transform:translateY(0);}',
      '.tap-acronym{font-family:"DM Mono",monospace;font-size:.9rem;font-weight:700;color:#c8a84b;}',
      '.tap-fullname{font-family:"Playfair Display",serif;font-size:.95rem;font-weight:600;color:#fff;margin-top:2px;margin-bottom:8px;}',
      '.tap-short{font-size:.8rem;line-height:1.55;color:#dde4f0;}',
      '.tap-link{display:inline-block;margin-top:10px;font-size:.74rem;color:#c8a84b;text-decoration:none;font-weight:600;}',
      '.tap-link:hover{text-decoration:underline;}',
    ].join('\n');
    document.head.appendChild(style);
  }

  function ensurePopover() {
    if (popover) return;
    injectStyles();
    popover = document.createElement('div');
    popover.className = 'tax-acronym-popover';
    popover.style.display = 'none';
    // Don't trigger hide when the user moves into the popover itself
    popover.addEventListener('mouseenter', function () { activeTarget = popover; });
    popover.addEventListener('mouseleave', hidePopover);
    document.body.appendChild(popover);
  }

  function showPopover(target) {
    const acronym = target.dataset.acronym;
    const entry = lookup[acronym];
    if (!entry) return;
    ensurePopover();

    popover.innerHTML =
      '<div class="tap-acronym">' + entry.acronym + '</div>' +
      '<div class="tap-fullname">' + entry.fullName + '</div>' +
      '<div class="tap-short">' + entry.shortDef + '</div>' +
      '<a class="tap-link" href="' + baseUrlForLinks + '#acro-' + entry.id + '">Read full entry →</a>';
    popover.style.display = 'block';

    // Position above target, or below if no room
    const rect = target.getBoundingClientRect();
    const ph = popover.offsetHeight;
    const pw = popover.offsetWidth;
    const sy = window.scrollY;
    const sx = window.scrollX;
    let top = rect.top + sy - ph - 8;
    if (top < sy + 10) top = rect.bottom + sy + 8;
    let left = rect.left + sx + rect.width / 2 - pw / 2;
    const vw = window.innerWidth;
    if (left < 10) left = 10;
    if (left + pw > vw - 10) left = vw - pw - 10;
    popover.style.top = top + 'px';
    popover.style.left = left + 'px';

    requestAnimationFrame(function () { popover.classList.add('show'); });
    activeTarget = target;
  }

  function hidePopover() {
    if (!popover) return;
    popover.classList.remove('show');
    setTimeout(function () {
      if (popover && !popover.classList.contains('show')) {
        popover.style.display = 'none';
      }
    }, 150);
    activeTarget = null;
  }

  function attachListeners() {
    document.addEventListener('mouseover', function (e) {
      const t = e.target.closest && e.target.closest('.tax-acronym');
      if (t && t !== activeTarget) showPopover(t);
    });
    document.addEventListener('mouseout', function (e) {
      const t = e.target.closest && e.target.closest('.tax-acronym');
      const r = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('.tax-acronym, .tax-acronym-popover');
      if (t && !r) hidePopover();
    });
    document.addEventListener('focusin', function (e) {
      const t = e.target.closest && e.target.closest('.tax-acronym');
      if (t) showPopover(t);
    });
    document.addEventListener('focusout', function (e) {
      const t = e.target.closest && e.target.closest('.tax-acronym');
      if (t) hidePopover();
    });
    document.addEventListener('click', function (e) {
      // Tap-elsewhere to dismiss on touch devices
      if (!e.target.closest('.tax-acronym, .tax-acronym-popover')) hidePopover();
    });
  }

  // ─────────────────────────────────────────────────────────────────────
  // Text scanning / wrapping
  // ─────────────────────────────────────────────────────────────────────
  function scanAndWrap(opts) {
    const acronymsToMatch = opts.onlyAcronyms
      ? opts.onlyAcronyms.map(function (a) { return a.toUpperCase(); }).filter(function (a) { return lookup[a]; })
      : Object.keys(lookup);
    if (acronymsToMatch.length === 0) return;

    // Build a regex with case-sensitive matching, longer acronyms first
    // (so "SSTB" matches before any shorter prefix). Word boundaries on both sides.
    // Note: we match against each entry's canonical case (since lookup keys are
    // upper-cased, but entry.acronym preserves original case like "MeF").
    const variants = [];
    for (const key in lookup) {
      variants.push(lookup[key].acronym);  // exact original casing
    }
    variants.sort(function (a, b) { return b.length - a.length; });
    const pattern = new RegExp('\\b(?:' + variants.map(escapeRegex).join('|') + ')\\b', 'g');

    const excludeSelector = opts.exclude;
    function shouldSkip(node) {
      let el = node.parentElement;
      while (el) {
        if (el.matches && el.matches(excludeSelector)) return true;
        el = el.parentElement;
      }
      return false;
    }

    function wrapTextNode(textNode) {
      const text = textNode.nodeValue;
      pattern.lastIndex = 0;
      if (!pattern.test(text)) return;
      pattern.lastIndex = 0;

      const fragment = document.createDocumentFragment();
      const seen = new Set();
      let lastIndex = 0;
      let match;
      let wrapped = false;

      while ((match = pattern.exec(text)) !== null) {
        const captured = match[0];
        const key = captured.toUpperCase();
        if (seen.has(key)) continue;  // first occurrence per node
        seen.add(key);

        if (match.index > lastIndex) {
          fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
        }
        const span = document.createElement('span');
        span.className = 'tax-acronym';
        span.dataset.acronym = key;
        span.tabIndex = 0;
        span.setAttribute('role', 'button');
        span.setAttribute('aria-label', captured + ' — tax acronym, hover for definition');
        span.textContent = captured;
        fragment.appendChild(span);
        lastIndex = match.index + captured.length;
        wrapped = true;
      }
      if (wrapped) {
        if (lastIndex < text.length) {
          fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
        }
        textNode.parentNode.replaceChild(fragment, textNode);
      }
    }

    const containers = document.querySelectorAll(opts.scanSelector);
    containers.forEach(function (container) {
      const walker = document.createTreeWalker(
        container,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: function (node) {
            if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
            if (shouldSkip(node)) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
          }
        }
      );
      const nodes = [];
      let n;
      while ((n = walker.nextNode())) nodes.push(n);
      nodes.forEach(wrapTextNode);
    });
  }

  // ─────────────────────────────────────────────────────────────────────
  // Public API
  // ─────────────────────────────────────────────────────────────────────
  const API = {
    /** Provide data inline (skips fetch). Accepts the .acronyms array. */
    setData: function (entries) {
      data = entries;
      buildLookups(entries);
    },

    /** Look up an acronym (case-insensitive). Returns entry or null. */
    lookup: function (acronym) {
      if (!acronym) return null;
      return lookup[acronym.toUpperCase()] || null;
    },

    /** Look up by id (e.g. 'qbi'). Returns entry or null. */
    byId: function (id) {
      return lookupById[id] || null;
    },

    /** All entries (including numeric/symbol ones). */
    all: function () { return data || []; },

    /** Entries filtered by category. */
    byCategory: function (cat) {
      return (data || []).filter(function (e) { return e.category === cat; });
    },

    /**
     * Scan the page and add tooltip behavior.
     * Options:
     *   scanSelector  — where to scan (default: 'main, article, .pw')
     *   exclude       — elements to skip
     *   baseUrl       — prefix for "Read full entry" links (default: '/acronyms')
     *   dataUrl       — JSON location (default: '/assets/data/acronyms.json')
     *   onlyAcronyms  — optional whitelist array (e.g. ['QBI','SSTB','UBIA'])
     */
    init: async function (opts) {
      opts = Object.assign({
        scanSelector: 'main, article, .pw',
        exclude: 'a, code, pre, input, textarea, .tax-acronym, .no-tooltip, .ac-card, h1, h2, nav, footer, .nav-links',
        baseUrl: '/acronyms',
        dataUrl: '/assets/data/acronyms.json',
        onlyAcronyms: null,
      }, opts || {});

      baseUrlForLinks = opts.baseUrl;

      if (!data) {
        try {
          await loadFrom(opts.dataUrl);
        } catch (err) {
          console.warn('[tax-acronyms]', err.message);
          return;
        }
      }

      // Wait for DOM ready if needed
      if (document.readyState === 'loading') {
        await new Promise(function (resolve) {
          document.addEventListener('DOMContentLoaded', resolve);
        });
      }

      scanAndWrap(opts);
      ensurePopover();
      attachListeners();
    },
  };

  global.TaxAcronyms = API;
})(window);
