import numpy as np, json
from collections import Counter
from math import exp, factorial

src = open('sim.py').read()
exec(src[:src.index('# médias da liga')])   # geral (tabela real), jogos restantes
# ---- resultados já disputados da 33ª rodada (FotMob, 30/10/2026)
RES33 = [('fluminense','internacional',2,1),('bragantino','chapecoense',3,0),('santos','palmeiras',0,0),('bahia','sao-paulo',3,2),
         ('remo','botafogo',2,1),('atletico-mg','cruzeiro',0,1),('vasco','flamengo',1,4),('gremio','athletico-pr',2,0),
         ('corinthians','mirassol',2,0),('coritiba','vitoria',2,0),   # sexta e sábado
         ('bragantino','santos',2,1),('chapecoense','mirassol',1,2),('internacional','coritiba',1,0),   # 34ª: segunda e terça
         ('athletico-pr','vasco',1,3),('flamengo','gremio',3,1),('botafogo','atletico-mg',1,0),('sao-paulo','corinthians',0,0),   # 34ª: quarta
         ('palmeiras','remo',6,1),('cruzeiro','bahia',3,2),('vitoria','fluminense',0,3),   # 34ª: quinta e sexta
         ('mirassol','atletico-mg',0,0),('chapecoense','vasco',0,2),   # 14/11
         ('coritiba','santos',0,1),('remo','chapecoense',2,0),('flamengo','athletico-pr',2,1),('cruzeiro','palmeiras',2,1),('corinthians','botafogo',4,0),('gremio','bahia',0,0),
         ('vasco','internacional',2,1),('vitoria','bragantino',2,1),('sao-paulo','fluminense',0,1),
         ('palmeiras','flamengo',1,1),('bahia','coritiba',0,1),('chapecoense','cruzeiro',1,2),('athletico-pr','remo',4,2),('fluminense','mirassol',1,0),('bragantino','vasco',1,0),
         ('santos','gremio',0,2),('internacional','vitoria',2,5),('botafogo','sao-paulo',1,1)]   # 23/11: 36ª   # 21-22/11: 36ª   # 19/11: fim da 35ª   # 18/11: 35ª   # 14/11: 35ª (abertura) e jogo atrasado da 21ª   # 34ª: quinta e sexta
for (h_,a_,x_,y_) in RES33:
    for c_,gf_,ga_ in ((h_,x_,y_),(a_,y_,x_)):
        n_,p_,j_,v_,e_,d_,gp_,gc_ = geral[c_]
        geral[c_] = (n_, p_+(3 if gf_>ga_ else 1 if gf_==ga_ else 0), j_+1, v_+(gf_>ga_), e_+(gf_==ga_), d_+(gf_<ga_), gp_+gf_, gc_+ga_)
    jogos = [g for g in jogos if not (g[0]==h_ and g[1]==a_)]
# Chapecoense x Vasco (adiado da 21ª) remarcado para 14/11: entra depois da 34ª rodada
jogos = [g for g in jogos if g[2]!=21 and g[2]<=34] + [g for g in jogos if g[2]==21] + [g for g in jogos if g[2]>34]

nome = {'Athletico Paranaense':'athletico-pr','Atlético-MG':'atletico-mg','Bahia':'bahia','Botafogo':'botafogo',
 'Chapecoense':'chapecoense','Corinthians':'corinthians','Coritiba':'coritiba','Cruzeiro':'cruzeiro','Flamengo':'flamengo',
 'Fluminense':'fluminense','Grêmio':'gremio','Internacional':'internacional','Mirassol':'mirassol','Palmeiras':'palmeiras',
 'RB Bragantino':'bragantino','Remo':'remo','Santos':'santos','São Paulo':'sao-paulo','Vasco da Gama':'vasco','Vitória':'vitoria'}
F = ['j','pts','gp','gc','xg','xga','ch','cha','alvo','alvoa','gr','gra','def','xgota']
A = {}
for l in open('v9/agg.txt'):
    k,*v = l.strip().split(';'); t,venue = k.split('|'); A[(nome[t],venue)] = dict(zip(F,map(float,v)))
GKD = {}
for l in open('v8/gk.txt'):
    t,on,xgot,ga = l.strip().split(';'); GKD[nome[t]] = dict(on=float(on), xgot=float(xgot), ga=float(ga))
PL = {}
for l in open('v9/pl.txt'):
    k,sh,g,xg = l.strip().split(';'); t,p = k.split('|'); PL.setdefault(nome[t],[]).append(dict(jogador=p, sh=float(sh), g=float(g), xg=float(xg)))

times = list(geral)
import desf
DESF_J = desf.carregar(geral, A, 'desfalques13.txt')   # 05/11: suspensões, 3º amarelo, expulsões e riscos do STJD
LUTA = {'vitoria','gremio','corinthians','internacional','mirassol','coritiba','botafogo'}   # 19/11: Vasco garantido matematicamente   # 17/11: desfalques só para quem ainda briga contra a queda
DESF_J = [j for j in DESF_J if j['clube'] in LUTA]
DESF = desf.fatores(DESF_J, jogos)
DESF = {k: {cc: (1.0, 1.0, []) for cc in v} for k, v in DESF.items()}   # 24/11: substituído pelas escalações prováveis
import recente
# técnicos novos: a fase conta só os jogos com o técnico atual
INICIO_TEC = {'corinthians':'2026-10-08',   # Diniz saiu em 07/10
              'coritiba':'2026-10-28',      # Seabra saiu em 27/10
              'vitoria':'2026-11-03'}       # Jair Ventura saiu em 02/11: ainda sem jogos -> fase neutra
