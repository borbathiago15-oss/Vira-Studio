/* VIRA Studio · Camadas da solução
   Home: cada seção fica presa (sticky) quando termina e a próxima sobe por cima,
   enquanto a de baixo recua (escala + escurece). Índice lateral e contador
   mostram em que camada da solução o visitante está.
   Sem dependências. Não altera nada que o React controla (só atributos data-*
   e variáveis CSS inline em elementos sem style próprio). */
(function () {
  'use strict';

  var LABELS = {
    hero: 'Início',
    cases: 'Projetos',
    manifesto: 'A ideia',
    solucoes: 'Soluções',
    'como-pensamos': 'Método',
    processo: 'Processo',
    tecnologia: 'Tecnologia',
    investimento: 'Investimento',
    faq: 'Dúvidas',
    sobre: 'Quem faz',
    contato: 'Sua solução'
  };

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var st = null;

  function isHome() {
    var p = location.pathname.replace(/\/index\.html$/, '/');
    return p === '/' || p === '';
  }

  function teardown() {
    if (!st) return;
    window.removeEventListener('scroll', st.onScroll);
    window.removeEventListener('resize', st.onResize);
    if (st.ro) st.ro.disconnect();
    st.items.forEach(function (it) {
      it.el.removeAttribute('data-vs-layer');
      it.el.removeAttribute('data-vs-flow');
      ['--vs-top', '--vs-z', '--vs-p', '--vs-origin', '--vs-scale'].forEach(function (v) {
        it.el.style.removeProperty(v);
      });
    });
    [st.index, st.meter, st.bar].forEach(function (n) { if (n && n.parentNode) n.parentNode.removeChild(n); });
    document.documentElement.removeAttribute('data-vs');
    st = null;
  }

  function setup() {
    teardown();
    if (!isHome()) return;
    var main = document.getElementById('conteudo');
    if (!main) return;

    var kids = Array.prototype.slice.call(main.children).filter(function (el) {
      return el.tagName !== 'SCRIPT' && el.tagName !== 'TEMPLATE' && el.offsetHeight > 0;
    });
    var sections = kids.filter(function (el) { return el.tagName === 'SECTION'; });
    if (sections.length < 4) return;

    document.documentElement.setAttribute('data-vs', '');
    var items = kids.map(function (el, i) {
      var isLayer = el.tagName === 'SECTION';
      el.setAttribute(isLayer ? 'data-vs-layer' : 'data-vs-flow', isLayer && i > 0 ? 'card' : '');
      el.style.setProperty('--vs-z', String(i + 1));
      return { el: el, layer: isLayer, h: 0, top: 0 };
    });
    // A última seção (CTA) não recua: é onde a solução fica pronta.
    var last = items[items.length - 1];

    // ---- índice e contador
    var layers = items.filter(function (it) { return it.layer; });
    var total = layers.length;
    var index = document.createElement('nav');
    index.className = 'vs-index';
    index.setAttribute('aria-label', 'Camadas da página');
    var count = document.createElement('span');
    count.className = 'vs-count';
    count.setAttribute('aria-hidden', 'true');
    count.innerHTML = '<span data-c>01</span><small>/' + pad(total) + '</small>';
    index.appendChild(count);
    var cN = count.querySelector('[data-c]');
    layers.forEach(function (it, n) {
      var id = it.el.id || (n === 0 ? 'hero' : '');
      var label = LABELS[id] || (it.el.querySelector('h2') || {}).textContent || 'Seção ' + (n + 1);
      var a = document.createElement('a');
      a.href = it.el.id ? '#' + it.el.id : '#conteudo';
      a.setAttribute('aria-label', pad(n + 1) + ' — ' + label);
      var tip = document.createElement('span');
      tip.className = 'vs-tip';
      tip.textContent = pad(n + 1) + ' · ' + label;
      a.appendChild(tip);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var y = it.natural;
        window.scrollTo({ top: Math.max(0, y), behavior: reduce.matches ? 'auto' : 'smooth' });
      });
      it.link = a;
      it.label = label;
      index.appendChild(a);
    });
    var meter = document.createElement('div');
    meter.className = 'vs-meter';
    meter.setAttribute('aria-hidden', 'true');
    meter.innerHTML = '<span>Camada <b data-n>01</b> / ' + pad(total) + '</span><span class="vs-bar"><i></i></span><span data-l></span>';
    var bar = document.createElement('div');
    bar.className = 'vs-top';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(index);
    document.body.appendChild(meter);
    document.body.appendChild(bar);
    var mN = meter.querySelector('[data-n]');
    var mL = meter.querySelector('[data-l]');

    var vh = window.innerHeight;
    var ticking = false;
    var current = -1;

    function measure() {
      vh = window.innerHeight;
      var small = window.innerWidth <= 860;
      // sticky não altera o fluxo: a posição natural é a soma das alturas anteriores
      var y = main.getBoundingClientRect().top + window.scrollY;
      items.forEach(function (it) {
        it.h = it.el.offsetHeight;
        it.natural = y;
        y += it.h;
        if (!it.layer) return;
        // Seção mais alta que a tela gruda pelo rodapé (top negativo), para que
        // todo o conteúdo seja lido antes de a próxima camada cobrir.
        var top = Math.min(0, vh - it.h);
        it.el.style.setProperty('--vs-top', top + 'px');
        var visibleTop = Math.max(0, it.h - vh);
        it.el.style.setProperty('--vs-origin', (visibleTop + Math.min(it.h, vh) * 0.5) + 'px');
        it.el.style.setProperty('--vs-scale', small ? '0.04' : '0.06');
      });
      update();
    }

    function update() {
      ticking = false;
      var cur = 0;
      for (var i = 0; i < items.length; i++) {
        var it = items[i];
        if (!it.layer) continue;
        var next = items[i + 1];
        var p = 0;
        if (next && it !== last && !reduce.matches) {
          var nt = next.el.getBoundingClientRect().top;
          p = clamp((vh - nt) / vh, 0, 1);
        }
        it.el.style.setProperty('--vs-p', p.toFixed(4));
      }
      // camada atual = última cujo topo já passou da metade da tela
      for (var k = 0; k < layers.length; k++) {
        if (layers[k].natural <= window.scrollY + vh * 0.5) cur = k;
      }
      var max = document.documentElement.scrollHeight - vh;
      var progress = max > 0 ? clamp(window.scrollY / max, 0, 1) : 0;
      meter.style.setProperty('--vs-total', progress.toFixed(4));
      bar.style.setProperty('--vs-total', progress.toFixed(4));
      var show = window.scrollY > vh * 0.35;
      index.classList.toggle('vs-show', show);
      if (!show) meter.classList.remove('vs-show');
      if (cur !== current) {
        current = cur;
        layers.forEach(function (l, n) {
          l.link.classList.toggle('vs-current', n === cur);
          l.link.classList.toggle('vs-done', n < cur);
          if (n === cur) l.link.setAttribute('aria-current', 'true');
          else l.link.removeAttribute('aria-current');
        });
        mN.textContent = pad(cur + 1);
        cN.textContent = pad(cur + 1);
        mL.textContent = '· ' + layers[cur].label;
        if (show) {
          meter.classList.add('vs-show');
          clearTimeout(st && st.mt);
          if (st) st.mt = setTimeout(function () { meter.classList.remove('vs-show'); }, 1800);
        }
      }
    }

    function onScroll() {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }
    var rt;
    function onResize() { clearTimeout(rt); rt = setTimeout(measure, 120); }

    st = { items: items, index: index, meter: meter, bar: bar, onScroll: onScroll, onResize: onResize };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize);
    if ('ResizeObserver' in window) {
      // conteúdo que abre/fecha (FAQ, cards expansíveis) muda a altura das seções
      st.ro = new ResizeObserver(onResize);
      sections.forEach(function (s) { st.ro.observe(s); });
    }
    measure();
  }

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  // Inicia depois da hidratação do Next e reage à navegação client-side.
  function boot() {
    setup();
    var main = document.getElementById('conteudo');
    if (main && 'MutationObserver' in window) {
      var last = location.pathname, t;
      new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(function () {
          if (location.pathname !== last || (isHome() && !st)) { last = location.pathname; setup(); }
        }, 150);
      }).observe(main, { childList: true });
    }
  }
  if (document.readyState === 'complete') setTimeout(boot, 60);
  else window.addEventListener('load', function () { setTimeout(boot, 60); });
})();
