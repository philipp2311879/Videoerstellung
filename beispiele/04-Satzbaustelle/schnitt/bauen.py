"""Tafel-Reel Satzbaustelle v2 (16.11.2026): Aussagesatz -> Fragesatz, gebaut wie 32-Wortwolke über baukasten/tafelreel.py.
Plan: ../PLAN-v2.md (mit dem Nutzer abgestimmt). v1 (Hund/Wurst) liegt als bauen_v1.py daneben.

Raum: raeume/klassenraum-lichterkette/klassenraum-lichterkette.webp (Nutzer), Real-ESRGAN x4 -> klassenraum-4x.png, Ecken raeume/klassenraum-lichterkette/ecken.py.
Tafel: echte Aufnahme aus _demo-seite/_aufnahme/sb2-tafel.cjs (3840x2060, Bild für Bild) -> ../bildschirm/sb2-tafel.mp4 + Marken.
„Pinguine | machen | Heiratsanträge | mit Steinen | .“ rastet im Jingle-Bells-Takt ein, „Machen“ und „?“ ploppen auf,
darunter „Machen | Pinguine | Heiratsanträge | mit Steinen | ?“. Nur der rote Verb-Stein wechselt den Platz.
Ton: schnitt/klavier.py (Steinway-Einzeltöne, jeder Stein spielt seinen Ton der Melodie; ab der Schlussfahrt der Refrain
einmal im normalen Tempo), keine Musik. Nutzer, 16.11.: „Klavier hoch“, „der Ton ist nun sehr gut“.

Aufruf:  python bauen.py [--kamera breit|ganz] --ton | --probe 1,7 | (ohne) | --titel
"""
import json, os, pathlib, sys
ORDNER = pathlib.Path(__file__).resolve().parent.parent
REPO = next(p for p in ORDNER.parents if (p / 'baukasten').is_dir())
os.environ['TAFELREEL_RAUM'] = str(REPO / 'raeume' / 'klassenraum-lichterkette')
sys.path.insert(0, str(REPO / 'baukasten'))
sys.path.insert(0, str(ORDNER / 'schnitt'))
import tafelreel as T

BS, TX, FERTIG = ORDNER / 'bildschirm', ORDNER / 'texte', ORDNER / 'fertig'
QUELLEN = {'tafel': BS / 'sb2-tafel.mp4'}
M = json.load(open(BS / 'sb2-tafel-marks.json', encoding='utf-8'))
TON = FERTIG / 'ton-v2.wav'

# Eintippen der neuen Steine: Das Fenster „Neuer Stein“ deckt den linken Rand der Fläche ab. Die Tafel bleibt darum stehen, sobald
# der Mauszeiger den Ausschnitt verlässt, und die Tipp-Pause wird herausgeschnitten: „Machen“ ploppt genau einen Schlag nach dem
# Punkt auf („Jin-gle bells, jin-gle | bells“), danach läuft alles im gleichen Takt (Viertel = 24 Bilder).
STEHT = M['R1-.'] + 11                                 # Aufnahme-Bild: Zeiger ist links aus dem Ausschnitt
POP_REEL = M['R1-.'] + 24                              # Reel-Bild für „Machen ploppt auf“
SPRUNG = M['pop-Machen'] - POP_REEL                    # so viele Aufnahme-Bilder fallen weg


def aufnahme_bild(r):
    return r if r <= STEHT else (STEHT if r < POP_REEL else r + SPRUNG)


def reel_bild(m):
    return m if m <= STEHT else (m - SPRUNG if m >= M['pop-Machen'] else None)