# fase recente com peso maior (sem distinção de técnico): mais expoente, menos encolhimento, limites mais largos
recente.E_XG, recente.E_PPG, recente.K_REC, recente.LIM = 0.8, 0.15, 2.0, (0.78, 1.28)
recente.ULT = (3, 3)   # 23/11: últimos 6 jogos de cada clube (3 em casa e 3 fora), em todas as competições
REC = recente.fatores(A, geral, 'recente12.txt')   # inclui todos os jogos de copa das últimas 4 semanas
estudo = [c for c in times if geral[c][1] < 40]
tot = lambda c: {f: A[(c,'casa')][f]+A[(c,'fora')][f] for f in F}

H=[A[(c,'casa')] for c in times]; W=[A[(c,'fora')] for c in times]; J=sum(h['j'] for h in H)
mu = {('xg','casa'): sum(h['xg'] for h in H)/J, ('xg','fora'): sum(w['xg'] for w in W)/J,
      ('gr','casa'): sum(h['gr'] for h in H)/J, ('gr','fora'): sum(w['gr'] for w in W)/J}
conv = (sum(h['gp'] for h in H)+sum(w['gp'] for w in W))/(sum(h['xg'] for h in H)+sum(w['xg'] for w in W))
K_MANDO=6.0

def rel(c, venue, stat, against):
    """razão (clube/mando) vs média da liga, encolhida para o total do clube. stat: xg ou gr"""
    a = A[(c,venue)]; T = tot(c)
    f = stat+'a' if against else stat
    opp_venue = 'fora' if venue=='casa' else 'casa'
    m = mu[(stat, opp_venue if against else venue)]
    m_all = (mu[(stat,'casa')]+mu[(stat,'fora')])/2
    team_rate = (T[f]/T['j'])/m_all
    return (a[f] + K_MANDO*m*team_rate)/(a['j']*m + K_MANDO*m)

# ---- finalização: jogador a jogador (poucas chances p/ gol = bônus), encolhimento leve
S0 = 40.0
def fin_jogadores(c):
    bonus = sum((p['g']-p['xg'])*p['sh']/(p['sh']+S0) for p in PL.get(c,[]))
    return float(np.clip(1 + bonus/tot(c)['xg'], 0.8, 1.25)), bonus
# ---- goleiro: gols evitados (xGOT enfrentado - gols), encolhimento leve
K_GK = 100.0
def gk_fator(c):
    g = GKD[c]; prev = (g['xgot']-g['ga'])*g['on']/(g['on']+K_GK)
    return float(np.clip(1 - prev/tot(c)['xga'], 0.8, 1.2)), prev
# fatores "neutros" (modelo base, fortemente encolhidos) para jogos fora do estudo
K_CONV=25.0
fin_base = {c: ((tot(c)['gp']+K_CONV*conv)/(tot(c)['xg']+K_CONV))/conv for c in times}
gk_base  = {c: ((tot(c)['gc']+K_CONV*conv)/(tot(c)['xga']+K_CONV))/conv for c in times}

M = {}
for c in times:
    fe, fb = fin_jogadores(c); ge, gp_ = gk_fator(c)
    M[c] = dict(
      att_xg={v: rel(c,v,'xg',False) for v in ('casa','fora')}, def_xg={v: rel(c,v,'xg',True) for v in ('casa','fora')},
      att_gr={v: rel(c,v,'gr',False) for v in ('casa','fora')}, def_gr={v: rel(c,v,'gr',True) for v in ('casa','fora')},
      fin_e=fe, fin_bonus=fb, gk_e=ge, gk_prev=gp_, fin_b=fin_base[c], gk_b=gk_base[c])

# ---- 24/11: escalações prováveis + métricas por jogador (goleiro titular, finalizadores, criação e linha do XI)
import escal
_code = {geral[c][0]: c for c in geral}
LIN = escal.fatores({c: tot(c)['xg'] for c in times}, {c: tot(c)['xga'] for c in times}, {c: GKD[c]['xgot'] for c in times}, _code)
for c in times:
    M[c]['fin_e_temp'], M[c]['gk_e_temp'] = M[c]['fin_e'], M[c]['gk_e']
    # 70% escalação provável, 30% temporada (as escalações da 37ª e 38ª ainda não saíram)
    M[c]['fin_e'] = LIN[c]['fin']**0.7 * M[c]['fin_e_temp']**0.3; M[c]['gk_e'] = LIN[c]['gk']**0.7 * M[c]['gk_e_temp']**0.3
    M[c]['att_lin'], M[c]['dfn_lin'] = LIN[c]['att'], LIN[c]['dfn']
# exceção por jogo: Yuri Alberto suspenso contra o Atlético-MG (36ª)
_y = escal.fatores({c: tot(c)['xg'] for c in times}, {c: tot(c)['xga'] for c in times}, {c: GKD[c]['xgot'] for c in times}, _code, clube_unico='Corinthians', fora_extra=('Yuri Alberto',))['corinthians']
LIN_J = {('corinthians', 36): _y}
def _m_jogo(c, r):
    L = LIN_J.get((c, r)); m = dict(M[c])
    if L: m['fin_e'] = L['fin']**0.7 * M[c]['fin_e_temp']**0.3; m['gk_e'] = L['gk']**0.7 * M[c]['gk_e_temp']**0.3; m['att_lin'], m['dfn_lin'] = L['att'], L['dfn']
    return m
