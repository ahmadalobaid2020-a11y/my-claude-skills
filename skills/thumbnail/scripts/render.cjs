#!/usr/bin/env node
// Render a thumbnail HTML page to PNG, plus a small preview to judge readability.
// Usage: node render.cjs page.html out.png [--width 1280 --height 720] [--preview 320]
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : def;
};
const [input, output] = args.filter((a, i) => !a.startsWith("--") && !(args[i - 1] || "").startsWith("--"));
if (!input || !output) {
  console.error("usage: node render.cjs page.html out.png [--width 1280] [--height 720] [--preview 320]");
  process.exit(1);
}
const width = Number(opt("width", 1280));
const height = Number(opt("height", 720));
const preview = Number(opt("preview", 320));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.resolve(input), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  const failed = await page.evaluate(() =>
    [...document.fonts].filter((f) => f.status === "error").map((f) => f.family)
  );
  if (failed.length) console.warn("fonts failed to load:", [...new Set(failed)].join(", "));
  await page.screenshot({ path: output, clip: { x: 0, y: 0, width, height } });

  if (preview > 0) {
    const small = output.replace(/\.png$/i, "") + `.preview${preview}.png`;
    const img = "data:image/png;base64," + fs.readFileSync(output).toString("base64");
    const p2 = await browser.newPage({
      viewport: { width: preview, height: Math.round((preview * height) / width) },
    });
    await p2.setContent(`<body style="margin:0"><img src="${img}" style="width:100%;display:block"></body>`);
    await p2.screenshot({ path: small });
    console.log("preview:", small);
  }
  await browser.close();
  const kb = Math.round(fs.statSync(output).size / 1024);
  console.log(`thumbnail: ${output} (${width}x${height}, ${kb} KB)`);
  if (kb > 2000) console.warn("over YouTube's 2 MB limit: convert to JPEG (ffmpeg -i in.png -q:v 3 out.jpg)");
})();
