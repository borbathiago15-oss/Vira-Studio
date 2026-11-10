"""Insere seções novas na Home (HTML + payload do React gerados da MESMA árvore, para a hidratação bater).

Uso: python3 add_sections.py <pasta-do-site>
"""
import sys, re, json, html, pathlib
from html.parser import HTMLParser
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import flight

ROOT = pathlib.Path(sys.argv[1])
VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source'}
ATTR = {'class': 'className', 'for': 'htmlFor', 'tabindex': 'tabIndex', 'srcset': 'srcSet', 'viewbox': 'viewBox'}

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ['root', {}, []]; self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = [tag, dict(attrs), []]
        self.stack[-1][2].append(n)
        if tag not in VOID:
            self.stack.append(n)
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack[-1][0] != tag:
            self.stack.pop()
        self.stack.pop()
    def handle_data(self, d):
        if d.strip() == '':
            return                     # sem nós de espaço em branco (JSX não teria)
        d = re.sub(r'\s+', ' ', d)
        self.stack[-1][2].append(d)

TAGRE = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|\'[^\']*\'|[^>])*?)(/?)>|<!--.*?-->', re.S)
def element_end(h, start):
    depth = 0
    for t in TAGRE.finditer(h, start):
        if t.group(0).startswith('<!--') or t.group(2).lower() in VOID or t.group(4):
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return t.end()

def to_flight(n):
    if isinstance(n, str):
        return n
    tag, attrs, kids = n
    props = {}
    for k, v in attrs.items():
        props[ATTR.get(k, k)] = v if v is not None else True
    ch = [to_flight(k) for k in kids]
    if ch:
        props['children'] = ch[0] if len(ch) == 1 else ch
    return ['$', tag, None, props]

def esc_text(s):
    return html.escape(s, quote=False).replace("'", '&#x27;').replace('"', '&quot;')

def to_html(n):
    if isinstance(n, str):
        return esc_text(n)
    tag, attrs, kids = n
    a = ''.join(f' {k}="{html.escape(v, quote=True)}"' if v is not None else f' {k}=""' for k, v in attrs.items())
    if tag in VOID:
        return f'<{tag}{a}/>'
    inner, prev_text = '', False
    for k in kids:
        is_text = isinstance(k, str)
        if is_text and prev_text:
            inner += '<!-- -->'        # React separa textos vizinhos assim
        inner += to_html(k)
        prev_text = is_text
    return f'<{tag}{a}>{inner}</{tag}>'

def load(fragment):
    t = Tree(); t.feed(fragment); t.close()
    return [k for k in t.root[2] if not isinstance(k, str)]

WA = 'https://wa.me/5581979128073?text=' + 'Ol%C3%A1%2C%20Thiago!%20Vi%20o%20caso%20no%20site%20e%20quero%20conversar%20sobre%20a%20minha%20opera%C3%A7%C3%A3o.'

DOR = f'''
<section id="da-dor-ao-sistema" class="v3-case" aria-labelledby="dor-title">
  <div class="v3-wrap">
    <p class="v3-kicker">Caso real · operador logístico</p>
    <h2 id="dor-title" class="v3-h2">Da dor ao sistema <em>funcionando.</em></h2>
    <p class="v3-lead">Um sistema de gestão com IA que construí para a diretoria de um operador logístico com dezenas de contratos. Está em uso todos os dias.</p>
    <div class="v3-ba">
      <div class="v3-col v3-before">
        <h3>Antes · apagando incêndio</h3>
        <ul>
          <li>Sem visão de gestão e sem dados confiáveis</li>
          <li>Nada consolidado: cada um tratava o desvio do seu jeito</li>
          <li>Nem todos sabiam que a ocorrência tinha acontecido</li>
          <li>O mesmo desvio voltava na semana seguinte</li>
          <li>A informação de SLA do cliente se perdia</li>
        </ul>
      </div>
      <div class="v3-arrow" aria-hidden="true">→</div>
      <div class="v3-col v3-after">
        <h3>Depois · gestão com dado</h3>
        <ul>
          <li>Uma visão, um padrão, um lugar</li>
          <li>Todo desvio tratado vira dado, causa e plano de ação</li>
          <li>Com a causa à vista, o desvio para de voltar</li>
          <li>A apresentação de SLA para o cliente sai em segundos</li>
          <li>A IA resume, aponta lacunas e mostra onde agir</li>
        </ul>
      </div>
    </div>
    <p class="v3-punch">O time não diminuiu. <span>Passou a trabalhar no que importa.</span></p>
    <p class="v3-note">Nome do cliente preservado. Telas reais na página do case.</p>
    <div class="v3-cta">
      <a class="v3-btn v3-btn-gold" href="{html.escape(WA)}" target="_blank" rel="noopener noreferrer" data-cta="dor-whatsapp">Sua operação tem uma dor assim? Fale comigo →</a>
      <a class="v3-btn v3-btn-ghost" href="/cases/inteligencia-operacional/">Ver o sistema</a>
    </div>
  </div>
</section>'''

