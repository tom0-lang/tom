# -*- coding: utf-8 -*-
"""把 assets/ 里的图片转 base64 注入 src/game.template.html，生成 index.html

用法：python src/assemble.py
依赖：无（仅标准库 + 已就位的 assets/）
"""
import base64, os

BASE = os.path.dirname(os.path.abspath(__file__))          # src/
ROOT = os.path.dirname(BASE)                                # 仓库根目录

FILES = {
    '{{BG_FAIR}}':    'assets/bg/bg-fair.jpg',
    '{{BG_STALL}}':   'assets/bg/bg-stall.jpg',
    '{{BG_SPRING}}':  'assets/bg/bg-spring.jpg',
    '{{BG_NOODLE}}':  'assets/bg/bg-noodle.jpg',
    '{{BG_WSTREET}}': 'assets/bg/bg-wedding-street.jpg',
    '{{BG_WHALL}}':   'assets/bg/bg-wedding-hall.jpg',
    '{{BG_BEDROOM}}': 'assets/bg/bg-bedroom.jpg',
    '{{BG_STARRY}}':  'assets/bg/bg-starry.jpg',
    '{{BG_FAMILY}}':  'assets/bg/bg-family.jpg',
    '{{TT_NORMAL}}':  'assets/chars/tt-normal.webp',
    '{{TT_NERVOUS}}': 'assets/chars/tt-nervous.webp',
    '{{TT_SORRY}}':   'assets/chars/tt-sorry.webp',
    '{{TT_WEDDING}}': 'assets/chars/tt-wedding.webp',
    '{{TT_DAD}}':     'assets/chars/tt-dad.webp',
    '{{RR_NORMAL}}':  'assets/chars/rr-normal.webp',
    '{{RR_LAUGH}}':   'assets/chars/rr-laugh.webp',
    '{{RR_POUTY}}':   'assets/chars/rr-pouty.webp',
    '{{RR_WEDDING}}': 'assets/chars/rr-wedding.webp',
    '{{RR_VEILED}}':  'assets/chars/rr-veiled.webp',
    '{{RR_PREGNANT}}':'assets/chars/rr-pregnant.webp',
    '{{RR_MOTHER}}':  'assets/chars/rr-mother.webp',
}

html = open(os.path.join(ROOT, 'src', 'game.template.html'), encoding='utf-8').read()
for key, rel in FILES.items():
    p = os.path.join(ROOT, rel)
    raw = open(p, 'rb').read()
    mime = 'image/webp' if rel.endswith('.webp') else 'image/jpeg'
    uri = 'data:%s;base64,' % mime + base64.b64encode(raw).decode()
    assert key in html, 'missing ' + key
    html = html.replace(key, uri)

# {{baby}} 是运行时模板（玩家取名），不是素材占位符——保留
for key in FILES:
    assert key not in html, 'leftover ' + key

out = os.path.join(ROOT, 'index.html')
open(out, 'w', encoding='utf-8', newline='\n').write(html)
print('written', out, os.path.getsize(out), 'bytes')
