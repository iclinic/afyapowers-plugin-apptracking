#!/usr/bin/env python3
"""
Valida os eventos JSON de um tracking plan antes do commit.

Uso:
    python3 validate_events.py segment/events/<app>

Checa, para cada arquivo *.json na pasta (recursivo):
  - JSON sintaticamente válido;
  - campos de topo obrigatórios, que dependem do tipo da rule (ver abaixo);
  - json_schema.description presente (a "descrição do evento");
  - o container de atributos esperado para o tipo existe;
  - required (se houver) só cita propriedades declaradas no próprio container;
  - toda propriedade declarada tem description preenchida;
  - description de propriedade é GENÉRICA: sem percentual, sem data, sem contagem
    de medição (regra do MarTech, review da data-infra-afya#910);
  - propriedade que o SDK do Segment captura sozinho (url, path, referrer, search,
    title) não é declarada em rule PAGE/SCREEN.

O tipo da rule muda o formato, então a validação é por tipo:

  | type     | tem `key` de topo? | onde ficam os atributos              |
  |----------|--------------------|--------------------------------------|
  | TRACK    | sim                | json_schema.properties.properties    |
  | PAGE     | sim                | json_schema.properties.properties    |
  | IDENTIFY | não                | json_schema.properties.traits        |
  | COMMON   | não                | .properties e/ou .traits (fragmento) |

`IDENTIFY` não tem nome de evento (é chamada, não evento custom) e carrega os
atributos em `traits`. Exigir `key` e `properties` dela produz falso positivo, que
foi o motivo desta correção (DC-12219).

Não valida a nomenclatura dos eventos (isso é o fluxo de review no Miro) nem se o
conteúdo bate com o mural — a fonte da verdade é o mural, e essa conferência é humana.
Sai com código != 0 se algum arquivo falhar, pra travar o commit num pre-commit/CI.
"""
import json
import re
import sys
from pathlib import Path

# Tipos medidos em 09/09/2026 nos 336 JSONs de data-infra-afya/segment/events:
# TRACK 316, PAGE 14, IDENTIFY 5, COMMON 1. Nenhum GROUP.
# Ao encontrar um tipo novo, acrescente aqui em vez de afrouxar a checagem.
TYPE_RULES = {
    # type: (exige `key` de topo, containers de atributos aceitos)
    "TRACK": (True, ("properties",)),
    "PAGE": (True, ("properties",)),
    "IDENTIFY": (False, ("traits",)),
    "COMMON": (False, ("properties", "traits")),
}
DEFAULT_RULE = (True, ("properties",))

TOP_LEVEL_ALWAYS = ["type", "version", "json_schema"]

# Propriedades que o SDK do Segment captura sozinho na chamada page/screen. Declarar
# duplica dado: elas também viajam em context.page. Reprovado pelo MarTech no review
# da data-infra-afya#910.
SDK_AUTO_PROPS = {"url", "path", "referrer", "search", "title"}

# Marcas de medição que não podem morar no schema. description é contrato e envelhece
# devagar; medição envelhece todo dia e vai para a PR, o card e a memória.
MEDICAO_NA_DESCRICAO = [
    (re.compile(r"\d[\d.,]*\s*%"), "percentual"),
    (re.compile(r"\b\d{2}/\d{2}(/\d{2,4})?\b"), "data"),
    (re.compile(r"\b\d{1,3}(\.\d{3})+\b"), "contagem"),
]


def validate_file(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"]

    for field in TOP_LEVEL_ALWAYS:
        if field not in data:
            problems.append(f"falta campo de topo '{field}'")

    rule_type = data.get("type")
    if rule_type in TYPE_RULES:
        needs_key, containers = TYPE_RULES[rule_type]
    else:
        # Tipo desconhecido é reportado em vez de validado no escuro: silenciar
        # esconderia um typo em `type`, e validar como TRACK culparia o arquivo errado.
        needs_key, containers = DEFAULT_RULE
        if rule_type is not None:
            problems.append(
                f"type '{rule_type}' não é conhecido pelo validador "
                f"(conhecidos: {', '.join(sorted(TYPE_RULES))}) — "
                "validado como TRACK; acrescente o tipo em TYPE_RULES"
            )

    if needs_key and "key" not in data:
        problems.append("falta campo de topo 'key'")
    elif not needs_key and "key" in data:
        problems.append(f"rule do tipo '{rule_type}' não deve ter campo de topo 'key'")

    schema = data.get("json_schema", {})
    if not isinstance(schema, dict):
        problems.append("json_schema não é um objeto")
        return problems

    if not schema.get("description"):
        problems.append("json_schema.description ausente ou vazio")

    lvl1 = schema.get("properties")
    if not isinstance(lvl1, dict):
        problems.append("json_schema.properties não encontrado ou não é um objeto")
        return problems

    esperado = " ou ".join(f"json_schema.properties.{c}" for c in containers)
    encontrados = [c for c in containers if isinstance(lvl1.get(c), dict)]
    if not encontrados:
        problems.append(f"container de atributos não encontrado (esperado {esperado})")
        return problems

    # Só faz sentido cruzar `required` onde há `properties` declarado. Fragmento com
    # container vazio (ex.: iclinic/_common.json) é válido e não tem o que cruzar.
    for container in encontrados:
        node = lvl1[container]
        props = node.get("properties")
        if not isinstance(props, dict):
            continue
        required = node.get("required", [])
        if not isinstance(required, list):
            problems.append(f"'{container}.required' deve ser uma lista")
            continue
        for r in required:
            if r not in props:
                problems.append(
                    f"'{r}' está em {container}.required mas não foi declarada "
                    f"em {container}.properties"
                )

        problems.extend(validate_descriptions(props, container))

        if rule_type in ("PAGE", "SCREEN"):
            auto = sorted(SDK_AUTO_PROPS & set(props))
            if auto:
                problems.append(
                    f"{container}.properties declara {', '.join(auto)}, que o SDK do "
                    f"Segment captura sozinho na chamada page/screen. Não declarar: o "
                    f"mesmo valor viaja em context.page"
                )

    return problems


def validate_descriptions(props: dict, container: str) -> list[str]:
    """Descrição de propriedade: obrigatória e genérica."""
    problems: list[str] = []
    for nome, corpo in props.items():
        if not isinstance(corpo, dict):
            continue
        desc = corpo.get("description")
        if not desc or not str(desc).strip():
            problems.append(
                f"'{nome}' está sem description em {container}.properties"
            )
            continue
        achados = [rotulo for padrao, rotulo in MEDICAO_NA_DESCRICAO
                   if padrao.search(str(desc))]
        if achados:
            problems.append(
                f"description de '{nome}' tem {', '.join(sorted(set(achados)))} "
                f"dentro do schema. Descrição é genérica: diz o que o campo é e "
                f"para aí. Medição vai para a PR, o card e a memória"
            )
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: python3 validate_events.py <pasta_de_eventos>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1])
    if not root.exists():
        print(f"pasta não existe: {root}", file=sys.stderr)
        return 2

    files = sorted(root.rglob("*.json"))
    if not files:
        print(f"nenhum .json encontrado em {root}", file=sys.stderr)
        return 2

    failed = 0
    for f in files:
        problems = validate_file(f)
        if problems:
            failed += 1
            print(f"✗ {f}")
            for p in problems:
                print(f"    - {p}")
        else:
            print(f"✓ {f}")

    print(f"\n{len(files) - failed}/{len(files)} OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