QUEM = '''
<section id="quem-constroi" class="v3-who" aria-labelledby="quem-title">
  <div class="v3-wrap v3-who-grid">
    <figure class="v3-photo">
      <img src="/brand/thiago-borba.webp" alt="Thiago Borba, fundador da VIRA Studio" width="720" height="960" loading="lazy" decoding="async">
      <figcaption><b>Thiago Borba</b><span>Fundador da VIRA Studio · João Pessoa, PB</span></figcaption>
    </figure>
    <div>
      <p class="v3-kicker">Quem constrói</p>
      <h2 id="quem-title" class="v3-h2">Sistemas feitos por <em>quem opera.</em></h2>
      <p class="v3-lead">Há 14 anos eu trabalho dentro de operação logística — comecei como analista comercial e hoje faço gestão regional, com dezenas de contratos sob responsabilidade. Os sistemas da VIRA nascem desse lugar: de quem já viveu planilha solta, informação perdida e o mesmo problema voltando toda semana.</p>
      <ul class="v3-creds">
        <li><b>14 anos</b>em operação logística</li>
        <li><b>Six Sigma</b>Green e Black Belt</li>
        <li><b>MBA</b>IA para Negócios</li>
        <li><b>MBA</b>Logística e Supply Chain</li>
      </ul>
      <p class="v3-quote">“Eu não começo pela tecnologia. Começo pela dor de quem está na operação.”</p>
    </div>
  </div>
</section>'''

# id da seção → (fragmento, inserir depois de)
NEW = [('da-dor-ao-sistema', DOR, 'marquee'), ('quem-constroi', QUEM, 'cases')]

def run():
    txt_p, html_p = ROOT / 'index.txt', ROOT / 'index.html'
    payload = txt_p.read_text(encoding='utf-8')
    rows = flight.parse(payload)
    page_row = next(r for r in rows if r[1] == 'J' and '"id":"cases"' in r[2] and r[2].startswith('["$","$1"'))
    o = json.loads(page_row[2])
    kids = o[3]['children'][0]

    def kkey(k):
        if isinstance(k, list) and k[1] == 'section':
            return k[3].get('id')
        if isinstance(k, list) and 'Marquee_wrap' in str(k[3].get('className', '')):
            return 'marquee'
        return None

    h = html_p.read_text(encoding='utf-8')
    for sid, frag, after in NEW:
        if f'id="{sid}"' in h:
            print('já existe:', sid); continue
        tree = load(frag)[0]
        el, markup = to_flight(tree), to_html(tree)
        idx = next(i for i, k in enumerate(kids) if kkey(k) == after)
        kids.insert(idx + 1, el)
        # HTML: depois do elemento correspondente
        if after == 'marquee':
            m = re.search(r'<div class="Marquee_wrap__pcbGG"', h)
        else:
            m = re.search(r'<section id="%s"' % after, h)
        s = m.start()
        e = element_end(h, s)
        h = h[:e] + markup + h[e:]
        print('inserida:', sid, 'depois de', after)
    page_row[2] = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    new_payload = flight.serialize(rows)
    h = flight.to_html(h, new_payload)
    if 'vira-v3.css' not in h:
        h = h.replace('</head>', '<link rel="stylesheet" href="/vira-v3.css?v=20261110"/></head>', 1)
    html_p.write_text(h, encoding='utf-8')
    txt_p.write_text(new_payload, encoding='utf-8')

run()
