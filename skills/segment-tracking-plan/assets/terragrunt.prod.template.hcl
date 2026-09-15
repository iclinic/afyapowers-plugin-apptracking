# ============================================================================
# TRACKING PLAN <APP> — PROD (restritivo) — USANDO EVENTOS JSON
# ============================================================================
# Copie para: segment/Prod/tracking_plan/tracking_plan-<app>/terragrunt.hcl
# Preencha:   <app> (slug, minúsculo), <App> (label), <SOURCE_ID_PROD>.
# Eventos:    segment/events/<app>/  (A MESMA pasta do dev — não duplique schemas)
#
# Modo PROD = RESTRITIVO: com BLOCK, o Segment DESCARTA qualquer evento/propriedade
# fora do plano nesta source. Confirme que a app em prod só emite o que está
# planejado, senão evento legítimo é bloqueado.
# ============================================================================

locals {
  # source_id de prod, direto (não use o ternário `label == "prod" ? ...`).
  source_id = ["<SOURCE_ID_PROD>"]
}

terraform {
  source = "../../../modules/tracking_plan/tracking_plan"
}

include {
  path = find_in_parent_folders("root.hcl")
}

inputs = {
  # Nome do Tracking Plan (sem o prefixo [Dev])
  name = "[<App>] Event Tracking Plan [IAC/GIT]"

  # Descrição
  description = "Plano de rastreamento restritivo para aplicação <App> — alerta sobre eventos não planejados e valida propriedades obrigatórias. Implementa as regras do mural de tracking usando eventos JSON modulares."

  # Tipo do Tracking Plan
  type = "LIVE"

  # ID da Source (prod, direto)
  source_id = local.source_id

  # Habilita uso de eventos JSON (MESMA events_path do dev)
  use_json_events = true
  events_path     = "${get_terragrunt_dir()}/../../../events/<app>"

  # Configurações de Schema — Modo RESTRITIVO (Produção)
  allow_unplanned_events           = false
  allow_unplanned_event_properties = false
  allow_event_on_violations        = false
  allow_properties_on_violations   = false
  common_event_on_violations       = "BLOCK"

  # Identify settings — RESTRITIVO
  allow_traits_on_violations          = false
  allow_unplanned_traits              = false
  common_event_on_violations_identify = "BLOCK"

  # Group settings — RESTRITIVO
  allow_group_traits_on_violations = false
  allow_unplanned_group_traits     = false
  common_event_on_violations_group = "BLOCK"
}
