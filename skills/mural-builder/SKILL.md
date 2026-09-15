---
name: mural-builder
description: "Transforma requisitos de produto (objetivo, contexto, perguntas de negócio e acionáveis, fluxos, wireframes, screenshots, telas do Miro, diagramas) em uma especificação de tracking de CDP/Segment e materializa num board do Miro, no template padrão da Afya (frame por funcionalidade, doc de necessidade de produto, telas numeradas, tabela de eventos). Use SEMPRE que o usuário pedir para documentar, especificar, mapear ou planejar o tracking de uma funcionalidade/jornada nova, ou criar um board de tracking no Miro do zero — mesmo sem citar Miro (ex.: 'documenta o tracking dessa tela', 'mapeia os eventos dessa jornada'). DIFERENTE de martech-event-review (avalia tabela JÁ existente) e segment-tracking-plan (instrumenta via IaC mural JÁ especificado) — aqui o foco é GERAR a spec e o board pela primeira vez. Ao final, encadeia automaticamente a martech-event-review sobre a tabela recém-criada."
---

# Criar Board de Especificação de Tracking (Miro) a partir de Requisitos de Produto

Esta skill parte de requisitos de produto **ainda não estruturados** — objetivo da
funcionalidade, contexto, perguntas de negócio, perguntas acionáveis, fluxos, wireframes,
screenshots, telas do Miro, diagramas — e produz uma **especificação de tracking de CDP/Segment**
materializada em um **board do Miro**, no template padrão da Afya (board de referência
`uXjVHKNS2EI=`).

## Onde esta skill entra no pipeline

```
requisitos de produto → [ESTA SKILL: gera a spec e cria o board] → martech-event-review (valida nomenclatura) → segment-tracking-plan (instrumenta via IaC)
```

- **`martech-event-review`** avalia uma tabela **já existente**; esta skill é o passo **anterior**:
  cria a tabela pela primeira vez, já tentando nascer dentro do padrão.
- **`segment-tracking-plan`** assume o mural como fonte da verdade e apenas instrumenta; esta
  skill é quem **produz** esse mural.
- Ao final, esta skill **encadeia automaticamente** a `martech-event-review` sobre a tabela que
  acabou de criar (ver Passo 6) — não pare antes disso.

## ⭐ Prioridades (ordem fixa, nunca inverta)

1. **Consultar a base de conhecimento antes de propor qualquer coisa**: as 6 regras de
   nomenclatura, propriedades globais obrigatórias, regras de `identify` e a distinção
   global x local, todas descritas na skill `martech-event-review` — aplique-as já na geração,
   não deixe para a revisão corrigir depois.
2. **Reutilizar eventos e propriedades já existentes sempre que possível** (ver Passo 2).
3. **Só propor evento/propriedade novo quando não houver opção adequada** — e, nesse caso,
   explicar por que um evento existente não serve.
4. **Seguir rigorosamente nomenclatura e diretrizes** — nunca ignore ou contradiga a base de
   conhecimento, mesmo que o requisito do usuário sugira um nome fora do padrão.

## Entradas

O usuário pode fornecer, em qualquer combinação e em qualquer ordem:

- Objetivo da funcionalidade e contexto do produto.
- Perguntas de negócio e perguntas acionáveis.
- Fluxos, wireframes, screenshots, telas do Miro, diagramas.

### Formato canônico: `assets/spec-tracking.template.md`

Qualquer que seja a entrada, ela é **normalizada** para o formato de
`assets/spec-tracking.template.md` (telas × eventos) antes de tocar no Miro. Ele é ao mesmo tempo:

- o **formato de entrega** para quem já sabe o que quer (o solicitante preenche e manda pronto,
  pulando o Passo 3); e
- o **artefato do Passo 3** quando a entrada é solta (você gera a spec preenchida e confirma com o
  usuário antes de materializar).

