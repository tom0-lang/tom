# -*- coding: utf-8 -*-
"""全量素材后处理：人物抠图去水印压缩 + 背景去水印压缩"""
import os
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'src')

CHARS = ['tt-normal', 'tt-nervous', 'tt-sorry', 'tt-wedding', 'tt-dad',
         'rr-normal', 'rr-laugh', 'rr-normal2', 'rr-laugh2', 'rr-pouty',
         'rr-wedding', 'rr-veiled', 'rr-pregnant', 'rr-mother']
BGS = ['bg-fair', 'bg-stall', 'bg-spring', 'bg-noodle', 'bg-wedding-street',
       'bg-wedding-hall', 'bg-bedroom', 'bg-starry', 'bg-family']

def clean_char(name):
    src = os.path.join(SRC, name + '.jpg')
    if not os.path.exists(src):
        print('MISS', name); return
    img = Image.open(src).convert('RGBA')
    w, h = img.size
    px = img.load()
    x0, y0 = int(w * 0.70), int(h * 0.85)
    for y in range(y0, h):
        for x in range(x0, w):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 0)
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    if h > 820:
        img = img.resize((max(1, int(w * 820 / h)), 820), Image.LANCZOS)
    img.save(os.path.join(BASE, name + '.webp'), 'WEBP', quality=88, method=6)
    print('char', name, img.size, os.path.getsize(os.path.join(BASE, name + '.webp')))

def clean_bg(name):
    img = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = img.size
    x0, y0 = int(w * 0.83), int(h * 0.87)
    pw, ph = w - x0, h - y0
    top = img.crop((x0, max(0, y0 - ph), w, y0)).transpose(Image.FLIP_TOP_BOTTOM)
    top = top.filter(ImageFilter.GaussianBlur(5))
    img.paste(top, (x0, y0))
    img = img.resize((1500, int(h * 1500 / w)), Image.LANCZOS)
    out = os.path.join(BASE, name + '.jpg')
    img.save(out, 'JPEG', quality=80, optimize=True)
    print('bg', name, img.size, os.path.getsize(out))

for n in CHARS:
    clean_char(n)
for n in BGS:
    clean_bg(n)
print('done')
