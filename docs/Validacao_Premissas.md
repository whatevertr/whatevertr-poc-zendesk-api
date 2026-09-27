# Validação de Premissas de Plataforma — POC Taxonomia Zendesk

**Versão:** 5.1 — 12/07/2026 (V1: T1–T5; V2: T6-A/T6-B e ajustes em T2/T4; V3: T7 — CSAT na trilha; V4: T8 — ramificação paralela, refinamento da ressalva do T7 e nota de mitigação existente no T6-A; V5.1: T9 — legado, automações e permissões + veredito geral. Arquivo novo, sem alteração do V4, por regra da sala de não sobrescrever)
**O que é isto:** resultado da prova de conceito das premissas de arquitetura do esqueleto de taxonomia (Grupo/célula → Motivo (categoria) → Submotivo (subcategoria)), executada em instância Zendesk trial externa e descartável (`SUBDOMINIO_TESTE`, Suite Professional trial, expira em 14 dias a contar de 12/07/2026). Todos os objetos criados usam dado sintético com nomes genéricos; nenhum dado das Ferramentas 01/02 foi enviado à instância. O histórico integral das chamadas de escrita está em `historico/` (request/response numerados + `manifest.json` para teardown).
**Método de execução:** chamadas REST à API v2 autenticadas pela sessão de administrador do navegador (mesma origem, com token anti-CSRF fornecido pela própria API), em razão de bloqueio de rede do ambiente de execução local. As chamadas e payloads são idênticos aos de execução por token de API.

---

## 1. Setup executado (Fase 1)

| Objeto | Nome | ID |
|---|---|---|
| Schedule (horas úteis) | Horario Util POC (seg–sex 8h–18h, America/Sao_Paulo) | 51262745177364 |
| Grupo | Celula SAC | 51262745235220 |
| Grupo | Celula Transporte | 51262730291092 |
| Grupo | Celula Logistica | 51262745284372 |
| Grupo | Celula Financeiro | 51262730328340 |
| Campo ticket (tagger) | Motivo (categoria) — Devolucao · Coleta · NFD · Estorno · Motivo Generico A · Motivo Generico B | 51262766832660 |
| Campo ticket (tagger) | Submotivo (subcategoria) — 10 opções, criticidade no nome (ex.: "Estorno - Critico" / "Estorno - Padrao") | 51262766882580 |
| Campo ticket (tagger) | Submotivo Estorno (subcategoria condicional demo) | 51262750652052 |
| Campo ticket (lookup zen:ticket) | Ticket Anterior (Trilha) | 51262735029524 |
| Formulário | Formulario Unificado POC (campos padrão + os 4 acima) | 51262768082068 |
| Política SLA | SLA Critico 4h uteis (first_reply_time 240 min úteis) | 51262753151764 |
| Política SLA | SLA Transacional 8h uteis (480 min úteis) | 51262769795860 |
| Política SLA | SLA Padrao 24h uteis (1.440 min úteis) | 51262738779540 |
| Trigger | Roteamento POC - motivo_devolucao → Celula SAC | 51262740366996 |
| Trigger | Roteamento POC - motivo_coleta → Celula Transporte | 51262763671060 |
| Trigger | Roteamento POC - motivo_nfd → Celula Logistica | 51262753884564 |
| Trigger | Roteamento POC - motivo_estorno → Celula Financeiro | 51262770727188 |
| Usuário end-user (sintético) | Cliente Teste POC | 51262855326996 |
| Tickets de teste | POC T2/T3/T4 — ids 2 a 13; T6 — casca 14, arranjo A 15–17, arranjo B 18–20 | (ver manifest) |
| Trigger (V2) | Trava POC - Estorno fora da Celula Financeiro (corretiva) | 51265215603092 |
| Políticas SLA (V2) | atualizadas para incluir `requester_wait_time` com as mesmas metas | ids acima |
| Trigger (V3) | CSAT POC - oferecer pesquisa apenas na casca (ao resolver) | 51265513480212 |
| Automação (V3) | CSAT POC - pesquisa 1h pos-resolucao (so casca) | 51265483134868 |
| Avaliação CSAT (V3) | satisfaction_rating good + comentário no ticket 14 | 51265522003092 |
| OAuth client/token (V3) | impersonação para resposta do cliente — **revogados após o teste** | (ver histórico 57+) |
| Tickets (V4) | T8 — casca paralela 21, etapas P1 22 e P2 23 | (ver manifest) |