CUR_R = [None]
W_XG, W_GR = 0.7, 0.3
# ---- retrospecto real casa/fora (gols e pontos), jogos sem expulsão e sem placar fora da curva
AR = {}
for l in open('v9/agg.txt'):
    k,*v = l.strip().split(';'); t,venue = k.split('|'); AR[(nome[t],venue)] = dict(zip(F,map(float,v)))
JR = sum(AR[(c,'casa')]['j'] for c in times)
mg_h = sum(AR[(c,'casa')]['gp'] for c in times)/JR; mg_a = sum(AR[(c,'fora')]['gp'] for c in times)/JR
def rel_res(c, venue, against):
    a = AR[(c,venue)]; T = {f: AR[(c,'casa')][f]+AR[(c,'fora')][f] for f in F}
    f = 'gc' if against else 'gp'
    m = (mg_a if venue=='casa' else mg_h) if against else (mg_h if venue=='casa' else mg_a)
    team = (T[f]/T['j'])/((mg_h+mg_a)/2)
    return (a[f] + K_MANDO*m*team)/(a['j']*m + K_MANDO*m)
RES = {c: {('att','casa'): rel_res(c,'casa',False), ('att','fora'): rel_res(c,'fora',False),
           ('def','casa'): rel_res(c,'casa',True), ('def','fora'): rel_res(c,'fora',True)} for c in times}
W_CH = 0.6   # peso das chances; 0.4 para o retrospecto real
# ---- viagem e descanso (coeficientes estimados nos 241 jogos sem expulsão)
B_DIST, B_REST_A, B_REST_H = -0.0301, -0.1251, -0.1956
ab = {'CAP':'athletico-pr','CAM':'atletico-mg','BAH':'bahia','BOT':'botafogo','CHA':'chapecoense','COR':'corinthians','CFC':'coritiba','CRU':'cruzeiro','FLA':'flamengo','FLU':'fluminense','GRE':'gremio','INT':'internacional','MIR':'mirassol','PAL':'palmeiras','RBB':'bragantino','REM':'remo','SAN':'santos','SAO':'sao-paulo','VAS':'vasco','VIT':'vitoria'}
VM = {}
for l in open('v9/viagem_media.txt'):
    t,d,sa,sh = l.strip().split(';'); VM[ab[t]] = dict(d=float(d), sa=float(sa), sh=float(sh))
VG = {}
for l in open('viagem.txt'):
    r_,h_,a_,d,ra,rh = l.strip().split(';'); VG[(ab[h_],ab[a_])] = dict(d=float(d), ra=float(ra), rh=float(rh))
# ---- descanso com Copa do Brasil, Libertadores e Sul-Americana (FotMob, 04/11)
DESC = {}
for l in open('descanso.txt'):
    dt_,h_,a_,rh_,ch_,nh_,cnh_,ra_,ca_,na_,cna_ = l.rstrip('\n').split('|')
    DESC[(recente.NOME[h_],recente.NOME[a_])] = dict(rh=float(rh_), nh=float(nh_) if nh_ else 99, cnh=cnh_, ra=float(ra_), na=float(na_) if na_ else 99, cna=cna_)
# final da Copa do Brasil (Grêmio x Palmeiras) em Brasília, 06/12: 4 dias depois da 38ª rodada
for k_ in (('gremio','mirassol'),('palmeiras','coritiba')):
    DESC[k_]['nh'] = 4.0; DESC[k_]['cnh'] = 'Copa do Brasil (final)'
def descanso(h, a):
    v = DESC[(h,a)]; out = []
    for c, rest, nxt, comp, B, avg in ((h, v['rh'], v['nh'], v['cnh'], B_REST_H, VM[h]['sh']), (a, v['ra'], v['na'], v['cna'], B_REST_A, VM[a]['sa'])):
        curto = 1.0 if rest <= 3.5 else 0.0                       # jogou há 3,5 dias ou menos (qualquer competição)
        rod = 0.0
        if comp and comp != 'Série A' and nxt <= 3.5: rod = 1.0    # decisão de copa em até 3,5 dias: tende a poupar titulares
        if comp == 'Copa Libertadores' and nxt <= 1.5: rod = 2.0   # jogo na véspera da final da Libertadores: time reserva
        if comp == 'Copa do Brasil (final)' and nxt <= 4.5: rod = 0.5   # final em Brasília 4 dias depois: rodízio parcial e viagem
        att = exp(B*(curto - avg) + B*rod); dfn = exp(-B*rod)      # rodízio também enfraquece a defesa
        out.append(dict(att=att, **{'def': dfn}, curto=curto, rod=rod, rest=rest, nxt=nxt, comp=comp))
    return out[0], out[1]
def viagem(h, a):
    v = VG[(h,a)]; sa = 1.0 if v['ra'] <= 3.5 else 0.0; sh = 1.0 if v['rh'] <= 3.5 else 0.0
    fa = exp(B_DIST*(v['d']-VM[a]['d'])/1000 + B_REST_A*(sa-VM[a]['sa']))
    fh = exp(B_REST_H*(sh-VM[h]['sh']))
    return fh, fa, v
# ---- evolução / fase: xG dos últimos 8 jogos sem expulsão e pontos por jogo nos últimos 10
FM = {}
for l in open('v9/forma.txt'):
    t,J_,p1,p2,p10,p5,xf,xa,xf8,xa8 = l.strip().split(';')
    c = ab[t]; ppg = geral[c][1]/geral[c][2]
    clip = lambda x: min(max(x,0.5),1.6)
    r_pts = clip(float(p10)/ppg)
    FM[c] = dict(att=clip(float(xf8)/float(xf))**0.20 * r_pts**0.05,
                 dfn=clip(float(xa8)/float(xa))**0.20 * (1/r_pts)**0.05,
                 ppg1=float(p1), ppg2=float(p2), ppg10=float(p10), ppg5=float(p5))
