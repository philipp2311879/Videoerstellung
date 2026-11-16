"""Ecken der grünen Tafel im Klassenraum mit Lichterkette (Nutzer, 16.11.2026) finden, wie 32-Wortwolke/raum/ecken.py.

klassenraum-4x.png (Real-ESRGAN x4plus aus klassenraum-lichterkette.webp) -> ecken.json (Ecken oben links, oben rechts,
unten rechts, unten links, in 4x-Pixeln; Kanten als Geraden gefittet) und gruen-maske.png (weiche Maske der grünen Fläche, 4x).
Aufruf: python ecken.py
"""
import json, pathlib
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

RAUM = pathlib.Path(__file__).resolve().parent
img = np.asarray(Image.open(RAUM / 'klassenraum-4x.png').convert('RGB')).astype(np.int32)
r, g, b = img[..., 0], img[..., 1], img[..., 2]

# Grün: wie stark G über R und B liegt (weich), harte Maske für die Ecken
gruen = np.clip((g - np.maximum(r, b) - 40) / 80.0, 0, 1)
hart = gruen > .5
ys, xs = np.nonzero(hart)
s, d = xs + ys, xs - ys
roh = [(xs[s.argmin()], ys[s.argmin()]), (xs[d.argmax()], ys[d.argmax()]), (xs[s.argmax()], ys[s.argmax()]), (xs[d.argmin()], ys[d.argmin()])]
print('Ecken roh', roh, 'Fläche', hart.sum())

# Kanten genauer: je Zeile/Spalte erster und letzter grüner Pixel, Geraden fitten (Mitte der Kante, Ränder weg)
x0, y0 = min(p[0] for p in roh), min(p[1] for p in roh)
x1, y1 = max(p[0] for p in roh), max(p[1] for p in roh)


def fit(ts, vs):
    ts, vs = np.array(ts, float), np.array(vs, float)
    for _ in range(3):
        a, c = np.polyfit(ts, vs, 1)
        rest = np.abs(vs - (a * ts + c))
        ok = rest < max(1.5, np.percentile(rest, 85))
        ts, vs = ts[ok], vs[ok]
    return np.polyfit(ts, vs, 1)


rand = 40
li, re, zy = [], [], []
for y in range(y0 + rand, y1 - rand, 4):
    z = np.flatnonzero(hart[y, x0 - 20:x1 + 20])
    if len(z) > (x1 - x0) * .8:
        zy.append(y); li.append(z[0] + x0 - 20); re.append(z[-1] + x0 - 20 + 1)
ob, un, sx = [], [], []
for x in range(x0 + rand, x1 - rand, 4):
    z = np.flatnonzero(hart[y0 - 20:y1 + 20, x])
    if len(z) > (y1 - y0) * .8:
        sx.append(x); ob.append(z[0] + y0 - 20); un.append(z[-1] + y0 - 20 + 1)
L, R = fit(zy, li), fit(zy, re)          # x = a*y + c
O, U = fit(sx, ob), fit(sx, un)          # y = a*x + c


def schnitt(kx, ky):
    a, c = kx
    e, f = ky
    x = (a * f + c) / (1 - a * e)
    return [x, e * x + f]


board = [schnitt(L, O), schnitt(R, O), schnitt(R, U), schnitt(L, U)]
print('Board (gefittet)', [[round(v, 1) for v in p] for p in board])

# Weiche Maske: leicht nach außen wachsen lassen, damit kein grüner Saum am Rahmen bleibt
m = Image.fromarray((gruen * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
m.save(RAUM / 'gruen-maske.png')

json.dump({'board': [[round(v, 1) for v in p] for p in board], 'roh': [list(map(int, p)) for p in roh]},
          open(RAUM / 'ecken.json', 'w'), indent=1)

# Kontrollbild: ganzes Bild klein + vier Ecken vergrößert
vor = Image.open(RAUM / 'klassenraum-4x.png').convert('RGB')
klein = vor.resize((941, 1672))
dr = ImageDraw.Draw(klein)
dr.polygon([(x / 4, y / 4) for x, y in board], outline=(255, 0, 0))
lupen = Image.new('RGB', (4 * 300, 300), 'white')
for i, (x, y) in enumerate(board):
    teil = vor.crop((int(x) - 60, int(y) - 60, int(x) + 60, int(y) + 60)).resize((300, 300), Image.NEAREST)
    dd = ImageDraw.Draw(teil)
    px, py = (x - (int(x) - 60)) * 2.5, (y - (int(y) - 60)) * 2.5
    dd.line((px - 30, py, px + 30, py), fill=(255, 0, 0)); dd.line((px, py - 30, px, py + 30), fill=(255, 0, 0))
    lupen.paste(teil, (i * 300, 0))
klein.save(RAUM / 'ecken-kontrolle.png')
lupen.save(RAUM / 'ecken-lupen.png')
print('fertig')
