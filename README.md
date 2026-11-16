# Lehrerkoffer – Videoerstellung

Alles, was wir brauchen, um Reels für Lehrerkoffer so zu bauen, wie wir sie machen: Hausstil (Schriften, Farben,
Positionen), Baukasten-Skripte, Klassenraum-Bilder, Soundeffekte, Klaviertöne, Shotcraft – und ein **Claude-Code-Skill**,
der weiß, wie Hook, Titelbild, Untertitel, Ton und Caption aussehen müssen.

## So benutzt du es (Mo)

1. Repo holen:
   ```bash
   git clone https://github.com/philipp2311879/Videoerstellung.git
   ```
2. Einmal einrichten (siehe unten).
3. Den Ordner in Claude Code öffnen und sagen, was du willst, z. B.
   „Mach ein Tafel-Reel zur Wortwolke mit der Frage ‚Was fällt dir zum Mittelalter ein?‘“ oder
   „Schneid aus den Clips in `reels/…/aufnahmen` ein Reel mit Gesicht, Reihe Klassenspiel, Wort VERTRETUNG“.
   Der Skill `lehrerkoffer-reel` (`.claude/skills/lehrerkoffer-reel/`) lädt automatisch und baut nach unseren Regeln.
4. Fertig sind immer drei Dinge: Video, `Titelbild.jpg`, Caption. Die kommen in den Content-Planer, nicht ins Git.
5. Neues Material (Skripte, Texte, kleine App-Aufnahmen) committen und pushen, damit wir beide denselben Stand haben:
   ```bash
   git pull
   ```
   vor dem Arbeiten, danach `git add`, `git commit`, `git push`.

## Einrichten (einmal)

Nötig: **Python 3.11+**, **FFmpeg** (ffmpeg und ffprobe im PATH), **Node 20+**, Git. Alles kostenlos.

Windows (PowerShell):
```bash
winget install Python.Python.3.12 Gyan.FFmpeg OpenJS.NodeJS.LTS Git.Git
```
Mac:
```bash
brew install python ffmpeg node git
```

Dann im Repo-Ordner:
```bash
pip install -r requirements.txt
```
```bash
npm install
```
```bash
npx playwright install chromium
```
Optional für genaue Untertitel-Zeiten (lädt beim ersten Lauf ein Whisper-Modell, ca. 500 MB):
```bash
pip install faster-whisper
```
Optional für Shotcraft (Remotion-Kamerafahrten, Editor im Browser): `cd werkzeuge/video-shotcraft/workbench` und
`npm install` (Anleitung in `werkzeuge/video-shotcraft/README.md`).

Test, ob alles läuft (baut das Umfrage-Reel nach, ein paar Minuten):
```bash
node baukasten/texte.cjs beispiele/01-Umfrage
```
```bash
cd beispiele/01-Umfrage/schnitt && python bauen.py --ton && python bauen.py && python bauen.py --titel
```
Ergebnis: `beispiele/01-Umfrage/fertig/Umfrage-v1.mp4` und `Titelbild.jpg`.
(Unter Windows heißt `python` evtl. `py`.)

## Was wo liegt

| Ordner | Inhalt |
|---|---|
| `.claude/skills/lehrerkoffer-reel/` | Der Skill: Ablauf (`SKILL.md`) und Regeln (`regeln/`: Hook und Inhalt, Tafel-Reels, Gesicht-Reels, Ton, Caption und Abgabe) |
| `hausstil/` | `HAUSSTIL.md` (verbindlich), Schriften Fredoka + Inter ExtraBold, Muster-Bild |
| `baukasten/` | `tafelreel.py` (Tafel-Reels), `gesichtreel.py` (Reels mit Gesicht), `texte.cjs` (Hook, Untertitel, Sticker, Endkarte), `titelbild.cjs`, `standbild.py`, `neues_reel.py` |
| `raeume/` | Klassenraum-Fotos mit grüner Tafel (hochgerechnet), Ecken und Masken |
| `beispiele/` | Fertig gebaute Reels zum Nachbauen und Abschauen: Wortwolke (Vorbild), Umfrage, Standpunkt, Timer, Satzbaustelle |
| `reels/` | Neue Reels, je ein Ordner (`py baukasten/neues_reel.py tafel <Name>` oder `gesicht <Name>`) |
| `werkzeuge/video-shotcraft/` | Remotion-Werkbank mit Kamerafahrten, Soundeffekten (Mixkit) und Editor (Apache-2.0, github.com/Vincentwei1021/video-shotcraft) |
| `werkzeuge/klavier/` | Steinway-Einzeltöne (University of Iowa, frei ohne Einschränkungen) |

## Was nicht hier liegt

- Rohaufnahmen und fertige Videos (zu groß für Git) → Content-Planer / Google Drive.
- Die Demo-Seite mit Dummy-Daten, aus der Philipp die App-Aufnahmen macht. App-Aufnahmen bekommst du von Philipp
  (MP4 + Marken-JSON) oder nimmst sie selbst auf lehrerkoffer.de auf (Anleitung im Skill, `regeln/tafel-reels.md`).
- Real-ESRGAN (nur für neue Klassenraum-Bilder nötig): kostenlos bei github.com/xinntao/Real-ESRGAN (Releases,
  `realesrgan-ncnn-vulkan`).