Trabalhar sempre com esse arquivo no meio é o que torna o Passo 5 idempotente: ele carrega a chave
`(TELA, Evento)` e o mapa campo → coluna do board.

Considere **todas** as entradas fornecidas antes de gerar a especificação — não responda com base
em apenas uma parte do que foi enviado. Se informação essencial estiver faltando (ex.: não dá para
saber o momento exato do disparo de um evento, ou a tela não tem nome), **pergunte antes de gerar**
em vez de assumir.

## Passo 1 — Análise de imagens (quando houver wireframe/screenshot/tela do Miro)

Para cada imagem/tela:

1. Identifique os componentes de interface (botões, campos, cards, listas, navegação).
2. Entenda o fluxo do usuário — o que ele está tentando fazer nessa tela, e o que vem antes/depois.
3. Identifique elementos passíveis de tracking.
4. Relacione cada elemento candidato ao **comportamento esperado do usuário**, não apenas ao
   elemento visual em si (um clique só vira evento se representar uma decisão/ação relevante).

**Não** sugira tracking para elementos sem valor analítico (divisores visuais, ícones puramente
decorativos, elementos que não mudam estado nem indicam intenção do usuário).

## Passo 2 — Verificar o que já existe (reuso antes de criar)

Antes de propor qualquer evento, verifique o catálogo de eventos/problemas já registrados:

- **Fonte primária**: a lista do SharePoint **"Lista de acompanhamento de problemas"**, no site
  `MartechAfyaOne`:
  `https://nreeducacional.sharepoint.com/sites/MartechAfyaOne/Lists/Lista%20de%20acompanhamento%20de%20problemas/AllItems.aspx`.
  - **Acesso restrito**: só contas Afya (`@afya.com.br`) autenticadas conseguem abrir esse link —
    contas de terceiros não têm acesso. Use os conectores de Microsoft 365 já disponíveis
    (`sharepoint_search` para achar itens/documentos relacionados, `read_resource` para ler o
    conteúdo completo a partir da URI retornada).
  - **Limitação conhecida**: as ferramentas de Microsoft 365 hoje disponíveis leem bem
    **bibliotecas de documentos e páginas**, mas não há uma ferramenta dedicada para ler itens de
    uma **Lista** do SharePoint (esse link aponta para uma Lista, não uma biblioteca). Tente
    `sharepoint_search` com termos da funcionalidade/evento em questão; se não retornar os itens da
    lista, **não invente conteúdo** — avise o usuário que a lista não pôde ser consultada
    automaticamente por essa via e peça que ele cole os itens relevantes (ou exporte a lista) para
    checagem de reuso.
- **Fontes que não dependem do SharePoint** (use-as sempre, e não só como plano B — elas dizem o
  que de fato existe hoje):
  - **Tracking plan em IaC**: `data-infra-afya/segment/events/<app>/**/*.json`, um arquivo por rule,
    com propriedades, `enum` e `required`. É o catálogo declarado do que já foi instrumentado. No
    **Afya One** há duas surfaces (`events/afya-one/app` e `events/afya-one/web`); jornadas de Learn
    costumam viver em `learn-engagement/` (não inventar pasta por feature). Em 24/08/2026 há plano
    de prod para 7 apps (`afya-one`, `afya-one-app`, `afya-sso`, `anywhere`, `iclinic-events`,
    `receita-pro`, `whitebook`) — produto fora dessa lista **não tem catálogo fechado**, então
    evento novo entra calado e o reuso é ainda mais importante. Detalhes:
    `segment-tracking-plan/references/afya-one-events-layout.md`.
  - **Tráfego real**: `raw_tracking_prod.<source>.tracks` lista todo evento `track` que a source já
    emitiu, com `first_seen`/`last_seen`. Serve para achar o evento que existe mas ninguém
    documentou — e para não ressuscitar nome fora do padrão que já morreu. Só leitura.
- Ao propor um evento, **primeiro** verifique se ele já cobre o comportamento descrito. Só declare
  "novo evento" depois de checar contra esse catálogo.