# ---- fase por mando: últimos 5 jogos em casa / fora (xG sem expulsão e pontos) vs a média do clube naquele mando
FV = {}
for l in open('v9/forma_mando.txt'):
    v_ = l.strip().split(';'); c = ab[v_[0]]
    Hj,pH,pH5,xfH,xaH,xfH5,xaH5 = map(float, v_[1:8]); Aj,pA,pA5,xfA,xaA,xfA5,xaA5 = map(float, v_[8:15])
    clip = lambda x: min(max(x,0.5),1.6)
    def fv(p,p5,xf,xa,xf5,xa5):
        rp = clip(p5/p) if p>0 else 1.0
        return dict(att=clip(xf5/xf)**0.25 * rp**0.07, dfn=clip(xa5/xa)**0.25 * (1/rp)**0.07, ppg=p, ppg5=p5, xf=xf, xf5=xf5, xa=xa, xa5=xa5)
    FV[c] = {'casa': fv(pH,pH5,xfH,xaH,xfH5,xaH5), 'fora': fv(pA,pA5,xfA,xaA,xfA5,xaA5)}
def lambdas_res(h, a):
    lh = mg_h*RES[h][('att','casa')]*RES[a][('def','fora')]
    la = mg_a*RES[a][('att','fora')]*RES[h][('def','casa')]
    return lh, la
def lambdas_ch(h, a):
    mh, ma = _m_jogo(h, CUR_R[0]), _m_jogo(a, CUR_R[0])
    if True:   # cruzamento completo em todos os jogos
        ah = W_XG*mh['att_xg']['casa'] + W_GR*mh['att_gr']['casa']; da = W_XG*ma['def_xg']['fora'] + W_GR*ma['def_gr']['fora']
        aa = W_XG*ma['att_xg']['fora'] + W_GR*ma['att_gr']['fora']; dh = W_XG*mh['def_xg']['casa'] + W_GR*mh['def_gr']['casa']
        lh = mu[('xg','casa')]*conv*ah*mh['fin_e']*mh['att_lin']*da*ma['gk_e']*ma['dfn_lin']
        la = mu[('xg','fora')]*conv*aa*ma['fin_e']*ma['att_lin']*dh*mh['gk_e']*mh['dfn_lin']
    else:
        lh = mu[('xg','casa')]*conv*mh['att_xg']['casa']*mh['fin_b']*ma['def_xg']['fora']*ma['gk_b']
        la = mu[('xg','fora')]*conv*ma['att_xg']['fora']*ma['fin_b']*mh['def_xg']['casa']*mh['gk_b']
    return lh, la

def lambdas(h, a):
    ch_h, ch_a = lambdas_ch(h, a); rs_h, rs_a = lambdas_res(h, a)
    fh, fa, _ = viagem(h, a)
    lh, la = ch_h, ch_a      # PERFIL PURO: só chances criadas/cedidas por mando (xG + grandes chances), goleiro e finalizadores
    return lh, la

def probs(lh, la, rho=0.08):
    ph=[exp(-lh)*lh**k/factorial(k) for k in range(11)]; pa=[exp(-la)*la**k/factorial(k) for k in range(11)]
    w=d=l=0
    for i in range(11):
        for j in range(11):
            p=ph[i]*pa[j]
            if i>j: w+=p
            elif i==j: d+=p
            else: l+=p
    d*=1+rho; s=w+d+l; return w/s,d/s,l/s

def placar(lh, la, rho=0.08):
    ph=[exp(-lh)*lh**k/factorial(k) for k in range(8)]; pa=[exp(-la)*la**k/factorial(k) for k in range(8)]
    grid={(i,j): ph[i]*pa[j]*((1+rho) if i==j else 1) for i in range(8) for j in range(8)}
    tot_=sum(grid.values()); top=sorted(grid.items(), key=lambda x:-x[1])[:3]
    return [(f"{i} x {j}", round(p/tot_*100,1)) for (i,j),p in top]

# ---- z-scores (desvio padrão entre os 20 clubes, por mando)
def zs(stat, venue):
    v = {c: A[(c,venue)][stat]/A[(c,venue)]['j'] for c in times}
    arr = np.array(list(v.values())); m, s = arr.mean(), arr.std(ddof=1)
    return {c: (v[c]-m)/s for c in times}, v
Z = {(s,v): zs(s,v) for s in ('xg','xga','gr','gra') for v in ('casa','fora')}

N=100_000; rng=np.random.default_rng(20261101); idx={c:i for i,c in enumerate(times)}; T_=len(times)
rep=lambda col: np.array([geral[c][col] for c in times])[None,:].repeat(N,0).astype(np.int32)
pts,vit,gp,gc = rep(1),rep(3),rep(6),rep(7)
forma=np.exp(rng.normal(0,0.10,(N,T_))); ddown=np.exp(rng.normal(0,0.10,(N,T_)))
prev=[]; condR=None
GH=[]; GA=[]; GJ=[]

ordem_rod = []
MOTD = []
MOT_G = []; MOT_R = []
for (h,a,r) in jogos:
    if r not in ordem_rod: ordem_rod.append(r)
