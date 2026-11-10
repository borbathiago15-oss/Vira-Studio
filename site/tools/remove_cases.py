"""Tira cases do site (HTML + payload do React + dados do bundle) mantendo a hidratação consistente.

Uso: python3 remove_cases.py <pasta-do-site> slug1 [slug2 ...]
"""
import sys, re, json, pathlib, shutil
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import flight

ROOT = pathlib.Path(sys.argv[1])
SLUGS = sys.argv[2:]
TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|\'[^\']*\'|[^>])*?)(/?)>|<!--.*?-->', re.S)
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
log = []

def element_end(h, start):
    depth = 0
    for t in TAG.finditer(h, start):
        if t.group(0).startswith('<!--') or t.group(2).lower() in VOID or t.group(4):
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return t.end()

def remove_enclosing(h, needle, tags=('li', 'article')):
    """Remove o menor <li>/<article> que contém cada ocorrência de needle."""
    n = 0
    while True:
        i = h.find(needle)
        if i < 0:
            return h, n
        best = None
        pos = i
        while True:
            cands = [h.rfind('<' + t + ' ', 0, pos) for t in tags] + [h.rfind('<' + t + '>', 0, pos) for t in tags]
            s = max(cands)
            if s < 0:
                break
            e = element_end(h, s)
            if e and e > i:
                best = (s, e)
                break
            pos = s
        if not best:
            raise SystemExit(f'sem elemento envolvente para {needle!r}')
        h = h[:best[0]] + h[best[1]:]
        n += 1

def drop_flight(obj, bad_refs=()):
    """Remove elementos cujo key ou href aponta para um slug removido."""
    def bad(el):
        if isinstance(el, str) and el in bad_refs:
            return True
        if not (isinstance(el, list) and len(el) == 4 and el[0] == '$'):
            return False
        key, props = el[2], el[3] if isinstance(el[3], dict) else {}
        if isinstance(key, str) and any(key == 'case-' + s for s in SLUGS):
            return True
        s = json.dumps(props, ensure_ascii=False)
        return any(f'"/cases/{x}"' in s or f'"slug":"{x}"' in s for x in SLUGS) and el[1] in ('li', 'article') or \
               (isinstance(props.get('item'), dict) and props['item'].get('slug') in SLUGS)
    def walk(n):
        if isinstance(n, list):
            if n and n[0] == '$' and len(n) == 4:
                if isinstance(n[3], dict):
                    for k, v in list(n[3].items()):
                        n[3][k] = walk(v)
                return n
            return [walk(x) for x in n if not bad(x)]
        if isinstance(n, dict):
            return {k: walk(v) for k, v in n.items()}
        return n
    return walk(obj)

WALL_SWAP = [
    (('src="/cases/sistemas/suprimentos-modo-tv.webp"', '{src:"/cases/sistemas/suprimentos-modo-tv.webp",w:1440,h:900}'),
     ('src="/cases/sistemas/inteligencia-financeiro.webp"', '{src:"/cases/sistemas/inteligencia-financeiro.webp",w:1440,h:900}')),
    (('src="/cases/sistemas/suprimentos-painel.webp"', '{src:"/cases/sistemas/suprimentos-painel.webp",w:1440,h:900}'),
     ('src="/cases/sistemas/inteligencia-pdca.webp"', '{src:"/cases/sistemas/inteligencia-pdca.webp",w:1440,h:900}')),
    (('width="390" height="844" decoding="async" data-nimg="1" class="HeroWall_img__wSSuY" style="color:transparent" src="/cases/sistemas/facilities-app.webp"',
      '{src:"/cases/sistemas/facilities-app.webp",w:390,h:844,phone:!0}'),
     ('width="620" height="1348" decoding="async" data-nimg="1" class="HeroWall_img__wSSuY" style="color:transparent" src="/cases/camila-luz-mobile.webp"',
      '{src:"/cases/camila-luz-mobile.webp",w:620,h:1348,phone:!0}')),
]
for js in ROOT.glob('_next/static/chunks/app/page-*.js'):
    t = js.read_text(encoding='utf-8')
    if 'HeroWall' in t or 'suprimentos-modo-tv' in t:
        for a, b in WALL_SWAP:
            t = t.replace(a[1], b[1])
        js.write_text(t, encoding='utf-8')
        log.append(f'parede do topo: telas trocadas em {js.name}')

# 1) dados do bundle (vitrine, grade de cases): filtra o array de cases
for js in ROOT.glob('_next/static/chunks/*.js'):
    t = js.read_text(encoding='utf-8')
    if 'r=["inteligencia-operacional"' in t and ';i.sort((e,a)=>r.indexOf' in t:
        cond = '&&'.join(f'"{s}"!==e.slug' for s in SLUGS)
        t = t.replace(';i.sort((e,a)=>r.indexOf', f';i=i.filter(e=>{cond});i.sort((e,a)=>r.indexOf', 1)
        js.write_text(t, encoding='utf-8')
        log.append(f'bundle filtrado: {js.name}')

