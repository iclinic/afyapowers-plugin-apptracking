# Afya One — layout de eventos JSON

Referência operacional para a skill `segment-tracking-plan` ao instrumentar
`data-infra-afya/segment/events/afya-one/`.

## Surfaces e tracking plans

| Surface | `events_path` | Terragrunt (dev) | Terragrunt (prod) |
|---|---|---|---|
| APP | `segment/events/afya-one/app` | `develop/.../tracking_plan-afya-one-app` | `Prod/.../tracking_plan-afya-one-app` |
| WEB | `segment/events/afya-one/web` | `develop/.../tracking_plan-afya-one` | `Prod/.../tracking_plan-afya-one` |

O módulo carrega `fileset(events_path, "**/*.json")`. Qualquer subpasta entra no plano.
**A `key` do JSON deve ser única por surface** (não por subpasta).

## Pastas usuais (WEB)

| Pasta | Uso |
|---|---|
| `web/global/` | Eventos compartilhados entre jornadas (ex.: `button_clicked`, `filter_applied`, `input_filled`, `rating_viewed` quando promovidos) |
| `web/learn-engagement/` | Learn / engajamento / consumo (Flashcards, podcasts, rating de conteúdo, etc.) |
| `web/learn-preparatory/` | Fluxos preparatórios (ex.: criação de simulado) |
| `web/search/` | Busca — **não promover para `global/`** pela política atual |
| `web/learn-performance/`, `web/course_page/`, … | Outros épicos |

## Pastas usuais (APP)

No `origin/master` do `data-infra-afya` (conferido 10/09/2026), `segment/events/afya-one/app/`
só tem `global/` e `epico-*` (epico-1…3, epico-artigo-quiz, epico-busca, epico-expansao-objetos,
epico-feed-vertical, epico-navegacao-pos, epico-videos-verticais). **`app/learn-engagement/` ainda
não existe.**

| Pasta | Uso |
|---|---|
| `app/global/` | Compartilhados do app (`Screen_Viewed`, `button_clicked`, assessments, …) — **existe** |
| `app/learn-engagement/` | **Alvo (criar)** no primeiro evento de Learn/engajamento do app (Flashcards e afins). Espelha o papel de `web/learn-engagement/`. Não invente `flashcards/` nem outro `epico-*` novo para isso. |
| `app/epico-*` | Épicos **já existentes** (legados). Atualize no lugar se a `key` já estiver aí; **não crie** `epico-*` novo quando o caso for Learn — nesse caso **crie** `app/learn-engagement/` e grave lá. |

## Política de colocação (resumo)

1. Feature nova de Learn → web: `web/learn-engagement/` (já existe). App: **criar**
   `app/learn-engagement/` no primeiro evento Learn do app (a pasta ainda não está no master).
2. **Não** criar pasta com nome da feature (`flashcards/`, `home-flashcards/`, …) salvo orientação
   explícita do time.
3. Se a `key` já existe na surface → atualizar o arquivo existente (merge de enums/props).
4. Se a cópia existente está em `learn-preparatory/` ou `learn-engagement/` **e** o evento é
   compartilhado → **mover para `global/`**, mergear, apagar a origem.
5. Pasta **`search/`**: atualizar no lugar; **não** mover para `global/`.
6. Device = All devices no mural → avaliar **app e web**; não assumir só uma surface.
7. Evento de tela no mural (`page_viewed` / `screen_viewed`) → merge em `web/global/Page_Viewed.json`
   (`"key": "Page Viewed"`) ou `app/global/Screen_Viewed.json` (`"key": "Screen Viewed"`).
   **Nunca** criar rule snake_case nova para tela (rule morta vs `analytics.page()`/`screen()`).

## Inventário rápido (Python)

Rode **nas duas surfaces** (`app` e `web`). Tipagem `IDENTIFY` (ex.: `web/global/identify.json`)
pode **não ter** `key` de topo — use `.get('key')` e ignore quem não tem, senão a web estoura
`KeyError`. Saída vazia = ok; qualquer `key` listada é duplicata (ex.: `epico-3` vs `global` no
app, ou `alternative_eliminated` em `learn-preparatory` + `learn-engagement` no web) e cai no
item 4 da política acima (mover/mergear pra `global/` e apagar a origem, quando aplicável).

```bash
# a partir da raiz do data-infra-afya — keys duplicadas por surface
python -c "
from pathlib import Path
import json
for surface in ('app', 'web'):
    root = Path('segment/events/afya-one') / surface
    m = {}
    for p in root.rglob('*.json'):
        k = json.loads(p.read_text(encoding='utf-8')).get('key')
        if k:
            m.setdefault(k, []).append(str(p))
    dups = {k: v for k, v in m.items() if len(v) > 1}
    print(surface, dups or 'ok')
"
```

One-liner equivalente (uma surface; troque `web` por `app`):

```bash
python -c "from pathlib import Path; import json; root=Path('segment/events/afya-one/web'); m={};
[m.setdefault(json.loads(p.read_text(encoding='utf-8')).get('key'), []).append(str(p)) for p in root.rglob('*.json')];
print({k:v for k,v in m.items() if k and len(v)>1})"
```

## Exemplo recente (Flashcards)

- Spec no Miro: áreas **Home de Flashcards** e **Jornada de Flashcards**.
- Eventos específicos da jornada → web: `web/learn-engagement/` (já existe). App: **criar**
  `app/learn-engagement/` se ainda não existir e gravar lá (não criar pasta `flashcards/` nem
  `epico-*` novo).
- Estado em `origin/master` do `data-infra-afya` (conferido 10/09/2026): os compartilhados ainda
  **não** estão em `web/global/` —
  `input_filled` → `web/learn-preparatory/`, `rating_viewed` e `results_filter_applied` →
  `web/learn-engagement/`. **Devem ser promovidos** a `web/global/` (item 4) no PR de instrumentação
  correspondente — mergear props do mural, mover o JSON, apagar a origem. Não procure esses três
  em `global/` até o PR landing.
- `search_performed` em `web/search/` permanece em `search/` (só merge de props, sem promoção).
