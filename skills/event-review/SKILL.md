---
name: event-review
description: Avalia a nomenclatura E a completude de eventos de tracking (MarTech/analytics) contra o padrão da Afya (nomenclatura, eventos globais x locais, métodos de chamada e propriedades obrigatórias). Opera em dois modos - no board do Miro, escrevendo o parecer na coluna Feedback Claude, ou pelo tráfego real em raw_tracking_prod cruzado com o tracking plan em IaC, quando não há mural ou quando o produto já está instrumentado. Use SEMPRE que o usuário pedir para revisar, validar, avaliar ou dar feedback sobre nomes de eventos, propriedades ou tabelas de eventos e tracking, mesmo que não cite a palavra nomenclatura explicitamente (por exemplo, avalia os eventos do board, esses nomes estão no padrão, revisa o tracking dessa tela, os eventos do prescription_segment estão certos, avalia sem o Miro). Também use quando o usuário colar as regras ou a documentação de tracking e pedir para aplicá-las.
---

# Avaliação de Eventos de Tracking MarTech (Afya)

Esta skill avalia eventos de tracking contra o padrão da Afya em duas dimensões —
**nomenclatura** (nome do evento e das propriedades) e **completude** (propriedades
obrigatórias presentes e uso correto do método de chamada).

As **regras** (seções seguintes) valem nos dois modos de execução; só muda a fonte de verdade e
onde o parecer é registrado:

| Modo | Fonte de verdade | Quando usar | Saída |
|---|---|---|---|
| **A — Miro** | tabelas do board | evento ainda vai ser instrumentado; existe mural validado | coluna "Feedback Claude" |
| **B — tráfego real** | tracking plan em IaC × `raw_tracking_prod` | produto já instrumentado; mural inexistente, bloqueado ou desatualizado | parecer em markdown / card Jira |

O modo B é mais fiel quando o produto já está em produção, porque mede **o que chega**, não o que
foi especificado. Quando os dois estão disponíveis, o mural diz a intenção e o lake diz o fato — a
divergência entre eles costuma ser o achado mais valioso.

## Modo A — review no board do Miro

Cada tela do produto tem uma tabela; cada **linha** é um evento. Colunas relevantes:

- **Evento** — nome do evento (alvo principal da avaliação). Ex.: `button_clicked`.
- **Atributos customizados** — as propriedades enviadas (texto tipo JSON). Avalie nomes
  das chaves E presença das obrigatórias.
- **Descrição Ação** — descrição em português do que dispara o evento (checar coerência
  semântica). Em murais antigos essa coluna pode aparecer como **`Ação`**; é a mesma coisa.
- **application_name** / **application_feature** / **session_id** / **[product]_id** — no template
  padrão essas obrigatórias têm **coluna própria**, fora de "Atributos customizados".
- **application_area** / **application_page** — só no AfyaOne, que exige as duas.
- **Feedback Claude** — onde o parecer é escrito.

🔴 **Antes de cobrar propriedade obrigatória como ausente, leia o schema inteiro da tabela**
(colunas via `table_list_rows` — ver fluxo Modo A; até 14/09/2026 o `layout_read` structured
ainda expõe `_schema=`/`_row_count`, mas some nessa data).
Lido do board de referência `uXjVHKNS2EI=` em 24/08/2026, o template padrão tem
`application_name`, `application_feature`, `session_id` e `[product]_id` como **colunas**, não como
chaves dentro de "Atributos customizados". Procurar essas chaves só nos atributos produz um parecer
de "falta `session_id`" contra uma tabela que declara `session_id` na coluna ao lado — e isso é
falso-positivo, não achado. Vale também o inverso: o cabeçalho é o literal `[product]_id`
(placeholder), então **a coluna existir não diz qual id o produto manda** — o nome real vem do mapa
de `<produto>_id`, e o preenchimento vem da célula.

⚠️ O board de referência **não é uniforme**: das 3 tabelas-modelo, só uma declara `session_id`.
Avalie contra o schema da tabela que está na sua frente, não contra um schema decorado.

