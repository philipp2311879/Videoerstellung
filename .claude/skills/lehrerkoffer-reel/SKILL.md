---
name: lehrerkoffer-reel
description: Baut Instagram-/TikTok-Reels für Lehrerkoffer (lehrerkoffer.de) genau so, wie Philipp und Mo sie machen – Hook, Hausstil (Fredoka-Sticker, Inter-Untertitel, Reihenfarben), Tafel-Reels im Klassenraum, Reels mit Gesicht aus Kamera-Takes, Originalton, leise Mixkit-Effekte, Endkarte „Kommentiere WORT“, Titelbild im 3:4-Raster, Caption. Unbedingt verwenden, sobald jemand ein Reel, Video, Tafel-Reel, Titelbild, Hook, Untertitel, Endkarte oder Caption für Lehrerkoffer machen, schneiden, prüfen oder verbessern will – auch bei „mach ein Video zu …“, „schneid die Takes“, „bau das Titelbild“, „Shotcraft“.
---

# Lehrerkoffer-Reels bauen

Lehrerkoffer ist eine kostenlose Seite für Lehrkräfte: alle Unterrichtswerkzeuge auf einer Seite statt auf 200 Webseiten,
und Lehrkräfte bestimmen mit, was als Nächstes gebaut wird. Die Reels sollen Fremde fangen und halten. **Maßstab ist allein
die Wiedergabezeit**, nicht eine Checkliste: Aufhänger in Sekunde 1, kein Durchhänger, lohnendes Ende.

Alle Pfade hier sind relativ zur Repo-Wurzel. Lies vor jedem Reel:
1. `hausstil/HAUSSTIL.md` – Schriften, Größen, Positionen, Farben, Endkarte, Titelbild (verbindlich).
2. Die passende Regel-Datei in diesem Skill-Ordner:
   - `regeln/hook-und-inhalt.md` – Hook, Sprache, was gezeigt werden darf (immer lesen)
   - `regeln/tafel-reels.md` – Reels ohne Person: App auf der Tafel im Klassenraum (das Format mit den meisten Views)
   - `regeln/gesicht-reels.md` – Reels mit Gesicht aus Kamera-Takes
   - `regeln/ton.md` – Originalton, Lautheit, Soundeffekte, Musik
   - `regeln/caption-und-abgabe.md` – Caption, Kommentar-Wort, Hashtags, was abgegeben wird
3. Bei Bedarf `werkzeuge/video-shotcraft/SKILL.md` (Remotion-Kamerafahrten, Workbench) – der Hausstil hat Vorrang vor
   Shotcrafts eigenen Schriften, Farben und Musik.

## Welches Format?

| Wenn … | dann | Baukasten |
|---|---|---|
| ein Werkzeug zeigen, ohne Person | **Tafel-Reel**: echte App-Aufnahme auf der Tafel im Klassenraum-Foto, Hook-Satz oben, eine Fahrt am Ende | `baukasten/tafelreel.py` |
| Philipp oder Mo vor der Kamera (Gag, Geschichte, Erklärung) | **Gesicht-Reel**: Takes schneiden, Originalton, Untertitel, Sticker, Endkarte | `baukasten/gesichtreel.py` |
| Kamerafahrten über Screenshots, 3D-Bühne, Editor im Browser | **Shotcraft** (Remotion), danach Texte/Titelbild aus dem Baukasten | `werkzeuge/video-shotcraft` |
| nur ein Titelbild (auch für alte Reels) | Standbild ohne Texte + Sticker | `baukasten/standbild.py`, `baukasten/titelbild.cjs` |

Nie Tafel-Szene und Selfie in einem Reel mischen (kam so schlecht an, dass es gelöscht wurde). Gesicht nur dort, wo es
selbst der Inhalt ist.

## Ablauf

1. **Idee in einem Satz klären**: Was ist das eine Versprechen? Welche Reihe (Farbe)? Welches Kommentar-Wort?
   Hook in Alltagssprache vorschlagen (2–3 Varianten), bei Unklarheit fragen. Siehe `regeln/hook-und-inhalt.md`.
