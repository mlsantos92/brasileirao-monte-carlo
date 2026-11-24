import numpy as np, json
from collections import defaultdict

# code: (nome, P, J, V, E, D, GP, GC)
geral = {
 'palmeiras':('Palmeiras',69,32,20,9,3,56,22),
 'flamengo':('Flamengo',70,32,21,7,4,64,27),
 'cruzeiro':('Cruzeiro',54,32,16,6,10,51,46),
 'athletico-pr':('Athletico-PR',54,32,15,9,8,50,38),
 'fluminense':('Fluminense',51,32,14,9,9,50,41),
 'atletico-mg':('Atlético-MG',50,32,14,8,10,44,38),
 'bahia':('Bahia',50,32,13,11,8,45,40),
 'santos':('Santos',46,32,12,10,10,49,47),
 'sao-paulo':('São Paulo',43,32,12,7,13,37,36),
 'bragantino':('Bragantino',41,32,11,8,13,39,38),
 'botafogo':('Botafogo',39,32,10,9,13,44,51),
 'coritiba':('Coritiba',39,32,10,9,13,38,50),
 'vasco':('Vasco',38,31,10,8,13,39,45),
 'vitoria':('Vitória',38,32,10,8,14,35,46),
 'mirassol':('Mirassol',37,32,9,10,13,37,45),
 'internacional':('Internacional',35,32,8,11,13,36,40),
 'corinthians':('Corinthians',33,32,8,9,15,34,42),
 'gremio':('Grêmio',34,32,8,10,14,35,44),
 'remo':('Remo',26,32,5,11,16,34,50),
 'chapecoense':('Chapecoense',21,31,4,9,18,32,63),
}
# (J, V, E, D, GP, GC)
casa = {
 'palmeiras':(16,12,3,1,30,10),'flamengo':(16,12,3,1,32,12),'fluminense':(16,11,3,2,29,16),
 'atletico-mg':(16,10,5,1,27,17),'sao-paulo':(16,10,3,3,25,13),'vitoria':(16,10,2,4,23,13),
 'athletico-pr':(16,9,5,2,27,15),'cruzeiro':(16,9,4,3,27,16),'vasco':(16,8,3,5,24,20),
 'bahia':(16,7,6,3,23,17),'mirassol':(17,7,6,4,24,22),'gremio':(16,7,5,4,25,21),
 'bragantino':(15,7,3,5,24,17),'botafogo':(16,6,6,4,26,22),'santos':(16,6,6,4,23,21),
 'internacional':(16,5,5,6,21,17),'coritiba':(16,5,5,6,20,21),'corinthians':(16,5,4,7,16,17),
 'remo':(16,3,7,6,20,21),'chapecoense':(15,3,5,7,21,34)}
fora = {
 'flamengo':(16,9,4,3,32,15),'palmeiras':(16,8,6,2,26,12),'cruzeiro':(16,7,2,7,24,30),
 'bahia':(16,6,5,5,22,23),'santos':(16,6,4,6,26,26),'athletico-pr':(16,6,4,6,23,23),
 'coritiba':(16,5,4,7,18,29),'bragantino':(17,4,5,8,15,21),'atletico-mg':(16,4,3,9,17,21),
 'botafogo':(16,4,3,9,18,29),'fluminense':(16,3,6,7,21,25),'internacional':(16,3,6,7,15,23),
 'corinthians':(16,3,5,8,18,25),'vasco':(15,2,5,8,15,25),'mirassol':(15,2,4,9,13,23),
 'sao-paulo':(16,2,4,10,12,23),'remo':(16,2,4,10,14,29),'chapecoense':(16,1,4,11,11,29),
 'vitoria':(16,0,6,10,12,33),'gremio':(16,1,5,10,10,23)}

# conferência: casa + fora = geral
for c,(n,P,J,V,E,D,GP,GC) in geral.items():
    h,a = casa[c],fora[c]
    assert h[0]+a[0]==J and h[1]+a[1]==V and h[2]+a[2]==E and h[3]+a[3]==D, c
    assert h[4]+a[4]==GP and h[5]+a[5]==GC, c
    assert 3*V+E==P, c

