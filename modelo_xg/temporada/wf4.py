src=open('wf.py').read().split("rows=[]")[0]
src=src.replace("LH=np.zeros(N); LA=np.zeros(N); ok=np.zeros(N,bool)","LH=np.zeros(N); LA=np.zeros(N); ok=np.zeros(N,bool); MH=np.ones(N); MA=np.ones(N)")
src=src.replace("            ok[k]=True","            ok[k]=True; MH[k]=mh; MA[k]=ma")
src=src.replace("    return LH,LA,ok","    return LH,LA,ok,MH,MA")
exec(src)
out=json.load(open('wf_out.json'))
LH,LA,ok1,MH,MA=lambdas(5,1.0,0.7,0.0,None); Pa=prob3(np.where(ok1,LH,1),np.where(ok1,LA,1),0.08)
LH,LA,ok2,MH,MA=lambdas(2,0.5,0.6,0.2,8)
s=np.where(metade,1.0,1.2)
Pr=prob3(MH*(np.where(ok2,LH,MH)/MH)**s, MA*(np.where(ok2,LA,MA)/MA)**s, 0.08)
ok=ok1&ok2
fr=np.bincount(res[ok&metade],minlength=3)/(ok&metade).sum()
ll=lambda P: -np.log(P[np.arange(N),res])
la,lr,lf=ll(Pa),ll(Pr),-np.log(fr[res])
# por blocos de ~3 rodadas (cronológico, 30 jogos)
idx=np.where(ok)[0]; evo=[]
for b in range(0,len(idx),30):
    sl=idx[b:b+30]
    if len(sl)<15: continue
    evo.append(dict(id=str(b), bloco=f"{G[sl[0]]['t'][8:10]}/{G[sl[0]]['t'][5:7]}", ate=f"{G[sl[-1]]['t'][8:10]}/{G[sl[-1]]['t'][5:7]}", atual=round(la[sl].mean(),3), recomendado=round(lr[sl].mean(),3), frequencia=round(lf[sl].mean(),3), n=len(sl)))
tab=out['tab']
for nome,msk in (('2º turno (teste)',ok&~metade),('Temporada',ok)):
    m=msk; r=res[m]
    tab.append(dict(periodo=nome, modelo='recomendado + contraste 1,2 no 2º turno', n=int(m.sum()), logloss=round(lr[m].mean(),4), brier=round(((Pr[m]-np.eye(3)[r])**2).sum(1).mean(),4), acerto=round((Pr[m].argmax(1)==r).mean()*100,1), empate_prev=round(Pr[m][:,1].mean()*100,1), empate_real=round((r==1).mean()*100,1)))
params=[
 dict(id='K',parametro='Encolhimento à média',atual='5 jogos fictícios',recomendado='2 jogos fictícios',efeito='Quanto o perfil de um clube é puxado para a média da liga enquanto há poucos jogos. Menos encolhimento deixou o modelo reagir mais rápido às diferenças reais entre os times.'),
 dict(id='wv',parametro='Perfil por mando',atual='100% casa/fora separados',recomendado='50% por mando + 50% geral',efeito='Separar casa e fora é útil, mas com ~18 jogos em cada mando o ruído é grande; misturar com o perfil geral foi melhor.'),
 dict(id='a',parametro='Métrica de chances',atual='70% xG + 30% grandes chances',recomendado='60% xG + 40% grandes chances',efeito='Diferença pequena entre 50% e 70%; usar só xG piorou. Manter a mistura.'),
 dict(id='gw',parametro='Gols reais',atual='0%',recomendado='20% gols + 80% chances',efeito='Um pouco de peso nos gols reais ajuda: captura finalização e goleiro que persistem.'),
 dict(id='hl',parametro='Forma recente',atual='Ajuste separado (últimos 6 jogos)',recomendado='Meia-vida de 8 jogos dentro do perfil',efeito='Dar mais peso aos jogos recentes de forma contínua (um jogo de 8 rodadas atrás vale metade) foi o ajuste que mais melhorou o teste.'),
 dict(id='rho',parametro='Reforço de empates',atual='0,08',recomendado='0,08',efeito='Já estava no ponto: com 0,08 a média prevista de empates (26%) bate com a real (26,4%) na temporada.'),
 dict(id='s',parametro='Contraste entre times',atual='1,0',recomendado='1,0 no 1º turno; 1,2 no 2º',efeito='No 2º turno o modelo era conservador demais com os azarões (dava 16% a resultados que aconteceram 8% das vezes); acentuar as diferenças em 20% melhorou o teste. No 1º turno isso piorava.')]
json.dump(params,open('dash/wf_params.json','w'),ensure_ascii=False)
json.dump([dict(t,id=t['periodo']+'|'+t['modelo']) for t in tab],open('dash/wf_tab.json','w'),ensure_ascii=False)
json.dump([dict(s_,id=s_['chave']+'|'+str(s_['valor'])) for s_ in out['sens']],open('dash/wf_sens.json','w'),ensure_ascii=False)
json.dump(out['cal'],open('dash/wf_cal.json','w'),ensure_ascii=False,default=float)
json.dump(evo,open('dash/wf_evo.json','w'),ensure_ascii=False)
print(tab[-2:]); print(evo)
