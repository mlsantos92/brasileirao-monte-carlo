import json
G=json.load(open('gk2.json')); MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
m=lambda t:MAP.get(t,t)
f1=lambda x:f"{x:.1f}".replace('.',','); sg=lambda x:('+' if x>0.05 else '−' if x<-0.05 else '')+f1(abs(x))
rx=json.load(open('../dash/raiox.json')); by={r['clube']:r for r in rx}
rank={(r['clube'],r['jogador']):i+1 for i,r in enumerate([x for x in G['rows'] if x['chutes']>=40])}
nq=len(rank)
for c,r in by.items():
    ks=[x for x in G['rows'] if x['clube']==c]; ks.sort(key=lambda x:-x['chutes'])
    pd=[dict(r=p[0],batedor=p[2],time=m(p[1]),goleiro=p[4],res=p[5]) for p in G['pens'] if m(p[3])==c]
    pa=[dict(r=p[0],batedor=p[2],goleiro=p[4],time_gk=m(p[3]),res=p[5]) for p in G['pens'] if m(p[1])==c]
    s=[]
    k=ks[0] if ks else None
    if k:
        s.append(f"{k['jogador']} sofreu {k['sofridos']} gols em {k['chutes']} chutes no alvo sem contar pênaltis, que valiam {f1(k['xgot'])} de xGOT: {sg(k['bruto'])} pelo número bruto.")
        s.append(f"Como na liga os goleiros sofrem em média 7% menos gols que o xGOT, o mérito ajustado é {sg(k['ajust'])}, com margem de ±{f1(k['faixa'])} (90%)"+(", ou seja, acima do que o acaso explicaria." if k['sig'] and k['ajust']>0 else ", ou seja, abaixo do que o acaso explicaria." if k['sig'] else ", dentro do que o acaso pode explicar.")+f" Descontando o ruído (só {int(k['peso']*100)}% do desvio é tratado como habilidade com essa amostra), o mérito estimado fica em {sg(k['encolhido'])}.")
        if k['pen_n']:
            s.append(f"Nos pênaltis, enfrentou {k['pen_n']}: {k['pen_def']} defendido{'s' if k['pen_def']!=1 else ''}, {k['pen_fora']} para fora ou na trave e {k['pen_g']} gol{'s' if k['pen_g']!=1 else ''} ({sg(k["pen_mer"])} no critério do pênalti: +0,79 por defesa, +0,08 por cobrança para fora ou na trave, −0,21 por gol).")
        if (c,k['jogador']) in rank: s.append(f"No ranking final dos {nq} goleiros com 40 chutes ou mais, ficou em {rank[(c,k['jogador'])]}º.")
    r.update(gk_aj=[dict(jogador=x['jogador'],jogos=x['jogos'],chutes=x['chutes'],xgot=x['xgot'],sofridos=x['sofridos'],bruto=x['bruto'],ajust=x['ajust'],faixa=x['faixa'],encolhido=x['encolhido'],pen=f"{x['pen_def']}/{x['pen_n']}" if x['pen_n'] else '—',pen_mer=x['pen_mer'],final=x['final']) for x in ks],
             gk_aj_txt=' '.join(s), pen_contra=pd, pen_favor=pa)
json.dump(rx,open('../dash/raiox.json','w'),ensure_ascii=False)
print(by['Grêmio']['gk_aj_txt']); print(by['Internacional']['gk_aj_txt']); print(by['Internacional']['pen_favor'],by['Mirassol']['pen_favor'])
