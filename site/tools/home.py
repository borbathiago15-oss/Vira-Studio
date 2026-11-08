"""Reorganiza a Home do virastudio.uk (HTML + payload Flight juntos, para a hidratação bater).

Nova ordem: Hero · faixa · Soluções · Cases · Como construímos (deck) · Tecnologia+IA ·
Investimento · Dúvidas · Contato. Saem da Home: Manifesto, Como pensamos, Sobre
(continuam em /processo e /sobre).

Uso: python3 home.py <pasta-do-site>
"""
import sys, re, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import flight

ROOT = pathlib.Path(sys.argv[1])
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|\'[^\']*\'|[^>])*?)(/?)>|<!--.*?-->', re.S)

def children(h, start, end):
    """Filhos diretos (start, end) entre start e end, ignorando texto."""
    out, depth, cur = [], 0, None
    for m in TAG.finditer(h, start, end):
        if m.group(0).startswith('<!--'):
            continue
        close, name, selfc = m.group(1), m.group(2).lower(), m.group(4)
        if close:
            depth -= 1
            if depth == 0:
                out.append((cur, m.end()))
        elif name in VOID or selfc:
            if depth == 0:
                out.append((m.start(), m.end()))
        else:
            if depth == 0:
                cur = m.start()
            depth += 1
    return out

def element_at(h, start):
    """(start, end) do elemento que começa em start."""
    m = TAG.match(h, start)
    name = m.group(2)
    end = h.index('</' + name + '>', start)  # placeholder, refinado abaixo
    depth = 0
    for t in TAG.finditer(h, start):
        if t.group(0).startswith('<!--'):
            continue
        if t.group(2).lower() in VOID or t.group(4):
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return start, t.end()

# ---------------- textos novos
OLD_T1, NEW_T1 = 'Da ideia', 'Como construímos'
OLD_T2, NEW_T2 = 'ao resultado.', 'a sua solução.'
OLD_LEAD = 'Quatro fases que se repetem em todo projeto — da marca ao sistema. O que muda é a profundidade de cada etapa.'
NEW_LEAD = 'Quatro etapas, sempre nesta ordem. Do diagnóstico da sua operação ao sistema funcionando — o que muda é a profundidade de cada uma.'
DROP_CLASSES = ('Process_detailed__IuewV', 'Process_bySolution__F2hu7')

def edit_processo_html(chunk):
    chunk = chunk.replace(f'<span>{OLD_T1}</span>', f'<span>{NEW_T1}</span>', 1)
    chunk = chunk.replace(f'<span>{OLD_T2}</span>', f'<span>{NEW_T2}</span>', 1)
    assert OLD_LEAD in chunk
    chunk = chunk.replace(OLD_LEAD, NEW_LEAD, 1)
    for cls in DROP_CLASSES:
        i = chunk.index(cls)
        s = chunk.rfind('<div', 0, i)
        a, b = element_at(chunk, s)
        chunk = chunk[:a] + chunk[b:]
    return chunk

def edit_processo_flight(body, R):
    o = json.loads(body)
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    s = s.replace(f'"{OLD_T1}"', f'"{NEW_T1}"').replace(f'"{OLD_T2}"', f'"{NEW_T2}"').replace(OLD_LEAD, NEW_LEAD)
    o = json.loads(s)
    container = o[3]['children'][1]          # div.container
    kids = container[3]['children']
    def drop(k):
        if isinstance(k, str) and k.startswith('$L') and k[2:] in R:
            return any(c in R[k[2:]][2][:400] for c in DROP_CLASSES)
        return isinstance(k, list) and len(k) == 4 and any(c in str(k[3].get('className', '')) for c in DROP_CLASSES)
    container[3]['children'] = [k for k in kids if not drop(k)]
    assert len(container[3]['children']) == len(kids) - 2, 'blocos do processo não encontrados'
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))

# ---------------- ordem
# chaves: id da seção / 'hero' / 'marquee'
ORDER = ['hero', 'marquee', 'solucoes', 'cases', 'processo', 'tecnologia', 'investimento', 'faq', 'contato', 'jsonld']

def key_html(chunk):
    m = re.match(r'<(\w+)([^>]*)>', chunk)
    tag, attrs = m.group(1), m.group(2)
    idm = re.search(r'\bid="([^"]+)"', attrs)
    if tag == 'script':
        return 'jsonld'
    if 'Hero_hero' in attrs:
        return 'hero'
    if 'Marquee_wrap' in attrs:
        return 'marquee'
    return idm.group(1) if idm else '?'

def run():
    txt_p, html_p = ROOT / 'index.txt', ROOT / 'index.html'
    payload = txt_p.read_text(encoding='utf-8')
    rows = flight.parse(payload)
    R = {r[0]: r for r in rows}

    # --- flight: lista de filhos da página (linha que contém a seção cases)
    page_row = next(r for r in rows if r[1] == 'J' and '"id":"cases"' in r[2] and r[2].startswith('["$","$1"'))
    o = json.loads(page_row[2])
    kids = o[3]['children'][0]

    def key_flight(k):
        if isinstance(k, str):
            body = R[k[2:]][2]
            m = re.search(r'"id":"([^"]+)"', body[:200])
            if m:
                return m.group(1)
            if body.startswith('["$","script"'):
                return 'jsonld'
            if body.startswith('["$","$L'):          # componente cliente (Tecnologia+IA)
                return 'tecnologia'
            if body.startswith('I['):
                return 'hero'
            return '?'
        if isinstance(k[1], str) and k[1].startswith('$L') and k is kids[0]:
            return 'hero'
        if k[1] == 'section':
            return k[3].get('id')
        if 'Marquee_wrap' in k[3].get('className', ''):
            return 'marquee'
        return '?'

    fk = {key_flight(k): k for k in kids}
    missing = [k for k in ORDER if k not in fk]
    assert not missing, ('flight sem', missing, list(fk))
    o[3]['children'][0] = [fk[k] for k in ORDER]
    page_row[2] = json.dumps(o, ensure_ascii=False, separators=(',', ':'))

    pr = next(r for r in rows if r[1] == 'J' and r[2].startswith('["$","section",null,{"id":"processo"'))
    pr[2] = edit_processo_flight(pr[2], R)
    new_payload = flight.serialize(rows)

    # --- HTML
    h = html_p.read_text(encoding='utf-8')
    ms = h.index('<main'); ms = h.index('>', ms) + 1
    me = h.index('</main>')
    parts = children(h, ms, me)
    hk = {key_html(h[a:b]): h[a:b] for a, b in parts}
    missing = [k for k in ORDER if k not in hk]
    assert not missing, ('html sem', missing, list(hk))
    hk['processo'] = edit_processo_html(hk['processo'])
    lead = h[ms:parts[0][0]]
    tail = h[parts[-1][1]:me]           # marcadores de Suspense do React (<!--$--><!--/$-->)
    new_main = lead + ''.join(hk[k] for k in ORDER) + tail
    h = h[:ms] + new_main + h[me:]
    h = flight.to_html(h, new_payload)

    assert flight.from_html(h) == new_payload
    html_p.write_text(h, encoding='utf-8')
    txt_p.write_text(new_payload, encoding='utf-8')
    print('Home reorganizada:', ' · '.join(ORDER))
    print('Removidas da Home:', sorted(set(hk) - set(ORDER)))

run()
