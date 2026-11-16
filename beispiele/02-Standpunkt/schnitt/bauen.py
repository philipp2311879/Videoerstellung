"""Tafel-Reel Standpunkt (15.11.2026), gebaut wie 32-Wortwolke v2 über baukasten/tafelreel.py.

„Robin Hood – Held oder Verbrecher?“ Die ganze Klasse setzt ihren Punkt auf den Strahl (25 Punkte, ein kleiner Haufen bei
„Verbrecher“, ein Berg bei „Held“). Unsere Besonderheit: Hinter jedem Punkt steckt eine Begründung. Die Lehrkraft tippt
links auf einen Punkt („Stehlen bleibt stehlen.“) und rechts („Er hat den Armen geholfen.“). Am Ende Fahrt auf das
Meinungsbild. Hook: „Bei dieser Frage muss sich die ganze Klasse entscheiden. Wo setzt du deinen Punkt?“

Quelle: ../bildschirm/sp-beamer.mp4 + sp-marks.json aus _demo-seite/_aufnahme/sp-tafel.cjs
Aufruf:  python bauen.py --ton | --probe 1,7 | (ohne) | --titel   (wie 01-Umfrage)
"""
import json, pathlib, sys
sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / 'baukasten').is_dir()) / 'baukasten'))
import tafelreel as T

ORDNER = pathlib.Path(__file__).resolve().parent.parent
BS, TX, FERTIG = ORDNER / 'bildschirm', ORDNER / 'texte', ORDNER / 'fertig'
QUELLEN = {'beamer': BS / 'sp-beamer.mp4'}
M = json.load(open(BS / 'sp-marks.json'))
AUSGABE = FERTIG / 'Standpunkt-v1.mp4'
TON = FERTIG / 'ton.wav'

L, LZ, RE, RZ, WG = M['links'], M['links-zu'], M['rechts'], M['rechts-zu'], M['maus-weg']
LESEN = 1.8                                       # Lesezeit bei offener Begründung etwas schneller (Bild steht still)
P = [(0.0, .3), (4.6, M['punkte-ende'] + .2), (5.0, L - 1.3)]          # Punkte ~2x, dann Wartezeit schnell
P.append((P[-1][0] + 1.8, L + .5))                                      # Maus fährt zum linken Punkt, Begründung geht auf
P.append((P[-1][0] + (LZ - (L + .5)) / LESEN, LZ))
P.append((P[-1][0] + 1.2, LZ + 1.2))                                    # Schließen
P.append((P[-1][0] + .4, RE - 1.3))                                     # Wartezeit schnell
P.append((P[-1][0] + 1.8, RE + .5))                                     # rechter Punkt
P.append((P[-1][0] + (RZ - (RE + .5)) / LESEN, RZ))
P.append((P[-1][0] + 1.2, RZ + 1.2))
P.append((P[-1][0] + .3, WG - .7))
P.append((P[-1][0] + .8, WG + .1))                                      # Maus geht weg
PUNKTE = P
T_ZOOM = PUNKTE[-1][0] + .1
ZOOM_DAUER = 1.4
DAUER = round(T_ZOOM + ZOOM_DAUER + 2.8, 2)
ZIEL_RAHMEN = (.5, .5, 2150, .36)


def quellzeit(t):
    for (a, qa), (b, qb) in zip(PUNKTE, PUNKTE[1:]):
        if t <= b:
            return qa + (qb - qa) * (t - a) / (b - a)
    return PUNKTE[-1][1] + (t - PUNKTE[-1][0])


def reelzeit(q):
    for (a, qa), (b, qb) in zip(PUNKTE, PUNKTE[1:]):
        if q <= qb:
            return a + (b - a) * (q - qa) / (qb - qa)
    return PUNKTE[-1][0] + (q - PUNKTE[-1][1])


T_LINKS = reelzeit(L - .09)
T_RECHTS = reelzeit(RE - .09)
TEXTE = [(TX / 'hook.png', 0.0, T_LINKS - .5), (TX / 'satz2.png', T_LINKS + .2, reelzeit(RZ + .9)),
         (TX / 'ende.png', T_ZOOM + ZOOM_DAUER - .2, DAUER + 1)]


def tafel(t):
    return 'beamer', quellzeit(t)


def ton():
    zeiten, _ = T.wechsel_zeiten(QUELLEN['beamer'], schwelle=.12, abstand=.1, bereich=(.03, .42, .97, .74))
    punkte = [z for z in zeiten if M['punkte'] - .2 < z < M['punkte-ende'] + .6]
    print('Punkte-Wechsel', len(punkte))
    POP, KL, AUF = T.sfx('ui/ui-popup-dry.mp3'), T.sfx('ui/ui-select-click.mp3'), T.sfx('transition/sweep-short.mp3')
    WUSCH, GLITZER = T.sfx('transition/swoosh-slow.mp3'), T.sfx('light/shimmer-sparkle-sweep.mp3')
    ev = [(POP, reelzeit(z), -17 - (k % 3)) for k, z in enumerate(punkte)]
    for t in (T_LINKS, T_RECHTS):
        ev += [(KL, t, -12), (AUF, t + .05, -16)]
    for z in (LZ, RZ):
        ev.append((KL, reelzeit(z + .66), -16))
    ev += [(WUSCH, T_ZOOM - .1, -12), (GLITZER, T_ZOOM + ZOOM_DAUER - .35, -14)]
    FERTIG.mkdir(parents=True, exist_ok=True)
    T.ton_schreiben(ev, DAUER, TON)


if __name__ == '__main__':
    print('Begründung links', round(T_LINKS, 2), 'rechts', round(T_RECHTS, 2))
    if '--ton' in sys.argv:
        ton()
    elif '--titel' in sys.argv:
        T.titelbild(QUELLEN['beamer'], WG + 1.0, TX / 'titel.png', FERTIG, rahmen=(.5, .5, 2350, .30))
    else:
        T.main(__file__)
