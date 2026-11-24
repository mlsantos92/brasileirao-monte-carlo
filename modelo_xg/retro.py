import json, os, re, datetime as dt, ast
src=open('sim37.py').read()
m=re.search(r"RES33 = (\[.*?\])\s*#", src, re.S)
txt=re.sub(r"#[^\n]*","",m.group(1))
RES=ast.literal_eval(txt)
real={(h,a):(x,y) for h,a,x,y in RES}
nome=json.load(open('resultado37.json'))
vers=[v for v in range(13,38) if os.path.exists(f'simj{v}.json') and os.path.exists(f'resultado{v}.json')]
def quando(v):
    t=dt.datetime.utcfromtimestamp(os.path.getmtime(f'resultado{v}.json'))-dt.timedelta(hours=3)
    return t
import desf
DJ={k:dt.datetime.fromisoformat(v.replace('Z','')) for k,v in desf.DATA_JOGO.items()}
for k,d in {('mirassol','atletico-mg'):'11-14',('chapecoense','vasco'):'11-14',('coritiba','santos'):'11-18',('remo','chapecoense'):'11-18',('cruzeiro','palmeiras'):'11-18',('flamengo','athletico-pr'):'11-18',
  ('corinthians','botafogo'):'11-19',('gremio','bahia'):'11-19',('vasco','internacional'):'11-19',('vitoria','bragantino'):'11-19',('sao-paulo','fluminense'):'11-20',('palmeiras','flamengo'):'11-21',('bahia','coritiba'):'11-21',
  ('chapecoense','cruzeiro'):'11-22',('athletico-pr','remo'):'11-22',('fluminense','mirassol'):'11-22',('bragantino','vasco'):'11-22',('santos','gremio'):'11-23',('internacional','vitoria'):'11-23',('botafogo','sao-paulo'):'11-23'}.items():
    DJ.setdefault(k, dt.datetime.fromisoformat('2026-'+d+'T15:00:00'))
utc=lambda v: dt.datetime.utcfromtimestamp(os.path.getmtime(f'resultado{v}.json'))
ult={}   # (h,a) -> (v, simj row)
nomes={}
for v in vers:
    r=json.load(open(f'resultado{v}.json'))
    for j in r['jogos']: nomes[(j['h'],j['a'])]=(j['mandante'],j['visitante'])
    for s in json.load(open(f'simj{v}.json'))['simj']:
        k=(s['h'],s['a'])
        if k in real and utc(v) < DJ[k]: ult[k]=(v,s)
rows=[]
for k,(v,s) in ult.items():
    x,y=real[k]; res='m' if x>y else ('e' if x==y else 'v')
    p={'m':s['pm']/100,'e':s['pe']/100,'v':s['pv']/100}
    fav=max(p,key=p.get)
    brier=sum((p[o]-(1 if o==res else 0))**2 for o in 'mev')
    import math
    m_,v_=nomes[k]
    rows.append(dict(id=f"{m_} x {v_}", rodada=s['rodada'], jogo=f"{m_} x {v_}", previsao_em=quando(v).strftime('%d/%m %H:%M'), versao=v,
        p_mandante=s['pm'], p_empate=s['pe'], p_visitante=s['pv'],
        favorito={'m':m_,'e':'Empate','v':v_}[fav], placar_previsto=s['placar'], placar_real=f"{x} x {y}",
        resultado={'m':m_,'e':'Empate','v':v_}[res], prob_resultado=round(p[res]*100,1),
        acertou='Sim' if fav==res else 'Não', acertou_placar='Sim' if s['placar']==f"{x} x {y}" else 'Não',
        brier=round(brier,3), logloss=round(-math.log(max(p[res],1e-4)),3)))
rows.sort(key=lambda r:(r['rodada'],r['jogo']))
n=len(rows)
import statistics as st
freq={o:sum(1 for r in rows if (r['resultado']==r['jogo'].split(' x ')[0] if o=='m' else (r['resultado']=='Empate' if o=='e' else r['resultado']==r['jogo'].split(' x ')[1])))/n for o in 'mev'}
def brier_const(q):
    t=0
    for r in rows:
        res='m' if r['resultado']==r['jogo'].split(' x ')[0] else ('e' if r['resultado']=='Empate' else 'v')
        t+=sum((q[o]-(1 if o==res else 0))**2 for o in 'mev')
    return t/n
