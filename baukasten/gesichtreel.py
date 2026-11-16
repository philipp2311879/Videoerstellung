"""Baukasten für Reels mit Gesicht (Kamera-Takes, frei gesprochen) im Hausstil.

Zusammengeführt aus den Gesicht-Reels bis 16.11.2026 (Begriffe raten, Überfahrt, Quiz mit KI, Drachenei) und auf den
Hausstil vom 14.11. umgestellt (hausstil/HAUSSTIL.md):
  - Schnitt aus Teilen (Clip, von, bis), Seitenverhältnis immer erhalten (nie verzerren), 1080 x 1920, 30 fps.
  - Ton: ORIGINALTON (neues Mikro, Philipp 10.11.: „original Audio einfach drauf“). Nur jeden Teil gleich laut machen,
    am Ende feste Verstärkung auf LUFS (Standard −19, Philipp 15.11.: −16 war „bisschen laut“) + Begrenzer −1,5 dB.
    Keine Enthallung, kein EQ, kein Kompressor, keine selbst gemachte Musik. Leise Mixkit-Effekte dürfen dazu.
  - Untertitel: Inter ExtraBold 80 px, weiß mit dunklem Schein, 2–4 Wörter, eine Zeile, Mitte y 1240 (Brusthöhe),
    bei OBEN-Teilen y 700; *Wort* = gelb (höchstens eins pro Häppchen); kleiner Pop beim Einblenden.
  - Sticker-Titel (texte/oben.png) die ersten STICKER_BIS Sekunden groß oben, dann weg.
  - Endkarte (texte/ende.png): Sticker + „Kommentiere WORT“ + lehrerkoffer.de über dem letzten Bild, ENDKARTE Sekunden.
  - Titelbild aus einem Bild ohne Texte + texte/titel.png (Titel in der Mitte des 3:4-Ausschnitts).

Ein Reel ist ein Skript <Reel>/schnitt/bauen.py (Vorlage: py baukasten/neues_reel.py gesicht <name>) mit:
  AUFNAHMEN = Ordner mit den Clips (C0xxx.MP4)
  TEILE = [('H1', 'C0318', 10.50, 18.48, ['Kennst du das?', 'Spontan *Vertretung*']), ...]
  DREHEN = {'C0329': 'transpose=1'}   Clips ohne Drehungs-Angabe selbst drehen
  OBEN = {'S4'}                        Untertitel dieser Teile oben (wenn auf Brusthöhe etwas Wichtiges zu sehen ist)
  STICKER_BIS, ENDKARTE, LUFS, GERAEUSCHE = [('ui/ui-popup-dry.mp3', zeit, dB), ...], AUSGABE
und ruft gesichtreel.main(__file__) auf.

Aufruf:  python bauen.py --liste          Zeitleiste + Lautheit je Teil (nichts wird gebaut)
         python bauen.py --kontakt        Kontaktbögen je Teil alle 0,25 s -> fertig/kontakt/ (Blick und Augen prüfen)
         python bauen.py                  alles: Schnitt, Wortzeiten, Texte (node texte.cjs), Reel
         python bauen.py --render         nur neu rendern (nach Änderung an Texten oder Geräuschen)
         python bauen.py --titel 3.2      Titelbild aus Sekunde 3,2 des Schnitts (ohne Texte) + texte/titel.png
Wortzeiten: mit faster-whisper (pip install faster-whisper), sonst aus der Lautstärke verteilt (gröber, prüfen!).
"""
import difflib, importlib.util, json, math, os, pathlib, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw

REPO = pathlib.Path(__file__).resolve().parents[1]
SFX = REPO / 'werkzeuge' / 'video-shotcraft' / 'assets' / 'audio' / 'sfx'
W, H, FPS, SR = 1080, 1920, 30, 48000


# ---------- Hilfen ----------
def ff(*a, **k):
    return subprocess.run(['ffmpeg', '-hide_banner', '-y', '-loglevel', 'error', *a], check=True, **k)


