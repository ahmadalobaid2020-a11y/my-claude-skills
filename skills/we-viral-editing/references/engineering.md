# Engineering: render stack, audio mix, reformatting, sibling skills

## Render stack (code-driven edits)
- **Cut**: EDL JSON `{"sources":{"src":"<path>"},"ranges":[{"start":a,"end":b,"note":"…"}]}` (key is `sources`, a dict) → one concat-filter encode. See `cutting.md`.
- **Graphics**: HyperFrames (HTML + GSAP → video via headless Chrome; `npx hyperframes render`). Output is yuv420p with no alpha: design cards on an opaque band, or render RGBA PNG sequences for overlays. Pin fonts locally (`@font-face`), never system fonts. Transform a wrapper `<div>`, not `<video>`.
- **Composite + mux**: ffmpeg `overlay` with `enable='between(t,A,B)'`; long graphs go in a file via `-/filter_complex graph.txt`. Finish with `-c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -movflags +faststart`.
- **Segmentation**: rembg u2net (~1–2 s/frame CPU, run in background) for popout heads; RVM for full green-screen-style cutouts.
- **Face tracking** for cropped presenter cards: a real landmark detector (MediaPipe eyes/nose), not skin-tone heuristics; crop from the back-of-head side, never into the brow/cheek.
- **HDR phone footage** → SDR before anything: ffmpeg `zscale` tone-map (fallback `colorspace` BT.2020→BT.709). This is a conversion, not a grade.
- Key-moment scouting: 1 fps, 640 px scene-change scout → manifest + contact sheet; go full-res only where needed (scene threshold ~0.4 if too many hits).
- Never write full-res frame dumps to disk; pipe and keep small JPGs. Clean scratch at the end.

## Audio mix
- Order: clean voice (Enhance Speech ~50% → denoise → EQ) → voice to dialog level → music bed → SFX → limiter → loudnorm to −14 LUFS / −1 dBTP (normalise once, at the end).
- Music under speech ≈ 6% linear / −20…−24 dB (≈ −30 LUFS pre-duck), ideally sidechain-ducked by the voice; fades in/out; music-only pieces louder.
- SFX are a **per-client toggle — ask or check `client-bible.md`**. Some talk-only clients want voice only, zero SFX, no music. When SFX are on: generated or library kit mapped to hit type (slam→boom 0.4 s, pill pop→pop 0.25 s, morph/mode change→whoosh 0.35 s, stamp→stamp, counter→tick 0.22 s, CTA reveal→ding), cued at tween start, cue times computed from transcript word times (so re-cuts re-time them). Restraint: whoosh on mode changes only, no pop on every element.
- Mix spec as JSON (per-track offset, gain, fades, duck flag) rendered by one script — never hand-mixed per section.
- Dynamic ducking beats a flat offset when the piece has pauses or B-roll-only stretches: `[music][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[ducked]` then `amix`. Music drops only under speech and breathes back between lines. Flat −20…−24 dB stays fine for continuous talk.
- Final loudness: **two-pass** loudnorm (measure, then apply with measured values) — single-pass dynamic mode is for live only. `ffmpeg-normalize in.mp4 -t -14 -tp -1 -c:a aac -b:a 192k -o out.mp4` does both passes; `--print-stats` measures without re-encoding. Podcasts/long talk may use −16 LUFS if the client asks.
- Declarative edits: describe inserts, titles, transitions and audio tracks as a JSON spec (editly-style: clips → layers → transition, top-level audioTracks) and render from it, so language/music/text variants regenerate from one file.
- ffmpeg: `amix=inputs=N:normalize=0:duration=first` → `alimiter=limit=0.891:level=false` (default `level=true` re-boosts to 0 dB). Verify with `volumedetect`/`ebur128`.
- YouTube long-form default: voice only, `loudnorm=I=-16:TP=-1.5:LRA=11` unless the client wants a bed. **Loudness by platform:** vertical short-form (Reels/TikTok/Shorts) −14 LUFS / −1 dBTP (house); 16:9 YouTube long-form and podcasts −16 LUFS / −1.5 dBTP.
- Voice chain before normalising: highpass ~80 Hz → denoise → gentle +2–3 dB presence around 3–5 kHz → limiter.
- If libass is available and a simple caption style is enough: ASS with explicit `PlayResX=1080` / `PlayResY=1920` (without them positioning drifts on 9:16), style `Alignment=2, MarginL=80, MarginR=80, MarginV≈540` for the house 62–72% position, burned with `-vf subtitles=captions.ass`. Karaoke uses `\kf` tags.
- Presenter PiP over graphics in pure ffmpeg: `chromakey`/cutout → `scale` → rounded alpha mask → blurred shadow underlay → `overlay=…:enable='between(t,A,B)'`.
- Optional guardrailed ffmpeg for agents: `kinocut` (Apache-2.0, MCP + CLI) validates commands before running and writes receipts.