relax_hist = {c: [] for c in times}; press_hist = {}
for rod in ordem_rod:
    gr_ = [(h,a,r) for (h,a,r) in jogos if r==rod]
    # jogos restantes por clube a partir desta rodada
    restam = np.zeros(T_)
    for (h,a,r) in jogos:
        if ordem_rod.index(r) >= ordem_rod.index(rod): restam[idx[h]]+=1; restam[idx[a]]+=1
    srt = -np.sort(-pts, axis=1)
    p7, p16, p17 = srt[:,6:7], srt[:,15:16], srt[:,16:17]
    Rr = np.maximum(restam[None,:], 1)
    pos = (pts[:,None,:] > pts[:,:,None]).sum(axis=2) + 1      # posição (empates pela frente)
    s_obj = np.where(pos >= 17, np.maximum(0, p16 - pts)/Rr,
                     np.minimum(np.maximum(0, p7 - pts), np.maximum(0, pts - p17))/Rr)
    press = (((np.abs(pts - p7) <= 3) & (pos <= 10)) | ((np.abs(pts - p17) <= 3) & (pos >= 12))).astype(float)
    s_c = np.minimum(s_obj, 1.5) - 0.165          # distância limitada ao intervalo observado, centrada na média da amostra
    p_c = press - 0.574                            # pressão centrada na média da amostra
    ATTM = np.ones_like(s_c)
    DEFM = np.ones_like(s_c)
    # Grêmio: se escapar, vai à Libertadores -> motivação extra enquanto a permanência estiver em jogo (premissa: cria 5% mais e cede 5% menos)
    ig_ = idx['gremio']; pg_ = pts[:,ig_]; R_ = Rr[0,ig_]
    vivo_ = (pg_ <= p17[:,0] + 3*R_) & (pg_ + 3*R_ >= p16[:,0])
    ATTM[:,ig_] = np.where(vivo_, 1.05, 1.0); DEFM[:,ig_] = np.where(vivo_, 0.95, 1.0)
    MOT_G.append(round(float(vivo_.mean()*100),1))
    reb_ = (pts + 3*Rr) < p16        # 24/11: já rebaixado matematicamente nesta simulação -> rende bem menos
    ATTM = np.where(reb_, ATTM*0.88, ATTM); DEFM = np.where(reb_, DEFM*1.12, DEFM)
    MOT_R.append({c: round(float(reb_[:,idx[c]].mean()*100),1) for c in ('remo','chapecoense','internacional')})
    for c in times:
        i_ = idx[c]
        _am = np.exp(-0.0573*s_c[:,i_] - 0.0906*p_c[:,i_])*ATTM[:,i_]; _dm = np.exp(0.1425*s_c[:,i_] + 0.1269*p_c[:,i_])*DEFM[:,i_]   # efeito estimado nos dados + bônus do Grêmio
        relax_hist[c].append(round(float((_am/_dm - 1).mean()*100),1))
        press_hist.setdefault(c, []).append(round(float(press[:,i_].mean()*100),1))
        _d = s_obj[:,i_]*Rr[0,i_]                   # distância em pontos até o objetivo mais próximo
        _lib = (pos[:,i_] < 17) & ((p7[:,0]-pts[:,i_]) < (pts[:,i_]-p17[:,0]))
        _sc = s_c[:,i_]; _pc = p_c[:,i_]
        MOTD.append(dict(id=f"{c}|{rod}", clube=geral[c][0], rodada=int(rod), pontos=round(float(pts[:,i_].mean()),1),
            jogos_restantes=int(restam[i_]), objetivo_lib=round(float(_lib.mean()*100),1), na_zona=round(float((pos[:,i_]>=17).mean()*100),1),
            distancia_pts=round(float(_d.mean()),1), distancia_pj=round(float(np.minimum(s_obj[:,i_],1.5).mean()),2),
            sob_pressao=round(float(press[:,i_].mean()*100),1),
            dist_ataque=round(float((np.exp(-0.0573*_sc)-1).mean()*100),1), dist_defesa=round(float((np.exp(0.1425*_sc)-1).mean()*100),1),
            press_ataque=round(float((np.exp(-0.0906*_pc)-1).mean()*100),1), press_defesa=round(float((np.exp(0.1269*_pc)-1).mean()*100),1),
            bonus_lib=round(float(((ATTM[:,i_]/DEFM[:,i_])-1).mean()*100),1), total=round(float((_am/_dm - 1).mean()*100),1)))
    for (h,a,r) in gr_:
        CUR_R[0]=r; lh,la=lambdas(h,a)
        fah,fdh,_n1 = DESF[(h,a,r)][h]; faa,fda,_n2 = DESF[(h,a,r)][a]
        lh*=fah*fda; la*=faa*fdh                      # desfalques: ataque do clube x defesa do adversário
        lh*=REC[h]['att']*REC[a]['def_']; la*=REC[a]['att']*REC[h]['def_']   # fase recente (últimas 4 semanas, técnico atual)
        # desgaste da Copa do Brasil no meio da semana: leve queda na 34ª (cria 5% menos, cede 5% mais)
        # descanso entre partidas (todas as competições) e rodízio antes de jogo decisivo de copa
        fdh_, fda_ = descanso(h, a)
        lh*=fdh_['att']*fda_['def']; la*=fda_['att']*fdh_['def']
        w,d,l=probs(lh,la)
        pl3=placar(lh,la); fh_,fa_,vv=viagem(h,a)
        prev.append(dict(rodada=r,h=h,a=a,mandante=geral[h][0],visitante=geral[a][0],xg_m=round(lh,2),xg_v=round(la,2),pm=round(w*100,1),pe=round(d*100,1),pv=round(l*100,1),placares=pl3,dist=vv['d'],desc_v=vv['ra'],desc_m=vv['rh'],f_viagem=round(fa_,3),f_desc_m=round(fh_,3)))
        i,j=idx[h],idx[a]
        mh = ATTM[:,i]*DEFM[:,j]
        ma = ATTM[:,j]*DEFM[:,i]
        g1=rng.poisson(lh*mh*forma[:,i]*ddown[:,j]); g2=rng.poisson(la*ma*forma[:,j]*ddown[:,i])
        tr=rng.random(N)<0.03; m=np.minimum(g1,g2); g1=np.where(tr,m,g1); g2=np.where(tr,m,g2)
        hw=g1>g2; dr=g1==g2; aw=g1<g2
        pts[:,i]+=3*hw+dr; pts[:,j]+=3*aw+dr; vit[:,i]+=hw; vit[:,j]+=aw; gp[:,i]+=g1; gc[:,i]+=g2; gp[:,j]+=g2; gc[:,j]+=g1
        if (h,a)==('internacional','coritiba'): condR=(hw.copy(),dr.copy(),aw.copy())
        GH.append(g1.astype(np.int8)); GA.append(g2.astype(np.int8)); GJ.append((h,a,r))
