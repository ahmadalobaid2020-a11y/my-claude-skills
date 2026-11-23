# B-roll, AI generation, covers and thumbnails

## When to use B-roll
- Vertical reel: 1–2 cutaways (AI or client-supplied), 2–4 s each, spaced apart, never back-to-back, never over the hook or the CTA. Pick **concrete, filmable** sentences only — not abstract claims or numbers (those become graphics).
- Long-form 16:9: about one per 15–20 s of runtime; also for scene-setting nouns ("open-source models" → datacenter shot).
- Client niche footage (drone, interiors, food process, clinic room) always beats AI. AI B-roll is for gaps.
- Give every B-roll shot exactly one **job**: Proof · Mechanism · Consequence · Action · Transition. No job → cut it.
- Hold times: AI stills ≤ ~3.5 s, real screenshots/documents 3–6 s; any single visual beat > 5 s gets split into 2–3 cuts (different crop, zoom or image).

## Generating (Higgsfield MCP, Seedance)
- Identity B-roll: upload the person's photo (`media_upload` → PUT → `media_confirm` type "image"), then `generate_video` with `medias:[{value:id, role:"image"}]` — role `image`, not `start_image` (start-frame interpolation gives stiff slide-like motion). No photo → text-to-video.
- Fire generation as soon as the shot plan is locked; build graphics while it runs (1–3 min). Wait with `jobs_wait`/`sync:true` or a ≥120 s wakeup — never busy-poll.
- Prompts: **short** (6–10 lines max); let a reference image carry the look. One subject/label per generation — multi-label shots come out garbled; generate separately and composite.
- Vertical over a dark band: `<scene/action>, dark moody environment, single accent light matching #<BRAND>, cinematic shallow depth of field, slow dolly move, 35mm texture, identity preserved`.
- Full-bleed / 16:9: same but `natural colour matching the footage, soft key light` instead of dark — B-roll must match the surrounding frame. (We never grade client footage; match the AI clip to it, not the other way.)
- Offer presets instead of raw prompts: shallow-DOF cinematic · handheld documentary · dark neon studio · warm golden-hour lifestyle · high-contrast B&W.
- Download the full 10 s, scrub a contact sheet, take the best-motion 2–6 s slice; check identity/wardrobe doesn't drift.
- Always tell the user the exact prompt + reference used so they can tweak.

## Compositing
- Top-band layouts: `scale=-2:864,crop=1080:864`, `enable='between(t,A,B)'`, and extend an opaque cover under the whole window to the next beat so the card underneath never flashes at the edges.
- Movie/stock clips: `cropdetect` and strip letterbox bars first.

## Covers (reel cover / first frame)
- The first frame is the cover: the hook text must be readable at frame 1 and at 200 px wide.
- House covers: the darkened freeze hook frame, text-hook title on brand pill, or the product hero. Keep text inside the 4:5 centre crop (the grid shows 4:5 of a 9:16 cover) — roughly y 420–1500.

## YouTube thumbnails
- Analyse the reference first: layout grid, face position, text word count and treatment, emotion, colour story, and *why it converts* (the curiosity gap). Steal the skeleton, never the text or identity.
- ≤ 4 words, uppercase, one focal point (face ≈ ⅓ frame height), 3 colours max (bg + subject + brand accent), strong contrast, nothing in the bottom-right (timestamp), ~5% margins.
- Highest-quality generation tier (text goes mushy otherwise); quote overlay text literally and keep it short.
- Check at ~200 px wide; spell-check every word (Arabic especially); check hands/eyes and accidental logos.
- Logo comparisons ("X + Y"): take logos from official brand/press pages; verify each file is a real non-empty image. Never invent the headline — confirm it.
- Skills that execute this: `famous-thumbnail`, `youtube-thumbnail-maker`, `higgsfield-youtube-thumbnail`.
