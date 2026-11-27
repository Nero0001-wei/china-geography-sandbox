"""Generate embedded destination plates (Pillow)."""
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont

base = Path(__file__).resolve().parent / 'materials'
base.mkdir(exist_ok=True)
font_path = os.environ.get('VEHICLE_SIGN_FONT','/System/Library/Fonts/STHeiti Medium.ttc')
for key, text, background, ink in [
    ('coach','城际客运','#172A34','#F9BF55'),
    ('intercity','城际列车','#152D36','#C4EFD5'),
    ('plate','A · 6802','#275071','#ECF3EE')
]:
    im=Image.new('RGB',(256,64),background)
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(font_path,38)
    draw.text((128,32),text,font=font,fill=ink,anchor='mm')
    im.save(base/f'sign-{key}.png',optimize=True)