## Regra fundamental sobre a coluna "Feedback Claude"

A skill **NÃO cria colunas** e **NÃO edita o schema**. Antes de avaliar uma tabela,
verifique se o schema já contém a coluna `Feedback Claude` (tipo text).

- Coluna **existe** → avalie e escreva o parecer nela.
- Coluna **NÃO existe** → **apenas avise o usuário** de que a tabela (identifique-a pelo
  título da tela e pela URL/`moveToWidget`) não tem a coluna e por isso **não foi avaliada**.
  Não crie a coluna, não escreva nada.

Ao final, liste as tabelas avaliadas e as puladas por falta da coluna.

## Conceitos: métodos de chamada

Cada registro usa um dos métodos padrão do Segment. O método correto depende do que o
evento representa:

- **track** — "o que o usuário faz". Ações específicas (ex.: `checkout_started`,
  `video_played`). É onde as 6 regras de nomenclatura se aplicam integralmente.
- **identify** — "quem é o usuário". Associa o usuário a um perfil com atributos
  permanentes (ver seção "Regras do identify").
- **page / screen** — "por onde o usuário navegou". Registro de visualização de página web
  (`page`) ou de tela em app mobile (`screen`).

Os métodos `identify`, `page` e `screen` são **tipos de chamada**, não eventos custom — não
os penalize pelas regras de particípio (3) e objeto_ação (4). Se um registro estiver rotulado
como `page`/`screen` mas descrever uma ação custom que deveria ser um `track`, aponte.

## Eventos globais x locais

- **Global** — ação com o mesmo significado em vários produtos; deve ser padronizada em todo
  o ecossistema. Ex.: `checkout_started`, `login`, `logout`, `signup_successful`. Nomes
  globais devem seguir a definição canônica do Martech; não crie variações.
- **Local** — específico de um produto/contexto. Ex.: `items_prescribed`. Segue as 6 regras
  normalmente.

Ao avaliar, se reconhecer um evento que deveria ser global (ex.: um "início de checkout"
nomeado de forma diferente de `checkout_started`), sinalize para alinhamento com o padrão global.

## As 6 regras de nomenclatura

Aplique aos **nomes de eventos** (coluna Evento) e, onde indicado, às **chaves de
propriedade** em Atributos customizados.

1. **snake_case** — minúsculas separadas por underline, em eventos e propriedades compostas.
   - Correto: `video_played` · Incorreto: `VideoPlayed`, `videoPlayed`, `video-played`.
2. **Inglês** — nomes/chaves em inglês. *Exceção:* **valores** voltados ao usuário podem estar
   em português (ex.: `button_name: "Selecionar"`).
   - Correto: `registration_started` · Incorreto: `cadastro_iniciado`.
3. **Verbo no particípio** — o nome do evento indica uma **ação concluída**.
   - Correto: `checkout_abandoned` · Incorreto: `checkout_abandonment`, `checkout_abandon`.
4. **[objeto]_[ação]** — ordem objeto + ação.
   - Correto: `article_clicked` · Incorreto: `clicked_article`.
5. **Identificadores terminam com `_id`** (propriedades).
   - Correto: `whitebook_id`, `session_id`, `receitapro_id` · Incorreto: `whitebook`, `product`.
6. **Booleanas começam com `has_`** (propriedades).
   - Correto: `has_coupon` · Incorreto: `flag_coupon`, `is_coupon`, `coupon`.

**Clareza (regra transversal):** nomes de eventos e propriedades devem ser claros e
descritivos, de modo que qualquer pessoa identifique o que está sendo registrado.

## Exceções às regras de nomenclatura

As exceções são **restritas** e não devem ser expandidas por conta própria:

- **Métodos de chamada**: `identify`, `page`, `screen` (e o tipo `track`) — não são eventos
  custom; isentos das regras 3 e 4.
- **Eventos globais definidos pelo Martech**: um conjunto pequeno e fechado, ex.: `login`,
  `logout`. Só esses fogem do padrão de particípio/objeto_ação. Qualquer outro evento `track`
  deve seguir as 6 regras. Se tiver dúvida se um nome é global-Martech, trate como exceção
  **apenas** para `login`/`logout` e sinalize os demais para validação do Martech.
