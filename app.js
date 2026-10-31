(function () {
  var DATA_BASE = window.DATA_BASE || "";
  var CONFIG = window.PAPER_SHARING_CONFIG || {};
  var SHEET_APPEND = CONFIG.SHEET_APPEND_URL || "";
  var MY_SHEET = CONFIG.MY_SHEET_LINK || "#";

  var sheetLinkEl = document.querySelector(".sheet-link");
  if (sheetLinkEl) sheetLinkEl.href = MY_SHEET;

  var tabs = document.querySelectorAll(".tabs button");
  var panels = document.querySelectorAll(".tab-panel");

  function switchTab(id) {
    tabs.forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-tab") === id);
    });
    panels.forEach(function (p) {
      p.classList.toggle("active", p.id === id);
    });
  }

  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      switchTab(btn.getAttribute("data-tab"));
    });
  });

  function loadJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(r.statusText);
      return r.json();
    });
  }

  function renderPaper(paper, showAbstract) {
    var abstract = paper.abstract || "";
    var hasAbstract = abstract.length > 0;
    var abstractClass = hasAbstract && !showAbstract ? "paper-abstract collapsed" : "paper-abstract";
    var html = '<div class="paper-card">';
    html += '<h3><a href="' + escapeHtml(paper.link) + '" target="_blank" rel="noopener">' + escapeHtml(paper.title) + '</a></h3>';
    if (paper.authors) {
      html += '<div class="paper-meta">' + escapeHtml(paper.authors) + '</div>';
    }
    if (abstract) {
      html += '<div class="' + abstractClass + '" data-full="' + (showAbstract ? "0" : "1") + '">' + escapeHtml(abstract) + '</div>';
    }
    html += '<div class="paper-actions">';
    html += '<a class="btn btn-outline" href="' + escapeHtml(paper.link) + '" target="_blank" rel="noopener">打开全文</a>';
    if (SHEET_APPEND && SHEET_APPEND !== "YOUR_APPS_SCRIPT_WEB_APP_URL") {
      var addUrl = SHEET_APPEND + "?title=" + encodeURIComponent(paper.title) + "&authors=" + encodeURIComponent(paper.authors || "") + "&paper_link=" + encodeURIComponent(paper.link || "");
      html += '<a class="btn btn-primary" href="' + addUrl + '" target="_blank" rel="noopener">加入我的列表</a>';
    }
    html += "</div></div>";
    return html;
  }

  function escapeHtml(s) {
    if (!s) return "";
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function renderPanel(panel, data) {
    var source = panel.getAttribute("data-source");
    if (!data || !data.papers) {
      panel.innerHTML = '<p class="error">暂无数据，请先运行 scripts/fetch_all.py 生成 ' + source + '</p>';
      panel.classList.remove("loading");
      return;
    }
    var updated = data.updated ? '<p class="updated">更新于 ' + escapeHtml(data.updated) + '</p>' : "";
    panel.innerHTML = updated + data.papers.map(function (p) { return renderPaper(p, false); }).join("");
    panel.classList.remove("loading");
    panel.querySelectorAll(".paper-abstract[data-full='1']").forEach(function (el) {
      el.addEventListener("click", function () {
        el.classList.remove("collapsed");
        el.removeAttribute("data-full");
      });
    });
  }

  function loadPanel(panel) {
    var source = panel.getAttribute("data-source");
    if (!source) return;
    var url = DATA_BASE + "data/" + source;
    panel.classList.add("loading");
    loadJSON(url)
      .then(function (data) { renderPanel(panel, data); })
      .catch(function (err) {
        panel.classList.remove("loading");
        panel.innerHTML = '<p class="error">加载失败: ' + escapeHtml(err.message) + '（请确保已运行 fetch_all.py 并在此目录或上级提供 data/）</p>';
      });
  }

  panels.forEach(loadPanel);
})();
