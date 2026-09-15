---
name: segment-tracking-plan
description: Cria e instrumenta um tracking plan do Segment via IaC (Terragrunt + Atlantis) no repo data-infra-afya, a partir de um mural do Miro já especificado — gera os eventos JSON modulares, monta o terragrunt de dev (permissivo) e depois de prod (restritivo) reusando os mesmos eventos, abre os PRs e roda atlantis plan e apply. Use SEMPRE que o usuário pedir para criar, subir, instrumentar ou codar um tracking plan ou plano de rastreamento do Segment, criar eventos JSON de tracking, montar os terragrunt.hcl de eventos de dev e prod, ou levar os eventos de um mural do Miro para produção via IaC, mesmo sem dizer tracking plan (por exemplo, sobe esses eventos pro Segment, cria o plano de eventos da extensão em dev e prod, instrumenta o tracking do Anywhere). Isto é DIFERENTE de revisar ou validar a nomenclatura dos eventos (esse é outro fluxo, no Miro) — aqui o foco é INSTRUMENTAR e SUBIR via IaC, tratando o mural como fonte da verdade já definida. Use TAMBÉM quando o pedido for mexer em JSON de tracking plan que JÁ existe sem mural novo, como responder review de PR, corrigir schema apontado pelo MarTech, preencher ou reescrever description de propriedade, e tirar ou acrescentar propriedade num evento já instrumentado (por exemplo, a Raab pediu mudanças na PR, ajusta o button_clicked, preenche as descrições desse evento).
---

# Criar Tracking Plan no Segment (dev → prod) via IaC

Instrumenta um **tracking plan do Segment** no repo `data-infra-afya` (Terragrunt + Atlantis),
usando **eventos JSON modulares**. Fluxo completo: primeiro **dev** (permissivo), depois **prod**
(restritivo) reusando os mesmos schemas.

Nasceu do trabalho da extensão **Afya Anywhere / WB Assist**, mas serve para qualquer app/BU.
Onde aparecer `<app>`, troque pelo slug da aplicação.

Este skill **não revisa nomenclatura** — ele assume que o mural já reflete o padrão decidido e o
instrumenta fielmente. Se o pedido for avaliar/validar nomes de eventos, esse é outro fluxo.

## ⭐ Princípios (interiorize antes de codar)

1. **O mural do Miro é a fonte final da verdade.** Nome do evento, propriedades, obrigatórios,
   enums, `application_name/feature/page`, valores de `button_name` — tudo sai do mural. Não invente,
   não deduza, não confie em memória nem no que "parece certo". Se algo não está no mural, não sobe.
   Essa disciplina existe porque um tracking plan errado é silencioso: o dado entra torto e só se
   descobre semanas depois, no dashboard.
2. **Em conflito, o mural vence.** Se um reviewer (humano ou bot) ou um padrão antigo divergir do
   mural, siga o mural e responda com a ressalva **citando o mural**. Exceções: (a) o próprio dono
   do produto decidir diferente numa conversa explícita — aí a decisão dele vira a nova verdade
   (registre isso no PR/card); (b) **evento de tela** — `page_viewed` / `screen_viewed` / `Page Viewed`
   no mural **não** viram `key` snake_case nova; traduzem para as rules TRACK já existentes
   (`"Page Viewed"` / `"Screen Viewed"`). Ver bullet "Evento de tela" abaixo.
3. **Leia o mural inteiro antes de codar.** Uma tabela de spec por área; não pegue só as linhas que
   um review citou — confira todas as áreas.
4. **Prove em dev antes de prod.** Dev primeiro (permissivo), valida via Atlantis plan, só então prod.
   Prod é restritivo e **descarta** o que estiver fora do plano; subir prod cru é arriscar bloquear
   evento legítimo.

## Pré-requisitos

- Repo `data-infra-afya` clonado; `gh` CLI autenticado; `python3` disponível.
- **Sources já criadas** no Segment (uma dev, uma prod) — você precisa dos dois `source_id`.
  A criação da source é outro passo/card; aqui assumimos que já existem.
- Acesso ao board do Miro via MCP (para ler a spec).
- **Apply é via Atlantis** por comentário no PR. As GitHub Actions **ignoram `segment/**`**, então o
  "check" verde não vem do CI — vem do `atlantis plan`/`apply`. A `master` é protegida (exige review).

## Layout do repositório

```
segment/
  events/<app>/...            # SCHEMAS dos eventos (JSON). COMPARTILHADOS entre dev e prod.
  develop/tracking_plan/tracking_plan-<app>/terragrunt.hcl   # plano DEV
  Prod/tracking_plan/tracking_plan-<app>/terragrunt.hcl      # plano PROD  (repare: "Prod", não "production")
  modules/tracking_plan/tracking_plan                        # módulo usado pelos dois
```