## 2. Casos de teste

### T1 — Formulário unificado + condicionalidade categoria→subcategoria

- **O que prova:** um único formulário carrega Motivo e Submotivo, e a plataforma condiciona a exibição do submotivo ao motivo selecionado.
- **Como verificado:** `POST /api/v2/ticket_forms` (201) com os dois campos; `PUT /api/v2/ticket_forms/{id}` com `agent_conditions` (200): o campo "Submotivo Estorno (subcategoria condicional demo)" só é exibido quando Motivo = Estorno.
- **Limite encontrado:** a condicionalidade nativa opera **exibindo/ocultando campos inteiros** com base no valor de outro campo. **Não existe filtragem de opções dentro de um único dropdown** (um campo "Submotivo (subcategoria)" único sempre exibe as 10 opções). O desenho compatível com a plataforma é um campo de submotivo por motivo, exibido condicionalmente — mecanismo demonstrado e funcionando.
- **Veredito: sustentada com ressalva** — a premissa "submotivo só exibe opções compatíveis" é atendida pelo padrão campo-por-motivo, não por filtragem de opções em campo único.

### T2 — SLA aplicada pela condição do Submotivo (subcategoria)

- **O que prova:** políticas de SLA aceitam campo customizado como condição e aplicam metas distintas conforme o valor da subcategoria.
- **Como verificado:** 3 políticas criadas (201) com condição `custom_fields_51262766882580 = tag do submotivo`. Tickets 7 (Devolucao - Critico), 8 (Coleta - Padrao) e 9 (Estorno - Padrao): `GET /api/v2/tickets/{id}.json?include=slas` retornou `first_reply_time` ativo com `breach_at` exato de cada meta em horas úteis — 4h → seg 12:00 local; 24h → qua 12:00; 8h → seg 16:00 (criação em domingo; relógio inicia seg 08:00 no schedule).
- **A política aceita campo customizado como condição: sim** (criação 201 e aplicação com metas corretas).
- **Ressalvas operacionais encontradas:**
  1. `first_reply_time` **não ativa em ticket criado pelo agente como solicitante** — o teste exigiu solicitante end-user (tickets 2–4, criados pelo admin, não receberam SLA);
  2. `policy_metrics` são **por prioridade** — o ticket precisa ter prioridade definida para a meta aplicar. Duas opções de ativação: **(a)** triggers submotivo→prioridade (um por criticidade; acopla prioridade à taxonomia, mais triggers para manter); **(b) recomendada:** metas iguais em todas as prioridades dentro de cada política — a criticidade mora na política/submotivo, não na prioridade — combinada com um único trigger global de prioridade default na criação; mais simples e com menos objetos de configuração (foi o desenho usado nesta POC: cada política define a mesma meta para low/normal/high/urgent);
  3. o endpoint `/api/v2/tickets/{id}/metric_events.json` **não materializou eventos durante toda a janela da POC (~1h após a criação dos tickets)** — defasagem assíncrona do endpoint; a verificação em tempo real foi feita por `include=slas`. Para auditoria por `metric_events`, prever janela de processamento de horas.
- **Veredito: sustentada com ressalva** (as três condições operacionais acima).

### T3 — Roteamento por grupo + teste negativo

- **O que prova:** a atribuição de célula dispara pelo valor do campo na criação, e trocar o motivo depois não reatribui (roteamento é por grupo, não por motivo).
- **Como verificado:** 4 triggers `update_type = Create` + valor de Motivo → grupo. Tickets 2, 3, 4 e 5 roteados corretamente na criação (4/4). Negativo: ticket 6 criado como Devolucao (→ Celula SAC), motivo alterado via PUT para Coleta — **grupo permaneceu Celula SAC** (auditoria sem novo evento de trigger de grupo).
- **Achado adicional (registrado):** no primeiro teste negativo (ticket 5), o canal `system` reverteu o grupo para o grupo do atribuído, porque o atribuído não era membro da célula de destino. O roteamento por grupo pressupõe **membresia correta dos agentes nas células**; com membresia correta (memberships criados), o comportamento é o esperado.
- **Veredito: sustentada.**