- **Valores em português** (regra 2): permitidos em valores exibidos ao usuário.

## Clique genérico x evento semântico

Nome conforme e propriedades completas **não bastam**. Um `button_clicked` pode estar certo na
nomenclatura e mesmo assim ser o evento errado. Pedido do MarTech (Raab) no review da
`data-infra-afya`#910: *"verificar se não existem casos que estão como button_clicked e deveriam ser
eventos semânticos"*.

**Os 2 sinais que denunciam, e os dois se medem:**

1. **Já existe evento semântico para a mesma ação.** Se a tabela do evento semântico existe na
   source e o volume dos dois bate, a ação está sendo contada em dois formatos. Casos medidos no
   iClinic entre 15/08 e 14/09/2026: `save_information` (11.857) contra `appointment_summary_saved`
   (11.775); `record_appointment` (29.248) contra `record_appointment_started` (29.900);
   `summary_history` (949) contra `summary_history_viewed` (554).
2. **O clique carrega payload exclusivo dele.** Propriedade que só faz sentido para um
   `button_name` é a assinatura de que ali existe um evento próprio escondido. Caso medido:
   `end_digital_signing`, 211.287 disparos, o único que manda `certificate_kind` e
   `certificate_provider`.

**Como medir** (Modo B, tráfego real): agrupar por `application_feature` e `button_name`, e para
cada propriedade esparsa olhar em quais `button_name` ela aparece. Propriedade concentrada em um
único botão é o sinal 2.

**Como reportar:** `⏳` observação, nomeando o evento semântico que já existe ou o que falta criar.
⚠️ **Não vira mudança no tracking plan** — é mudança no app, e portanto card do time de produto.
Não tentar resolver dentro de uma PR de plano.

## Propriedades globais obrigatórias

Devem estar presentes no objeto `properties` de **todos os eventos `track`** e também em
`page`/`screen`:

| Propriedade | Tipo | Observação |
|---|---|---|
| `application_name` | string | Nome da aplicação (ex.: whitebook, medcel, portal_afya). |
| `application_feature` | string | Recurso/etapa da jornada (ex.: search, home, onboarding). |
| `session_id` | string | ID único da sessão. |
| `<produto>_id` | string | Identificador do usuário **no produto**. O nome é por produto — ver tabela abaixo. **Só em eventos identificados** — NÃO enviar em eventos anônimos. |

- **AfyaOne** exige, além dessas, mais duas: `application_area` e `application_page`.
- Ao avaliar, verifique se essas chaves aparecem em Atributos customizados. Aponte as que
  faltarem. Se o evento for anônimo (antes de login/identificação), a **ausência** do
  `<produto>_id` é o esperado — não marque como erro; a **presença** dele em evento anônimo é que
  deve ser sinalizada.

### O `product_id` é nomeado por produto — não é uma propriedade literal

⚠️ **Erro clássico de review: apontar "falta `product_id`".** A propriedade global obrigatória é o
*identificador do usuário no produto*, e o nome real dela é **`<produto>_id`**. Praticamente nenhuma
source de produto tem uma coluna chamada `product_id` — e não deve ter. Antes de apontar ausência,
descubra qual é o `<produto>_id` daquela source.

Mapa confirmado em `raw_tracking_prod` (28/07/2026; as duas últimas linhas remedidas em 24/08/2026):

| Source de tracking | Identificador do usuário no produto |
|---|---|
| `iclinic_events` | `iclinic_id` |
| `afya_one_app_events` / `afya_one_web_events` | `afya_id` |
| `portal_afya_event` | `portalafya_id` |
| `whitebook_web_events`, `wb_assist_*`, `afya_anywhere_events` | `whitebook_id` |
| `prescription_segment` (ReceitaPro) | `receitapro_id` |
| `prescription_events_afyarx` (legado AfyaRX) | `physician_id` |
| `educon_lll_events` | **sem `<produto>_id` confirmado** — candidato: `medcel_id` (ver aviso abaixo) |
| `medcel_snowplow` | **sem `<produto>_id` confirmado** — o id de pessoa é `user_id`, mas o preenchimento varia MUITO por tabela (ver aviso abaixo) |

