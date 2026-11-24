import json
C=json.load(open('cruz_raw.json'))
KG=918/978.1; KR=978.1/522.1
MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
m=lambda t:MAP.get(t,t)
f1=lambda x:f"{x:.1f}".replace('.',','); f2=lambda x:f"{float(x):.2f}".replace('.',',')
sg=lambda x:('+' if x>0.05 else '−' if x<-0.05 else '')+f1(abs(x))
rx=json.load(open('../dash/raiox.json')); by={r['clube']:r for r in rx}
def ev(s):
    a,at,gk,gt,xg,xgot,r,fora=s.split('~'); return dict(a=a,at=m(at),gk=gk,gt=m(gt),xg=float(xg),xgot=float(xgot),r=r.replace('R','')+'ª',fora=fora=='1')
def desc(k,e):
    if k=='a_fal': return f"{e['a']} marcou em {e['gk']} ({e['gt']}) com um chute de só {f2(e['xgot'])} de xGOT ({e['r']} rodada)"
    if k=='a_def': return f"{e['a']} parou em {e['gk']} ({e['gt']}): chute de {f2(e['xgot'])} de xGOT defendido ({e['r']})"
    if k=='a_ruim': return (f"{e['a']} mandou para fora uma chance de {f2(e['xg'])} de xG contra o {e['gt']} ({e['r']})" if e['fora'] else f"{e['a']} acertou o alvo, mas fraco: chance de {f2(e['xg'])} de xG virou {f2(e['xgot'])} de xGOT contra o {e['gt']} ({e['r']})")
    if k=='a_ind': return f"{e['a']} fez gol indefensável em {e['gk']} ({e['gt']}): chance de {f2(e['xg'])} virou {f2(e['xgot'])} de xGOT ({e['r']})"
    if k=='g_fal': return f"{e['gk']} levou gol de {e['a']} ({e['at']}) num chute de só {f2(e['xgot'])} de xGOT ({e['r']})"
    if k=='g_def': return f"{e['gk']} defendeu chute de {e['a']} ({e['at']}) de {f2(e['xgot'])} de xGOT ({e['r']})"
    if k=='g_ruim': return (f"{e['a']} ({e['at']}) mandou para fora uma chance de {f2(e['xg'])} de xG ({e['r']})" if e['fora'] else f"{e['a']} ({e['at']}) chutou fraco{(' em '+e['gk']) if e['gk'] else ''}: chance de {f2(e['xg'])} de xG virou {f2(e['xgot'])} de xGOT ({e['r']})")
    if k=='g_ind': return f"{e['gk']} sofreu gol indefensável de {e['a']} ({e['at']}): chance de {f2(e['xg'])} virou {f2(e['xgot'])} de xGOT ({e['r']})"
for t,o in C.items():
    r=by[m(t)]
    atk=[dict(jogador=a[0],gols=a[1],xg=a[2],xgot=a[3],fin=a[4],gk_ef=round(a[1]-KG*a[3],1)) for a in o['a']]
    gks=[dict(jogador=k[0],chutes=k[1],xg=k[2],xgot=k[3],sofridos=k[4],fin_adv=round(k[3]-KR*k[2],1),merito=round(k[3]-k[4],1)) for k in o['k']]
    gks.sort(key=lambda g:-g['chutes'])
    lances={k:[desc(k,ev(s)) for s in v] for k,v in o['e'].items()}
    # texto
    s=[]
    if atk:
        p=min(atk,key=lambda p:p['gk_ef'])
        if p['gk_ef']<=-1: s.append(f"No ataque, quem mais sofreu com os goleiros adversários foi {p['jogador']}: os chutes dele no alvo valiam {f1(p['xgot'])} de xGOT e viraram {p['gols']} gols ({sg(p['gk_ef'])}).")
        q=max(atk,key=lambda p:p['gk_ef'])
        if q['gk_ef']>=1: s.append(f"{q['jogador']} foi o mais beneficiado: {q['gols']} gols para {f1(q['xgot'])} de xGOT ({sg(q['gk_ef'])}), aproveitando defesas que o goleiro deveria ter feito.")
        w=min(atk,key=lambda p:p['fin'])
        if w['fin']<=-1: s.append(f"Na colocação do chute, {w['jogador']} foi quem mais desperdiçou: chances de {f1(w['xg'])} de xG viraram chutes de só {f1(w['xgot'])} de xGOT ({sg(w['fin'])}), o que facilitou a vida dos goleiros.")
    for g in gks[:1]:
        s.append(f"No gol, {g['jogador']} encarou {g['chutes']} chutes no alvo, que valiam {f1(g['xgot'])} de xGOT. "+(f"Os adversários finalizaram {'melhor' if g['fin_adv']>0 else 'pior'} que a média contra ele ({sg(g['fin_adv'])} de xGOT em relação ao que chances como aquelas costumam render), {'o que dificultou' if g['fin_adv']>0 else 'o que facilitou'} o trabalho. " if abs(g['fin_adv'])>=1.5 else "A qualidade dos chutes que recebeu ficou na média. ")+f"Ele sofreu {g['sofridos']}, {f1(abs(g['merito']))} {'a menos' if g['merito']>=0 else 'a mais'} do que o esperado pelo xGOT.")
    r.update(cruz_txt=' '.join(s), cruz_atk=atk, cruz_gk=gks, cruz_lances=lances)
json.dump(rx,open('../dash/raiox.json','w'),ensure_ascii=False)
for c in ['Grêmio','Internacional']: print(by[c]['cruz_txt']); print(json.dumps(by[c]['cruz_lances'],ensure_ascii=False)[:900],'\n')