# 2) páginas
for html_p in sorted(ROOT.rglob('*.html')):
    rel = html_p.relative_to(ROOT).as_posix()
    if any(rel.startswith(f'cases/{s}/') for s in SLUGS):
        continue
    h = html_p.read_text(encoding='utf-8')
    if not any(f'/cases/{s}' in h or f'Ver {name}' in h or 'sistemas/suprimentos-' in h or 'sistemas/facilities-' in h for s in SLUGS for name in ('Gestão de Suprimentos', 'Gestão de Facilities')):
        continue
    orig = h
    # payload do React
    payload = flight.from_html(h)
    rows = flight.parse(payload)
    changed = False
    # linhas que SÃO um card de case removido viram referências a cortar ("$2d" / "$L2d")
    bad_ids = []
    for r in rows:
        if r[1] == 'J' and r[2].startswith('["$"'):
            try:
                el = json.loads(r[2])
            except Exception:
                continue
            if isinstance(el, list) and len(el) == 4 and isinstance(el[2], str) and any(el[2] == 'case-' + s for s in SLUGS):
                bad_ids.append(r[0])
    bad_refs = {p + i for i in bad_ids for p in ('$', '$L')}
    for r in rows:
        if r[1] == 'J' and bad_refs and any(('"' + ref + '"') in r[2] for ref in bad_refs):
            o2 = drop_flight(json.loads(r[2]), bad_refs)
            new = json.dumps(o2, ensure_ascii=False, separators=(',', ':'))
            if new != r[2]:
                r[2] = new; changed = True
    for r in rows:
        if r[1] == 'J' and any(f'/cases/{s}' in r[2] or f'case-{s}' in r[2] for s in SLUGS):
            o = json.loads(r[2])
            o2 = drop_flight(o)
            new = json.dumps(o2, ensure_ascii=False, separators=(',', ':'))
            if new != r[2]:
                r[2] = new; changed = True
    rows = [r for r in rows if r[0] not in bad_ids]
    new_payload = flight.serialize(rows)
    # HTML
    total = 0
    for s in SLUGS:
        h, n = remove_enclosing(h, f'href="/cases/{s}/"')
        total += n
    # slides da vitrine (Home) com imagens dos cases removidos
    for img in ('suprimentos-', 'facilities-'):
        pos = 0
        while True:
            m = re.compile(r'src="/cases/sistemas/' + img).search(h, pos)
            if not m:
                break
            s = h.rfind('<div class="Showcase_slide__k0asx', 0, m.start())
            e = element_end(h, s) if s >= 0 else -1
            if s < 0 or e < m.start():
                pos = m.end()          # fora da vitrine (ex.: parede do topo)
                continue
            h = h[:s] + h[e:]
            total += 1
            pos = s
    # parede do topo (lista própria no bundle da Home): troca as telas por outras já públicas
    for a, b in WALL_SWAP:
        h = h.replace(a[0], b[0])

    # bolinhas da vitrine (Home)
    for name in ('Gestão de Suprimentos', 'Gestão de Facilities'):
        pat = re.compile(r'<button type="button" class="Showcase_dot__kjb0i[^"]*"[^>]*aria-label="Ver ' + name + r'"[^>]*>.*?</button>', re.S)
        h, n = pat.subn('', h)
        total += n
    if changed:
        h = flight.to_html(h, new_payload)
        txt = html_p.with_name('index.txt') if html_p.name == 'index.html' else None
        if txt and txt.exists():
            txt.write_text(new_payload, encoding='utf-8')
    if h != orig:
        html_p.write_text(h, encoding='utf-8')
        log.append(f'{rel}: {total} elementos HTML removidos, payload {"alterado" if changed else "igual"}')

# 3) páginas dos cases → fora; redirecionamento para /cases/
for s in SLUGS:
    d = ROOT / 'cases' / s
    if d.exists():
        shutil.rmtree(d)
        log.append(f'removida a página /cases/{s}/')
red = ROOT / '_redirects'
lines = red.read_text().splitlines() if red.exists() else []
for s in SLUGS:
    for src in (f'/cases/{s}', f'/cases/{s}/'):
        rule = f'{src} /cases/ 301'
        if rule not in lines:
            lines.append(rule)
red.write_text('\n'.join(lines) + '\n')

# imagens dos cases removidos
for s in SLUGS:
    pref = s.replace('gestao-', '')
    for f in (ROOT / 'cases' / 'sistemas').glob(pref + '-*'):
        f.unlink(); log.append(f'imagem removida: {f.name}')

# 4) sitemap
sm = ROOT / 'sitemap.xml'
t = sm.read_text()
for s in SLUGS:
    t = re.sub(r'<url>\s*<loc>https://virastudio\.uk/cases/' + s + r'/</loc>.*?</url>\s*', '', t, flags=re.S)
sm.write_text(t)

print('\n'.join(log))
left = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.html', '.txt', '.xml')
        and any(f'/cases/{s}' in p.read_text(encoding='utf-8', errors='ignore') for s in SLUGS)]
print('ainda citam os slugs:', left or 'nenhum')
