exec(open('wf.py').read().split("rows=[]")[0])
import pandas as pd
rows=[]; cache={}
for K,wv,a,gw,hl in itertools.product([1,2,3],[0.25,0.5,0.75],[0.4,0.5,0.6,0.7],[0.1,0.2,0.3],[4,6,8,10,12]):
    LH,LA,ok=lambdas(K,wv,a,gw,hl)
    for rho in [0.04,0.08,0.12]:
        P=prob3(np.where(ok,LH,1),np.where(ok,LA,1),rho)
        a1=metr(P,ok&metade); a2=metr(P,ok&~metade); a3=metr(P,ok)
        rows.append(dict(K=K,wv=wv,a=a,gw=gw,hl=hl,rho=rho,ll1=a1[0],ll2=a2[0],br2=a2[1],acc2=a2[2],ll=a3[0],br=a3[1],acc=a3[2],pe=a3[3]))
df=pd.DataFrame(rows); b=df.sort_values('ll1').iloc[0]; print(df.sort_values('ll1').head(6).to_string())
# comparação pareada no 2º turno (fora da amostra de ajuste)
def P_of(K,wv,a,gw,hl,rho):
    LH,LA,ok=lambdas(K,wv,a,gw,hl); return prob3(np.where(ok,LH,1),np.where(ok,LA,1),rho),ok
Pa,oka=P_of(5,1.0,0.7,0.0,None,0.08); Pb,okb=P_of(int(b.K),b.wv,b.a,b.gw,int(b.hl),b.rho)
m=oka&okb&~metade; r=res[m]
la=-np.log(Pa[m][np.arange(m.sum()),r]); lb=-np.log(Pb[m][np.arange(m.sum()),r])
d=la-lb; print('2º turno n=',m.sum(),'ll atual',la.mean().round(4),'ll novo',lb.mean().round(4),'dif',d.mean().round(4),'EP',(d.std()/np.sqrt(len(d))).round(4))
fr=np.bincount(res[ok_:=oka&metade],minlength=3)/ok_.sum(); lf=-np.log(fr[r]).mean(); print('ll frequência (do 1º turno)',round(lf,4),'uniforme',round(math.log(3),4))
json.dump(dict(best=b.to_dict()),open('wf_best.json','w'))
