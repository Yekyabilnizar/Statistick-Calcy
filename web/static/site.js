/* site.js – pencarian metode di banner dan tab hasil (dipakai semua halaman) */
(function () {
  var idxEl = document.getElementById('search-index'), q = document.getElementById('q'), box = document.getElementById('sres');
  var items = [];
  try { items = JSON.parse(idxEl.textContent); } catch (e) {}
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  var act = -1;
  function search(text) {
    var toks = norm(text).split(/\s+/).filter(Boolean);
    if (!toks.length) return [];
    var res = [];
    items.forEach(function (it) {
      var title = norm(it.t), hay = norm(it.t + ' ' + it.k + ' ' + it.d), score = 0, ok = true;
      toks.forEach(function (t) {
        if (hay.indexOf(t) < 0) { ok = false; return; }
        score += title.indexOf(t) >= 0 ? 3 : 1;
        if (title.indexOf(t) === 0) score += 2;
      });
      if (ok) res.push([score, it]);
    });
    res.sort(function (a, b) { return b[0] - a[0]; });
    return res.slice(0, 8).map(function (r) { return r[1]; });
  }
  function show() {
    var r = search(q.value); act = -1;
    if (!q.value.trim()) { box.className = 'sres'; box.innerHTML = ''; return; }
    box.innerHTML = r.length ? r.map(function (it) { return '<a href="' + it.u + '"><b>' + esc(it.t) + '</b><small>' + esc(it.g) + '</small></a>'; }).join('')
      : '<div class="none">' + (window.LANG === 'en' ? 'No matching method. Try another word, e.g. “regression”, “factorial”, or “logistic”.' : 'Tidak ada metode yang cocok. Coba kata lain, mis. “regresi”, “faktorial”, atau “logistik”.') + '</div>';
    box.className = 'sres open';
  }
  if (q) {
    q.addEventListener('input', show);
    q.addEventListener('keydown', function (e) {
      var links = box.querySelectorAll('a');
      if (e.key === 'ArrowDown' && links.length) { act = (act + 1) % links.length; }
      else if (e.key === 'ArrowUp' && links.length) { act = (act - 1 + links.length) % links.length; }
      else if (e.key === 'Enter') { var t = links[act >= 0 ? act : 0]; if (t) { location.href = t.getAttribute('href'); } return; }
      else if (e.key === 'Escape') { box.className = 'sres'; return; }
      else return;
      e.preventDefault();
      links.forEach(function (a, i) { a.classList.toggle('act', i === act); });
    });
    document.addEventListener('click', function (e) { if (!document.getElementById('search').contains(e.target)) box.className = 'sres'; });
  }
  // tab hasil
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.tab-btn');
    if (!b) return;
    var tabs = b.closest('.tabs');
    tabs.querySelectorAll('.tab-btn').forEach(function (x) { x.classList.remove('on'); });
    tabs.querySelectorAll('.tab-panel').forEach(function (x) { x.classList.remove('on'); });
    b.classList.add('on');
    var p = document.getElementById(b.getAttribute('data-t'));
    if (p) { p.classList.add('on'); if (window.drawPlots) window.drawPlots(p); }
  });
})();