**Conceito-chave:** os JSONs em `segment/events/<app>` são só o **contrato/schema**. Não têm ambiente
nem dado. Dev e prod **apontam para a MESMA pasta de eventos** — o que muda entre eles é só o
`source_id` (onde o dado entra) e o **modo de schema** (permissivo/restritivo). É o padrão da casa:
confira `tracking_plan-afya-one` / `tracking_plan-afya-one-app` em `develop/` e `Prod/`.

🔴 **Permissivo é transitório, não é uma das duas opções.** A direção do MarTech, dita pela Raab em
14/09/2026, é que **todos** os tracking plans virem restritivos com o tempo. Consequências ao
escrever schema:

- **Não use "o plano hoje é permissivo" como argumento** para declarar de qualquer jeito, nem para
  deixar propriedade sem descrição. Plano permissivo só adia o erro.
- Em plano restritivo, **propriedade não declarada é omitida** e some do lake. Caso vivo: no
  whitebook o `path` sumiu por isso. ⚠️ Isso **não** contradiz a seção "O que NÃO se declara": ali
  a propriedade continua chegando por `context.page`, que é outra parte do payload.

### Afya One — duas surfaces (obrigatório ler antes de gravar)

O Afya One tem **dois** `events_path` e dois tracking plans:

| Surface | Pasta de eventos | Tracking plan |
|---|---|---|
| **APP** | `segment/events/afya-one/app` | `tracking_plan-afya-one-app` |
| **WEB** | `segment/events/afya-one/web` | `tracking_plan-afya-one` |

Cada surface carrega **todos** os `**/*.json` da pasta. **`key` deve ser único dentro da surface** —
dois arquivos com o mesmo `key` (mesmo em subpastas diferentes) quebram/duplicam o plano. Antes de
criar, inventarie as keys existentes (`rg '"key"' segment/events/afya-one/<surface>`).

Detalhes e política de pastas: [`references/afya-one-events-layout.md`](references/afya-one-events-layout.md).

## Fluxo geral

1. **Ler o mural** (Miro) → extrair a spec de cada área.
2. **Criar/atualizar os eventos JSON** na pasta correta da surface (`app/` e/ou `web/`).
3. **Dev**: terragrunt permissivo (se app novo) **ou** só eventos se o plano já existe; PR +
   `atlantis plan` (0 destroy), review, apply, merge.
4. **Prod**: só depois do dev; restritivo reusando a **mesma** `events_path`.

---

## Passo 1 — Ler o mural (Miro)

O produto entrega um mural com **uma tabela de spec por área** (evento, propriedades,
`application_name/feature/page`, obrigatórios, valores). Leia **todas** antes de codar.

Gotchas ao ler via MCP do Miro:

- **`context_get` quase sempre dá 502** (faz resumo por IA no origin). **Não fique retentando.**
- Preferir a API canvas (obrigatória a partir de **14/09/2026** — ver deprecação abaixo):
  - `canvas_search(..., result_mode="overview"|"areas"|"matches", patterns=[...])` → **achar**
    frames/áreas (ex.: "Home de Flashcards"). Não lê schema.
  - `canvas_read_as_svg` (após o search: `widget_ids` do frame **ou** os quatro `scope_*`; URL com
    `?moveToWidget=<frame_id>` ajuda) → **ler** o escopo (tabelas, shapes, docs).
  - `table_list_rows(miro_url="...?moveToWidget=<TABLE_ID>", limit=…)` → **schema (column metadata)
    + linhas**. É daqui que sai a lista de colunas (ex.: existe `Feedback Claude`?) — substitui o
    `_schema=` / `_row_count` que o `layout_read` structured devolvia.
- 🔴 **Deprecados, remoção em 14/09/2026** (mesma data): `layout_read`, `board_list_items`,
  `layout_create` / `layout_update` / `layout_get_dsl`. O substituto de **leitura** do `layout_read`
  é `canvas_read_as_svg` (+ `table_list_rows` para schema de tabela). O substituto de **busca** do
  `board_list_items` é `canvas_search`. **Não use esses deprecated no fluxo principal** — em cinco
  dias o Modo A/Passo 1 quebra se ainda dependerem deles.
- Células vêm ora como **texto puro**, ora como **Quill delta**
  (`{"format":"delta","ops":[{"insert":"..."}]}`) — parseie os dois (incluindo negrito/`strike`).
