# Captions: timing, rendering, RTL

House caption *styles* are in `house-style.md` (pick one of the 8 per client). This is how to build them so they're exact.

## Timing
- Drive every caption from real per-word timestamps of the **final cut** (never an even split across a chunk).
- House default: one line, 2–4 words (median 3), ~1.2 s per cue, no overlapping intervals. Karaoke one-word style is an alternative for creator/coach reels.
- Cue-break algorithm (three independent triggers, first one wins): (a) cue duration would exceed ~1.2 s / word cap reached, (b) **inter-word gap ≥ ~250 ms** — break even if the word target isn't hit, so natural pauses read as pauses, (c) sentence punctuation / explicit break flag. Hard backstop: never more than 1 visible line (2 only for bilingual). [remotion template-tiktok `createTikTokStyleCaptions`, captacity]
- Caption animation vocabulary for briefs: **Highlight** (active word coloured/boxed) · **Underline** · **Bounce** · **Scale** (active word grows) · **Karaoke** (fill sweeps through the word, ASS `\kf`) · **Reveal** (words appear as spoken). Name one per client in `client-bible.md`. Market-known skins, handy when a client references them: **Hormozi** (heavy white caps, yellow/brand key word, box highlight), **MrBeast** (impact-style font, thick stroke, pop-in per word), Minimal, Neon (glow), Typewriter (character reveal).
- Optional client toggle: keyword → emoji pops (💸 money/price, 🔥 hot/trend, 🤖 AI, ✅ result, ⚠️ warning), max one per 3–4 s, never on the face.
- Word timing accuracy: WhisperX (wav2vec2 forced alignment) gives the tightest word boundaries but fails on digit/currency tokens and overlapping speech — another reason to normalise numbers before timing. stable-ts is a lighter alternative that suppresses timestamps in silence and can regroup cues by punctuation/gap/duration (useful to auto-fix flash words after splicing). Scribe stays the default.
- Lead the spoken word by ~0.13 s so text never lags the voice. Hard cut between chunks unless the style is word-by-word build.
- Zero-width words (`start == end`) after splicing make the neighbour flash — repair from neighbour timing (confirm the audio has no real gap first).
- Mega-words: Scribe can merge a phrase into one hyphenated token (> 14 chars, 2+ hyphens) — split with interpolated times for captions only; card anchors may keep the original.
- Numbers/money transcribe inconsistently ("$300" vs "three hundred dollars", "٥٠٠" vs "500" vs "خمسمية"). Normalise to one written form in the caption file; never assume word indices survive a re-transcription.
- Fix transcript typos in the caption file only; graphic triggers stay keyed to the original transcript.
- A caption crossing a cut: re-hear and re-split — never crop text by time fraction or invent a clipped phrase.
- Captions show what was **said**, not the marketing script.

## Placement
- House position: ~62–72% down (chest level), inside x 80–1000. Never across the face — measure the head box per beat; if space runs out: smaller size → re-break → other anchor → later window. Never cover the face.
- Platform-safe for 9:16: x 6–89%, y 11–83%; keep the right ~230 px clear of the like/share rail on long lines; nothing above y≈230 or below y≈1440 unless it's the end card.
- 16:9 long-form: no burned-in running captions by default (YouTube CC) unless the client asks; 6% inset for any text.
- During a hook title the running captions may pause (the hook title replaces them for that sentence), then resume.

## Rendering
- Sizes (1080 wide): one-word karaoke ~66–92 px; 2–4 word line ~56–72 px; step down one size for > ~60 characters or words > 14 characters; long words must never leave the frame.
- Legibility: soft shadow or pill/capsule, not a thin hard stroke. On white/light backgrounds flip to dark text (≈#141414) with a light halo. Any highlighter/underline animation needs a capsule behind the text.
- Burn with HTML/HyperFrames or PIL. Local ffmpeg often lacks libass, so don't rely on `subtitles=`.
- Emoji: use the OS colour-emoji font at native strike size; redraw rather than upscale anything > ~200 px.

## Arabic / RTL / Farsi
- Animate and highlight whole shaped words, never individual letters (breaks shaping). Kashida (تطويل) only for hook stacks/key words.
- Isolate Latin names and numbers with `<bdi>`; keep a Latin island on one line (wrapping it confuses layout checkers).
- Chrome renders translated RTL elements at negative x: `html,body{direction:ltr}` + `body *{direction:rtl}`.
- Confirm the font has Arabic glyphs (see `intake.md`), and give Arabic lines more leading than Latin.
- Bilingual: main language big, second language small beneath (or outlined pill). Each language version gets its own caption file and its own QC pass.
