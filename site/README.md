# virastudio.uk

Site do VIRA Studio publicado no Cloudflare Worker `solitary-cell-a1f1`.

## Como publicar
Todo push na branch configurada na Cloudflare (Workers Builds) publica sozinho:
- Diretório raiz: `site`
- Comando de build: (vazio)
- Comando de deploy: `npx wrangler deploy`

## Estrutura
| Pasta | O que é |
|---|---|
| `public/` | O site pronto (HTML/CSS/JS estáticos). É o que vai ao ar. |
| `public/vira-stack.css` e `.js` | Home em camadas (seções empilhando ao rolar) + índice de camadas. |
| `tools/patch.py` | Reaplica contatos e o efeito sobre uma cópia nova do site, se precisar regenerar. |
| `wrangler.jsonc` | Configuração do Worker. |

## Mudanças rápidas
- Texto ou contato: editar o HTML em `public/` **e** o `index.txt` da mesma pasta (é o que o Next usa ao navegar entre páginas).
- Não alterar o tamanho de blocos `NN:T<hex>,` no `index.txt`/scripts sem recalcular — o `patch.py` mostra como.

## Atenção
O código-fonte Next.js da versão de 20/10 não foi encontrado. `public/` foi gerado a partir do site no ar em 08/11/2026.
Próximo passo recomendado: reconstruir o fonte Next aqui em `site/src` e trocar `public/` pelo build.

## Histórico
- 08/11/2026 — e-mail thiago@virastudio.uk, Instagram @virastudiobr, Home em camadas.
- 08/11/2026 — deploy automático ligado (Workers Builds, raiz `site`).
