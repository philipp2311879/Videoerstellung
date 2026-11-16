"""Gemeinsamer Baukasten für die Tafel-Reels (15.11.2026), 1:1 aus dem Wortwolke-Reel v2 (11k Views in 12 h, 28k nach 2 Tagen).

Nutzer, 15.11.2026: „Mach für weitere Tools solche Videos, auch mit so einer Hook, dem Design … baue es identisch mit den
gleichen Skills.“ Nicht für Glücksrad und Klassenraumplaner.

Look: KI-Klassenraum (raeume/klassenraum-gruen), echte App-Aufnahme perspektivisch auf dem grünen Bildschirm, Kamera steht
fest wie ein Handy hinten im Raum, leichtes Kamerarauschen, nur am Ende eine Fahrt auf das Ergebnis, Hook oben, zweiter Satz,
Endkarte (Sticker + „Kommentiere WORT“ + lehrerkoffer.de), leise Mixkit-Effekte aus werkzeuge/video-shotcraft.

Ein Reel ist ein Skript (z. B. 01-Umfrage/schnitt/bauen.py) mit:
  QUELLEN = {'name': Pfad zum Video}       Aufnahmen aus der Demo (1920x1080 oder 3840x2160)
  def tafel(t) -> (name, quellzeit)        was zur Reel-Zeit t auf der Tafel läuft
  DAUER, T_ZOOM, ZOOM_DAUER, ZIEL_RAHMEN   Länge, Beginn und Dauer der Fahrt, Ziel (fx, fy, breite, hoch)
  TEXTE = [(png, von, bis), ...]           Texte aus texte/*.png (texte.cjs)
  AUSGABE                                   Pfad des fertigen Reels
und ruft am Ende tafelreel.main(__file__) auf. Aufruf: python bauen.py [--probe 1,5,9]
"""
import importlib.util, json, math, os, pathlib, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = pathlib.Path(__file__).resolve().parents[1]
# Anderer Raum (16.11.2026, Satzbaustelle v2): vor dem Import os.environ['TAFELREEL_RAUM'] auf einen Ordner mit
# klassenraum-4x.png, gruen-maske.png und ecken.json setzen (z. B. raeume/klassenraum-lichterkette); ein Reel kann
# FEST (cx, cy, breite) selbst festlegen.
RAUM = pathlib.Path(os.environ.get('TAFELREEL_RAUM', REPO / 'raeume' / 'klassenraum-gruen'))
SFX = REPO / 'werkzeuge' / 'video-shotcraft' / 'assets' / 'audio' / 'sfx'
W, H, FPS = 1080, 1920, 30

FOTO = Image.open(RAUM / 'klassenraum-4x.png').convert('RGB')
MASKE = Image.open(RAUM / 'gruen-maske.png').convert('L')
FW, FH = FOTO.size
BOARD = np.array(json.load(open(RAUM / 'ecken.json'))['board'], float)       # OL, OR, UR, UL (4x)
FOTO2, MASKE2 = FOTO.reduce(2), MASKE.reduce(2)


def homographie(src, dst):
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    h = np.linalg.solve(np.array(A, float), np.array(b, float))
    return np.append(h, 1).reshape(3, 3)


def ecken(w, h):
    return np.array([[0, 0], [w, 0], [w, h], [0, h]], float)


H_BOARD = homographie(ecken(1, 1), BOARD)


def tafelpunkt(fx, fy):
    p = H_BOARD @ [fx, fy, 1]
    return p[0] / p[2], p[1] / p[2]


def tafel_rahmen(fx, fy, w, hoch=.5):
    x, y = tafelpunkt(fx, fy)
    h = w * 16 / 9
    return np.array([x, y - h * (hoch - .5), w])


def glatt(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


FEST = tafel_rahmen(.5, .5, 2500, .44)            # wie Wortwolke v2


class Quelle:
    """Liest ein Video der Reihe nach; at(t) mit nicht fallendem t. Startet ffmpeg erst beim ersten Aufruf (mit -ss)."""
    def __init__(self, pfad):
        self.pfad = str(pfad)
        info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height',
                               '-of', 'csv=p=0', self.pfad], capture_output=True, text=True).stdout.strip().split(',')
        self.w, self.h = int(info[0]), int(info[1])
        dauer = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', self.pfad],
                                     capture_output=True, text=True).stdout.strip())
        self.letztes = int(dauer * FPS) - 3
        self.p, self.n, self.bild = None, -1, None

    def at(self, t):
        ziel = min(max(0, int(round(t * FPS))), self.letztes)
        if self.p is not None and ziel < self.n:          # rückwärts: neu starten
            self.p.kill()
            self.p = None
        if self.p is None:
            start = max(0, ziel - 2)
            self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{start / FPS:.4f}', '-i', self.pfad, '-f', 'rawvideo',
                                       '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.n = start - 1
        while self.n < ziel:
            roh = self.p.stdout.read(self.w * self.h * 3)
            if len(roh) < self.w * self.h * 3:
                break
            self.n += 1
            self.bild = roh
        return Image.frombuffer('RGB', (self.w, self.h), self.bild, 'raw', 'RGB', 0, 1)

    def zu(self):
        if self.p:
            self.p.kill()


