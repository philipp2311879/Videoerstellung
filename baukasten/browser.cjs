// Gemeinsamer Browser-Start für texte.cjs und titelbild.cjs.
// Playwright kommt aus dem node_modules des Repos (npm install). Chromium: `npx playwright install chromium`.
// Eigener Chromium-Pfad geht per Umgebungsvariable CHROMIUM_PFAD, ein anderes Playwright per PLAYWRIGHT_PFAD.
const path = require("path");
const fs = require("fs");
const { pathToFileURL } = require("url");

function playwright() {
  if (process.env.PLAYWRIGHT_PFAD) return require(process.env.PLAYWRIGHT_PFAD);
  try {
    return require("playwright");
  } catch (e) {
    console.error("Playwright fehlt. Im Repo-Ordner einmal ausführen:  npm install  und  npx playwright install chromium");
    process.exit(1);
  }
}

async function browser() {
  const opt = {};
  if (process.env.CHROMIUM_PFAD) opt.executablePath = process.env.CHROMIUM_PFAD;
  return playwright().chromium.launch(opt);
}

const REPO = path.resolve(__dirname, "..");
const schrift = (n) => pathToFileURL(path.join(REPO, "hausstil", "schriften", n)).href;

// Reihenfarben aus hausstil/HAUSSTIL.md. Neue Reihe = neue Farbe nur nach Rückfrage bei Philipp.
const REIHEN = {
  blau: { verlauf: "#1f5bff, #2f8dff 45%, #19b4ff", pille: "#1f6bff" },        // Werkzeug / Rätsel
  pink: { verlauf: "#ff4fa0, #ff7ac8 33%, #b57bff 66%, #ff9e6b", pille: "#ff69b4" }, // Freebie Friday (Escape-Room)
  gruen: { verlauf: "#18a957, #39c46b 50%, #8bd43a", pille: "#1fae5b" },       // Klassenspiel
  orange: { verlauf: "#ff8a00, #ffb000 50%, #ffcc33", pille: "#ff9500" },      // Ihr wünscht, wir bauen (Sonntag)
};

function reihe(name) {
  const r = REIHEN[name || "blau"];
  if (!r) {
    console.error(`Unbekannte Reihe "${name}". Erlaubt: ${Object.keys(REIHEN).join(", ")}`);
    process.exit(1);
  }
  return r;
}

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

// Sticker-HTML: Zeilen mit | trennen ("Freebie|Friday")
function sticker(text) {
  return String(text).split("|").map((z) =>
    `<div class="z"><span class="rand">${esc(z)}</span><span class="fuell">${esc(z)}</span></div>`).join("<br>");
}

// CSS für Sticker, Pille, Sätze und Untertitel (eine Quelle für alle Skripte)
function css(r) {
  return `
@font-face { font-family: "Fredoka"; src: url("${schrift("fredoka.woff2")}") format("woff2"); font-weight: 300 700; }
@font-face { font-family: "Inter"; src: url("${schrift("Inter-ExtraBold.ttf")}"); font-weight: 800; }
.satz { position: absolute; left: 70px; right: 70px; text-align: center; font: 800 78px/1.12 "Inter"; color: #fff; letter-spacing: -.5px;
  text-shadow: 0 0 4px rgba(0,0,0,.9), 0 0 14px rgba(0,0,0,.75), 0 4px 26px rgba(0,0,0,.55); }
.satz em, .ut em { font-style: normal; color: #ffd43b; }
.ut { position: absolute; left: 30px; right: 30px; text-align: center; white-space: nowrap; font: 800 80px/1 "Inter"; color: #fff;
  letter-spacing: -.5px; transform: translateY(-50%);
  text-shadow: 0 0 4px rgba(0,0,0,.9), 0 0 14px rgba(0,0,0,.75), 0 4px 26px rgba(0,0,0,.55); }
.sticker { position: absolute; left: 0; right: 0; text-align: center; transform: rotate(-3deg); }
.z { position: relative; display: inline-block; font: 700 var(--gr, 150px)/1 "Fredoka"; white-space: nowrap; }
.z + br + .z { margin-top: -.06em; }
.rand { position: absolute; left: 0; top: 0; color: #fff; -webkit-text-stroke: calc(var(--gr, 150px) * .17) #fff;
  filter: drop-shadow(0 10px 0 rgba(20,37,79,.35)) drop-shadow(0 16px 26px rgba(0,0,0,.4)); }
.fuell { position: relative; background-image: linear-gradient(100deg, ${r.verlauf}); -webkit-background-clip: text; background-clip: text; color: transparent; }
.pille { display: inline-block; margin-top: 18px; padding: 12px 40px 16px; border-radius: 70px; border: 8px solid #fff; background: ${r.pille};
  color: #fff; font: 600 var(--pg, 56px)/1 "Fredoka"; letter-spacing: 1px; box-shadow: 0 8px 22px rgba(0,0,0,.35); transform: rotate(2deg); white-space: nowrap; }
.adresse { position: absolute; left: 0; right: 0; text-align: center; font: 800 46px "Inter"; color: #fff;
  text-shadow: 0 0 4px rgba(0,0,0,.9), 0 0 12px rgba(0,0,0,.7); }`;
}

// Zu breite Sticker-Zeilen verkleinern (Rand und Schatten brauchen Platz bis zum Bildrand)
async function stickerEinpassen(page, sel = ".sticker", maxBreite = 930) {
  await page.evaluate(([sel, maxBreite]) => {
    for (const s of document.querySelectorAll(sel)) {
      if (!s.offsetParent && getComputedStyle(s).display === "none") continue;
      const gr = parseFloat(getComputedStyle(s).getPropertyValue("--gr")) || 150;
      const zeilen = [...s.querySelectorAll(".z")];
      if (!zeilen.length) continue;
      const breit = Math.max(...zeilen.map((z) => z.getBoundingClientRect().width));
      if (breit > maxBreite) s.style.setProperty("--gr", (gr * maxBreite / breit).toFixed(1) + "px");
    }
  }, [sel, maxBreite]);
}

module.exports = { browser, REPO, schrift, REIHEN, reihe, esc, sticker, css, stickerEinpassen, fs, path, pathToFileURL };
