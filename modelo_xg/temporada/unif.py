import json,re
MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
m=lambda t:MAP.get(t,t)
f1=lambda x:f"{x:.1f}".replace('.',','); sg=lambda x:('+' if x>0.05 else '−' if x<-0.05 else '')+f1(abs(x))
G=json.load(open('gk2.json')); RAW=json.load(open('gk_raw.json')); A=json.load(open('atk2.json'))
npxg={(m(k[0]),k[1]):k[7] for k in RAW['K']}
KR=RAW['T']['np'][1]/sum(k[7] for k in RAW['K'])   # xGOT/xG dos chutes que chegam ao goleiro
rx=json.load(open('../dash/raiox.json')); by={r['clube']:r for r in rx}
for c,r in by.items():
    ks=[x for x in G['rows'] if x['clube']==c]; ks.sort(key=lambda x:-x['chutes'])
    tot=sum(x['ajust']+x['pen_mer'] for x in ks); est=sum(x['final'] for x in ks)
    # 1) tabela antiga de goleiros e textos: passam a usar o bloco novo
    r['goleiros']=[dict(jogador=x['jogador'],chutes_no_gol=x['chutes'],xgot=x['xgot'],sofridos=x['sofridos'],evitados=x['final']) for x in ks]
    r['goleiro_txt']=r['gk_aj_txt']
    # 2) defesa: goleiros vs média da liga (mesma base da linha)
    r['def_gk']=round(tot,1); r['def_gk_est']=round(est,1)
    s=r['def_txt']; s=s[:s.find('Comparando com a média')].strip()
    tt=r['def_acima']+tot
    s+=f" Comparando com a média da liga, a linha ficou em {sg(r['def_acima'])} e os goleiros em {sg(tot)} (sem pênaltis no xGOT, com pênaltis à parte; {sg(est)} depois de descontar o acaso): no total, {f1(abs(tt))} gols {'a menos' if tt>=0 else 'a mais'} do que um time comum sofreria com as mesmas chances"+(", quase tudo pelo goleiro." if abs(tot)>2*abs(r['def_acima']) and abs(tot)>=2 else ".")
    r['def_txt']=s
    # 3) duelos: atacantes sem pênaltis e goleiros com atribuição corrigida
    atk=[dict(jogador=a[0],gols=a[1],xg=a[2],xgot=a[3],fin=a[4],gk_ef=a[5]) for t,L in A.items() if m(t)==c for a in L]
    gks=[dict(jogador=x['jogador'],chutes=x['chutes'],xg=round(npxg[(c,x['jogador'])],1),xgot=x['xgot'],sofridos=x['sofridos'],fin_adv=round(x['xgot']-KR*npxg[(c,x['jogador'])],1),merito=x['ajust']) for x in ks]
    r['cruz_atk']=atk; r['cruz_gk']=gks
    t=[]
    if atk:
        p=min(atk,key=lambda p:p['gk_ef'])
        if p['gk_ef']<=-1: t.append(f"No ataque, sem contar pênaltis, quem mais sofreu com os goleiros adversários foi {p['jogador']}: os chutes dele no alvo valiam {f1(p['xgot'])} de xGOT e viraram {p['gols']} gols ({sg(p['gk_ef'])} em relação ao que um goleiro médio deixaria passar).")
        q=max(atk,key=lambda p:p['gk_ef'])
        if q['gk_ef']>=1: t.append(f"{q['jogador']} foi o mais beneficiado: {q['gols']} gols para {f1(q['xgot'])} de xGOT ({sg(q['gk_ef'])}).")
        w=min(atk,key=lambda p:p['fin'])
        if w['fin']<=-1: t.append(f"Na colocação do chute, {w['jogador']} foi quem mais desperdiçou: chances de {f1(w['xg'])} de xG viraram chutes de só {f1(w['xgot'])} de xGOT ({sg(w['fin'])}).")
    if gks:
        g=gks[0]
        t.append(f"No gol, {g['jogador']} encarou {g['chutes']} chutes no alvo (sem pênaltis), que valiam {f1(g['xgot'])} de xGOT. "+(f"Os adversários finalizaram {'melhor' if g['fin_adv']>0 else 'pior'} que a média contra ele ({sg(g['fin_adv'])} de xGOT), {'o que dificultou' if g['fin_adv']>0 else 'o que facilitou'} o trabalho. " if abs(g['fin_adv'])>=1.5 else "A qualidade dos chutes que recebeu ficou na média. ")+f"Comparado a um goleiro médio, ficou em {sg(g['merito'])}.")
    r['cruz_txt']=' '.join(t)
    # 4) diagnóstico: separa goleiro e linha quando o texto atribui a "goleiro e defesa"
    d=r['diagnostico']; d=re.sub(r' Pelo bloco de goleiros.*?\.(?= |$)','',d)
    if 'goleiro' in d:
        d=d.replace('sinal de goleiro e defesa decisivos.','sinal de goleiro e defesa decisivos.',1)
        extra=f" Pelo bloco de goleiros, a parte do gol é {sg(tot)} gols em relação a um goleiro médio ({sg(est)} descontando o acaso) e a da defesa de linha, {sg(r['def_acima'])}; o resto vem de finalização ruim dos adversários ou de acaso."
        i=d.find('decisivos.'); j=d.find('individuais.')
        k=(i+len('decisivos.')) if i>=0 else ((j+len('individuais.')) if j>=0 else -1)
        if k>0: d=d[:k]+extra+d[k:]
    r['diagnostico']=d
json.dump(rx,open('../dash/raiox.json','w'),ensure_ascii=False)
for c in ['Grêmio','Vasco','Internacional']:
    print(c,'\n',by[c]['diagnostico'][:700],'\n',by[c]['def_txt'][-300:],'\n',by[c]['cruz_txt'],'\n')
