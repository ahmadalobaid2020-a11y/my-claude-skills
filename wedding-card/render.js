// Renders card.html frame by frame and encodes a WhatsApp-ready MP4.
// Usage: node render.js [--preview]   (preview = a few still frames only)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DURATION = 25.5;
const dir = __dirname;
const frames = path.join(dir, '.frames');
const preview = process.argv.includes('--preview');

(async () => {
  fs.rmSync(frames, { recursive: true, force: true });
  fs.mkdirSync(frames, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.join(dir, 'card.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);

  if (preview) {
    for (const t of [1.8, 4.6, 5.6, 10.8, 17, 24]) {
      await page.evaluate(s => window.seek(s), t);
      await page.screenshot({ path: path.join(frames, `p_${t}.png`) });
    }
    await browser.close();
    return;
  }

  const total = Math.round(FPS * DURATION);
  for (let i = 0; i < total; i++) {
    await page.evaluate(s => window.seek(s), i / FPS);
    await page.screenshot({ path: path.join(frames, `f_${String(i).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 95 });
    if (i % 90 === 0) console.log(`frame ${i}/${total}`);
  }
  await page.evaluate(s => window.seek(s), 10.8);
  await page.screenshot({ path: path.join(dir, 'poster.jpg'), type: 'jpeg', quality: 90 });
  await browser.close();

  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, 'f_%04d.jpg'),
    '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100', '-shortest',
    '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow',
    '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', path.join(dir, 'wedding-invitation.mp4')], { stdio: 'inherit' });
  fs.rmSync(frames, { recursive: true, force: true });
  console.log('done');
})();
