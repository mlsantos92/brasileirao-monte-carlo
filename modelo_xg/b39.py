import json
r=json.load(open('resultado39.json')); sj=json.load(open('simj39.json')); cen=json.load(open('cenario39.json'))
src=open("sim39.py").read(); ns={}; exec(src[:src.index('nome = {')],ns); geral=ns['geral']
G={(g['rodada'],g['mandante'],g['visitante']):g for g in r['jogos']}
S={(x['rodada'],geral[x['h']][0],geral[x['a']][0]):x for x in sj['simj']}
jg=[]
for k,g in G.items():
    x=S[k]
    jg.append(dict(jogo=f"{g['mandante']} x {g['visitante']}",rodada=g['rodada'],mandante=g['mandante'],visitante=g['visitante'],p_mandante=x['pm'],p_empate=x['pe'],p_visitante=x['pv'],gols_esp_mandante=x['gm'],gols_esp_visitante=x['gv'],placar_estimado=x['placar'],prob_placar=x['prob_placar'],distancia_km=int(g['dist'])))
json.dump(jg,open('dash/jogos.json','w'),ensure_ascii=False)
keys=['clube','pontos','estudo','z_xg_casa','z_xg_fora','z_xga_casa','z_xga_fora','z_gr_casa','z_gr_fora','z_gra_casa','z_gra_fora','gols_evitados','bonus_finalizadores','melhor_finalizador','rebaixamento','titulo','top5','g4','g6','pts_proj','pts_p10','pts_p90','ppg1','ppg2','ppg10','ppg_casa','ppg_casa5','ppg_fora','ppg_fora5']
cl=[]
for o in r['clubes']:
    d={k:o[k] for k in keys}; d['relax_38']=o['relax_por_rodada'][-1]; cl.append(d)
cl.sort(key=lambda x:-x['pontos']); json.dump(cl,open('dash/clubes.json','w'),ensure_ascii=False)
json.dump([dict(pontos_finais=int(k),permanencia=v) for k,v in r['safe_curve'].items()],open('dash/corte.json','w'))
json.dump([dict(z4=", ".join(c),prob=p) for c,p in r['z4']],open('dash/z4.json','w'),ensure_ascii=False)
nm={'gremio':'Grêmio','corinthians':'Corinthians','internacional':'Internacional','mirassol':'Mirassol','coritiba':'Coritiba'}
json.dump([dict(clube=geral[k][0],mandante_vence=v['cv'],empate=v['e'],visitante_vence=v['mv']) for k,v in r['cond'].items()],open('dash/cond.json','w'),ensure_ascii=False)
cz=[]
for x in r['cruz']:
    c,adv=x['clube'],x['adversario']; casa=x['local']=='Casa'
    key=(x['rodada'],c,adv) if casa else (x['rodada'],adv,c)
    s_=S[key]; g=G[key]
    w,d,l=(s_['pm'],s_['pe'],s_['pv']) if casa else (s_['pv'],s_['pe'],s_['pm'])
    a,b=s_['placar'].split(' x ')
    x.update(vitoria=w,empate=d,derrota=l,pts_esperados=round((3*w+d)/100,2),placar_estimado=f"{a} x {b}" if casa else f"{b} x {a}",distancia_km=int(g['dist']),
             gols_esp_clube=s_['gm'] if casa else s_['gv'], gols_esp_adv=s_['gv'] if casa else s_['gm'])
    cz.append(x)
json.dump(cz,open('dash/briga.json','w'),ensure_ascii=False)
# motivação por rodada
ordem=sj['ordem']; mot=[]
for clube,vals in sj['relax'].items():
    row=dict(clube=clube)
    for rr,v in zip(ordem,vals): row[f"r{rr}"]=v
    mot.append(row)
mot.sort(key=lambda x:-x['r38'])
json.dump(mot,open('dash/motivacao.json','w'),ensure_ascii=False)
# cenário
jgc=[dict(id=f"{g['rodada']}|{g['mandante']}|{g['visitante']}", rodada=g['rodada'], mandante=g['mandante'], placar=f"{g['gm']} x {g['gv']}", visitante=g['visitante']) for g in cen['jogos']]
base=sorted(geral, key=lambda k:(-geral[k][1],-geral[k][3],-(geral[k][6]-geral[k][7]),-geral[k][6]))
prevpos={geral[k][0]:i for i,k in enumerate(base,1)}; tb=[]
for rr in ordem:
    cur=[t for t in cen['tabelas'] if t['rodada']==rr]
    for t in cur: tb.append(dict(id=f"{rr}|{t['clube']}", rodada=rr, pos=t['pos'], clube=t['clube'], pontos=t['pontos'], jogos=t['jogos'], v=t['v'], e=t['e'], d=t['d'], sg=t['sg'], variacao=prevpos[t['clube']]-t['pos']))
    prevpos={t['clube']:t['pos'] for t in cur}
json.dump(jgc,open('dash/cen_jogos.json','w'),ensure_ascii=False); json.dump(tb,open('dash/cen_tabela.json','w'),ensure_ascii=False)
for t in cen['tabelas']:
    if t['rodada']==38 and t['pos']>=14: print(t['pos'],t['clube'],t['pontos'])
for g in cen['jogos']:
    if {'Grêmio','Corinthians','Internacional','Mirassol','Coritiba'} & {g['mandante'],g['visitante']}: print(g['rodada'],g['mandante'],g['gm'],'x',g['gv'],g['visitante'])