Fora do Miro, confirme com:

```sql
SELECT table_schema, column_name, count(*) AS tabelas
FROM raw_tracking_prod.information_schema.columns
WHERE table_schema = '<source>' AND column_name LIKE '%\\_id'
GROUP BY 1, 2 ORDER BY 3 DESC
```

#### Não existe exceção de `product_id` literal — as duas que pareciam ser, não são

⚠️ Uma versão anterior deste mapa registrava `educon_lll_events` e `medcel_snowplow` como exceções
que usariam `product_id` como identificador do usuário. **O dado contradiz isso.** Medido em
`raw_tracking_prod` (24/08/2026), nas duas sources `product_id` é o **item do catálogo**, não a
pessoa:

| Medição (30 dias, salvo onde indicado) | Resultado |
|---|---|
| `educon_lll_events.checkout_started` | 6.432 eventos · `product_id` **163 distintos**, 100% preenchido · `medcel_id` **1.370 distintos** (63,7% preenchido) · `student_id` 795 |
| `educon_lll_events.cart_abandoned` | 1.218 eventos · `product_id` **93 distintos** · `user_id` 323 · `session_id` 1.218 (1 por evento) |
| `medcel_snowplow.br_com_medcel_contract_1` (histórico completo) | 24,45 mi eventos · `product_id` **168 distintos** ao lado de `product_name` **174 distintos** · `user_id` **100% nulo nesta tabela** |
| `medcel_snowplow.br_com_medcel_user_1` (histórico completo) | 363,8 mi eventos · `user_id` **113.235 distintos**, ~100% preenchido |
| `medcel_snowplow.br_com_medcel_contract_2` (histórico completo) | 123,3 mi eventos · `user_id` 22.475 distintos, só **6%** preenchido |

**O discriminador é a cardinalidade:** catálogo tem dezenas/centenas de valores estáveis; pessoa tem
milhares, crescendo com a base. `product_id` empatando com `product_name` fecha o caso. Em
`medcel_snowplow` ele só aparece nas tabelas `br_com_medcel_contract_*`, sempre ao lado de
`product_name` — é o produto contratado, e `medcel_id` não existe nessa source.

O contraste dentro da **mesma** source é a melhor ilustração da regra: `product_id` tem **168**
valores distintos e `user_id` tem **113.235**. Três ordens de grandeza separam catálogo de pessoa.

⚠️ **Mas `user_id` no `medcel_snowplow` não é um id confiável de saída: o preenchimento varia por
tabela**, de ~100% em `br_com_medcel_user_1` a **6%** em `br_com_medcel_contract_2` e **0%** em
`br_com_medcel_contract_1`. Ou seja, ele é o candidato certo a id de pessoa e ainda assim **não
serve para medir cobertura da source como um todo** — meça tabela a tabela, nunca extrapole de uma
tabela para a source. Esse é o mesmo erro de leitura que "coluna existe = propriedade é enviada".

**Como agir nessas duas sources:** não cobre "falta `product_id`" e **não aceite** `product_id` como
cumprindo o papel do id de usuário. Aponte com a evidência — em `educon_lll_events` o candidato é
`medcel_id` — e trate a escolha do nome canônico como **decisão do MarTech**. Este mapa não tem
autoridade para batizar as duas.

⚠️ **Generalize o método, não a tabela:** antes de aceitar qualquer coluna como o `<produto>_id` de
uma source nova, meça a cardinalidade dela contra o volume de eventos. Nome plausível não é prova —
foi exatamente assim que `product_id` entrou neste mapa como exceção.

O que **de fato** deve ser sinalizado:

- **Ausência do `<produto>_id`** nos eventos identificados daquela source (usando o nome certo).
- **Id cross-produto ocupando o lugar dele.** `sso_id` é a identidade SSO da Afya e vale entre
  produtos; ele **não** cumpre o papel do id no produto. O mesmo para `user_id`. Quando aparecem
  sozinhos, o evento não tem identificador de produto — aponte, mas como "o `<produto>_id` não está
  sendo enviado", não como "usaram o nome errado".
- **Coluna existe e chega vazia.** Presença no schema não é preenchimento: a coluna sobrevive no
  lake muito depois de o app parar de enviar. Meça a taxa de preenchimento, e ao longo do tempo
  (série mensal) — foi assim que se descobriu que o ReceitaPro trocou `receitapro_id` por `sso_id`
  ao longo de nov/2025→jun/2026, com uma versão antiga de app sustentando a cauda.
- **Identificadores extras** (`physician_id`, `sso_id`, `patient_id`) são bem-vindos como
  enriquecimento e não devem ser cobrados como erro — só não substituem o `<produto>_id`.

Se o produto for novo e você não souber qual é o `<produto>_id` canônico, **não invente**: sinalize
para validação do Martech.

Propriedades **default** (userId, anonymousId, context, device, os, timestamps, messageId,
version, etc.) são coletadas automaticamente pelo SDK da Segment. Não precisam estar na tabela;
não as cobre como obrigatórias custom.

## Regras do identify

`analytics.identify` associa o usuário a um perfil com atributos permanentes. Deve ser
disparado **junto com** os eventos: `signup_successful`, `login`, `call_me_now_form_converted`,
`profile_updated`.

Traits obrigatórios no `identify`:

| Trait | Tipo | Observação |
|---|---|---|
| `user_id` | string/null | `null` enquanto o usuário não estiver autenticado (atribuído via vuc_id no CDP). |
| `application_name` | string | — |
| `application_feature` | string | — |
| `session_id` | string | — |
| `<produto>_id` | string | Identificador do usuário no produto (`iclinic_id`, `afya_id`, `receitapro_id`…). |
| `email` | string | — |
| `name` | string | — |

Obs.: `anonymousId` é campo default do payload do Segment (fora de `traits`) e é gerado pelo SDK; não deve ser cobrado como trait/tabela.

Enriquecimento recomendado (não obrigatório): `crm`, `specialty`, `formation_degree`, etc.

Ao avaliar um `identify`, cheque presença dos traits obrigatórios e a regra do `user_id = null`
antes da autenticação. O `anonymousId` **não** está na tabela acima de propósito (é default do
payload, não trait) — **não o cobre como faltante**, seja escrito como `anonymousId` ou
`anonymous_id`; é o mesmo tratamento das propriedades default descrito acima.

## Fluxo de execução — Modo A (Miro)

Use as ferramentas do Miro; marque `invocation_source: "skill"`.

🔴 **Deprecação Miro MCP — remoção em 14/09/2026:** `layout_read`, `board_list_items`,
`layout_create`/`layout_update`/`layout_get_dsl` saem nessa data. **Não dependa deles no fluxo
principal.** Papéis corretos:

| Precisa | Tool |
|---|---|
| **Achar** frames/áreas/tabelas | `canvas_search` (`overview` / `areas` / `matches`) |
| **Ler** geometria/conteúdo do escopo | `canvas_read_as_svg` (após search: `widget_ids` do container **ou** os quatro `scope_*`) |
| **Schema + linhas** da tabela | `table_list_rows(?moveToWidget=<table_id>, limit=…)` — devolve **column metadata** (`columnTitle` / tipos) e as linhas; isso substitui o `_schema=` / `_row_count` do `layout_read` structured |

`canvas_search` **não** substitui `layout_read`: serve para localizar, não para ler schema.

1. **Localize o board**: `canvas_search` → anote ids/URLs dos frames e tabelas. Em seguida
   `canvas_read_as_svg` no frame (`widget_ids` ou `?moveToWidget=<frame_id>` + scope) para ver
   títulos de tela e posição das tabelas. Evite `context_get` (502 frequente).
