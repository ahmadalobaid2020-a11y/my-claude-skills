# Motion graphics and on-screen design craft

`house-style.md` lists *what* We Viral puts on screen. This file is *how to make it look expensive*. Distilled from albert-reel(-white/-screen), famous-reel/youtube-editor, youtube-clean, open-edit, community-reels-engine, and the design skills (taste-skill, high-end-visual-design, apple-design, emil-design-eng, impeccable, figma motion, animation-vocabulary, review-animations).

## 1. Card doctrine
- **Cards carry the visual, captions carry the words.** Logo, icon, number, graph, one word. No sub-lines, eyebrow+title+chip stacks or explanations. If a card needs a sentence, redesign it.
- **3 things max** on a graphics stage at once (subject/window, label, number, caption each count). A 4th → cut one or split across time. Count on a rendered frame.
- **One idea per frame**; two ideas = two sequential frames. Never say on screen what the caption already says.
- Every graphic has a job: hierarchy, state change, feedback, or sequence. "Looks cool" is not a job.
- **Anchor to an early word**: the card's key visual lands on the beat's first word (or +0.2 s), never the last. ≤ 1 s of empty card, ever. Exception: a CTA's literal trigger ("اكتب كلمة…") anchors late — fill the beat's front with secondary visuals at ~35% opacity.
- Cards are contiguous in graphics-led formats (one always on screen); in talking-head formats the face gets full frame between graphics.
- A static card reads as a slide: make hero cards 2–4 stages (entrance → development → payoff) on different words, finished before the beat's last word. E.g. hook = claim + on-screen proof (punch 2.2–2.6× on the receipt); "two things merge" = orbit → snap (touching) → burst.
- Before → after: show the "before" from t=0, scale-punch on its word, then swap sequentially (old exits ~0.16 s before new pops) — not a crossfade.
- Numbers: count-up 500–900 ms; if the beat is < 1.2 s, just pop the final number. A lone static stat reads sterile — draw a curve/area and pop the number at its peak.
- Recurring devices (sticker, badge, arrow) need a consistent trigger rule ("every price", "every named doctor") or they don't recur; vary position/scale each time.
- Stamps/badges sit beside panels, never over data.
- No expanding shockwave rings for impact; no per-word pulsing on cards.

## 2. Layout modes (choose per sentence, hold 6–15 s)
Vertical 9:16:
- **Face full frame** + captions (direct address, hook, CTA).
- **Split**: graphics top band (0–864) + face bottom ~55%; or speaker top half (1920×1080 source scaled to 1707×960, cropped) + graphics/B-roll bottom on brand BG (a common split format for talk-only creator clients).
- **Face shrinks** into a rounded card while an explanatory graphic plays, then releases back to full frame. The face is never fully covered.
- **Popout**: speaker in a floating rounded card (radius ~36) on white/brand BG with a mandatory soft drop-shadow (alpha ~90, blur ~22), head segmented (rembg/RVM) and composited 100–200 px above the frame edge. Order: BG cards → shadow → rounded video → head cutout → captions.
Landscape 16:9 (long-form):
- **A** full cam (hook, direct address, CTA — always the opener and closer) · **B** full graphic (concepts, lists, numbers) · **C** cam PiP ~480 px bottom-right over a graphic/screen · **D** full B-roll. Something new every ~5 s, never one mode > 10 s, never two B-rolls back-to-back, mode changes on word boundaries. Write the plan as JSON `{start,end,mode,what}` and show a one-line summary before rendering.
- 16:9 cards use wide/multi-column layouts (a centred narrow column looks like a cropped reel). Optional "app window" frame (title bar + panel) for UI-style explainers.
- Position changes between modes ease (~0.35 s), never hard-jump.

## 3. Screen recordings
- Crop OS/browser chrome and pillarbox bars (`cropdetect`) first; output fixed size.
- Show the screen only while the voice narrates on-screen action; word-anchored windows `[first word − 0.05, next non-demo word]`. Cut silent demo stretches.
- Extract each window through the full EDL chain (a separately-cut companion drifts ~0.4 s over 14 segments).
- Zoom: default none. Punch only when unreadable at 1×: fast cosine punch (~0.35 s) after ~0.5 s full view, hold ≥ 4 s with faint drift. 1.2–1.4× normal, 1.6× ceiling for general screens; up to 1.6–1.9× only for tiny UI (a button) when the client likes punchy. One push per stretch. Left-aligned content → focus x≈0; headers → y≈0. Never chase the cursor, never zoom while the recorder's own zoom animates. An accent ring on the value often beats zooming.
- No text overlaid on live screen footage; point with the ring/zoom only.
- Auto-check every window frame for blank/low detail before compositing.

