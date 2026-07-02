/* Kiwi Dialectic community layer
   - Loads Cactus Comments (federated Matrix, LGPLv3) into #kd-comments
   - Derives commentSectionId from the current URL path so every page has its own thread
   - Privacy-first: no IP logging by this site; Cactus uses Matrix (guest posting enabled)
   - Prefers reduced motion; graceful fallback if Cactus fails to load
*/
(function () {
  // The public CDN latest.cactus.chat has been unreliable — DNS often unresolved.
  // We self-host the compiled client next to this script, and fall back to the CDN
  // only if the local copy fails.
  // Derive the /assets/ base URL from the currentScript src so it works from any
  // depth in the site (root, subdir, sub-subdir).
  var thisScript = document.currentScript || (function(){
    var s = document.getElementsByTagName('script');
    return s[s.length-1];
  })();
  var ASSETS_BASE = thisScript && thisScript.src
    ? thisScript.src.replace(/community\.js(\?.*)?$/, '')
    : '/assets/';

  // NOTE (2 July 2026): the public Cactus service (matrix.cactus.chat) is down
  // — every Matrix client-server endpoint returns 404. Comments are disabled
  // pending a decision on hosting. We still render the section header + intro
  // + fallback message so the community placeholder stays visible.
  var CACTUS_ENABLED = false;

  var CACTUS_CSS = ASSETS_BASE + "cactus-style.css";
  var CACTUS_JS  = ASSETS_BASE + "cactus.js";
  var CACTUS_CSS_FALLBACK = "https://latest.cactus.chat/style.css";
  var CACTUS_JS_FALLBACK  = "https://latest.cactus.chat/cactus.js";
  var SITE_NAME  = "sixthinkers";
  var HOMESERVER = "https://matrix.cactus.chat:8448";
  var SERVER     = "cactus.chat";

  function slugFromPath() {
    var p = (window.location.pathname || "/").replace(/\/+$/, "");
    if (!p || p === "") return "home";
    // strip .html, drop leading slash, replace unsafe chars
    var s = p.replace(/^\/+/, "").replace(/\.html?$/i, "").replace(/[\/\s]+/g, "-");
    s = s.replace(/[^a-z0-9\-]/gi, "").toLowerCase();
    return s || "home";
  }

  function loadCSS(href) {
    return new Promise(function (resolve, reject) {
      var l = document.createElement("link");
      l.rel = "stylesheet"; l.href = href;
      l.onload = resolve; l.onerror = reject;
      document.head.appendChild(l);
    });
  }
  function loadJS(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src; s.async = true;
      s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function markBroken(root) {
    if (root) root.classList.add("is-broken");
  }

  function boot() {
    var root = document.querySelector(".kd-community");
    if (!root) return;
    var mount = root.querySelector("#kd-comments");
    if (!mount) return;

    if (!CACTUS_ENABLED) {
      // Show the graceful fallback — don't hammer a dead endpoint.
      // Rewrite the fallback text and the “Kōrero open” live badge so we
      // don't mislead visitors while the comment host is being sorted.
      var fb = root.querySelector('.kc-fallback');
      if (fb) {
        fb.innerHTML = 'On-page kōrero is offline while we sort a comment host. In the meantime, jump into the conversation on <a href="https://kiwidialectic.substack.com" target="_blank" rel="noopener">Substack</a> or on <a href="https://facebook.com/kiwidialectic" target="_blank" rel="noopener">Facebook</a>.';
      }
      var live = root.querySelector('.kc-live');
      if (live) {
        var label = live.querySelector('span:last-child');
        if (label) label.textContent = 'Kōrero soon';
      }
      markBroken(root);
      return;
    }

    var sectionId = slugFromPath();
    mount.innerHTML = '<div class="kc-loading">Loading kōrero…</div>';

    // Try local first, then CDN fallback
    function loadAssets() {
      return Promise.all([loadCSS(CACTUS_CSS), loadJS(CACTUS_JS)])
        .catch(function () {
          return Promise.all([loadCSS(CACTUS_CSS_FALLBACK), loadJS(CACTUS_JS_FALLBACK)]);
        });
    }

    loadAssets().then(function () {
      if (typeof window.initComments !== "function") {
        markBroken(root); return;
      }
      // Clear loader
      mount.innerHTML = "";
      try {
        window.initComments({
          node: mount,
          defaultHomeserverUrl: HOMESERVER,
          serverName: SERVER,
          siteName: SITE_NAME,
          commentSectionId: sectionId,
          guestPostingEnabled: true,
          loginEnabled: true,
          updateInterval: 30
        });
      } catch (e) {
        markBroken(root);
      }
    }).catch(function () {
      markBroken(root);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
