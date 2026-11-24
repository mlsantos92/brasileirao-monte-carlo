import json,re
A=json.load(open('atk_raw.json')); X=json.load(open('xa_raw.json'))
MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
rx=json.load(open('../dash/raiox.json')); by={r['clube']:r for r in rx}
L=lambda v: json.loads(v) if isinstance(v,str) else (v or [])
for t,pl in A.items():
    r=by[MAP.get(t,t)]
    pen={p['jogador']:p for p in L(r.get('jog_acima'))+L(r.get('jog_abaixo'))}
    conv={p['jogador']:p['conversores'] for p in L(r.get('xa_jog'))}
    rows=[]
    for n,g,xg,a,xa,cc in pl:
        p=pen.get(n)
        rows.append(dict(jogador=n,gols=g,xg=xg,dif_g=round(g-xg,1),assist=a,xa=xa,dif_a=round(a-xa,1),total=round(g+a-xg-xa,1),passes=cc,
                         pen=(f"{p['pen_gols']}/{p['penaltis']}" if p and p.get('penaltis') else ''),conversores=conv.get(n,'')))
    rows.sort(key=lambda p:-p['total'])
    txt=r['jogadores_txt']; i=txt.find(' No gol,')
    fin, gk = (txt[:i], txt[i+1:]) if i>=0 else (txt,'')
    fin=re.sub(r'^Na frente,','Na finalização,',fin)
    xa=r['xa_txt']; xa='Na criação, o'+xa[1:] if xa.startswith('Os passes') else xa
    o=X[t]
    r.update(ataque_jog=rows, ataque_txt=(fin.strip()+' '+xa).strip(), goleiro_txt=gk.strip(), xa_g=o['g'], xa_xg=round(o['xg'],1))
json.dump(rx,open('../dash/raiox.json','w'),ensure_ascii=False)
print(by['Internacional']['ataque_txt']); print(by['Internacional']['goleiro_txt']); print(by['Internacional']['ataque_jog'][:2])
