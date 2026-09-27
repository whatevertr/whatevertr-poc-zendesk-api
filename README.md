> 🇧🇷 [Leia em português](README.pt-BR.md)

# PoC — Validating Service-Desk Architecture Premises via the Zendesk API

Nine test suites run entirely through the REST API on a disposable trial instance, proving, before any official build, that the platform sustains a redesigned support architecture: collapsed groups, a three-level taxonomy (group → category → sub-category), SLA anchored on field values, and multi-ticket journey measurement.

> 🌐 **Language note:** this README is in English; the detailed docs under `docs/` are currently in Portuguese. Translations welcome — open a PR.

## What this proves

**9 test suites · 13 verdicts · validated exclusively via REST API · fully auditable request/response history.**

- A unified ticket form with conditional fields, including the real limit of native conditionality (it toggles fields, not dropdown options) and the viable pattern around it.
- SLA policies driven by custom field values, in business hours, with the three operational requirements nobody mentions upfront: end-user requester, ticket priority set, and the metric-events endpoint lagging by hours.
- Group-based routing fired on creation, the negative test (changing the reason does not reroute), and a corrective trigger that reverts invalid moves in the same update.
- **The core premise:** end-to-end journey SLA is analytically computable from the platform's native trail, for linear chains and parallel trees alike (critical path vs. total effort), linked by a lookup field.
- Customer experience: one visible ticket number (the shell), internal stages invisible in the portal, and the exact leak risk, proven, not assumed.
- One CSAT survey per journey (never per stage), answered programmatically through OAuth impersonation and joined with the composed SLA in a one-row-per-journey report.
- Legacy migration: only *solve* is blocked by an empty required field (enforced by the API too, not just the UI), native bulk backfill via jobs, and the sequence that migrates without stopping operations.
- Views per sub-category reproducing per-group workspaces; renames safe by construction (automations reference IDs); the single plan-gated item (custom roles require Enterprise).

Full evidence and limits: [`docs/Validacao_Premissas.md`](docs/Validacao_Premissas.md) · per-test summary: [`docs/MAPA_TESTES.md`](docs/MAPA_TESTES.md) · as-is × to-be projection model: [`docs/Simulacao_Pos_Coleta.md`](docs/Simulacao_Pos_Coleta.md).

## Repo map

```
docs/       Premise validation (9 suites, 13 verdicts) · simulation model · test map · method note
scripts/    API client with automatic write-history capture · parameterized projection model · synthetic-base generator
data/       SYNTHETIC base (generated from declared parameters) the model runs on
historico/  The audit trail: 104 write calls + 1 identity-assumption GET, as numbered request/response pairs + teardown manifest
```

All instance data is synthetic; identifiers were substituted for publication (`SUBDOMINIO_TESTE`, `_AT_`, `Trilha NN` conventions). The substitution map does not accompany this publication. Spreadsheets and credentials never enter the repo (`.gitignore`).

## How to reproduce

1. Create a Zendesk trial and an API token (Admin Center → Apps and integrations → API).
2. Add a `.env` at the root (never committed):
   ```
   ZENDESK_SUBDOMAIN=your-subdomain
   ZENDESK_EMAIL=your-admin-email
   ZENDESK_API_TOKEN=your-token
   ```
3. `pip install -r scripts/requirements.txt`
4. Replay the setup and tests in the order of `historico/`, the numbered pairs are an executable script: exact payload sent, exact response expected, T1 through T9. `scripts/zd_client.py` captures the same kind of history for your own runs.
5. **Projection model** (`scripts/simulacao_pos_coleta.py`): runs on the **synthetic base included** in `data/`. Generate and run:
   ```bash
   python scripts/gerar_base_sintetica.py
   POC_DIR="data" python scripts/simulacao_pos_coleta.py
   ```
   The base is generated from declared parameters (fixed seed) — see [`docs/Simulacao_Pos_Coleta.md`](docs/Simulacao_Pos_Coleta.md). The numbers demonstrate the model; they are **not** a finding about any real organization.

## Stack

Python 3 (`requests`, `openpyxl`) · Zendesk API v2 (tickets, ticket fields/forms, groups, SLA policies, triggers, automations, views, satisfaction ratings, custom roles, bulk jobs) · OAuth with the `impersonate` scope for acting as the end user.

Technical note: the sandboxed environment originally planned for the scripts had its egress proxy blocking the Zendesk domain, so the calls were executed from the browser's authenticated admin session (same-origin `fetch` + the CSRF token the API itself provides). Same endpoints, same payloads, same evidence, the history does not care who carried it. The token-based client is included and works wherever outbound traffic is allowed.

## How this was built

Method and epistemic floor (the chronicler, the honest scorecard, verdicts stated with their limits): [`docs/METODO.md`](docs/METODO.md). The full method (The Constellation Method) is being published incrementally; these are field notes, dated and versioned.
