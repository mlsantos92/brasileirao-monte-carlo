import json,math,statistics as st
D=json.load(open('gk_raw.json'))
MAP={'Athletico Paranaense':'Athletico-PR','RB Bragantino':'Bragantino','Vasco da Gama':'Vasco'}
m=lambda t:MAP.get(t,t)
f1=lambda x:f"{x:.1f}".replace('.',','); sg=lambda x:('+' if x>0.05 else '−' if x<-0.05 else '')+f1(abs(x))
n,X,G=D['T']['np']; kNP=G/X
pn,pg,psv,poff,pxgot=D['T']['pen']; kP=pg/pxgot  # pênaltis no alvo: xGOT subestima conversão
rows=[]
for t,nm,j,nn,x,v,g,xg,p_n,p_g,p_sv,p_off,p_x in D['K']:
    adj=kNP*x-g; se=kNP*math.sqrt(v); padj=kP*p_x-p_g
    rows.append(dict(clube=m(t),jogador=nm,jogos=j,chutes=nn,xgot=round(x,1),sofridos=g,bruto=round(x-g,1),ajust=adj,se=se,pen_n=p_n,pen_g=p_g,pen_def=p_sv,pen_fora=p_off,pen_mer=round(padj,1)))
# empirical Bayes sobre o mérito por unidade de xGOT
big=[r for r in rows if r['chutes']>=40]
rate=[r['ajust']/r['xgot'] for r in big]; nv=[(r['se']/r['xgot'])**2 for r in big]
tau2=max(1e-6, st.pvariance(rate)-st.mean(nv)); print('tau',math.sqrt(tau2),'sd obs',st.pstdev(rate),'noise',math.sqrt(st.mean(nv)))
for r in rows:
    b=tau2/(tau2+(r['se']/r['xgot'])**2) if r['xgot']>0 else 0
    r['peso']=round(b,2); r['encolhido']=round(r['ajust']*b,1); r['ajust']=round(r['ajust'],1); r['faixa']=round(1.64*r['se'],1)
    r['final']=round(r['encolhido']+r['pen_mer']*b,1)
    r['sig']= abs(r['ajust'])>r['faixa']
rows.sort(key=lambda r:-r['final'])
for r in rows[:8]+rows[-6:]: print(r['clube'],r['jogador'],r['chutes'],r['bruto'],r['ajust'],'±',r['faixa'],r['peso'],r['encolhido'],'pen',r['pen_def'],'/',r['pen_n'],r['pen_mer'],'final',r['final'])
json.dump(dict(rows=rows,kNP=kNP,kP=kP,pens=D['P'],tot=D['T']),open('gk2.json','w'),ensure_ascii=False)
