# ============================================================================
# TRACKING PLAN <APP> — DEV (permissivo) — USANDO EVENTOS JSON
# ============================================================================
# Copie para: segment/develop/tracking_plan/tracking_plan-<app>/terragrunt.hcl
# Preencha:   <app> (slug, minúsculo), <App> (label), <SOURCE_ID_DEV>.
# Eventos:    segment/events/<app>/  (MESMA pasta usada pelo prod)
#
# Modo DEV = PERMISSIVO de propósito: não bloqueia eventos/props fora do plano,
# pra você iterar sem travar a app enquanto valida a instrumentação.
# ============================================================================

locals {
  # NÃO use o padrão `label == "prod" ? [...] : [...]` no source_id — este arquivo
  # já é do develop; ponha o id de dev direto (evita id inválido no ambiente errado).
  source_id = ["<SOURCE_ID_DEV>"]
}

terraform {
  source = "../../../modules/tracking_plan/tracking_plan"
}

include {
  path = find_in_parent_folders("root.hcl")
}

inputs = {
  # Nome do Tracking Plan
  name = "[Dev][<App>] Event Tracking Plan [IAC/GIT]"

  # Descrição
  description = "Plano de rastreamento para aplicação <App> usando eventos JSON modulares"

  # Tipo do Tracking Plan
  type = "LIVE"

  # ID da Source (dev, direto)
  source_id = local.source_id

  # Habilita uso de eventos JSON (schemas compartilhados com o prod)
  use_json_events = true
  events_path     = "${get_terragrunt_dir()}/../../../events/<app>"

  # Configurações de Schema — Modo PERMISSIVO (Dev)
  allow_unplanned_events           = true
  allow_unplanned_event_properties = true
  allow_event_on_violations        = true
  allow_properties_on_violations   = true
  common_event_on_violations       = "ALLOW"

  # Identify settings — PERMISSIVO
  allow_traits_on_violations          = true
  allow_unplanned_traits              = true
  common_event_on_violations_identify = "ALLOW"

  # Group settings — PERMISSIVO
  allow_group_traits_on_violations = true
  allow_unplanned_group_traits     = true
  common_event_on_violations_group = "ALLOW"
}
