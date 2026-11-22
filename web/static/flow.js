(function () {
  var $ = function (id) { return document.getElementById(id); };
  var all = JSON.parse($('all-methods').textContent), cur = JSON.parse($('cur-slug').textContent);
  var fam = $('fl-fam'), grp = $('fl-grp'), met = $('fl-met');
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function fillGroups(sel) {
    var g = []; all.forEach(function (m) { if (m.f === fam.value && g.indexOf(m.g) < 0) g.push(m.g); });
    grp.innerHTML = g.map(function (x) { return '<option' + (x === sel ? ' selected' : '') + '>' + esc(x) + '</option>'; }).join('');
  }
  function fillMethods(sel) {
    met.innerHTML = all.filter(function (m) { return m.f === fam.value && m.g === grp.value; }).map(function (m) { return '<option value="' + m.s + '"' + (m.s === sel ? ' selected' : '') + '>' + esc(m.t) + '</option>'; }).join('');
  }
  function go() { if (met.value) location.href = (window.LP || '') + '/alur-metode?m=' + encodeURIComponent(met.value); }
  var c = all.filter(function (m) { return m.s === cur; })[0];
  fillGroups(c && c.g); fillMethods(cur);
  fam.addEventListener('change', function () { fillGroups(); fillMethods(); go(); });
  grp.addEventListener('change', function () { fillMethods(); go(); });
  met.addEventListener('change', go);
})();
