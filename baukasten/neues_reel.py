"""Legt einen neuen Reel-Ordner mit Vorlagen an.

Aufruf:  py baukasten/neues_reel.py tafel   <Name>    Reel ohne Person: App auf der Tafel im Klassenraum (wie Wortwolke)
         py baukasten/neues_reel.py gesicht <Name>    Reel mit Gesicht aus Kamera-Takes

Ergebnis: reels/<JJJJ-MM-TT>-<Name>/
  aufnahmen/   Kamera-Clips (nicht im Git)           bildschirm/  App-Aufnahmen (MP4) + Marken (JSON)
  texte/       texte.json (Hook, Sticker, Wort, Reihe) schnitt/     bauen.py
  fertig/      Reel, Titelbild, ton.wav (Videos nicht im Git)   CAPTION.md
"""
import datetime, pathlib, re, sys

REPO = pathlib.Path(__file__).resolve().parents[1]

TAFEL = '''"""Tafel-Reel {name} ({datum}), gebaut wie das Wortwolke-Reel über baukasten/tafelreel.py.

Idee in einem Satz: ...
Hook: „...“ (Neugier, in Alltagssprache, kein Spoiler)
Quelle: ../bildschirm/aufnahme.mp4 (1920x1080 oder 3840x2160, QR-Kasten ausgeblendet)

Aufruf:  python bauen.py --ton | --probe 1,5,9 | (ohne: rendern) | --titel
"""
import json, pathlib, sys
sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / 'baukasten').is_dir()) / 'baukasten'))
# Anderer Raum: vor dem Import  os.environ['TAFELREEL_RAUM'] = str(<repo>/'raeume'/'klassenraum-lichterkette')
import tafelreel as T

ORDNER = pathlib.Path(__file__).resolve().parent.parent
BS, TX, FERTIG = ORDNER / 'bildschirm', ORDNER / 'texte', ORDNER / 'fertig'
QUELLEN = {{'tafel': BS / 'aufnahme.mp4'}}
AUSGABE = FERTIG / '{name}-v1.mp4'
TON = FERTIG / 'ton.wav'

# (Reel-Zeit, Quellzeit): Wartezeiten schneller, echte Bewegungen (Maus, Ziehen) in echter Geschwindigkeit
PUNKTE = [(0.0, 0.5), (8.0, 8.5)]
T_ZOOM = PUNKTE[-1][0] + .1          # ab hier die eine Fahrt aufs Ergebnis
ZOOM_DAUER = 1.4
DAUER = round(T_ZOOM + ZOOM_DAUER + 2.8, 2)
ZIEL_RAHMEN = (.5, .55, 1750, .36)   # Ziel der Fahrt: (fx, fy auf der Tafel, Breite im Foto, Höhe des Punkts im Bild)
# T.WEICH = 0; T.SCHAERFE = 60      # wenn Inhalt klein ist: scharf statt weich (Tafel lesbar!)

TEXTE = [(TX / 'hook.png', 0.0, 4.0), (TX / 'satz2.png', 4.3, T_ZOOM - .1),
         (TX / 'ende.png', T_ZOOM + ZOOM_DAUER - .2, DAUER + 1)]


def quellzeit(t):
    for (a, qa), (b, qb) in zip(PUNKTE, PUNKTE[1:]):
        if t <= b:
            return qa + (qb - qa) * (t - a) / (b - a)
    return PUNKTE[-1][1] + (t - PUNKTE[-1][0])


def tafel(t):
    return 'tafel', quellzeit(t)


def ton():
    """Leise Mixkit-Effekte wie bei der Wortwolke: Pop je neuem Element, Klick, Wusch + Glitzern bei der Fahrt."""
    POP, WUSCH, GLITZER = T.sfx('ui/ui-popup-dry.mp3'), T.sfx('transition/swoosh-slow.mp3'), T.sfx('light/shimmer-sparkle-sweep.mp3')
    zeiten, _ = T.wechsel_zeiten(QUELLEN['tafel'])            # sichtbare Änderungen in der Aufnahme (Quellzeit)
    ev = [(POP, z, -17 - (k % 3)) for k, z in enumerate(zeiten) if z < PUNKTE[-1][1]]   # Quellzeit ~ Reelzeit anpassen!
    ev += [(WUSCH, T_ZOOM - .1, -12), (GLITZER, T_ZOOM + ZOOM_DAUER - .35, -14)]
    FERTIG.mkdir(parents=True, exist_ok=True)
    T.ton_schreiben(ev, DAUER, TON)


if __name__ == '__main__':
    if '--ton' in sys.argv:
        ton()
    elif '--titel' in sys.argv:
        T.titelbild(QUELLEN['tafel'], PUNKTE[-1][1], TX / 'titel.png', FERTIG, rahmen=(.5, .5, 2350, .30))
    else:
        T.main(__file__)
'''

