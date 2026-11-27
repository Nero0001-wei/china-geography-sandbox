"""Create repeatable, original PBR color tiles for the nine miniature scenes."""

from pathlib import Path
from PIL import Image, ImageDraw
import random, math

OUT = Path(__file__).resolve().parent / "textures"
OUT.mkdir(exist_ok=True)
PALETTE = {
    "marble": ((206, 193, 165), "stone"),
    "granite": ((179, 151, 112), "stone"),
    "graniteLight": ((214, 192, 153), "stone"),
    "whitewash": ((231, 222, 200), "plaster"),
    "ochre": ((181, 112, 59), "plaster"),
    "plum": ((140, 56, 49), "plaster"),
    "ashlar": ((167, 145, 125), "block"),
    "greyTile": ((83, 85, 83), "roof"),
    "greenTile": ((65, 113, 104), "roof"),
    "goldTile": ((196, 131, 57), "roof"),
    "rouge": ((143, 51, 45), "wood"),
    "timber": ((101, 66, 45), "wood"),
    "beam": ((115, 79, 52), "wood"),
    "water": ((47, 146, 168), "water"),
    "deepwater": ((36, 119, 154), "water"),
    "grass": ((132, 158, 89), "grass"),
    "pine": ((62, 107, 79), "grass"),
    "snow": ((221, 229, 221), "stone"),
    "loess": ((184, 143, 105), "strata"),
    "loessDark": ((161, 124, 91), "strata"),
    "scree": ((121, 134, 127), "stone"),
    "sand": ((180, 141, 97), "stone"),
    "rock": ((159, 124, 92), "stone"),
    "clay": ((130, 121, 108), "clay"),
    "clayLight": ((153, 141, 123), "clay"),
    "clayDark": ((100, 93, 81), "clay"),
    "dark": ((53, 61, 58), "plain"),
    "gold": ((215, 171, 72), "metal"),
    "bronze": ((99, 108, 87), "metal"),
    "teal": ((71, 129, 124), "glass"),
    "mint": ((112, 167, 151), "metal"),
    "pink": ((215, 153, 145), "block"),
    "lilac": ((128, 108, 170), "roof"),
    "sky": ((72, 133, 164), "roof"),
    "turquoise": ((63, 148, 139), "roof"),
}


def offset(color, n):
    return tuple(max(0, min(255, int(x + n))) for x in color)


for name, (color, mode) in PALETTE.items():
    rng = random.Random(name)
    im = Image.new("RGB", (192, 192))
    pix = im.load()
    for y in range(192):
        for x in range(192):
            noise = rng.uniform(-5, 5)
            if mode in ("stone", "plaster", "grass", "clay"):
                noise += 3 * math.sin(x * 0.11 + math.sin(y * 0.13)) + 2 * math.cos((x - y) * 0.17)
            if mode == "strata":
                noise += 3 * math.sin(x * 8 * math.pi / 192 + 2 * math.sin(y * math.pi / 24))
                noise += 6 * math.cos(y * math.pi / 7 + math.sin(x * math.pi / 32) * 1.5) + 4 * math.sin(
                    y * math.pi / 3 + math.sin(x * math.pi / 24)
                )
            if mode == "wood":
                noise += 5 * math.sin(y * 0.5 + math.sin(x * 0.05))
            if mode == "roof":
                noise += 6 * math.cos(x * math.pi / 8)
            pix[x, y] = offset(color, noise)
    dr = ImageDraw.Draw(im)
    if mode == "roof":
        for x in range(0, 192, 16):
            dr.line((x, 0, x, 192), fill=offset(color, 28), width=2)
            dr.line((x + 3, 0, x + 3, 192), fill=offset(color, -24), width=2)
            for y in range((x // 16 % 2) * 12, 192, 24):
                dr.line((x + 3, y, x + 14, y), fill=offset(color, -19), width=1)
    if mode == "block":
        for y in range(0, 193, 24):
            dr.line((0, y, 192, y), fill=offset(color, -18), width=2)
            for x in range((y // 24 % 2) * 24, 194, 48):
                dr.line((x, y, x, y + 24), fill=offset(color, -19), width=2)
    if mode == "glass":
        for y in range(0, 192, 12):
            dr.line((0, y, 192, y), fill=offset(color, -33), width=2)
        for x in range(0, 192, 24):
            dr.line((x, 0, x, 192), fill=offset(color, 24), width=2)
    if mode == "water":
        for _ in range(135):
            x, y = rng.randrange(192), rng.randrange(192)
            dr.line((x, y, x + rng.randrange(4, 16), y - 1), fill=offset(color, rng.randint(10, 27)))
    if mode == "grass":
        for _ in range(260):
            x, y = rng.randrange(192), rng.randrange(192)
            dr.line((x, y, x + 2, y - 4), fill=offset(color, rng.randint(-24, 18)))
    im.save(OUT / (name + ".png"), optimize=True)
