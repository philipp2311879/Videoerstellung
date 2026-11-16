# Klassenräume für Tafel-Reels

Je Raum: `klassenraum-4x.png` (Foto, mit Real-ESRGAN x4 hochgerechnet), `gruen-maske.png` (weiche Maske der grünen
Tafel), `ecken.json` (Ecken der Tafel in 4x-Pixeln: oben links, oben rechts, unten rechts, unten links), `ecken.py`
(rechnet beides aus dem Foto aus), `ecken-kontrolle.png` (zum Ansehen), das Originalbild.

| Raum | Wofür |
|---|---|
| `klassenraum-gruen` | Standard der Tafel-Reels (Wortwolke, Umfrage, Standpunkt, Timer). Ein Raum = wiedererkennbare Serie. |
| `klassenraum-lichterkette` | realistischer, mit Lichterkette (Satzbaustelle v2, Winter). |
| `klassenraum-ipad` | mit iPad vorne auf dem Tisch; `ecken.json` hat `board` und `ipad` (Textbaustelle, eigener Bau). |

Raum wählen: vor `import tafelreel` im `bauen.py`
`os.environ['TAFELREEL_RAUM'] = str(REPO / 'raeume' / 'klassenraum-lichterkette')`.

Neuer Raum: Bild von Philipp (fotorealistischer Klassenraum mit grüner, leerer Tafel, Tafel nicht zu weit oben, sonst liegt
der Hook auf der Tafel) → Real-ESRGAN x4 → neuer Ordner, `ecken.py` aus `klassenraum-lichterkette` kopieren, laufen lassen,
`ecken-kontrolle.png` prüfen. Zoom höchstens ca. 2,4×, sonst wird das Foto weich.
