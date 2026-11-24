import json, math, itertools
import numpy as np
NOME={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
G=[]
for l in open('jogos.txt'):
    r=l.rstrip('\n').split('|'); x,y=map(int,r[4].split('-')); xh,xa=map(float,r[5].split('/'))
    bh,ba=(r[6].split('/')+['',''])[:2]
    G.append(dict(t=r[1],r=int(r[0]),h=NOME.get(r[2],r[2]),a=NOME.get(r[3],r[3]),gh=x,ga=y,xh=xh,xa=xa,bh=float(bh or 0),ba=float(ba or 0)))
G.sort(key=lambda g:g['t'])
cl=sorted(set(g['h'] for g in G)); ix={c:i for i,c in enumerate(cl)}; N=len(G)
res=np.array([0 if g['gh']>g['ga'] else 1 if g['gh']==g['ga'] else 2 for g in G])
# grade de placares para probabilidades
K_=11; fact=np.array([math.factorial(k) for k in range(K_)],float)
def prob3(lh,la,rho):
    k=np.arange(K_)
    ph=np.exp(-lh)[:,None]*lh[:,None]**k/fact; pa=np.exp(-la)[:,None]*la[:,None]**k/fact
    M=ph[:,:,None]*pa[:,None,:]
    d=np.einsum('nii->n',M)*(1+rho); w=np.triu(M,1).sum((1,2)); l=np.tril(M,-1).sum((1,2))  # i=home goals rows
    # triu: j>i => away wins ; tril: i>j => home wins
    hw=np.tril(M,-1).sum((1,2)); aw=np.triu(M,1).sum((1,2)); t=hw+d+aw
    return np.stack([hw/t,d/t,aw/t],1)
def lambdas(K,wv,a,gw,hl):
    dec=1.0 if hl is None else 0.5**(1/hl)
    # somas por clube: [venue][stat] ; stats: ataque e defesa (valor misto), peso
    S=np.zeros((len(cl),2,3))   # venue 0 casa 1 fora ; [atq, def, n]
    T=np.zeros((len(cl),3))     # geral
    LH=np.zeros(N); LA=np.zeros(N); ok=np.zeros(N,bool)
    sh=sa=0.0; n_=0; sbh=sba=0.0
    for k,g in enumerate(G):
        h,aw=ix[g['h']],ix[g['a']]
        if n_>=20 and S[h,0,2]>=1 and S[aw,1,2]>=1:
            mh=sh/n_; ma=sa/n_
            def r(i,v,j,m_other,m_own):
                # força de ataque (j=0) ou defesa (j=1) do clube i no mando v, relativa à média
                base = m_own if j==0 else m_other
                vs=(S[i,v,j]+K*base)/(S[i,v,2]+K); gs=(T[i,j]+K*(mh+ma)/2)/(T[i,2]+K)
                return wv*vs/base + (1-wv)*gs/((mh+ma)/2)
            LH[k]=mh*r(h,0,0,ma,mh)*r(aw,1,1,mh,ma)
            LA[k]=ma*r(aw,1,0,mh,ma)*r(h,0,1,ma,mh)
            ok[k]=True
        # atualiza com o jogo
        # métrica de chance: a*xG + (1-a)*bigchance*escala ; mistura com gols (gw)
        esc = (sh/max(sbh,1e-9)) if n_ else 0.35
        vh=a*g['xh']+(1-a)*g['bh']*esc; va=a*g['xa']+(1-a)*g['ba']*esc
        vh=(1-gw)*vh+gw*g['gh']; va=(1-gw)*va+gw*g['ga']
        for i,v,f,c in ((h,0,vh,va),(aw,1,va,vh)):
            S[i,v,:]*=dec; T[i,:]*=dec
            S[i,v,0]+=f; S[i,v,1]+=c; S[i,v,2]+=1; T[i,0]+=f; T[i,1]+=c; T[i,2]+=1
        sh+=vh; sa+=va; n_+=1; sbh+=g['bh']; sba+=g['ba']
    return LH,LA,ok
def metr(P,m):
    r=res[m]; p=P[m]
    ll=-np.log(np.clip(p[np.arange(len(r)),r],1e-6,1)).mean()
    oh=np.eye(3)[r]; br=((p-oh)**2).sum(1).mean()
    acc=(p.argmax(1)==r).mean()
    return ll,br,acc,p[:,1].mean()
ronda=np.array([g['r'] for g in G]); tt=np.array([g['t'] for g in G])
metade=tt< '2026-07-01'   # 1º turno (até a pausa) para ajustar, resto para testar
rows=[]
for K,wv,a,gw,hl in itertools.product([2,5,10,20],[0.0,0.5,1.0],[0.5,0.7,1.0],[0.0,0.2,0.4],[None,8,16]):
    LH,LA,ok=lambdas(K,wv,a,gw,hl)
    for rho in [0.0,0.04,0.08,0.12,0.16]:
        P=prob3(np.where(ok,LH,1),np.where(ok,LA,1),rho)
        a1=metr(P,ok&metade); a2=metr(P,ok&~metade); a3=metr(P,ok)
        rows.append(dict(K=K,wv=wv,a=a,gw=gw,hl=hl,rho=rho,ll1=a1[0],br1=a1[1],ll2=a2[0],br2=a2[1],acc2=a2[2],ll=a3[0],br=a3[1],acc=a3[2],pe=a3[3],n=int(ok.sum()),n2=int((ok&~metade).sum())))
json.dump(rows,open('wf_grid.json','w'))
import pandas as pd
df=pd.DataFrame(rows)
atual=df[(df.K==5)&(df.wv==1.0)&(df.a==0.7)&(df.gw==0)&(df.hl.isna())&(df.rho==0.08)]
print('ATUAL\n',atual.to_string())
best1=df.sort_values('ll1').head(5); print('MELHOR NO 1º TURNO\n',best1.to_string())
print('MELHOR GERAL\n',df.sort_values('ll').head(5).to_string())