sg=gp-gc
ch=pts.astype(np.int64)*10**9+vit.astype(np.int64)*10**6+(sg.astype(np.int64)+500)*10**3+gp.astype(np.int64)
ch=ch*100+rng.integers(0,100,size=ch.shape)
ordem=np.argsort(-ch,axis=1); pos=np.empty_like(ordem); pos[np.arange(N)[:,None],ordem]=np.arange(T_)[None,:]; pos+=1
reb=pos>=17

r2 = {o['code']:o for o in json.load(open('resultado2.json'))['clubes']}
r3 = {o['code']:o for o in json.load(open('resultado22.json'))['clubes']}
# vagas na Libertadores (24/11): +1 se o Palmeiras ganhar a Libertadores (28/11), +1 se o Grêmio cair
P_PAL_LIB = 0.60
LIB_PAL = np.random.default_rng(7).random(N) < P_PAL_LIB
EXTRA = LIB_PAL.astype(int) + reb[:, idx['gremio']].astype(int)
CUT_D = (4 + EXTRA)[:, None] if False else (4 + EXTRA)
CUT_T = 6 + EXTRA
print('vagas extras: 0=%.1f%% 1=%.1f%% 2=%.1f%%' % tuple((EXTRA==v).mean()*100 for v in (0,1,2)))
clubes=[]
for c in times:
    i=idx[c]; T=tot(c); m=M[c]; g=GKD[c]
    top = sorted(PL.get(c,[]), key=lambda p: -((p['g']-p['xg'])*p['sh']/(p['sh']+S0)))
    best = top[0] if top else None
    clubes.append(dict(code=c, clube=geral[c][0], pontos=geral[c][1], estudo=c in estudo, jogos_limpos=int(T['j']),
      xg_jogo=round(T['xg']/T['j'],2), grandes_jogo=round(T['gr']/T['j'],2), xga_jogo=round(T['xga']/T['j'],2), grandes_contra_jogo=round(T['gra']/T['j'],2),
      chutes_por_gol=round(T['ch']/T['gp'],1) if T['gp'] else None,
      z_xg_casa=round(Z[('xg','casa')][0][c],2), z_xg_fora=round(Z[('xg','fora')][0][c],2),
      z_xga_casa=round(Z[('xga','casa')][0][c],2), z_xga_fora=round(Z[('xga','fora')][0][c],2),
      z_gr_casa=round(Z[('gr','casa')][0][c],2), z_gr_fora=round(Z[('gr','fora')][0][c],2),
      z_gra_casa=round(Z[('gra','casa')][0][c],2), z_gra_fora=round(Z[('gra','fora')][0][c],2),
      gols_evitados=round(g['xgot']-g['ga'],1), fator_goleiro=round(m['gk_e'],3),
      bonus_finalizadores=round(m['fin_bonus'],1), fator_ataque=round(m['fin_e'],3),
      melhor_finalizador=(f"{best['jogador']} ({best['g']:.1f} gols, {best['xg']:.1f} xG, {best['sh']:.0f} chutes, ponderados)" if best else ""),
      rebaixamento=round(reb[:,i].mean()*100,1), reb_v3=r3[c]['rebaixamento'], reb_v2=r2[c]['rebaixamento'], reb_v1=r2[c]['reb_antes'], tit_v3=r3[c]['titulo'], ppg1=FM[c]['ppg1'], ppg2=FM[c]['ppg2'], ppg10=FM[c]['ppg10'], f_forma_att=round(FM[c]['att'],3), f_forma_def=round(FM[c]['dfn'],3), ppg_casa=FV[c]['casa']['ppg'], ppg_casa5=FV[c]['casa']['ppg5'], ppg_fora=FV[c]['fora']['ppg'], ppg_fora5=FV[c]['fora']['ppg5'], fase_casa=round(FV[c]['casa']['att']/FV[c]['casa']['dfn'],3), fase_fora=round(FV[c]['fora']['att']/FV[c]['fora']['dfn'],3), fv_casa_att=round(FV[c]['casa']['att'],3), fv_casa_def=round(FV[c]['casa']['dfn'],3), fv_fora_att=round(FV[c]['fora']['att'],3), fv_fora_def=round(FV[c]['fora']['dfn'],3), relax_por_rodada=relax_hist[c],
      titulo=round((pos[:,i]==1).mean()*100,1), top5=round((pos[:,i]<=5).mean()*100,1), g4=round((pos[:,i]<=CUT_D).mean()*100,1), g6=round((pos[:,i]<=CUT_T).mean()*100,1), g4_fixo=round((pos[:,i]<=4).mean()*100,1), g6_fixo=round((pos[:,i]<=6).mean()*100,1),
      pts_proj=int(np.median(pts[:,i])), pts_p10=int(np.percentile(pts[:,i],10)), pts_p90=int(np.percentile(pts[:,i],90))))

