# Ton

## Stimme (Reels mit Gesicht)

- **Originalton nehmen** (neues Mikro seit 09.11.2026): „durch deine Bearbeitung ist der Ton zu schlecht geworden, original
  Audio einfach drauf.“ Keine KI-Enthallung, kein EQ, kein Kompressor, kein Gate – außer Philipp fragt ausdrücklich danach.
- Nur die Teile gleich laut machen (je Teil auf −20 LUFS), am Ende **feste Verstärkung auf −19 LUFS** + Begrenzer −1,5 dBFS.
  (−16 LUFS war Philipp „bisschen laut“.) `gesichtreel.py` macht das; Ergebnis mit ffmpeg `ebur128` nachmessen.
- Achtung bei eigenen Skripten: ffmpegs `alimiter` hebt ohne `level=false` alles wieder auf 0 dBFS an.
- Hört es sich hallig oder dumpf an: nicht „wegbearbeiten“, sondern Aufnahme prüfen (Mikro nah, Rauschunterdrückung aus)
  und Philipp fragen. Ein Funk-Ansteckmikro über USB klang in jeder Position dumpf.

## Soundeffekte

- Leise **Mixkit-Effekte** aus `werkzeuge/video-shotcraft/assets/audio/sfx/` (Quellen in `assets/audio/ATTRIBUTION.md`).
  Bewährt (Wortwolke, „die Töne von Wortwolke sind wirklich toll“): `ui/ui-popup-dry.mp3` (neues Element),
  `ui/ui-select-click.mp3` (Klick), `transition/sweep-short.mp3`, `ui/ui-success-soft.mp3` (Ergebnis),
  `transition/swoosh-slow.mp3` + `light/shimmer-sparkle-sweep.mp3` (Fahrt am Ende).
- Unter einer Stimme etwa 10 dB leiser als die Stimme; Effekte allein müssen sehr weich sein („zu aggressiv“ abgelehnt).
- **Genau aufs Bild**: der Ton liegt auf dem Bild, auf dem das Element erscheint/landet (`wechsel_zeiten()` findet sie).
- Wenn es musikalisch sein soll („satisfying“): **echte Instrumenten-Einzeltöne**, keine UI-Glöckchen.
  Satzbaustelle v2: jeder Stein spielt beim Einrasten seinen Ton von „Jingle Bells“ (Steinway-Töne der University of Iowa,
  frei ohne Einschränkungen, `werkzeuge/klavier/`, Skript `beispiele/04-Satzbaustelle/schnitt/klavier.py`). Das
  Kristall-Glöckchen fand Philipp „mehr als schrecklich“. Proben zum Anhören schicken, bevor das Video gebaut wird.

## Musik

- **Nie selbst Musik komponieren oder synthetisieren**, auch wenn sie gut klingt.
- Reels werden **ohne Musik** geliefert (Tafel-Reels mit leisen Effekten). Musik legt, wer postet, in Instagram drunter,
  eher ruhig und leise. Erzähl-Reels mit Stimme: ohne oder sehr leise.
- Die BGM-Tracks in Shotcraft (Trap/Phonk) nicht nehmen; „destroy“ ist abgenutzt. Andere Tracks nur nach Rückfrage.
