"""Ecken der grünen Tafel (16:9) und des grünen iPads (hochkant) im neuen Klassenraum des Nutzers (15.11.2026).

klassenraum.webp (ChatGPT, 1024x1536) -> klassenraum-4x.png (Real-ESRGAN x4plus) -> ecken.json (je Fläche: oben links,
oben rechts, unten rechts, unten links, 4x-Pixel) und gruen-maske.png (weiche Maske beider grüner Flächen, 4x).
Aufruf: python ecken.py
"""
import json, pathlib
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

RAUM = pathlib.Path(__file__).resolve().parent
img = np.asarray(Image.open(RAUM / 'klassenraum-4x.png').convert('RGB')).astype(np.int32)
r, g, b = img[..., 0], img[..., 1], img[..., 2]
gruen = np.clip((g - np.maximum(r, b) - 40) / 80.0, 0, 1)
hart = gruen > .5
H, W = hart.shape


def ecken_von(maske):
    ys, xs = np.nonzero(maske)
    s, d = xs + ys, xs - ys
    return [(int(xs[s.argmin()]), int(ys[s.argmin()])), (int(xs[d.argmax()]), int(ys[d.argmax()])),
            (int(xs[s.argmax()]), int(ys[s.argmax()])), (int(xs[d.argmin()]), int(ys[d.argmin()]))], int(maske.sum())


oben = hart.copy(); oben[H // 2:] = False
unten = hart.copy(); unten[:H // 2] = False
board, fb = ecken_von(oben)
ipad, fi = ecken_von(unten)
for name, e, f in (('Tafel', board, fb), ('iPad', ipad, fi)):
    br = np.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]); ho = np.hypot(e[3][0] - e[0][0], e[3][1] - e[0][1])
    print(name, e, 'Fläche', f, 'Seitenverhältnis', round(br / ho, 3))
json.dump({'board': [list(p) for p in board], 'ipad': [list(p) for p in ipad]}, open(RAUM / 'ecken.json', 'w'), indent=1)

m = Image.fromarray((gruen * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
m.save(RAUM / 'gruen-maske.png')

vor = Image.open(RAUM / 'klassenraum-4x.png').convert('RGB').resize((1024, 1536))
dr = ImageDraw.Draw(vor)
dr.polygon([(x / 4, y / 4) for x, y in board], outline=(255, 0, 0))
dr.polygon([(x / 4, y / 4) for x, y in ipad], outline=(0, 0, 255))
vor.save(RAUM / 'ecken-kontrolle.png')
