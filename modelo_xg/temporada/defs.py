import json
D=json.load(open('def_raw.json'))
MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
f1=lambda x:f"{x:.1f}".replace('.',','); f2=lambda x:f"{x:.2f}".replace('.',',')
sg=lambda x:('+' if x>0.05 else '−' if x<-0.05 else '')+f1(abs(x))
rx=json.load(open('../dash/raiox.json')); by={r['clube']:r for r in rx}
L=lambda v: json.loads(v) if isinstance(v,str) else (v or [])
tot_x=sum(v[0] for v in D['T'].values()); tot_b=sum(v[1]+v[6] for v in D['T'].values()); share=tot_b/tot_x
print('share',share)
for t,v in D['T'].items():
    c=MAP.get(t,t); r=by[c]
    xga,bxg,bn,_,_,oln,olxg,sem=v; imp=bxg+olxg; esp=share*xga; ac=imp-esp
    gks=L(r.get('goleiros')); gkev=sum(g.get('evitados',0) for g in gks)
    pls=[]
    for p in D['P'].get(t,[]):
        n,mn,b,bx,ol,olx,lm,cl,it,tk,er,solo=p
        pls.append(dict(jogador=n,min=mn,bloqueios=b,xg_bloq=round(bx,2),linha=ol,xg_linha=round(olx,2),imp=round(bx+olx,2),p90=round((bx+olx)/mn*90,3) if mn else 0,ultimo=lm,cortes=cl,interc=it,desarmes=tk,erros=er))
    pls.sort(key=lambda p:-p['imp'])
    top=[p for p in pls if p['imp']>=0.5][:2]
    art='da' if c=='Chapecoense' else 'do'
    s=f"A defesa de linha {art} {c} tirou {f1(imp)} de xG antes de chegar ao goleiro: {bn} chutes bloqueados ({f1(bxg)})"
    s+=(f" e {oln} bola{'s' if oln>1 else ''} tirada{'s' if oln>1 else ''} em cima da linha ({f1(olxg)})." if oln else ".")
    s+=f" Pelo volume de chances que cedeu ({f1(xga)} de xG), a média da liga seria {f1(esp)}, ou seja, {f1(abs(ac))} {'acima' if ac>=0 else 'abaixo'} do esperado. " if abs(ac)>=0.05 else " Isso está na média da liga para o volume de chances cedidas. "
    if top:
        s+="Quem mais contribuiu: "+"; ".join(f"{p['jogador']} ({p['bloqueios']} bloqueios, {f1(p['imp'])} de xG impedido"+(f", {p['linha']} em cima da linha" if p['linha'] else "")+")" for p in top)+". "
    ers=[p for p in pls if p['erros']>=2]
    if ers: s+="Do outro lado, "+", ".join(f"{p['jogador']} ({p['erros']} erros que viraram gol)" for p in ers)+". "
    tt=ac+gkev
    s+=f"Comparando com a média da liga, a linha ficou em {sg(ac)} e os goleiros em {sg(gkev)} gols evitados pelo xGOT: no total, {f1(abs(tt))} gols {'a menos' if tt>=0 else 'a mais'} do que um time comum sofreria com as mesmas chances"+(", quase tudo pelo goleiro." if abs(gkev)>2*abs(ac) and abs(gkev)>=2 else ".")
    r.update(def_txt=s, def_jog=pls, def_xga=round(xga,1), def_bloq=bn, def_bxg=round(bxg,1), def_linha=oln, def_lxg=round(olxg,1), def_esp=round(esp,1), def_acima=round(ac,1), def_gk=round(gkev,1))
json.dump(rx,open('../dash/raiox.json','w'),ensure_ascii=False)
for c in ['Grêmio','Mirassol','Internacional','Corinthians']: print(by[c]['def_txt'],'\n')
for t,v in sorted(D['T'].items(),key=lambda kv:-(kv[1][1]+kv[1][6]-share*kv[1][0])): print(t, round(v[1]+v[6]-share*v[0],1))
