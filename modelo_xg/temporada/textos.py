import json
A=json.load(open('temporada/analise.json')); tab=A['tab']
cl={c['clube']:c for c in json.load(open('dash/clubes.json'))}
jg=json.load(open('dash/jogos.json'))
f1=lambda x: f"{x:.1f}".replace('.',',')
f2=lambda x: f"{x:.2f}".replace('.',',')
def sg(x): return ('+' if x>0 else '−' if x<0 else '')+f1(abs(x))
out=[]
for r in tab:
    c=r['clube']; m=cl[c]
    dif=r['pts']-r['xpts']; at=r['gp']-r['xg']; de=r['xga']-r['gc']
    d=[]
    d.append(f"{r['pos']}º com {r['pts']} pontos. Pelo volume de chances que cria e cede (xG), somaria {f1(r['xpts'])} pontos, o que o colocaria em {r['pos_xpts']}º.")
    causas=[]
    if abs(at)>=4: causas.append(f"marcou {abs(at):.0f} gols {'a mais' if at>0 else 'a menos'} do que as chances indicavam ({r['gp']} gols para {f1(r['xg'])} de xG)")
    if abs(de)>=4: causas.append(f"sofreu {abs(de):.0f} gols {'a menos' if de>0 else 'a mais'} do que o esperado ({r['gc']} para {f1(r['xga'])} de xG contra){', sinal de goleiro e defesa decisivos' if de>0 else ', o que aponta goleiro abaixo ou erros individuais'}")
    if dif<=-4:
        d.append(f"Tem {abs(dif):.0f} pontos a menos do que o desempenho justificaria" + (": " + " e ".join(causas) + "." if causas else ", por detalhes espalhados em vários jogos."))
    elif dif>=4:
        d.append(f"Tem {dif:.0f} pontos a mais do que o desempenho justificaria" + (": " + " e ".join(causas) + "." if causas else ", vencendo jogos equilibrados."))
    else:
        d.append("A pontuação condiz com o que o time produz em campo." + (" Por baixo disso há dois desvios que se compensam: " + "; e ".join(causas) + "." if len(causas)==2 else (" Destaque: " + causas[0] + "." if causas else "")))
    if abs(r['ppg_casa']-r['ppg_fora'])>=0.8:
        d.append(f"Depende muito do mando: {f2(r['ppg_casa'])} pontos por jogo em casa contra {f2(r['ppg_fora'])} fora.")
    tr=r['ppg_t2']-r['ppg_t1']; trx=r['xgd_t2']-r['xgd_t1']
    if abs(tr)>=0.35:
        d.append(f"{'Melhorou' if tr>0 else 'Caiu'} na segunda metade: {f2(r['ppg_t1'])} pontos por jogo nos 19 primeiros jogos e {f2(r['ppg_t2'])} depois" + (f", acompanhado do saldo de xG ({sg(r['xgd_t1'])} para {sg(r['xgd_t2'])} por jogo)." if (trx>0)==(tr>0) and abs(trx)>=0.2 else ", sem mudança equivalente no saldo de xG, o que sugere parte de sorte." if abs(trx)<0.2 else f", embora o saldo de xG tenha ido no sentido contrário ({sg(r['xgd_t1'])} para {sg(r['xgd_t2'])})."))
    u=r['ppg_u10']-r['xppg_u10']
    d.append(f"Nos últimos 10 jogos: {f2(r['ppg_u10'])} pontos por jogo, para {f2(r['xppg_u10'])} esperados pelo xG" + (", acima do que produziu." if u>=0.3 else ", abaixo do que produziu." if u<=-0.3 else ", em linha com o desempenho."))
    # perspectiva
    p=[]
    rest=[j for j in jg if c in (j['mandante'],j['visitante'])]
    def lado(j):
        casa=j['mandante']==c; adv=j['visitante'] if casa else j['mandante']
        w=j['p_mandante'] if casa else j['p_visitante']; e=j['p_empate']
        return f"{adv} ({'casa' if casa else 'fora'}, {w:.0f}% de vitória)", (3*w+e)/100
    if rest:
        L=[lado(j) for j in rest]
        p.append(f"Faltam {len(rest)} jogos: " + ", ".join(x[0] for x in L) + f". Pontos esperados: {f1(sum(x[1] for x in L))}.")
    p.append(f"Projeção de {m['pts_proj']} pontos (entre {m['pts_p10']} e {m['pts_p90']} em 80% das simulações).")
    if m['titulo']>=99.5: p.append("Campeão.")
    elif m['titulo']>0: p.append(f"Chance de título: {f1(m['titulo'])}%.")
    if 0<m['top5']<100 or (m['top5']==100 and m['titulo']<99.5 and r['pos']<=5): p.append(f"Chance de terminar no top 5: {f1(m['top5'])}%.")
    if m['rebaixamento']>=99.5: p.append("Rebaixado em todas as simulações.")
    elif m['rebaixamento']>0: p.append(f"Chance de queda: {f1(m['rebaixamento'])}%.")
    elif r['pos']>=10: p.append("Sem risco de queda nas simulações.")
    if dif<=-4 and rest: p.append("O desempenho é melhor que a pontuação, então o modelo dá a ele chances acima do que a tabela sugere; com tão poucos jogos, porém, a recuperação conta pouco.")
    if dif>=4 and m['rebaixamento']>0: p.append("Como pontuou acima do que produz, o modelo não conta com a mesma eficiência daqui para frente.")
    out.append(dict(r, xpts_dif=round(dif,1), dif_ataque=round(at,1), dif_defesa=round(de,1), queda=m['rebaixamento'], titulo=m['titulo'], top5=m['top5'],
        pts_proj=m['pts_proj'], pts_p10=m['pts_p10'], pts_p90=m['pts_p90'], diagnostico=" ".join(d), perspectiva=" ".join(p)))
json.dump(out,open('dash/raiox.json','w'),ensure_ascii=False)
bt=A['bt']
res=[dict(metrica='Jogos do campeonato', modelo=bt['n'], unif=None, freq=None, descricao='Todos os jogos disputados até 23/11 (rodadas 1 a 36 e jogos adiados), com xG do FotMob.'),
 dict(metrica='Acerto do resultado (%)', modelo=bt['acerto'], unif=33.3, freq=bt['acerto_mandante'], descricao='% de jogos em que o resultado mais provável pelo perfil dos clubes aconteceu. Referência: apostar sempre no mandante.'),
 dict(metrica='Brier score (menor é melhor)', modelo=bt['brier'], unif=bt['brier_unif'], freq=bt['brier_freq'], descricao=f"Referência da frequência: {f1(bt['freq'][0])}% mandante, {f1(bt['freq'][1])}% empate, {f1(bt['freq'][2])}% visitante para todo jogo."),
 dict(metrica='Log loss (menor é melhor)', modelo=bt['logloss'], unif=1.099, freq=None, descricao='Penaliza mais quando o modelo dá pouca chance ao que aconteceu.')]
json.dump(res,open('dash/raiox_bt.json','w'),ensure_ascii=False)
for o in out:
    if o['clube'] in ('Internacional','Grêmio','Corinthians','Coritiba','Flamengo'): print(o['clube'],'\n ',o['diagnostico'],'\n ',o['perspectiva'])