MR = {k: reel_bild(v) for k, v in M.items() if reel_bild(v) is not None}
f = lambda k: MR[k] / T.FPS
# Nutzer, 16.11.: „schwierig bis unmöglich zu lesen … muss nicht der Original-Screen sein. Wichtig: Steine so groß wie möglich
# und extrem scharf, alles drum herum kann abgeschnitten sein.“ -> App auf die Steinfläche zuschneiden (ohne Kopfzeile,
# Seitenleiste, Titel, Lupen), Tafel ohne Weichzeichner und leicht nachgeschärft; Kamera wahlweise ganzes Foto oder Tafel breit.
T.WEICH, T.SCHAERFE = 0.0, 45
ZUSCHNITT = (400, 330, 3590, 2060)                     # App-Pixel (3840x2060): x 200–1795, y 165–1030 CSS, Seitenverhältnis der Tafel
WEISS = [(3440, 330, 3590, 500), (400, 330, 470, 430)]  # Lupen oben rechts, Rand des Schubladen-Griffs links
KAMERA = sys.argv[sys.argv.index('--kamera') + 1] if '--kamera' in sys.argv else os.environ.get('SB2_KAMERA', 'breit')
os.environ['SB2_KAMERA'] = KAMERA
if KAMERA == 'ganz':
    FEST = (T.FW / 2, T.FH / 2, min(T.FW, T.FH * 9 / 16))          # ganzes Foto = Original-Ausschnitt
    ZIEL_RAHMEN = (.47, .30, 2600, .45)
else:
    FEST = (2195, 1100 + 2760 * 16 / 9 / 2, 2760)                    # Tafel füllt die Breite, Lichterkette darüber bleibt
    ZIEL_RAHMEN = (.47, .30, 2500, .42)
AUSGABE = FERTIG / 'Satzbaustelle-v2.mp4' if KAMERA == 'breit' else FERTIG / f'kamera-{KAMERA}' / 'Satzbaustelle-v2.mp4'
T_LETZT = f('R2-?')                                    # letzter Stein „?“ rastet ein
T_ZOOM = round(max(f('maus-weg') + .1, T_LETZT + .8), 2)
ZOOM_DAUER = 2.4
VIERTEL = .36                                          # Nachspiel: Refrain einmal im normalen Tempo ab T_ZOOM
DAUER = round(T_ZOOM + 12 * VIERTEL + 1.8, 2)

TEXTE = [(TX / 'hook.png', 0.0, f('R1-.') + .35),
         (TX / 'satz2.png', f('R1-.') + .55, T_ZOOM - .05),
         (TX / 'satz3.png', T_ZOOM + .15, T_ZOOM + ZOOM_DAUER - .05),
         (TX / 'ende.png', T_ZOOM + ZOOM_DAUER, DAUER + 1)]


def vorbereiten(bild, t):
    from PIL import ImageDraw
    bild = bild.copy()
    d = ImageDraw.Draw(bild)
    for r in WEISS:
        d.rectangle(r, fill=(255, 255, 255))
    return bild.crop(ZUSCHNITT)


VERSATZ = 1                                            # sb2-tafel.mp4 zeigt Bild n der Liste erst als Bild n+1 (concat), geprüft 16.11.


def tafel(t):
    r = int(round(t * T.FPS))
    return 'tafel', (aufnahme_bild(r) + VERSATZ) / T.FPS


def ton(lage='hoch'):
    import klavier as K
    land, frage, klicks = K.aus_marks(MR)
    gleit = [16, 13, 13, 24, 13, 22, 13, 13, 20, 7]
    druck = [2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    landungen = land[:5] + land[6:]
    greifen = [t - (g + d) / T.FPS for t, g, d in zip(landungen, gleit, druck)]
    ev = K.ereignisse(land, frage, greifen, klicks, T_ZOOM, ZOOM_DAUER, lage, nachspiel=T_ZOOM, viertel=VIERTEL)
    K.mischen(ev, DAUER, TON)


if __name__ == '__main__':
    print('Kamera', KAMERA, 'Landungen', [round(MR[k] / 30, 2) for k in MR if k.startswith(('R1-', 'R2-', 'pop-'))],
          'Zoom', T_ZOOM, 'Dauer', DAUER)
    if '--ton' in sys.argv:
        i = sys.argv.index('--ton')
        ton(sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith('--') else 'hoch')
    elif '--titel' in sys.argv:
        T.titelbild(QUELLEN['tafel'], M['ende'] / T.FPS - .5, TX / 'titel.png', AUSGABE.parent, rahmen=(.47, .30, 2640, .30), vorbereiten=vorbereiten)
    else:
        T.main(__file__)
