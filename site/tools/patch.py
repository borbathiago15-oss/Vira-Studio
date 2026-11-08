"""Aplica as mudanças de comunicação e o empilhamento sobre o build estático do virastudio.uk.

Uso: python3 patch.py <pasta-origem> <pasta-destino>
"""
import shutil, sys, re, pathlib

SRC, DST = map(pathlib.Path, sys.argv[1:3])
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

OLD_MAIL = 'virastudiocontato@gmail.com'
NEW_MAIL = 'thiago@virastudio.uk'
IG_URL = 'https://www.instagram.com/virastudiobr'
IG_HANDLE = '@virastudiobr'
VERSION = '20261108c'

report = {}

PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')

def flight_payload(text, suffix):
    if suffix == '.txt':
        return text
    import json
    return ''.join(json.loads('"' + m.group(1) + '"') for m in PUSH_RE.finditer(text))

def raw_transform(s):
    """Mesmas trocas, no formato cru (aspas sem escape) — usadas dentro de linhas T do RSC."""
    s = s.replace(OLD_MAIL, NEW_MAIL)
    a = '"telephone":"+5581979128073","inLanguage"'
    b = '"telephone":"+5581979128073","sameAs":["%s"],"inLanguage"' % IG_URL
    return s.replace(a, b)

def fix_text_rows(original, patched, suffix):
    """Linhas T do Flight declaram o tamanho em bytes do conteúdo; recalcula depois das trocas."""
    full = flight_payload(original, suffix)
    for m in re.finditer(r'(?:^|\n|[\]}])([0-9a-f]+):T([0-9a-f]+),', full):
        rid, hexlen = m.group(1), m.group(2)
        n = int(hexlen, 16)
        content = full[m.end():].encode('utf-8')[:n].decode('utf-8')
        new_n = len(raw_transform(content).encode('utf-8'))
        if new_n != n:
            old_h, new_h = f'{rid}:T{hexlen},', f'{rid}:T{new_n:x},'
            assert patched.count(old_h) == 1, (rid, patched.count(old_h))
            patched = patched.replace(old_h, new_h)
            bump('t_rows_fixed')
    return patched

def bump(k, n=1):
    report[k] = report.get(k, 0) + n

