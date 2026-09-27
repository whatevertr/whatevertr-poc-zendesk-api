# -*- coding: utf-8 -*-
"""
Simulacao pos-coleta — modelo de projecao as-is x to-be.
Projeta o estado to-be sobre as duas planilhas de coleta (Ferramentas 01 e 02).
Nao posta nada; leitura local apenas.

Glossario (termos de dados, sem jargao interno):
- Grupo ATIVO  = grupo as-is que mapeia para uma celula to-be (tem destino).
- Grupo ORFAO  = grupo sem destino/dono valido (registro sem pai); fora da projecao.
- Bloco        = chave de agrupamento dos grupos as-is.
- Categoria    = motivo de atendimento (nivel 1). Subcategoria = submotivo (nivel 2).

Uso: POC_DIR="/caminho/da/pasta" python3 simulacao_pos_coleta.py
"""
import os
from collections import defaultdict
from pathlib import Path
import openpyxl

# =====================================================================
# PARAMETROS EDITAVEIS, recalibrar aqui conforme as coletas acontecerem
# None = usar o que esta marcado nas planilhas (estado atual). Um valor
# numerico substitui a marcacao da planilha pela projecao percentual.
# =====================================================================
PCT_EXCLUIR_COLAPSADOS = None   # ex.: 0.15 -> 15% dos grupos colapsados marcados Excluir
PCT_SUBCAT_NOVAS       = None   # ex.: 0.05 -> novas subcategorias = 5% das linhas da arvore
ORFAOS_VIRAM_CELULAS   = False  # True: cada bloco orfao vira 1 celula
                                # False: bloco orfao (sem celula) fica fora da projecao
F01 = '01_FERRAMENTA_Area_Colapso_Grupos_Zendesk_POC.xlsx'
F02 = '02_FERRAMENTA_Coleta_SLA_Formularios_Zendesk_POC.xlsx'
# =====================================================================

BASE = Path(os.environ.get('POC_DIR', '.'))

def carrega():
    wb1 = openpyxl.load_workbook(BASE / F01)
    cg = list(wb1['colapso_grupos'].iter_rows(min_row=2, values_only=True))
    premissas1 = list(wb1['Premissas_Dummy'].iter_rows(values_only=True))
    wb2 = openpyxl.load_workbook(BASE / F02)
    sla = list(wb2['SLA (coleta)'].iter_rows(min_row=3, values_only=True))
    fm = [r for r in wb2['Formulários (apoio TI)'].iter_rows(min_row=3, values_only=True)
          if r[1] and not str(r[1]).startswith('★')]
    premissas2 = list(wb2['Premissas_Dummy'].iter_rows(values_only=True))
    return cg, sla, fm, premissas1, premissas2

