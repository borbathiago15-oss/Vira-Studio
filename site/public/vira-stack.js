/* VIRA Studio · Cartões da construção
   Transforma a lista de etapas (Entender → Criar → Construir → Entregar) num
   baralho: cada cartão gruda no topo e o próximo sobe por cima; o de baixo recua
   um pouco. Funciona na Home e em /processo, inclusive em navegação sem recarregar.
   Só usa atributos data-* e variáveis CSS — nada que o React controle. */
(function () {
  'use strict';
  var SELECTOR = 'ol.Process_phases__7yR_E';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var decks = [];
  var ticking = false;

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  function scan() {
    decks = decks.filter(function (d) { return document.contains(d.el); });
    var lists = document.querySelectorAll(SELECTOR);
    for (var i = 0; i < lists.length; i++) {
      var ol = lists[i];
      if (ol.hasAttribute('data-vs-deck')) continue;
      var cards = Array.prototype.slice.call(ol.children).filter(function (n) { return n.tagName === 'LI'; });
      if (cards.length < 2) continue;
      ol.setAttribute('data-vs-deck', '');
      ol.style.setProperty('--vs-total-txt', '"' + cards.length + '"');
      cards.forEach(function (li, n) { li.style.setProperty('--vs-i', String(n)); });
      decks.push({ el: ol, cards: cards });
    }
    update();
  }

  function update() {
    ticking = false;
    if (reduce.matches) return;
    for (var d = 0; d < decks.length; d++) {
      var cards = decks[d].cards;
      for (var i = 0; i < cards.length; i++) {
        var cur = cards[i], next = cards[i + 1];
        var p = 0;
        if (next) {
          var a = cur.getBoundingClientRect();
          var b = next.getBoundingClientRect();
          // quanto o próximo cartão já cobriu o atual (0 = nada, 1 = encostou no topo)
          p = clamp(1 - (b.top - a.top) / Math.max(a.height, 1));
        }
        cur.style.setProperty('--vs-p', p.toFixed(3));
      }
    }
  }

  function onScroll() {
    if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
  }

  function boot() {
    scan();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    if ('MutationObserver' in window) {
      var t;
      new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(scan, 120);
      }).observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === 'complete') setTimeout(boot, 60);
  else window.addEventListener('load', function () { setTimeout(boot, 60); });
})();
