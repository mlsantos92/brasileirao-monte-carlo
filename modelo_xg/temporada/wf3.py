exec(open('wf.py').read().split("rows=[]")[0])
import pandas as pd
df=pd.concat([pd.DataFrame(json.load(open('wf_grid.json')))])
CFG={'atual':dict(K=5,wv=1.0,a=0.7,gw=0.0,hl=None,rho=0.08),'recomendado':dict(K=2,wv=0.5,a=0.6,gw=0.2,hl=8,rho=0.08)}
P={};OK={}
for k,c in CFG.items():
    LH,LA,ok=lambdas(c['K'],c['wv'],c['a'],c['gw'],c['hl']); P[k]=prob3(np.where(ok,LH,1),np.where(ok,LA,1),c['rho']); OK[k]=ok
ok=OK['atual']&OK['recomendado']
fr=np.bincount(res[ok&metade],minlength=3)/(ok&metade).sum()
P['frequencia']=np.tile(fr,(N,1)); P['uniforme']=np.full((N,3),1/3)
tab=[]
for nome,msk in (('1º turno (ajuste)',ok&metade),('2º turno (teste)',ok&~metade),('Temporada',ok)):
    for k in ('atual','recomendado','frequencia','uniforme'):
        ll,br,acc,pe=metr(P[k],msk); tab.append(dict(periodo=nome,modelo=k,n=int(msk.sum()),logloss=round(ll,4),brier=round(br,4),acerto=round(acc*100,1),empate_prev=round(pe*100,1),empate_real=round((res[msk]==1).mean()*100,1)))
m=ok&~metade; r=res[m]
d=-np.log(P['atual'][m][np.arange(m.sum()),r])+np.log(P['recomendado'][m][np.arange(m.sum()),r])
print(pd.DataFrame(tab).to_string()); print('dif 2º turno',d.mean().round(4),'EP',(d.std()/np.sqrt(len(d))).round(4))
# sensibilidade: melhor ll do 2º turno e do 1º turno por valor de cada parâmetro (grade ampla)
sens=[]
nomes={'K':'Encolhimento à média (jogos fictícios)','wv':'Peso do perfil por mando (vs. geral)','a':'Peso do xG na métrica de chances (resto: grandes chances)','gw':'Peso dos gols reais','hl':'Meia-vida da forma (jogos)','rho':'Reforço de empates'}
for p in ['K','wv','a','gw','hl','rho']:
    for v,gp in df.groupby(df[p].fillna(-1)):
        sens.append(dict(parametro=nomes[p],chave=p,valor=('sem decaimento' if v==-1 else v),ll_ajuste=round(gp.ll1.min(),4),ll_teste=round(gp.sort_values('ll1').iloc[0].ll2,4)))
print(pd.DataFrame(sens).to_string())
# calibração do recomendado na temporada
cal=[]
pr=P['recomendado'][ok]; rr=res[ok]
for lo,hi in [(0,.2),(.2,.35),(.35,.5),(.5,.65),(.65,1.01)]:
    ps=[];hs=[]
    for i in range(3):
        mk=(pr[:,i]>=lo)&(pr[:,i]<hi); ps+=list(pr[mk,i]); hs+=list(rr[mk]==i)
    cal.append(dict(faixa=f"{int(lo*100)}–{min(int(hi*100),100)}%",previsto=round(np.mean(ps)*100,1),real=round(np.mean(hs)*100,1),n=len(ps)))
print(cal)
# evolução por rodada (log loss médio acumulado)
evo=[]
idx=np.where(ok)[0]
for k in ('atual','recomendado','frequencia'):
    pass
json.dump(dict(tab=tab,sens=sens,cal=cal,cfg=CFG,dif=float(d.mean()),ep=float(d.std()/np.sqrt(len(d)))),open('wf_out.json','w'),ensure_ascii=False,default=str)