- Texto **riscado** (`"attributes":{"strike":true}`) = evento descartado/adiado — **não sobe**.
- Sem MCP Miro autenticado (`namespaceStatus: ready`), **pare** e peça ao usuário conectar o MCP —
  não invente a spec.

Antes de escrever qualquer JSON, tenha em mãos, por evento: nome (`key`), a lista de propriedades com
tipos, quais são obrigatórias, os enums/valores fixos, e o `button_name` exato quando houver.

---

## Passo 2 — Criar os eventos JSON

Um arquivo por evento. Copie `assets/event.template.json` e preencha a partir do mural.

### Onde gravar (Afya One / learn)

1. **Não invente pasta de feature** (ex.: `flashcards/`) nem `epico-*` novo para Learn.
   - **WEB:** use `web/learn-engagement/` (já existe no master).
   - **APP:** `app/learn-engagement/` **ainda não existe** no master — **crie a pasta** no primeiro
     evento de Learn/engajamento do app e grave lá. Não use um `epico-*` novo como substituto.
2. **Antes de criar**, busque se a `key` já existe na surface:
   - Se existir → **atualize o arquivo existente** (merge de enums/props do mural), **não** crie
     cópia noutra subpasta.
   - Se a cópia existente estiver em **`learn-preparatory/`** ou **`learn-engagement/`** e o
     evento for claramente **compartilhado** (reusado por mais de uma jornada) → **promova para
     `global/`** (mova o JSON, mergeie a spec do mural, apague a cópia antiga).
   - **Exceção explícita:** **não** promova nem mova eventos da pasta **`search/`** para `global`
     nesta política — deixe em `search/` e só atualize o arquivo lá.
3. Eventos **novos e específicos** da jornada ficam em `learn-engagement/` (criando
   `app/learn-engagement/` se for a primeira vez no app).
4. Se o mural pedir app **e** web (Device = All devices), espelhe nas duas surfaces, respeitando
   keys já existentes em cada uma.

### Regras de formato que costumam morder

- **`json_schema.description`** fica logo após `$schema` (é a "descrição do evento"). Na dúvida do
  padrão, olhe um evento existente, ex.: `segment/events/afya-one/app/global/Screen_Viewed.json`.
- 🔴 **`description` de propriedade é GENÉRICA: diz o que o campo é e para aí.** Sem percentual de
  preenchimento, sem contagem, sem data de medição, sem nome de janela. Pedido do MarTech (Raab) no
  review da `data-infra-afya`#910, com exemplo dado por ela: `application_name` é
  `"Nome da aplicação que emitiu o evento"`, e **não** `"Nome da aplicação que emitiu o evento, no
  padrão MarTech. Preenchimento de 99,42% de 15/08 a 14/09/2026 e o único valor é iclinic_web."`.
  🔑 **Medição não mora no schema.** O schema é contrato e envelhece devagar; medição envelhece todo
  dia. Número medido vai para o corpo da PR, para o card e para a memória.
- 🔴 **Toda propriedade declarada precisa de `description` preenchida.** Descrição vazia (`""`) é o
  estado em que a maioria dos JSONs do `iclinic/` está hoje, e é justamente o que o MarTech cobra.
- Propriedades ficam **aninhadas** em `json_schema.properties.properties.properties` (sim, aninhado).
- `required` lista os obrigatórios; use `enum` para valores fixos; `"type": "integer"` para inteiros
  discretos (nota, passo), **não** `"number"`.
- Grave JSON em **UTF-8** (acentos em descrições). Se o console quebrar no `✓` do script, force
  UTF-8 no ambiente (bash: `PYTHONIOENCODING=utf-8 …`; PowerShell: `$env:PYTHONIOENCODING = "utf-8"`).

### O que NÃO se declara (o template só mostra o que entra)

- 🔴 **Propriedade que o SDK do Segment captura sozinho não se declara.** Em chamada `page`/`screen`
  são **`url`, `path`, `referrer`, `search` e `title`**. Declarar duplica dado, e foi reprovado pelo
  MarTech no review da `data-infra-afya`#910.
- **Por que não se perde nada:** elas viajam **duas vezes no mesmo payload**, em `properties` e em
  `context.page`. Medido na tela `Exibição do Alerta de Faltas`, 399.408 disparos de 10/09 a
  14/09/2026: `url` e `path` idênticos nos dois lados em **100%**, `referrer` em **97,69%** dos dois
  lados, `search` em **10,98%** dos dois lados. Quem precisa do valor lê de `context.page`.
- ⚠️ **Não confunda com a propriedade do PRODUTO que tem nome parecido.** `name` de tela, `category`
  e os ids do produto continuam sendo declarados.

