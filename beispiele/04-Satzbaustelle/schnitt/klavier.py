"""Klavier-Spur für das Tafel-Reel Satzbaustelle v2 (16.11.2026): Jeder Stein spielt beim Einrasten seinen Ton von
„Jingle bells, jingle bells, jingle all the way“ (E E E | E E E | E G C D E), auf dem letzten Stein („?“) ein warmer C-Dur-Akkord.

Nutzer, 16.11.: Kristall-Glöckchen „mehr als schrecklich“, „können wir nicht einfach genau den Ton von Jingle Bells nehmen?
die Klavier-Note“. Töne: echte Einzeltöne eines Steinway B aus den University of Iowa Musical Instrument Samples
(theremin.music.uiowa.edu, „may be downloaded and used for any projects, without restrictions“), mf, in
werkzeuge/klavier. Nichts synthetisiert, keine Tonhöhen verschoben.

Zeiten kommen aus der Aufnahme (bildschirm/sb2-tafel-marks.json, Bildnummern bei 30 fps): Landung = Bild, auf dem der Stein
liegt. Reihe 1 = Ton 1–5, „Machen“ ploppt auf = Ton 6 („bells“), „?“ ploppt leise nach, Reihe 2 = Ton 7–11.

Aufruf:  python klavier.py --probe    (Proben hoch/tief nach fertig/probe/, mit den geplanten Bildnummern)
"""
import json, pathlib, subprocess, sys, wave
import numpy as np

HIER = pathlib.Path(__file__).resolve().parent
REPO = next(p for p in HIER.parents if (p / 'baukasten').is_dir())
KLAVIER = REPO / 'werkzeuge' / 'klavier'
SFX = REPO / 'werkzeuge' / 'video-shotcraft' / 'assets' / 'audio' / 'sfx'
SR, FPS = 48000, 30

MELODIE = ['E', 'E', 'E', 'E', 'E', 'E', 'E', 'G', 'C', 'D', 'E']           # Ton 1–11
BETONUNG = [0, -2.5, -1, 0, -2.5, -0.5, 0, -1, -0.5, -1.5, 0]              # leichte Akzente wie gespielt (dB)
LAGE = {'hoch': '5', 'tief': '4'}
_CACHE = {}


def laden(pfad, stereo=True):
    k = (str(pfad), stereo)
    if k not in _CACHE:
        roh = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(pfad), '-ac', '2' if stereo else '1', '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True).stdout
        a = np.frombuffer(roh, np.float32).copy().reshape(-1, 2 if stereo else 1)
        _CACHE[k] = a
    return _CACHE[k]


def note(name, lage, lang=1.6):
    """Klavierton ab dem Anschlag, lang Sekunden, weich ausgeblendet. Liefert Stereo (n, 2), Spitze 1."""
    a = laden(KLAVIER / f'Piano.mf.{name}{LAGE[lage]}.aiff')
    h = np.abs(a).max(1)
    an = int(np.argmax(h > .08 * h.max()))
    an = max(0, an - int(.004 * SR))
    b = a[an:an + int(lang * SR)].copy()
    fade = int(min(.6, lang * .45) * SR)
    b[-fade:] *= (np.linspace(1, 0, fade, dtype=np.float32) ** 2)[:, None]
    return b / (np.abs(b).max() + 1e-9)


def sfx(rel):
    a = laden(SFX / rel, stereo=False)
    a = a / (np.abs(a).max() + 1e-9)
    return np.repeat(a, 2, axis=1)


def db(x):
    return 10 ** (x / 20)


def mischen(ereignisse, dauer, aus, spitze_db=-2.0):
    n = int(dauer * SR)
    spur = np.zeros((n + SR * 4, 2), np.float32)
    for probe, t, g in ereignisse:
        i = int(round(t * SR))
        if i < 0:
            probe, i = probe[-i:], 0
        e = min(len(spur), i + len(probe))
        spur[i:e] += probe[:e - i] * db(g)
    spur = spur[:n]
    spur *= db(spitze_db) / (np.abs(spur).max() + 1e-9)
    ende = int(.25 * SR)
    spur[-ende:] *= np.linspace(1, 0, ende, dtype=np.float32)[:, None]
    pcm = (np.clip(spur, -1, 1) * 32767).astype('<i2')
    aus = pathlib.Path(aus)
    aus.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(aus), 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    print('Ton', len(ereignisse), 'Ereignisse ->', aus)