### T4 — A trilha (premissa central)

- **O que prova:** a esteira de devolução se decompõe em tickets encadeados (SAC → Transporte → Logistica → Financeiro), cada um com SLA próprio, com cadeia e duração ponta-a-ponta reconstruíveis analiticamente via API.
- **Execução:** tickets 10 → 11 → 12 → 13, cada um criado na célula correta pelo trigger de motivo (Devolucao, Coleta, NFD, Estorno), encerrado antes da abertura do seguinte, e vinculado ao anterior pelo campo lookup.
- **(i) SLA independente por ticket:** confirmado — cada ticket exibiu `first_reply_time` próprio com stage `achieved`, sem interferência entre etapas.
- **(ii) Cadeia reconstruível via API:** confirmado — **campo:** lookup "Ticket Anterior (Trilha)" (id 51262735029524, tipo `lookup`, alvo `zen:ticket`); **endpoint:** `GET /api/v2/tickets/{id}.json`, lendo `custom_fields[{id do lookup}].value` (= id do ticket anterior). A cadeia 13→12→11→10 foi reconstruída de trás para frente exclusivamente por esse caminho, sem estado local.
- **(iii) Timestamps compõem ponta-a-ponta:** confirmado — `GET /api/v2/tickets/{id}/metrics.json` fornece `created_at`/`solved_at` por etapa. Composição demonstrada: início 2026-07-12T20:18:24Z (criação do 10), fim 2026-07-12T20:18:30Z (solução do 13); duração da trilha = 6 s corridos = Σ permanência das 4 etapas + Σ intervalos entre solução de uma etapa e abertura da seguinte (durações em segundos porque o teste automatizou as etapas; a fórmula independe da escala).
- **Código de extração:**

```python
def trilha(zd_get, ultimo_ticket_id, lookup_field_id):
    cadeia, cur = [], ultimo_ticket_id
    while cur:
        t = zd_get(f"/api/v2/tickets/{cur}.json")["ticket"]
        m = zd_get(f"/api/v2/tickets/{cur}/metrics.json")["ticket_metric"]
        cadeia.insert(0, {"id": cur, "grupo": t["group_id"],
                          "criado": m["created_at"], "resolvido": m["solved_at"]})
        prev = next((c["value"] for c in t["custom_fields"]
                     if c["id"] == lookup_field_id), None)
        cur = int(prev) if prev else None
    # SLA total da trilha = soma das permanencias + soma dos gaps entre etapas
    from datetime import datetime
    p = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    permanencia = sum((p(e["resolvido"]) - p(e["criado"])).total_seconds() for e in cadeia)
    gaps = sum((p(cadeia[i+1]["criado"]) - p(cadeia[i]["resolvido"])).total_seconds()
               for i in range(len(cadeia)-1))
    return cadeia, permanencia, gaps, permanencia + gaps
```

- **Formulação:** o SLA total da trilha = soma das permanências das etapas (solved − created de cada ticket) + soma dos intervalos entre a solução de uma etapa e a abertura da seguinte — tudo calculável sobre o rastro nativo da plataforma (timestamps de `/metrics` + vínculo do lookup), sem instrumentação adicional.
- **Veredito da premissa: SIM — o SLA de trilha é calculável analiticamente sobre o rastro da plataforma, com ressalva:** o vínculo é um campo customizado (lookup), não um recurso nativo de encadeamento; a reconstrução depende de o processo preencher o campo a cada abertura de etapa (automatizável por macro/trigger/integração). Métricas de SLA por etapa e timestamps são nativos.

### T5 — Limites de plano

- **Plano do trial:** Zendesk **Suite Professional** (trial 14 dias, 5 agentes), **com boost ativo `enterprise_productivity_pack`** (14 dias) — o trial opera acima do Professional puro. Fonte: `GET /api/v2/account/subscription.json` e `GET /api/v2/account/boosts.json`.