2. **Para cada tabela**, chame `table_list_rows` (mesmo com `limit: 1` basta para o schema) e
   verifique se existe coluna `Feedback Claude`.
   - Sem a coluna → lista de "puladas", não escreva.
   - Com a coluna → passo 3 (releia com `limit` alto se precisar de todas as linhas).
3. **Leia as linhas**: `table_list_rows` (com `limit` alto se a tabela for grande). Guarde o
   `rowId` de cada linha. Extraia Evento, Atributos customizados e Ação. Parseie Quill delta
   quando a célula vier como `{"format":"delta","ops":[...]}`.
4. **Avalie cada linha** em duas dimensões:
   - **Nomenclatura**: nome do evento (regras 1–4 + clareza, respeitando exceções e global x
     local); chaves das propriedades (regras 1, 2, 5, 6).
   - **Completude**: método de chamada coerente; propriedades globais obrigatórias presentes
     (`application_name`, `application_feature`, `session_id`, `<produto>_id` quando identificado;
     `application_area`/`application_page` no AfyaOne); para `identify`, os traits obrigatórios.
     Procure cada obrigatória **nas duas** possibilidades — coluna própria da tabela **e** chave em
     "Atributos customizados". Só é ausência quando não está em nenhuma das duas. E **presente
     significa existe E está preenchida**: coluna declarada com célula vazia é ausência, não
     presença — é a mesma regra de "presença no schema não é preenchimento" que vale no Modo B.
     Quando a célula está vazia, diga qual dos dois casos é: não se aplica (evento anônimo) ou
     faltou.
   - **Coerência semântica** com a coluna "Descrição Ação" (ou "Ação", em murais antigos).
5. **Escreva o parecer**: `table_sync_rows` com o `rowId` e a célula
   `{"columnTitle": "Feedback Claude", "value": "<parecer>"}`.
6. **Resumo final**: tabelas avaliadas, contagem por status, e tabelas puladas por falta da coluna.

## Fluxo de execução — Modo B (tráfego real, sem Miro)

Cruze **o que foi declarado** com **o que chega**. Duas fontes:

| Fonte | Onde |
|---|---|
| Tracking plan declarado | `data-infra-afya/segment/events/<app>/**/*.json` (1 JSON por rule; no Afya One use `app/` e `web/` conforme a surface) + o `terragrunt.hcl` de `segment/Prod/tracking_plan/tracking_plan-<app>/` (ou `tracking_plan-afya-one-app`) para o modo do catálogo. Keys devem ser únicas por surface — ver `segment-tracking-plan` / `references/afya-one-events-layout.md`. |
| Tráfego real | `raw_tracking_prod.<source>` — **`<source>` é o slug da source no Segment, que é o próprio nome do schema** (ex.: `prescription_segment`). Mesmo placeholder em todas as queries abaixo. |

Acesso ao lake: profile `prod` + warehouse SQL de prod (ver a skill/memória de query ad-hoc no
Databricks). Só leitura — nunca escreva no `raw_tracking_prod`.

1. **Leia o plano declarado.** Liste os `*.json` e extraia, por rule: `key`, `type`
   (TRACK/IDENTIFY), propriedades, `enum`s e a lista `required`. Confira também no `terragrunt.hcl`
   se `allow_unplanned_events` é `false` (catálogo fechado) e se `allow_event_on_violations` é
   `true` (violação monitorada) — isso muda a gravidade do parecer.
2. **Inventarie o que está vivo.** A tabela `tracks` tem todos os eventos track da source:

   ```sql
   SELECT event, event_text, count(*) AS total,
          sum(CASE WHEN timestamp >= current_timestamp() - INTERVAL 30 DAYS THEN 1 ELSE 0 END) AS d30,
          min(timestamp) AS first_seen, max(timestamp) AS last_seen
   FROM raw_tracking_prod.<source>.tracks
   GROUP BY 1, 2 ORDER BY d30 DESC, total DESC
   ```

   `identify`, `page` e `screen` **não** estão em `tracks` — vêm de `identifies`, `pages` e
   `screens`. Compare o inventário com o plano nas duas direções: rules **declaradas sem tráfego**
   (instrumentação que nunca saiu) e eventos **vivos fora do plano** (bloqueados se o catálogo é
   fechado).