# ---------- Bildschirm-Look (aus 32-Wortwolke/schnitt/bauen.py) ----------
_LK = {}


def licht(w, h, staerke, glanz):
    fx = np.linspace(0, 1, w)[None, :]
    fy = np.linspace(0, 1, h)[:, None]
    lum = 1 - staerke * (.7 * fx + .3 * fy)
    band = np.exp(-((fx * .8 + fy * .6 - .32) / .16) ** 2) * glanz
    return lum.astype(np.float32), band.astype(np.float32)


def bildschirm_look(img, staerke=.06, glanz=.05, schwarz=6, mal=1.0):
    k = (img.size, staerke, glanz)
    if k not in _LK:
        _LK[k] = licht(img.size[0], img.size[1], staerke, glanz)
    lum, band = _LK[k]
    a = np.asarray(img).astype(np.float32)
    g = a.mean(2, keepdims=True)
    a = g + (a - g) * .95
    a = a * (lum[..., None] * mal) * np.array([.975, .985, 1.0], np.float32)
    a = schwarz + a * (1 - schwarz / 255)
    a = a + (255 - a) * band[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def einsetzen(ziel, quelle, quad_foto, kam, alpha, weich=0.0):
    x0, y0, w, h = kam
    s = W / w
    quad = (quad_foto - [x0, y0]) * s
    breite = max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[3]))
    if breite * 1.25 < quelle.size[0]:
        f = max(breite * 1.25 / quelle.size[0], .1)
        quelle = quelle.resize((max(2, int(quelle.size[0] * f)), max(2, int(quelle.size[1] * f))), Image.LANCZOS)
    if SCHAERFE:
        quelle = quelle.filter(ImageFilter.UnsharpMask(radius=1.1, percent=SCHAERFE, threshold=2))
    quelle = bildschirm_look(quelle)
    if weich:
        quelle = quelle.filter(ImageFilter.GaussianBlur(weich))
    Hm = homographie(quad, ecken(*quelle.size))
    Hm = Hm / Hm[2, 2]
    gewarpt = quelle.transform((W, H), Image.PERSPECTIVE, tuple(Hm.reshape(-1)[:8]), Image.BICUBIC)
    return Image.composite(gewarpt, ziel, alpha)


def kamera(t, R):
    ziel = tafel_rahmen(*R.ZIEL_RAHMEN)
    u = glatt((t - R.T_ZOOM) / R.ZOOM_DAUER)
    fest = np.array(getattr(R, 'FEST', FEST), float)
    cx, cy, w = fest + (ziel - fest) * u
    h = w * 16 / 9
    return min(max(cx - w / 2, 0), FW - w), min(max(cy - h / 2, 0), FH - h), w, h


# ---------- Texte ----------
_TX = {}


def text_laden(pfad):
    pfad = str(pfad)
    if pfad not in _TX:
        im = Image.open(pfad).convert('RGBA')
        _TX[pfad] = (im, im.getbbox())
    return _TX[pfad]


def text_drauf(bild, t, texte):
    for pfad, a, e in texte:
        if t < a or t > e:
            continue
        im, bb = text_laden(pfad)
        u = 1.0 if a == 0.0 else min(1.0, (t - a) / .22)
        v = min(1.0, (e - t) / .18)
        alpha = min(u, v)
        s = .9 + .1 * (1 - (1 - u) ** 3)
        teil = im.crop(bb)
        if s < .999:
            teil = teil.resize((max(1, int(teil.size[0] * s)), max(1, int(teil.size[1] * s))), Image.BICUBIC)
        if alpha < .999:
            r, g, b_, al = teil.split()
            al = al.point(lambda p: int(p * alpha))
            teil = Image.merge('RGBA', (r, g, b_, al))
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        bild.paste(teil, (int(cx - teil.size[0] / 2), int(cy - teil.size[1] / 2)), teil)
    return bild


