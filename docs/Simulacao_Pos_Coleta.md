# Simulação Pós-Coleta — Modelo de Projeção As-Is × To-Be

> ⚠️ **Escopo (leia primeiro).** Os números desta página são **calculados sobre uma base sintética**, em `data/`, gerada por parâmetros declarados (`scripts/gerar_base_sintetica.py`, seed fixa). Eles **demonstram o funcionamento e a reprodutibilidade do modelo — não são achado sobre nenhuma organização real.** A base sintética foi gerada do zero por parâmetros, não é uma base real perturbada. A magnitude de qualquer redução aqui é consequência dos parâmetros escolhidos, não uma medição do mundo.

## Glossário (termos de dados, sem jargão interno)
- **Grupo ativo** — grupo as-is que mapeia para uma célula to-be (tem destino).
- **Grupo órfão** — grupo sem destino/dono válido (registro sem referência-pai); não representa fluxo real. Fica fora da projeção.
- **Bloco** — chave de agrupamento dos grupos as-is.
- **Categoria** — motivo de atendimento (nível 1 da taxonomia). **Subcategoria** — submotivo (nível 2, sob a categoria).

## O que o modelo faz

Dado um desenho de atendimento que cresceu sem estrutura — muitos grupos, sem taxonomia consistente — a reorganização proposta **colapsa grupos em células** (grupo as-is → célula to-be) e organiza os atendimentos numa árvore **categoria → subcategoria** com SLA por nó. Este modelo projeta o estado to-be sobre duas planilhas de coleta e mede o efeito:

- **Ferramenta 01** (`data/01_FERRAMENTA_Area_Colapso_Grupos_Zendesk_POC.xlsx`) — aba `colapso_grupos`: por bloco, quais grupos as-is colapsam em qual célula to-be. Bloco sem célula → grupos **órfãos** (fora da projeção).
- **Ferramenta 02** (`data/02_FERRAMENTA_Coleta_SLA_Formularios_Zendesk_POC.xlsx`) — aba `SLA (coleta)`: árvore categoria/subcategoria, grupos colapsados (manter/excluir), categorias novas; aba `Formulários (apoio TI)`: cada formulário = uma trilha, com o grupo e o peso de uso.

## Como reproduzir

```bash
pip install -r scripts/requirements.txt
python scripts/gerar_base_sintetica.py                 # cria data/ (sintética, seed=42)
POC_DIR="data" python scripts/simulacao_pos_coleta.py  # roda o modelo e imprime o comparativo
```

Todo número abaixo sai desse comando. Mudar os parâmetros declarados no topo de `gerar_base_sintetica.py` muda os números — de propósito: é o que evidencia que são calculados, não fixados.

## Premissas de cálculo (verificáveis nas planilhas)

1. **Mapa grupo→célula:** a célula to-be vale para todas as linhas do mesmo bloco (preenchida na 1ª linha; forward-fill). Grupo sem célula no bloco fica **órfão**.
2. **Bloco órfão:** grupos de um bloco sem célula ficam **fora da projeção**. O parâmetro `ORFAOS_VIRAM_CELULAS` simula o cenário em que cada bloco órfão vira 1 célula.
3. **Categorias to-be** = categorias distintas da árvore as-is + grupos colapsados mantidos (total − marcados "Excluir"). Colisão de nomes verificada no modelo.
4. **Subcategorias to-be** = subcategorias da árvore + novas surgidas em reunião.
5. **Linhas de SLA:** âncora na subcategoria; sem ela, na categoria.
6. **Trilha = formulário:** grupo sem célula conta como destino próprio (não colapsa).

## Resultado sobre a base sintética (exemplo desta rodada)

Comparativo as-is × to-be (seed=42; muda com os parâmetros):

| Dimensão | As-is | To-be projetado |
|---|---|---|
| Grupos ativos (mapeados p/ célula) | 204 | 35 |
| Grupos órfãos (sem célula/destino) | 64 | fora da projeção |
| Motivos (categoria) | 120 | 152 |
| Submotivos (subcategoria) | 60 | 75 |
| Linhas de SLA | 58 | 167 |

**Leitura do modelo (mecânica, não achado):** o colapso reduz o nº de grupos; em contrapartida, grupos colapsados que são mantidos reaparecem como **categoria** da célula (por construção da regra), e as linhas de SLA a coletar aumentam — o modelo **transfere a complexidade do roteamento (grupos) para a taxonomia (categorias)**, onde ela é gerida por formulário, não por estrutura organizacional. O crescimento de categorias/SLA é essa transferência, não um efeito indesejado.

Projeção por trilha (30 trilhas nesta rodada) — médias:

| Métrica | Valor (base sintética) |
|---|---|
| Redução média simples (contagem distinta) | 4,8% |
| Redução média ponderada pelo uso | 7,1% |
| Redução média do nº efetivo de destinos (uso-concentrado) | 5,4% |

*(Números pequenos aqui são esperados: a base sintética distribui grupos entre formulários de forma aleatória declarada; o valor demonstra a métrica, não mede um caso real.)*

## Duas métricas de redução por trilha

- **red%** — por contagem distinta: 1 − (células to-be ÷ grupos as-is).
- **red% ponderada pelo uso** — número efetivo de destinos (1/Σp², p = peso do grupo no formulário): trilhas com uso concentrado em poucos grupos reduzem menos na prática. A diferença entre as duas é o que separa "remover destino ocioso" de "reduzir carga operacional real".

## Limites do modelo

- É modelo de **projeção**, não decisão — insumo de conferência humana.
- O bloco órfão (grupos sem célula) é a maior fonte de incerteza; enquanto não coletado, as reduções por trilha ficam subestimadas.
- Junção por nome de categoria exige chave composta quando há categorias repetidas entre guarda-chuvas.
- **Sobre a base:** ver o aviso de escopo no topo. Base sintética que exibe um fenômeno **não prova** o fenômeno — só mostra que o modelo o calcula e reproduz.