3. **Colha as violações que o Segment já registrou.** As tabelas costumam ter
   `context_protocols_violations` (JSON array). É o Protocols dizendo campo e motivo:

   ```sql
   SELECT x.type, x.field, count(*) AS n, min(x.description) AS descricao
   FROM (SELECT explode(from_json(context_protocols_violations,
                'array<struct<description:string,field:string,type:string>>')) AS x
         FROM raw_tracking_prod.<source>.<evento>
         WHERE context_protocols_violations IS NOT NULL AND timestamp >= date('<data_do_apply>'))
   GROUP BY 1, 2 ORDER BY n DESC
   ```

4. **Meça a completude de verdade.** Para cada rule viva, taxa de preenchimento das obrigatórias
   (`count` vs `sum(CASE WHEN <col> IS NOT NULL ...)`) e os valores distintos dos campos com `enum`,
   para achar o que está fora da lista.
5. **Aplique as regras** de nomenclatura e completude normalmente, agora sobre nomes reais de evento,
   nomes reais de coluna e valores reais.
6. **Entregue o parecer** em markdown ou card Jira, com uma linha por correção: *o que chega hoje →
   o que deve passar a chegar*, com o volume ao lado para dar prioridade. Separe explicitamente o
   que é **erro do app** do que é **erro do plano** — os dois acontecem, e o dev não deve receber
   uma lista onde tudo é culpa dele.

### Armadilhas do Modo B

- **Source sem tracking plan não tem violação para colher — nem a coluna.** Antes de rodar a query
  do passo 3, confirme que a coluna `context_protocols_violations` existe na source. Medido em
  24/08/2026, `educon_lll_events` e `medcel_snowplow` não têm **nenhuma** tabela com essa coluna, e o
  `data-infra-afya/segment/Prod/tracking_plan/` cobre só 7 apps (`afya-one`, `afya-one-app`,
  `afya-sso`, `anywhere`, `iclinic-events`, `receita-pro`, `whitebook`). Sem Protocols não há
  catálogo fechado nem validação: propriedade nova **não é descartada**, entra calada e vira coluna
  no lake. O Modo B ainda funciona nessas sources (inventário por `tracks` + taxa de preenchimento),
  mas o passo 3 não se aplica e a recomendação de processo passa a ser **"criar o plano"**, não
  "corrigir violações". Não relate "0 violações" onde não existe validador.
- **Violação só existe depois do apply do plano.** Antes disso o Protocols não valida nada, então
  período anterior aparece limpo por **ausência de validação**, não por conformidade. Descubra a data
  do apply e meça a taxa só na janela posterior — senão você reporta "2% de violação" onde o real é
  40%.
- **Coluna no schema ≠ propriedade sendo enviada.** O schema do lake acumula tudo que já passou; a
  coluna sobrevive anos depois de o app parar de mandar. Sempre meça preenchimento, e em **série
  mensal** — foi assim que se detectou uma migração silenciosa de identificador ao longo de 8 meses,
  sustentada no fim só por uma versão antiga de app em campo (filtre por `context_app_version` e
  `host_application` para achar a origem da cauda).
- **Evento morto ainda aparece no `tracks`.** Volume histórico alto não significa vivo — olhe
  `last_seen`. Evento morto com nome fora do padrão entra no parecer como "não ressuscitar com esse
  nome", não como correção urgente.
- **`page`/`screen` são validados por rules TRACK.** Uma rule declarada como TRACK com key
  `Page Viewed` / `Screen Viewed` valida as chamadas `analytics.page()`/`screen()`, cujos dados caem
  em `pages`/`screens`. Não reporte isso como método errado.
- **Props de contexto de página do Segment** (`name`, `path`, `url`, `referrer`, `search`, `title`)
  são standard e não entram no plan — não as cobre como faltantes.