## Passo 3 — Gerar a especificação (rascunho em texto, antes de tocar no Miro)

Para **cada evento recomendado**, produza:

- **Nome do evento** (seguindo as 6 regras de nomenclatura da `martech-event-review`: snake_case,
  inglês, particípio, objeto_ação, `_id` em identificadores, `has_` em booleanas — respeitando as
  exceções fechadas de métodos de chamada e globais Martech).
- **Momento exato do disparo** (ex.: "ao clicar no botão Confirmar, após validação do formulário").
- **Objetivo do evento** (que pergunta de negócio/acionável ele ajuda a responder).
- **Propriedades recomendadas**, incluindo as globais obrigatórias (`application_name`,
  `application_feature`, `session_id`, `<produto>_id` quando identificado; `application_area` e
  `application_page` no AfyaOne) mais as específicas do evento, com tipo e obrigatoriedade.

  ⚠️ **A obrigatória é o `<produto>_id`, nunca `product_id` literal.** O nome real é por produto
  (`iclinic_id`, `afya_id`, `receitapro_id`, `whitebook_id`, `portalafya_id`…) — use o mapa da
  `martech-event-review` e nunca gere uma spec pedindo `product_id`, senão a própria review vai
  reprovar o que esta skill acabou de propor. Se a source for nova e o id canônico não existir no
  mapa, escreva `a definir (MarTech)` em vez de inventar: em `educon_lll_events` e
  `medcel_snowplow`, `product_id` existe e é o **item do catálogo**, não a pessoa.
- **Justificativa** da recomendação.
- Se for evento **novo**: por que nenhum evento existente (Passo 2) cobre o caso.

### Validação antes de finalizar o rascunho

Antes de apresentar ao usuário, verifique:

- Há eventos duplicados entre si na proposta?
- Há eventos específicos demais que poderiam ser generalizados/reaproveitados?
- As propriedades seguem o padrão (nomenclatura + obrigatórias)?
- O conjunto de eventos responde a **todas** as perguntas de negócio informadas?
- O conjunto de eventos permite responder às perguntas acionáveis informadas?

Se encontrar lacunas, **indique-as explicitamente** — não preencha com suposições.

### Formato da resposta (rascunho, antes de escrever no Miro)

1. Resumo da solução.
2. Eventos recomendados.
3. Propriedades de cada evento.
4. Cobertura das perguntas de negócio.
5. Cobertura das perguntas acionáveis.
6. Observações e melhorias sugeridas.

Apresente esse rascunho ao usuário. Se houver ajuste, incorpore antes de ir para o Passo 4. O
objetivo final é o **board consistente**, não a resposta em texto — este rascunho é uma etapa de
confirmação, não o entregável.

## Passo 4 — Board e frame de destino

Pergunte (se não tiver sido informado):

- **Board de destino**: URL do board Miro onde a especificação deve ser adicionada. Pode ser o
  próprio board-template/vigente (`uXjVHKNS2EI=`) ou outro indicado pelo usuário — este board é
  **vivo**: cada funcionalidade/jornada nova vira um novo frame dentro dele, ele não é recriado do
  zero a cada uso.
- **Tipo de seção**, pelo formato do conteúdo:
  - **Jornada/fluxo com telas** → frame no padrão `[Nome da funcionalidade]` (telas numeradas +
    tabela por tela).
  - **Evento pontual analítico/ativação de marketing**, sem telas de fluxo → seção "Eventos
    Pontuais Analíticos e/ou Ativação Marketing".
  - **Novo `page_viewed`/`button_clicked` avulso, fora de jornada** → seção "Registro de novos
    Pages e/ou button_clicked (sem jornada)".

Use `canvas_search` (`overview` / `areas`) para **achar** área livre e frames irmãos; em seguida
`canvas_read_as_svg` no escopo escolhido para **ler** geometria/estilo (cores, tamanhos, legendas
amarelas) — **não recrie a legenda do zero**, replique o padrão visual já existente no board.
Evite `context_get` (502 frequente).

