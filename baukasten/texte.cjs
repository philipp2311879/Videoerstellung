// Alle Texte eines Reels im Hausstil (hausstil/HAUSSTIL.md) als durchsichtige PNGs (1080 x 1920).
// Gleiche Gestaltung wie das Wortwolke-Reel und die Tafel-Reels.
//
// Aufruf:  node baukasten/texte.cjs <Reel-Ordner>
// liest   <Reel-Ordner>/texte/texte.json  (und, falls da, texte/untertitel.json, schreibt gesichtreel.py)
// schreibt <Reel-Ordner>/texte/
//   hook.png, satz2.png, satz3.png   Sätze oben (Reels ohne Person)
//   oben.png                         Sticker + Pille groß oben, erste ca. 2 s (Reels mit Gesicht)
//   ende.png                         Endkarte: Sticker + Pille „Kommentiere WORT“ + lehrerkoffer.de (+ ende_satz)
//   titel.png                        Sticker + Pille in der Mitte des 3:4-Ausschnitts (fürs Titelbild)
//   ut-000.png …                     Untertitel-Häppchen (Inter ExtraBold 80 px, Mitte y 1240 bzw. 700 „oben“)
//
// texte.json (alles optional außer sticker/wort/pille):
// {
//   "reihe": "blau" | "pink" | "gruen" | "orange",           Farbe der Reihe, Standard blau
//   "hook":  {"html": "Satz mit <em>Schlüsselwort</em>", "top": 178, "size": 66},
//   "satz2": {...}, "satz3": {...}, "ende_satz": {...},
//   "sticker": "Umfrage",            Titel (höchstens 3 Wörter; Zeilenumbruch mit |)
//   "pille": "Wer liegt richtig?",   Pille unter dem Titel auf Titelbild
//   "pille_oben": "Klassenspiel",    Pille im Reel oben (Standard: wie pille)
//   "wort": "UMFRAGE",               Kommentar-Wort der Endkarte
//   "sticker_gr": 150, "titel_gr": 170, "oben_gr": 140, "titel_top": 1080
// }
const { browser, reihe, sticker, css, stickerEinpassen, esc, fs, path, pathToFileURL } = require("./browser.cjs");

const ordner = path.resolve(process.argv[2] || ".");
const tx = path.join(ordner, "texte");
const cfgPfad = path.join(tx, "texte.json");
if (!fs.existsSync(cfgPfad)) {
  console.error("Fehlt: " + cfgPfad);
  process.exit(1);
}
const cfg = JSON.parse(fs.readFileSync(cfgPfad, "utf8"));
const utPfad = path.join(tx, "untertitel.json");
const untertitel = fs.existsSync(utPfad) ? JSON.parse(fs.readFileSync(utPfad, "utf8")) : [];
const r = reihe(cfg.reihe);

const satz = (s) => (s ? `<div class="satz" style="top:${s.top}px; font-size:${s.size}px">${s.html}</div>` : "");
const sterne = (t) => esc(t).replace(/\*([^*]+)\*/g, "<em>$1</em>");     // *Wort* -> gelb
const gr = cfg.sticker_gr || 150, grT = cfg.titel_gr || 170, grO = cfg.oben_gr || 140;

const varianten = [];
if (cfg.hook) varianten.push("hook");
if (cfg.satz2) varianten.push("satz2");
if (cfg.satz3) varianten.push("satz3");
if (cfg.sticker) varianten.push("oben", "titel");
if (cfg.wort) varianten.push("ende");

const html = `<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
${css(r)}
html, body { margin: 0; width: 1080px; height: 1920px; background: transparent; overflow: hidden; }
.v { display: none; position: absolute; inset: 0; }
${["hook", "satz2", "satz3", "oben", "titel", "ende", "utebene"].map((v) => `body[data-v="${v}"] .${v}`).join(", ")} { display: block; }
</style></head><body data-v="hook">
<div class="v hook">${satz(cfg.hook)}</div>
<div class="v satz2">${satz(cfg.satz2)}</div>
<div class="v satz3">${satz(cfg.satz3)}</div>
<div class="v oben">
  <div class="sticker" style="top:290px; --gr:${grO}px">${cfg.sticker ? sticker(cfg.sticker) : ""}<br><div class="pille" style="--pg:52px">${esc(cfg.pille_oben || cfg.pille || "")}</div></div>
</div>
<div class="v titel">
  <div class="sticker" style="top:${cfg.titel_top || 1080}px; --gr:${grT}px">${cfg.sticker ? sticker(cfg.sticker) : ""}<br><div class="pille" style="--pg:60px">${esc(cfg.pille || "")}</div></div>
</div>
<div class="v ende">
  <div class="sticker" style="top:1130px; --gr:${gr}px">${cfg.sticker ? sticker(cfg.sticker) : ""}<br><div class="pille">Kommentiere ${esc(cfg.wort || "")}</div></div>
  <div class="adresse" style="top:1440px">lehrerkoffer.de</div>
  ${satz(cfg.ende_satz)}
</div>
<div class="v utebene"><div class="ut" id="ut"></div></div>
<script>
const q = new URLSearchParams(location.search);
document.body.dataset.v = q.get("v") || "hook";
</script>
</body></html>`;

(async () => {
  const datei = path.join(tx, "_texte.html");
  fs.writeFileSync(datei, html);
  const b = await browser();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  for (const v of varianten) {
    await p.goto(pathToFileURL(datei).href + "?v=" + v);
    await p.evaluate(() => document.fonts.ready);
    await stickerEinpassen(p, `.${v} .sticker`);
    await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(tx, v + ".png"), omitBackground: true });
  }
  // Untertitel-Häppchen
  for (const f of fs.readdirSync(tx)) if (/^ut-\d+\.png$/.test(f)) fs.unlinkSync(path.join(tx, f));
  if (untertitel.length) {
    await p.goto(pathToFileURL(datei).href + "?v=utebene");
    await p.evaluate(() => document.fonts.ready);
    for (let i = 0; i < untertitel.length; i++) {
      const u = untertitel[i];
      await p.evaluate(([inhalt, y]) => {
        const el = document.getElementById("ut");
        el.innerHTML = inhalt;
        el.style.top = y + "px";
        el.style.fontSize = "80px";
        // zu breit (über 1020 px): verkleinern, nie umbrechen
        const w = el.scrollWidth;
        if (w > 1020) el.style.fontSize = (80 * 1020 / w).toFixed(1) + "px";
      }, [sterne(u.text), u.oben ? 700 : 1240]);
      await p.screenshot({ path: path.join(tx, `ut-${String(i).padStart(3, "0")}.png`), omitBackground: true });
    }
  }
  await b.close();
  console.log("Texte fertig:", varianten.join(", ") + (untertitel.length ? `, ${untertitel.length} Untertitel` : ""));
})();