## 4. Typography on screen
- Hierarchy = weight + size + leading together; the key word 1.5–3× bigger or 2 weights heavier, not a 4 px bump.
- Tracking by size: big titles/numbers −2…−4%; small labels +2…+5%. **Never negative tracking on Arabic** (breaks joins).
- Leading 1.0–1.1 on display, 1.3–1.5 on multi-line blocks; +10% when descenders/diacritics are present.
- Arabic reads smaller than Latin at the same px: size Arabic +10–15% when paired. Keep numerals LTR inside RTL runs; isolate Latin names with `<bdi>`.
- Emphasis = the brand accent or a weight jump in the same family. No random serif word in a sans line. Serif only for luxury real estate / heritage clinic / premium coach, and then commit.
- Max 2 families on screen (display + caption, or display + one mono for data).
- Treat each line of a stacked hook as its own block (own indent, own size) — not a left-aligned paragraph.

## 5. Colour and material (premium vs cheap)
Premium:
- One accent, used identically on every card, pill, number and end card. Numbers are the one place saturation can run high.
- Diffuse, low-opacity (< 10%), tinted shadows; bigger surfaces get deeper shadows.
- Glass only for 1–2 hero moments (title, end card, featured stat), with a 1 px inner top highlight (~10–15% white) + backdrop blur.
- Nested "double-bezel" cards (outer tinted shell + hairline + inner core) for hero cards.
- 2–4% grain on title/end cards.
- Card contrast holds on the brightest and darkest frame of the shot (dark card over daylight ≥ 60–70% fill).
- One radius family per client (8–12 px clinic/SaaS; soft/pill for lifestyle/coach), locked for the whole edit.
- Flat brand panels, one big tight headline, grey→white word fill synced to speech, fade + lift + de-blur entrances, split-screen proof (panel slides in, face stays) instead of full takeovers.
Cheap (avoid):
- Flat rectangle + harsh black drop shadow; grey 1 px border; glass on everything; mixed radii.
- "AI purple" glow gradients, neon glow stacked on grids, bordered boxes everywhere, a pop SFX on every element.
- Text on footage with no scrim, stroke or shadow.
- Same card template 6+ times in a row with no rhythm change; 3 items in a 4-cell grid.

## 6. Motion values
- Enter: ease-out `cubic-bezier(0.23,1,0.32,1)` (GSAP `power3.out`/`expo.out`) or critically-damped spring (response 0.3–0.4 s). Move/morph on screen: `cubic-bezier(0.77,0,0.175,1)`. Loops/tickers: linear. Never ease-in or plain `ease` on an entrance.
- Durations: micro pop 150–250 ms · card/lower-third 350–550 ms · title/hook 400–700 ms · count-up 500–900 ms. Stay under ~900 ms except transitions/montage wipes.
- Exit faster than entry (150–200 ms), in the same spatial direction the element came from.
- Start from scale 0.92–0.97 + opacity 0, never scale(0).
- Stagger children 30–90 ms.
- Scale from the anchor (the word, number or shoulder it belongs to), not the centre.
- Bounce/overshoot only for momentum moments (a number slamming on a beat, 3D emoji pop). Default is no bounce.
- Awkward crossfade → 2–4 px blur for < 200 ms during the swap.
- Animate transform and opacity only (render cost, dropped frames).

## 7. Style vocabularies (for new clients without a look)
Swap tokens, keep structure: **Editorial** (warm paper, framed footage, blue labels — explainers) · **Signal** (dark BG, one lime/brand accent, crisp entries — single strong beat) · **Diagram** (pale teal, numbered nodes — steps/process) · **Pulse** (dark grid, node tiles, a signal travelling the links — faceless process) · **VOX** (paper desk, footage as a taped tilted polaroid switching sides, red arrows, highlighter on the active caption) · **White popout** (white BG, dark text, one accent, floating rounded speaker card with head popout). Recommend one per sentence based on what it does (compare / connect / demonstrate / list / count / invite), not a menu.

## 8. Critique before calling graphics done
1. What draws the eye first — is it the right thing? 2. One accent, no drift. 3. Contrast holds on the worst frame. 4. One radius and card construction system. 5. No flat black shadows. 6. Every entrance has a faster, same-direction exit. 7. Nothing from scale(0), nothing ease-in. 8. Reveals staggered. 9. Hierarchy obvious at a glance. 10. Arabic and Latin optically balanced. 11. Every motion has a job. 12. ≤ 3–4 elements per screen. 13. Rhythm varies across the video. 14. Logo, colours and font match the intake.
Severity for brand issues: 🔴 contradicts brand (wrong logo/colour/font, misspelled name) → fix before delivery · 🟡 inconsistent → fix if cheap · 🟢 minor style → mention.
