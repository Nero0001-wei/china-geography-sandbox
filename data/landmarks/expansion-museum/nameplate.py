"""Create the small gray-stone title panel for the Jiangdongmen memorial model."""

import argparse
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TITLE = "侵华日军南京大屠杀遇难同胞纪念馆"


def build(font_path):
    width, height = 752, 70
    stone = Image.new("RGB", (width, height))
    noise = Random(19371213)
    stone.putdata([(value - 2, value, value) for value in
                   (146 + noise.randrange(-7, 8) for _ in range(width * height))])
    draw = ImageDraw.Draw(stone)
    font = ImageFont.truetype(font_path, 39)
    draw.text((width / 2, height / 2), TITLE, font=font, anchor="mm", fill=(46, 47, 46))
    stone.save(HERE / "stone-inscription.png", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", default="/System/Library/Fonts/STHeiti Medium.ttc")
    build(parser.parse_args().font)
