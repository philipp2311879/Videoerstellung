"""Tafel-Reel Umfrage (15.11.2026), gebaut wie 32-Wortwolke v2 über baukasten/tafelreel.py.

Die Klasse stimmt ab: „Welcher Planet ist am heißesten?“ Merkur, Venus, Mars, Jupiter. Während der Abstimmung sieht
niemand das Ergebnis, nur der Zähler läuft (unsere Besonderheit: keiner läuft der Mehrheit hinterher). Dann „Abstimmung
beenden“: Balken zählen hoch, die meisten lagen falsch (Merkur 54 %), Venus ist grün markiert.
Hook: „Die meisten tippen hier falsch. Am Ende siehst du, ob du recht hattest.“ (lädt zum Mitraten und Kommentieren ein)

Quelle: ../bildschirm/um-beamer.mp4 + um-marks.json aus _demo-seite/_aufnahme/um-tafel.cjs
Aufruf:  python bauen.py --ton        -> ../fertig/ton.wav (Mixkit-Effekte)
         python bauen.py --probe 1,7   -> Standbilder in ../fertig/probe
         python bauen.py              -> ../fertig/Umfrage-v1.mp4 (mit ton.wav, falls vorhanden)
         python bauen.py --titel      -> ../fertig/Titelbild.jpg + 3:4-Vorschau
"""
import json, pathlib, sys
sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / 'baukasten').is_dir()) / 'baukasten'))
import tafelreel as T

ORDNER = pathlib.Path(__file__).resolve().parent.parent
BS, TX, FERTIG = ORDNER / 'bildschirm', ORDNER / 'texte', ORDNER / 'fertig'
QUELLEN = {'beamer': BS / 'um-beamer.mp4'}
M = json.load(open(BS / 'um-marks.json'))
AUSGABE = FERTIG / 'Umfrage-v1.mp4'
TON = FERTIG / 'ton.wav'

KLICK = M['beendet'] - .09                       # Maustaste unten
BEWEGUNG = KLICK - 1.2                           # Maus fährt zum Knopf
WEG = M['maus-weg'] + .1
# (Reel-Zeit, Quellzeit): Stimmen 2x, stille Wartezeit schnell, ab der Mausbewegung echte Geschwindigkeit
PUNKTE = [(0.0, .5), (4.0, M['stimmen-ende'] + .3), (4.4, BEWEGUNG)]
PUNKTE.append((4.4 + WEG - BEWEGUNG, WEG))
T_ZOOM = PUNKTE[-1][0] + .1
ZOOM_DAUER = 1.4
DAUER = round(T_ZOOM + ZOOM_DAUER + 2.8, 2)
ZIEL_RAHMEN = (.5, .55, 1750, .36)
T_KLICK = PUNKTE[2][0] + (KLICK - BEWEGUNG)

TEXTE = [(TX / 'hook.png', 0.0, T_KLICK - .55), (TX / 'satz2.png', T_KLICK + .15, T_ZOOM - .1),
         (TX / 'ende.png', T_ZOOM + ZOOM_DAUER - .2, DAUER + 1)]


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


def tafel(t):
    return 'beamer', quellzeit(t)


def ton():
    zeiten, _ = T.wechsel_zeiten(QUELLEN['beamer'], schwelle=.25, abstand=.12, bereich=(.40, .74, .60, .82))
    stimmen = [z for z in zeiten if M['stimmen'] - .2 < z < M['stimmen-ende'] + .6]
    print('Zähler-Wechsel', len(stimmen))
    POP, KL, SWEEP, ERFOLG = T.sfx('ui/ui-popup-dry.mp3'), T.sfx('ui/ui-select-click.mp3'), T.sfx('transition/sweep-short.mp3'), T.sfx('ui/ui-success-soft.mp3')
    WUSCH, GLITZER = T.sfx('transition/swoosh-slow.mp3'), T.sfx('light/shimmer-sparkle-sweep.mp3')
    ev = [(POP, reelzeit(z), -17 - (k % 3)) for k, z in enumerate(stimmen)]
    ev += [(KL, T_KLICK, -12), (SWEEP, T_KLICK + .12, -17), (ERFOLG, T_KLICK + 1.05, -13),
           (WUSCH, T_ZOOM - .1, -12), (GLITZER, T_ZOOM + ZOOM_DAUER - .35, -14)]
    FERTIG.mkdir(parents=True, exist_ok=True)
    T.ton_schreiben(ev, DAUER, TON)


if __name__ == '__main__':
    print('Klick bei', round(T_KLICK, 2), 's')
    if '--ton' in sys.argv:
        ton()
    elif '--titel' in sys.argv:
        # ohne Lösung (Rate-Reel): alle 24 Stimmen da, Ergebnis noch verborgen; Mauszeiger rechts unten wegretuschiert
        T.titelbild(QUELLEN['beamer'], M['stimmen-ende'] + .6, TX / 'titel.png', FERTIG, rahmen=(.5, .5, 2350, .30),
                    flicken=[(1408, 748, 1454, 794)])
    else:
        T.main(__file__)
