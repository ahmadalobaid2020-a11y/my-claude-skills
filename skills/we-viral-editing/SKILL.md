---
name: we-viral-editing
description: The We Viral master video-editing playbook — house style distilled from 1,088 finished agency videos, plus the best craft from editing/design skills and open-source editing projects (cutting, captions, motion design, clipping, auto-reframe, audio, QC, multi-agent long-form). Use whenever you edit, cut, caption, animate, clip, reformat, script, QC or review any video for clients across niches (clinics, restaurants, real estate, study-abroad, coaches, SaaS, and more). Always first asks, in the chat's language, about logo, brand colours and font. Triggers: "edit this", "we viral style", "house style", "make a reel for <client>", "caption this", "cut this video", "turn this into shorts", "resize for YouTube", "plan the edit", "check this export", and any Arabic, Turkish or English short- or long-form video work.
---

# We Viral editing playbook

We Viral is an agency making vertical short-form video for Arab, Turkish and Gulf businesses. Follow this so every edit looks like the same senior team made it.

**Load references only when the step needs them** (keeps context lean):

| Step | Read |
|---|---|
| Before editing (always) | `references/intake.md` |
| Client colours, logo, end card, languages | `references/client-bible.md` |
| Picking a format / beat sheet for a niche | `references/formats.md` |
| Hook lines, script→visual cues, CTAs | `references/scripts-hooks-ctas.md` |
| Speech cut, takes, silence, sync | `references/cutting.md` |
| Captions timing, placement, Arabic/RTL | `references/captions.md` + caption systems in `references/house-style.md` |
| Graphics, layouts, typography, easing, premium look | `references/motion-design.md` + vocabulary in `references/house-style.md` |
| B-roll, AI generation, covers, thumbnails | `references/broll-thumbnails.md` |
| Render stack, audio mix, reformatting, which sibling skill to use | `references/engineering.md` |
| Animated graphic styles, approval-gated flow, Gemini review, faceless reels (bundled engine) | `references/engine.md` |
| Long recording → shorts (clip scoring), scene detection, 16:9→9:16 auto-reframe | `references/clipping-reframe.md` |
| Folders, naming, deliverable set | `references/pipeline.md` |
| QC and self-review | `references/qc-review.md` |
| Long-form, batches, notes rounds, sub-agents | `references/orchestration.md` |
| After delivery | `references/errors-log.md` |
| Drive statistics behind the rules | `references/stats.md` |
| Where every technique came from (skills, GitHub repos, licences) | `references/sources.md` |

## Step 0 — Intake (mandatory, before any editing)

Ask these three questions **in the language the person is chatting in**, numbered, in one message (full templates for Arabic, Turkish and English are in `intake.md`):

1. Do you want me to use a logo in the video? If yes, please upload it.
2. Do you have brand colours? If yes, please provide them.
3. Do you have a specific font you want me to use? If yes, please provide it.

Don't re-ask anything already answered in the chat. For known clients, show what's on file and ask them to confirm. Accept any form of answer (file, link, screenshot, words). A "no" or skip → house defaults, stated in one line. The speech cut may start while you wait; styling may not.

## The 12 house rules

1. **9:16, 1080x1920, H.264 yuv420p, AAC 48 kHz, +faststart.** 4K only when the source is 4K and the client wants it. Never 608x1080, 720x1280, 1080x1934 or rotated renders.
2. **Hook in the first frame** (see hook devices). Never open on a logo, a slow establishing shot or a greeting without text.
3. **Captions on everything with speech**: one line, 2–4 words (median 3), ~1.2 s per cue, ~62–72% down the frame, never over the face, key word in the brand colour.
4. **The brand colour (from the intake) drives** key words, pills, highlight boxes, prices and the end card. One accent, no drift.
5. **Something changes every 2–4 s**: kinetic words, icon pops, B-roll, 110–115% punch-ins on alternate jump cuts. Median ~12 cuts/min; food/process montages 25–45.
6. **Illustrate the words**: every showable noun, number or claim gets a visual. Cards carry visuals; captions carry words. Max 3 things on screen.
7. **Numbers are hero graphics**: big, brand or money-green, counting up.
8. **One clear CTA on screen** (phone/WhatsApp pill, comment keyword, "للتفاصيل تواصلوا معنا", link in bio, "click the button below").
9. **Close on a branded card** (logo + phone/handle/badges, 1.5–2.5 s, fade to black). Talk-only pieces end on the presenter with the phone pill.
10. **Never colour-grade.** Footage arrives graded. Exposure/WB fixes, shot matching and HDR→SDR conversion only. Tints are graphic devices.
11. **Audio: −14 LUFS integrated, −1 dBTP** for vertical short-form (16:9 YouTube long-form: −16 LUFS / −1.5 dBTP), two-pass normalisation. Clean the voice first; music ≈ −20…−24 dB under speech; SFX and music are a per-client toggle — some talk-only clients want voice only, ask.
12. **Versions organised**: `NN.v.mp4`, language suffixes (`ENG`, `TR`, `عربي`, `فارسي`), separate music/no-music and text/no-text masters.