# ---------- Bauen ----------
def raum_mit_tafel(tafelbild, kam):
    x0, y0, w, h = kam
    if w > 2200:
        foto, mfoto, box = FOTO2, MASKE2, (x0 / 2, y0 / 2, (x0 + w) / 2, (y0 + h) / 2)
    else:
        foto, mfoto, box = FOTO, MASKE, (x0, y0, x0 + w, y0 + h)
    bild = foto.resize((W, H), Image.BICUBIC, box=box, reducing_gap=2.0)
    maske = mfoto.resize((W, H), Image.BILINEAR, box=box, reducing_gap=2.0)
    return einsetzen(bild, tafelbild, BOARD, kam, maske, weich=WEICH)


WEICH = .35          # Weichzeichner der eingesetzten Tafel; ein Reel kann T.WEICH = 0 setzen (Satzbaustelle v2: Steine scharf)
SCHAERFE = 0         # Nachschärfen der verkleinerten Tafel in Prozent (UnsharpMask), 0 = aus wie bisher


def bild_bei(R, t, q, i):
    kam = kamera(t, R)
    name, ts = R.tafel(t)
    tafelbild = q[name].at(ts)
    if hasattr(R, 'vorbereiten'):                        # z. B. App auf die Steinfläche zuschneiden (Satzbaustelle v2)
        tafelbild = R.vorbereiten(tafelbild, t)
    bild = raum_mit_tafel(tafelbild, kam)
    a = np.asarray(bild).astype(np.int16)
    rausch = np.random.default_rng(i).normal(0, 2.4, (H, W, 1)).astype(np.int16)
    bild = Image.fromarray(np.clip(a + rausch, 0, 255).astype(np.uint8))
    return text_drauf(bild, t, R.TEXTE)


def reel_laden(pfad):
    spec = importlib.util.spec_from_file_location('reel', pfad)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['reel'] = mod
    spec.loader.exec_module(mod)
    return mod


_R = None


def _init(pfad):
    global _R
    _R = reel_laden(pfad)


def quellen(R):
    return {k: Quelle(v) for k, v in R.QUELLEN.items()}


def stueck(args):
    i0, i1, pfad = args
    R = _R
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', pfad],
                           stdin=subprocess.PIPE)
    q = quellen(R)
    for i in range(i0, i1):
        enc.stdin.write(bild_bei(R, i / FPS, q, i).tobytes())
    enc.stdin.close()
    enc.wait()
    for x in q.values():
        x.zu()
    return pfad


def main(pfad):
    R = sys.modules.get('__main__')
    aus = pathlib.Path(R.AUSGABE)
    aus.parent.mkdir(parents=True, exist_ok=True)
    print('Dauer', R.DAUER, 'Zoom ab', round(R.T_ZOOM, 2))
    if '--probe' in sys.argv:
        ziel = aus.parent / 'probe'
        ziel.mkdir(parents=True, exist_ok=True)
        q = quellen(R)
        for t in sorted(float(x) for x in sys.argv[sys.argv.index('--probe') + 1].split(',')):
            bild_bei(R, t, q, int(t * FPS)).save(ziel / f'probe-{t:05.2f}.jpg', quality=90)
        print('Proben in', ziel)
        return
    from multiprocessing import Pool
    teile = aus.parent / '_teile'
    teile.mkdir(parents=True, exist_ok=True)
    n = int(R.DAUER * FPS)
    k = max(2, min(10, (os.cpu_count() or 4) - 1))          # 10 Teile parallel auf dem PC von Philipp, sonst weniger
    grenzen = [round(n * j / k) for j in range(k + 1)]
    auftraege = [(grenzen[j], grenzen[j + 1], str(teile / f'teil-{j:02d}.mp4')) for j in range(k)]
    with Pool(k, initializer=_init, initargs=(str(pathlib.Path(pfad).resolve()),)) as pool:
        for p in pool.imap_unordered(stueck, auftraege):
            print('fertig', pathlib.Path(p).name, flush=True)
    (teile / 'liste.txt').write_text('\n'.join(f"file '{a[2].replace(chr(92), '/')}'" for a in auftraege))
    ton = getattr(R, 'TON', None)
    if ton and pathlib.Path(ton).exists():
        audio = ['-i', str(ton)]
    else:
        audio = ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(teile / 'liste.txt'), *audio,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', str(aus)], check=True)
    for f in teile.iterdir():
        f.unlink()
    teile.rmdir()
    print('fertig', aus)


