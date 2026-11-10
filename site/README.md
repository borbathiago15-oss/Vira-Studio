# virastudio.uk

Site do VIRA Studio publicado no Cloudflare Worker `solitary-cell-a1f1`.

## Como publicar
Todo push na branch configurada na Cloudflare (Workers Builds) publica sozinho:
- Diretório raiz: `/` (raiz do repositório — a config fica em `/wrangler.jsonc`, apontando para `site/public`)
- Comando de build: (vazio)
- Comando de deploy: `npx wrangler deploy`

## Estrutura
| Pasta | O que é |
|---|---|
| `public/` | O site pronto (HTML/CSS/JS estáticos). É o que vai ao ar. |
| `public/vira-stack.css` e `.js` | Cartões da construção: as 4 etapas empilham ao rolar (Home e /processo), referência Mercado Pago. |
| `tools/patch.py` | Reaplica contatos e injeta o CSS/JS sobre uma cópia nova do site. |
| `tools/home.py` | Reordena a Home (HTML + payload do React juntos). Rodar depois do patch.py. |
| `public/vira-hud.js` | Animação HUD (SVG, linha do tempo determinística): topo da Home ("sistema") e Tecnologia + IA ("ia"). |
| `tools/hud-video.html` + `tools/render.py` | Gera os vídeos MP4 da mesma animação (9:16 e 4:5), quadro a quadro. |
| `tools/seo.py` | og:image/twitter em todas as páginas, sitemap com data, llms.txt gerado das páginas reais. Rodar por último. |
| `tools/remove_cases.py` | Tira cases do site inteiro (páginas, vitrine, grade, links, imagens, sitemap) sem quebrar a hidratação. |
| `tools/add_sections.py` + `public/vira-v3.css` | Seções de venda da Home: Da dor ao sistema e Quem constrói. |
| `tools/flight.py` | Leitura/escrita do payload do React (RSC) usado pelos dois scripts. |
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
- 08/11/2026 — Home reordenada (Soluções → Cases → Como construímos → Tecnologia → Investimento → Dúvidas → Contato); saem Manifesto, Como pensamos e Sobre (seguem em /processo e /sobre). Empilhamento só nas 4 etapas.
- 08/11/2026 — Animação HUD no topo (substitui a parede de projetos) e em Tecnologia + IA; vídeos Reels/LinkedIn gerados do mesmo código.
- 08/11/2026 — og-image.jpg recriada no estilo HUD (a cópia do site no ar não tinha trazido a imagem); HSTS ligado.
- 09/11/2026 — SEO: llms.txt, sitemap com data atual, og:image em todas as páginas, twitter:title por página; scripts esperam a hidratação do React (corrige erro #418 intermitente na Home).
- 10/11/2026 — Saem os cases Gestão de Facilities e Gestão de Suprimentos (redirect 301 para /cases/, imagens apagadas). Entram na Home 'Da dor ao sistema' (logo após o topo) e 'Quem constrói' (com foto); barra fixa de WhatsApp no celular; tabela de Investimento rola no celular.
