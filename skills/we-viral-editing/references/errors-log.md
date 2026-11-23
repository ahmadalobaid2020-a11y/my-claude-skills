# Errors not to repeat (living log)

This file is how the skill gets better every job. After every delivery:

1. Write a short retro: what went well, what went wrong. No self-praise — the useful part is the error.
2. Any mistake that could happen again becomes a row below (and, if it's a script bug, a fix in `scripts/`).
3. A new client preference goes into `client-bible.md` under that client, not here.
4. Archive a finished project's generator/EDL into the project folder so the next job starts from a proven reference.

Goal: every piece of feedback is given only once.

| # | Mistake | Rule that prevents it | Source |
|---|---|---|---|
| 1 | Picked an earlier, "cleaner" take of a repeated line | Always the LAST complete take, kept whole; cut only between takes | client job |
| 2 | Re-graded footage that arrived graded | Never colour-grade; exposure/WB fixes and shot matching only | house |
| 3 | Whooshes and pops on a voice-only client's reels | Some talk-only clients want voice only; SFX/music is a per-client toggle — ask | client job |
| 4 | Wrote a retired program/community name in a client's video | Never write a name the client has retired; check the client entry for renamed terms | client job |
| 5 | Silence threshold −30 dB clipped word endings | −40 dB default, −35 fallback, never −30/−32 | albert/famous |
| 6 | A/V drift after ~40 s | concat filter, never copy-concat AAC segments | albert/famous |
| 7 | Verified against a stale cached transcript | Delete cached JSON after every re-cut | famous |
| 8 | Transcript said "output" but audio had only "out" | Verify clipped words on the audio (word end vs duration) | famous |
| 9 | Music at 15% buried the voice | Music ≈ 6% linear / −20…−24 dB under speech, duck on voice | albert |
| 10 | Card empty for 2–3 s waiting for its trigger word | Anchor the key visual to an early word; ≤ 1 s empty | albert |
| 11 | Stamp graphic covered table values | Place stamps beside the panel, never over data | famous-youtube |
| 12 | Zoom 2.2× on screen share "too much" | 1.2–1.4× normal, 1.6× ceiling, one push per stretch | youtube-clean |
| 13 | Parallel agents filled the disk with frame dumps | Stream via pipes; keep JPGs only; clean scratch | youtube-clean |
| 14 | Dropped frames in Chrome-rendered overlays | Force RGBA PNG layers; check frame count | client job |
| 15 | Used a guessed brand colour/font | Run the intake questions before editing | user request 2026-09-29 |
