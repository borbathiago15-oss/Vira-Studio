/* VIRA Studio · HUD "Sistema montando"
   Painel em SVG com linha do tempo determinística: render(t) desenha o quadro
   do segundo t. O mesmo código roda ao vivo no site (loop) e é capturado
   quadro a quadro para gerar o vídeo — por isso nada aqui depende de relógio.
   Sem números de resultado inventados: só etapas e status. */
(function (global) {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var GOLD = '#d4af6a', GOLD_DIM = 'rgba(212,175,106,0.38)', GOLD_FAINT = 'rgba(212,175,106,0.12)';
  var TEXT = '#f5f5f5', MUTED = '#8a8a91', SURFACE = '#151518';
  var MONO = '"JetBrains Mono", ui-monospace, Menlo, monospace';
  var SANS = 'Montserrat, system-ui, sans-serif';
  var LOOP = 10;

  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function seg(t, a, b) { return clamp((t - a) / (b - a)); }
  function ease(p) { return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; }
  function out(p) { return 1 - Math.pow(1 - p, 3); }

  var VARIANTS = {
    sistema: {
      tag: 'VIRA // SISTEMA',
      lines: ['> mapeando a operação', '> estruturando os dados', '> conectando a IA'],
      status: ['Integração', 'Automação', 'IA aplicada'],
      phases: ['INICIANDO', 'DIAGNÓSTICO', 'MONTANDO', 'ONLINE']
    },
    ia: {
      tag: 'VIRA // IA',
      lines: ['> lendo os dados da operação', '> encontrando padrões', '> sugerindo a próxima ação'],
      status: ['Análise', 'Previsão', 'Alertas'],
      phases: ['CONECTANDO', 'ANALISANDO', 'APRENDENDO', 'ATIVA']
    }
  };
  var BARS = [0.42, 0.66, 0.5, 0.82, 0.7, 0.92];
  var LINE_PTS = [[0, 0.7], [0.18, 0.62], [0.34, 0.66], [0.5, 0.44], [0.66, 0.48], [0.82, 0.26], [1, 0.18]];

  function createPanel(container, opts) {
    opts = opts || {};
    var V = VARIANTS[opts.variant] || VARIANTS.sistema;
    var LINES = V.lines.map(function (txt, k) { return { txt: txt, at: 1 + k }; });
    var STATUS = V.status;
    var svg = el('svg', { viewBox: '0 0 600 600', role: 'img', 'aria-label': 'Animação: um sistema sendo montado — diagnóstico, dados e IA conectados.' });
    svg.style.width = '100%'; svg.style.height = '100%'; svg.style.display = 'block'; svg.style.overflow = 'visible';
    var defs = el('defs', {}, svg);
    var f = el('filter', { id: 'vhGlow', x: '-50%', y: '-50%', width: '200%', height: '200%' }, defs);
    el('feGaussianBlur', { stdDeviation: '6', result: 'b' }, f);
    var m = el('feMerge', {}, f); el('feMergeNode', { in: 'b' }, m); el('feMergeNode', { in: 'SourceGraphic' }, m);
    var rg = el('radialGradient', { id: 'vhCore' }, defs);
    el('stop', { offset: '0', 'stop-color': '#fff3d6' }, rg);
    el('stop', { offset: '0.35', 'stop-color': GOLD }, rg);
    el('stop', { offset: '1', 'stop-color': GOLD, 'stop-opacity': '0' }, rg);
    var lg = el('linearGradient', { id: 'vhFill', x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
    el('stop', { offset: '0', 'stop-color': GOLD, 'stop-opacity': '0.35' }, lg);
    el('stop', { offset: '1', 'stop-color': GOLD, 'stop-opacity': '0' }, lg);

    var root = el('g', {}, svg);

    // grade de fundo
    var grid = el('g', { stroke: GOLD_FAINT, 'stroke-width': 1 }, root);
    for (var gx = 0; gx <= 600; gx += 40) el('line', { x1: gx, y1: 0, x2: gx, y2: 600 }, grid);
    for (var gy = 0; gy <= 600; gy += 40) el('line', { x1: 0, y1: gy, x2: 600, y2: gy }, grid);

    // cantoneiras do HUD
    var corners = el('g', { stroke: GOLD, 'stroke-width': 2, fill: 'none', 'stroke-linecap': 'round' }, root);
    var cornerPaths = [
      'M8 48 V8 H48', 'M552 8 H592 V48', 'M592 552 V592 H552', 'M48 592 H8 V552'
    ].map(function (d) { return el('path', { d: d, pathLength: 1, 'stroke-dasharray': 1 }, corners); });

    // ---------- anel
    var RX = 300, RY = 168;
    var ring = el('g', {}, root);
    var halo = el('circle', { cx: RX, cy: RY, r: 70, fill: 'url(#vhCore)' }, ring);
    var core = el('circle', { cx: RX, cy: RY, r: 16, fill: '#fff3d6', filter: 'url(#vhGlow)' }, ring);
    var r1 = el('circle', { cx: RX, cy: RY, r: 54, fill: 'none', stroke: GOLD, 'stroke-width': 1.5 }, ring);
    var r2 = el('g', {}, ring);
    el('circle', { cx: RX, cy: RY, r: 86, fill: 'none', stroke: GOLD_DIM, 'stroke-width': 1, 'stroke-dasharray': '2 6' }, r2);
    el('path', { d: arc(RX, RY, 86, -40, 60), fill: 'none', stroke: GOLD, 'stroke-width': 3, 'stroke-linecap': 'round' }, r2);
    el('path', { d: arc(RX, RY, 86, 150, 210), fill: 'none', stroke: GOLD, 'stroke-width': 3, 'stroke-linecap': 'round' }, r2);
    var ticks = el('g', { stroke: GOLD, 'stroke-width': 1.5 }, ring);
    for (var i = 0; i < 72; i++) {
      var a = i / 72 * Math.PI * 2, L = i % 6 === 0 ? 12 : 5;
      el('line', { x1: RX + Math.cos(a) * 112, y1: RY + Math.sin(a) * 112, x2: RX + Math.cos(a) * (112 + L), y2: RY + Math.sin(a) * (112 + L), opacity: i % 6 === 0 ? 1 : 0.45 }, ticks);
    }
    var orbit = el('g', {}, ring);
    el('ellipse', { cx: RX, cy: RY, rx: 140, ry: 44, fill: 'none', stroke: GOLD_DIM, 'stroke-width': 1 }, orbit);
    var sat = el('circle', { cx: RX + 140, cy: RY, r: 4, fill: GOLD, filter: 'url(#vhGlow)' }, orbit);
    var tagL = el('text', { x: 40, y: 56, fill: GOLD, 'font-family': MONO, 'font-size': 13, 'letter-spacing': 2 }, root);
    tagL.textContent = V.tag;
    var tagR = el('text', { x: 560, y: 56, fill: MUTED, 'font-family': MONO, 'font-size': 13, 'text-anchor': 'end', 'letter-spacing': 2 }, root);

    // ---------- terminal
    var term = el('g', {}, root);
    el('rect', { x: 40, y: 318, width: 520, height: 104, rx: 10, fill: SURFACE, stroke: GOLD_DIM }, term);
    var termLines = LINES.map(function (ln, k) {
      var t = el('text', { x: 60, y: 350 + k * 28, fill: TEXT, 'font-family': MONO, 'font-size': 16 }, term);
      var ok = el('text', { x: 540, y: 350 + k * 28, fill: GOLD, 'font-family': MONO, 'font-size': 14, 'text-anchor': 'end', 'letter-spacing': 1 }, term);
      ok.textContent = 'OK';
      return { t: t, ok: ok, txt: ln.txt, at: ln.at };
    });
    var cursor = el('rect', { width: 9, height: 17, fill: GOLD }, term);

    // ---------- painel (3 cartões)
    var dash = el('g', {}, root);
    var cards = [40, 220, 400].map(function (x) {
      var g = el('g', {}, dash);
      el('rect', { x: x, y: 440, width: 160, height: 124, rx: 10, fill: SURFACE, stroke: GOLD_DIM }, g);
      return g;
    });
    // barras
    var bars = BARS.map(function (h, k) {
      return el('rect', { x: 56 + k * 22, width: 14, rx: 2, fill: k === BARS.length - 1 ? GOLD : GOLD_DIM }, cards[0]);
    });
    el('line', { x1: 52, y1: 548, x2: 188, y2: 548, stroke: GOLD_DIM }, cards[0]);
    // linha
    var pts = LINE_PTS.map(function (p) { return [236 + p[0] * 128, 460 + p[1] * 84]; });
    var dLine = 'M' + pts.map(function (p) { return p.join(' '); }).join(' L');
    var area = el('path', { d: dLine + ' L364 548 L236 548 Z', fill: 'url(#vhFill)' }, cards[1]);
    var line = el('path', { d: dLine, fill: 'none', stroke: GOLD, 'stroke-width': 2.5, 'stroke-linejoin': 'round', pathLength: 1, 'stroke-dasharray': 1 }, cards[1]);
    var dot = el('circle', { r: 4.5, fill: '#fff3d6', filter: 'url(#vhGlow)' }, cards[1]);
    // status
    var stats = STATUS.map(function (s, k) {
      var y = 474 + k * 30;
      var box = el('rect', { x: 414, y: y - 12, width: 16, height: 16, rx: 4, fill: 'none', stroke: GOLD_DIM }, cards[2]);
      var chk = el('path', { d: 'M418 ' + (y - 4) + ' l4 4 l7 -8', fill: 'none', stroke: GOLD, 'stroke-width': 2.2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', pathLength: 1, 'stroke-dasharray': 1 }, cards[2]);
      var tx = el('text', { x: 440, y: y + 1, fill: TEXT, 'font-family': SANS, 'font-size': 14, 'font-weight': 600 }, cards[2]);
      tx.textContent = s;
      return { box: box, chk: chk, tx: tx };
    });

    // linha de varredura
    var scan = el('rect', { x: 0, width: 600, height: 2, fill: GOLD, opacity: 0.18 }, root);

    container.appendChild(svg);

    function render(T, mode) {
      var loop = mode !== 'once';
      var t = loop ? T % LOOP : T;
      var fadeOut = loop ? 1 - seg(t, 9.2, 10) : 1;

      cornerPaths.forEach(function (p, k) { p.setAttribute('stroke-dashoffset', 1 - ease(seg(t, 0.05 + k * 0.08, 0.6 + k * 0.08))); });
      grid.setAttribute('opacity', 0.9 * out(seg(t, 0, 0.8)));

      var ri = out(seg(t, 0.2, 1.2));
      ring.setAttribute('opacity', ri * (0.25 + 0.75 * fadeOut));
      ring.setAttribute('transform', 'translate(' + RX + ' ' + RY + ') scale(' + (0.8 + 0.2 * ri) + ') translate(' + (-RX) + ' ' + (-RY) + ')');
      var pulse = 1 + 0.12 * Math.sin(T * 2.4);
      core.setAttribute('r', 14 * pulse);
      halo.setAttribute('r', 64 + 10 * Math.sin(T * 2.4));
      r2.setAttribute('transform', 'rotate(' + (T * 24) + ' ' + RX + ' ' + RY + ')');
      ticks.setAttribute('transform', 'rotate(' + (-T * 6) + ' ' + RX + ' ' + RY + ')');
      r1.setAttribute('stroke-opacity', 0.55 + 0.45 * Math.abs(Math.sin(T * 1.2)));
      var oa = T * 1.3;
      sat.setAttribute('cx', RX + Math.cos(oa) * 140);
      sat.setAttribute('cy', RY + Math.sin(oa) * 44);

      var pi = t < 1 ? 0 : t < 4 ? 1 : t < 6.4 ? 2 : 3;
      tagR.textContent = V.phases[pi];
      tagR.setAttribute('fill', pi === 3 ? GOLD : MUTED);
      tagL.setAttribute('opacity', out(seg(t, 0.3, 0.9)));
      tagR.setAttribute('opacity', out(seg(t, 0.3, 0.9)));

      // terminal
      term.setAttribute('opacity', out(seg(t, 0.7, 1.1)) * fadeOut);
      var cx = 60, cy = 350, showCursor = false;
      termLines.forEach(function (ln, k) {
        var p = seg(t, ln.at, ln.at + 0.75);
        var n = Math.round(ln.txt.length * p);
        ln.t.textContent = ln.txt.slice(0, n);
        ln.ok.setAttribute('opacity', seg(t, ln.at + 0.8, ln.at + 0.95));
        if (t >= ln.at - 0.2) { cx = 60 + n * 9.6 + 2; cy = 350 + k * 28; showCursor = p < 1 || k === termLines.length - 1; }
      });
      cursor.setAttribute('x', cx); cursor.setAttribute('y', cy - 14);
      cursor.setAttribute('opacity', showCursor && Math.floor(T * 2.5) % 2 === 0 ? 1 : 0);

      // painel
      cards.forEach(function (g, k) {
        var p = out(seg(t, 3.8 + k * 0.25, 4.5 + k * 0.25));
        g.setAttribute('opacity', p * fadeOut);
        g.setAttribute('transform', 'translate(0 ' + (16 * (1 - p)) + ')');
      });
      bars.forEach(function (b, k) {
        var p = out(seg(t, 4.2 + k * 0.1, 5.0 + k * 0.1));
        var h = BARS[k] * 84 * p * (1 + 0.04 * Math.sin(T * 1.6 + k));
        b.setAttribute('y', 548 - h); b.setAttribute('height', Math.max(h, 0.01));
      });
      var lp = ease(seg(t, 4.6, 5.9));
      line.setAttribute('stroke-dashoffset', 1 - lp);
      area.setAttribute('opacity', seg(t, 5.4, 6.2));
      var L = line.getTotalLength ? line.getTotalLength() : 0;
      if (L) { var pt = line.getPointAtLength(L * lp); dot.setAttribute('cx', pt.x); dot.setAttribute('cy', pt.y); }
      dot.setAttribute('opacity', lp > 0.02 ? 1 : 0);
      stats.forEach(function (s, k) {
        var p = seg(t, 5.0 + k * 0.4, 5.4 + k * 0.4);
        s.chk.setAttribute('stroke-dashoffset', 1 - out(p));
        s.box.setAttribute('stroke', p > 0.5 ? GOLD : GOLD_DIM);
        s.tx.setAttribute('opacity', 0.45 + 0.55 * p);
      });

      var sy = (T * 120) % 720 - 60;
      scan.setAttribute('y', sy);
    }

    return { svg: svg, render: render, loop: LOOP };
  }

  function arc(cx, cy, r, a0, a1) {
    var p = function (a) { a = a * Math.PI / 180; return [cx + Math.cos(a) * r, cy + Math.sin(a) * r]; };
    var s = p(a0), e = p(a1);
    return 'M' + s[0] + ' ' + s[1] + ' A' + r + ' ' + r + ' 0 ' + (a1 - a0 > 180 ? 1 : 0) + ' 1 ' + e[0] + ' ' + e[1];
  }

  // ---------- montagem automática no site: <div data-vira-hud></div>
  function autoMount() {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var hosts = document.querySelectorAll('[data-vira-hud]:not([data-vira-hud-on])');
    Array.prototype.forEach.call(hosts, function (host) {
      host.setAttribute('data-vira-hud-on', '');
      var panel = createPanel(host, { variant: host.getAttribute('data-vira-hud') });
      if (reduce) { panel.render(7.5, 'once'); return; }
      var visible = false, start = null, raf = 0;
      function frame(now) {
        if (start === null) start = now;
        panel.render((now - start) / 1000);
        raf = visible ? requestAnimationFrame(frame) : 0;
      }
      panel.render(0);
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (ents) {
          visible = ents[0].isIntersecting;
          if (visible && !raf) raf = requestAnimationFrame(frame);
        }, { threshold: 0.15 }).observe(host);
      } else { visible = true; raf = requestAnimationFrame(frame); }
    });
  }

  // ---------- site: insere os painéis na Home (topo e Tecnologia + IA)
  function siteMount() {
    var p = location.pathname;
    if (p !== '/' && p !== '/index.html') { document.documentElement.removeAttribute('data-vira-hero'); return; }
    var hero = document.querySelector('section.Hero_hero__MpeZv');
    if (hero && !hero.querySelector('[data-vira-hud]')) {
      var h = document.createElement('div');
      h.className = 'vh-host vh-hero';
      h.setAttribute('data-vira-hud', 'sistema');
      hero.appendChild(h);
      document.documentElement.setAttribute('data-vira-hero', '');
    }
    var tec = document.querySelector('#tecnologia .container');
    if (tec && !tec.querySelector('[data-vira-hud]')) {
      var k = document.createElement('div');
      k.className = 'vh-host vh-tec';
      k.setAttribute('data-vira-hud', 'ia');
      tec.appendChild(k);
    }
    autoMount();
  }

  global.ViraHUD = { createPanel: createPanel, autoMount: autoMount, siteMount: siteMount, LOOP: LOOP };

  if (!global.__VIRA_HUD_CAPTURE__ && document.documentElement) {
    var boot = function () {
      siteMount();
      if ('MutationObserver' in window) {
        var tm;
        new MutationObserver(function () { clearTimeout(tm); tm = setTimeout(siteMount, 150); })
          .observe(document.getElementById('conteudo') || document.body, { childList: true });
      }
    };
    if (document.readyState === 'complete') setTimeout(boot, 80);
    else window.addEventListener('load', function () { setTimeout(boot, 80); });
  }
})(window);