GESICHT = '''"""Reel mit Gesicht: {name} ({datum}), gebaut über baukasten/gesichtreel.py (Hausstil, Originalton).

Aufbau: Hook (Gesicht + echte Stimme in Sekunde 1) -> ... -> Endkarte „Kommentiere WORT“.
Clips: ../aufnahmen/ (nur der letzte Take, außer Philipp sagt etwas anderes)

Aufruf:  python bauen.py --liste | --kontakt | (ohne: alles bauen) | --render | --titel <sekunde>
"""
import pathlib, sys
sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / 'baukasten').is_dir()) / 'baukasten'))
import gesichtreel as G

ORDNER = pathlib.Path(__file__).resolve().parent.parent
AUFNAHMEN = ORDNER / 'aufnahmen'
AUSGABE = ORDNER / 'fertig' / '{name}-v1.mp4'

# (Teil, Clip, von, bis, Untertitel-Häppchen)  Häppchen: 2–4 Wörter, eine Zeile, *Wort* = gelb (höchstens eins)
# Grenzen: Anfang direkt vor dem ersten Laut, Ende direkt nach dem letzten Laut (keine Luft, Augen nicht schon weg)
TEILE = [
    ('H1', 'C0001', 0.00, 3.00, ['Kennst du das?']),
]
DREHEN = {{}}           # z. B. {{'C0329': 'transpose=1'}} für Clips, die ohne Drehungs-Angabe liegen
OBEN = set()          # Teile, deren Untertitel oben (y 700) stehen, weil auf Brusthöhe etwas Wichtiges zu sehen ist
STICKER_BIS = 2.0     # Sticker-Titel groß oben, erste ca. 2 s
ENDKARTE = 2.0        # Endkarte 1,5–2 s
LUFS = -19.0          # Stimme (Originalton); −16 war Philipp „bisschen laut“
GERAEUSCHE = []       # leise Effekte, z. B. [('ui/ui-popup-dry.mp3', 4.2, -10)]  (dB relativ zur Stimme)

if __name__ == '__main__':
    G.main(__file__)
'''

TEXTE_TAFEL = '''{{
  "reihe": "blau",
  "hook": {{"html": "Ein Satz, der <em>neugierig</em><br>macht. Am Ende siehst du …", "top": 178, "size": 66}},
  "satz2": {{"html": "Zweiter Satz, wenn der<br>wichtigste Teil <em>beginnt</em>", "top": 260, "size": 74}},
  "sticker": "{titel}",
  "pille": "Was es ist",
  "wort": "{wort}"
}}
'''

TEXTE_GESICHT = '''{{
  "reihe": "blau",
  "sticker": "{titel}",
  "pille_oben": "Klassenspiel",
  "pille": "Was es bringt",
  "wort": "{wort}"
}}
'''

CAPTION = '''# Caption {name}

Video: `fertig/{name}-v1.mp4`. Titelbild: `fertig/Titelbild.jpg`. Kommentar-Wort: **{wort}**.
Vor dem Posten die automatische Nachricht für {wort} mit dem Link anlegen. Musik in Instagram drunterlegen (leise).

---

Erster Satz: Neugier oder Frage zum Mitreden (Rate- und Meinungsfragen bringen Kommentare).

Was man sieht, in ganzen, normalen Sätzen. Das Besondere unseres Werkzeugs zuerst.

So läuft's:
1️⃣ …
2️⃣ …
3️⃣ …

✅ Kostenlos, alles auf einer Seite.

Kommentiere {wort} und folge uns, dann schicken wir dir den Link per Nachricht. 🤍

#unterrichtsideen #lehrerleben #lehrerkoffer
'''


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ('tafel', 'gesicht'):
        sys.exit(__doc__)
    art, name = sys.argv[1], re.sub(r'[^\w\-äöüÄÖÜß]', '-', sys.argv[2]).strip('-')
    datum = datetime.date.today().isoformat()
    ordner = REPO / 'reels' / f'{datum}-{name}'
    if ordner.exists():
        sys.exit(f'Gibt es schon: {ordner}')
    for d in ('aufnahmen', 'bildschirm', 'texte', 'schnitt', 'fertig'):
        (ordner / d).mkdir(parents=True)
    wort = re.sub(r'[^A-ZÄÖÜ]', '', name.upper()) or 'KOFFER'
    titel = name.replace('-', ' ')
    vorlage = TAFEL if art == 'tafel' else GESICHT
    (ordner / 'schnitt' / 'bauen.py').write_text(vorlage.format(name=name, datum=datum), encoding='utf-8')
    tx = TEXTE_TAFEL if art == 'tafel' else TEXTE_GESICHT
    (ordner / 'texte' / 'texte.json').write_text(tx.format(titel=titel, wort=wort), encoding='utf-8')
    (ordner / 'CAPTION.md').write_text(CAPTION.format(name=name, wort=wort), encoding='utf-8')
    print('Angelegt:', ordner)
    print('Als Nächstes:', 'App-Aufnahme nach bildschirm/aufnahme.mp4 legen' if art == 'tafel' else 'Clips nach aufnahmen/ kopieren',
          '-> texte/texte.json und schnitt/bauen.py anpassen -> python schnitt/bauen.py')


if __name__ == '__main__':
    main()
