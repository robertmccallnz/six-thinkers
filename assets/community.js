/* Kiwi Dialectic community layer
   - Loads Cactus Comments (federated Matrix, LGPLv3) into #kd-comments
   - Derives commentSectionId from the current URL path so every page has its own thread
   - Privacy-first: no IP logging by this site; Cactus uses Matrix (guest posting enabled)
   - Prefers reduced motion; graceful fallback if Cactus fails to load
*/
(function () {
  var CACTUS_CSS = "https://latest.cactus.chat/style.css";
  var CACTUS_JS  = "https://latest.cactus.chat/cactus.js";
  var SITE_NAME  = "kiwidialectic"; // Matrix-registered via @bot.cactusbot:cactus.chat
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

    var sectionId = slugFromPath();
    // Show a loading hint while Cactus fetches
    mount.innerHTML = '<div class="kc-loading">Loading kōrero…</div>';

    Promise.all([loadCSS(CACTUS_CSS), loadJS(CACTUS_JS)]).then(function () {
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