# ---------- Ton (aus 32-Wortwolke/schnitt/ton.py) ----------
SR = 48000


def sfx(rel):
    roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SFX / rel), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True).stdout
    a = np.frombuffer(roh, np.float32).copy()
    return a / (np.abs(a).max() + 1e-9)


def db(x):
    return 10 ** (x / 20)


def ton_schreiben(ereignisse, dauer, aus):
    """ereignisse: Liste (probe, zeit, dB). Spitze auf -3 dBFS, Stereo 48 kHz."""
    n = int(dauer * SR) + SR
    spur = np.zeros(n, np.float32)
    for probe, t, g in ereignisse:
        i = int(t * SR)
        if 0 <= i < n:
            e = min(n, i + len(probe))
            spur[i:e] += probe[:e - i] * db(g)
    spitze = np.abs(spur).max()
    if spitze > 0:
        spur *= db(-3) / spitze
    pcm = (np.clip(np.stack([spur, spur], 1)[:int(dauer * SR)], -1, 1) * 32767).astype('<i2')
    with wave.open(str(aus), 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    print('Ton', len(ereignisse), 'Ereignisse ->', aus)


def wechsel_zeiten(pfad, schwelle=.35, abstand=.16, y0=12, bereich=None):
    """Zeitpunkte (Quellzeit), an denen sich im Video etwas sichtbar ändert (z. B. ein neues Wort, ein neuer Punkt).
    bereich = (x0, y0, x1, y1) als Bruchteile, um nur einen Teil des Bildes anzusehen."""
    w, h = 192, 108
    roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(pfad), '-vf', f'scale={w}:{h}', '-f', 'rawvideo',
                          '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    f = np.frombuffer(roh, np.uint8).reshape(-1, h, w).astype(np.int16)
    if bereich:
        bx0, by0, bx1, by1 = bereich
        f = f[:, int(by0 * h):int(by1 * h), int(bx0 * w):int(bx1 * w)]
    else:
        f = f[:, y0:, :]
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    zeiten, letzte = [], -9
    for i, v in enumerate(d):
        t = (i + 1) / FPS
        if v > schwelle and t - letzte > abstand:
            zeiten.append(t)
            letzte = t
    return zeiten, d


# ---------- Titelbild (aus 32-Wortwolke/schnitt/titelbild.py) ----------
def titelbild(quelle_pfad, zeit, titel_png, aus_ordner, rahmen=(.5, .5, 2350, .30), flicken=(), vorbereiten=None):
    """flicken: Kästen (x0, y0, x1, y1) in Quellpixeln, die mit der Farbe direkt darüber gefüllt werden (Mauszeiger weg).
    vorbereiten: wie R.vorbereiten(bild, t) im Reel (z. B. Zuschnitt), wird nach dem Flicken angewandt."""
    cx, cy, w = tafel_rahmen(*rahmen)
    h = w * 16 / 9
    kam = (min(max(cx - w / 2, 0), FW - w), min(max(cy - h / 2, 0), FH - h), w, h)
    q = Quelle(quelle_pfad)
    tafel = q.at(zeit).copy()
    q.zu()
    for x0, y0, x1, y1 in flicken:
        streifen = np.asarray(tafel.crop((x0, y0 - 6, x1, y0 - 1))).reshape(-1, 3)
        ImageDraw.Draw(tafel).rectangle((x0, y0, x1, y1), fill=tuple(int(v) for v in np.median(streifen, 0)))
    if vorbereiten:
        tafel = vorbereiten(tafel, zeit)
    x0, y0, w, h = kam
    box = (x0, y0, x0 + w, y0 + h)
    bild = FOTO.resize((W, H), Image.BICUBIC, box=box, reducing_gap=2.0)
    maske = MASKE.resize((W, H), Image.BILINEAR, box=box, reducing_gap=2.0)
    bild = einsetzen(bild, tafel, BOARD, kam, maske)
    titel = Image.open(titel_png).convert('RGBA')
    bild = bild.convert('RGB')
    bild.paste(titel, (0, 0), titel)
    aus_ordner = pathlib.Path(aus_ordner)
    aus_ordner.mkdir(parents=True, exist_ok=True)
    bild.save(aus_ordner / 'Titelbild.jpg', quality=93)
    bild.crop((0, 240, 1080, 1680)).save(aus_ordner / 'Titelbild-3x4-Vorschau.jpg', quality=90)
    print('Titelbild ->', aus_ordner / 'Titelbild.jpg')