Plus the craft rules everyone gets wrong: **last complete take wins, kept whole**; cut on the audio signal, not the transcript; re-transcribe and verify the final cut; concat filter, never copy-concat; every re-cut rebuilds everything derived from it.

## Hook devices (pick one; ranked by frequency)

| Device | What it looks like | Typical niches |
|---|---|---|
| Text-hook title | Bold 1–2 line question/claim at the top, often held all video | real estate, restaurants, talk-only creators |
| Darkened freeze hook frame | First 0.3–0.6 s freeze under a navy→purple gradient, 2-line white question; doubles as cover | real estate |
| Walk-in / door entry | Presenter walks in, whip or motion blur on the first cut | clinics, driving schools |
| Freeze + sticker cutout | Game rule title, participants cut out with thick white outline, radial zoom-blur | restaurants, games/challenges |
| Defocus-in | First frame blurred/zoomed, snaps sharp | clinics, SaaS |
| Drone → blue map mode | Aerial tints blue, plot outline glows, area number pops | real estate developers |
| Prop / trend hijack | Mask, money throw, stopwatch, product to lens | pet products, kids' products |
| Challenge / budget | "معي 2000 ليرة…", "5000 ليرة إذا جاوبت صح" | restaurants, games/challenges |
| Kinetic price / % counter | Big translucent number counting up behind the head | driving schools, SaaS |
| Pixelated reveal | Product mosaic until "واليوم رسمياً…" | restaurants |
| Claim + proof punch | Claim line, then a hard punch (2.2–2.6×) onto the receipt/screenshot/number | coaches, SaaS |

## Formats by niche (beat sheets in `formats.md`)
Real estate: drone → blue map mode, interior walk, glowing price, QR/licence end card · Clinics: doctor to camera, brand pills, 3D icons, before/after, WhatsApp + flags end card, language versions · Restaurants: ASMR process montage or presenter challenge, hero bite, price starbursts · Study abroad: bilingual captions, flags, fees, objection-led · Coaches: kinetic words, memes/split screen, circled proof, comment-keyword CTA · SaaS: glass UI cards, counting stats, free-trial CTA · Brand films/events: music, drone, fast montage, logo, 16:9 + BTS · Seasonal: 5–15 s templated greeting, AR + TR · A03 own ads: navy rings, 2x2 reel grid, package price cards · YouTube long-form: A/B/C/D shot modes (`motion-design.md` §2).

## Workflow

0. **Intake** — the three questions above; read the client entry.
1. **Brief** — niche, format, hook device, caption system, CTA, SFX/music toggle, deliverable set (sizes, languages).
2. **Script → visual cues** — one visual cue per line (`scripts-hooks-ctas.md`); lock hook and CTA.
3. **Speech cut** — transcribe, last-take EDL, signal-based cut points, re-transcribe and triple-check (`cutting.md`). For long pieces get the clean cut approved before graphics (`orchestration.md`).
4. **Preview frame** — one caption frame + end card with the intake branding → "Match?"
5. **Graphics pass** — hook, captions, illustrations, numbers, B-roll, transitions (`motion-design.md`, `captions.md`, `broll-thumbnails.md`).
6. **Audio pass** — clean voice, bed, SFX if on, limiter, −14 LUFS (`engineering.md`).
7. **Close** — CTA on screen, branded end card, fade to black.
8. **Export & QC** — `python scripts/qc.py <file>` on every deliverable; contact sheet; self-eval checklist (`qc-review.md`). State honestly what was checked.
9. **Variants** — languages, music/no-music, text/no-text, other aspect ratios (reframe with face focus, re-place text).
10. **Retro** — add any repeatable mistake to `errors-log.md`; save confirmed brand values to `client-bible.md`.

## Tools (bundled — the skill works on its own)
- `scripts/transcribe.py` → `silence_edl.py` → `cutjoin.py` → `verify_cut.py` — the speech cut.
- `scripts/captions.py` — captions in the house styles with the intake colour/font, Arabic-safe, optional burn-in.
- `scripts/mix_audio.py` — voice clean, music bed with ducking, two-pass loudness.
- `scripts/reframe.py` — 16:9 → 9:16 face-tracked reframe.
- `scripts/qc.py`, `scripts/contact_sheet.py`, `scripts/receipt.py` — export check, review sheet, release receipt.
- `engine/` — animated graphic styles, approval gates, Gemini review, faceless reels (`references/engine.md`).
Setup and requirements: `references/engineering.md`.

## Working with other skills
Everything above is built in. If optional extra skills are installed (table in `engineering.md`) and one renders, this playbook still decides branding (from the intake), caption system, hook device, CTA, end card and SFX/music policy, and overrides that skill's own defaults. Never re-grade footage.