import math
def ll_const(q):
    t=0
    for r in rows:
        res='m' if r['resultado']==r['jogo'].split(' x ')[0] else ('e' if r['resultado']=='Empate' else 'v')
        t+=-math.log(q[res])
    return t/n
uni={'m':1/3,'e':1/3,'v':1/3}
acc=sum(r['acertou']=='Sim' for r in rows)/n
acc_m=freq['m']   # "sempre mandante"
res_rows=[
 dict(metrica='Jogos avaliados', modelo=n, ingenuo=None, mandante=None, descricao='Jogos disputados desde a primeira simulação (33ª rodada em diante), com a última previsão feita antes de cada jogo.'),
 dict(metrica='Acerto do resultado (%)', modelo=round(acc*100,1), ingenuo=33.3, mandante=round(acc_m*100,1), descricao='% de jogos em que o resultado mais provável (vitória do mandante, empate ou do visitante) aconteceu. Na referência da amostra, aposta-se sempre no resultado mais comum (vitória do mandante).'),
 dict(metrica='Brier score (menor é melhor)', modelo=round(sum(r['brier'] for r in rows)/n,3), ingenuo=round(brier_const(uni),3), mandante=round(brier_const(freq),3), descricao='Erro quadrático das três probabilidades contra o que aconteceu (0 = perfeito, 0,667 = chutar 1/3 para tudo). A referência da amostra usa para todo jogo as frequências reais destes jogos ('+f"{freq['m']*100:.0f}% mandante, {freq['e']*100:.0f}% empate, {freq['v']*100:.0f}% visitante"+'), um adversário difícil porque já conhece o resultado.'),
 dict(metrica='Log loss (menor é melhor)', modelo=round(sum(r['logloss'] for r in rows)/n,3), ingenuo=round(ll_const(uni),3), mandante=round(ll_const(freq),3), descricao='Penaliza mais quando o modelo dá pouca chance ao que aconteceu.'),
 dict(metrica='Placar exato (%)', modelo=round(sum(r['acertou_placar']=='Sim' for r in rows)/n*100,1), ingenuo=None, mandante=None, descricao='% de jogos em que o placar mais provável do modelo foi o placar real.'),
]
# calibração
faixas=[(0,20),(20,35),(35,50),(50,65),(65,101)]
cal=[]
for lo,hi in faixas:
    ps=[];hs=[]
    for r in rows:
        res='m' if r['resultado']==r['jogo'].split(' x ')[0] else ('e' if r['resultado']=='Empate' else 'v')
        for o,key in (('m','p_mandante'),('e','p_empate'),('v','p_visitante')):
            if lo<=r[key]<hi: ps.append(r[key]); hs.append(1 if o==res else 0)
    if ps: cal.append(dict(faixa=f"{lo}–{min(hi,100)}%", previsto=round(sum(ps)/len(ps),1), real=round(sum(hs)/len(hs)*100,1), n=len(ps)))
# evolução da chance de queda
evo=[]
ultimo_do_dia={}
for v in vers: ultimo_do_dia[quando(v).date()]=v
for v in sorted(ultimo_do_dia.values()):
    r=json.load(open(f'resultado{v}.json'))
    for c in r['clubes']:
        if c['code'] in ('internacional','gremio','corinthians','mirassol','vitoria','botafogo','coritiba','vasco'):
            evo.append(dict(id=f"{v}|{c['clube']}", versao=v, data=quando(v).strftime('%d/%m'), clube=c['clube'], queda=c['rebaixamento']))
json.dump(rows,open('dash/retro_jogos.json','w'),ensure_ascii=False)
json.dump(res_rows,open('dash/retro_resumo.json','w'),ensure_ascii=False)
json.dump(cal,open('dash/retro_calib.json','w'),ensure_ascii=False)
json.dump(evo,open('dash/retro_queda.json','w'),ensure_ascii=False)
print(n, freq); [print(x) for x in res_rows]; [print(x) for x in cal]
print(sorted(set((r['versao'],r['previsao_em']) for r in rows)))
missing=[k for k in real if k not in ult]; print('sem previsão:',missing)