def lautheit(pfad, von=None, bis=None):
    a = ['ffmpeg', '-hide_banner', '-nostats']
    if von is not None:
        a += ['-ss', f'{von}', '-t', f'{bis - von}']
    r = subprocess.run(a + ['-i', str(pfad), '-vn', '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True, errors='replace')
    werte = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    return float(werte[-1]) if werte else -70.0


def wav_lesen(pfad):
    with wave.open(str(pfad)) as w:
        n, k = w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), '<i2').astype(np.float32) / 32768
    return a.reshape(-1, k)


def wav_schreiben(pfad, a):
    a = np.clip(a, -1, 1)
    with wave.open(str(pfad), 'wb') as w:
        w.setnchannels(a.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype('<i2').tobytes())


def glatt(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def reel_laden(pfad):
    spec = importlib.util.spec_from_file_location('reel', pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Plan:
    """Zeitleiste aus TEILE: Start jedes Teils im Reel, Ende des Schnitts, Endkarte."""
    def __init__(self, R):
        self.R = R
        self.ordner = pathlib.Path(R.__file__).resolve().parent.parent
        self.tmp = self.ordner / 'fertig' / '_tmp'
        self.start, t = {}, 0.0
        for n, c, v, b, _ in R.TEILE:
            self.start[n] = t
            t += b - v
        self.t_karte = t
        self.endkarte = getattr(R, 'ENDKARTE', 2.0)
        self.gesamt = t + self.endkarte
        self.clips = sorted({x[1] for x in R.TEILE})

    def clip(self, c):
        for endung in ('.MP4', '.mp4', '.MOV', '.mov'):
            p = pathlib.Path(self.R.AUFNAHMEN) / f'{c}{endung}'
            if p.exists():
                return p
        sys.exit(f'Clip fehlt: {c} in {self.R.AUFNAHMEN}')


# ---------- 1. Schnitt ----------
def liste(P):
    print(f'{"Reel":>6}  Teil  Clip    von     bis    Lautheit  Untertitel')
    for n, c, v, b, h in P.R.TEILE:
        print(f'{P.start[n]:6.2f}  {n:4}  {c}  {v:6.2f}  {b:6.2f}  {lautheit(P.clip(c), v, b):6.1f}    {" / ".join(h)}')
    print(f'Schnitt {P.t_karte:.2f} s + Endkarte {P.endkarte:.1f} s = {P.gesamt:.2f} s')


def basis(P):
    P.tmp.mkdir(parents=True, exist_ok=True)
    f, cmd = [], []
    for c in P.clips:
        cmd += ['-i', str(P.clip(c))]
    dreh = getattr(P.R, 'DREHEN', {})
    for k, (n, c, v, b, _) in enumerate(P.R.TEILE):
        i = P.clips.index(c)
        d = dreh.get(c, '')
        d = d + ',' if d else ''
        f.append(f'[{i}:v]trim={v}:{b},setpts=PTS-STARTPTS,{d}scale={W}:{H}:force_original_aspect_ratio=increase,'
                 f'crop={W}:{H},setsar=1,fps={FPS}[v{k}]')
        gain = -20.0 - lautheit(P.clip(c), v, b)
        f.append(f'[{i}:a]atrim={v:.3f}:{b:.3f},asetpts=PTS-STARTPTS,aresample={SR},aformat=channel_layouts=stereo,'
                 f'volume={gain:.1f}dB,afade=t=in:d=0.01,afade=t=out:st={max(0, b - v - 0.01):.3f}:d=0.01[a{k}]')
    n = len(P.R.TEILE)
    f.append(''.join(f'[v{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[v]')
    f.append(''.join(f'[a{k}]' for k in range(n)) + f'concat=n={n}:v=0:a=1[a]')
    ff(*cmd, '-filter_complex', ';'.join(f), '-map', '[v]', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast',
       '-pix_fmt', 'yuv420p', '-an', str(P.tmp / 'basis.mp4'), '-map', '[a]', '-c:a', 'pcm_s16le', str(P.tmp / 'stimme.wav'))
    print(f'Schnitt fertig: {P.t_karte:.2f} s')


# ---------- 2. Wortzeiten ----------
def norm(s):
    return re.sub(r'[^a-zäöüß0-9]', '', s.lower())


def sprechspanne(mono, t0, t1):
    """Erster und letzter Sprach-Rahmen im Fenster (20 ms, Schwelle 95.-Perzentil − 25 dB)."""
    x = mono[int(t0 * SR):int(t1 * SR)]
    n = int(.02 * SR)
    if len(x) < n * 3:
        return t0, t1
    e = 10 * np.log10((x[:len(x) // n * n].reshape(-1, n) ** 2).mean(1) + 1e-12)
    an = np.where(e > np.percentile(e, 95) - 25)[0]
    return (t0 + an[0] * .02, t0 + (an[-1] + 1) * .02) if len(an) else (t0, t1)


def whisper_woerter(mono16, t0, t1):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    global _MODELL
    if '_MODELL' not in globals():
        name = os.environ.get('WHISPER_MODELL', 'small')
        print('Whisper-Modell', name, '(erstes Mal lädt es herunter)')
        _MODELL = WhisperModel(name, device='auto', compute_type='int8')
    stueck = mono16[int(t0 * 16000):int(t1 * 16000)]
    segs, _ = _MODELL.transcribe(stueck, language='de', word_timestamps=True, vad_filter=False)
    return [(w.word, t0 + w.start, t0 + w.end) for s in segs for w in (s.words or [])]


def zeiten(P):
    stimme = wav_lesen(P.tmp / 'stimme.wav').mean(1)
    mono16 = None
    haeppchen, ut_json = [], []
    oben = getattr(P.R, 'OBEN', set())
    whisper_da = importlib.util.find_spec('faster_whisper') is not None
    if whisper_da:
        ff('-i', str(P.tmp / 'stimme.wav'), '-ar', '16000', '-ac', '1', '-f', 'f32le', str(P.tmp / 'stimme16.raw'))
        mono16 = np.fromfile(P.tmp / 'stimme16.raw', np.float32)
    else:
        print('Hinweis: faster-whisper fehlt, Untertitel-Zeiten werden aus der Lautstärke verteilt (gröber, im Reel prüfen).')
    for n, c, v, b, teile in P.R.TEILE:
        if not teile:
            continue
        t0, t1 = P.start[n], P.start[n] + (b - v)
        a0, a1 = sprechspanne(stimme, t0, t1)
        woerter = [w for h in teile for w in h.replace('*', '').split()]
        st = [None] * len(woerter)
        ww = whisper_woerter(mono16, t0, t1) if whisper_da else None
        if ww:
            ww = [w for w in ww if norm(w[0])]
            sm = difflib.SequenceMatcher(a=[norm(w) for w in woerter], b=[norm(w[0]) for w in ww], autojunk=False)
            for blk in sm.get_matching_blocks():
                for j in range(blk.size):
                    st[blk.a + j] = ww[blk.b + j][1]
        if st[0] is None or st[0] < a0 - .05:
            st[0] = a0
        # Lücken nach Buchstaben verteilen
        laenge = [max(2, len(norm(w))) for w in woerter]
        for j in range(len(woerter)):
            if st[j] is None:
                r = next((q for q in range(j + 1, len(woerter)) if st[q] is not None), None)
                rechts = st[r] if r is not None else a1
                bis_r = (r if r is not None else len(woerter))
                anteil = laenge[j - 1] / sum(laenge[j - 1:bis_r]) if j else 0
                st[j] = st[j - 1] + (rechts - st[j - 1]) * anteil
        idx = 0
        for h in teile:
            von = st[idx]
            idx += len(h.replace('*', '').split())
            bis = st[idx] if idx < len(woerter) else min(t1, a1 + .25)
            haeppchen.append((round(von, 3), round(max(bis, von + .3), 3), len(ut_json)))
            ut_json.append({'text': h, 'oben': n in oben})
    (P.ordner / 'texte').mkdir(exist_ok=True)
    (P.ordner / 'texte' / 'untertitel.json').write_text(json.dumps(ut_json, ensure_ascii=False, indent=1), encoding='utf-8')
    (P.tmp / 'zeiten.json').write_text(json.dumps(haeppchen), encoding='utf-8')
    for von, bis, i in haeppchen:
        print(f'{von:6.2f}-{bis:6.2f}  {"oben " if ut_json[i]["oben"] else ""}{ut_json[i]["text"]}')


def texte(P):
    if not (P.ordner / 'texte' / 'texte.json').exists():
        sys.exit('Fehlt: texte/texte.json (sticker, pille, pille_oben, wort, reihe). Vorlage: baukasten/neues_reel.py')
    subprocess.run(['node', str(REPO / 'baukasten' / 'texte.cjs'), str(P.ordner)], check=True)


# ---------- 3. Ton ----------
def sfx(rel):
    roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SFX / rel), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(roh, np.float32).copy().reshape(-1, 2)
    return a / (np.abs(a).max() + 1e-9)


def mischen(P):
    n = int(P.gesamt * SR)
    st = wav_lesen(P.tmp / 'stimme.wav')
    mix = np.zeros((n, 2), np.float32)
    mix[:min(n, len(st))] += st[:n]
    for rel, t, db in getattr(P.R, 'GERAEUSCHE', []):
        s = sfx(rel) * 10 ** (db / 20) * 10 ** (-20 / 20)      # dB relativ zur Stimme (die liegt bei −20 LUFS)
        i = int(t * SR)
        if 0 <= i < n:
            e = min(n, i + len(s))
            mix[i:e] += s[:e - i]
    wav_schreiben(P.tmp / 'mix.wav', mix / max(1.0, np.abs(mix).max()))
    ziel = getattr(P.R, 'LUFS', -19.0)
    return ziel - lautheit(P.tmp / 'mix.wav')


# ---------- 4. Bild ----------
_TX = {}


def png(pfad):
    pfad = str(pfad)
    if pfad not in _TX:
        im = Image.open(pfad).convert('RGBA')
        bb = im.getbbox() or (0, 0, 1, 1)
        _TX[pfad] = (im.crop(bb), bb)
    return _TX[pfad]


def drauf(bild, pfad, alpha=1.0, s=1.0):
    teil, bb = png(pfad)
    if s < .999:
        teil = teil.resize((max(1, int(teil.size[0] * s)), max(1, int(teil.size[1] * s))), Image.BICUBIC)
    if alpha < .999:
        r, g, b_, al = teil.split()
        teil = Image.merge('RGBA', (r, g, b_, al.point(lambda p: int(p * alpha))))
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    bild.alpha_composite(teil, (int(cx - teil.size[0] / 2), int(cy - teil.size[1] / 2)))


def render(P):
    tx = P.ordner / 'texte'
    hp = json.loads((P.tmp / 'zeiten.json').read_text(encoding='utf-8'))
    gain = mischen(P)
    ziel = pathlib.Path(P.R.AUSGABE)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    sticker_bis = getattr(P.R, 'STICKER_BIS', 2.0)
    lesen = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', str(P.tmp / 'basis.mp4'), '-f', 'rawvideo',
                              '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    schreiben = subprocess.Popen(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
         '-i', '-', '-i', str(P.tmp / 'mix.wav'),
         # level=false: sonst hebt alimiter alles wieder auf 0 dBFS an (+1,5 dB lauter als gewollt)
         '-af', f'volume={gain:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=false,aresample={SR}',
         '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '256k', '-ac', '2', '-shortest', '-movflags', '+faststart', str(ziel)],
        stdin=subprocess.PIPE)
    groesse, letztes, nr = W * H * 3, None, 0
    while nr / FPS < P.gesamt - 1e-6:
        t = nr / FPS
        roh = lesen.stdout.read(groesse) if t < P.t_karte else b''
        if len(roh) < groesse:
            roh = letztes
        letztes = roh
        img = Image.frombuffer('RGB', (W, H), roh, 'raw', 'RGB', 0, 1)
        if t >= P.t_karte:                                       # Endkarte: letztes Bild, sanft abgedunkelt
            u = glatt((t - P.t_karte) / .3)
            img = Image.eval(img, lambda v, f=1 - .3 * u: int(v * f))
        img = img.convert('RGBA')
        if t < sticker_bis and (tx / 'oben.png').exists():
            drauf(img, tx / 'oben.png', alpha=min(1.0, (sticker_bis - t) / .25))
        if t < P.t_karte:
            for von, bis, i in hp:
                if von <= t < bis:
                    u = (t - von) / .12
                    drauf(img, tx / f'ut-{i:03d}.png', alpha=min(1.0, u * 1.5), s=.9 + .1 * glatt(u))
                    break
        elif (tx / 'ende.png').exists():
            u = (t - P.t_karte - .1) / .25
            if u > 0:
                drauf(img, tx / 'ende.png', alpha=min(1.0, u), s=.9 + .1 * glatt(u))
        schreiben.stdin.write(img.convert('RGB').tobytes())
        nr += 1
    lesen.stdout.close()
    schreiben.stdin.close()
    schreiben.wait(); lesen.wait()
    print(f'fertig: {ziel}  ({nr / FPS:.2f} s, Ton {getattr(P.R, "LUFS", -19.0):.0f} LUFS)')


# ---------- 5. Kontaktbögen und Titelbild ----------
def kontakt(P):
    aus = P.ordner / 'fertig' / 'kontakt'
    aus.mkdir(parents=True, exist_ok=True)
    kw, kh, sp = 216, 384, 8
    dreh = getattr(P.R, 'DREHEN', {})
    for n, c, v, b, _ in P.R.TEILE:
        d = dreh.get(c, '')
        vf = (d + ',' if d else '') + f'fps=4,scale={kw}:{kh}:force_original_aspect_ratio=increase,crop={kw}:{kh}'
        roh = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{v}', '-t', f'{b - v}', '-i', str(P.clip(c)), '-vf', vf,
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
        bilder = [Image.frombuffer('RGB', (kw, kh), roh[i:i + kw * kh * 3], 'raw', 'RGB', 0, 1)
                  for i in range(0, len(roh) - kw * kh * 3 + 1, kw * kh * 3)]
        zeilen = math.ceil(len(bilder) / sp)
        blatt = Image.new('RGB', (kw * sp, kh * zeilen), 'white')
        for k, bi in enumerate(bilder):
            bi = bi.copy()
            ImageDraw.Draw(bi).text((6, 6), f'{v + k * .25:.2f}', fill='yellow')
            blatt.paste(bi, ((k % sp) * kw, (k // sp) * kh))
        blatt.save(aus / f'{n}-{c}.jpg', quality=85)
    print('Kontaktbögen ->', aus, '(Augen offen? Blick in die Linse? Mimik nicht übertrieben? Schnitt direkt nach dem letzten Laut)')


def titel(P, t):
    tx = P.ordner / 'texte'
    if not (tx / 'titel.png').exists():
        texte(P)
    aus = pathlib.Path(P.R.AUSGABE).parent
    roh = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t}', '-i', str(P.tmp / 'basis.mp4'), '-frames:v', '1',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    img = Image.frombuffer('RGB', (W, H), roh[:W * H * 3], 'raw', 'RGB', 0, 1).convert('RGBA')
    img.alpha_composite(Image.open(tx / 'titel.png').convert('RGBA'))
    img = img.convert('RGB')
    img.save(aus / 'Titelbild.jpg', quality=93)
    img.crop((0, 240, 1080, 1680)).save(aus / 'Titelbild-3x4-Vorschau.jpg', quality=90)
    print('Titelbild ->', aus / 'Titelbild.jpg', '(3:4-Vorschau ansehen: Titel ganz zu sehen? Augen offen?)')


def main(pfad):
    try:
        sys.stdout.reconfigure(errors='replace')
    except AttributeError:
        pass
    R = sys.modules.get('__main__')
    P = Plan(R)
    a = sys.argv[1:]
    if '--liste' in a:
        return liste(P)
    if '--kontakt' in a:
        return kontakt(P)
    if '--titel' in a:
        if not (P.tmp / 'basis.mp4').exists():
            basis(P)
        return titel(P, float(a[a.index('--titel') + 1]))
    if '--render' not in a or not (P.tmp / 'basis.mp4').exists():
        basis(P)
        zeiten(P)
    texte(P)
    render(P)
