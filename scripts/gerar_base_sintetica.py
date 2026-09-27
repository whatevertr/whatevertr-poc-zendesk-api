# -*- coding: utf-8 -*-
"""
Gerador de base SINTETICA para a simulacao pos-coleta.

Por que existe: a simulacao foi rodada, na origem, sobre duas planilhas reais de
uma operacao (que NAO podem ser publicadas). Para o repositorio ser honesto e
reproduzivel, este gerador cria duas planilhas de entrada com dados
**inteiramente sinteticos, gerados por parametros declarados abaixo** (seed fixa).
Rodar a simulacao sobre elas demonstra que o MODELO funciona e reproduz — os
numeros sao consequencia dos parametros, nao achado sobre nenhuma organizacao real.

A base sintetica NAO e a real perturbada: e gerada do zero por parametros, para
que nem a forma da distribuicao real vaze.

Glossario (termos de dados, sem jargao interno):
- Grupo ATIVO  = grupo as-is que mapeia para uma celula to-be (tem destino).
- Grupo ORFAO  = grupo sem destino/dono valido no bloco (registro sem pai);
                 nao representa fluxo real. Fica fora da projecao.
- Bloco        = chave de agrupamento dos grupos as-is (neutra).
- Categoria    = motivo de atendimento (nivel 1 da taxonomia).
- Subcategoria = submotivo (nivel 2, sob a categoria).

Uso:
    python gerar_base_sintetica.py            # grava em ../data/
"""
import random
from pathlib import Path
import openpyxl

# ===================== PARAMETROS DECLARADOS (seed fixa) =====================
SEED = 42
N_BLOCOS               = 44     # blocos de agrupamento
GRUPOS_MIN, GRUPOS_MAX = 3, 9   # grupos as-is por bloco
PCT_BLOCO_ORFAO        = 0.16   # blocos sem celula (grupos ficam orfaos)
N_CATEGORIAS           = 60     # categorias (motivos) na arvore as-is
PCT_SUB_POR_CATEGORIA  = 1.4    # media de subcategorias por categoria
PCT_SLA_PREENCHIDO     = 0.45   # fracao das linhas da arvore com SLA "Sim"
N_COLAPSADOS           = 50     # grupos colapsados (candidatos)
PCT_EXCLUIR            = 0.30   # fracao dos colapsados marcados "Excluir"
N_NOVOS_REUNIAO        = 15     # categorias novas surgidas em reuniao
N_FORMULARIOS          = 30     # formularios (= trilhas)
GRUPOS_POR_FORM_MIN, GRUPOS_POR_FORM_MAX = 2, 12
# ============================================================================

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
F01 = '01_FERRAMENTA_Area_Colapso_Grupos_Zendesk_POC.xlsx'
F02 = '02_FERRAMENTA_Coleta_SLA_Formularios_Zendesk_POC.xlsx'


def gerar():
    random.seed(SEED)
    DATA_DIR.mkdir(exist_ok=True)

    # ---------- F01: colapso_grupos ----------
    wb1 = openpyxl.Workbook()
    ws = wb1.active; ws.title = 'colapso_grupos'
    ws.append(['Bloco', 'col2', 'col3', 'col4', 'Grupo (as-is)', 'Celula (to-be)'])
    grupos_todos = []
    gid = 0
    cel_id = 0
    for b in range(1, N_BLOCOS + 1):
        bloco = f'bloco-{b:02d}'
        n = random.randint(GRUPOS_MIN, GRUPOS_MAX)
        orfao = random.random() < PCT_BLOCO_ORFAO
        celula = None if orfao else f'Celula {(cel_id := cel_id + 1):02d}'
        for j in range(n):
            gid += 1
            grupo = f'grupo-{gid:03d}'
            grupos_todos.append(grupo)
            # celula so na 1a linha do bloco (forward-fill no script)
            ws.append([bloco, '', '', '', grupo, celula if j == 0 else None])
    prem1 = wb1.create_sheet('Premissas_Dummy')
    prem1.append(['Base', 'SINTETICA (gerada por parametros declarados, seed=42)'])
    prem1.append(['Escopo', 'demonstracao do modelo — nao e dado de organizacao real'])
    wb1.save(DATA_DIR / F01)

    # ---------- F02: SLA (coleta) ----------
    wb2 = openpyxl.Workbook()
    sla = wb2.active; sla.title = 'SLA (coleta)'
    sla.append(['Nivel', 'Motivo', 'c2', 'c3', 'SLA', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'Tipo', 'Acao'])
    sla.append(['', '', '', '', '', '', '', '', '', '', '', '', ''])  # linha 2 (script le de row 3)
    # arvore: categorias + subcategorias
    for i in range(1, N_CATEGORIAS + 1):
        cat = f'categoria-{i:03d}'
        slap = 'Sim (8h uteis)' if random.random() < PCT_SLA_PREENCHIDO else ''
        sla.append(['Categoria', cat, '', '', slap, '', '', '', '', '', '', 'motivos', ''])
        for _k in range(1 if random.random() < (PCT_SUB_POR_CATEGORIA - 1) else 0 + 1):
            slap3 = 'Sim (4h uteis)' if random.random() < PCT_SLA_PREENCHIDO else ''
            sla.append(['Subcategoria', f'{cat}.sub{_k+1}', '', '', slap3, '', '', '', '', '', '', 'motivos', ''])
    # grupos colapsados
    for i in range(1, N_COLAPSADOS + 1):
        acao = 'Excluir (sem uso)' if random.random() < PCT_EXCLUIR else 'Manter'
        sla.append(['', f'colapsado-{i:03d}', '', '', '', '', '', '', '', '', '', 'grupo colapsado', acao])
    # categorias novas de reuniao
    for i in range(1, N_NOVOS_REUNIAO + 1):
        sla.append(['Subcategoria', f'nova-reuniao-{i:02d}', '', '', 'Sim (8h uteis)', '', '', '', '', '', '', 'novo (reuniao de coleta)', ''])

    # ---------- F02: Formularios (apoio TI) ----------
    fm = wb2.create_sheet('Formulários (apoio TI)')
    fm.append(['Formulario', 'Grupo', 'Uso 2025', 'c3'])
    fm.append(['★ cabecalho ignorado', '★', '', ''])  # linha 2, ignorada
    for f in range(1, N_FORMULARIOS + 1):
        form = f'Trilha {f:02d}'
        k = random.randint(GRUPOS_POR_FORM_MIN, GRUPOS_POR_FORM_MAX)
        for g in random.sample(grupos_todos, min(k, len(grupos_todos))):
            uso = random.randint(1, 500)  # peso de uso sintetico
            fm.append([form, g, uso, ''])
    prem2 = wb2.create_sheet('Premissas_Dummy')
    prem2.append(['Base', 'SINTETICA (gerada por parametros declarados, seed=42)'])
    prem2.append(['Uso 2025', 'pesos sinteticos aleatorios — nao refletem volume real'])
    wb2.save(DATA_DIR / F02)

    print(f'OK: base sintetica em {DATA_DIR}')
    print(f'  {F01} — grupos as-is: {len(grupos_todos)}')
    print(f'  {F02} — categorias: {N_CATEGORIAS}, colapsados: {N_COLAPSADOS}, novos: {N_NOVOS_REUNIAO}, trilhas: {N_FORMULARIOS}')


if __name__ == '__main__':
    gerar()
