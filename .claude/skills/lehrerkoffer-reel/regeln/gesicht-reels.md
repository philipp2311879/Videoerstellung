# Reels mit Gesicht (Kamera-Takes)

Gesicht dort, wo es selbst der Inhalt ist: ein Gag (Tür knallt zu, auf den Tisch werfen), eine kurze Geschichte, eine
Meinung in eigenen Worten, eine Pointe. Nie als Rahmen um eine Bildschirm-Vorführung (Selfie + Tafel gemischt kam so
schlecht an, dass es gelöscht wurde). Werkzeug zeigen = harter Schnitt auf eine **echte App-Aufnahme** oder auf das echte
iPad/die echte Tafel im Raum, nie abgefilmter Bildschirm mit Moiré.

## Takes auswählen

- **Nur der letzte Take** (letztes Video, passender Ton): er spricht den Text jedes Mal freier, der letzte Durchgang ist
  seine Fassung. Innerhalb des Takes je Satz der letzte saubere Versuch. Ausnahme nur, wenn er ausdrücklich sagt „nimm die
  besten Sätze aus beiden Videos“.
- **Blick**: keine Stellen, an denen er nach oben oder unten schaut. `python bauen.py --kontakt` macht Kontaktbögen alle
  0,25 s je Teil (`fertig/kontakt/`): Augen offen, Blick in die Linse? Kurzer Blick auf einen Gegenstand, auf den er zeigt,
  ist okay.
- **Mimik natürlich**: aufgerissene Augen mit hochgezogenen Brauen oder breites Zähne-Grinsen raus, auch wenn der Blick
  sauber ist. „Natürlich lächeln“ heißt ruhig und freundlich.
- **Grenzen**: Anfang direkt vor dem ersten Laut, Ende direkt nach dem letzten Laut (keine Luft danach, sonst gehen die
  Augen schon weg). Gehen die Augen schon während des letzten Wortes weg: Bild ein paar Bilder früher wechseln, Ton
  darunter auslaufen lassen (L-Schnitt).
- Stücke enthalten oft zwei Anläufe ohne Pause („Und genau das … / Und genau das …“): jedes gewählte Stück einzeln
  anhören/transkribieren und auf Doppler prüfen. Schnitt mitten im Wort zerstört Wörter („Ordner“ → „Ort“).
- **Echte Bewegung nie beschleunigen** (Fall auf den Tisch in echter Geschwindigkeit; jedes 1,25×–3× wirkte künstlich).
  Kein künstliches Wackeln.
- **Seitenverhältnis immer erhalten** (nie ein Bild in ein anderes Format zwingen). Clips ohne Drehungs-Angabe in `DREHEN`
  selbst drehen (`transpose=1` = 90° im Uhrzeigersinn).

## Kamera-Clips

- Sony-Kamera: `C0xxx.MP4`, 1920×1080 mit Drehung −90 → hochkant, 50 fps, Ton im Clip (beide Kanäle gleich).
  Speicherkarte erst freigeben, wenn die Kopie geprüft ist (md5 oder ffmpeg ohne Fehler); `robocopy /J` lieferte schon
  kaputte Kopien.
- Die Kamera-Uhr geht ca. 9 h 38 min nach (für Zuordnung über Zeitstempel).

## Aufbau und Look (alles in `baukasten/gesichtreel.py`)

- Sekunde 1: Gesicht + echte Stimme + bekannte Lage. Sticker-Titel (`texte/oben.png`, Reihenfarbe) groß oben die ersten
  ca. 2 s (`STICKER_BIS`).
- Untertitel: 2–4 Wörter je Häppchen, **Wort für Wort wie gesprochen** (nur Füllwörter wie „äh“ weglassen), eine Zeile, Inter ExtraBold 80 px weiß mit dunklem Schein, Mitte y 1240; wo auf Brusthöhe etwas Wichtiges
  ist (iPad, Tafel), oben auf y 700 (`OBEN`). Höchstens ein gelbes Schlüsselwort (`*Wort*`).
  Zeiten kommen aus faster-whisper (wenn installiert) – sonst grob verteilt: dann im fertigen Reel prüfen und Häppchen anpassen.
- Glas-Effekte, Karten, Pops nur an den Kernstellen; „nicht so krass professionell, viel KI reinknallen“ war ein
  Kritikpunkt. Hook als schlichter Text, Untertitel weiß.
- Ende: Endkarte (`texte/ende.png`) über dem letzten Bild, 1,5–2 s. Darf einen Satz haben wie „Schick das einer Lehrkraft,
  die Vertretung liebt.“ (`ende_satz` in texte.json).

## Bauen

```
py baukasten/neues_reel.py gesicht <Name>         # Ordner + Vorlagen
# Clips nach reels/<Ordner>/aufnahmen/, TEILE in schnitt/bauen.py eintragen, texte/texte.json ausfüllen
cd reels/<Ordner>/schnitt
python bauen.py --liste                            # Zeitleiste + Lautheit je Teil
python bauen.py --kontakt                          # Augen/Blick prüfen
python bauen.py                                    # Schnitt, Wortzeiten, Texte, fertiges Reel
python bauen.py --render                           # nur neu rendern (Texte/Geräusche geändert)
python bauen.py --titel 3.2                        # Titelbild aus Sekunde 3,2 (Augen offen, Ausdruck)
```

Für das Titelbild vorher mit `py baukasten/standbild.py fertig/_tmp/basis.mp4 3.2 probe.png --blatt` einen Kontaktbogen
um die Stelle machen und das Bild mit offenen Augen und natürlichem Ausdruck wählen (nie mitten im Wort).
