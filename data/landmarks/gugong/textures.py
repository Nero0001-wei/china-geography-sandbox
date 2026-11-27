"""Paint small, tileable architectural textures for the Taihe Hall miniature."""
from math import cos, exp, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFont

TARGET = Path(__file__).resolve().parent / 'textures'
TARGET.mkdir(exist_ok=True)
noise = Random(1695)


def save(image, name):
    image.save(TARGET / (name + '.png'), optimize=True)


def roof():
    n = 128
    im = Image.new('RGB', (n, n))
    for y in range(n):
        for x in range(n):
            u = x % 32
            v = (y + (x // 32 % 2) * 12) % 32
            ridge = exp(-((u - 6) / 3.7) ** 2)
            shade = exp(-((u - 11) / 3.1) ** 2)
            seam = exp(-((v - 3) / 1.2) ** 2) * (.32 + .68 * (1 - ridge))
            glaze = .91 + .22 * ridge - .26 * shade - .16 * seam + .05 * cos(u * 2 * pi / 32) + noise.uniform(-.026, .026)
            im.putpixel((x,y), tuple(min(255, int(k * glaze)) for k in (220, 148, 48)))
    save(im, 'amber-tiles')


def door():
    w,h=192,192
    im=Image.new('RGB',(w,h),(117,44,37))
    d=ImageDraw.Draw(im)
    for i in range(4):
        left=i*48
        d.rectangle((left+2,6,left+45,184), fill=(130,44,34), outline=(176,78,40), width=3)
        d.rectangle((left+7,12,left+40,108), fill=(43,55,52), outline=(192,131,60), width=2)
        # The gold lattice is baked, so it stays visible in oblique views.
        for yy in range(17,108):
            for xx in range(left+9,left+39):
                a=(xx+yy)%13; b=(xx-yy)%13
                if min(a,b)<2: d.point((xx,yy),fill=(178,126,65))
                elif (a in (4,5,9,10) and b in (4,5,9,10)): d.point((xx,yy),fill=(186,148,90))
        for yy0,yy1 in [(112,127),(133,173)]:
            d.rectangle((left+7,yy0,left+39,yy1),outline=(84,41,32),width=2)
            d.rectangle((left+10,yy0+3,left+36,yy1-3),outline=(186,103,44))
        cx=left+23
        d.line((cx,137,cx+8,151,cx,168,cx-8,151,cx,137), fill=(161,92,44),width=2)
    save(im,'lattice-doors')


def beam():
    im=Image.new('RGB',(192,48),(39,83,82));d=ImageDraw.Draw(im)
    for y,c in [(0,'#ae7837'),(1,'#e3b773'),(4,'#183c42'),(7,'#579493'),(40,'#21475a'),(44,'#c5994e'),(47,'#54422a')]:
        d.line([(0,y),(191,y)],fill=c,width=2)
    for x in (0,48,96,144,192):
        d.polygon([(x-23,24),(x,9),(x+23,24),(x,39)],fill='#1b5260',outline='#d5ac64',width=2)
        d.ellipse((x-7,17,x+7,31),outline='#dcbc77',width=2)
        d.arc((x-16,17,x-1,31),80,295,fill='#91b1a3',width=2)
        d.arc((x+1,17,x+16,31),260,120,fill='#91b1a3',width=2)
        d.line((x+18,17,x+24,12,x+30,17),fill='#c8a762',width=2)
    save(im,'bracket-paint')


def stone():
    size=128
    im=Image.new('RGB',(size,size))
    for y in range(size):
        for x in range(size):
            f=2*sin(x*2*pi/size + 2*sin(y*2*pi/size))+2*sin((x+y)*4*pi/size)+noise.uniform(-3,3)
            im.putpixel((x,y),tuple(round(v+f) for v in (208,203,186)))
    save(im,'marble')
    d=ImageDraw.Draw(im)
    for y in range(0,128,32):
        d.line((0,y,127,y),fill='#aaa699',width=2)
        off=32 if y%64 else 0
        for x in range(off,128,64):
            d.line((x,y,x,y+32),fill='#aba99c',width=2)
    save(im,'flagstones')


def imperial_ramp():
    im=Image.new('RGB',(128,256),'#c6c0ad')
    d=ImageDraw.Draw(im)
    for x in (3,7,120,124):
        d.line((x,0,x,255),fill='#a7a18f',width=2)
    # A small relief motif for the imperial way: cloud scrolls and serpentine spines.
    for y in range(16,264,38):
        for x in (25,102):
            d.arc((x-15,y-7,x+12,y+11),35,324,fill='#aaa38f',width=2)
            d.arc((x-14,y-9,x+13,y+9),35,324,fill='#e6e0cc',width=2)
    for offset in (0,125):
        spine=[(64+int(17*sin(i/12)),offset+10+i) for i in range(102)]
        d.line([(x+1,y+2) for x,y in spine],fill='#a7a18f',width=7)
        d.line(spine,fill='#e4decb',width=5)
        for i in (16,38,57,79):
            x,y=spine[i]; side=(-1)**(i//18)
            foot=[(x,y),(x+10*side,y-4),(x+14*side,y-1),(x+19*side,y-6)]
            d.line(foot,fill='#efead7',width=3)
        x,y=spine[-1]
        d.polygon([(x-4,y-2),(x+4,y-4),(x+7,y+2),(x+3,y+9),(x-4,y+7)],fill='#ded9c4')
    save(im,'imperial-ramp')


def plaque():
    im=Image.new('RGB',(256,100),'#8c5725');d=ImageDraw.Draw(im)
    d.rectangle((2,2,253,97),outline='#e9bd68',width=3)
    d.rectangle((8,8,247,91),fill='#203f51',outline='#b88e46',width=3)
    # These three Chinese characters read right to left on the eaves plaque.
    for path in ['/System/Library/Fonts/STHeiti Medium.ttc','/System/Library/Fonts/Supplemental/Songti.ttc',
                 '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc']:
        if Path(path).exists():
            font=ImageFont.truetype(path,64)
            d.text((128,49),'殿和太',anchor='mm',font=font,fill='#e9be6c')
            break
    else:
        raise RuntimeError('Rebuilding the plaque requires a Chinese font; the source texture is bundled.')
    save(im,'taihe-plaque')


if __name__=='__main__':
    roof(); door(); beam(); stone(); imperial_ramp(); plaque()