### Convenções de modelagem (checklist — siga o mural, isto é só o "como")

- **`application_name` pode variar por área** — não assuma um valor único. (No Anywhere: `whitebook`
  no chat, `anywhere` em home/onboarding/nota/shell, `iclinic` no registrar.) Siga o mural.
- **`button_name`**: use o **valor exato do mural**, que às vezes **não** é igual ao nome do evento
  (ex.: evento `generate_documents_clicked` com `button_name: assist_generate_documents_clicked`; ou
  um evento de rating com `button_name` enum `rate_positive`/`rate_negative`).
- **Evento de tela** (não copie snake_case do mural):
  - WEB → **`"key": "Page Viewed"`** no arquivo existente
    `segment/events/afya-one/web/global/Page_Viewed.json` (tipo TRACK; valida `analytics.page()`).
  - APP → **`"key": "Screen Viewed"`** em
    `segment/events/afya-one/app/global/Screen_Viewed.json` (valida `analytics.screen()`).
  - Se o mural escrever `page_viewed`, `Page Viewed`, `screen_viewed`, etc., isso é **rótulo da
    ação de tela** — traduza para a rule acima. **Não** crie `page_viewed.json` / `screen_viewed`
    com `key` snake_case: em prod (`allow_unplanned_events = false`) vira rule morta, porque o
    tráfego real continua caindo em `Page Viewed` / `Screen Viewed`.
  - O que o mural manda de verdade aqui são **props/enums** (páginas, features, etc.) a mergear
    nesses JSONs globais — não o nome da rule.
- **Nomes no passado/consolidados**: siga o mural (ex.: `mic_permission_resolved`, `tab_status_updated`,
  `recording_cancel_confirmed`, `silence_alerted`). Um evento consolidado usa uma propriedade de estado
  (`status`, `state`, `interaction`) em vez de vários eventos separados.
- **`result` → prefira `status`** como nome de propriedade.
- **Obrigatoriedade** (padrão comum): id de sessão sempre obrigatório; o id do usuário logado
  (ex.: `whitebook_id`) obrigatório **exceto** em eventos **pré-login** (tela, permissões,
  install/uninstall, login_failed, onboarding). O id cross-ecossistema (ex.: `afya_id`) costuma ser
  **opcional**.
- **Objetos aninhados**: se o mural pede um custo detalhado, use um objeto (`custo: {intention, ...}`),
  não um campo achatado tipo `custo_total`.
- **PII** (texto de pergunta, nome de arquivo) sempre **opcional**.
- **Fora de escopo não sobe**: eventos riscados/marcados como versão futura ficam de fora do PR.
- Ao **estender** um evento global/compartilhado: acrescente enums/páginas/features do mural;
  se um `required` antigo impede o caso novo (ex.: `assessment_id` obrigatório num filtro de
  flashcard), torne a prop opcional **só** se o mural não a exige — e documente no `description`.

Valide os JSON antes de commitar (a partir do workbench, apontando para o checkout do
`data-infra-afya`):

```bash
# bash / Git Bash / WSL
PYTHONIOENCODING=utf-8 python3 src/skills/segment/segment-tracking-plan/scripts/validate_events.py \
  /caminho/para/data-infra-afya/segment/events/afya-one/app
PYTHONIOENCODING=utf-8 python3 src/skills/segment/segment-tracking-plan/scripts/validate_events.py \
  /caminho/para/data-infra-afya/segment/events/afya-one/web
```

```powershell
# PowerShell (Windows) — env e continuações são diferentes; o executável costuma ser `python`
$env:PYTHONIOENCODING = "utf-8"
python src/skills/segment/segment-tracking-plan/scripts/validate_events.py `
  C:\caminho\para\data-infra-afya\segment\events\afya-one\app
python src/skills/segment/segment-tracking-plan/scripts/validate_events.py `
  C:\caminho\para\data-infra-afya\segment\events\afya-one\web
```

O script checa sintaxe e estrutura (aninhamento, `description`, `required` coerente). Ele **não** checa
se o conteúdo bate com o mural — essa conferência é sua/humana.

---

## Passo 3 — Dev (permissivo): terragrunt + PR + Atlantis

Copie `assets/terragrunt.dev.template.hcl` para
`segment/develop/tracking_plan/tracking_plan-<app>/terragrunt.hcl` e preencha `<app>`, `<App>` e o
`<SOURCE_ID_DEV>`. O modo dev é **permissivo** de propósito (não bloqueia eventos/props não
planejados) para você conseguir iterar sem travar a app.