🔴 `layout_read` / `board_list_items` / `layout_*` de escrita estão **deprecated e saem em
14/09/2026**. Não dependa deles. Schema de tabela = column metadata de `table_list_rows` (não
`_schema=` do `layout_read`).

## Passo 5 — Materializar no Miro

Para o padrão de **jornada com telas** (o mais comum):

1. Crie um novo `FRAME` com o nome real da funcionalidade (substitui `[Nome da funcionalidade]`),
   posicionado ao lado dos frames existentes (não sobreponha).
2. Dentro do frame, crie (via `canvas_create_from_svg` / `doc_create` / `table_create` — **não**
   use `layout_create`, removido em **14/09/2026**):
   - Um `DOC` **"Necessidade de Produto"** com a lista real de perguntas de negócio e seus
     acionáveis, no formato `- Pergunta N` / `  Acionável N` (espelha o padrão do template).
   - Um retângulo/imagem por tela (**"TELA N"** → nome real da tela). Se o usuário forneceu a
     imagem/screenshot, insira-a (`Miro:image_create`, se disponível); caso não haja imagem, deixe
     o retângulo rotulado com o nome da tela.
   - Círculos numerados sobre cada tela marcando o ponto exato do disparo de cada evento — a
     numeração **reinicia a cada tela** (mantém o padrão do template: evento 1, 2, 3... por tela).
   - Uma `TABLE` por tela com o schema:
     ```
     Evento:select(page_viewed#bd0a0a, button_clicked#6631d7, video_played#305bab,
     video_paused#a0c4fb, video_completed#c6dcff, card_clicked#067429) |
     Atributos customizados:text | Descrição Ação:text | application_name:text |
     application_feature:text | session_id:text | [product]_id:text |
     Status:select(Pendente#ffc6c6, Em andamento#fff6b6, Concluído#adf0c7) |
     Data da implementação:date | Device:multiselect(Tablet e mobile#d6d6d6, Desktop#595959,
     All devices#1a1a1a) | Aprovação EA:select(Aprovado#adf0c7, Revisar#fff6b6,
     Pendente aprovação#ffc6c6) | Observação:text | Feedback Claude:text
     ```
     Este é o `_schema` do board de referência `uXjVHKNS2EI=` (lido coluna por coluna em
     24/08/2026, com as cores originais), com **uma** alteração deliberada: a penúltima coluna
     chama-se `Status EA` no template e aqui está como **`Aprovação EA`**, porque `Status EA` é
     **impossível de criar por API** ao lado de `Status` (ver o bloco 🔴 abaixo). Use este schema
     como está para criar; para **ler** tabela que já existe, o nome é o que estiver nela.
     Quatro detalhes que erram fácil:

     - A coluna de descrição chama **`Descrição Ação`**, não `Ação`.
     - `application_name`, `session_id` e `[product]_id` são **colunas próprias** da tabela — o
       template as tira de dentro de "Atributos customizados". Preencha nelas.
     - O template **não tem** `application_area`/`application_page`. Se o produto for AfyaOne (que
       exige as duas), acrescente-as como colunas extras em vez de escondê-las nos atributos.
     - A coluna de aprovação tem as opções `Aprovado`/`Revisar`/`Pendente aprovação` e **não** se
       chama `Status MarTech`. No template ela é **`Status EA`**; em tabela que você criar ela sai
       como **`Aprovação EA`**, pelo motivo do bloco 🔴 abaixo. Trate os dois nomes como a mesma
       coluna.

     **Importante**: o template original **não tem** a coluna `Feedback Claude` — adicione-a
     sempre, pois é ela que permite o encadeamento automático com a `martech-event-review` no
     Passo 6. As opções do `select` de Evento devem incluir os nomes reais propostos, somados aos
     valores padrão já usados no template.

     ⚠️ **O próprio board de referência não é uniforme:** das 3 tabelas-modelo lidas, só uma tem a
     coluna `session_id`. Trate o schema acima como o alvo (é o mais completo) e, se o board de
     destino tiver uma variante, **siga a variante do destino** para não criar tabela incompatível
     com as vizinhas — mas nunca deixe de acrescentar `Feedback Claude`.

     🔴 **`Status` + `Status EA` na mesma tabela é impossível via API — e o bloqueio é pelo TÍTULO.**
     Medido em 24/08/2026: `table_create` com as duas colunas falha inteiro com
     `Unable to create column 'Status EA': field with role=com.miro.system.status already exists`.
     Só **uma** coluna por tabela recebe o papel de status do Miro, e quem decide é o título — trocar
     o tipo não resolve (testado com `select` e `multiselect`, os dois falham). O contorno que
     funciona é **renomear a segunda mantendo `select` e as mesmas opções**: `Aprovação EA` cria sem
     erro e preserva o dropdown colorido.

     Consequência prática: **o `_schema` do board de referência não é reproduzível por API ao pé da
     letra.** Ao criar tabela nova, use `Aprovação EA` e registre a divergência no resumo do Passo 7
     — renomear a coluna do template é decisão do MarTech, não sua. Em tabela **já existente** com
     `Status EA`, não tente renomear nada: leia e escreva na coluna como ela está.