2. **Ordner anlegen**: `py baukasten/neues_reel.py tafel <Name>` bzw. `gesicht <Name>` → `reels/<Datum>-<Name>/`
   mit `schnitt/bauen.py`, `texte/texte.json`, `CAPTION.md`.
3. **Material hinein**: App-Aufnahme nach `bildschirm/` (Tafel-Reel) bzw. Kamera-Clips nach `aufnahmen/` (Gesicht-Reel).
4. **Texte** in `texte/texte.json` (Reihe, Hook, Sticker, Pille, Wort), dann `node baukasten/texte.cjs reels/<Ordner>`.
5. **Bauen** (aus `reels/<Ordner>/schnitt/`):
   - Tafel: `python bauen.py --probe 1,5,9` (Standbilder ansehen!) → `python bauen.py --ton` → `python bauen.py` → `python bauen.py --titel`
   - Gesicht: `python bauen.py --liste` → `python bauen.py --kontakt` (Augen/Blick prüfen) → `python bauen.py` → `python bauen.py --titel <Sekunde>`
6. **Selbst prüfen**, bevor du etwas zeigst (Standbilder in voller Größe ansehen, nicht nur Zahlen):
   - Hook in der ersten Sekunde lesbar/hörbar? Nichts in den gesperrten Zonen (y < 160, y > 1520, rechts x > 940)?
   - Tafel-Inhalt groß und scharf lesbar? Kein blauer QR-Kasten, kein Mauszeiger im Titelbild?
   - Untertitel stimmen Wort für Wort mit dem Gesagten, sitzen auf y 1240 (oder 700), höchstens ein gelbes Wort?
   - Endkarte 1,5–2 s mit richtigem Wort? Titelbild-3x4-Vorschau: Titel ganz im Bild, Augen offen?
   - Ton: Stimme −19 LUFS (Gesicht) bzw. Effekte leise; keine Musik eingebaut.
7. **Abgeben**: Video, `Titelbild.jpg`, Caption (Text aus `CAPTION.md`) – siehe `regeln/caption-und-abgabe.md`.
   Neue Fassung = neue Datei (`-v2`), alte nie überschreiben.

## Harte Regeln (Kurzfassung)

- Nur echte Ansichten der Seite, keine KI-Bilder der Oberfläche (erfinden Text und QR). Echte Bewegungen nie beschleunigen.
- Kein Glücksrad und kein Klassenraumplaner (werden umgebaut). Vokabeln/Karteikarten nie als Lehrkraft-Funktion zeigen.
- „kostenlos“ ja, **nie** „für immer kostenlos“. Nirgends „POV“. HYROX nie nennen.
- Beispielinhalte: echte, neutrale Unterrichtsfragen (Geschichte, Englisch, Deutsch, Erdkunde …), keine Tagespolitik,
  nichts mit Mathe, keine echten Kinder, keine Klassenstufen auf Ausmalbildern.
- Neutral sprechen: nichts aus „meiner Klasse“ erzählen; direkt an eine Person („Kennst du das?“). Keine Werbe-Sprache.
- Keine selbst komponierte oder synthetisierte Musik. Musik legt, wer postet, in Instagram drunter.
- Seitenverhältnis immer erhalten, nie verzerren. Kein Wackeln als Effekt.
- Nur kostenlose Werkzeuge. Downloads (Modelle, Musik, Bilder) nur nach Rückfrage mit Datei, Quelle und Größe.
- Rückfrage bei Philipp: neue Reihe/Farbe, Musik-Track, neues Werkzeug im Reel, alles Politische, Gesicht anderer Personen.

## Werkzeuge einrichten

Siehe `README.md` (Python 3.11+, FFmpeg, Node 20+, `pip install -r requirements.txt`, `npm install`,
`npx playwright install chromium`). Fehlt etwas, die Fehlermeldung lesen und die Einrichtung nachholen, nicht umbauen.
