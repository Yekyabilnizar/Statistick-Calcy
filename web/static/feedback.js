(function () {
  var EN = window.LANG === 'en';
  function T(id, en) { return EN ? en : id; }
  var $ = function (id) { return document.getElementById(id); };
  var rating = 0, busy = false;
  function paint() { document.querySelectorAll('#fb-stars button[data-v]').forEach(function (b) { var v = +b.getAttribute('data-v'); if (v >= 1) { b.textContent = v <= rating ? '★' : '☆'; b.classList.toggle('on', v <= rating); } }); }
  $('fb-stars').addEventListener('click', function (e) { var b = e.target.closest('button[data-v]'); if (!b) return; rating = +b.getAttribute('data-v'); paint(); });
  function msg(t, k) { var m = $('fb-msgbox'); m.innerHTML = t ? '<div class="notice ' + k + '"><span>' + (k === 'error' ? '⛔' : 'ℹ️') + '</span><div></div></div>' : ''; if (t) m.querySelector('div > div').textContent = t; }
  $('fb-form').addEventListener('submit', function (e) {
    e.preventDefault(); if (busy) return;
    if ($('fb-msg').value.trim().length < 10) { msg(T('Pesan terlalu pendek (minimal 10 karakter).', 'Message too short (at least 10 characters).'), 'error'); return; }
    if (!$('fb-ok').checked) { msg(T('Centang persetujuan penyimpanan masukan terlebih dahulu.', 'Please tick the consent to store your feedback first.'), 'error'); return; }
    busy = true; $('fb-send').disabled = true; msg(T('Mengirim…', 'Sending…'), 'info');
    fetch('/api/feedback', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
      kategori: $('fb-kat').value, metode: $('fb-met').value, pesan: $('fb-msg').value, nilai: rating, kontak: $('fb-contact').value, setuju: $('fb-ok').checked, website: $('fb-hp').value})})
      .then(function (r) { return r.json().catch(function () { return {ok: false, error: T('Server tidak merespons dengan benar.', 'The server did not respond correctly.')}; }); })
      .then(function (j) {
        busy = false; $('fb-send').disabled = false;
        if (!j.ok) { msg(EN ? 'Could not send your feedback right now. Please try again in a moment.' : (j.error || 'Gagal mengirim.'), 'error'); return; }
        $('fb-form').hidden = true; $('fb-done').hidden = false;
      }).catch(function () { busy = false; $('fb-send').disabled = false; msg(T('Koneksi gagal. Coba lagi.', 'Connection failed. Please try again.'), 'error'); });
  });
  $('fb-again').addEventListener('click', function () {
    $('fb-msg').value = ''; $('fb-contact').value = ''; $('fb-ok').checked = false; rating = 0; paint(); msg('');
    $('fb-form').hidden = false; $('fb-done').hidden = true;
  });
})();
