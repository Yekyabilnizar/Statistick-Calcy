/* belajar.js – penanda selesai, progres, lencana, dan kartu belajar bertab (disimpan di peramban) */
(function () {
  var KEY = 'statcalc-selesai';
  function load() { try { var v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; } }
  function save(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
  var done = load();

  /* ---------- halaman jalur belajar ---------- */
  var idx = document.getElementById('learn');
  if (idx) {
    var order = JSON.parse(idx.getAttribute('data-order')), n = 0, firstTodo = null;
    var perT = {1: [0, 0], 2: [0, 0], 3: [0, 0]};
    document.querySelectorAll('.mod-row').forEach(function (r) {
      var s = r.getAttribute('data-slug'), t = r.getAttribute('data-t'), ok = done.indexOf(s) >= 0;
      r.classList.toggle('done', ok); r.querySelector('.mod-ck').textContent = ok ? '✓' : '○';
      if (perT[t]) { perT[t][1]++; if (ok) perT[t][0]++; }
      if (ok) n++;
    });
    for (var i = 0; i < order.length; i++) { if (done.indexOf(order[i]) < 0) { firstTodo = order[i]; break; } }
    var total = order.length, pct = total ? Math.round(100 * n / total) : 0;
    document.getElementById('lp-text').textContent = window.LANG === 'en' ? n + ' of ' + total + ' modules completed (' + pct + '%)' : n + ' dari ' + total + ' modul selesai (' + pct + '%)';
    document.getElementById('lp-bar').style.width = pct + '%';
    var E = window.LANG === 'en';
    var msg = E ? (n === 0 ? 'Start with the first module. Each takes about 5 minutes.' : n === total ? 'Great, all modules done! Keep practising in the calculators.' : pct >= 50 ? 'Over halfway there. Keep going!' : 'Nice, continue with the next module.') : (n === 0 ? 'Mulai dari modul pertama. Setiap modul hanya sekitar 5 menit.' : n === total ? 'Luar biasa, semua modul selesai! Lanjutkan berlatih di kalkulator.' : pct >= 50 ? 'Sudah lebih dari separuh jalan. Terus lanjut!' : 'Bagus, teruskan modul berikutnya.');
    document.getElementById('lp-msg').textContent = msg;
    var nx = document.getElementById('lp-next');
    if (firstTodo) { nx.href = (window.LP || '') + '/belajar/' + firstTodo; nx.textContent = E ? (n ? '▶ Continue learning' : '▶ Start learning') : (n ? '▶ Lanjutkan belajar' : '▶ Mulai belajar'); }
    else { nx.textContent = E ? '🏆 Open calculators' : '🏆 Buka kalkulator'; nx.href = (window.LP || '') + '/rancangan-percobaan'; }
    document.querySelectorAll('.stage-card').forEach(function (c) {
      var t = c.getAttribute('data-t'), a = perT[t] || [0, 0], p = a[1] ? Math.round(100 * a[0] / a[1]) : 0;
      c.querySelector('.ring').style.setProperty('--p', p); c.querySelector('.ring span').textContent = p + '%';
      c.querySelector('.stage-count').textContent = window.LANG === 'en' ? a[0] + ' of ' + a[1] + ' modules completed' : a[0] + ' dari ' + a[1] + ' modul selesai';
    });
    var on = {first: n >= 1, t1: perT[1][1] && perT[1][0] === perT[1][1], half: pct >= 50, t2: perT[2][1] && perT[2][0] === perT[2][1], t3: perT[3][1] && perT[3][0] === perT[3][1], all: n === total};
    document.querySelectorAll('.badge').forEach(function (b) { b.classList.toggle('on', !!on[b.getAttribute('data-b')]); });
  }

  /* ---------- halaman modul ---------- */
  var wrap = document.getElementById('lc-wrap');
  if (wrap) {
    var cards = Array.prototype.slice.call(wrap.querySelectorAll('.lc')), nav = document.getElementById('lc-nav'), fill = document.querySelector('#lc-steps i');
    var cur = 0, seen = {}, showAll = false, btns = [];
    cards.forEach(function (c, i) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = c.getAttribute('data-label'); b.addEventListener('click', function () { go(i); });
      nav.appendChild(b); btns.push(b);
      if (i < cards.length - 1) {
        var d = document.createElement('div'); d.className = 'lc-next';
        var nb = document.createElement('button'); nb.type = 'button'; nb.textContent = 'Lanjut: ' + cards[i + 1].getAttribute('data-label').replace(/^\S+\s/, '') + ' →';
        nb.addEventListener('click', function () { go(i + 1); window.scrollTo({top: wrap.offsetTop - 20, behavior: 'smooth'}); });
        d.appendChild(nb); c.appendChild(d);
      }
    });
    var all = document.createElement('button'); all.type = 'button'; all.className = 'all'; all.textContent = (window.LANG === 'en' ? '☰ Show all' : '☰ Tampilkan semua');
    all.addEventListener('click', function () { showAll = !showAll; wrap.classList.toggle('tabbed', !showAll); all.textContent = window.LANG === 'en' ? (showAll ? '▤ Show by section' : '☰ Show all') : (showAll ? '▤ Tampilkan per bagian' : '☰ Tampilkan semua'); });
    nav.appendChild(all);
    function go(i) {
      cur = Math.max(0, Math.min(cards.length - 1, i)); seen[cur] = 1;
      cards.forEach(function (c, k) { c.classList.toggle('on', k === cur); btns[k].classList.toggle('on', k === cur); btns[k].classList.toggle('seen', !!seen[k]); });
      fill.style.width = (100 * (cur + 1) / cards.length) + '%';
      try { history.replaceState(null, '', '#' + (cur + 1)); } catch (e) {}
    }
    wrap.classList.add('tabbed');
    var h = parseInt((location.hash || '').slice(1), 10); go(h >= 1 && h <= cards.length ? h - 1 : 0);
    document.addEventListener('keydown', function (e) {
      if (e.target.matches && e.target.matches('input,textarea,select')) return;
      if (e.key === 'ArrowRight') go(cur + 1); else if (e.key === 'ArrowLeft') go(cur - 1);
    });
  }

  /* ---------- rumus (KaTeX dihosting sendiri, dimuat hanya bila ada) ---------- */
  if (document.querySelector('.math')) {
    var base = '/static/katex/', v = (document.querySelector('script[src*="belajar.js"]') || {}).src || '';
    v = (v.split('?v=')[1] || '1');
    var css = document.createElement('link'); css.rel = 'stylesheet'; css.href = base + 'katex.min.css?v=' + v; document.head.appendChild(css);
    function ld(src, cb) { var s = document.createElement('script'); s.src = base + src + '?v=' + v; s.onload = cb; document.head.appendChild(s); }
    ld('katex.min.js', function () { ld('auto-render.min.js', function () {
      var root = document.getElementById('lc-wrap');
      try { renderMathInElement(root, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '\\(', right: '\\)', display: false}], throwOnError: false}); root.classList.add('math-ok'); } catch (e) {}
    }); });
  }

  /* ---------- tombol selesai ---------- */
  var btn = document.getElementById('mod-done');
  if (btn) {
    var slug = btn.getAttribute('data-slug'), st = document.getElementById('mod-state');
    function paint() {
      var ok = done.indexOf(slug) >= 0;
      btn.textContent = window.LANG === 'en' ? (ok ? '✓ Done (click to undo)' : '✓ Mark as done') : (ok ? '✓ Selesai (klik untuk batalkan)' : '✓ Tandai selesai');
      btn.classList.toggle('pri', ok); btn.classList.toggle('sec', !ok);
      if (st) st.textContent = ok ? (window.LANG === 'en' ? '✓ Completed' : '✓ Sudah selesai') : '';
    }
    btn.addEventListener('click', function (e) {
      done = load();
      var i = done.indexOf(slug);
      if (i >= 0) done.splice(i, 1); else { done.push(slug); if (window.confetti) confetti(e.clientX, e.clientY); if (window.toast) toast(window.LANG === 'en' ? '🎉 Module completed! Total ' + done.length + ' modules.' : '🎉 Modul selesai! Total ' + done.length + ' modul.'); }
      save(done); paint();
    });
    paint();
  }
})();
