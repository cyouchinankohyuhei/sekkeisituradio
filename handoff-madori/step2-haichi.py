# 2F座標を基準（1F = 2F - 910）。y=0 が図の上端、下向き正。単位mm
S=0.05; M=60; W=19565
floors = {
 "2F": [
  ("撮影スペース",0,4550,0,4550,"room"),
  ("階段(記入漏れ・推定)",910,2730,3640,4550,"stair"),
  ("和室8帖",4550,8190,0,3640,"room"),("押入",4550,8190,3640,4550,"oshi"),
  ("洋室",8190,10920,0,4550,"room"),("階段(概略)",9240,10290,2275,4550,"stair"),
  ("押入",10920,11830,0,4550,"oshi"),
  ("和室8帖",11830,15470,0,3640,"room"),("押入",11830,14560,3640,4550,"oshi"),("階段",14560,15470,3640,4550,"stair"),
  ("和室8帖",15470,19110,0,3640,"room"),("押入",15470,19110,-455,0,"oshi"),("押入",15470,19110,3640,4550,"oshi"),
  ("縁側",19110,19565,0,4550,"engawa"),
 ],
 "1F": [
  ("ホール",910,2730,0,3640,"room"),("階段",910,2730,3640,4550,"stair"),
  ("店舗",2730,10010,0,4550,"room"),
  ("土間",10010,11375,0,910,"doma"),("WC",10010,11375,910,2275,"room"),("WC",10010,11375,2275,3640,"room"),("階段",10010,11375,3640,4550,"stair"),
  ("廊下",11375,12740,0,4550,"room"),
  ("和室6帖",12740,15470,0,3640,"room"),("階段",12740,15470,3640,4550,"stair"),
  ("床の間",15470,15925,0,1365,"room"),("洗面脱衣",15925,17290,0,1365,"room"),
  ("台所",15470,19110,1365,4550,"room"),("",18200,19110,910,1365,"room-nolabel"),
 ]}
fill={"room":"#fff","room-nolabel":"#fff","stair":"#dbe8f5","oshi":"#eee","engawa":"#f6efdc","doma":"#e6e1d8"}
FH=4550*S+170
H=2*FH+40
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*S+2*M}" height="{H}" font-family="Noto Sans CJK JP, WenQuanYi Zen Hei, sans-serif">',
     '<rect width="100%" height="100%" fill="#fff"/>',
     '<defs><pattern id="h" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#aaa" stroke-width="1"/></pattern></defs>']
for i,(fl,rooms) in enumerate(floors.items()):
    oy=i*FH+90
    X=lambda x:M+x*S; Y=lambda y:oy+y*S
    out.append(f'<text x="{M}" y="{oy-50}" font-size="22" font-weight="bold">{fl}</text>')
    for g in range(0,W+1,910):
        out.append(f'<line x1="{X(g)}" y1="{Y(-455)}" x2="{X(g)}" y2="{Y(4550)}" stroke="#e4e4e4"/>')
    for name,x0,x1,y0,y1,k in rooms:
        out.append(f'<rect x="{X(x0)}" y="{Y(y0)}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" fill="{fill[k]}" stroke="#222" stroke-width="2"/>')
        if k=="oshi": out.append(f'<rect x="{X(x0)}" y="{Y(y0)}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" fill="url(#h)" stroke="none"/>')
        if name and k!="room-nolabel":
            fs=13 if (x1-x0)<1000 or (y1-y0)<1000 else 15
            if (x1-x0)<600:
                n=len(name); [out.append(f'<text x="{X((x0+x1)/2)}" y="{Y((y0+y1)/2)+(j-(n-1)/2)*13+4}" font-size="11" text-anchor="middle">{c}</text>') for j,c in enumerate(name)]
            else:
                out.append(f'<text x="{X((x0+x1)/2)}" y="{Y(1000 if name=='洋室' else (y0+y1)/2)+5}" font-size="{fs}" text-anchor="middle">{name}</text>')
    if fl=="1F":
        out.append(f'<line x1="{X(8190)}" y1="{Y(0)}" x2="{X(8190)}" y2="{Y(4550)}" stroke="#d33" stroke-width="2" stroke-dasharray="8 5"/>')
        out.append(f'<text x="{X(8190)+5}" y="{Y(400)}" font-size="12" fill="#d33">段差</text>')
        pts=" ".join(f"{X(a)},{Y(b)}" for a,b in [(17290,0),(19110,0),(19110,910),(18200,910),(18200,1365),(17290,1365)])
        out.append(f'<polygon points="{pts}" fill="#fff" stroke="#222" stroke-width="2"/>')
        out.append(f'<text x="{X(18200)}" y="{Y(600)}" font-size="15" text-anchor="middle">フロ</text>')
        out.append(f'<text x="{X(18650)}" y="{Y(1250)}" font-size="10" text-anchor="middle" fill="#555">台所側</text>')
        # 1F外形の点線を2Fと比較できるよう表示
    # 寸法（上）
    xs = sorted({r[1] for r in rooms}|{r[2] for r in rooms})
    if fl=="1F": xs=[910,2730,10010,11375,12740,15470,19110]
    else: xs=[0,910,4550,8190,10920,11830,15470,19110,19565]
    dy=Y(4550)+30
    out.append(f'<line x1="{X(xs[0])}" y1="{dy}" x2="{X(xs[-1])}" y2="{dy}" stroke="#36c"/>')
    for a,b in zip(xs,xs[1:]):
        out.append(f'<line x1="{X(a)}" y1="{dy-6}" x2="{X(a)}" y2="{dy+6}" stroke="#36c"/>')
        out.append(f'<text x="{X((a+b)/2)}" y="{dy-5}" font-size="11" text-anchor="middle" fill="#36c">{b-a:,}</text>')
    out.append(f'<line x1="{X(xs[-1])}" y1="{dy-6}" x2="{X(xs[-1])}" y2="{dy+6}" stroke="#36c"/>')
    out.append(f'<text x="{X((xs[0]+xs[-1])/2)}" y="{dy+22}" font-size="12" text-anchor="middle" fill="#36c">計 {xs[-1]-xs[0]:,}</text>')
# 方位（左斜め下が北）
cx,cy=W*S+M-30,40
out.append(f'<g transform="translate({cx},{cy}) rotate(225)"><line x1="0" y1="18" x2="0" y2="-18" stroke="#000" stroke-width="2"/><polygon points="0,-24 -6,-12 6,-12" fill="#000"/></g>')
out.append(f'<text x="{cx-30}" y="{cy+30}" font-size="14" font-weight="bold">N</text>')
out.append(f'<text x="{M}" y="{H-12}" font-size="12" fill="#555">配置確認用（縮尺概略）。1階は2階に対し左に910、右に455引っ込んだ位置で重ねて表示。グリッド＝910</text>')
out.append('</svg>')
open("layout.svg","w").write("\n".join(out))