3. Preencha as linhas da tabela via `Miro:table_sync_rows`, uma linha por evento, com os dados do
   rascunho aprovado no Passo 3. Em "Atributos customizados", registre as propriedades como texto
   (formato tipo JSON), coerente com o que `martech-event-review` espera ler depois.
4. Copie/reaproveite as legendas amarelas de instrução (a numeração 1-7 explicando o padrão) do
   frame-template — não precisam de conteúdo novo, são fixas.

Para os padrões de **"Eventos Pontuais"** e **"Registro de novos Pages"**, siga a mesma lógica mas
sem as telas numeradas: adicione as linhas diretamente na tabela existente dessa seção (ou crie uma
nova, se a seção ainda não existir no board de destino), usando o mesmo schema.

## Idempotência — rodar de novo não pode duplicar nada

A skill precisa ser segura para reexecução: a spec muda, o board é o mesmo, e rodar de novo tem de
**convergir**, não acumular. A regra é sempre *ler antes de criar*.

**Chave estável:** `(TELA, Evento)`, do formato canônico. Quando o mesmo evento aparece duas vezes
na mesma tela (dois disparos distintos), o `#` da spec entra na chave.

Antes de qualquer escrita, no Passo 5:

1. **Achar** com `canvas_search`; **ler** o escopo com `canvas_read_as_svg`. Para cada tabela
   candidata, **`table_list_rows` (`limit: 1` basta)** devolve o schema via column metadata
   (`columnTitle`…) e indica se há linhas — substitui `_schema=` / `_row_count` do `layout_read`
   structured (deprecated, remoção **14/09/2026**). `canvas_search` não lê schema.
2. **Frame** — existe frame com o nome da funcionalidade? Reutilize-o; não crie um segundo.
3. **Tabela** — existe tabela para aquela tela dentro do frame? Reutilize-a.
4. **Coluna** — leia o schema da tabela reaproveitada (`table_list_rows`):
   - `Feedback Claude` já existe → **não recrie** (recriar zera o parecer anterior).
   - falta alguma coluna do schema alvo → acrescente **só a que falta**, nunca recrie a tabela.
5. **Linha** — `table_list_rows` e case por `(TELA, Evento)`:
   - casou → `table_sync_rows` com o `rowId` existente (**update**), preservando `Status`,
     `Data da implementação`, `Status EA`/`Aprovação EA` (o nome que a tabela tiver), `Observação` e
     `Feedback Claude` que já estivessem preenchidos; sobrescreva só o que a spec redefine.
   - não casou → linha nova.