def ereignisse(land, pop_frage, greifen, klicks, t_zoom, zoom_dauer, lage='hoch', fassung='melodie', nachspiel=None, viertel=.36):
    """land: 11 Zeiten (s) für Ton 1–11 (Reihe 1, „Machen“ ploppt auf, Reihe 2); pop_frage: Zeit, an der „?“ aufploppt;
    greifen: Zeiten, an denen ein Stein angefasst wird; klicks: Zeiten der Knopfdrücke (Neue Steine, Farbe, Ablage)."""
    assert len(land) == 11
    TAP, KLICK = sfx('ui/switch-tap.mp3'), sfx('ui/switch-click-quick.mp3')
    POP, FUNKEL = sfx('ui/ui-message-pop.mp3'), sfx('light/sparkle-touch.mp3')
    WUSCH, GLITZER = sfx('transition/swoosh-slow.mp3'), sfx('light/shimmer-sparkle-sweep.mp3')
    ev = [(TAP, t, -30) for t in greifen] + [(KLICK, t, -30) for t in klicks]
    for i, t in enumerate(land):
        ton = MELODIE[i] if fassung == 'melodie' else 'E'
        letzter = i == 10
        lang = (3.6 if nachspiel is None else 1.6) if letzter else (1.7 if i in (5, 7, 8) else 1.2)
        ev.append((note(ton, lage, lang), t, -6 + BETONUNG[i]))
        ev.append((KLICK, t - .005, -27))                                   # leises Einrasten, damit man den Stein „hört“
        if letzter:
            for akk, g in (('C', -13), ('G', -15)):                          # warmer Schlussakkord unter dem E
                ev.append((note(akk, lage, lang), t + .012, g))
            if lage == 'hoch':
                ev.append((note('C', 'tief', lang), t + .02, -14))
            ev.append((FUNKEL, t + .05, -24))
        if i == 5:
            ev.append((POP, t - .01, -20))
        if i in (1, 6):                                                     # die roten Steine: ein Hauch Glitzer
            ev.append((FUNKEL, t + .03, -27))
    ev.append((POP, pop_frage - .01, -21))
    ev.append((note('E', 'hoch' if lage == 'tief' else 'hoch', .8), pop_frage, -22))
    ev += [(WUSCH, t_zoom - .1, -28), (GLITZER, t_zoom + zoom_dauer - .45, -26)]
    if nachspiel is not None:
        ev += nachspiel_ereignisse(nachspiel, viertel, lage)
    return ev


NACH_SCHLAEGE = [0, 1, 2, 4, 5, 6, 8, 9, 10, 11.5, 12]


def nachspiel_ereignisse(start, viertel=.36, lage='hoch'):
    """Nutzer, 16.11.: „sehr langsam, man checkt kaum, dass es Jingle Bells ist. Am Ende nochmal schneller laufen lassen.“
    Der Refrain einmal im normalen Tempo (Viertel = viertel s) während Schlussfahrt und Endkarte, Schlussakkord auf „way“."""
    ev = []
    for i, (s, ton) in enumerate(zip(NACH_SCHLAEGE, MELODIE)):
        t = start + s * viertel
        letzter = i == len(MELODIE) - 1
        ev.append((note(ton, lage, 3.2 if letzter else (viertel * 2.2 if s in (2, 6) else viertel * 1.6)), t, -7 + BETONUNG[i] * .6))
        if letzter:
            for akk, g in (('C', -13), ('G', -15)):
                ev.append((note(akk, lage, 3.2), t + .012, g))
            ev.append((note('C', 'tief', 3.2), t + .02, -14))
    for s in (0, 4, 8):                                                      # leise Grundtöne darunter
        ev.append((note('C', 'tief', viertel * 3.6), start + s * viertel + .01, -21))
    return ev


def aus_marks(marks, versatz=0.0):
    """Zeiten (s, Reel-Zeit = Bild/30 + versatz) aus sb2-tafel-marks.json."""
    f = lambda k: marks[k] / FPS + versatz
    r1 = [f(k) for k in ('R1-Pinguine', 'R1-machen', 'R1-Heiratsanträge', 'R1-mit Steinen', 'R1-.')]
    r2 = [f(k) for k in ('R2-Machen', 'R2-Pinguine', 'R2-Heiratsanträge', 'R2-mit Steinen', 'R2-?')]
    land = r1 + [f('pop-Machen')] + r2
    klicks = [f(k) for k in marks if k.startswith(('neu-auf', 'farbe-', 'ablage-'))]
    return land, f('pop-?'), klicks


if __name__ == '__main__':
    if '--probe' in sys.argv:
        geplant = {'R1-Pinguine': 30, 'R1-machen': 54, 'R1-Heiratsanträge': 78, 'R1-mit Steinen': 126, 'R1-.': 150,
                   'pop-Machen': 210, 'pop-?': 222, 'R2-Machen': 258, 'R2-Pinguine': 282, 'R2-Heiratsanträge': 306,
                   'R2-mit Steinen': 342, 'R2-?': 354, 'neu-auf': 163}
        land, frage, klicks = aus_marks(geplant)
        greifen = [t - .5 for t in land[:5] + land[6:]]
        for lage in ('hoch',):
            mischen(ereignisse(land, frage, greifen, klicks, 12.6, 2.4, lage, nachspiel=12.6), 18.6,
                    HIER.parent / 'fertig' / 'probe' / f'klavier-{lage}-mit-nachspiel.wav')
    else:
        print(__doc__)
