# Final da Copa do Brasil 2026: Grêmio x Palmeiras, jogo único em campo neutro (Mané Garrincha, 06/12)
import json, numpy as np, sys
sys.path.insert(0, '/home/claude')
src = open('sim39.py').read()
ns = {}; exec(src[:src.index('N=100_000; rng=')], ns)
lambdas, REC, probs, placar, CUR_R = ns['lambdas_ch'], ns['REC'], ns['probs'], ns['placar'], ns['CUR_R']
CUR_R[0] = None                       # XI titular de cada clube (sem a suspensão de jogo específico)
G, P = 'gremio', 'palmeiras'
lh1, la1 = lambdas(G, P); lh2, la2 = lambdas(P, G)
lg = (lh1 + la2)/2*REC[G]['att']*REC[P]['def_']   # campo neutro: média dos dois mandos + fase recente
lp = (la1 + lh2)/2*REC[P]['att']*REC[G]['def_']
w, d, l = probs(lg, lp)
N = 200_000; rng = np.random.default_rng(20261206)
fg = np.exp(rng.normal(0, .10, N))*np.exp(rng.normal(0, .10, N)); fp = np.exp(rng.normal(0, .10, N))*np.exp(rng.normal(0, .10, N))
g = rng.poisson(lg*fg); p = rng.poisson(lp*fp)
# inflaciona empates como no campeonato (rho 0,08): converte parte dos jogos decididos por 1 gol em empate
emp = g == p
alvo = d - emp.mean()
if alvo > 0:
    um = np.where(np.abs(g - p) == 1)[0]; k = int(alvo*N)
    esc = rng.choice(um, size=min(k, len(um)), replace=False); m = np.maximum(g[esc], p[esc]); g[esc] = m; p[esc] = m
emp = g == p
# prorrogação: 30 minutos, ritmo de gols ~85% do tempo normal
ge = rng.poisson(lg*fg*(30/90)*0.85); pe_ = rng.poisson(lp*fp*(30/90)*0.85)
pro_g = emp & (ge > pe_); pro_p = emp & (pe_ > ge); pen = emp & (ge == pe_)
# pênaltis: 50% cada (ver nota)
pen_g = pen & (rng.random(N) < 0.5); pen_p = pen & ~pen_g
tit_g = (g > p) | pro_g | pen_g
res = dict(jogo='Grêmio x Palmeiras', data='06/12', local='Mané Garrincha, Brasília (campo neutro)',
  xg_gremio=round(lg, 2), xg_palmeiras=round(lp, 2),
  gremio_90=round((g > p).mean()*100, 1), empate_90=round(emp.mean()*100, 1), palmeiras_90=round((p > g).mean()*100, 1),
  gremio_prorrogacao=round(pro_g.mean()*100, 1), palmeiras_prorrogacao=round(pro_p.mean()*100, 1), penaltis=round(pen.mean()*100, 1),
  gremio_penaltis=round(pen_g.mean()*100, 1), palmeiras_penaltis=round(pen_p.mean()*100, 1),
  titulo_gremio=round(tit_g.mean()*100, 1), titulo_palmeiras=round((~tit_g).mean()*100, 1),
  placares=[dict(placar=f"{a} x {b}", prob=round(float(((g == a) & (p == b)).mean()*100), 1)) for a, b in sorted({(int(x), int(y)) for x, y in zip(g[:20000], p[:20000])}, key=lambda t: -((g == t[0]) & (p == t[1])).mean())[:6]],
  fatores=dict(gremio=dict(goleiro=ns['LIN'][G]['goleiro'], xi=ns['LIN'][G]['xi'], fase_ataque=round(REC[G]['att'], 3), fase_defesa=round(REC[G]['def_'], 3)),
               palmeiras=dict(goleiro=ns['LIN'][P]['goleiro'], xi=ns['LIN'][P]['xi'], fase_ataque=round(REC[P]['att'], 3), fase_defesa=round(REC[P]['def_'], 3))))
json.dump(res, open('dash/final_cdb.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'fatores'}, ensure_ascii=False, indent=0))
print('mando G:', round(lh1, 2), round(la1, 2), '| mando P:', round(lh2, 2), round(la2, 2))
