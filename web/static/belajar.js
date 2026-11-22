/* belajar.js – penanda modul selesai (disimpan di peramban) dan ringkasan progres */
(function () {
  var KEY = 'statcalc-selesai';
  function load() { try { var v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; } }
  function save(a) { try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} }
  var done = load();

  var idx = document.getElementById('learn');
  if (idx) {
    var order = JSON.parse(idx.getAttribute('data-order')), n = 0, firstTodo = null;
    document.querySelectorAll('.mod-row').forEach(function (r) {
      var s = r.getAttribute('data-slug'), ok = done.indexOf(s) >= 0;
      r.classList.toggle('done', ok); r.querySelector('.mod-ck').textContent = ok ? '✓' : '○';
      if (ok) n++;
    });
    for (var i = 0; i < order.length; i++) { if (done.indexOf(order[i]) < 0) { firstTodo = order[i]; break; } }
    document.getElementById('lp-text').textContent = n + ' dari ' + order.length + ' modul selesai';
    document.getElementById('lp-bar').style.width = (order.length ? (100 * n / order.length) : 0) + '%';
    var nx = document.getElementById('lp-next');
    if (firstTodo) { nx.href = '/belajar/' + firstTodo; nx.textContent = n ? '▶ Lanjutkan belajar' : '▶ Mulai belajar'; }
    else { nx.textContent = '🎉 Semua modul selesai'; nx.href = '/rancangan-percobaan'; }
  }

  var btn = document.getElementById('mod-done');
  if (btn) {
    var slug = btn.getAttribute('data-slug'), st = document.getElementById('mod-state');
    function paint() {
      var ok = done.indexOf(slug) >= 0;
      btn.textContent = ok ? '✓ Selesai (klik untuk batalkan)' : '✓ Tandai selesai';
      btn.classList.toggle('pri', ok); btn.classList.toggle('sec', !ok);
      if (st) st.textContent = ok ? '✓ Sudah selesai' : '';
    }
    btn.addEventListener('click', function () {
      done = load();
      var i = done.indexOf(slug);
      if (i >= 0) done.splice(i, 1); else done.push(slug);
      save(done); paint();
    });
    paint();
  }
})();
