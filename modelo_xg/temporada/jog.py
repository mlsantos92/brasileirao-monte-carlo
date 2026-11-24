import json
TM=["Atlético-MG","Palmeiras","Coritiba","Bragantino","Internacional","Athletico-PR","Remo","Vitória","Grêmio","Fluminense","Chapecoense","Santos","Corinthians","Bahia","Flamengo","São Paulo","Mirassol","Vasco","Cruzeiro","Botafogo"]
POS={'G':'Goleiro','D':'Defensor','M':'Meio-campista','A':'Atacante'}
rows=[]
for ln in open('jog_p1.txt').read().splitlines()+open('jog_p2.txt').read().splitlines():
    if not ln.strip(): continue
    a=ln.split('|')
    t,n,p,j,mn,g,xg,npxg,ast,xa,cc,pen,sh,col,gef,b,bx,ol,olx,lm,cl,it,tk,er=a
    j,mn,g,ast,cc,sh,b,ol,lm,cl,it,tk,er=map(int,(j,mn,g,ast,cc,sh,b,ol,lm,cl,it,tk,er))
    xg,npxg,xa,col,gef,bx,olx=map(float,(xg,npxg,xa,col,gef,bx,olx))
    pc,pb=map(int,pen.split('/'))
    rows.append(dict(clube=TM[int(t)],jogador=n,pos=POS[p],jogos=j,minutos=mn,gols=g,xg=round(xg,2),gols_xg=round(g-xg,2),npxg=round(npxg,2),
      assist=ast,xa=round(xa,2),assist_xa=round(ast-xa,2),ga_total=round(g+ast-xg-xa,2),passes_final=cc,pen_conv=pc,pen_bat=pb,pen_saldo=round(pc-0.788*pb,2),
      chutes=sh,colocacao=col,efeito_gol=gef,bloqueios=b,xg_impedido=round(bx+olx,2),linha=ol,ultimo=lm,cortes=cl,interc=it,desarmes=tk,erros=er))
G=json.load(open('gk2.json'))
for k in G['rows']:
    mins=None
    rows.append(dict(clube=k['clube'],jogador=k['jogador'],pos='Goleiro',jogos=k['jogos'],minutos=k['jogos']*90,gk_chutes=k['chutes'],gk_xgot=k['xgot'],gk_sofridos=k['sofridos'],
      gk_bruto=k['bruto'],gk_ajust=k['ajust'],gk_margem=k['faixa'],gk_estimado=k['encolhido'],gk_pen=f"{k['pen_def']}/{k['pen_n']}" if k['pen_n'] else '—',gk_pen_def=k['pen_def'],gk_pen_mer=k['pen_mer'],gk_total=k['final']))
json.dump(rows,open('../dash/jogadores.json','w'),ensure_ascii=False)
print(len(rows))
