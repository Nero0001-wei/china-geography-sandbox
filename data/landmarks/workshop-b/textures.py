"""Generate small seamless, original colour maps for the miniature material library."""
from pathlib import Path
import math, random
from PIL import Image
OUT=Path(__file__).parent/'textures'
OUT.mkdir(exist_ok=True)
PALETTE={
'limestone':('stone','#a79477'),'cliff':('stone','#857766'),'karst':('stone','#9a9e90'),
'darkrock':('stone','#5a6257'),'sandstone':('stone','#b49a79'),'oldstone':('masonry','#918d81'),
'chalk':('stone','#d7d0b6'),'jade':('marble','#549696'),'river':('water','#4b989c'),
'goldroof':('tiles','#deab48'),'bluegray':('tiles','#4e575c'),'gold':('metal','#dcb771'),
'red':('lacquer','#984c38'),'paint':('paint','#4c7770'),'wood':('wood','#8a5c36'),
'darkwood':('wood','#553a2e'),'paper':('plaster','#dfc797'),'windows':('windows','#66513b'),
'leaf':('foliage','#52784a'),'leaflight':('foliage','#7d9554'),'pines':('foliage','#365c4d'),
'bamboo':('wood','#83924e'),'whitefur':('fur','#e2dfca'),'blackfur':('fur','#292b28'),
'steel':('metal','#c6d3d2'),'glaze':('glass','#678b9a'),'clear':('water','#7cc0be'),
'fall':('falls','#c4e4df'),'foam':('falls','#edf5ed'),'soil':('stone','#9c9169'),
'terracotta':('masonry','#a56c52'),'tufa':('stone','#72735b'),'rust':('wood','#a15a3e')}
N=192
for i,(name,(kind,hx)) in enumerate(PALETTE.items()):
    rgb=tuple(bytes.fromhex(hx[1:])); rng=random.Random(137+i); img=Image.new('RGB',(N,N)); pixels=img.load()
    for y in range(N):
        v=y/N*math.tau
        for x in range(N):
            u=x/N*math.tau
            n=rng.uniform(-.052,.052)
            if kind in ('stone','masonry','marble'):
                n+=.043*math.sin(3*u+2.7*math.sin(2*v))+.03*math.cos(7*u+4*v)+.021*math.sin(19*v+5*math.sin(3*u))
                if kind=='masonry' and (y%32<2 or (x+(y//32%2)*31)%64<2):n-=.19
            elif kind=='tiles': n+=.14*math.cos(12*u)-.10*(y%36<3)
            elif kind=='wood':n+=.075*math.sin(14*u+1.3*math.cos(2*v))+.04*math.cos(31*u+.4*math.sin(v))
            elif kind=='windows':n+=(-.24 if 4<x%32<28 and 4<y%44<39 else .2)
            elif kind=='foliage':n+=.11*math.sin(13*u+9*math.sin(7*v))+.11*math.cos(4*v+2*u)
            elif kind in ('falls','fur'):n+=.10*math.sin(23*u+2*math.sin(2*v))+.07*math.cos(37*u+v)
            elif kind in ('water','glass'):n+=.075*math.cos(13*v+2*math.sin(3*u))+.035*math.sin(27*v+4*u)
            else:n*=.45
            pixels[x,y]=tuple(max(0,min(255,round(c*(1+n)))) for c in rgb)
    img.save(OUT/(name+'.jpg'),quality=87)

# Fine gilded gate and tower inscriptions are baked into a two-tone framed material.
from PIL import ImageDraw, ImageFont
for key, text in (('yellow-sign', '黄鹤楼'), ('dali-sign', '大理')):
    plaque=Image.new('RGB',(384,133),'#413429')
    brush=ImageDraw.Draw(plaque)
    for inset,color in ((0,'#98734c'),(5,'#e4bc70'),(9,'#755034')):
        brush.rectangle((inset,inset,383-inset,132-inset),outline=color,width=3)
    fontpath=Path('/System/Library/Fonts/Supplemental/Songti.ttc')
    if fontpath.exists():
        font=ImageFont.truetype(str(fontpath),92,index=1)
        brush.text((192,64),text,fill='#f6d68e',font=font,anchor='mm',stroke_width=1)
    else:
        raise RuntimeError('Install Songti.ttc in the macOS Supplemental fonts directory to redraw the plaques.')
    plaque.save(OUT/(key+'.jpg'),quality=93)
