# Desfalques: lesionados, suspensos e dúvidas (FotMob, 27/10/2026) + Viveros (dúvida, joelho; imprensa 26/10)
# Gera, para cada jogo restante, um fator de ataque (<=1) e de defesa (>=1) por clube.
from datetime import datetime, timezone

NOME = {'Athletico Paranaense':'athletico-pr','Atlético-MG':'atletico-mg','Bahia':'bahia','Botafogo':'botafogo',
 'Chapecoense':'chapecoense','Corinthians':'corinthians','Coritiba':'coritiba','Cruzeiro':'cruzeiro','Flamengo':'flamengo',
 'Fluminense':'fluminense','Grêmio':'gremio','Internacional':'internacional','Mirassol':'mirassol','Palmeiras':'palmeiras',
 'RB Bragantino':'bragantino','Remo':'remo','Santos':'santos','São Paulo':'sao-paulo','Vasco da Gama':'vasco','Vitória':'vitoria'}

def D(s): return datetime.fromisoformat(s.replace('Z','+00:00'))

# datas dos jogos restantes (FotMob); Chapecoense x Vasco (adiado) remarcado para 14/11
DATAS_ROD = {33: None, 34: None, 35: '2026-11-18T00:00:00Z', 36: '2026-11-21T00:00:00Z', 37: '2026-11-28T00:00:00Z', 38: '2026-12-02T00:00:00Z'}
DATA_JOGO = {
 ('fluminense','internacional'):'2026-10-28T22:30:00Z',('bragantino','chapecoense'):'2026-10-28T22:30:00Z',('santos','palmeiras'):'2026-10-28T22:30:00Z',
 ('bahia','sao-paulo'):'2026-10-29T00:30:00Z',('remo','botafogo'):'2026-10-29T00:30:00Z',('atletico-mg','cruzeiro'):'2026-10-29T22:30:00Z',
 ('vasco','flamengo'):'2026-10-29T23:00:00Z',('gremio','athletico-pr'):'2026-10-30T00:30:00Z',('corinthians','mirassol'):'2026-10-30T23:00:00Z',
 ('coritiba','vitoria'):'2026-10-31T19:00:00Z',
 ('bragantino','santos'):'2026-11-02T23:00:00Z',('chapecoense','mirassol'):'2026-11-03T22:30:00Z',('internacional','coritiba'):'2026-11-04T00:30:00Z',
 ('athletico-pr','vasco'):'2026-11-04T22:30:00Z',('flamengo','gremio'):'2026-11-04T22:30:00Z',('botafogo','atletico-mg'):'2026-11-05T00:30:00Z',
 ('sao-paulo','corinthians'):'2026-11-05T00:30:00Z',('palmeiras','remo'):'2026-11-05T22:30:00Z',('cruzeiro','bahia'):'2026-11-06T00:30:00Z',
 ('vitoria','fluminense'):'2026-11-06T23:00:00Z',('chapecoense','vasco'):'2026-11-14T23:30:00Z'}

def data_jogo(h, a, r):
    if (h,a) in DATA_JOGO: return D(DATA_JOGO[(h,a)])
    return D(DATAS_ROD[r])

# retorno previsto -> data a partir da qual o jogador volta a estar disponível
RET = {'Late October 2026':'2026-11-01T00:00:00Z', 'About a week':'2026-11-03T12:00:00Z', 'About 1-2 weeks':'2026-11-07T00:00:00Z',
       'Early November 2026':'2026-11-10T00:00:00Z', 'Mid November 2026':'2026-11-20T00:00:00Z', 'Late November 2026':'2026-11-30T00:00:00Z', 'A few weeks':'2026-11-25T00:00:00Z', 'A few days':'2026-11-07T00:00:00Z',
       'Early December 2026':'2027-01-01T00:00:00Z', 'Mid December 2026':'2027-01-01T00:00:00Z', 'Late December 2026':'2027-01-01T00:00:00Z',
       'Out for season':'2027-01-01T00:00:00Z'}
PRIMEIRO_JOGO = {}   # 1º jogo de cada clube (dúvidas e "voltando aos treinos" afetam só ele)

# peso defensivo por posição (aumento de gols sofridos por titular absoluto ausente) - premissa
DEF_POS = {'keeper_long':0.06, 'centerback':0.04, 'rightback':0.03, 'leftback':0.03, 'right_wing_back':0.03, 'left_wing_back':0.03,
           'centerdefensivemidfielder':0.03, 'centermidfielder':0.015}