6. **Nunca delete** frame, tabela, coluna ou linha para "recriar limpo". Evento que saiu da spec
   entra como observação no resumo final (Passo 7) para decisão humana — a skill não remove
   histórico de tracking.

⚠️ **Não use `context_get`** para essa inspeção: responde **502** consistentemente na nossa org.
Caminho válido **sem** `layout_read` (deprecated, remoção **14/09/2026**): `canvas_search`
(achar) + `canvas_read_as_svg` (ler escopo) + `table_list_rows` (schema/linhas). Esses três
cobrem tudo o que é preciso.

⚠️ **O que garante a idempotência é a leitura, não a memória da conversa.** Uma segunda execução em
outra sessão não sabe o que a primeira criou; se você pular a leitura do board, ela duplica.

🔴 **`table_create` que falha NÃO é no-op — ele deixa tabela órfã no board.** Medido em 24/08/2026:
duas chamadas que morreram no erro de `Status EA` deixaram, cada uma, uma tabela **parcialmente
criada** (com todas as colunas até a que falhou, zero linhas) empilhada na mesma coordenada da
tabela boa. Uma varredura do board mostrou **4 tabelas** onde só 2 tinham sido criadas com sucesso.

Portanto:

- **Depois de qualquer erro de criação, rode `canvas_search` + `canvas_read_as_svg` (e
  `table_list_rows` nas tabelas suspeitas) antes de tentar de novo** — retentar às cegas empilha
  órfã sobre órfã, todas invisíveis no retorno da chamada que falhou.
- A assinatura da órfã é **zero linhas + schema truncado** (colunas param exatamente na que causou
  o erro), na mesma posição de uma tabela irmã. Confirme com `table_list_rows`, não com
  `_row_count`/`_schema` do `layout_read`.
- Não a confunda com tabela legítima ainda vazia: se houver dúvida, **avise o usuário e deixe a
  remoção para ele**. Esta skill não deleta itens de board (ver Passo 6/Cuidados).
- Corolário: **valide o conjunto de colunas antes de chamar `table_create`**, não durante. O erro
  vem coluna a coluna e cada tentativa custa uma órfã.

## Passo 6 — Encadear a martech-event-review (automático, sempre)

Assim que a tabela estiver escrita, **rode em seguida, sem esperar novo pedido do usuário**, o
fluxo da skill `martech-event-review` sobre a(s) tabela(s) recém-criada(s):

1. Confirme que a coluna `Feedback Claude` existe (ela foi criada no Passo 5 — deve existir).
2. Leia as linhas (`table_list_rows`), avalie nomenclatura + completude de cada evento.
3. Escreva o parecer na coluna `Feedback Claude` (`table_sync_rows`), com os marcadores
   `✔ / ⚠ / △` conforme o formato definido em `martech-event-review`.

## Passo 7 — Resumo final ao usuário

Feche com:

- Link do board/frame criado (`?moveToWidget=<id>` do frame).
- Lista de eventos criados (novos x reaproveitados).
- Resultado da revisão automática (quantos `✔`, `⚠`, `△`).
- Lacunas pendentes, se houver (perguntas de negócio/acionáveis não totalmente cobertas).

## Cuidados

- Nunca crie evento fora do padrão de nomenclatura só porque o requisito do usuário sugeriu um
  nome diferente — aplique as regras e explique o ajuste.
- Não sobrescreva frames/tabelas de outras funcionalidades já existentes no board de destino.
- Se o board de destino não tiver o padrão visual esperado (frame `[Nome da funcionalidade]`,
  tabelas com o schema descrito), avise o usuário em vez de inventar uma estrutura diferente.
- A ausência de acesso à lista do SharePoint (Passo 2) — seja por falta de conta Afya autenticada,
  seja pela limitação das ferramentas de Microsoft 365 para ler Listas — não deve travar a skill:
  sinalize a limitação e prossiga com o que o usuário puder confirmar manualmente.