> **Não** use o padrão `label == "prod" ? [...] : [...]` no `source_id` — deixa o id inválido no
> ambiente errado. Ponha o id direto (o arquivo já é do `develop`).

Depois:

1. **Branch** a partir da `origin/master` recém-atualizada (não do HEAD defasado):
   ```bash
   git fetch origin master
   git checkout -b feat/DC-XXXXX/segment-dev-tracking-plan-<app> origin/master
   ```
2. **Commit** referenciando o card: `[DC-XXXXX] ...`. **Push**.
3. **Abra o PR** preenchendo `.github/pull_request_template.md` (Resumo, Cards relacionados,
   Prioridade). Use `gh pr create --body-file <arquivo>`.
4. **Atlantis plan** por comentário no PR:
   ```
   atlantis plan -d segment/develop/tracking_plan/tracking_plan-<app>
   ```
   Você quer algo como `Plan: N to add, 0 to change, 0 to destroy`. **0 destroy** é o alvo. O output
   vem picado em vários comentários ("Continued..."); concatene e procure a linha `Plan:`.
5. **Resolva o review** (se houver). Threads via GraphQL:
   - Responder: `addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId, body})`
   - Fechar: `resolveReviewThread(input:{threadId})`
   - **Copilot é bot**: só resolva a thread (corrige + resolve), **sem responder**.
   - Divergiu do reviewer com base no mural? Responda citando o mural (o mural é a fonte).
6. **Atlantis apply** após aprovação, e **merge**.

---

## Passo 4 — Prod (restritivo): reusa os mesmos eventos

Só depois do dev mergeado. Copie `assets/terragrunt.prod.template.hcl` para
`segment/Prod/tracking_plan/tracking_plan-<app>/terragrunt.hcl`. É **igual ao dev**, mudando 4 coisas:
diretório (`Prod/`), `source_id` (prod), `name` (sem `[Dev]`), e o **modo → RESTRITIVO**
(`false`/`BLOCK`). A `events_path` é a **mesma** do dev. Espelhe
`segment/Prod/tracking_plan/tracking_plan-afya-one`.

> **Prod NÃO pode ser permissivo.** Com `BLOCK`, o Segment **descarta** qualquer evento/propriedade
> fora do plano nessa source. Para source nova é o desejado; mas confirme que a app em prod só emite o
> que está planejado, senão evento legítimo é bloqueado.

Confira que o conjunto de inputs bate com o template de prod da casa:

```bash
diff <(grep -oE '^\s+[a-z_]+\s*=' segment/Prod/tracking_plan/tracking_plan-afya-one/terragrunt.hcl | tr -d ' =' | sort) \
     <(grep -oE '^\s+[a-z_]+\s*=' segment/Prod/tracking_plan/tracking_plan-<app>/terragrunt.hcl   | tr -d ' =' | sort)
# só deve diferir a local "label" (que não usamos)
```

Depois: branch nova (`feat/DC-YYYYY/segment-prod-tracking-plan-<app>`), commit `[DC-YYYYY]`, PR com
template, `atlantis plan -d segment/Prod/tracking_plan/tracking_plan-<app>` (0 destroy),
review/aprovação, `atlantis apply`, merge.

---

## Checklist final

- [ ] Eventos JSON criados/validados a partir do mural (sem os itens fora de escopo).
- [ ] Surface correta (`app` / `web`); **sem keys duplicadas** na surface.
- [ ] Pasta correta (`learn-engagement` para Learn; promoção a `global` só a partir de
      `learn-preparatory`/`learn-engagement`; **não** promover `search/`).
- [ ] Dev: terragrunt permissivo (se novo), `source_id` dev direto, `events_path` correto —
      ou só JSON se o plano já existe.
- [ ] PR dev: plan `0 destroy`, review resolvido, apply + merge.
- [ ] Prod: terragrunt **restritivo** (`false`/`BLOCK`), `source_id` prod, **mesma** `events_path`.
- [ ] PR prod: plan `0 destroy`, aprovação, apply + merge.
- [ ] Cards Jira atualizados (sub-tarefa dev + sub-tarefa prod sob a tarefa guarda-chuva).

## Apêndice — convenções Jira (opcional)

- Hierarquia: **Épico → Tarefa (guarda-chuva) → Sub-tarefa** (uma pra dev, uma pra prod).
- Branch: `feat/DC-XXXXX/descricao`; commit referencia `[DC-XXXXX]`.
- Ao abrir card: preencher Área demandante, Sub-área, Time, assignee e prioridade conforme o padrão.
- Transição para "Concluído" quando o PR do card estiver aplicado + mergeado; feche a Tarefa
  guarda-chuva quando todas as sub-tarefas fecharem.
