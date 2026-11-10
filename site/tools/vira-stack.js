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

  function hydrated(n) {
    for (var k in n) if (k.indexOf('__reactFiber') === 0 || k.indexOf('__reactProps') === 0) return true;
    return false;
  }
  var retry = 0;

  function scan() {
    var pending = Array.prototype.some.call(document.querySelectorAll(SELECTOR), function (ol) {
      return !ol.hasAttribute('data-vs-deck') && !hydrated(ol);
    });
    if (pending) { if (retry++ < 100) setTimeout(scan, 100); return; }
    retry = 0;
    collapsibles();
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

  // Barra fixa de WhatsApp no celular: aparece depois do topo, some perto do formulário
  var WA = 'https://wa.me/5581979128073?text=' + encodeURIComponent('Olá, Thiago! Vim pelo site da VIRA Studio e quero conversar sobre um projeto.');
  function waBar() {
    if (document.querySelector('.v3-wa')) return;
    var a = document.createElement('a');
    a.className = 'v3-wa'; a.href = WA; a.target = '_blank'; a.rel = 'noopener noreferrer';
    a.setAttribute('data-cta', 'barra-whatsapp');
    a.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.4.1-.2 0-.3 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>Conversar no WhatsApp';
    document.body.appendChild(a);
    var tick = false;
    function upd() {
      tick = false;
      var form = document.querySelector('#contato form, form[class*="ProjectForm"]');
      var nearForm = form && form.getBoundingClientRect().top < window.innerHeight && form.getBoundingClientRect().bottom > 0;
      a.classList.toggle('on', window.scrollY > window.innerHeight * 0.6 && !nearForm);
    }
    window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true });
    upd();
  }

  // Investimento no celular: escopo recolhido atrás de "Ver o que está incluso"
  function collapsibles() {
    var lists = document.querySelectorAll('#investimento .Investment_scopeList__rYUeq, #investimento .Investment_tiers__91fbw');
    Array.prototype.forEach.call(lists, function (ul, n) {
      if (ul.hasAttribute('data-v3c')) return;
      ul.setAttribute('data-v3c', '');
      if (!ul.id) ul.id = 'v3-escopo-' + n;
      ul.classList.add('v3-collapsed');
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'v3-more';
      b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', ul.id);
      b.textContent = 'Ver o que está incluso';
      b.addEventListener('click', function () {
        var open = b.getAttribute('aria-expanded') !== 'true';
        b.setAttribute('aria-expanded', String(open));
        ul.classList.toggle('v3-collapsed', !open);
        b.textContent = open ? 'Fechar' : 'Ver o que está incluso';
      });
      ul.parentNode.insertBefore(b, ul);
    });
  }

  function boot() {
    (function tryWa(n) {
      var main = document.getElementById('conteudo');
      if (main && !hydrated(main) && n < 100) return setTimeout(function () { tryWa(n + 1); }, 100);
      waBar();
      collapsibles();
    })(0);
    scan();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    if ('MutationObserver' in window) {
      var t;
      new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(scan, 120);
      }).observe(document.getElementById('conteudo') || document.body, { childList: true });
    }
  }

  if (document.readyState === 'complete') setTimeout(boot, 60);
  else window.addEventListener('load', function () { setTimeout(boot, 60); });
})();