| Premissa / recurso usado | Onde foi usado na POC | Plano necessário (documentação Zendesk vigente) |
|---|---|---|
| Múltiplos formulários de ticket | Formulario Unificado POC (2º formulário da conta) | Suite Growth ou superior |
| Campos condicionais (conditional ticket fields) | Condição Motivo=Estorno → exibir submotivo demo | Suite Growth ou superior |
| Políticas de SLA | 3 políticas por valor da subcategoria | Suite Growth ou superior |
| SLA em horas úteis (schedule) | Horario Util POC | Suite Growth ou superior (múltiplos schedules: Enterprise) |
| Campos customizados dropdown (tagger) | Motivo (categoria) / Submotivo (subcategoria) | Todos os planos |
| Campo lookup (relationship zen:ticket) | Ticket Anterior (Trilha) | Todos os planos Suite |
| Triggers com condição em campo customizado | 4 triggers de roteamento | Todos os planos |
| API de métricas / metric events | Verificação T2/T4 | Todos os planos (endpoint com defasagem assíncrona) |

- **Conferência contra o plano contratado:** se o contrato for Suite Professional ou superior, todas as features usadas estão cobertas; abaixo de Growth, caem formulários múltiplos, campos condicionais e SLA. Referências: [Creating conditional ticket fields](https://support.zendesk.com/hc/en-us/articles/4408834799770), [Creating ticket forms](https://support.zendesk.com/hc/en-us/articles/4408846520858).
- **Veredito: registrado** — nenhuma feature usada exige Enterprise, exceto múltiplos schedules (não usado; 1 schedule bastou).

### T6-A — Experiência do cliente na trilha (casca + etapas internas)

- **O que prova:** o desenho casca (número único do cliente) + etapas internas sustenta simultaneamente (i) cliente vê um número só, (ii) etapas medem SLA, (iii) cadeia reconstruível.
- **Montagem:** ticket-casca 14 (solicitante Cliente Teste POC, Celula SAC, Devolucao, status pendente) + etapas Coleta→NFD→Estorno em dois arranjos: **A** (tickets 15–17, solicitante = cliente original, primeiro comentário como nota interna) e **B** (tickets 18–20, solicitante = usuário interno). Cadeia via lookup em ambos (etapa 1 → casca).
- **Janela do cliente** (mecanismo do trial: `GET /api/v2/users/{id}/requests.json` — a lista do portal do solicitante — e `GET /api/v2/requests/{id}/comments.json` — os comentários visíveis a ele):
  - Casca 14 aparece na lista do cliente; comentário público visível (1).
  - **Arranjo A: etapas 15–17 NÃO aparecem na lista do cliente** — ticket cujo histórico só tem notas internas não é exibido no portal do solicitante, mesmo com o cliente como requester. Comentários visíveis nas etapas: zero (nota interna invisível). O número da etapa não vaza.
  - **Arranjo B: etapas 18–20 não aparecem** (solicitante interno — invisibilidade estrutural).
  - **Risco de vazamento provado:** um único comentário público na etapa 17 (arranjo A) fez o ticket **aparecer imediatamente na lista do cliente**. No arranjo A, a invisibilidade depende da disciplina "somente notas internas nas etapas".
- **SLA nas etapas:** `first_reply_time` **não ativa** em nenhum dos dois arranjos (A: primeiro comentário interno; B: solicitante agente). `requester_wait_time` **ativa nos dois** (políticas atualizadas para incluir a métrica com as mesmas metas). Na casca: `first_reply_time` ativo e `requester_wait_time` pausado pelo status pendente. SLA de resolução não existe como métrica de política; tempo de resolução é medido pelas métricas nativas do ticket (`full_resolution_time`).
- **Veredito:** **o arranjo A sustenta os três requisitos**, com duas condições de operação: a métrica de SLA das etapas é `requester_wait_time` (não `first_reply_time`), e a invisibilidade exige comunicação exclusivamente por notas internas nas etapas (um comentário público expõe o ticket ao cliente). Nota: a disciplina de notas internas já é prática treinada na operação atual — a mitigação existe em produção, não é conduta nova a implantar. O arranjo B dá invisibilidade estrutural (não depende de disciplina), mede as mesmas métricas, mas perde o vínculo semântico do solicitante real nas etapas — a escolha é entre disciplina operacional (A) e pureza do dado de solicitante (B); a cadeia é reconstruível em ambos.

### T6-B — Trava de roteamento (corretiva)

- **O que prova:** a disciplina "motivo × grupo válido" é sustentável por plataforma, não só por conduta.
- **Montagem:** trigger "Trava POC - Estorno fora da Celula Financeiro (corretiva)" (id 51265215603092): em atualização (`update_type = Change`), se Motivo = Estorno e grupo ≠ Celula Financeiro → reverte o grupo para Celula Financeiro + aplica tag `roteamento_corrigido`.
- **Teste:** ticket 20 (Estorno, Celula Financeiro) movido manualmente para Celula SAC via PUT → **na mesma atualização** o trigger reverteu o grupo para Celula Financeiro e aplicou a tag (auditoria: Suporte → Financeiro [roteamento na criação] → SAC [movimento manual] → Financeiro [trava]). Sem loop: após a correção a condição fica falsa.
- **Comportamento com atribuído não-membro (achado do T3, revalidado):** se o agente atribuído não é membro do grupo de destino, o canal `system` realinha o grupo ao do atribuído na atualização seguinte — a trava corrige de volta, mas a combinação gera ping-pong potencial; membresia correta das células continua sendo pré-requisito.
- **Veredito: sustentável por plataforma** — a trava corretiva funciona por trigger nativo (reversão em cascata viável, sem loop). A variante tag+notificação fica como fallback documentado (a tag foi aplicada; notificação não testada para não gerar e-mail externo). A gestão de mudança pode contar com trava técnica, não apenas conduta.

### T7 — CSAT na trilha

- **O que prova:** a satisfação é medível por jornada — uma única pesquisa, na casca — e cruzável com o SLA composto da trilha.
- **Disponibilidade e ativação:** o recurso existe no plano do trial (Suite Professional) e estava **desativado por padrão**; ativado via `PUT /api/v2/account/settings.json` (`active_features.customer_satisfaction: true`). A ativação criou a automação-sistema "Solicitar índice de satisfação do cliente" (janela padrão: **24h após resolvido**; execução de automações é horária).
- **Janela mínima de disparo:** automação própria criada com `SOLVED = 1` aceita (janela mínima efetiva ≈ 1h, pela execução horária das automações). Para disparo **imediato** na resolução, o caminho é trigger (`status = solved` → `satisfaction_score = offered`) — usado no teste. Automação-sistema desativada para controle do experimento.
- **Filtro de etapa (verificado):** oferta condicionada a `tags includes trilha_casca` e `tags not_includes etapa_trilha` (tag aplicada às etapas; em produção, na criação da etapa). Resolver a etapa 15 **não** ofereceu pesquisa (`satisfaction: unoffered`); resolver a casca 14 ofereceu **imediatamente** (`offered`) — uma pesquisa por trilha. Observação: a automação-sistema tem condição nativa `ticket_is_public = public`, que por si só já exclui etapas do arranjo A (só notas internas), mas não as do arranjo B — a exclusão por tag cobre os dois arranjos.
- **Registro da resposta:** avaliar como admin retorna 403 (**só o solicitante pode avaliar**). A rota legada de assumir identidade (`/users/{id}/assume`) não existe mais (404). Mecanismo usado, conforme documentação vigente: token OAuth com escopo `impersonate` + cabeçalho `X-On-Behalf-Of` com o e-mail do end-user (token descartável criado para o teste e **revogado em seguida**; valor censurado no histórico). Resposta gravada: `POST /api/v2/tickets/14/satisfaction_rating.json` → **score `good` + comentário**, persistidos em `ticket.satisfaction_rating` (id 51265522003092) e listáveis em `/api/v2/satisfaction_ratings.json`.
- **Cruzamento trilha × CSAT (relatório-unidade):** código do T4 estendido — dado o ticket-casca: (i) cadeia(s) pelo lookup, (ii) SLA composto pelos timestamps, (iii) `satisfaction_rating` da casca. Saída obtida (uma linha por trilha): cadeia 14→15→16→17, ponta-a-ponta 1.397 s, CSAT `good`; cadeia 14→18→19→20, ponta-a-ponta 1.424 s, CSAT `good`. **Achado de desenho:** o lookup permite mais de uma cadeia pendurada na mesma casca — o extrator precisa tratar filhos múltiplos (ramificação); no processo real, uma cadeia por casca deve ser regra de operação.
- **Limites encontrados:** ativação do CSAT não vem ligada por padrão; janela mínima por automação ≈ 1h (imediato só por trigger); a resposta do cliente exige canal autenticado do solicitante (portal/e-mail com token de pesquisa) — programaticamente, impersonação OAuth; avaliação só com ticket resolvido (não fechado); só `good`/`bad` como valores.
- **Veredito: SIM, com ressalva** — CSAT é medível por trilha (uma pesquisa, na casca, com exclusão de etapa verificada nos dois arranjos) e cruzável com o SLA composto num relatório-unidade por jornada. As ressalvas são operacionais: disparo imediato requer trigger, resposta depende de canal autenticado do cliente, e a ramificação sob a casca só deve existir quando o processo é paralelo por desenho — bifurcação acidental (etapa duplicada) é mitigada pela costura automatizada abrir as etapas, não agentes (ver T8).

### T8 — Ramificação paralela na trilha

- **O que prova:** a trilha suporta etapas paralelas por desenho, com casca fechando por completude, CSAT único e extrator que trata árvore (não só cadeia linear).
- **Montagem:** casca 21 (Cliente Teste POC, Celula SAC, Devolucao, tag `trilha_casca`, pendente) + duas etapas abertas **em paralelo**, ambas com lookup → casca e tag `etapa_trilha` (arranjo B): P1 = ticket 22 (Coleta, Celula Transporte) e P2 = ticket 23 (NFD, Celula Logistica).
- **Fechamento por completude (verificado):** regra "casca só resolve quando todas as filhas resolverem", implementada como script consultando os irmãos pelo lookup (papel que em produção é do webhook/integração — **triggers e automações nativos não consultam outros tickets**, condição cross-ticket não existe na plataforma; este é o limite que empurra a completude para a costura automatizada). Sequência do teste: resolver P1 → casca **permaneceu pendente** (filho 23 aberto); resolver P2 → **casca resolvida por completude**.
- **CSAT sob paralelismo (verificado):** pesquisa oferecida **uma única vez**, apenas na resolução final da casca — nada na resolução de P1 (primeira paralela), nada nas etapas (`unoffered` em 22 e 23; lista de ratings mostra oferta só no 21).
- **Extrator com caminho crítico:** código do T4/T7 estendido para árvores (filhos múltiplos, BFS pelo lookup), devolvendo a árvore completa, duas métricas etiquetadas — **duração da jornada** (primeiro created → último solved; caminho crítico) e **esforço total** (soma das permanências das etapas) — o SLA individual de cada etapa (`requester_wait_time`) e o `satisfaction_rating` da casca. Demonstrado nas duas topologias com o **mesmo extrator**: trilha paralela (raiz 21: jornada 53 s < esforço 70 s — assinatura do paralelismo) e trilha sequencial do T4 (raiz 10: jornada 5 s > esforço 2 s — assinatura da fila sequencial, gaps entre etapas).
- **Acidente × desenho (nota):** o rastro distingue os dois casos. Paralelismo **intencional** aparece como padrão que se repete por desenho da trilha: mesmas combinações de motivos-filho sob o mesmo motivo de casca, abertura quase simultânea, presente em toda ocorrência daquela trilha. Bifurcação **acidental** (etapa duplicada) aparece como anomalia: filho duplicado do mesmo motivo, fora do padrão da trilha, distribuição esparsa. A mitigação do acidente não é vigiar agente — é a **costura automatizada abrir as etapas** (macro/trigger/integração), eliminando a digitação manual do vínculo; o caso do T7 (duas cadeias na casca 14) foi exatamente um artefato de abertura manual.
- **Veredito: SIM** — ramificação paralela sustentada com casca fechando por completude, CSAT único e extrator de caminho crítico funcionando nas duas topologias. Ressalva única: a regra de completude não é expressável em trigger/automação nativos (condição cross-ticket inexiste); vive na costura automatizada via API/webhook — mesmo componente que já é pré-requisito para abrir etapas e preencher o vínculo.

### T9 — Legado, automações e permissões

**T9.1 — Campo obrigatório × ticket antigo (grau de esforço da migração)**

- **Montagem:** 5 tickets "legado" (24–28) criados no formulário existente; em seguida, campo novo "Aprovacao Financeira (POC T9)" (id 51441453381396) criado com as duas variantes de obrigatoriedade — `required: true` (agente, para resolver) e `required_in_portal: true` (end-user, na criação) — e adicionado ao mesmo formulário (leitura dos campos atuais + acréscimo; sem remoção).
- **Comportamento via API com o campo vazio no ticket antigo (ticket 24):** comentar → **200 (passa)**; reatribuir pessoa → **200 (passa)**; reatribuir grupo → **200, mas o grupo não mudou** — não por causa do campo: a trava corretiva do T6-B reverteu o movimento (ticket de Estorno movido para fora do Financeiro; tag `roteamento_corrigido` presente) — a trava operando em condição real; **resolver → 422** ("Aprovacao Financeira (POC T9): é necessário(a) para resolver um ticket") — **a obrigatoriedade de resolução é validada também na API**, não só na interface.
- **Migração em massa (1c):** `PUT /api/v2/tickets/update_many.json?ids=24,...,28` preenchendo o campo novo e definindo o grupo numa única chamada → retorna `job_status`; acompanhamento por polling em `/api/v2/job_statuses/{id}`; job `completed`, 5/5 sucesso. Limites de mecânica: até 100 ids por chamada (lotes maiores = paginar em jobs sucessivos); jobs são assíncronos e enfileirados. Após o preenchimento em lote, o resolver do ticket 24 passou (200 → solved). Observação de migração: movimentos de grupo que violem travas corretivas são revertidos pelo próprio trigger — a migração deve mover para combinações válidas ou desativar temporariamente as travas durante a janela de migração.
- **Veredito e sequência recomendada:** o que trava é **somente o resolver** com campo obrigatório vazio (UI e API); comentar e reatribuir passam — a operação não para. Sequência que migra legado sem parar operação: (1) criar o campo novo **sem** obrigatoriedade; (2) preencher o legado em massa via update_many/jobs; (3) ativar `required: true` depois do backfill; (4) travas corretivas desativadas ou alinhadas durante a janela. Nessa ordem, nenhum ticket fica bloqueado em nenhum momento.

**T9.2 — Autonomia de views (1 grupo + N views por submotivo)**

- Duas views criadas no **mesmo grupo** (Celula Financeiro), filtradas por valores diferentes do Submotivo (subcategoria) e com conjuntos de colunas **diferentes**, incluindo campos customizados como coluna: "POC View - Estorno Critico" (id 51441438099348; colunas subject, requester, Motivo, Submotivo) e "POC View - Estorno Padrao" (id 51441419457428; colunas subject, priority, created, Submotivo).
- Verificado: cada view retorna somente os tickets do seu submotivo (crítico: 25; padrão: 26, 27 e 9 — o legado 24 saiu ao ser resolvido, coerente com a condição status < solved), com suas próprias colunas.
- Campo novo adicionado ao formulário **depois** das views: ambas permaneceram intactas (condições e colunas inalteradas).
- **Veredito: SIM** — 1 grupo + N views por submotivo reproduz o workspace atual por grupo, com colunas específicas por contexto (o caso "estorno Pix vs conciliação" num grupo só). Sem ressalva de plataforma; a única nota é de gestão (views compartilhadas são administradas por quem tem permissão de views — ver T9.4).

**T9.3 — Renome × automações**

- Trigger criado referenciando grupo na ação e campo na condição (id no histórico); em seguida, **renomeados via API** o grupo Celula Logistica (→ "Celula Logistica RENOMEADA T9") e o **título** do campo Motivo (categoria) (→ "Motivo (categoria) RENOMEADO T9") — IDs inalterados.
- Ticket criado **após os renomes** (id 29, motivo Generico A) → roteado corretamente para o grupo renomeado (id 51262745284372). Renomes revertidos na sequência (registrados no histórico).
- **Veredito: automações sobrevivem a renome — referência é por ID.** Consequência para o projeto: renomear grupos/campos no go-live é seguro; apenas grupos **extintos** no colapso exigem de-para de automações (transferir referências antes de excluir). O medo do renome não tem fundamento técnico.

**T9.4 — Permissão de membresia e views (autonomia de gestão)**

- `GET /api/v2/custom_roles.json` respondeu (200) — leitura de papéis disponível no trial (boost Enterprise). Papéis existentes × permissões relevantes:

| Papel | Gerir membros de grupo | Views | Gerir campos/formulários | Acesso a tickets |
|---|---|---|---|---|
| Agente light | não | somente leitura | não | do próprio grupo |
| Colaborador | não | somente leitura | não | do próprio grupo |
| Administrador de faturamento | sim | completo | sim | todos |
| Administrador | sim | completo | sim | todos |

- **Criar** papel custom não-admin (ex.: "Gestor de Célula" com `group_access` e views) → **402 Payment Required**: a criação de papéis personalizados não está coberta pelo trial/boost — é recurso Enterprise pleno.
- **Veredito: registrado com limite.** No trial, gestão de membros de grupo e de views compartilhadas é privilégio de administrador; papel intermediário não-admin com essas permissões existe na plataforma (custom roles), mas **exige Enterprise** — item a conferir contra o plano contratado. Se o plano final for Growth/Professional, a autonomia de gestão de células fica com admins; se Enterprise, um papel "gestor de célula" é configurável.

**Veredito geral do T9:** a migração de legado é de esforço **baixo e sequenciável** (nada trava a operação se a obrigatoriedade entrar depois do backfill em massa, que é nativo via jobs); a autonomia operacional por views é **plena**; renome é **seguro por construção** (referência por ID), restando de-para apenas para grupos extintos; e a autonomia de gestão descentralizada (papéis custom) é o único item **condicionado a plano** (Enterprise). Nenhum bloqueio de plataforma para a estratégia de migração do desenho.

## 3. Resumo dos vereditos

| Teste | Premissa | Veredito |
|---|---|---|
| T1 | Formulário unificado com condicionalidade categoria→subcategoria | Sustentada com ressalva (condicionalidade por campo, não por opção) |
| T2 | SLA ancorada no valor da subcategoria | Sustentada com ressalva (solicitante end-user; prioridade definida; defasagem de metric_events) |
| T3 | Roteamento por grupo; trocar motivo não roteia | Sustentada (pressupõe membresia dos agentes nas células) |
| T4 | SLA de trilha calculável sobre o rastro da plataforma | Sustentada com ressalva (vínculo via campo lookup, preenchimento é responsabilidade do processo) |
| T5 | Features cabem no plano | Registrado — Suite Growth+ cobre tudo o que foi usado |
| T6-A | Cliente vê um número só; etapas medem SLA; cadeia reconstruível | Sustentada no arranjo A (métrica das etapas = requester_wait_time; invisibilidade exige só notas internas) |
| T6-B | Disciplina de roteamento sustentável por plataforma | Sustentada (trava corretiva por trigger reverte e marca, sem loop) |
| T7 | CSAT medível por trilha e cruzável com SLA composto | Sustentada com ressalva (trigger para disparo imediato; canal autenticado do cliente; ramificação só quando paralela por desenho — acidente mitigado pela costura automatizada) |
| T8 | Ramificação paralela com completude, CSAT único e caminho crítico | Sustentada (ressalva: completude vive na costura via API/webhook — condição cross-ticket não existe em trigger/automação) |
| T9.1 | Campo obrigatório não trava legado se sequenciado (backfill em massa nativo) | Sustentada (só o resolver trava com campo vazio — validado também na API; sequência recomendada documentada) |
| T9.2 | 1 grupo + N views por submotivo reproduz o workspace por grupo | Sustentada |
| T9.3 | Automações sobrevivem a renome (referência por ID) | Sustentada (de-para só para grupos extintos) |
| T9.4 | Papel não-admin para gerir membros/views | Registrado com limite — existe (custom roles), mas exige Enterprise; conferir plano contratado |

## 4. Teardown

A instância é descartável (expira sozinha). Para desmontagem antecipada ou reexecução limpa, `historico/manifest.json` lista todo objeto criado (tipo, id, nome), na ordem inversa recomendada de remoção: tickets → triggers → políticas SLA → formulário → campos → memberships → grupos → schedule → usuário sintético.
