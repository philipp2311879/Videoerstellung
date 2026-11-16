"""Ecken des grünen Smartboards und des iPad-Bildschirms im KI-Klassenraum (Nutzer, 14.11.2026) finden.

klassenraum-4x.png (Real-ESRGAN x4 aus klassenraum-original.webp) -> ecken.json (Ecken oben links, oben rechts,
unten rechts, unten links, in 4x-Pixeln) und gruen-maske.png (weiche Maske der grünen Fläche, 4x).
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
board = [(xs[s.argmin()], ys[s.argmin()]), (xs[d.argmax()], ys[d.argmax()]), (xs[s.argmax()], ys[s.argmax()]), (xs[d.argmin()], ys[d.argmin()])]
print('Board', board, 'Fläche', hart.sum())

# Weiche Maske: leicht nach außen wachsen lassen, damit kein grüner Saum am Rahmen bleibt
m = Image.fromarray((gruen * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
m.save(RAUM / 'gruen-maske.png')

# iPad vorne links: dunkle Fläche im Bereich des Tisches (Original etwa x 210–515, y 1235–1390 -> 4x)
x0, y0, x1, y1 = 800, 4880, 2120, 5620
teil = img[y0:y1, x0:x1]
dunkel = (teil.max(axis=2) < 70)
lab = dunkel
ys2, xs2 = np.nonzero(lab)
xs2, ys2 = xs2 + x0, ys2 + y0
s2, d2 = xs2 + ys2, xs2 - ys2
ipad = [(xs2[s2.argmin()], ys2[s2.argmin()]), (xs2[d2.argmax()], ys2[d2.argmax()]), (xs2[s2.argmax()], ys2[s2.argmax()]), (xs2[d2.argmin()], ys2[d2.argmin()])]
print('iPad dunkel', ipad, 'Fläche', lab.sum())

json.dump({'board': [list(map(int, p)) for p in board], 'ipad_dunkel': [list(map(int, p)) for p in ipad]}, open(RAUM / 'ecken.json', 'w'), indent=1)

# Kontrollbild
vor = Image.open(RAUM / 'klassenraum-4x.png').convert('RGB').resize((1024, 1536))
dr = ImageDraw.Draw(vor)
dr.polygon([(x / 4, y / 4) for x, y in board], outline=(255, 0, 0))
dr.polygon([(x / 4, y / 4) for x, y in ipad], outline=(0, 0, 255))
vor.save(RAUM / 'ecken-kontrolle.png')
