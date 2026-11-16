"""Tafel-Reel Timer (15.11.2026), gebaut wie 32-Wortwolke v2 über baukasten/tafelreel.py.

Timer mit drei Phasen (Lesen 5 Min. rot, Partnerarbeit 10 Min. blau, Vorstellen 5 Min. grün) im Vollbild an der Tafel.
Start, dann Zeitraffer (Bild für Bild mit vorgespulter Uhr): der Zeiger läuft durch die Farben, die Leiste zeigt die
aktuelle Phase, bei jedem Wechsel ein Gong. „Zeit ist um“, Zurücksetzen, die Uhr ist wieder voll wie im ersten Bild
(Schleife). Am Ende Fahrt auf die Uhr. Hook: „Nie wieder die Frage: Wie lange noch?“

Quelle: ../bildschirm/tm-tafel.mp4 + tm-tafel-marks.json (3840x2160) aus _demo-seite/_aufnahme/tm-tafel.cjs
Aufruf:  python bauen.py --ton | --probe 1,7 | (ohne) | --titel   (wie 01-Umfrage)
"""
import json, pathlib, sys
sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / 'baukasten').is_dir()) / 'baukasten'))
import tafelreel as T

ORDNER = pathlib.Path(__file__).resolve().parent.parent
BS, TX, FERTIG = ORDNER / 'bildschirm', ORDNER / 'texte', ORDNER / 'fertig'
QUELLEN = {'beamer': BS / 'tm-tafel.mp4'}
M = json.load(open(BS / 'tm-tafel-marks.json'))
AUSGABE = FERTIG / 'Timer-v1.mp4'
TON = FERTIG / 'ton.wav'

A0 = .6                                            # Reel beginnt kurz vor der Mausbewegung zum Start
KLICK = M['gestartet'] - 3 / 30                    # Maustaste unten
P = [(0.0, A0), (M['zeit-um'] + .8 - A0, M['zeit-um'] + .8)]          # echte Aufnahme 1:1 (Zeitraffer steckt schon drin)
P.append((P[-1][0] + .3, M['vor-reset']))                              # stille Wartezeit schnell
P.append((P[-1][0] + (M['maus-weg'] + .1 - M['vor-reset']), M['maus-weg'] + .1))   # Zurücksetzen, Maus geht weg
PUNKTE = P
T_ZOOM = PUNKTE[-1][0] + .1
ZOOM_DAUER = 1.4
DAUER = round(T_ZOOM + ZOOM_DAUER + 2.8, 2)
ZIEL_RAHMEN = (.5, .48, 1500, .32)


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


T_START, T_P2, T_P3, T_UM = reelzeit(KLICK), reelzeit(M['phase2']), reelzeit(M['phase3']), reelzeit(M['zeit-um'])
TEXTE = [(TX / 'hook.png', 0.0, T_P2 - .5), (TX / 'satz2.png', T_P2 + .1, T_UM + .3),
         (TX / 'ende.png', T_ZOOM + ZOOM_DAUER - .2, DAUER + 1)]


def tafel(t):
    return 'beamer', quellzeit(t)


def ton():
    KL, AUFZ, TICK = T.sfx('ui/ui-select-click.mp3'), T.sfx('counter/clock-knob-spin.mp3'), T.sfx('counter/clock-tick-single.mp3')
    GONG, FERTIG_TON = T.sfx('ui/chime-crystal.mp3'), T.sfx('ui/ui-success-soft.mp3')
    WUSCH, GLITZER = T.sfx('transition/swoosh-slow.mp3'), T.sfx('light/shimmer-sparkle-sweep.mp3')
    ev = [(KL, T_START, -12), (AUFZ, T_START + .05, -18)]
    t, k = T_START + .3, 0
    while t < T_UM - .1:
        ev.append((TICK, t, -29 - 2 * (k % 2)))
        t += .25
        k += 1
    ev += [(GONG, T_P2, -12), (GONG, T_P3, -12), (FERTIG_TON, T_UM, -11)]
    ev.append((KL, reelzeit(M['reset'] - 2 / 30), -13))
    ev += [(WUSCH, T_ZOOM - .1, -12), (GLITZER, T_ZOOM + ZOOM_DAUER - .35, -14)]
    FERTIG.mkdir(parents=True, exist_ok=True)
    T.ton_schreiben(ev, DAUER, TON)


if __name__ == '__main__':
    print('Start', round(T_START, 2), 'Phase 2', round(T_P2, 2), 'Phase 3', round(T_P3, 2), 'Zeit um', round(T_UM, 2))
    if '--ton' in sys.argv:
        ton()
    elif '--titel' in sys.argv:
        T.titelbild(QUELLEN['beamer'], M['maus-weg'] + 1.0, TX / 'titel.png', FERTIG, rahmen=(.5, .5, 2350, .30))
    else:
        T.main(__file__)
