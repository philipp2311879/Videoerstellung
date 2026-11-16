// Titelbild im Hausstil: Hintergrund (1080 x 1920, ohne eingebrannte Texte) + Sticker in Reihenfarbe + Pille,
// Titel in der Mitte des 3:4-Ausschnitts, den Instagram im Profilraster zeigt (y 240–1680).
//
// Aufruf:
//   node baukasten/titelbild.cjs <hintergrund.png|jpg> <Ausgabe-Ordner> --sticker "Begriffe raten" --pille "Vertretungsstunde"
//        [--reihe blau|pink|gruen|orange] [--top 1080] [--gr 170] [--zoom 1.0]
// schreibt <Ausgabe-Ordner>/Titelbild.jpg und Titelbild-3x4-Vorschau.jpg (immer ansehen: ist der Titel ganz zu sehen?).
// Hintergrund holen: py baukasten/standbild.py <video> <sekunde> <hintergrund.png>
// (Gesicht mit offenen Augen und Ausdruck, nie mitten im Wort; ohne Person das stärkste Bild der App, bei Rate-Reels ohne Lösung.)
const { browser, reihe, sticker, css, stickerEinpassen, esc, fs, path, pathToFileURL } = require("./browser.cjs");

const args = process.argv.slice(2);
const pos = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));
const opt = (n, std) => {
  const i = args.indexOf("--" + n);
  return i >= 0 ? args[i + 1] : std;
};
if (pos.length < 2 || !opt("sticker")) {
  console.error('Aufruf: node titelbild.cjs <hintergrund> <ausgabe-ordner> --sticker "Titel" --pille "Pille" [--reihe blau]');
  process.exit(1);
}
const [bg, aus] = pos.map((p) => path.resolve(p));
const r = reihe(opt("reihe", "blau"));
const zoom = parseFloat(opt("zoom", "1"));

const html = `<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
${css(r)}
html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }
.bg { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
</style></head><body>
<img class="bg" src="${pathToFileURL(bg).href}" style="${zoom !== 1 ? `transform: scale(${zoom}); transform-origin: 50% 100%;` : ""}">
<div class="sticker" style="top:${opt("top", 1080)}px; --gr:${opt("gr", 170)}px">${sticker(opt("sticker"))}<br><div class="pille" style="--pg:60px">${esc(opt("pille", ""))}</div></div>
</body></html>`;

(async () => {
  fs.mkdirSync(aus, { recursive: true });
  const tmp = path.join(aus, "_titelbild.html");
  fs.writeFileSync(tmp, html);
  const b = await browser();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(tmp).href);
  await p.evaluate(() => document.fonts.ready);
  await stickerEinpassen(p);
  await p.waitForTimeout(150);
  await p.screenshot({ path: path.join(aus, "Titelbild.jpg"), type: "jpeg", quality: 93 });
  await p.screenshot({ path: path.join(aus, "Titelbild-3x4-Vorschau.jpg"), type: "jpeg", quality: 90,
    clip: { x: 0, y: 240, width: 1080, height: 1440 } });
  const box = await p.evaluate(() => {
    const b = document.querySelector(".sticker").getBoundingClientRect();
    return [Math.round(b.top), Math.round(b.bottom)];
  });
  await b.close();
  fs.unlinkSync(tmp);
  const ok = box[0] >= 240 && box[1] <= 1680;
  console.log(`Titelbild -> ${path.join(aus, "Titelbild.jpg")}  (Titel y ${box[0]}–${box[1]}: ${ok ? "im 3:4-Raster" : "ACHTUNG, ragt aus dem 3:4-Raster"})`);
})();
