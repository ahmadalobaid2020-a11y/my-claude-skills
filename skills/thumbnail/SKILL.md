---
name: thumbnail
description: Design YouTube thumbnails (1280x720 PNG/JPEG) with bold Arabic or English text over a video frame, photo or generated image. Use for "صورة مصغرة", "ثمبنيل", "thumbnail", "cover image", or variants for A/B testing.
---

# thumbnail

Build the thumbnail as an HTML page, render it with Chromium, then judge it at small size.

- Template: `~/.claude/skills/thumbnail/template.html` (Arabic RTL, Cairo font, dark gradient, highlight word, badge)
- Render: `node ~/.claude/skills/thumbnail/scripts/render.cjs page.html out.png`
  - writes `out.png` (1280x720) and `out.preview320.png`; other sizes: `--width 1080 --height 1920` (Shorts), `--width 1280 --height 1280`
  - warns when a web font fails to load or the file is over YouTube's 2 MB limit

## Workflow

1. Ask only what is missing: video topic, the 2–5 words to show, language, and the background (a frame from their video, a photo, or a generated image).
2. Work in a folder in the user's working directory. Copy the template to `thumb.html` there and put the background beside it as `background.jpg`:
   - frame from a video: `ffmpeg -ss 00:01:23 -i video.mp4 -frames:v 1 -q:v 2 background.jpg` (try several times, pick the sharpest face or action)
   - generated image: use an image tool the session has; ask for a 16:9 picture with empty space on the text side and no text in it
   - no background: delete the `url(...)` part and use a solid or gradient `--bg`
3. Edit text, colors and layout. Rules that make thumbnails work:
   - 2–5 words, never the full video title; one highlighted word in the accent colour
   - text at least ~90px, heavy weight, outline or shadow; strong contrast with the background
   - one focal point (a face with clear emotion, or one object); text on one side, subject on the other
   - nothing important in the bottom-right corner (YouTube's duration badge)
   - Arabic: keep `dir="rtl"`, use Cairo or Tajawal from Google Fonts; English: `font-family: "Anton"` or `"Bebas Neue"` look strong
4. Render, then open BOTH images with Read. Judge the 320px preview: can you read the words and see the subject instantly? Fix and re-render until yes.
5. For A/B tests make 2–3 variants that differ in one thing (text, colour, or crop) and name them `thumb-a.png`, `thumb-b.png`.
6. Deliver the PNG path(s); give a JPEG (`ffmpeg -i thumb.png -q:v 3 thumb.jpg`) if the PNG is over 2 MB. Only use photos, logos and faces the user has the right to use.
