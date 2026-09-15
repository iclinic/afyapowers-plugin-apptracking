# Spec de tracking — <Nome da funcionalidade/jornada>

<!--
  FORMATO CANÔNICO DE ENTRADA da skill `martech-mural-builder`.

  Duas formas de usar:
    (a) o solicitante preenche este arquivo e entrega pronto;
    (b) a skill gera este arquivo a partir dos requisitos soltos (Passo 3) e pede confirmação.

  Em ambos os casos ele é a fonte da verdade do que vai para o board: cada linha da
  tabela "Eventos" vira UMA linha de tabela no Miro.

  🔑 CHAVE DE IDEMPOTÊNCIA = o par (TELA, Evento).
  Rodar a skill de novo com a mesma chave ATUALIZA a linha existente via `table_sync_rows`;
  nunca cria uma segunda linha, nunca cria uma segunda tabela para a mesma tela.
  Se um evento precisar aparecer duas vezes na MESMA tela (dois disparos distintos),
  desambigue no campo `#` — ele entra na chave.
-->

## Identificação

| Campo | Valor | Observação |
|---|---|---|
| Produto | `<afya_one \| iclinic \| whitebook \| receitapro \| ...>` | — |
| `application_name` | `<valor real que o app envia>` | vai para a coluna homônima da tabela |
| `<produto>_id` | `<ex.: afya_id, iclinic_id, receitapro_id>` | **não use `product_id`** — ver o mapa em `martech-event-review`. Se a source não tiver id de produto confirmado, escreva `a definir (MarTech)` |
| Board de destino | `<URL do Miro>` | vazio = a skill pergunta |
| Tipo de seção | `<jornada \| evento_pontual \| page_avulso>` | decide o padrão do Passo 4 |

## Perguntas de negócio

1. `<pergunta de negócio 1>`
   - Acionável: `<o que se faz com a resposta>`
2. `<pergunta de negócio 2>`
   - Acionável: `<...>`

> Toda pergunta listada aqui precisa ser respondível pelo conjunto de eventos abaixo.
> Pergunta sem evento que a responda é **lacuna declarada**, não erro de preenchimento.

## Telas

### TELA 1 — `<nome real da tela>`

| Campo | Valor |
|---|---|
| `application_feature` | `<ex.: checkout, onboarding, search>` |
| `application_area` | `<só AfyaOne; senão deixe vazio>` |
| `application_page` | `<só AfyaOne; senão deixe vazio>` |
| Imagem | `<caminho ou URL do wireframe/screenshot; vazio = retângulo rotulado>` |

#### Eventos

| # | Evento | Método | Descrição Ação | Atributos customizados | Device | Identificado? |
|---|---|---|---|---|---|---|
| 1 | `button_clicked` | `track` | Ao clicar em "Confirmar", após a validação do formulário | `{"button_name": "Confirmar", "has_coupon": false}` | `All devices` | `sim` |
| 2 | `page_viewed` | `page` | Ao carregar a tela, uma vez por navegação | `{}` | `All devices` | `não` |

### TELA 2 — `<nome real da tela>`

<!-- repita o bloco acima; a numeração de eventos REINICIA em cada tela -->

---

## Como cada campo cai no board

| Campo desta spec | Coluna da tabela no Miro |
|---|---|
| `Evento` | `Evento` (select) |
| `Atributos customizados` | `Atributos customizados` (text, JSON) |
| `Descrição Ação` | `Descrição Ação` (text) — **o template do Miro não chama essa coluna de `Ação`** |
| `application_name` (Identificação) | `application_name` |
| `application_feature` (por tela) | `application_feature` |
| `application_area` (por tela, só AfyaOne) | `application_area` — **não existe no template**: crie a coluna quando o produto for AfyaOne |
| `application_page` (por tela, só AfyaOne) | `application_page` — idem |
| — (fixo, obrigatório) | `session_id` |
| `<produto>_id` (Identificação) | `[product]_id` |
| `Device` | `Device` (multiselect) |
| — (nasce vazio) | `Status`, `Data da implementação`, `Observação` |
| — (nasce vazio) | `Aprovação EA` em tabela nova · `Status EA` em tabela que já existe — mesma coluna, ver a skill |
| — (nasce vazio, preenchido pela review) | `Feedback Claude` |

Deixar `application_area`/`application_page` fora do board num produto AfyaOne não é economia de
coluna: as duas são **obrigatórias** ali, e sem coluna própria elas acabam escondidas dentro de
"Atributos customizados" ou simplesmente não especificadas — nos dois casos a review não consegue
distinguir "não se aplica" de "faltou".

`Identificado? = não` significa evento anônimo: nesse caso o `[product]_id` fica **vazio de
propósito** e a `martech-event-review` não deve cobrá-lo. `Identificado? = sim` e a célula vazia é
que é achado.
