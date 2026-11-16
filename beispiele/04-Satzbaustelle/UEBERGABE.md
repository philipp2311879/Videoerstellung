# Übergabe Satzbaustelle v2 (16.11.2026)

## Stand: fertig gebaut

- Video: `fertig\Satzbaustelle-v2.mp4` (1080x1920, 17,5 s), Titelbild `fertig\Titelbild.jpg` + `Titelbild-3x4-Vorschau.jpg`,
  Caption `CAPTION.md` (zum Kopieren `fertig\Caption.txt`), alte Caption `CAPTION-v1.md`, alte Fassung `fertig\Satzbaustelle-v1.mp4`
  und `fertig\Titelbild-v1.jpg` bleiben liegen.
- Inhalt: Hook „Achte nur auf den roten Stein. Am Ende verstehst du, warum.“, Reihe 1 „Pinguine | machen | Heiratsanträge |
  mit Steinen | .“, „Machen“ und „?“ ploppen auf, Reihe 2 „Machen | Pinguine | Heiratsanträge | mit Steinen | ?“; dann „Deine SuS
  bauen beide Sätze einzeln auf ihrem iPad“, Fahrt mit „Vorne siehst du dann: Das Verb springt nach vorne“, Endkarte mit
  „Schick das einer Lehrkraft, die Deutsch unterrichtet.“ + „Kommentiere SATZBAUSTELLE“ + lehrerkoffer.de.
- Nutzer 16.11.: Steine müssen groß und scharf lesbar sein -> App auf die Steinfläche zugeschnitten, Kamera: Tafel füllt die
  Breite (Variante „ganz“ = ganzes Foto per `python bauen.py --kamera ganz`). Ton „Klavier hoch mit Nachspiel“ freigegeben
  („der Ton ist nun sehr gut“); Kristall-Glöckchen abgelehnt.

## Bauen

1. Aufnahme: `_demo-seite\_aufnahme\sb2-tafel.cjs` (Demo-Server `demo-seite` aus `.claude\launch.json`), schreibt
   `bildschirm\sb2-tafel.mp4` + `-marks.json`. Steine landen auf festen Bildnummern (Viertel = 24 Bilder).
2. `schnitt\bauen.py --ton hoch`, `schnitt\bauen.py` (10 Teile parallel, ca. 4 Min.), `schnitt\bauen.py --titel`,
   Standbilder `schnitt\bauen.py --probe 0.5,6.4,10.9,12.6,16`. Synchronität prüfen: `schnitt\pruefe_sync.py`.

## Offen

- Erledigt 16.11. (Nutzer: „Ja, auf v2 umstellen“): Im Content-Planer „Tafel-Reel Satzbaustelle … (Pinguine, v2)“, Mi 18.11.,
  18:00, lädt hoch: mo. Video, Vorschaubild (Titelbild), Caption, Notizen und To-do für mo zeigen auf v2. Drive: „2026-11-18
  Tafel-Reel Satzbaustelle v2 Pinguine (Aussage oder Frage).mp4“ und „… v2 – Titelbild.jpg“; die v1-Dateien liegen noch daneben.
- Der Nutzer lädt selbst hoch (16.11.). Vor dem Posten: automatische Nachricht für SATZBAUSTELLE.
