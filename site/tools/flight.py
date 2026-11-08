"""Parser/serializer mínimo do payload Flight (RSC) do Next."""
import re, json

def parse(payload):
    rows, i, n = [], 0, len(payload)
    b = payload.encode('utf-8')
    # trabalhar em bytes por causa das linhas T (tamanho em bytes)
    i = 0
    while i < len(b):
        m = re.compile(rb'([0-9a-f]*):').match(b, i)
        if not m:
            raise ValueError('linha inválida em %d: %r' % (i, b[i:i+40]))
        rid = m.group(1).decode(); j = m.end()
        tm = re.compile(rb'T([0-9a-f]+),').match(b, j)
        if tm:
            ln = int(tm.group(1), 16); s = tm.end()
            rows.append([rid, 'T', b[s:s+ln].decode('utf-8')]); i = s + ln
        else:
            k = b.find(b'\n', j)
            if k < 0: k = len(b)
            rows.append([rid, 'J', b[j:k].decode('utf-8')]); i = k + 1
    return rows

def serialize(rows):
    out = []
    for rid, kind, body in rows:
        if kind == 'T':
            out.append(f'{rid}:T{len(body.encode("utf-8")):x},{body}')
        else:
            out.append(f'{rid}:{body}\n')
    return ''.join(out)

PUSH = re.compile(r'<script>self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)</script>')

def from_html(h):
    return ''.join(json.loads('"' + m.group(1) + '"') for m in PUSH.finditer(h))

def to_html(h, payload):
    ms = list(PUSH.finditer(h))
    enc = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
    first, last = ms[0], ms[-1]
    # remove todos os pushes antigos e coloca um só no lugar do primeiro
    parts, pos = [], 0
    for idx, m in enumerate(ms):
        parts.append(h[pos:m.start()])
        if idx == 0:
            parts.append('<script>self.__next_f.push([1,' + enc + '])</script>')
        pos = m.end()
    parts.append(h[pos:])
    return ''.join(parts)
