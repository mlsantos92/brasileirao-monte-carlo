import json,re,sys
B=sys.argv[1]; SIM=sys.argv[2]
RES=json.loads(sys.argv[3]); EXCL=set(json.loads(sys.argv[4])); JOGARAM=set(json.loads(sys.argv[5])); TIRAR_LUTA=set(json.loads(sys.argv[6]))
P={'V':3,'E':1,'D':0}; tok=lambda s: re.findall(r'\[[VED]\]|[VED]',s)
old={c['clube']:c for c in json.load(open(B+'clubes.json'))}
cl=json.load(open('dash/clubes.json'))
for c in cl:
    for k in ['relax_38','ppg5','seq5','ppg_casa3','seq_casa3','ppg_fora3','seq_fora3']: c[k]=old[c['clube']][k]
up={}
for h,a,x,y in RES:
    up[h]=('V' if x>y else 'E' if x==y else 'D','casa'); up[a]=('V' if y>x else 'E' if x==y else 'D','fora')
for c in cl:
    if c['clube'] in up:
        r,m=up[c['clube']]
        for campo,n in (('5',5),('_'+m+'3',3)):
            t=(tok(c['seq'+campo])+[r])[-n:]; c['seq'+campo]=''.join(t); c['ppg'+campo]=round(sum(P[x.strip('[]')] for x in t)/len(t),2)
json.dump(cl,open('dash/clubes.json','w'),ensure_ascii=False)
oj={j['jogo']:j for j in json.load(open(B+'jogos.json'))}
jg=json.load(open('dash/jogos.json'))
def filt(s): return '; '.join(x for x in s.split('; ') if x and not (' sem ' in x and x.split(' sem ')[0] in TIRAR_LUTA))
for j in jg:
    o=oj[j['jogo']]; j['desc_mandante'],j['desc_visitante']=o['desc_mandante'],o['desc_visitante']; j['obs_descanso']=filt(o['obs_descanso'])
json.dump(jg,open('dash/jogos.json','w'),ensure_ascii=False)
d=[x for x in json.load(open(B+'desfalques.json')) if x['id'] not in EXCL and x['clube'] not in TIRAR_LUTA]
for x in d:
    if x['clube'] in JOGARAM:
        m=re.match(r'(\d+) de (\d+)',x['jogos_fora'])
        if m:
            a,n=int(m[1]),int(m[2]); a=max(0,a-1); x['jogos_fora']=f'{a} de {n-1}'; x['n_jogos']=a
        else: print('??',x['jogador'],x['jogos_fora'])
json.dump(d,open('dash/desfalques.json','w'),ensure_ascii=False)
sj=json.load(open(f'simj{SIM}.json')); mot=[]
for clube,vals in sj['relax'].items():
    row=dict(clube=clube)
    for rr,v in zip(sj['ordem'],vals): row[f"r{rr}"]=v
    mot.append(row)
mot.sort(key=lambda x:-x[f"r{sj['ordem'][-1]}"]); json.dump(mot,open('dash/motivacao.json','w'),ensure_ascii=False)
json.dump(json.load(open(f'motiv_p{SIM}.json')),open('dash/motiv_detalhe.json','w'),ensure_ascii=False)
oc=json.load(open(B+'caminho.json'))
jgk={(j['mandante'],j['visitante']):j for j in jg}
cj={(c['mandante'],c['visitante']):c for c in json.load(open('dash/cen_jogos.json'))}
tb=json.load(open('dash/cen_tabela.json')); R=max(t['rodada'] for t in tb)
fin={t['clube']:t for t in tb if t['rodada']==R}; clm={c['clube']:c for c in cl}
new=[]
for c in oc:
    x=dict(c); C=c['clube']; A=c['adversario']; k=(C,A) if c['local']=='C' else (A,C)
    if k not in jgk: continue
    j=jgk[k]; s=cj[k]; gm,gv=[int(v) for v in s['placar'].split(' x ')]
    g,ga=(gm,gv) if c['local']=='C' else (gv,gm)
    x['placar']=f'{g}x{ga}'; x['resultado']='V' if g>ga else 'E' if g==ga else 'D'
    if c['local']=='C': x['p_vit'],x['p_emp'],x['p_der']=j['p_mandante'],j['p_empate'],j['p_visitante']
    else: x['p_vit'],x['p_emp'],x['p_der']=j['p_visitante'],j['p_empate'],j['p_mandante']
    x['obs']=j['obs_descanso']; x['pts_final']=fin[C]['pontos']; x['pos_final']=fin[C]['pos']; x['risco']=clm[C]['rebaixamento']; x['pts_atual']=clm[C]['pontos']
    new.append(x)
json.dump(new,open('dash/caminho.json','w'),ensure_ascii=False)
print('jogos',len(jg),'caminho',len(new),'desf',len(d))
print(sorted(set((c['clube'],c['pts_final'],c['pos_final']) for c in new),key=lambda t:t[2]))
e=json.load(open('dash/evolucao.json')); ev=set(x['clube'] for x in e)
for c in cl:
    if c['clube'] in up and c['clube'] in ev:
        last=max(x['jogo'] for x in e if x['clube']==c['clube'])
        e.append(dict(id=f"{c['clube']}|{last+1}",clube=c['clube'],jogo=last+1,pontos=c['pontos'])); print(c['clube'],last+1,c['pontos'])
json.dump(e,open('dash/evolucao.json','w'),ensure_ascii=False)
