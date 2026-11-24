# Forma das últimas 2 semanas (18/10 a 01/11, FotMob): xG criado/cedido e pontos vs a média do clube na temporada
K_REC = 3.0                 # jogos "fantasmas" na média da temporada (encolhimento: amostra de 2-3 jogos)
E_XG, E_PPG = 0.5, 0.10     # expoentes (peso adicional da fase recente)
LIM = (0.85, 1.18)
NOME = {'Athletico Paranaense':'athletico-pr','Atlético-MG':'atletico-mg','Bahia':'bahia','Botafogo':'botafogo','Chapecoense':'chapecoense',
 'Corinthians':'corinthians','Coritiba':'coritiba','Cruzeiro':'cruzeiro','Flamengo':'flamengo','Fluminense':'fluminense','Grêmio':'gremio',
 'Internacional':'internacional','Mirassol':'mirassol','Palmeiras':'palmeiras','RB Bragantino':'bragantino','Remo':'remo','Santos':'santos',
 'São Paulo':'sao-paulo','Vasco da Gama':'vasco','Vitória':'vitoria','Torque':'torque','Boca Juniors':'boca','Estudiantes':'estudiantes'}
ULT = None   # (casa, fora): se definido, usa só os últimos N jogos em casa e N fora de cada clube, em todas as competições
def fatores(A, geral, arq='recente.txt', inicio=None):
    inicio = inicio or {}
    R = {}
    linhas = [l for l in open(arq) if l.strip()]
    if ULT:
        por = {}
        for l in linhas:
            f_ = l.strip().split('|'); dt,h,a = f_[1],f_[2],f_[3]
            so = set(f_[8].split(',')) if len(f_) > 8 and f_[8] else None
            for c,lado in ((NOME[h],'casa'),(NOME[a],'fora')):
                if so is not None and c not in so: continue
                por.setdefault((c,lado),[]).append((dt,l))
        keep = {}
        for (c,lado),lst in por.items():
            lst.sort(key=lambda t:t[0], reverse=True)
            for dt,l in lst[:ULT[0] if lado=='casa' else ULT[1]]: keep.setdefault(l,set()).add(c)
        linhas = [l for l in linhas if l in keep]
    for l in linhas:
        f_ = l.strip().split('|'); rd,dt,h,a,sc,xh,xa,red = f_[:8]; gh,ga = map(int, sc.split(' - ')); w = 0.5 if red=='1' else 1.0
        so = set(f_[8].split(',')) if len(f_) > 8 and f_[8] else None      # jogos de copa: só para o clube ainda vivo na competição
        if len(f_) > 9: w *= float(f_[9])                         # peso menor quando não há xG (gols no lugar) ou rival estrangeiro
        for c,xf,xc,gf,gc in ((NOME[h],float(xh),float(xa),gh,ga),(NOME[a],float(xa),float(xh),ga,gh)):
            if dt < inicio.get(c, '0000'): continue     # só jogos com o técnico atual
            if c not in NOME.values(): continue
            if so is not None and c not in so: continue
            if ULT and c not in keep.get(l,()): continue
            r = R.setdefault(c, dict(n=0.0,xf=0.0,xc=0.0,p=0.0,jogos=[]))
            r['n']+=w; r['xf']+=w*xf; r['xc']+=w*xc; r['p']+=w*(3 if gf>gc else 1 if gf==gc else 0)
            r['jogos'].append(f"{h} {sc} {a}")
    out = {}
    for c in geral:
        T = {k: A[(c,'casa')][k]+A[(c,'fora')][k] for k in ('xg','xga','j')}
        sx, sc_ = T['xg']/T['j'], T['xga']/T['j']
        ppg = geral[c][1]/geral[c][2]
        r = R.get(c, dict(n=0,xf=0,xc=0,p=0,jogos=[]))
        n = r['n']
        rx = (r['xf'] + K_REC*sx)/(n+K_REC)/sx
        rc = (r['xc'] + K_REC*sc_)/(n+K_REC)/sc_
        rp = ((r['p'] + K_REC*ppg)/(n+K_REC) + 0.5)/(ppg + 0.5)
        fa = min(LIM[1], max(LIM[0], rx**E_XG * rp**E_PPG))
        fd = min(LIM[1], max(LIM[0], rc**E_XG / rp**E_PPG))
        out[c] = dict(att=fa, def_=fd, n=n, xf=r['xf']/n if n else None, xc=r['xc']/n if n else None, ppg=r['p']/n if n else None,
                      xf_temp=sx, xc_temp=sc_, ppg_temp=ppg, jogos=r['jogos'])
    # normaliza: a média geométrica da liga fica em 1 (a fase recente redistribui força, não muda o nível de gols)
    import math
    ga = math.exp(sum(math.log(v['att']) for v in out.values())/len(out)); gd = math.exp(sum(math.log(v['def_']) for v in out.values())/len(out))
    for v in out.values(): v['att']/=ga; v['def_']/=gd
    return out
