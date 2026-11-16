"""Prüft im fertigen Reel, ob die Klaviertöne auf den Landungen liegen: Anschläge in der Tonspur vs. Bildwechsel im Tafel-Bereich.
Aufruf: python pruefe_sync.py"""
import pathlib, subprocess
import numpy as np

V = pathlib.Path(__file__).resolve().parent.parent / 'fertig' / 'Satzbaustelle-v2.mp4'
roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(V), '-ac', '1', '-ar', '8000', '-f', 'f32le', '-'], capture_output=True).stdout
a = np.abs(np.frombuffer(roh, np.float32))
blk = 80                                                     # 10 ms
h = a[:len(a) // blk * blk].reshape(-1, blk).max(1)
d = np.diff(h, prepend=0)
anschlaege, letzte = [], -1
for i in np.flatnonzero(d > .08 * h.max()):
    if i - letzte > 15:
        anschlaege.append(round(i * .01, 2))
    letzte = i
print('Anschläge (s):', anschlaege[:30])
w, hh = 108, 192
bild = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(V), '-vf', f'scale={w}:{hh}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
f = np.frombuffer(bild, np.uint8).reshape(-1, hh, w).astype(np.int16)[:, 45:105, :]   # Tafelbereich
dv = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
print('größte Bildwechsel (s):', sorted(round((i + 1) / 30, 2) for i in np.argsort(dv)[-14:]))
