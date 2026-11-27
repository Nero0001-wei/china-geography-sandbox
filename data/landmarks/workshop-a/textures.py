"""Paint seamless color materials and architectural details for these miniatures."""

from pathlib import Path
from math import sin, cos, tau, pi
import random, urllib.request, json
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "textures"
OUT.mkdir(exist_ok=True)
rng = random.Random(27)
font_cjk = "/System/Library/Fonts/STHeiti Medium.ttc"


def surface(name, color, style):
    image = Image.new("RGB", (256, 256), color)
    draw = ImageDraw.Draw(image)
    for y in range(256):
        for x in range(256):
            v = rng.gauss(0, 3) + sin(x / 10) * sin(y / 14) * 2
            if style == "water":
                v += 2.5 * sin((x * 0.09 + sin(y * 0.13)) * 2 + y * 0.3)
            image.putpixel((x, y), tuple(max(0, min(255, int(i + v))) for i in color))
    if style == "brick":
        for row in range(-1, 17):
            y = row * 16
            draw.line((0, y, 256, y), fill=tuple(int(i * 0.73) for i in color))
            for x in range(-40 + 20 * (row % 2), 256, 40):
                draw.line((x, y, x, y + 15), fill=tuple(int(i * 0.73) for i in color))
    if style == "tile":
        for x in range(0, 256, 16):
            draw.line((x, 0, x, 256), fill=tuple(int(i * 0.72) for i in color), width=3)
            draw.line(
                (x + 3, 0, x + 3, 256), fill=tuple(min(255, int(i * 1.14)) for i in color), width=2
            )
        for y in range(0, 256, 52):
            draw.line((0, y, 256, y), fill=tuple(int(i * 0.81) for i in color))
    image.save(OUT / (name + ".jpg"), quality=87)


for name, color, style in [
    ("limestone", (176, 164, 141), "brick"),
    ("granite", (183, 180, 169), "stone"),
    ("terracotta", (146, 71, 49), "brick"),
    ("goldtile", (198, 141, 57), "tile"),
    ("slate", (67, 72, 73), "tile"),
    ("copper", (66, 109, 91), "tile"),
    ("bluetile", (74, 115, 153), "tile"),
    ("river", (79, 134, 134), "water"),
    ("sandstone", (186, 173, 143), "brick"),
    ("meadow", (109, 121, 73), "stone"),
    ("rock", (150, 143, 125), "stone"),
]:
    surface(name, color, style)

img = Image.new("RGB", (256, 256), "#ded4b3")
d = ImageDraw.Draw(img)
for rad, fill in [(124, "#313e40"), (117, "#bab7a1"), (112, "#f0e2c2")]:
    d.ellipse((128 - rad, 128 - rad, 128 + rad, 128 + rad), fill=fill)
for k in range(60):
    a = k * tau / 60
    r = 92 if k % 5 == 0 else 103
    d.line(
        (128 + r * sin(a), 128 - r * cos(a), 128 + 108 * sin(a), 128 - 108 * cos(a)),
        fill="#30312b",
        width=5 if k % 5 == 0 else 2,
    )
d.line((128, 128, 104, 72), fill="#302c24", width=7)
d.line((128, 128, 194, 88), fill="#302c24", width=4)
d.ellipse((121, 121, 135, 135), fill="#302c24")
img.save(OUT / "clock.png")

globe = Image.new("RGB", (768, 384), "#24759a")
d = ImageDraw.Draw(globe)
cache = Path("/tmp/sandtable-a-naturalearth.geojson")
if cache.exists():
    j = json.loads(cache.read_text())
else:
    j = json.load(
        urllib.request.urlopen(
            "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"
        )
    )
for f in j["features"]:
    g = f["geometry"]
    polygons = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for poly in polygons:
        for i, ring in enumerate(poly):
            d.polygon(
                [((lon + 180) / 360 * 768, (90 - lat) / 180 * 384) for lon, lat in ring],
                fill="#d0ae62" if not i else "#24759a",
            )
for x in range(0, 768, 64):
    d.line((x, 0, x, 384), fill="#91a28c", width=1)
for y in range(0, 384, 64):
    d.line((0, y, 768, y), fill="#849d92", width=1)
globe.save(OUT / "world.png")

img = Image.new("RGB", (720, 208), "#9e472e")
d = ImageDraw.Draw(img)
d.rectangle((4, 4, 715, 203), outline="#8b6941", width=6)
for flip in [-1, 1]:

    def pt(x, y):
        return (360 + flip * x, y)

    points = [pt(x, 94 + 30 * sin(x / 26) + 10 * sin(x / 9)) for x in range(48, 312)]
    d.line(points, fill="#6d3724", width=14)
    d.line(points, fill="#d4a34e", width=10)
    for i in range(20, len(points) - 10, 12):
        x, y = points[i]
        d.ellipse((x - 2, y - 3, x + 2, y + 2), fill="#865b36")
        d.polygon(
            [(x - 4 * flip, y - 3), (x + 8 * flip, y - 13), (x + 5 * flip, y - 2)], fill="#d8aa55"
        )
    x, y = points[1]
    d.ellipse((x - 11, y - 9, x + 11, y + 9), fill="#ddb260")
    d.line([pt(48, points[0][1]), pt(32, y - 9), pt(24, y - 6)], width=5, fill="#e5bd6c")
    for xp in [85, 128, 202, 241]:
        ya = 94 + 30 * sin(xp / 26) + 10 * sin(xp / 9)
        d.line([pt(xp, ya), pt(xp + 11, ya + 16), pt(xp - 1, ya + 30)], width=4, fill="#d1a455")
        for da in [-8, 0, 8]:
            d.line([pt(xp, ya + 29), pt(xp - 7 + da, ya + 32)], fill="#e3bb70", width=2)
d.ellipse((343, 74, 376, 107), fill="#d9af62", outline="#f7da8f", width=3)
img.save(OUT / "dragon-wall.png")
for name, characters in [("heaven", "南天门"), ("qin", "四海归一"), ("confucius", "天下文枢")]:
    im = Image.new("RGB", (384, 96), "#334755")
    dr = ImageDraw.Draw(im)
    dr.rectangle((2, 2, 381, 93), outline="#bfa060", width=5)
    dr.text(
        (192, 45),
        characters,
        anchor="mm",
        font=ImageFont.truetype(font_cjk, 63),
        fill="#e3bf74",
        spacing=1,
    )
    im.save(OUT / (name + ".png"))