## Reformatting (9:16 ↔ 1:1 ↔ 4:5 ↔ 16:9)
- Sizes: 9:16 1080×1920 · 4:5 1080×1350 · 1:1 1080×1080 · 16:9 1920×1080 (4K doubles).
- Video fit modes: **crop** (fill, lose edges — default for talking heads, focus on the face), **letterbox** (bars/brand BG, nothing lost — for graphics-heavy frames), **stretch** (never).
- Reframe with face focus (tracked crop, fresh decision per shot, blurred-background fallback — full algorithm in `clipping-reframe.md`), then re-place captions/graphics for the new safe zones — don't just crop a finished 9:16 with burned-in text.
- Adobe `video_resize` does letterbox/crop/stretch only (no face-tracked video reframe) and needs uploaded assets, not local paths. For tracked reframes use a crop script driven by face landmarks.
- Batch: one job per target size, deliver the set together.

## Built-in toolkit (works with nothing else installed)
| Job | Tool |
|---|---|
| Transcribe (Scribe via `ELEVENLABS_API_KEY`, else local faster-whisper) | `scripts/transcribe.py` |
| First-pass silence keep-list | `scripts/silence_edl.py` |
| Apply EDL (concat filter, punch-ins, fades) | `scripts/cutjoin.py` |
| Verify the cut (gaps, fragments, dupes, clipped end, script coverage) | `scripts/verify_cut.py` |
| Captions → ASS (house styles, brand colour/font, Arabic) + burn-in | `scripts/captions.py` |
| Voice clean, music bed, ducking, two-pass loudness | `scripts/mix_audio.py` |
| 16:9 → 9:16 face-tracked reframe | `scripts/reframe.py` |
| Export QC / review sheet / release receipt | `scripts/qc.py`, `scripts/contact_sheet.py`, `scripts/receipt.py` |
| Animated graphic styles, approval gates, Gemini review, faceless | `engine/` (see `engine.md`) |
Minimum install: Python 3.10+, FFmpeg (with libass), `pip install numpy "opencv-python<5" requests faster-whisper` (OpenCV 5 removed the Haar face detector `reframe.py` falls back to). Engine additionally needs Node 22+ and Chrome.

## Optional extras (use if installed on the machine; never required)
| Need | Skill |
|---|---|
| Vertical reel with animated cards, dark style | `albert-reel`, `famous-reel-editor` |
| White popout style / screen-share tutorial | `albert-reel-white`, `albert-reel-white-screen` |
| 16:9 YouTube edit | `famous-youtube-editor`; long-form with sub-agents `youtube-clean` |
| Arabic creator reel, clean → elements with approval gates, faceless | `community-reels` (`community-clean`, `community-elements`, `community-eye`, `community-decode`) — the same engine is bundled in `engine/` |
| Edit already in CapCut | `capcut-smartcut` |
| Long YouTube → ranked shorts | `youtube-clipper` |
| Captioned edit from a spec, lint/verify gates | `open-edit` |
| AI B-roll / popup graphics | `youtube-broll-maker`, `youtube-popup-graphic`, `higgsfield-generate` |
| Thumbnails | `famous-thumbnail`, `youtube-thumbnail-maker` |
| AI rough cut from footage, multi-format resize | Adobe `adobe-edit-quick-cut`, `adobe-resize-photos-and-videos` |
| Finding/checking fonts (Arabic support) | `adobe-fonts` |
When delegating to an extra, pass: the intake answers (logo, colours, font), the client entry, the caption system, SFX/music toggle, hook device and CTA. Their own default colours/fonts/SFX must be overridden by these. Never let a sibling skill re-grade footage.
