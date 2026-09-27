> 🇺🇸 [Read in English](README.md)

# PoC — Validação de Premissas de Arquitetura de Atendimento via API Zendesk

Estudo de caso técnico: prova de conceito executada 100% via API REST (Zendesk API v2) para validar, **antes do desenvolvimento oficial**, se a plataforma sustenta as premissas de um redesenho de estrutura de atendimento: colapso de grupos em células, taxonomia de três níveis (**grupo → categoria → subcategoria**), SLA ancorado na subcategoria, roteamento por grupo e medição de jornadas multi-ticket ("trilhas").

Executada em instância trial descartável (14 dias, Suite Professional com boost Enterprise). Todos os dados criados na instância são sintéticos.

## O que a PoC prova

**9 testes, 13 vereditos** (detalhe completo em [`docs/Validacao_Premissas.md`](docs/Validacao_Premissas.md); resumo por teste em [`docs/MAPA_TESTES.md`](docs/MAPA_TESTES.md)):

- Formulário unificado com campos condicionais; o limite real da condicionalidade nativa (campo, não opção) e o padrão viável.
- SLA por valor de campo customizado, em horas úteis, com as três condições operacionais que ninguém conta (solicitante end-user, prioridade definida, defasagem do endpoint de metric events).
- Roteamento por grupo disparado na criação + teste negativo + trava corretiva contra movimentação inválida.
- **A premissa central:** SLA de jornada ponta-a-ponta calculável analiticamente sobre o rastro nativo da plataforma, em cadeias sequenciais e árvores paralelas (caminho crítico × esforço total), com vínculo por campo lookup.
- Experiência do cliente: um número único visível (casca), etapas internas invisíveis, e o risco exato de vazamento, provado.
- CSAT único por jornada (nunca por etapa), respondido programaticamente via impersonação OAuth e cruzado com o SLA composto.
- Migração de legado: o que trava com campo obrigatório (só o resolver, validado também na API), backfill em massa nativo via jobs, e a sequência que migra sem parar operação.
- Views por subcategoria reproduzindo workspaces por grupo; renome seguro por construção (referência por ID); o único item condicionado a plano (papéis custom = Enterprise).

## Estrutura

```
docs/       Validação de premissas (9 testes, vereditos) · Modelo de simulação as-is × to-be · Mapa de testes · Nota de método
scripts/    Cliente API com histórico automático de escrita · Modelo de projeção parametrizável · Gerador da base sintética
data/       Base SINTÉTICA (gerada por parâmetros declarados) sobre a qual o modelo roda
historico/  Prova de auditoria: 104 chamadas de escrita + 1 GET de assunção de identidade, em pares request/response numerados + manifest de teardown
```

## Stack

Python 3 (`requests`, `openpyxl`) · Zendesk API v2 (tickets, ticket_fields, ticket_forms, groups, slas/policies, triggers, automations, views, satisfaction_ratings, custom_roles, jobs) · autenticação por sessão + CSRF (com fallback documentado a basic auth por token) · OAuth com escopo `impersonate` para ações em nome do end-user.

**Nota técnica.** O ambiente isolado originalmente previsto para os scripts tinha o proxy de saída bloqueando o domínio Zendesk, então as chamadas foram executadas pela sessão autenticada de admin do navegador (`fetch` same-origin + o token CSRF que a própria API fornece). Mesmos endpoints, mesmos payloads, mesma evidência — o histórico não muda por quem carregou a chamada. O cliente por token está incluído e funciona onde o tráfego de saída é permitido.

## Como reproduzir

1. Crie um trial em zendesk.com e um token de API (Admin Center → Apps e integrações → API).
2. Crie um `.env` na raiz (não versionado):
   ```
   ZENDESK_SUBDOMAIN=seu-subdominio
   ZENDESK_EMAIL=seu-email-admin
   ZENDESK_API_TOKEN=seu-token
   ```
3. `pip install -r scripts/requirements.txt`
4. Reproduza o setup e os testes na ordem do `historico/` — os pares request/response numerados são o roteiro executável (payload enviado e resposta esperada de cada passo). O cliente `scripts/zd_client.py` grava o mesmo tipo de histórico das suas execuções.
5. **Modelo de simulação** (`scripts/simulacao_pos_coleta.py`): roda sobre a **base sintética incluída** em `data/`. Gere e rode:
   ```bash
   python scripts/gerar_base_sintetica.py
   POC_DIR="data" python scripts/simulacao_pos_coleta.py
   ```
   A base é gerada por parâmetros declarados (seed fixa) — ver [`docs/Simulacao_Pos_Coleta.md`](docs/Simulacao_Pos_Coleta.md). Os números demonstram o modelo; **não** são achado sobre organização real.

## Notas

- Nenhum dado real: instância descartável, dados sintéticos, nomes genéricos; identificadores substituídos (convenções `SUBDOMINIO_TESTE`, `_AT_`, `Trilha NN`). O mapa de substituição não acompanha esta publicação.
- O histórico registra também erros e correções (422 de payload, 402 de limite de plano, 404 de rota descontinuada) — é log de auditoria, não vitrine editada.
- **Como isto foi construído** (método, piso epistêmico): [`docs/METODO.md`](docs/METODO.md).

*Traduções são bem-vindas — abra um PR.*