REPOSICAO = 0.5      # o substituto entrega metade da contribuição ofensiva do titular
CAP_ATT, CAP_DEF = 0.25, 0.15

def carregar(geral, A, arq='desfalques.txt'):
    """A: agregados por (clube, mando) com xg e j (ponderados) -> xG bruto estimado da temporada"""
    jog = []
    for l in open(arq):
        t,p,tipo,ret,retd,pos,mins,rat,npxg,xa,rec = l.rstrip('\n').split('|')
        c = NOME[t]; jj = geral[c][2]
        xg_rate = (A[(c,'casa')]['xg']+A[(c,'fora')]['xg'])/(A[(c,'casa')]['j']+A[(c,'fora')]['j'])
        tot_att = xg_rate*jj*1.6                       # npxG do time + 0.8 x xA (≈0,75 do xG)
        mins, rat, npxg, xa, rec = float(mins), float(rat), float(npxg), float(xa), float(rec)
        share_att = (npxg + 0.8*xa)/tot_att
        share_min = mins/(jj*90)
        pres = max(rec/720, 0.3)                       # presença nos últimos 8 jogos (piso 0,3: a temporada ainda o inclui)
        fr = min(1.5, max(0.5, 1 + (rat - 6.8))) if rat > 0 else 0.5
        att = REPOSICAO*share_att*pres
        dfn = DEF_POS.get(pos, 0.0)*share_min*pres*fr
        if ret == 'Doubtful': modo, prob = 'primeiro', 0.5
        elif ret == 'Back in training': modo, prob = 'primeiro', 0.25
        elif tipo == 'suspension' and retd: modo, prob = 'ate', 1.0
        elif tipo == 'suspension': modo, prob = 'primeiro', 1.0     # suspenso sem data: cumpre no próximo jogo
        elif tipo == 'stjd': modo, prob = 'lista', 1.0                 # julgamento no STJD: chance de ficar fora em cada um dos próximos jogos
        else: modo, prob = 'ate', 1.0
        ate = D(retd) if (tipo=='suspension' and retd) else (D(RET[ret]) if ret in RET else None)
        probs = [float(x) for x in ret.split('/')] if tipo == 'stjd' else None
        if tipo == 'stjd': ate = None
        jog.append(dict(clube=c, time=t, jogador=p, tipo=tipo, retorno=ret, probs=probs, nota_stjd=retd if tipo=='stjd' else '', pos=pos, minutos=int(mins), nota=rat, npxg=npxg, xa=xa,
                        share_att=share_att, pres=pres, att=att, dfn=dfn, modo=modo, prob=prob, ate=ate))
    return jog

def fatores(jog, jogos):
    """retorna {(h,a,r): {clube: (fator_ataque, fator_defesa, [jogadores fora])}}"""
    prim = {}
    for (h,a,r) in sorted(jogos, key=lambda x: data_jogo(*x)):
        for c in (h,a): prim.setdefault(c, (h,a,r))
    ordem = {}
    for (h,a,r) in sorted(jogos, key=lambda x: data_jogo(*x)):
        for c in (h,a): ordem.setdefault(c, []).append((h,a,r))
    out = {}
    for (h,a,r) in jogos:
        dt = data_jogo(h,a,r); res = {}
        for c in (h,a):
            la, ld, nomes = 0.0, 0.0, []
            for p in jog:
                if p['clube'] != c: continue
                if p['modo'] == 'primeiro': w = p['prob'] if prim[c] == (h,a,r) else 0.0
                elif p['modo'] == 'lista':
                    k_ = ordem[c].index((h,a,r)); w = p['probs'][k_] if k_ < len(p['probs']) else 0.0
                else: w = 1.0 if (p['ate'] is not None and dt <= p['ate']) else 0.0
                if w <= 0: continue
                la += w*p['att']; ld += w*p['dfn']
                if p['att'] + p['dfn'] >= 0.005: nomes.append(p['jogador'] + (' (dúvida)' if p['modo']=='primeiro' else ''))
            res[c] = (1 - min(la, CAP_ATT), 1 + min(ld, CAP_DEF), nomes)
        out[(h,a,r)] = res
    return out
