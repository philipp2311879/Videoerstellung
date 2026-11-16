# Tafel-Reels (ohne Person)

Das erfolgreichste Format: Wortwolke 11k Views in 12 h, 28k nach zwei Tagen, viele Kommentare und Follower.
„Das war ja kein Tutorial, hat nur gut gezeigt, wie das Tafelbild sein kann.“ Jede neue Folge wird **genau so** gebaut.

## Die Formel

- **Raum**: ein realistisches Klassenraum-Foto mit grüner Tafel (`raeume/`), die echte App wird perspektivisch auf die
  grüne Fläche gesetzt, mit Lichtverlauf, leicht angehobenem Schwarz, leichtem Kamerarauschen. Es soll aussehen wie
  abgefilmter Unterricht, nicht wie eine Grafik.
  - `klassenraum-gruen` – Standard der Serie (Wortwolke, Umfrage, Standpunkt, Timer). Ein Raum = wiedererkennbare Serie.
  - `klassenraum-lichterkette` – realistischer, Winter (Satzbaustelle v2); per `os.environ['TAFELREEL_RAUM']`.
  - `klassenraum-ipad` – mit iPad vorne auf dem Tisch (Textbaustelle; zwei Bildschirme, eigener Bau nötig).
  - Neuer Raum: Bild von Philipp (ChatGPT-Klassenraum mit grüner Tafel), mit Real-ESRGAN x4 hochrechnen
    (realesrgan-ncnn-vulkan, kostenlos), `ecken.py` aus einem vorhandenen Raum kopieren und laufen lassen →
    `ecken.json` + `gruen-maske.png`, `ecken-kontrolle.png` ansehen.
- **Kamera steht fest** wie ein Handy hinten im Raum. Kein Wackeln, kein Zoom, keine Fahrten – außer **einer** Fahrt am
  Ende auf das Ergebnis an der Tafel (`T_ZOOM`, `ZOOM_DAUER`, `ZIEL_RAHMEN`). Geräte im Raum bleiben aus.
- **Hook-Satz oben** (texte.json `hook`), höchstens ein zweiter Satz, wenn der wichtigste Teil beginnt (`satz2`), evtl.
  ein dritter bei der Fahrt (`satz3`). Keine Untertitel. Sticker erst auf Endkarte und Titelbild.
- **Endkarte** über dem Ergebnis: Sticker + „Kommentiere WORT“ + lehrerkoffer.de (+ evtl. `ende_satz`).
- **Ton**: leise Mixkit-Effekte genau auf das Bild (Pop je neuem Element aus `wechsel_zeiten`, Klick, Wusch + Glitzern bei
  der Fahrt), keine Musik. Siehe `ton.md`.
- **Länge** 13–20 s. Wartezeiten schneller laufen lassen (Zeitraffer über `PUNKTE`), echte Bewegungen (Maus, Ziehen,
  Einrasten) in echter Geschwindigkeit. Endet am besten so, wie es beginnt (Schleife).

## App-Aufnahmen (`bildschirm/`)

- Echte Aufnahme der App in 1920×1080 oder 3840×2160 (scharf!), 30 fps, nur der Inhalt, kein Browser-Rahmen.
  Philipp nimmt sie aus seiner Demo-Seite mit Dummy-Klassen auf (Bild für Bild, mit Marken-JSON für die Zeitpunkte).
  Selbst aufnehmen geht auch: lehrerkoffer.de im Browser-Vollbild, Bildschirmaufnahme (OBS, Xbox Game Bar, macOS),
  ruhige Maus. Nie echte Schülernamen oder echte Klassen zeigen.
- **Der hellblaue Kasten mit dem QR-Code muss immer weg** („QR ausblenden“ vor der Aufnahme; bei der Wortwolke erst nach
  dem ersten Begriff möglich).
- Beispielinhalt = echte Unterrichtsfrage (siehe `hook-und-inhalt.md`), Antworten realistisch (Bots/Testgeräte, ~24 Stimmen).
- Vor dem Bauen fragen bzw. nachsehen, was das Werkzeug **besonders** kann, und das als Hauptteil aufnehmen.

## Lesbarkeit (Philipp, 16.11.)

Bei ganzem Raum und ganzer App waren die Steine der Satzbaustelle „schwierig bis unmöglich zu lesen“: „Wichtig ist, dass
die Steine so groß wie möglich sind und extrem scharf. Alles drum herum kann abgeschnitten sein.“
- App auf den Inhalt zuschneiden (`vorbereiten(bild, t)` im `bauen.py`, Beispiel `beispiele/04-Satzbaustelle`),
  Kamera so, dass die Tafel die Breite füllt (`FEST`), `T.WEICH = 0`, leicht nachschärfen (`T.SCHAERFE = 60`).
- Vor dem großen Bau immer `python bauen.py --probe …` und die Standbilder in voller Größe ansehen.

## Bauen

```
node baukasten/texte.cjs reels/<Ordner>          # hook.png, satz2.png, ende.png, titel.png
cd reels/<Ordner>/schnitt
python bauen.py --probe 0.5,5,10                  # Standbilder nach fertig/probe/
python bauen.py --ton                             # fertig/ton.wav (Effekte)
python bauen.py                                   # fertig/<Name>-v1.mp4 (mehrere Teile parallel, ein paar Minuten)
python bauen.py --titel                           # fertig/Titelbild.jpg + Titelbild-3x4-Vorschau.jpg
```

Vorlagen: `beispiele/01-Umfrage` (Zeitraffer + Klick + Ergebnis), `02-Standpunkt`, `03-Timer` (4K-Aufnahme, Schleife),
`04-Satzbaustelle` (anderer Raum, Zuschnitt, Klaviertöne). Jede lässt sich aus dem Repo nachbauen.

Titelbild: stärkstes Bild der App (bei Rate-Reels ohne Lösung), Mauszeiger mit `flicken=[(x0, y0, x1, y1)]` wegretuschieren.

## Nicht als Tafel-Reel

Begriffe raten (an der Tafel steht nur ein Countdown; das Spannende passiert bei den Menschen), Lautstärke-Ampel
(bräuchte echten Klassenlärm), Arbeitsblatt-Generatoren (nichts an der Tafel), Mathe-Werkzeuge, Glücksrad, Klassenraumplaner.