- **Catálogo fechado é uma nota de processo obrigatória no parecer:** com
  `allow_unplanned_events = false`, evento não declarado é **descartado e não chega no lake**. Toda
  mudança de evento ou propriedade exige PR no `data-infra-afya` no mesmo ciclo do deploy do app.

## Formato do parecer

No Modo A, o parecer vai na célula "Feedback Claude" (um por linha/evento). No Modo B, os mesmos
marcadores valem no markdown ou no card, agrupados por evento. Em ambos:

Conciso e acionável. Marcadores:

- `✅` conforme — atende às regras (nomenclatura + completude).
- `⚠️` ajustar — viola regra; **sugira a correção**.
- `⏳` observação — no padrão com ressalva (exceção, semântica, global x local, duplicidade).

Cubra nomenclatura E completude quando relevante.

**Exemplo 1 (conforme, mas com observação):**
`button_clicked` com props completas →
`✅ Nome conforme (snake_case, inglês, particípio, objeto_ação). Propriedades obrigatórias presentes (application_name, application_feature, session_id, iclinic_id). _id OK.`
⚠️ **Props completas não fecham o parecer de um clique genérico.** Antes do `✅`, rodar a checagem
de [clique genérico x evento semântico](#clique-genérico-x-evento-semântico). Se o botão duplicar um
evento semântico que já existe, ou carregar payload exclusivo, o parecer leva `⏳` junto.

**Exemplo 2 (ajustar nome):**
`checkout_abandonment` →
`⚠️ Nome fora do particípio (regra 3). Correto: checkout_abandoned.`

**Exemplo 3 (ajustar completude):**
`video_played` sem session_id →
`✅ Nome conforme. ⚠️ Completude: falta a propriedade obrigatória session_id. Se for evento identificado, confirmar também o id do usuário no produto (whitebook_id).`

**Exemplo 4 (global):**
evento de início de checkout nomeado fora do padrão →
`⚠️ Evento global: use o nome canônico do Martech checkout_started em vez de uma variação.`

**Exemplo 5 (identify):**
`identify` →
`⏳ Método identify (exceção às regras 3 e 4). Cheque traits obrigatórios (user_id null até auth, application_name, application_feature, session_id, receitapro_id, email, name) e o disparo junto a signup_successful/login/profile_updated. anonymousId é default do payload, não trait — não cobre como faltante.`

**Exemplo 6 (id de produto em evento anônimo):**
`iclinic_id` presente antes do login →
`⚠️ iclinic_id não deve ser enviado em evento anônimo — remover até a identificação do usuário.`

**Exemplo 7 (id de produto ausente / substituído por id cross-produto):**
evento identificado chegando só com `sso_id` →
`⚠️ Completude: o id do usuário no produto (receitapro_id) não está sendo enviado. sso_id é identidade SSO da Afya (cross-produto) e não cumpre esse papel. Se a coluna existe mas chega vazia, medir preenchimento por mês antes de concluir.`

## Cuidados

Nos dois modos:

- Exceções de nomenclatura são fechadas (métodos de chamada + globais Martech como login/logout);
  não amplie a lista — na dúvida, sinalize para validação do Martech.
- Itens que mudam o contrato (enum, `required`, nome de propriedade) são **decisão do Martech** —
  aponte e recomende, mas não trate como tarefa mecânica de dev.

Modo A (Miro):

- Só escreva em `Feedback Claude`; nunca altere Evento, Ação ou Atributos.
- Não invente `rowId`: use os retornados por `table_list_rows`.
- Se `table_sync_rows` retornar "Column ... not found", trate como "pulada" e avise.
- Muitas tabelas → processe tela a tela e dê progresso.

Modo B (lake):

- Acesso somente leitura ao `raw_tracking_prod`; nada de DDL/DML.
- Não conclua nada de janela onde o plano ainda não estava aplicado (ver Armadilhas).
- Não altere os JSON do tracking plan no mesmo passo do parecer — o parecer é o insumo da decisão,
  e a mudança de plano vira PR separado (fluxo da skill `segment-tracking-plan`).
