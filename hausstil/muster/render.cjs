// Rendert muster.html als PNG (Playwright aus _demo-seite, nur gelesen).
const { chromium } = require("C:/Users/phili/Desktop/Lehrerkoffer-Flyer/_demo-seite/node_modules/playwright");
const path = require("path");
const { pathToFileURL } = require("url");
(async () => {
  const b = await chromium.launch({ executablePath: path.join(process.env.LOCALAPPDATA, "ms-playwright/chromium-1234/chrome-win64/chrome.exe") });
  const p = await b.newPage({ viewport: { width: 1700, height: 1180 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(path.join(__dirname, "muster.html")).href);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, "..", "Hausstil-Vorschlag.png") });
  await b.close();
})();
