import json
R=json.load(open('xa_raw.json'))
for t,o in sorted(R.items(), key=lambda kv: kv[1]['a']-kv[1]['xa']):
    pxg=o['xg']-o['npxg']; ind_g=o['g']-o['pen']-o['a']; ind_x=o['npxg']-o['xa']
    print(f"{t:22s} A {o['a']:2d} xA {o['xa']:5.1f} d {o['a']-o['xa']:+5.1f} | ind {ind_g:2d} x {ind_x:5.1f} d {ind_g-ind_x:+5.1f} | pen {o['pen']} x {pxg:4.1f} | npG-npxG {o['g']-o['pen']-o['npxg']:+5.1f} | xA/npxG {o['xa']/o['npxg']:.2f} cc {o['cc']}")
