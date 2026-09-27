# Nota de método — como isto foi construído · Method note — how this was built

> 🇧🇷 português abaixo · 🇺🇸 English below · *link do repositório do método: (a definir)*

---

## 🇧🇷 Português

Esta validação é um resultado aplicado do **The Constellation Method** (*Método Constelação: uma estrutura triádica de contexto com um modelo autoral de cognição do usuário*), criado por mim, em desenvolvimento incremental. É um método de colaboração humano-IA — uma variante *self-authored* e epistêmica de *context engineering* (termo documentado pela [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

O método monta o contexto em camadas **antes** de o trabalho começar: enquadramento da tarefa, um papel explícito com restrições epistêmicas, e um modelo autoautorado da cognição da autora (autoria no sentido de **autoridade sobre o conteúdo**: a formulação é elicitada em diálogo com a instância, mas o modelo é validado e de propriedade da autora — como ela raciocina e onde erra — não inferido pela máquina). Carrega uma função reutilizável, o **cronista**, que sustenta um **piso epistêmico**: marcar o que não foi verificado, discordar quando a evidência discorda, manter um placar honesto. São técnicas reconhecidas (mitigação de *sycophancy*, [Sharma et al. 2023](https://arxiv.org/abs/2310.13548); confiança verbalizada, [Tian et al. 2023](https://aclanthology.org/2023.emnlp-main.330/)) — passadas por um prompt, elas **atenuam** a bajulação, não a removem.

**A execução rodou sob esse piso, e a marca está no registro:** o histórico numerado de request/response guarda as falhas ao lado dos acertos (erros de payload 422, limites de plano 402, rotas descontinuadas 404) — log de auditoria, não vitrine editada. Os vereditos são declarados com seus limites ("sustentada, com ressalva"), não como achados só favoráveis. Os pares numerados são um script executável: a montagem se reproduz a partir deles.

O método completo será publicado de forma incremental. Estas são **notas de campo, datadas e versionadas**.

---

## 🇺🇸 English

This validation is an applied outcome of **The Constellation Method** (*a triadic context scaffold with a self-authored user-cognition model*), created by me, in incremental development. It is a human–AI collaboration method — a *self-authored*, epistemic variant of context engineering (term documented by [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

The method assembles context in layers **before** the work begins: task framing, an explicit role with epistemic constraints, and a self-authored model of the author's cognition (authorship here meaning **authority over the content**: the wording is elicited in dialogue with the instance, but the model is validated by and owned by the author — how she reasons and where she errs — not inferred by the machine). It carries a reusable function, the **chronicler**, that holds an **epistemic floor**: mark what is unverified, disagree when the evidence disagrees, keep an honest scorecard. These are recognized techniques (sycophancy mitigation, [Sharma et al. 2023](https://arxiv.org/abs/2310.13548); verbalized confidence, [Tian et al. 2023](https://aclanthology.org/2023.emnlp-main.330/)) — passed through a prompt, they **attenuate** sycophancy, they don't remove it.

**The execution ran under that floor, and its mark is in the record:** the numbered request/response history keeps failures alongside passes (payload errors 422, plan limits 402, discontinued routes 404) — an audit log, not an edited showcase. Verdicts are stated with their limits ("supported, with caveat"), not favorable-only findings. The numbered pairs are an executable script: the setup reproduces from them.

The full method will be published incrementally. These are **field notes, dated and versioned**.
