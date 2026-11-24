"""Escalação esperada a partir de quem foi titular nos últimos 5 jogos do Brasileirão (FotMob).
Peso de cada jogador = titularidades/5 (zerado ou reduzido para quem está fora), normalizado para 10 jogadores de linha e 1 goleiro.
fin: finalização dos prováveis titulares (gols − xG sem pênaltis, encolhida pelo nº de chutes, S0=40), ponderada pelo peso
gk : goleiro(s) prováveis pelo mérito estimado por xGOT (encolhimento empírico), aplicado ao xGOT que o time costuma enfrentar
att: criação esperada (npxG + 0,8·xA por 90) vs o time mais usado da temporada, amortecida (^0,4)
dfn: xG impedido por 90 da linha esperada vs a mais usada (efeito pequeno)"""
import json, numpy as np
J = json.load(open('dash/jogadores.json'))
G = {(r['clube'], r['jogador']): r for r in json.load(open('temporada/gk2.json'))['rows']}
ST = json.load(open('v10/starts.json'))
# fora dos jogos que faltam (fração dos 3 jogos): lesões longas e suspensão já conhecida
FORA = {('Corinthians','Rodrigo Garro'): 1.0,
        ('Atlético-MG','Reinier'): 1.0, ('Atlético-MG','Victor Hugo'): 1.0}
S0 = 40.0
def esperado(clube, fora_extra=()):
    """XI definido (sem média): goleiro e 10 de linha com mais titularidades nos últimos 5 jogos (desempate: minutos na temporada).
    Quem está fora é trocado pelo jogador de mesma posição com mais titularidades fora do XI."""
    mins = {r['jogador']: r['minutos'] for r in J if r['clube'] == clube}
    posj = {r['jogador']: r['pos'] for r in J if r['clube'] == clube}
    gk, lin = [], []
    for it in ST[clube].split('|'):
        nm, v = it.rsplit('=', 1); n, pos = nm.rsplit(':', 1)
        (gk if pos == 'G' else lin).append((n, int(v)))
    fora = lambda n: FORA.get((clube, n), 0) >= 1 or n in fora_extra
    ordem = lambda L: sorted(L, key=lambda x: (-x[1], -mins.get(x[0], 0)))
    g = [n for n, _ in ordem(gk) if not fora(n)][:1]
    base = [n for n, _ in ordem(lin)][:10]
    resto = [n for n, _ in ordem(lin) if n not in base and not fora(n)]
    xi, trocas = [], []
    for n in base:
        if not fora(n): xi.append(n); continue
        p = posj.get(n); sub = next((m for m in resto if posj.get(m) == p), resto[0] if resto else None)
        if sub: resto.remove(sub); xi.append(sub); trocas.append(f"{sub} no lugar de {n}")
    return {g[0]: 1.0}, {n: 1.0 for n in xi}, trocas

def fatores(tot_xg, tot_xga, xgot_season, nome_code, clube_unico=None, fora_extra=()):
    out = {}
    for clube in ([clube_unico] if clube_unico else ST):
        c = nome_code[clube]
        pl = {r['jogador']: r for r in J if r['clube'] == clube and r['pos'] != 'Goleiro'}
        reg = sorted(pl.values(), key=lambda r: -r['minutos'])[:10]
        rate = lambda r: (r['npxg'] + 0.8*r['xa'])/r['minutos']*90
        imp = lambda r: r['xg_impedido']/r['minutos']*90
        avg_rate = np.mean([rate(r) for r in reg]); avg_imp = np.mean([imp(r) for r in reg])
        wg, wl, trocas = esperado(clube, fora_extra)
        r_xi = sum(w*(rate(pl[p]) if p in pl else 0.6*avg_rate) for p, w in wl.items()); r_reg = sum(rate(r) for r in reg)
        i_xi = sum(w*(imp(pl[p]) if p in pl else 0.6*avg_imp) for p, w in wl.items()); i_reg = sum(imp(r) for r in reg)
        att = float(np.clip((r_xi/r_reg)**0.4, 0.90, 1.06))
        dfn = float(np.clip(1 - 0.5*(i_xi - i_reg)/(tot_xga[c]/36), 0.97, 1.03))
        bonus = sum(w*(((pl[p]['gols']-pl[p]['pen_conv']) - pl[p]['npxg'])*pl[p]['chutes']/(pl[p]['chutes']+S0)) for p, w in wl.items() if p in pl)
        fin = float(np.clip(1 + bonus/tot_xg[c], 0.8, 1.25))
        m_rate = 0.0
        for k, w in wg.items():
            g = G.get((clube, k)); m_rate += w*((g['encolhido']/g['xgot']) if g and g['xgot'] > 0 else 0.0)
        prev = m_rate*xgot_season[c]
        gkf = float(np.clip(1 - prev/tot_xga[c], 0.8, 1.2))
        prov = sorted(wl.items(), key=lambda x: -x[1])
        out[c] = dict(clube=clube, goleiro=' / '.join(f"{k} ({round(v*100)}%)" if v < 0.99 else k for k, v in sorted(wg.items(), key=lambda x: -x[1])),
                      xi=[p for p, _ in prov[:10]], pesos=prov, trocas=trocas, gk=gkf, fin=fin, att=att, dfn=dfn, fin_bonus=round(bonus, 2), gk_prev=round(prev, 2),
                      ausentes_do_xi_regular=[r['jogador'] for r in reg if wl.get(r['jogador'], 0) < 0.4],
                      sem_dados=[p for p in wl if p not in pl])
    return out