def modelo(cg, sla, fm):
    # --- mapa grupo as-is -> celula to-be (forward-fill no bloco) ---
    mapa, cur_bloco, cur_cel = {}, object(), None
    for r in cg:
        bloco, grupo, cel = r[0], r[4], r[5]
        if bloco != cur_bloco: cur_bloco, cur_cel = bloco, None
        if cel: cur_cel = cel
        mapa[grupo] = cur_cel
    grupos_asis = [r[4] for r in cg if r[4]]
    celulas = set(v for v in mapa.values() if v)
    orfaos = [g for g, v in mapa.items() if not v]           # grupos sem destino
    blocos_orfaos = set(r[0] for r in cg if not mapa.get(r[4]))

    # --- arvore de categorias / colapsados / novos ---
    arv = [r for r in sla if r[11] == 'motivos']
    col = [r for r in sla if r[11] == 'grupo colapsado']
    nov = [r for r in sla if r[11] and 'reuni' in str(r[11])]
    exc = [r for r in col if r[12] and str(r[12]).startswith('Excluir')]
    if PCT_EXCLUIR_COLAPSADOS is not None:
        n_exc = round(PCT_EXCLUIR_COLAPSADOS * len(col))
    else:
        n_exc = len(exc)
    n_nov = round(PCT_SUBCAT_NOVAS * len(arv)) if PCT_SUBCAT_NOVAS is not None else len(nov)

    cat_asis = len(set(r[1] for r in arv))                   # categorias distintas (as-is)
    sub_asis = sum(1 for r in arv if r[0] == 'Subcategoria')
    cat_puras_asis = sum(1 for r in arv if r[0] == 'Categoria')
    col_mantidos = len(col) - n_exc
    sla_asis = sum(1 for r in arv if r[4] and str(r[4]).startswith('Sim'))

    tobe_celulas = len(celulas) + (len(blocos_orfaos) if ORFAOS_VIRAM_CELULAS else 0)
    tobe_cat = cat_asis + col_mantidos          # colapsados mantidos entram como categoria
    tobe_sub = sub_asis + n_nov                 # novas subcategorias sob categoria existente
    tobe_sla = tobe_sub + cat_puras_asis + col_mantidos  # ancora: subcategoria; sem ela, categoria

    comp = [
        ('Grupos ativos (mapeados p/ celula)', len(grupos_asis) - len(orfaos), len(celulas)),
        ('Grupos orfaos (sem celula/destino)', len(orfaos),
         len(blocos_orfaos) if ORFAOS_VIRAM_CELULAS else '(fora da projecao)'),
        ('Motivos (categoria)', cat_asis, tobe_cat),
        ('Submotivos (subcategoria)', sub_asis, tobe_sub),
        ('Linhas de SLA', sla_asis, tobe_sla),
    ]

    # --- projecao por trilha (formulario = trilha) ---
    forms = defaultdict(list)
    for r in fm: forms[r[0]].append((r[1], r[2] or 0))
    trilhas = []
    for fname, pares in forms.items():
        gs = {}
        for g_, p in pares: gs[g_] = gs.get(g_, 0) + p
        n_asis = len(gs)
        cel_uso = defaultdict(float); n_orf = 0
        for g_, p in gs.items():
            c = mapa.get(g_)
            if c: cel_uso[c] += p
            else: n_orf += 1; cel_uso['(orfao) ' + g_] = p
        n_tobe = len(set(mapa.get(g_) for g_ in gs if mapa.get(g_))) + n_orf
        red = 1 - n_tobe / n_asis if n_asis else 0.0
        # nro efetivo (ponderado pelo uso 2025): 1/soma(p^2) com p normalizado
        tot = sum(gs.values()) or 1
        den = sum((p/tot)**2 for p in gs.values())
        eff_asis = 1/den if den else float(len(gs))
        totc = sum(cel_uso.values()) or 1
        denc = sum((p/totc)**2 for p in cel_uso.values())
        eff_tobe = 1/denc if denc else float(len(cel_uso))
        red_pond = 1 - eff_tobe / eff_asis if eff_asis else 0.0
        trilhas.append({'form': fname, 'asis': n_asis, 'tobe': n_tobe, 'orf': n_orf,
                        'uso': tot, 'red': red, 'eff_asis': eff_asis, 'eff_tobe': eff_tobe,
                        'red_pond': red_pond})
    trilhas.sort(key=lambda x: -x['asis'])
    return comp, trilhas

def imprime(comp, trilhas):
    print('== COMPARATIVO AS-IS x TO-BE PROJETADO ==')
    for nome, a, b in comp:
        red = f"{(1 - b/a)*100:5.1f}%" if isinstance(b, (int, float)) and a else '     -'
        print(f'{nome:<40} {a:>6} -> {str(b):>18} {red}')
    print()
    print('== PROJECAO POR TRILHA (formulario = trilha) — top 15 por tamanho ==')
    print(f"{'formulario':<38} {'as-is':>5} {'to-be':>5} {'orf':>4} {'red%':>6} {'red% pond.uso':>13}")
    for t in trilhas[:15]:
        print(f"{str(t['form'])[:38]:<38} {t['asis']:>5} {t['tobe']:>5} {t['orf']:>4} "
              f"{t['red']*100:>5.1f}% {t['red_pond']*100:>12.1f}%")
    n = len(trilhas)
    m_simples = sum(t['red'] for t in trilhas) / n
    soma_uso = sum(t['uso'] for t in trilhas) or 1
    m_uso = sum(t['red'] * t['uso'] for t in trilhas) / soma_uso
    m_pond = sum(t['red_pond'] for t in trilhas) / n
    print(f'\ntrilhas: {n}')
    print(f'reducao media simples (contagem distinta):      {m_simples*100:.1f}%')
    print(f'reducao media ponderada pelo uso 2025:          {m_uso*100:.1f}%')
    print(f'reducao media do nro efetivo (uso-concentrado): {m_pond*100:.1f}%')

if __name__ == '__main__':
    cg, sla, fm, p1, p2 = carrega()
    print('Parametros registrados nas abas Premissas_Dummy:')
    for r in p2 + p1:
        if r[1]: print(f'  - {r[0]}: {r[1]}')
    print()
    comp, trilhas = modelo(cg, sla, fm)
    imprime(comp, trilhas)
