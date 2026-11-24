import json
R=json.load(open('xa_raw.json'))
MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
f1=lambda x:f"{x:.1f}".replace('.',',')
sg=lambda x:('+' if x>0.05 else '−' if x<-0.05 else '')+f1(abs(x))
def gl(n): return '1 gol' if n==1 else f'{n} gols'
def ast(n): return 'nenhuma assistência' if n==0 else '1 assistência' if n==1 else f'{n} assistências'
def nomes(pr):
    return ', '.join(f"{p[0]} ({p[1]})" for p in pr)
rx=json.load(open('../dash/raiox.json'))
by={r['clube']:r for r in rx}
for t,o in R.items():
    c=MAP.get(t,t); r=by[c]
    d=o['a']-o['xa']; ig=o['g']-o['pen']-o['a']; ix=o['npxg']-o['xa']; di=ig-ix; px=o['xg']-o['npxg']
    seen=set(); jog=[]
    for x in o['top']+o['bot']:
        if x[0] in seen: continue
        seen.add(x[0]); jog.append(dict(jogador=x[0],assist=x[1],xa=round(x[2],2),dif=round(x[1]-x[2],1),passes=x[3],conversores=nomes(x[5]) or '—'))
    jog.sort(key=lambda p:-p['dif'])
    art='da' if c=='Chapecoense' else 'do'
    s=f"Os passes {art} {c} valiam {f1(o['xa'])} assistências pelo xA e viraram {o['a']} ({sg(d)}). "
    if d<=-3: s+="Quem recebe desperdiça boa parte das chances criadas. "
    elif d>=3: s+="Quem recebe converte acima do esperado: as chances criadas renderam mais gols do que valiam. "
    else: s+="As chances criadas viraram gols no ritmo esperado. "
    neg=[p for p in jog if p['dif']<=-1.5]; pos=[p for p in jog if p['dif']>=1.5]
    if neg:
        p=min(neg,key=lambda p:p['dif'])
        s+=f"Quem mais perdeu foi {p['jogador']} ({ast(p['assist'])} para {f1(p['xa'])} de xA em {p['passes']} passes para finalização)"
        s+=(f"; os gols que saíram dos passes dele foram de {p['conversores']}. " if p['conversores']!='—' else ", sem nenhum gol dos companheiros. ")
    if pos:
        p=max(pos,key=lambda p:p['dif'])
        s+=f"{p['jogador']} teve mais assistências que o esperado ({p['assist']} para {f1(p['xa'])} de xA)"
        s+=(f", com gols de {p['conversores']}. " if p['conversores']!='—' else ". ")
    s+=f"Nos lances sem assistência (jogadas individuais, rebotes e bola parada sem passe, sem pênaltis), foram {gl(ig)} para cerca de {f1(ix)} de xG ({sg(di)}). "
    if abs(d)>=2 or abs(di)>=2:
        s+=("A diferença do ataque vem mais das jogadas assistidas." if abs(d)>abs(di) else "A diferença do ataque vem mais dos lances sem assistência.")
    r.update(xa_txt=s.strip(), xa_jog=jog, xa_a=o['a'], xa_xa=round(o['xa'],1), xa_ind_g=ig, xa_ind_x=round(ix,1), xa_pen=o['pen'], xa_pen_x=round(px,1), xa_cc=o['cc'])
json.dump(rx,open('../dash/raiox.json','w'),ensure_ascii=False)
for c in ['Internacional','Mirassol','Corinthians','Grêmio','Athletico-PR']: print(c,'|',by[c]['xa_txt'],'\n')
