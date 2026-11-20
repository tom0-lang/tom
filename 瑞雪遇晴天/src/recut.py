# -*- coding: utf-8 -*-
"""确定性抠图：边缘泛洪 + 大组件保留 + 去水印 + 裁剪压缩"""
import os, sys
from collections import deque, Counter
from PIL import Image

sys.setrecursionlimit(10000)
BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'src')
T = 62          # 与背景参考色的距离阈值
T2 = 105        # 边缘羽化阈值

CHARS = ['tt-normal', 'tt-nervous', 'tt-sorry', 'tt-wedding', 'tt-dad',
         'rr-normal', 'rr-laugh', 'rr-normal2', 'rr-laugh2', 'rr-pouty',
         'rr-wedding', 'rr-veiled', 'rr-pregnant', 'rr-mother']

def dist(c, ref):
    return abs(c[0]-ref[0]) + abs(c[1]-ref[1]) + abs(c[2]-ref[2])

def recut(name):
    img = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    w, h = img.size
    px = img.load()
    # 背景参考色：四边中位数
    rs, gs, bs = [], [], []
    for x in range(0, w, 4):
        for y in (0, h-1):
            c = px[x, y]; rs.append(c[0]); gs.append(c[1]); bs.append(c[2])
    for y in range(0, h, 4):
        for x in (0, w-1):
            c = px[x, y]; rs.append(c[0]); gs.append(c[1]); bs.append(c[2])
    rs.sort(); gs.sort(); bs.sort()
    ref = (rs[len(rs)//2], gs[len(gs)//2], bs[len(bs)//2])
    # 边缘泛洪
    visited = bytearray(w*h)
    q = deque()
    for x in range(w):
        for y in (0, h-1):
            if not visited[y*w+x] and dist(px[x, y], ref) <= T:
                visited[y*w+x] = 1; q.append((x, y))
    for y in range(h):
        for x in (0, w-1):
            if not visited[y*w+x] and dist(px[x, y], ref) <= T:
                visited[y*w+x] = 1; q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny*w+nx]:
                if dist(px[nx, ny], ref) <= T:
                    visited[ny*w+nx] = 1; q.append((nx, ny))
    # 羽化：与已清区相邻且颜色接近的像素也清掉
    edge = set()
    for y in range(h):
        base = y*w
        for x in range(w):
            if not visited[base+x]:
                if ((x > 0 and visited[base+x-1]) or (x < w-1 and visited[base+x+1])
                        or (y > 0 and visited[base+x-w]) or (y < h-1 and visited[base+x+w])):
                    if dist(px[x, y], ref) <= T2:
                        edge.add(base+x)
    for i in edge:
        visited[i] = 1
    # 透明化
    out = Image.new('RGBA', (w, h))
    opx = out.load()
    for y in range(h):
        base = y*w
        for x in range(w):
            if visited[base+x]:
                opx[x, y] = (0, 0, 0, 0)
            else:
                opx[x, y] = px[x, y] + (255,)
    # 大组件保留（清除水印残留/碎屑）
    comp = [0]*(w*h)
    sizes = {}
    cid = 0
    for i in range(w*h):
        if not visited[i] and comp[i] == 0:
            cid += 1
            q2 = deque([i]); comp[i] = cid; n = 0
            while q2:
                j = q2.popleft(); n += 1
                x, y = j % w, j // w
                for nj in ((j+1 if x < w-1 else -1), (j-1 if x > 0 else -1),
                           (j+w if y < h-1 else -1), (j-w if y > 0 else -1)):
                    if nj >= 0 and not visited[nj] and comp[nj] == 0:
                        comp[nj] = cid; q2.append(nj)
            sizes[cid] = n
    if sizes:
        biggest = max(sizes.values())
        keep = {c for c, n in sizes.items() if n >= max(1500, biggest*0.04)}
        opx2 = out.load()
        for i in range(w*h):
            if not visited[i] and comp[i] not in keep:
                x, y = i % w, i // w
                opx2[x, y] = (0, 0, 0, 0)
    # 裁剪 + 缩放
    bbox = out.split()[3].getbbox()
    out = out.crop(bbox)
    w2, h2 = out.size
    if h2 > 820:
        out = out.resize((max(1, int(w2*820/h2)), 820), Image.LANCZOS)
    out.save(os.path.join(BASE, name + '.webp'), 'WEBP', quality=88, method=6)
    print('recut', name, out.size, os.path.getsize(os.path.join(BASE, name + '.webp')))

for n in CHARS:
    recut(n)
print('all done')