# Grêmio: se não cair, vai à Libertadores pela Copa do Brasil (24/11)
for o_ in clubes:
    if o_['code']=='gremio':
        i_=idx['gremio']; vaga_=(~reb[:,i_]) | (pos[:,i_]<=CUT_D)
        o_['g4']=round(float(vaga_.mean()*100),1); o_['g6']=round(float(((~reb[:,i_]) | (pos[:,i_]<=CUT_T)).mean()*100),1)
# ---- cruzamento jogo a jogo, só clubes do estudo
cruz=[]
risco_ = {o['code'] for o in clubes if 0 < o['rebaixamento'] < 100}   # 24/11: só quem ainda tem chance de cair
for g in prev:
    for c in risco_:
        if c not in (g['h'],g['a']): continue
        casa = g['h']==c; adv = g['a'] if casa else g['h']; v = 'casa' if casa else 'fora'; va = 'fora' if casa else 'casa'
        w,d,l = (g['pm'],g['pe'],g['pv']) if casa else (g['pv'],g['pe'],g['pm'])
        cruz.append(dict(id=f"{geral[c][0]}|{g['rodada']}|{geral[adv][0]}", clube=geral[c][0], rodada=g['rodada'], local='Casa' if casa else 'Fora', adversario=geral[adv][0],
          z_cria=round(Z[('xg',v)][0][c],2), z_cede=round(Z[('xga',v)][0][c],2),
          z_adv_cria=round(Z[('xg',va)][0][adv],2), z_adv_cede=round(Z[('xga',va)][0][adv],2),
          gols_esp_clube=g['xg_m'] if casa else g['xg_v'], gols_esp_adv=g['xg_v'] if casa else g['xg_m'],
          vitoria=w, empate=d, derrota=l, pts_esperados=round((3*w+d)/100,2)))

safe={}
for p in range(36,49):
    t_=ok=0
    for c in risco_:
        i=idx[c]; mk=pts[:,i]==p; t_+=mk.sum(); ok+=(~reb[mk,i]).sum()
    if t_>500: safe[p]=round(ok/t_*100,1)
z4=Counter(tuple(sorted(times[k] for k in row)) for row in ordem[:20000,-4:])
z4_top=[(list(geral[c][0] for c in k), round(v/200,1)) for k,v in z4.most_common(6)]
base_=reb.mean(axis=0); IMP=[]
for k_,(h_,a_,r_) in enumerate(GJ):
    g1_,g2_=GH[k_].astype(int),GA[k_].astype(int); t_=0
    for m_ in (g1_>g2_, g1_==g2_, g1_<g2_):
        if m_.mean()>0: t_+=m_.mean()*np.abs(reb[m_].mean(axis=0)-base_).sum()
    IMP.append((r_,h_,a_,k_,t_*100))
alvo=max([x for x in IMP if x[0]==min(y[0] for y in IMP)], key=lambda x:x[4])
COND_JOGO=(alvo[1],alvo[2]); kk=alvo[3]; g1_,g2_=GH[kk].astype(int),GA[kk].astype(int)
hw,dr,aw=g1_>g2_, g1_==g2_, g1_<g2_
viv=[c for c in times if 0.02<base_[idx[c]]<0.995]
cond={c: dict(cv=round(reb[hw,idx[c]].mean()*100,1), e=round(reb[dr,idx[c]].mean()*100,1), mv=round(reb[aw,idx[c]].mean()*100,1)) for c in sorted(viv,key=lambda c:-base_[idx[c]])}
json.dump(dict(jogo=COND_JOGO, imp=[dict(rodada=int(r_),mandante=geral[h_][0],visitante=geral[a_][0],indice=round(float(t_),1)) for (r_,h_,a_,k_,t_) in IMP]), open('importancia39.json','w'), ensure_ascii=False, indent=1)
json.dump(dict(clubes=clubes, jogos=prev, cruz=cruz, safe_curve=safe, z4=z4_top, cond=cond), open('resultado39.json','w'), ensure_ascii=False, indent=1)

for o in sorted([c for c in clubes if c['estudo']], key=lambda x:-x['rebaixamento']):
    print(f"   fase casa att {o['fv_casa_att']} def {o['fv_casa_def']} | fora att {o['fv_fora_att']} def {o['fv_fora_def']}"); print(f"{o['clube']:13s} {o['pontos']} reb v3 {o['reb_v3']:5.1f} v4 {o['rebaixamento']:5.1f} proj {o['pts_proj']} [{o['pts_p10']}-{o['pts_p90']}] "
          f"z cria C/F {o['z_xg_casa']}/{o['z_xg_fora']} cede C/F {o['z_xga_casa']}/{o['z_xga_fora']} GK {o['gols_evitados']} f{o['fator_goleiro']} fin {o['bonus_finalizadores']} f{o['fator_ataque']} | {o['melhor_finalizador']}")
for o in clubes:
    if not o['estudo']: print(f"  {o['clube']:13s} tit {o['tit_v3']}->{o['titulo']} top5 {o['top5']} proj {o['pts_proj']} [{o['pts_p10']}-{o['pts_p90']}] GK {o['gols_evitados']} f{o['fator_goleiro']} fin f{o['fator_ataque']}")
print(safe); print(z4_top); print(cond)
s={}
for x in cruz: s[x['clube']]=s.get(x['clube'],0)+x['pts_esperados']
print({k:round(v,1) for k,v in s.items()})

