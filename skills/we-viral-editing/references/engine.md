# Bundled engine: animated graphics, Gemini review, faceless reels

`engine/` is a bundled copy of the Community Reels Engine (CC0 — free to use, change, share or sell; third-party parts keep their own licences, see `engine/THIRD-PARTY-NOTICES.md`). Use it for **HTML/GSAP motion-graphic styles, the hash-locked clean → approve → dress → render flow, Gemini whole-video understanding/review, and faceless reels**. For simple jobs (cut + captions + audio) the `scripts/` toolkit is enough.

## Setup (once per machine)
Needs Node 22+, Python 3.9+, FFmpeg, Chrome. Run inside `engine/`:
```
npm ci
python reel.py doctor
python reel.py demo        # 5 styles from synthetic media, no API cost
```
Gemini (optional, for analyze/decode/review): `python reel.py setup-key` (hidden prompt; saved locally in engine/.env — never commit or share that file).

## Recorded video flow
1. `python reel.py prepare <video> --name <project>` — copy, hash, proxy, waveform, HDR→SDR.
2. `python reel.py analyze <project> --allow-upload --budget-usd 1` (Gemini; uploads the video, so ask first) — proposed keeper spans, uncertain words, visual opportunities. Treat times as proposals; confirm against the waveform and `scripts/verify_cut.py`.
3. Build the keep-list (house rules: last complete take, whole; see `cutting.md`) → `python reel.py clean <project>`.
4. Show the clean cut → `python reel.py approve <project> --by "<name>"` records the person's approval (hash-locked; any later change to the cut invalidates it).
5. `python reel.py dress <project> --style editorial|signal|diagram|pulse|vox [--workers 2]` — captions + motion beats on the clean timeline. Override the style's colours/fonts with the intake answers (`intake.md`).
6. `python reel.py render <project>` — renders, restores the approved audio and verifies it bit-for-bit.
7. `python reel.py review <project> --allow-upload` (Gemini) — findings are hypotheses; replay each timestamp before acting.

## Other commands
- `prepare` the reference, then `decode <project> --allow-upload` — explain a reference reel's technique (hook, captions, rhythm, motion) for an original adaptation; never copy branded assets or wording.
- `story` then `dress/render --faceless` — faceless reel from approved narration or intentional silence (`engine/docs/faceless.md`).

## Details
`engine/docs/workflow.md`, `styles.md` (the five visual systems), `troubleshooting.md`, `verification.md`, `ASSISTANT-PLAYBOOK.md` (beginner-guided mode), `MANUAL-AR.html` (Arabic manual).
