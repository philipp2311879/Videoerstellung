# Hausstil für alle Reels (Philipp, 14.11.2026)

Jedes Reel bekommt **denselben Look und ein Titelbild**. Ziel sind Klicks: ein Profil, das geplant aussieht, und ein Titel,
den man im Raster sofort lesen kann. Muster: `Hausstil-Vorschlag.png` (Quelle `muster/`).
Vorbild ist der Titel „Freebie Friday“ aus dem Drachenei-Reel; der kam gut an.

Alles hier ist im Baukasten schon eingebaut (`baukasten/texte.cjs`, `titelbild.cjs`, `tafelreel.py`, `gesichtreel.py`).
Nie eine eigene Schrift, Farbe, Größe oder Position pro Reel erfinden.

## Bildmaße und sichere Zonen (Reel 1080 × 1920, 30 fps)

| Zone | Bereich | Regel |
|---|---|---|
| Instagram-Kopf | y 0–160 | nichts Wichtiges |
| Profilraster (3:4) | y 240–1680 | Instagram zeigt im Profil nur diesen Ausschnitt: Titel des Titelbilds muss hier liegen |
| Caption und Name | y 1520–1920 | keine Untertitel, keine Titel |
| Knöpfe rechts | x 940–1080, y 800–1680 | frei lassen |

## Schriften (`schriften/`)

- **Titel:** Fredoka Bold (`fredoka.woff2`).
- **Untertitel, Hook-Sätze und Kleintext:** Inter ExtraBold (`Inter-ExtraBold.ttf`).
- Keine anderen Schriften in Reels (kein Impact, keine Serifen, kein Caveat). Handschrift nur in Karussells (Notizbuch-Look).

## Titel (Sticker)

- Fredoka Bold, **Farbverlauf der Reihe**, darum ein **weißer Rand** (Text-Stroke ca. 24 px bei 140 px Schrift) und
  ein weicher dunkler Schatten, ganz leicht schräg (−3°).
- Darunter eine **Pille** in der Reihenfarbe mit weißem Rand: sagt, was es ist („Escape-Room“, „Klassenspiel“ …).
- Im Reel mit Gesicht: erste ca. 2 s groß oben (Oberkante y ≈ 290, Schrift ca. 140 px, höchstens 2 Zeilen à 1–2 Wörter),
  danach weg (`texte/oben.png`). Nie in die Zone y < 160.
- Höchstens 3 Wörter. Was man erklären muss, gehört in die Untertitel.

## Reihenfarben (`"reihe"` in `texte/texte.json`)

| Reihe | Schlüssel | Verlauf | Pille |
|---|---|---|---|
| Freebie Friday (Escape-Room, jeden Freitag) | `pink` | `#ff4fa0 → #ff7ac8 → #b57bff → #ff9e6b` | `#ff69b4` |
| Werkzeug / Rätsel | `blau` | `#1f5bff → #2f8dff → #19b4ff` | `#1f6bff` |
| Klassenspiel (Begriffe raten, Flüsterwelt …) | `gruen` | `#18a957 → #39c46b → #8bd43a` | `#1fae5b` |
| Ihr wünscht, wir bauen (Sonntag) | `orange` | `#ff8a00 → #ffb000 → #ffcc33` | `#ff9500` |

Neue Reihe = neue Farbe nur nach Rückfrage bei Philipp.

## Untertitel (Reels mit Gesicht oder Stimme)

- Inter ExtraBold **80 px**, weiß, dunkler weicher Schein (kein Kasten, kein TV-Look), 2–4 Wörter, eine Zeile.
- **Immer dieselbe Höhe:** Mitte bei y ≈ 1240 (Brusthöhe). Nur ausweichen, wenn dort etwas Wichtiges zu sehen ist,
  dann auf y ≈ 700 (über dem Kopf, `OBEN` in `bauen.py`), nie in die Caption-Zone.
- Schlüsselwort gelb `#ffd43b`, höchstens eins pro Häppchen (`*Wort*`). Kleiner Pop beim Einblenden.

## Reels ohne Person (Viral-Stil, Tafel-Reels)

Philipp, 14.11.: „nicht zu viel Erklärung, Klassenraum, bisschen Musik, am Anfang was hinschreiben, Caption viel.“
- Ein Satz als Hook oben (Oberkante y ≈ 180–260, Inter ExtraBold 66–78 px, weiß mit dunklem Schein, Schlüsselwort gelb,
  höchstens 3 Zeilen), höchstens ein zweiter Satz, wenn der wichtigste Teil beginnt. Keine Untertitel.
- Sticker-Titel erst auf Endkarte und Titelbild. Alles Erklärende in die Caption.
- Kamera steht fest wie ein Handy hinten im Raum: kein Wackeln, keine Fahrten, kein Zoom; höchstens am Ende eine Fahrt
  auf das Ergebnis an der Tafel („die Instagram-Leute mögen es mehr, wenn man einfach die Tafel sieht, wie im echten
  Unterricht“; eine Fassung mit Fahrten und iPad-Bildschirm war „zu KI“). Nur die Tafel zeigt etwas.
- Leichtes Kamerarauschen über das ganze Bild, damit Foto und eingesetzter Bildschirm eine Aufnahme werden.
- Ein Neugier-Hook wirkt besser als eine Beschreibung („Am Ende verstehst du, warum …“).
- Leise Soundeffekte (Mixkit aus `werkzeuge/video-shotcraft/assets/audio/sfx`), keine Musik; Musik kommt in Instagram
  dazu. Vorbild: Wortwolke (`beispiele/00-Wortwolke-Vorbild`).

## Endkarte

Immer gleich: Sticker + Pille in Reihenfarbe „Kommentiere WORT“ + darunter lehrerkoffer.de in Inter ExtraBold,
1,5–2 s stehen lassen. Das Wort steht auch in der Caption. Darf einen Satz oben haben („Schick das einer Lehrkraft, die …“).

## Titelbild (Pflicht für jedes Reel)

- 1080 × 1920 JPG, liegt als `Titelbild.jpg` neben dem fertigen Reel.
- Gesicht mit **offenen Augen** und Ausdruck (Bild aus dem Take suchen, nie mitten im Wort), bei Reels ohne Person das
  stärkste Bild der App. Bei Rate-Reels **ohne Lösung**.
- Titel-Sticker + Pille **in der Mitte des 3:4-Ausschnitts** (Oberkante y ≈ 1050–1080, Schrift ca. 160–170 px),
  keine Untertitel, kein Kleintext.
- Immer die 3:4-Vorschau prüfen (`Titelbild-3x4-Vorschau.jpg`): Ist der Titel im Raster ganz zu sehen?

## Raster

- Titelbilder machen das Raster ruhig; Video und Karussell nicht krampfhaft abwechseln.
- Experimente als Trial-Reel posten, die erscheinen nicht im Raster.
