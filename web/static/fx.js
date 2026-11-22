/* fx.js – gerak halus & interaksi umum: muncul saat gulir, penghitung angka, riak tombol, bilah baca, toast, konfeti */
(function () {
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.add('js');

  /* bilah progres gulir */
  var bar = document.createElement('div'); bar.className = 'scrollbar'; document.body.appendChild(bar);
  var top = document.createElement('button'); top.className = 'totop'; top.type = 'button'; top.setAttribute('aria-label', 'Kembali ke atas'); top.textContent = '↑'; document.body.appendChild(top);
  function onScroll() {
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight, y = h.scrollTop || document.body.scrollTop;
    bar.style.width = (max > 0 ? Math.min(100, 100 * y / max) : 0) + '%';
    top.classList.toggle('show', y > 600);
  }
  window.addEventListener('scroll', onScroll, {passive: true}); onScroll();
  top.addEventListener('click', function () { window.scrollTo({top: 0, behavior: reduce ? 'auto' : 'smooth'}); });

  /* muncul saat tergulir ke layar */
  var sel = '.panel,.mcard,.stat,.mod-row,.prose,.notice,.badge,.stage-card,h2.sec-h,.flow,.sc-wrap';
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, {rootMargin: '0px 0px -6% 0px', threshold: 0.05});
    var seen = 0;
    function watch(root) {
      (root || document).querySelectorAll(sel).forEach(function (el) {
        if (el.classList.contains('rv')) return;
        var r = el.getBoundingClientRect();
        el.classList.add('rv');
        el.style.transitionDelay = Math.min((seen++ % 6) * 40, 200) + 'ms';
        if (r.top < innerHeight) { requestAnimationFrame(function () { el.classList.add('in'); }); } else io.observe(el);
      });
    }
    watch();
    window.fxWatch = watch;
  } else { window.fxWatch = function () {}; }

  /* penghitung angka (.stat b, .count) */
  document.querySelectorAll('.stat b').forEach(function (el) {
    var to = parseInt(el.textContent, 10); if (!isFinite(to) || reduce || to > 9999) return;
    el.textContent = '0'; var t0 = null;
    function step(t) { if (!t0) t0 = t; var p = Math.min((t - t0) / 900, 1), e = 1 - Math.pow(1 - p, 3); el.textContent = Math.round(to * e); if (p < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  });

  /* riak pada tombol */
  document.addEventListener('pointerdown', function (e) {
    var b = e.target.closest && e.target.closest('.btn,.tab-btn,.mod-row,.mcard .go');
    if (!b || reduce) return;
    var r = b.getBoundingClientRect(), s = document.createElement('span'), d = Math.max(r.width, r.height) * 1.6;
    s.className = 'ripple'; s.style.cssText = 'width:' + d + 'px;height:' + d + 'px;left:' + (e.clientX - r.left - d / 2) + 'px;top:' + (e.clientY - r.top - d / 2) + 'px';
    if (getComputedStyle(b).position === 'static') b.style.position = 'relative';
    b.classList.add('has-ripple'); b.appendChild(s); setTimeout(function () { s.remove(); }, 600);
  });

  /* toast */
  var host = document.createElement('div'); host.className = 'toasts'; host.setAttribute('aria-live', 'polite'); document.body.appendChild(host);
  window.toast = function (msg, ms) {
    var t = document.createElement('div'); t.className = 'toast'; t.textContent = msg; host.appendChild(t);
    requestAnimationFrame(function () { t.classList.add('on'); });
    setTimeout(function () { t.classList.remove('on'); setTimeout(function () { t.remove(); }, 300); }, ms || 2600);
  };

  /* konfeti */
  window.confetti = function (x, y) {
    if (reduce) return;
    var c = document.createElement('canvas'); c.className = 'confetti'; c.width = innerWidth; c.height = innerHeight; document.body.appendChild(c);
    var g = c.getContext('2d'), cols = ['#2563EB', '#0D9488', '#F59E0B', '#E11D48', '#7C3AED', '#16A34A'], P = [], i;
    x = x == null ? innerWidth / 2 : x; y = y == null ? innerHeight / 3 : y;
    for (i = 0; i < 70; i++) { var a = Math.random() * Math.PI * 2, v = 4 + Math.random() * 7; P.push({x: x, y: y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 4, s: 5 + Math.random() * 6, c: cols[i % cols.length], r: Math.random() * 6, vr: (Math.random() - .5) * .4}); }
    var t0 = null;
    function f(t) {
      if (!t0) t0 = t; var el = t - t0; g.clearRect(0, 0, c.width, c.height);
      P.forEach(function (p) { p.vy += .22; p.x += p.vx; p.y += p.vy; p.vx *= .99; p.r += p.vr; g.save(); g.translate(p.x, p.y); g.rotate(p.r); g.globalAlpha = Math.max(0, 1 - el / 1400); g.fillStyle = p.c; g.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); g.restore(); });
      if (el < 1500) requestAnimationFrame(f); else c.remove();
    }
    requestAnimationFrame(f);
  };
})();
