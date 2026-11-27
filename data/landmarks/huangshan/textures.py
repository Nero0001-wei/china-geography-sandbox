"""Draw the tileable surface maps and transparent pine shoot with Python and Pillow."""
import math
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter, ImageOps

DEST = Path(__file__).resolve().parent / 'textures'
DEST.mkdir(exist_ok=True)
SIZE = 512
rng = Random(22411)


def noise(size):
    field = Image.new('L', (size, size))
    field.putdata([rng.randrange(256) for _ in range(size * size)])
    return field.resize((SIZE, SIZE), Image.Resampling.BICUBIC)


def surface(kind):
    grain = noise(SIZE)
    coarse = noise(13)
    medium = noise(58)
    if kind == 'granite':
        texture = Image.blend(Image.blend(coarse, medium, .48), grain, .46)
        image = ImageOps.colorize(texture, '#777673', '#d6cbb3').convert('RGB')
        draw = ImageDraw.Draw(image)
        for _ in range(12000):
            x, y = rng.randrange(SIZE), rng.randrange(SIZE)
            c = rng.choice(['#757579', '#a8a59c', '#c8c4af', '#d5cdb8', '#9b998e'])
            draw.line((x, y, x + rng.choice([0, 1, 2]), y + rng.choice([0, 1])), fill=c)
        # Sparse joint hairlines follow the predominant upright granite fracture planes.
        for _ in range(12):
            x, y = rng.uniform(0,SIZE),rng.uniform(-15,SIZE)
            stroke=[(x,y)]
            for i in range(rng.randrange(3,8)):
                x+=rng.uniform(-5,8)
                y+=rng.uniform(4,12)
                stroke.append((x,y))
            draw.line(stroke,fill=rng.choice(['#aaa69b','#938e83','#8f8c80']),width=1)
    else:
        value = Image.blend(Image.blend(noise(23).resize((160, 512)).resize((512, 512)), medium, .24), grain, .28)
        image = ImageOps.colorize(value, '#41362f', '#af8b64').convert('RGB')
        draw = ImageDraw.Draw(image)
        for _ in range(1650):
            x, y = rng.randrange(-5, SIZE), rng.randrange(-30, SIZE)
            length = rng.uniform(7, 39)
            curve = [(x, y), (x + 2, y + length * .27), (x, y + length * .7), (x + 3, y + length)]
            draw.line(curve, fill=rng.choice(['#55473b', '#554438', '#695546', '#80654d']), width=rng.choice([1, 1, 2]))
            draw.line([(a+1,b) for a,b in curve[1:]], fill=rng.choice(['#a68a69', '#927455']), width=1)
    image.save(DEST / (kind + '.jpg'), quality=90)


def pine_spray():
    # The root is at the lower edge. UV-mapped leaf cards arc out of their living twig.
    img = Image.new('RGBA', (SIZE, SIZE))
    draw = ImageDraw.Draw(img)
    def needles(a, b, radius):
        ax, ay = a
        bx, by = b
        dx, dy = bx-ax, by-ay
        dist = math.hypot(dx, dy)
        nx, ny = -dy/dist, dx/dist
        draw.line([a,b], fill=(104,86,56,255), width=2)
        for i in range(39):
            pos = rng.uniform(.05, 1)
            x, y = ax + dx*pos, ay + dy*pos
            sign = rng.choice([-1,1])
            length = radius*rng.uniform(.18,1)*(.85+.2*math.sin(math.pi*pos))
            lean = rng.uniform(.2,1.1)*length
            target=(x+nx*length*sign+dx/dist*lean, y+ny*length*sign+dy/dist*lean)
            color = rng.choice([(50,69,45), (65,86,49), (74,92,49), (88,106,57), (112,126,71),
                                (86,106,66), (124,137,83), (63,84,53)])
            draw.line([(x,y),target],fill=(*color,255),width=rng.choice([1,2,2,2]))
    root = (256,490)
    for side in (-1,1):
        for j in range(9):
            u=j/9
            at=(256+5*math.sin(u*8),452-328*u+side*4)
            end=(256+side*(122*(1-u)+45)*rng.uniform(.9,1.22), at[1]-(60+34*u))
            for k in range(4):
                t=(k+.55)/4
                cx=at[0]+(end[0]-at[0])*t
                cy=at[1]+(end[1]-at[1])*t
                sx=end[0]-at[0]
                tip=(cx+sx*.17 + rng.uniform(-13,13), cy-rng.uniform(26,51))
                needles((cx,cy),tip,21)
            needles(at,end,17)
    needles(root,(255,49),18)
    needles((255,124),(263,45),23)
    box=img.getbbox()
    img=img.crop(box).resize((SIZE-6,SIZE-6),Image.Resampling.LANCZOS)
    final=Image.new('RGBA',(SIZE,SIZE))
    final.paste(img,(3,3))
    final.save(DEST/'pine-spray.png',optimize=True)
    
if __name__=='__main__':
    under = ImageOps.colorize(Image.blend(noise(36), noise(512), .35), '#324533', '#74814a').convert('RGB')
    needles = ImageDraw.Draw(under)
    for _ in range(10500):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        d = rng.choice([-1, 1])
        needles.line((x, y, x+d*rng.randrange(2,9), y-rng.randrange(2,7)), fill=rng.choice(['#3c5136','#4c643b','#647643','#8e965d','#70874e']))
    under.save(DEST/'dense-needles.jpg', quality=88)
    surface('granite')
    surface('bark')
    pine_spray()