jogos_rest = """chapecoense,vasco,21
bragantino,chapecoense,33
fluminense,internacional,33
santos,palmeiras,33
bahia,sao-paulo,33
remo,botafogo,33
atletico-mg,cruzeiro,33
vasco,flamengo,33
gremio,athletico-pr,33
corinthians,mirassol,33
coritiba,vitoria,33
bragantino,santos,34
chapecoense,mirassol,34
internacional,coritiba,34
athletico-pr,vasco,34
flamengo,gremio,34
botafogo,atletico-mg,34
sao-paulo,corinthians,34
palmeiras,remo,34
cruzeiro,bahia,34
vitoria,fluminense,34
corinthians,botafogo,35
coritiba,santos,35
cruzeiro,palmeiras,35
flamengo,athletico-pr,35
gremio,bahia,35
mirassol,atletico-mg,35
remo,chapecoense,35
sao-paulo,fluminense,35
vasco,internacional,35
vitoria,bragantino,35
athletico-pr,remo,36
atletico-mg,corinthians,36
bahia,coritiba,36
botafogo,sao-paulo,36
bragantino,vasco,36
chapecoense,cruzeiro,36
fluminense,mirassol,36
internacional,vitoria,36
palmeiras,flamengo,36
santos,gremio,36
atletico-mg,vasco,37
botafogo,bahia,37
chapecoense,palmeiras,37
corinthians,gremio,37
coritiba,flamengo,37
fluminense,cruzeiro,37
internacional,bragantino,37
mirassol,athletico-pr,37
sao-paulo,remo,37
vitoria,santos,37
athletico-pr,sao-paulo,38
bahia,atletico-mg,38
bragantino,fluminense,38
cruzeiro,internacional,38
flamengo,chapecoense,38
gremio,mirassol,38
palmeiras,coritiba,38
remo,corinthians,38
santos,botafogo,38
vasco,vitoria,38"""
jogos = [(l.split(',')[0], l.split(',')[1], int(l.split(',')[2])) for l in jogos_rest.split('\n')]
assert len(jogos)==61
# cada time deve fechar 38 jogos
cnt = defaultdict(int)
for h,a,_ in jogos: cnt[h]+=1; cnt[a]+=1
for c in geral: assert geral[c][2]+cnt[c]==38, (c, geral[c][2], cnt[c])
cnt_casa = defaultdict(int)
for h,a,_ in jogos: cnt_casa[h]+=1
for c in geral: assert casa[c][0]+cnt_casa[c]==19, (c,'casa')

times = list(geral)
# médias da liga
Jh = sum(casa[c][0] for c in times)
mu_h = sum(casa[c][4] for c in times)/Jh   # gols do mandante por jogo
mu_a = sum(fora[c][4] for c in times)/Jh   # gols do visitante por jogo

# Força geral (sem mando), usada como "prior" para encolher as forças por mando
mu_all = (mu_h+mu_a)/2
att_g = {c: (geral[c][6]/geral[c][2])/mu_all for c in times}
def_g = {c: (geral[c][7]/geral[c][2])/mu_all for c in times}

K = 6.0  # jogos "fantasmas" de encolhimento rumo à força geral do clube
def shrink(gols, J, mu, prior):
    return (gols + K*mu*prior)/(J*mu + K*mu)

att_h = {c: shrink(casa[c][4], casa[c][0], mu_h, att_g[c]) for c in times}  # ataque em casa
def_h = {c: shrink(casa[c][5], casa[c][0], mu_a, def_g[c]) for c in times}  # gols sofridos em casa
att_a = {c: shrink(fora[c][4], fora[c][0], mu_a, att_g[c]) for c in times}
def_a = {c: shrink(fora[c][5], fora[c][0], mu_h, def_g[c]) for c in times}

def lambdas(h, a):
    return mu_h*att_h[h]*def_a[a], mu_a*att_a[a]*def_h[h]

from math import exp, factorial
def probs(lh, la, rho=0.08):
    # Poisson com ajuste leve de empates (inflação de empates comum no Brasileirão)
    ph = [exp(-lh)*lh**k/factorial(k) for k in range(11)]
    pa = [exp(-la)*la**k/factorial(k) for k in range(11)]
    W=D=L=0
    for i in range(11):
        for j in range(11):
            p=ph[i]*pa[j]
            if i>j: W+=p
            elif i==j: D+=p
            else: L+=p
    D2 = D*(1+rho); s = W+D2+L
    return W/s, D2/s, L/s

N = 100_000
rng = np.random.default_rng(2026)
idx = {c:i for i,c in enumerate(times)}
T = len(times)
pts = np.array([geral[c][1] for c in times])[None,:].repeat(N,0).astype(np.int32)
vit = np.array([geral[c][3] for c in times])[None,:].repeat(N,0).astype(np.int32)
gp = np.array([geral[c][6] for c in times])[None,:].repeat(N,0).astype(np.int32)
gc = np.array([geral[c][7] for c in times])[None,:].repeat(N,0).astype(np.int32)

# incerteza da força: cada temporada simulada sorteia um multiplicador por clube
forma = np.exp(rng.normal(0, 0.10, size=(N,T)))
ddown = np.exp(rng.normal(0, 0.10, size=(N,T)))

