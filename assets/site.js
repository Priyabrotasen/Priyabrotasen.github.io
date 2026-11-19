/* Site behaviour. Each feature is a small self-contained function that does
   nothing if its elements are not on the page; add a new one and call it at the bottom. */
(function () {
  "use strict";
  var root = document.documentElement;
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }

  /* Theme: follows the system until the visitor chooses; the choice is remembered. */
  function initTheme() {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    function current() {
      var set = root.getAttribute("data-theme");
      if (set === "light" || set === "dark") return set;
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    function label() { btn.setAttribute("aria-label", "Switch to " + (current() === "dark" ? "light" : "dark") + " theme"); }
    label();
    btn.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      label();
    });
  }

  /* Highlight the nav link of the section being read (homepage only). */
  function initScrollSpy() {
    var nav = document.getElementById("nav-links");
    if (!nav || document.body.getAttribute("data-page") !== "home" || !("IntersectionObserver" in window)) return;
    var links = {};
    each(nav.querySelectorAll("a"), function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var active = null;
    function activate(id) {
      if (id === active || !links[id]) return;
      if (active) links[active].removeAttribute("aria-current");
      active = id;
      links[id].setAttribute("aria-current", "true");
      var a = links[id];
      if (a.offsetLeft < nav.scrollLeft || a.offsetLeft + a.offsetWidth > nav.scrollLeft + nav.clientWidth) {
        nav.scrollLeft = a.offsetLeft - 16;
      }
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) activate(en.target.id); });
    }, { rootMargin: "-25% 0px -65% 0px" });
    each(document.querySelectorAll("main .section[id]"), function (s) { observer.observe(s); });
  }

  /* Copy buttons: any element with data-copy="text". */
  function initCopy() {
    function copy(text) {
      if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
      return new Promise(function (resolve, reject) {
        var ta = document.createElement("textarea");
        ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); }
        document.body.removeChild(ta);
      });
    }
    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest ? ev.target.closest("[data-copy]") : null;
      if (!btn) return;
      var label = btn.querySelector("span");
      var original = label.textContent;
      copy(btn.getAttribute("data-copy")).then(function () {
        label.textContent = "Copied"; btn.classList.add("done");
      }, function () {
        label.textContent = "Press Ctrl+C";
      }).then(function () {
        setTimeout(function () { label.textContent = original; btn.classList.remove("done"); }, 1800);
      });
    });
  }

  /* Publication filters: each [data-filter="key"] group filters cards on data-key. */
  function initPublicationFilters() {
    var box = document.getElementById("pub-filters");
    if (!box) return;
    var cards = document.querySelectorAll("#pub-list .publication-item");
    var countEl = document.getElementById("pub-count");
    var emptyEl = document.getElementById("pub-empty");
    var state = {};
    function press(group, value) {
      each(group.querySelectorAll(".chip"), function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-value") === value ? "true" : "false");
      });
    }
    function apply() {
      var shown = 0;
      each(cards, function (c) {
        var ok = Object.keys(state).every(function (k) { return !state[k] || c.getAttribute("data-" + k) === state[k]; });
        c.hidden = !ok;
        if (ok) shown++;
      });
      countEl.textContent = "Showing " + shown + " of " + cards.length;
      emptyEl.hidden = shown !== 0;
    }
    box.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".chip");
      if (!btn) return;
      var group = btn.closest("[data-filter]");
      state[group.getAttribute("data-filter")] = btn.getAttribute("data-value");
      press(group, btn.getAttribute("data-value"));
      apply();
    });
    document.getElementById("pub-reset").addEventListener("click", function () {
      state = {};
      each(box.querySelectorAll("[data-filter]"), function (g) { press(g, ""); });
      apply();
    });
  }

  initTheme();
  initScrollSpy();
  initCopy();
  initPublicationFilters();
})();
