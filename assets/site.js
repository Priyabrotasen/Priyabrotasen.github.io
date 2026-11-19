(function () {
  "use strict";
  var root = document.documentElement;

  /* ---- Theme: follows the system until the visitor chooses; the choice persists ---- */
  var themeBtn = document.getElementById("theme-toggle");
  function currentTheme() {
    var set = root.getAttribute("data-theme");
    if (set === "light" || set === "dark") return set;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function labelTheme() {
    if (themeBtn) themeBtn.setAttribute("aria-label", "Switch to " + (currentTheme() === "dark" ? "light" : "dark") + " theme");
  }
  if (themeBtn) {
    labelTheme();
    themeBtn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      labelTheme();
    });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      if (mq.addEventListener) mq.addEventListener("change", labelTheme);
    }
  }

  /* ---- Mobile navigation ---- */
  var navBtn = document.getElementById("nav-toggle");
  var nav = document.getElementById("site-nav");
  function setNav(open) {
    nav.classList.toggle("open", open);
    navBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (navBtn && nav) {
    navBtn.addEventListener("click", function () { setNav(!nav.classList.contains("open")); });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && nav.classList.contains("open")) { setNav(false); navBtn.focus(); }
    });
    document.addEventListener("click", function (ev) {
      if (nav.classList.contains("open") && !nav.contains(ev.target) && !navBtn.contains(ev.target)) setNav(false);
    });
  }

  /* ---- Copy buttons (BibTeX, short bio) ---- */
  function copyText(text) {
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
    copyText(btn.getAttribute("data-copy")).then(function () {
      label.textContent = "Copied"; btn.classList.add("done");
    }, function () {
      label.textContent = "Press Ctrl+C";
    }).then(function () {
      setTimeout(function () { label.textContent = original; btn.classList.remove("done"); }, 1800);
    });
  });

  /* ---- Pressed-state helper for a group of filter buttons ---- */
  function press(group, value) {
    Array.prototype.forEach.call(group.querySelectorAll(".chip-btn"), function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-value") === value ? "true" : "false");
    });
  }

  /* ---- Publication filters ---- */
  var pubFilters = document.getElementById("pub-filters");
  if (pubFilters) {
    var state = { year: "", type: "", status: "" };
    var pubs = document.querySelectorAll("#pub-groups .pub");
    var groups = document.querySelectorAll("[data-year-group]");
    var countEl = document.getElementById("pub-count");
    var emptyEl = document.getElementById("pub-empty");
    var apply = function () {
      var shown = 0;
      Array.prototype.forEach.call(pubs, function (p) {
        var ok = (!state.year || p.getAttribute("data-year") === state.year) &&
                 (!state.type || p.getAttribute("data-type") === state.type) &&
                 (!state.status || p.getAttribute("data-status") === state.status);
        p.hidden = !ok;
        if (ok) shown++;
      });
      Array.prototype.forEach.call(groups, function (g) {
        g.hidden = !g.querySelector(".pub:not([hidden])");
      });
      countEl.textContent = "Showing " + shown + " of " + pubs.length;
      emptyEl.hidden = shown !== 0;
    };
    pubFilters.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".chip-btn");
      if (!btn) return;
      var group = btn.closest("[data-filter]");
      state[group.getAttribute("data-filter")] = btn.getAttribute("data-value");
      press(group, btn.getAttribute("data-value"));
      apply();
    });
    document.getElementById("pub-reset").addEventListener("click", function () {
      state = { year: "", type: "", status: "" };
      Array.prototype.forEach.call(pubFilters.querySelectorAll("[data-filter]"), function (g) { press(g, ""); });
      apply();
    });
  }

  /* ---- Project category filter ---- */
  var projFilter = document.getElementById("project-filter");
  if (projFilter) {
    projFilter.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".chip-btn");
      if (!btn) return;
      var value = btn.getAttribute("data-value");
      press(projFilter, value);
      Array.prototype.forEach.call(document.querySelectorAll("[data-category-group]"), function (g) {
        g.hidden = !!value && g.getAttribute("data-category-group") !== value;
      });
    });
  }
})();
