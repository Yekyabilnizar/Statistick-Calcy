/* tool.js – alat analisis di halaman metode: ambil data, bangun formulir kolom, jalankan, tampilkan hasil. */
(function () {
  var spec = JSON.parse(document.getElementById('spec').textContent);
  var slug = spec.slug, fields = spec.fields;
  var $ = function (id) { return document.getElementById(id); };
  var info = null, timer = null;
  function L(a, b) { return window.LANG === 'en' ? b : a; }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function notice(msg, kind) {
    var ic = {info: 'ℹ️', success: '✅', warning: '⚠️', error: '⛔'}[kind || 'info'];
    return '<div class="notice ' + (kind || 'info') + '"><span>' + ic + '</span><div>' + esc(msg) + '</div></div>';
  }
  function post(url, body) {
    return fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(Object.assign({lang: window.LANG || 'id'}, body))})
      .then(function (r) { return r.json().catch(function () { return {ok: false, error: L('Server tidak merespons dengan benar (kode ', 'The server did not respond correctly (code ') + r.status + ').'}; }); });
  }

  /* ---------- sumber data ---------- */
  function setSrc(name) {
    document.querySelectorAll('.src-tabs button').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-src') === name); });
    ['sample', 'file', 'paste', 'manual'].forEach(function (n) { $('src-' + n).hidden = n !== name; });
    $('data').hidden = name === 'manual';
    if (name === 'manual') { openManual(); return; }
    if (name === 'sample') loadSample();
    if (name === 'paste') { $('data').value = ''; $('data').focus(); resetForm(); $('data-msg').innerHTML = notice(L('Tempel data (baris pertama berisi nama kolom), formulir kolom akan muncul otomatis.', 'Paste your data (first row = column names); the column form will appear automatically.'), 'info'); }
  }
  function loadSample() {
    fetch('/api/' + slug + '/sample').then(function (r) { return r.json(); }).then(function (j) {
      $('data').value = j.csv || ''; inspect();
    }).catch(function () { $('data-msg').innerHTML = notice(L('Data contoh gagal dimuat. Muat ulang halaman.', 'Sample data failed to load. Reload the page.'), 'error'); });
  }
  function resetForm() { info = null; $('form-panel').hidden = true; $('preview').innerHTML = ''; }

  function inspect() {
    var text = $('data').value;
    if (!text.trim()) { resetForm(); return; }
    $('data-msg').innerHTML = '<span class="spin"></span>' + L('Membaca data…', 'Reading data…');
    post('/api/inspect', {csv: text}).then(function (j) {
      if (!j.ok) { resetForm(); $('data-msg').innerHTML = notice(j.error, 'error'); return; }
      info = j.info;
      var nm = info.columns.filter(function (c) { return c.missing; }).length;
      $('data-msg').innerHTML = notice(info.rows + L(' baris dan ', ' rows and ') + info.columns.length + L(' kolom terbaca.', ' columns read.') + (nm ? L(' Ada ', ' ') + nm + L(' kolom dengan sel kosong; baris tidak lengkap dilewati saat analisis.', ' column(s) have empty cells; incomplete rows are skipped during analysis.') : ''), 'success');
      var p = info.preview;
      $('preview').innerHTML = '<details class="more"><summary>👁️ ' + L('Pratinjau data', 'Data preview') + '</summary><div class="sc-wrap"><table class="sc-table"><thead><tr>' +
        p.header.map(function (h) { return '<th>' + esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' +
        p.rows.map(function (r) { return '<tr>' + r.map(function (v) { return '<td>' + esc(v) + '</td>'; }).join('') + '</tr>'; }).join('') +
        '</tbody></table></div><p class="cap">' + L('Menampilkan 8 baris pertama.', 'Showing the first 8 rows.') + '</p></details>';
      buildForm(); $('form-panel').hidden = false; $('result').innerHTML = ''; $('xlsx').hidden = true;
    });
  }

  /* ---------- formulir kolom ---------- */
  var state = {};
  function pool(type) {
    return info.columns.filter(function (c) { return type === 'num' || type === 'num_multi' ? c.numeric : type === 'cat' || type === 'cat_opt' || type === 'cat_multi' ? c.cat : true; })
      .map(function (c) { return c.name; });
  }
  var COLT = ['num', 'cat', 'any', 'cat_opt', 'any_opt', 'num_multi', 'cat_multi', 'any_multi'];
  function isMulti(t) { return t.slice(-5) === 'multi'; }
  function isOpt(t) { return t === 'cat_opt' || t === 'any_opt'; }
  function opt(c, sel) { return '<option value="' + esc(c) + '"' + (sel ? ' selected' : '') + '>' + esc(c) + '</option>'; }
  function buildForm() {
    var host = $('fields'); host.innerHTML = '';
    var used = [];
    fields.forEach(function (f) {
      var wrap = document.createElement('div'); wrap.className = 'fld'; wrap.setAttribute('data-name', f.name);
      var id = 'f_' + f.name, html = '<label class="l" for="' + id + '">' + esc(f.label) + '</label>', t = f.type;
      if (COLT.indexOf(t) >= 0 && !isMulti(t)) {
        var cand = pool(t).filter(function (c) { return f.reuse || used.indexOf(c) < 0; });
        var def = f.want && cand.indexOf(f.want) >= 0 ? f.want : (isOpt(t) ? '' : cand.length ? cand[(f.pos < 0 ? cand.length + f.pos : f.pos)] || cand[0] : '');
        if (isOpt(t) && f.want && cand.indexOf(f.want) >= 0) def = f.want;
        html += '<select id="' + id + '">' + (isOpt(t) ? '<option value="">' + L('(tidak ada)', '(none)') + '</option>' : '') + cand.map(function (c) { return opt(c, c === def); }).join('') + '</select>';
        if (def && !f.reuse) used.push(def);
      } else if (COLT.indexOf(t) >= 0) {
        var cm = pool(t).filter(function (c) { return used.indexOf(c) < 0; });
        var sel = (f.want || []).filter(function (c) { return cm.indexOf(c) >= 0; });
        if (!sel.length && f.auto) sel = f.auto === true ? cm.slice(0, 4) : cm.slice(0, Number(f.auto));
        html += '<select id="' + id + '" multiple>' + cm.map(function (c) { return opt(c, sel.indexOf(c) >= 0); }).join('') + '</select>' +
          '<div class="h">' + L('Tahan Ctrl (atau ⌘) untuk memilih lebih dari satu.', 'Hold Ctrl (or ⌘) to select more than one.') + '</div>';
        used = used.concat(sel);
      } else if (t === 'int' || t === 'float') {
        html += '<input id="' + id + '" type="number" min="' + f.min + '" max="' + f.max + '" step="' + (f.step || 1) + '" value="' + f.default + '">';
      } else if (t === 'float_opt') {
        html += '<input id="' + id + '" type="number" step="any" placeholder="' + esc(f.placeholder || '') + '">';
      } else if (t === 'text') {
        html += '<input id="' + id + '" type="text" maxlength="200" value="' + esc(f.default || '') + '">';
      } else if (t === 'bool') {
        html = '<label class="chk"><input id="' + id + '" type="checkbox"' + (f.default ? ' checked' : '') + '><span>' + esc(f.label) + (f.help ? '<div class="h" style="font-weight:400">' + esc(f.help) + '</div>' : '') + '</span></label>';
      } else if (t === 'select') {
        html += '<select id="' + id + '">' + f.options.map(function (o) { return opt(o, o === f.default); }).join('') + '</select>' + (f.help ? '<div class="h">' + esc(f.help) + '</div>' : '');
      } else if (t === 'select_multi') {
        html += '<div class="chkgrid" id="' + id + '">' + f.options.map(function (o) { return '<label><input type="checkbox" value="' + esc(o) + '"' + (f.default.indexOf(o) >= 0 ? ' checked' : '') + '>' + esc(o) + '</label>'; }).join('') + '</div>';
      }
      wrap.innerHTML = html; host.appendChild(wrap);
    });
    host.querySelectorAll('select').forEach(function (s) { s.addEventListener('change', refreshOptions); });
  }
  /* saat satu kolom diganti, kolom itu tidak boleh dipakai lagi di isian sesudahnya */
  function refreshOptions() {
    var used = [];
    fields.forEach(function (f) {
      var el = $('f_' + f.name), t = f.type;
      if (!el || COLT.indexOf(t) < 0) return;
      var multi = isMulti(t);
      var cur = multi ? Array.prototype.filter.call(el.options, function (o) { return o.selected; }).map(function (o) { return o.value; }) : [el.value];
      var cand = pool(t).filter(function (c) { return f.reuse || used.indexOf(c) < 0; });
      var keep = cur.filter(function (c) { return cand.indexOf(c) >= 0; });
      if (!multi && !keep.length && !isOpt(t)) keep = [cand[0]];
      el.innerHTML = (isOpt(t) ? '<option value="">' + L('(tidak ada)', '(none)') + '</option>' : '') + cand.map(function (c) { return opt(c, keep.indexOf(c) >= 0); }).join('');
      if (!multi && keep.length) el.value = keep[0];
      if (!f.reuse) used = used.concat(keep.filter(Boolean));
    });
  }
  function collect() {
    var p = {};
    fields.forEach(function (f) {
      var el = $('f_' + f.name), t = f.type;
      if (!el) return;
      if (isMulti(t) && COLT.indexOf(t) >= 0) p[f.name] = Array.prototype.filter.call(el.options, function (o) { return o.selected; }).map(function (o) { return o.value; });
      else if (t === 'select_multi') p[f.name] = Array.prototype.map.call(el.querySelectorAll('input:checked'), function (i) { return i.value; });
      else if (t === 'bool') p[f.name] = el.checked;
      else if (t === 'int' || t === 'float') p[f.name] = parseFloat(el.value);
      else if (t === 'float_opt') p[f.name] = el.value === '' ? null : parseFloat(el.value);
      else p[f.name] = el.value === '' ? null : el.value;
    });
    return p;
  }

  /* ---------- jalankan ---------- */
  var busy = false, last = null;
  function resultOpts() {
    var o = {}, ctrl = {}, any = false;
    $('result').querySelectorAll('[data-opt]').forEach(function (s) { o[s.getAttribute('data-opt')] = s.value; any = true; });
    $('result').querySelectorAll('[data-opt-ctrl]').forEach(function (s) { ctrl[s.getAttribute('data-opt-ctrl')] = s.value; any = true; });
    if (Object.keys(ctrl).length) o.ctrl = ctrl;
    return o;
  }
  function activeTab() {
    var nav = $('result').querySelector('.tab-nav'); if (!nav) return 0;
    var bs = Array.prototype.slice.call(nav.querySelectorAll('.tab-btn')); var i = bs.findIndex(function (b) { return b.classList.contains('on'); });
    return i < 0 ? 0 : i;
  }
  function run(rerun) {
    if (busy || !info) return;
    var keep = rerun ? activeTab() : 0, opts = rerun ? resultOpts() : {};
    if (!rerun) last = {csv: $('data').value, params: collect(), alpha: parseFloat($('alpha').value)};
    last.opts = opts;
    busy = true; $('run').disabled = true;
    if (rerun) $('result').style.opacity = '.55';
    else $('result').innerHTML = '<div class="notice info"><span><span class="spin"></span></span><div>' + L('Menghitung… analisis berat dapat memakan beberapa detik.', 'Calculating… heavy analyses can take a few seconds.') + '</div></div>';
    post('/api/' + slug + '/run', last).then(function (j) {
      busy = false; $('run').disabled = false; $('result').style.opacity = '';
      if (!j.ok) { $('result').innerHTML = notice(j.error, 'error'); $('xlsx').hidden = true; return; }
      $('result').innerHTML = j.html; $('xlsx').hidden = false;
      var nav = $('result').querySelector('.tab-nav'), btn = nav && nav.querySelectorAll('.tab-btn')[keep];
      if (btn) btn.click();
      else { var first = $('result').querySelector('.tab-panel.on'); if (first) drawPlots(first); }
      initPredictors($('result'));
      if (window.fxWatch) fxWatch($('result'));
      if (window.toast && !rerun) toast(L('✅ Analisis selesai', '✅ Analysis complete'));
      if (!rerun) $('result').scrollIntoView({behavior: 'smooth', block: 'start'});
    }).catch(function () { busy = false; $('run').disabled = false; $('result').style.opacity = ''; $('result').innerHTML = notice(L('Koneksi ke server gagal. Coba lagi.', 'Connection to the server failed. Please try again.'), 'error'); });
  }
  function chartImages() {
    var boxes = Array.prototype.slice.call($('result').querySelectorAll('.plot-box'));
    if (!boxes.length) return Promise.resolve([]);
    return loadPlotly().then(function () {
      return Promise.all(boxes.map(function (b) {
        try {
          var d = JSON.parse(b.querySelector('.plot-data').textContent), lay = theme(d.layout), w = 900, h = lay.height || 420;
          lay.width = w; lay.paper_bgcolor = '#FFFFFF'; lay.plot_bgcolor = '#FFFFFF';
          var t = d.layout && d.layout.title ? (d.layout.title.text || d.layout.title) : '';
          return Plotly.toImage({data: d.data, layout: lay}, {format: 'png', width: w, height: h, scale: 1})
            .then(function (png) { return {title: String(t).replace(/<[^>]+>/g, ''), png: png}; }).catch(function () { return null; });
        } catch (e) { return Promise.resolve(null); }
      }));
    }).then(function (a) { return a.filter(Boolean); }).catch(function () { return []; });
  }
  function download() {
    if (!last) { alert(L('Jalankan analisis terlebih dahulu.', 'Run the analysis first.')); return; }
    last.opts = resultOpts();
    var btn = $('xlsx'), lbl = btn.innerHTML;
    btn.disabled = true; btn.innerHTML = '<span class="spin"></span>' + L('Menyiapkan Excel…', 'Preparing Excel…');
    chartImages().then(function (imgs) {
      return fetch('/api/' + slug + '/xlsx', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(Object.assign({lang: window.LANG || 'id', images: imgs}, last))});
    })
      .then(function (r) { if (!r.ok) throw new Error(); return r.blob(); })
      .then(function (b) { var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'hasil_' + slug + '.xlsx'; document.body.appendChild(a); a.click(); a.remove(); if (window.toast) toast(L('⬇️ Berkas Excel diunduh (data, hasil, dan grafik)', '⬇️ Excel file downloaded (data, results, and charts)')); })
      .catch(function () { alert(L('Gagal membuat berkas Excel. Jalankan analisis terlebih dahulu.', 'Could not create the Excel file. Run the analysis first.')); })
      .then(function () { btn.disabled = false; btn.innerHTML = lbl; });
  }
  /* uji lanjut / kontrol Dunnett / SD-SE: hitung ulang dengan opsi baru, tab aktif dipertahankan */
  $('result').addEventListener('change', function (e) {
    if (e.target.matches && (e.target.matches('[data-opt]') || e.target.matches('[data-opt-ctrl]'))) run(true);
  });

  /* ---------- kalkulator prediksi regresi ---------- */
  function tq(v) { return Number.isFinite(v) ? v : NaN; }
  function fmt(v) { if (!Number.isFinite(v)) return '–'; var a = Math.abs(v); return (a !== 0 && (a >= 1e6 || a < 1e-3)) ? v.toExponential(4) : (Math.round(v * 1e6) / 1e6).toString(); }
  function initPredictors(root) {
    root.querySelectorAll('.predictor').forEach(function (box) {
      if (box.getAttribute('data-ready')) return;
      var c = JSON.parse(box.getAttribute('data-cfg')); box.setAttribute('data-ready', '1');
      var h = '<div class="pgrid">' + c.xs.map(function (x, i) {
        return '<div class="fld"><label class="l">' + esc(x) + '</label><input type="number" step="any" data-i="' + i + '" value="' + c.mean[i] + '"><div class="h">' + L('rentang data: ', 'data range: ') + fmt(c.min[i]) + ' – ' + fmt(c.max[i]) + '</div></div>';
      }).join('') + '</div><div class="pout"></div>';
      box.innerHTML = h;
      function calc() {
        var vals = Array.prototype.map.call(box.querySelectorAll('input'), function (i) { return parseFloat(i.value); });
        var out = box.querySelector('.pout');
        if (vals.some(function (v) { return !Number.isFinite(v); })) { out.innerHTML = '<p class="cap">' + L('Isi semua nilai X.', 'Fill in all X values.') + '</p>'; return; }
        var x = (c.intercept ? [1] : []).concat(vals), n = x.length, pred = 0, v = 0, i, j;
        for (i = 0; i < n; i++) { pred += x[i] * c.beta[i]; for (j = 0; j < n; j++) v += x[i] * c.cov[i][j] * x[j]; }
        var sm = Math.sqrt(Math.max(v, 0)), sp = Math.sqrt(Math.max(v + c.s2, 0)), cl = Math.round((1 - c.alpha) * 100);
        var extra = vals.some(function (q, k) { return q < c.min[k] || q > c.max[k]; });
        out.innerHTML = '<div class="pbig">Ŷ = ' + fmt(pred) + '</div><p class="cap">' + L('Prediksi untuk ', 'Prediction for ') + esc(c.y) + '</p>' +
          '<div class="sc-wrap"><table class="sc-table"><thead><tr><th>' + L('Selang', 'Interval') + '</th><th>' + L('Bawah', 'Lower') + '</th><th>' + L('Atas', 'Upper') + '</th></tr></thead><tbody>' +
          '<tr><td>CI ' + cl + '% ' + L('(rata-rata Y)', '(mean of Y)') + '</td><td>' + fmt(pred - c.tcrit * sm) + '</td><td>' + fmt(pred + c.tcrit * sm) + '</td></tr>' +
          '<tr><td>PI ' + cl + '% ' + L('(satu pengamatan baru)', '(single new observation)') + '</td><td>' + fmt(pred - c.tcrit * sp) + '</td><td>' + fmt(pred + c.tcrit * sp) + '</td></tr></tbody></table></div>' +
          (extra ? '<div class="notice warning"><span>⚠️</span><div>' + L('Nilai X berada di luar rentang data. Ini ekstrapolasi, jadi prediksi kurang dapat dipercaya.', 'The X values are outside the data range. This is extrapolation, so the prediction is less reliable.') + '</div></div>' : '');
      }
      box.addEventListener('input', calc); calc();
    });
  }

  /* ---------- ketik di tabel ---------- */
  var grid = {head: [], rows: []}, gridInit = false;
  function parseTSV(t) { return t.replace(/\r/g, '').split('\n').filter(function (l) { return l.length; }).map(function (l) { return l.split('\t'); }); }
  function drawGrid() {
    var h = '<table><thead><tr><th class="rn">#</th>' + grid.head.map(function (x, j) { return '<th><input data-r="-1" data-c="' + j + '" value="' + esc(x) + '"></th>'; }).join('') + '</tr></thead><tbody>' +
      grid.rows.map(function (r, i) { return '<tr><td class="rn">' + (i + 1) + '</td>' + r.map(function (v, j) { return '<td><input data-r="' + i + '" data-c="' + j + '" value="' + esc(v) + '"></td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table>';
    $('grid').innerHTML = h;
  }
  function syncGrid() {
    var head = grid.head.map(function (x, j) { return (x || '').trim() || L('Kolom', 'Column') + (j + 1); });
    var lines = [head.join('\t')].concat(grid.rows.filter(function (r) { return r.some(function (v) { return String(v).trim() !== ''; }); }).map(function (r) { return r.join('\t'); }));
    $('data').value = lines.join('\n');
    clearTimeout(timer); timer = setTimeout(function () { if (grid.rows.length) inspect(); else resetForm(); }, 600);
  }
  function setGrid(tsv) {
    var t = parseTSV(tsv); grid.head = t[0] || ['A', 'B']; grid.rows = t.slice(1);
    var w = grid.head.length; grid.rows = grid.rows.map(function (r) { while (r.length < w) r.push(''); return r.slice(0, w); });
    drawGrid(); syncGrid();
  }
  function openManual() {
    $('data-msg').innerHTML = notice(L('Ketik atau tempel data di tabel. Formulir kolom muncul otomatis begitu data terbaca.', 'Type or paste data into the table. The column form appears automatically once the data is read.'), 'info');
    if (!gridInit) {
      gridInit = true;
      fetch('/api/' + slug + '/sample').then(function (r) { return r.json(); }).then(function (j) { setGrid(j.csv || ''); buildManualGen(); });
    } else syncGrid();
  }
  function blankRow() { return grid.head.map(function () { return ''; }); }
  $('grid').addEventListener('input', function (e) {
    var i = +e.target.getAttribute('data-r'), j = +e.target.getAttribute('data-c');
    if (i < 0) grid.head[j] = e.target.value; else grid.rows[i][j] = e.target.value;
    syncGrid();
  });
  $('grid').addEventListener('paste', function (e) {
    var t = (e.clipboardData || window.clipboardData).getData('text');
    if (t.indexOf('\t') < 0 && t.indexOf('\n') < 0) return;
    e.preventDefault();
    var i = +e.target.getAttribute('data-r'), j = +e.target.getAttribute('data-c'), blk = parseTSV(t);
    blk.forEach(function (r, di) {
      var ri = i < 0 ? di - 1 : i + di;
      if (ri >= 0) while (grid.rows.length <= ri) grid.rows.push(blankRow());
      r.forEach(function (v, dj) {
        var cj = j + dj; while (grid.head.length <= cj) { grid.head.push(L('Kolom', 'Column') + (grid.head.length + 1)); grid.rows.forEach(function (rr) { rr.push(''); }); }
        if (ri < 0) grid.head[cj] = v; else grid.rows[ri][cj] = v;
      });
    });
    drawGrid(); syncGrid();
  });
  $('g-addrow').addEventListener('click', function () { grid.rows.push(blankRow()); drawGrid(); syncGrid(); });
  $('g-delrow').addEventListener('click', function () { grid.rows.pop(); drawGrid(); syncGrid(); });
  $('g-addcol').addEventListener('click', function () { grid.head.push(L('Kolom', 'Column') + (grid.head.length + 1)); grid.rows.forEach(function (r) { r.push(''); }); drawGrid(); syncGrid(); });
  $('g-delcol').addEventListener('click', function () { if (grid.head.length > 1) { grid.head.pop(); grid.rows.forEach(function (r) { r.pop(); }); drawGrid(); syncGrid(); } });
  $('g-clear').addEventListener('click', function () { grid.rows = []; for (var i = 0; i < 6; i++) grid.rows.push(blankRow()); drawGrid(); syncGrid(); });
  /* pembangkit kerangka tabel untuk RAL/RAK */
  function buildManualGen() {
    if (spec.key !== 'ral' && spec.key !== 'rak') return;
    var rak = spec.key === 'rak';
    $('manual-gen').innerHTML = '<details class="more"><summary>🧱 ' + L('Buat kerangka tabel otomatis', 'Create a table skeleton automatically') + '</summary><div class="fields" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">' +
      '<div class="fld"><label class="l">' + L('Jumlah perlakuan', 'Number of treatments') + '</label><input id="mg-t" type="number" min="2" max="30" value="4"></div>' +
      '<div class="fld"><label class="l">' + (rak ? L('Jumlah kelompok', 'Number of groups') : L('Ulangan per perlakuan', 'Replicates per treatment')) + '</label><input id="mg-r" type="number" min="2" max="30" value="4"></div>' +
      '<div class="fld"><label class="l">' + L('Nama kolom perlakuan', 'Treatment column name') + '</label><input id="mg-nt" value="' + L('Perlakuan', 'Treatment') + '"></div>' +
      (rak ? '<div class="fld"><label class="l">' + L('Nama kolom kelompok', 'Group column name') + '</label><input id="mg-nb" value="' + L('Kelompok', 'Group') + '"></div>' : '') +
      '<div class="fld"><label class="l">' + L('Nama kolom respon', 'Response column name') + '</label><input id="mg-ny" value="' + L('Respon', 'Response') + '"></div></div>' +
      '<button type="button" class="btn sec mini" id="mg-go" style="margin-top:10px">' + L('Buat tabel', 'Create table') + '</button></details>';
    $('mg-go').addEventListener('click', function () {
      var t = Math.min(Math.max(+$('mg-t').value || 4, 2), 30), r = Math.min(Math.max(+$('mg-r').value || 4, 2), 30), rows = [], i, k;
      grid.head = [$('mg-nt').value || 'Perlakuan'].concat(rak ? [$('mg-nb').value || 'Kelompok'] : []).concat([$('mg-ny').value || 'Respon']);
      for (i = 1; i <= t; i++) for (k = 1; k <= r; k++) rows.push(rak ? ['P' + i, 'K' + k, ''] : ['P' + i, '']);
      grid.rows = rows; drawGrid(); syncGrid();
    });
  }

  /* ---------- pembangkit rancangan ---------- */
  if (spec.gen && $('gen-fields')) {
    $('gen-fields').innerHTML = spec.gen.fields.map(function (f) {
      var id = 'g_' + f.name, h = '<div class="fld"><label class="l" for="' + id + '">' + esc(f.label) + '</label>';
      if (f.type === 'select') h += '<select id="' + id + '">' + f.options.map(function (o) { return opt(o, o === f.default); }).join('') + '</select>';
      else if (f.type === 'text') h += '<input id="' + id + '" type="text" value="' + esc(f.default || '') + '">';
      else h += '<input id="' + id + '" type="number" min="' + f.min + '" max="' + f.max + '" value="' + f.default + '">';
      return h + '</div>';
    }).join('');
    $('gen-run').addEventListener('click', function () {
      var b = {}; spec.gen.fields.forEach(function (f) { var v = $('g_' + f.name).value; b[f.name] = (f.type === 'int' || f.type === 'float') ? parseFloat(v) : v; });
      $('gen-out').innerHTML = '<span class="spin"></span>' + L('Membangkitkan…', 'Generating…');
      post('/api/' + slug + '/gen', b).then(function (j) { $('gen-out').innerHTML = j.ok ? j.html : notice(j.error, 'error'); });
    });
  }

  /* ---------- grafik (Plotly dimuat saat pertama dibutuhkan) ---------- */
  var plotlyReady = null;
  function loadPlotly() {
    if (window.Plotly) return Promise.resolve();
    if (plotlyReady) return plotlyReady;
    plotlyReady = new Promise(function (res, rej) {
      var s = document.createElement('script'); s.src = 'https://cdn.plot.ly/plotly-2.35.2.min.js'; s.onload = res; s.onerror = rej; document.head.appendChild(s);
    });
    return plotlyReady;
  }
  var FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
  var AX = {showgrid: true, gridcolor: '#EEF2F7', zeroline: false, showline: true, linecolor: '#C9D3DF', ticks: 'outside', tickcolor: '#C9D3DF', ticklen: 4, automargin: true, fixedrange: true, title: {standoff: 10}};
  function theme(l) {
    var out = Object.assign({}, l);
    out.height = l.height || 400; out.margin = l.margin || {l: 56, r: 20, t: 54, b: 56};
    out.paper_bgcolor = 'rgba(0,0,0,0)'; out.plot_bgcolor = 'rgba(255,255,255,0)';
    out.colorway = ['#1E3A8A', '#7CB518', '#0E9F9A', '#F59E0B', '#DC4C64', '#6D5BD0', '#3B82F6', '#9CA3AF'];
    out.font = {family: FONT, color: '#1F2D3D', size: 12.5};
    out.title = Object.assign({x: 0.01, xanchor: 'left', y: 0.97, font: {size: 14.5, color: '#0E1A2B'}}, typeof l.title === 'string' ? {text: l.title} : (l.title || {}));
    out.legend = Object.assign({orientation: 'h', y: -0.22, x: 0, font: {size: 12}}, l.legend || {});
    out.hoverlabel = {bgcolor: '#14223A', bordercolor: '#14223A', font: {color: '#fff', family: FONT, size: 12}};
    out.dragmode = false;
    if (l.xaxis) out.xaxis = Object.assign({}, AX, l.xaxis);
    if (l.yaxis) out.yaxis = Object.assign({}, AX, l.yaxis);
    Object.keys(l).forEach(function (k) { if (/^[xy]axis\d+$/.test(k)) out[k] = Object.assign({}, AX, l[k]); });
    return out;
  }
  var PCFG = {responsive: true, displaylogo: false, scrollZoom: false, doubleClick: false, showTips: false,
              modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian', 'zoom3d', 'pan3d', 'orbitRotation', 'tableRotation', 'resetCameraDefault3d', 'resetCameraLastSave3d'],
              toImageButtonOptions: {format: 'png', scale: 2}};
  window.drawPlots = function (root) {
    var boxes = root.querySelectorAll('.plot-box');
    if (!boxes.length) return;
    loadPlotly().then(function () {
      boxes.forEach(function (b) {
        var el = b.querySelector('.plot');
        if (el.getAttribute('data-done')) { Plotly.Plots.resize(el); return; }
        var d = JSON.parse(b.querySelector('.plot-data').textContent);
        var hh = (d.layout && d.layout.height) || 420;
        el.style.height = hh + 'px';
        if (hh > 500) b.classList.add('wide');
        Plotly.newPlot(el, d.data, theme(d.layout), PCFG);
        el.setAttribute('data-done', '1');
      });
    }).catch(function () { boxes.forEach(function (b) { b.querySelector('.plot').innerHTML = '<p class="cap">' + L('Grafik tidak dapat dimuat (pustaka grafik tidak terjangkau). Periksa koneksi internet Anda.', 'The chart could not be loaded (the charting library is unreachable). Check your internet connection.') + '</p>'; }); });
  };

  /* ---------- pasang kejadian ---------- */
  document.querySelectorAll('.src-tabs button').forEach(function (b) { b.addEventListener('click', function () { setSrc(b.getAttribute('data-src')); }); });
  $('data').addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(inspect, 600); });
  $('file').addEventListener('change', function () {
    var f = this.files[0]; if (!f) return;
    if (f.size > 4 * 1024 * 1024) { $('data-msg').innerHTML = notice(L('Berkas terlalu besar (maksimal 4 MB).', 'File too large (maximum 4 MB).'), 'error'); return; }
    var fd = new FormData(); fd.append('file', f);
    $('data-msg').innerHTML = '<span class="spin"></span>' + L('Membaca berkas…', 'Reading file…');
    fetch('/api/parse', {method: 'POST', body: fd}).then(function (r) { return r.json(); }).then(function (j) {
      if (!j.ok) { $('data-msg').innerHTML = notice(j.error, 'error'); return; }
      $('data').value = j.csv; inspect();
    }).catch(function () { $('data-msg').innerHTML = notice(L('Berkas gagal dikirim. Coba lagi.', 'The file failed to upload. Please try again.'), 'error'); });
  });
  $('run').addEventListener('click', function () { run(false); });
  $('xlsx').addEventListener('click', download);
  loadSample();
})();