for f in DST.rglob('*'):
    if not f.is_file() or f.suffix not in ('.html', '.txt', '.js'):
        continue
    t = f.read_text(encoding='utf-8')
    o = t
    n = t.count(OLD_MAIL)
    t = t.replace(OLD_MAIL, NEW_MAIL)
    bump('email', n)

    if f.suffix == '.js':
        n = t.count('instagram:null')
        t = t.replace('instagram:null',
                      'instagram:{handle:"%s",url:"%s"}' % (IG_HANDLE, IG_URL))
        bump('js_instagram', n)
    else:
        # --- Rodapé: HTML
        li_mail = f'<li><a href="mailto:{NEW_MAIL}">{NEW_MAIL}</a></li>'
        li_ig = (f'<li><a href="{IG_URL}" target="_blank" rel="noopener noreferrer">'
                 f'Instagram <!-- -->{IG_HANDLE}</a></li>')
        if li_mail + '</ul>' in t:
            t = t.replace(li_mail + '</ul>', li_mail + li_ig + '</ul>')
            bump('footer_html')
        # --- Rodapé: payload RSC (escapado dentro de <script> no .html, cru no .txt)
        for q in ('\\"', '"'):
            mail_el = (f'[{q}${q},{q}li{q},null,{{{q}children{q}:[{q}${q},{q}a{q},null,'
                       f'{{{q}href{q}:{q}mailto:{NEW_MAIL}{q},{q}children{q}:{q}{NEW_MAIL}{q}}}]}}]')
            ig_el = (f'[{q}${q},{q}li{q},null,{{{q}children{q}:[{q}${q},{q}a{q},null,'
                     f'{{{q}href{q}:{q}{IG_URL}{q},{q}target{q}:{q}_blank{q},{q}rel{q}:{q}noopener noreferrer{q},'
                     f'{q}children{q}:[{q}Instagram {q},{q}{IG_HANDLE}{q}]}}]}}]')
            if mail_el + ',null]' in t:
                t = t.replace(mail_el + ',null]', mail_el + ',' + ig_el + ']')
                bump('footer_rsc')

        # --- Página de contato: HTML
        p_mail = (f'<p class="contato_channelItem__K5Aob"><span class="contato_channelLabel__78iQi">E-mail</span>'
                  f'<a href="mailto:{NEW_MAIL}">{NEW_MAIL}</a></p>')
        p_ig = (f'<p class="contato_channelItem__K5Aob"><span class="contato_channelLabel__78iQi">Instagram</span>'
                f'<a href="{IG_URL}" target="_blank" rel="noopener noreferrer">{IG_HANDLE}</a></p>')
        if p_mail in t:
            t = t.replace(p_mail, p_mail + p_ig)
            bump('contato_html')
        for q in ('\\"', '"'):
            c_mail = (f'[{q}${q},{q}p{q},null,{{{q}className{q}:{q}contato_channelItem__K5Aob{q},{q}children{q}:['
                      f'[{q}${q},{q}span{q},null,{{{q}className{q}:{q}contato_channelLabel__78iQi{q},{q}children{q}:{q}E-mail{q}}}],'
                      f'[{q}${q},{q}a{q},null,{{{q}href{q}:{q}mailto:{NEW_MAIL}{q},{q}children{q}:{q}{NEW_MAIL}{q}}}]]}}]')
            c_ig = (f'[{q}${q},{q}p{q},null,{{{q}className{q}:{q}contato_channelItem__K5Aob{q},{q}children{q}:['
                    f'[{q}${q},{q}span{q},null,{{{q}className{q}:{q}contato_channelLabel__78iQi{q},{q}children{q}:{q}Instagram{q}}}],'
                    f'[{q}${q},{q}a{q},null,{{{q}href{q}:{q}{IG_URL}{q},{q}target{q}:{q}_blank{q},{q}rel{q}:{q}noopener noreferrer{q},{q}children{q}:{q}{IG_HANDLE}{q}}}]]}}]')
            if c_mail in t:
                t = t.replace(c_mail, c_mail + ',' + c_ig)
                bump('contato_rsc')

        # --- JSON-LD: sameAs com o Instagram
        for q in ('\\"', '"'):
            a = f'{q}telephone{q}:{q}+5581979128073{q},{q}inLanguage{q}'
            b = f'{q}telephone{q}:{q}+5581979128073{q},{q}sameAs{q}:[{q}{IG_URL}{q}],{q}inLanguage{q}'
            n = t.count(a)
            if n:
                t = t.replace(a, b)
                bump('jsonld_sameAs', n)

        # --- Empilhamento: CSS + JS em todas as páginas (o script só ativa na Home)
        if f.suffix == '.html' and '</head>' in t and 'vira-stack.js' not in t:
            tag = (f'<link rel="stylesheet" href="/vira-stack.css?v={VERSION}"/>'
                   f'<script src="/vira-stack.js?v={VERSION}" defer=""></script>'
                   f'<script src="/vira-hud.js?v={VERSION}" defer=""></script>')
            t = t.replace('</head>', tag + '</head>', 1)
            bump('stack_injected')

    if f.suffix in ('.html', '.txt'):
        t = fix_text_rows(o, t, f.suffix)
    if t != o:
        f.write_text(t, encoding='utf-8')

left = [str(f.relative_to(DST)) for f in DST.rglob('*')
        if f.is_file() and f.suffix in ('.html', '.txt', '.js') and OLD_MAIL in f.read_text(encoding='utf-8')]
print(report)
print('e-mail antigo restante em:', left or 'nenhum')
