# QC and self-review

`scripts/qc.py` covers the file spec. This covers everything a script can't see, plus the gates to run before showing anything to the client.

## Layered gates (cheap → expensive)
1. **Lint the plan** before render: every card/caption anchor asserted against the transcript (`EXPECT={idx:"word"}` block at the top of the generator; compare case-insensitively with trailing punctuation stripped). Use `find_after(word, t)` when a trigger word repeats.
2. **Bounds / safe zones** on the timeline (no video needed). Triage every violation: CHROME (credit/kicker — ignore) · TRANSIENT (crosses the margin on entry/exit — ship, mention) · MINOR (small bleed — ship, suggest fix) · MAJOR (blocks delivery — move it).
3. **Contrast**: measure text against the actual footage behind it; add a shadow/capsule only where it measurably fixes legibility.
4. **Render**, then `python scripts/qc.py out.mp4` (size, fps, codec, loudness, true peak, faststart, A/V drift).
5. **Look at it**: `python scripts/contact_sheet.py out.mp4` plus frames at: first frame, every join, every graphic entrance/exit, the CTA, the last word. Actually read the sheet.

## Self-eval checklist (before showing any cut)
- First and last word not clipped (hear them).
- Caption text == spoken word at 3–4 sample points — compare with what was *said*, not the script.
- Captions never cross the face; readable over every B-roll.
- Numbers on screen match the numbers spoken.
- No empty card > 1 s, no one-frame flash of a wrong frame at transitions, no strobe.
- No double zoom (your punch-in fighting a screen recorder's baked-in auto-zoom).
- Logo, brand colours and font are the ones from the intake (see `intake.md`).
- A/V drift < 1 frame (compare stream durations; for sync-critical builds run a ±6-frame shift search).
- If audio was re-muxed after a graphics render, the decoded audio must match the approved clean master (hash or null-diff). Mismatch = broken render.
- AI B-roll matches what's being said and the identity/wardrobe doesn't drift mid-clip; contradictory B-roll is worse than none.
- Every SVG/logo renders visibly on the background it sits on (`currentColor` → solid black; broken viewBox → invisible). Bake explicit fills.
- Popout/cutout seam: the hair continues across the frame edge with no duplication.
- Feed-size check: view the cover and first frame at ~200 px wide. Still readable?

## Pairwise, not absolute
Self-scoring "is this good?" is unreliable. When iterating, render the new version and compare it head-to-head with the previous one at the same timestamps (hook, a busy graphic beat, the CTA); keep the iteration only if it's visibly better. Cap at 3 rounds, then show the user. [SeeCut]

## Release receipt
For the final deliverable record: file name, SHA-256, duration, qc.py result, and a cover thumbnail, in the project folder. It proves which render is final when versions pile up. [kinocut]

## Honesty rules
- Say what was checked and how: "frame-sampled + signal-checked", never "I watched/listened to it".
- A sub-agent's "done" is not evidence. Re-probe the file, read a contact sheet, check first/last frames and sync yourself.
- LLM/vision QC findings (Gemini etc.) are hypotheses. Replay that exact timestamp before acting. A failed review call = incomplete review, not a pass.
- Expected false positives: natural pauses on a quiet mic tripping a "silence" detector; your own recreated on-screen text tripping a "document visible" check. Confirm once, move on.

## Known render failure modes
| Symptom | Cause | Fix |
|---|---|---|
| A/V desync growing after ~40 s | `concat -c copy` of AAC segments | concat filter, single encode |
| ~2 s drift mid-file | mixed colour range / timescale segments | normalise before concat |
| Dropped frames in Chrome/HyperFrames overlay | opaque frames as RGB, translucent as RGBA → ffmpeg re-inits filtergraph | force every PNG layer RGBA (1 px transparent column); check `nb_read_frames` |
| Dropped frames with lead-in | `tpad` + offset overlay | bake the lead-in as a real still clip |
| RTL elements at negative x in renders | Chrome RTL layout | `html,body{direction:ltr}` + `body *{direction:rtl}` |
| Segment silent | `afade` after output-side `-ss` | input-side seek |
| Mix clips to 0 dB | `alimiter` default auto-level | `alimiter=limit=0.891:level=false` |
| Won't open in QuickTime/IG | moov atom at end | `-movflags +faststart` |
| "FFmpeg not found" in hyperframes | PATH | add ffmpeg dir to PATH |
| `-filter_complex_script` error | removed in new ffmpeg | `-/filter_complex file.txt` |
| `npx hyperframes` ETARGET | transient npm 404 | run cached copy from `~/.npm/_npx` |
| GSAP punch-in does nothing | transform on `<video>` | transform a wrapping `<div>` |
| Disk filled during parallel renders | raw frame dumps | stream through pipes; keep only small JPGs; clean scratch |

## Adversarial second pass
For hero pieces and long-form, run a separate reviewer (fresh agent or `community-eye`) whose only job is to find faults at exact timestamps. On one long-form video this caught ~20 real issues the editor missed.