prev = []
results_gremio_cori = None
for (h,a,r) in jogos:
    lh, la = lambdas(h,a)
    W,D,L = probs(lh,la)
    prev.append(dict(rodada=r, mandante=geral[h][0], visitante=geral[a][0],
                     xg_m=round(lh,2), xg_v=round(la,2), pm=round(W*100,1), pe=round(D*100,1), pv=round(L*100,1)))
    i,j = idx[h], idx[a]
    LH = lh*forma[:,i]*ddown[:,j]
    LA = la*forma[:,j]*ddown[:,i]
    g1 = rng.poisson(LH); g2 = rng.poisson(LA)
    # inflação de empates: pequena fração de jogos "travados" vira empate
    trava = rng.random(N) < 0.03
    m = np.minimum(g1,g2); g1 = np.where(trava, m, g1); g2 = np.where(trava, m, g2)
    hw = g1>g2; dr = g1==g2; aw = g1<g2
    pts[:,i] += 3*hw + dr; pts[:,j] += 3*aw + dr
    vit[:,i] += hw; vit[:,j] += aw
    gp[:,i]+=g1; gc[:,i]+=g2; gp[:,j]+=g2; gc[:,j]+=g1
    if (h,a)==('corinthians','mirassol'): results_gremio_cori = (hw.copy(), dr.copy(), aw.copy())

sg = gp-gc
chave = pts.astype(np.int64)*10**9 + vit.astype(np.int64)*10**6 + (sg.astype(np.int64)+500)*10**3 + gp.astype(np.int64)
chave = chave*100 + rng.integers(0,100,size=chave.shape)  # sorteio p/ empates restantes
ordem = np.argsort(-chave, axis=1)
pos = np.empty_like(ordem)
rows = np.arange(N)[:,None]
pos[rows, ordem] = np.arange(T)[None,:]
pos += 1

rebaix = (pos>=17)
out=[]
for c in times:
    i=idx[c]
    out.append(dict(code=c, clube=geral[c][0], pts=geral[c][1], j=geral[c][2],
        casa_pts=3*casa[c][1]+casa[c][2], casa_j=casa[c][0],
        fora_pts=3*fora[c][1]+fora[c][2], fora_j=fora[c][0],
        rest_casa=cnt_casa[c], rest_fora=cnt[c]-cnt_casa[c],
        rebaix=round(rebaix[:,i].mean()*100,1),
        titulo=round((pos[:,i]==1).mean()*100,1),
        top5=round((pos[:,i]<=5).mean()*100,1),
        pts_med=int(np.median(pts[:,i])), pts_p10=int(np.percentile(pts[:,i],10)), pts_p90=int(np.percentile(pts[:,i],90)),
        pos_med=int(np.median(pos[:,i])),
        att_h=round(att_h[c],2), def_h=round(def_h[c],2), att_a=round(att_a[c],2), def_a=round(def_a[c],2)))

# pontos para escapar: pontuação do 17º colocado
p17 = np.sort(pts,axis=1)[:,-17]
p16 = np.sort(pts,axis=1)[:,-16]
corte = dict(p16_mediana=int(np.median(p16)), p16_p90=int(np.percentile(p16,90)), p17_mediana=int(np.median(p17)))

# chance de escapar por pontuação final (para clubes da briga)
def escape_por_pts(c):
    i=idx[c]; d={}
    for p in range(35,50):
        mask = pts[:,i]==p
        if mask.sum()>300: d[p]=round((1-rebaix[mask,i].mean())*100,1)
    return d
safe_curve = {}
for p in range(36,49):
    tot=0; ok=0
    for c in ['internacional','corinthians','gremio','mirassol','vitoria','vasco','coritiba','botafogo']:
        i=idx[c]; m = pts[:,i]==p; tot+=m.sum(); ok+=(~rebaix[m,i]).sum()
    if tot>500: safe_curve[p]=round(ok/tot*100,1)

# Z4 mais provável
from collections import Counter
z4 = Counter()
samp = ordem[:, -4:]
for row in samp[:20000]:
    z4[tuple(sorted(times[k] for k in row))]+=1
z4_top = [(list(geral[c][0] for c in k), round(v/20000*100,1)) for k,v in z4.most_common(6)]

# condicional Coritiba x Grêmio
hw,dr,aw = results_gremio_cori
cond = {}
for c in ['gremio','corinthians','internacional','mirassol']:
    i=idx[c]
    cond[c] = dict(cori_vence=round(rebaix[hw,i].mean()*100,1), empate=round(rebaix[dr,i].mean()*100,1), gremio_vence=round(rebaix[aw,i].mean()*100,1))

# Conferência de pontos esperados (fórmula fechada vs simulação)
exp_pts = defaultdict(float)
for p in prev:
    pass

res = dict(mu_h=round(mu_h,3), mu_a=round(mu_a,3), clubes=out, jogos=prev, corte=corte,
           safe_curve=safe_curve, z4=z4_top, cond=cond, N=N)
json.dump(res, open('resultado.json','w'), ensure_ascii=False, indent=1)
print('mu_h',mu_h,'mu_a',mu_a)
for o in sorted(out, key=lambda x:-x['rebaix']):
    print(f"{o['clube']:15s} {o['pts']:3d} reb {o['rebaix']:5.1f}  tit {o['titulo']:5.1f} top5 {o['top5']:5.1f}  pts {o['pts_med']} [{o['pts_p10']}-{o['pts_p90']}] attH {o['att_h']} defH {o['def_h']} attA {o['att_a']} defA {o['def_a']}")
print(corte); print(safe_curve); print(z4_top); print(cond)
