import json, math
from collections import defaultdict
NOME={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
nm=lambda s: NOME.get(s,s)
G=[]
for l in open('jogos.txt'):
    r=l.rstrip('\n').split('|')
    x,y=map(int,r[4].split('-')); xh,xa=map(float,r[5].split('/'))
    G.append(dict(r=int(r[0]),t=r[1],h=nm(r[2]),a=nm(r[3]),gh=x,ga=y,xh=xh,xa=xa,reds=r[9]))
G.sort(key=lambda g:g['t'])
RHO=0.08
def probs(lh,la,rho=RHO):
    ph=[math.exp(-lh)*lh**k/math.factorial(k) for k in range(11)]; pa=[math.exp(-la)*la**k/math.factorial(k) for k in range(11)]
    w=d=l=0.0; tot=0
    for i in range(11):
        for j in range(11):
            p=ph[i]*pa[j]*((1+rho) if i==j else 1); tot+=p
            if i>j: w+=p
            elif i==j: d+=p
            else: l+=p
    return w/tot,d/tot,l/tot
clubes=sorted(set(g['h'] for g in G)|set(g['a'] for g in G))
# ratings in-sample por mando (xG), média da liga
mh=sum(g['xh'] for g in G)/len(G); ma=sum(g['xa'] for g in G)/len(G)
S=defaultdict(lambda: defaultdict(float))
for g in G:
    S[g['h']]['xf_c']+=g['xh']; S[g['h']]['xa_c']+=g['xa']; S[g['h']]['n_c']+=1
    S[g['a']]['xf_f']+=g['xa']; S[g['a']]['xa_f']+=g['xh']; S[g['a']]['n_f']+=1
K=4  # encolhimento leve
att_c={c:(S[c]['xf_c']+K*mh)/(S[c]['n_c']+K)/mh for c in clubes}; def_c={c:(S[c]['xa_c']+K*ma)/(S[c]['n_c']+K)/ma for c in clubes}
att_f={c:(S[c]['xf_f']+K*ma)/(S[c]['n_f']+K)/ma for c in clubes}; def_f={c:(S[c]['xa_f']+K*mh)/(S[c]['n_f']+K)/mh for c in clubes}
C=defaultdict(lambda: defaultdict(float)); jogos_cl=defaultdict(list)
bt=dict(n=0,hit=0,brier=0,ll=0,brier_u=0,ll_u=0,res=[0,0,0])
for g in G:
    pw,pd,pl=probs(g['xh'],g['xa'])               # xPts: chances reais do jogo
    mw,md,ml=probs(mh*att_c[g['h']]*def_f[g['a']], ma*att_f[g['a']]*def_c[g['h']])   # modelo pré-jogo (perfil da temporada)
    res=0 if g['gh']>g['ga'] else (1 if g['gh']==g['ga'] else 2)
    pm=[mw,md,ml]; bt['n']+=1; bt['hit']+= (pm.index(max(pm))==res); bt['brier']+=sum((pm[i]-(i==res))**2 for i in range(3)); bt['ll']+=-math.log(pm[res]); bt['res'][res]+=1
    for c,ishome in ((g['h'],1),(g['a'],0)):
        gf,ga_=(g['gh'],g['ga']) if ishome else (g['ga'],g['gh']); xf,xa=(g['xh'],g['xa']) if ishome else (g['xa'],g['xh'])
        pts=3 if gf>ga_ else (1 if gf==ga_ else 0)
        xp=(3*pw+pd) if ishome else (3*pl+pd); mp=(3*mw+md) if ishome else (3*ml+md)
        jogos_cl[c].append(dict(t=g['t'],casa=ishome,pts=pts,xp=xp,mp=mp,gf=gf,ga=ga_,xf=xf,xa=xa))
n=bt['n']; f=[x/n for x in bt['res']]
bt_out=dict(n=n, acerto=round(bt['hit']/n*100,1), brier=round(bt['brier']/n,3), logloss=round(bt['ll']/n,3),
   brier_unif=round(2/3,3), brier_freq=round(sum(f[i]*(1-f[i])**2+sum(f[j]**2 for j in range(3) if j!=i)*f[i] for i in range(3)),3),
   acerto_mandante=round(f[0]*100,1), freq=[round(x*100,1) for x in f])
# classificação real
tab=[]
for c in clubes:
    J=jogos_cl[c]; nj=len(J)
    s=lambda k,sub=J: sum(x[k] for x in sub)
    casa=[x for x in J if x['casa']]; fora=[x for x in J if not x['casa']]
    t1=J[:19]; t2=J[19:]; u10=J[-10:]
    tab.append(dict(clube=c, j=nj, pts=s('pts'), v=sum(x['pts']==3 for x in J), gp=s('gf'), gc=s('ga'),
        xpts=round(s('xp'),1), mpts=round(s('mp'),1), xg=round(s('xf'),1), xga=round(s('xa'),1),
        ppg_casa=round(s('pts',casa)/len(casa),2), ppg_fora=round(s('pts',fora)/len(fora),2),
        xgd_casa=round((s('xf',casa)-s('xa',casa))/len(casa),2), xgd_fora=round((s('xf',fora)-s('xa',fora))/len(fora),2),
        ppg_t1=round(s('pts',t1)/len(t1),2), ppg_t2=round(s('pts',t2)/len(t2),2), xppg_t1=round(s('xp',t1)/len(t1),2), xppg_t2=round(s('xp',t2)/len(t2),2),
        xgd_t1=round((s('xf',t1)-s('xa',t1))/len(t1),2), xgd_t2=round((s('xf',t2)-s('xa',t2))/len(t2),2),
        ppg_u10=round(s('pts',u10)/10,2), xppg_u10=round(s('xp',u10)/10,2), xgd_u10=round((s('xf',u10)-s('xa',u10))/10,2)))
tab.sort(key=lambda r:(-r['pts'],-r['v'],-(r['gp']-r['gc']),-r['gp']))
for i,r in enumerate(tab): r['pos']=i+1
for i,r in enumerate(sorted(tab,key=lambda r:-r['xpts'])): r['pos_xpts']=i+1
json.dump(dict(tab=tab,bt=bt_out,jogos=jogos_cl),open('analise.json','w'),ensure_ascii=False)
print(bt_out)
for r in tab: print(r['pos'],r['clube'],r['pts'],r['xpts'],r['mpts'],r['pos_xpts'],r['gp'],r['xg'],r['gc'],r['xga'],'| t1',r['ppg_t1'],'t2',r['ppg_t2'],'u10',r['ppg_u10'],r['xppg_u10'])