for g in prev: print(g['rodada'], g['mandante'], g['xg_m'], 'x', g['xg_v'], g['visitante'], '|', g['pm'], g['pe'], g['pv'], '|', g['placares'])

# ---- cenário típico: simulação com pontuação final mais próxima da mediana de cada clube
med = np.median(pts, axis=0)
dev = ((pts - med[None,:])**2).sum(axis=1).astype(float)
# desempate: também próximo do saldo mediano
dev += 0.05*((sg - np.median(sg,axis=0)[None,:])**2).sum(axis=1)
GHa=np.stack(GH); GAa=np.stack(GA)
extremo = ((GHa>=5)|(GAa>=5)|(np.abs(GHa.astype(int)-GAa.astype(int))>=4)).any(axis=0)
dev = np.where(extremo, np.inf, dev)
print('simulações sem placar extremo:', int((~extremo).sum()))
k = int(np.argmin(dev))
print('cenario', k, 'dev', dev[k])
cen = dict(jogos=[], tabelas=[])
tab = {c: dict(p=geral[c][1], j=geral[c][2], v=geral[c][3], e=geral[c][4], d=geral[c][5], gp=geral[c][6], gc=geral[c][7]) for c in times}
ordem_r = []
for (h,a,r) in GJ:
    if r not in ordem_r: ordem_r.append(r)
for rr in ordem_r:
    for gi,(h,a,r) in enumerate(GJ):
        if r != rr: continue
        x, y = int(GH[gi][k]), int(GA[gi][k])
        cen['jogos'].append(dict(rodada=r, mandante=geral[h][0], visitante=geral[a][0], gm=x, gv=y))
        for c, f, ag in ((h,x,y),(a,y,x)):
            t = tab[c]; t['j']+=1; t['gp']+=f; t['gc']+=ag
            if f>ag: t['p']+=3; t['v']+=1
            elif f==ag: t['p']+=1; t['e']+=1
            else: t['d']+=1
    ordc = sorted(times, key=lambda c: (-tab[c]['p'], -tab[c]['v'], -(tab[c]['gp']-tab[c]['gc']), -tab[c]['gp']))
    for i,c in enumerate(ordc,1):
        t=tab[c]; cen['tabelas'].append(dict(rodada=rr, pos=i, clube=geral[c][0], pontos=t['p'], jogos=t['j'], v=t['v'], e=t['e'], d=t['d'], gp=t['gp'], gc=t['gc'], sg=t['gp']-t['gc']))
json.dump(cen, open('cenario39.json','w'), ensure_ascii=False, indent=1)
for g in cen['jogos']: print(g['rodada'], g['mandante'], g['gm'], 'x', g['gv'], g['visitante'])
for t in cen['tabelas']:
    if t['rodada']==38: print(t['pos'], t['clube'], t['pontos'], t['v'], t['sg'])

# ---- probabilidades e placar a partir das simulações (já com motivação e incerteza)
from collections import Counter as _C
simj = []
for gi,(h,a,r) in enumerate(GJ):
    x = GH[gi].astype(int); y = GA[gi].astype(int)
    pm, pe, pv = (x>y).mean()*100, (x==y).mean()*100, (x<y).mean()*100
    res = 'm' if pm>=max(pe,pv) else ('e' if pe>=pv else 'v')
    msk = (x>y) if res=='m' else ((x==y) if res=='e' else (x<y))
    cnt = _C(zip(x[msk][:60000].tolist(), y[msk][:60000].tolist())).most_common(1)[0][0]
    pc = ((x==cnt[0])&(y==cnt[1])).mean()*100
    simj.append(dict(rodada=r, h=h, a=a, pm=round(pm,1), pe=round(pe,1), pv=round(pv,1), placar=f"{cnt[0]} x {cnt[1]}", prob_placar=round(pc,1), gm=round(x.mean(),2), gv=round(y.mean(),2)))
relax_rod = {geral[c][0]: relax_hist[c] for c in times}
json.dump(dict(simj=simj, relax=relax_rod, press={geral[c][0]: press_hist[c] for c in times}, ordem=ordem_rod), open('simj39.json','w'), ensure_ascii=False)
for c in ['Grêmio','Corinthians','Internacional','Mirassol','Coritiba','Vitória','Botafogo','Vasco','Bragantino','São Paulo','Santos','Remo','Chapecoense']:
    print(c, relax_rod[c])

json.dump(MOTD, open('motiv_p39.json','w'), ensure_ascii=False)

print('MOT_G', MOT_G); print('MOT_R', MOT_R)

# ---- amostra para o simulador interativo do painel (24/11)
NS = 10000
sim_out = dict(
    clubes=[dict(code=c, clube=geral[c][0], pontos=int(geral[c][1]), v=int(geral[c][3]), gp=int(geral[c][6]), gc=int(geral[c][7])) for c in times],
    jogos=[dict(rodada=int(r), h=h, a=a, mandante=geral[h][0], visitante=geral[a][0],
                pm=round(float((GH[gi]>GA[gi]).mean()*100),1), pe=round(float((GH[gi]==GA[gi]).mean()*100),1), pv=round(float((GH[gi]<GA[gi]).mean()*100),1))
           for gi,(h,a,r) in enumerate(GJ)],
    gh=[''.join(str(min(int(v),9)) for v in GH[gi][:NS]) for gi in range(len(GJ))],
    ga=[''.join(str(min(int(v),9)) for v in GA[gi][:NS]) for gi in range(len(GJ))],
    n=NS)
json.dump(sim_out, open('dash/simulador.json','w'), ensure_ascii=False, separators=(',',':'))
