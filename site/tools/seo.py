"""Ajustes de SEO sobre o build estático do virastudio.uk.

- og:image / og:site_name / twitter:* completos em todas as páginas indexáveis
- sitemap.xml com lastmod da data de geração
- llms.txt gerado a partir dos títulos e descrições reais das páginas (nada inventado)
- 404 sem canonical (é noindex)

Uso: python3 seo.py <pasta-do-site> [AAAA-MM-DD]
"""
import sys, re, html, pathlib, datetime

ROOT = pathlib.Path(sys.argv[1])
DAY = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
BASE = 'https://virastudio.uk'
OG_IMG = BASE + '/brand/og-image.jpg'
OG_ALT = 'VIRA Studio — Sua operação, com inteligência.'

def meta(head, attr, key):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(key)), head)
    return html.unescape(m.group(1)) if m else None

def esc(s):
    return html.escape(s, quote=True)

pages = []
for f in sorted(ROOT.rglob('index.html')):
    h = f.read_text(encoding='utf-8')
    i = h.index('</head>')
    head = h[:i]
    if 'noindex' in (meta(head, 'name', 'robots') or ''):
        continue
    title = html.unescape(re.search(r'<title>(.*?)</title>', head).group(1))
    desc = meta(head, 'name', 'description') or ''
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', head).group(1)
    ogt = meta(head, 'property', 'og:title') or title
    ogd = meta(head, 'property', 'og:description') or desc
    add = []
    if not meta(head, 'property', 'og:image'):
        add += [f'<meta property="og:image" content="{OG_IMG}"/>',
                '<meta property="og:image:width" content="1200"/>',
                '<meta property="og:image:height" content="630"/>',
                f'<meta property="og:image:alt" content="{esc(OG_ALT)}"/>']
    if not meta(head, 'property', 'og:site_name'):
        add.append('<meta property="og:site_name" content="VIRA Studio"/>')
    if not meta(head, 'property', 'og:locale'):
        add.append('<meta property="og:locale" content="pt_BR"/>')
    if not meta(head, 'property', 'og:type'):
        add.append('<meta property="og:type" content="website"/>')
    # twitter:title/description genéricos nas internas → os da própria página
    new_head = re.sub(r'<meta name="twitter:title" content="[^"]*"/>', f'<meta name="twitter:title" content="{esc(ogt)}"/>', head)
    new_head = re.sub(r'<meta name="twitter:description" content="[^"]*"/>', f'<meta name="twitter:description" content="{esc(ogd)}"/>', new_head)
    if add or new_head != head:
        h = new_head + ''.join(add) + h[i:]
        f.write_text(h, encoding='utf-8')
    pages.append({'url': canon if canon.startswith('http') else BASE + canon, 'title': title, 'desc': desc})

# 404: noindex não deve declarar canonical
p404 = ROOT / '404.html'
if p404.exists():
    t = p404.read_text(encoding='utf-8')
    t2 = re.sub(r'<link rel="canonical" href="[^"]*"/>', '', t)
    if t2 != t:
        p404.write_text(t2, encoding='utf-8')

# sitemap: atualiza lastmod
sm = ROOT / 'sitemap.xml'
s = sm.read_text(encoding='utf-8')
s = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{DAY}</lastmod>', s)
sm.write_text(s, encoding='utf-8')

# llms.txt
def short(t):
    return t.replace(' | VIRA Studio', '').strip()

by = {p['url'].replace(BASE, '') or '/': p for p in pages}
def line(path):
    p = by.get(path)
    return f"- [{short(p['title'])}]({p['url']}): {p['desc']}" if p else None

home = by['/']
out = [
    '# VIRA Studio',
    '',
    f"> {home['desc']}",
    '',
    'Estúdio brasileiro que cria sistemas com inteligência artificial aplicada à operação das empresas, '
    'além da marca e do site que apresentam o negócio. Atendimento em todo o Brasil, em português.',
    '',
    '- Site: https://virastudio.uk',
    '- E-mail: thiago@virastudio.uk',
    '- WhatsApp: +55 81 97912-8073',
    '- Instagram: https://www.instagram.com/virastudiobr',
    '',
    '## Soluções',
]
out += [l for l in (line('/digital/'), line('/web/'), line('/brand/')) if l]
out += ['', '## Cases']
out += [line(k) for k in sorted(by) if k.startswith('/cases/') and k != '/cases/']
out += ['', '## Sobre e contato']
out += [l for l in (line('/cases/'), line('/processo/'), line('/sobre/'), line('/contato/')) if l]
(ROOT / 'llms.txt').write_text('\n'.join(out) + '\n', encoding='utf-8')
print(f'{len(pages)} páginas indexáveis · sitemap lastmod {DAY} · llms.txt com {len(out)} linhas')
