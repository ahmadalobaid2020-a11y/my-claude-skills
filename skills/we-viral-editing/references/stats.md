# Stats from the study (2026-09-25)

**Corpus:** 1,088 finished renders analysed from the agency's delivered-work archive (all `Render`/`Renders`/`Done`/`Ready`/`Export` folders across client project folders, excluding Not Subtitled, Not Stabilized, Unedited, For the Editor, Topaz intermediates and raw footage). 3 files failed to decode. About 75 clients.
**Method:** each video was run through ffprobe for its specs, ffmpeg scene detection (threshold 0.28) for cuts per minute, and EBU R128 for loudness, then reviewed on a 12-frame contact sheet (hook frames at 0.1, 1.0 and 2.5 s, the body, and the last 1.2 s). The drive also held 237 SRT files, 166 Premiere projects parsed for effects, and the script docs.

## Format
- Vertical 9:16: **96%**. 1080x1920: 960 files; 2160x3840: 25; 1920x1080: 24; 3072x1024 (anamorphic film): 6; 1080x1350 (4:5 ads): 5.
- Off-spec mistakes: 608x1080 (14), 720x1280 (14), 1080x1934 (12), 608x1088 (5), 2160x3838 (5).
- Frame rate: 30 fps (553), 25 (391), 60 (83), 24 (33), 50 (24).
- Codec: H.264 (1,072). Alpha .mov assets: qtrle (11), ProRes (2). Audio at 48 kHz: 94%.
- Bitrate deciles (Mbps): 5.0 / 7.3 / 11.3 / 15.3 / 16.3 / 17.2 / 18.0 / 19.9 / 22.0.

## Duration (seconds, deciles)
15 / 20 / 26 / 32 / 37 / 44 / 51 / 58 / 73. **Median about 37 s.** Most pieces run 15–75 s. Exceptions: brand films (4 min), long-form 16:9 (3.5 min) and street trivia (2.5 min).

## Pace (cuts per minute, deciles)
0 / 1.8 / 5.0 / 8.6 / 11.9 / 15.8 / 20.0 / 24.0 / 30.8.
- Single-take talks: 0–5 (graphics carry the pace).
- Talking head with jump cuts and B-roll: 10–20.
- Real-estate tours: 13–25.
- Food, process and event montages: 22–45.
- Real estate / construction speed-ramps: 30–45.

## Loudness (integrated LUFS, deciles)
−23.1 / −20.6 / −18.6 / −16.1 / −15.3 / −14.1 / −13.6 / −12.9 / −12.1. **Median −15.3.** True peak median is about 0 dBTP, so many renders touch or exceed 0. Hence the house target: **−14 LUFS / −1 dBTP**. 20 deliberately silent exports (no-music versions, showcase posts, alpha assets).

## Captions (237 SRT, 9,428 cues)
Cue length p10 / p50 / p90 = 0.57 / 1.2 / 1.95 s. Words per cue: 1 / 3 / 5. Characters: 7 / 16 / 24. Lines: always 1.

## Per client (n, median duration, median cuts/min, median LUFS)
Client names are anonymised below (niche + letter); the numbers are exactly as measured.

| Client (niche) | n | dur | cuts/min | LUFS |
|---|---|---|---|---|
| App/consumer-product client A | 123 | 35 | 8.2 | −13.0 |
| Real-estate client A | 112 | 51 | 15.1 | −19.9 |
| Restaurant client A | 72 | 24 | 15.1 | −14.6 |
| Coach/creator client A | 70 | 56 | 4.1 | −13.7 |
| We Viral (own) | 38 | 15 | 0 | −15.9 |
| Restaurant client B | 37 | 32 | 19.7 | −15.6 |
| Study-abroad client A | 28 | 18 | 8.2 | −14.6 |
| SaaS client A | 28 | 48 | 20.2 | −23.0 |
| Coach/creator client B | 26 | 37 | 1.4 | −15.0 |
| Coach/creator client C | 25 | 46 | 7.1 | −21.2 |
| Real-estate client B | 25 | 56 | 31.5 | −13.0 |
| Travel client A | 25 | 39 | 22.4 | −12.8 |
| Clinic client A | 21 | 26 | 9.2 | −14.3 |
| Real-estate client C | 19 | 67 | 13.1 | −18.6 |
| Clinic client B | 18 | 37 | 22.6 | −17.3 |
| Fashion/brand-film client A | 18 | 27 | 20.9 | −15.8 |
| Clinic client C | 18 | 33 | 21.6 | −13.5 |
| Restaurant client C | 17 | 17 | 22.4 | −9.3 |
| Clinic client D | 15 | 39 | 10.2 | −15.4 |
| Clinic client E | 15 | 52 | 15.0 | −19.1 |
| Coach/creator client D | 15 | 21 | 11.2 | −13.1 |
| Clinic client F | 14 | 35 | 13.8 | −18.9 |
| Restaurant client D | 14 | 19 | 27.3 | −20.4 |
| Clinic client G | 13 | 26 | 25.2 | −20.7 |
| Coach/creator client E | 13 | 45 | 9.4 | −15.6 |
| Clinic client H | 13 | 37 | 1.6 | −16.7 |
| Coach/creator client F | 13 | 33 | 8.8 | −15.1 |

The full table (all ~75 clients) came from the analysis run; the rest have n ≤ 12.
