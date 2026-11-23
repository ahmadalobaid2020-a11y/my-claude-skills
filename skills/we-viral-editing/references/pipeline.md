# Pipeline: folders, tools, versions, delivery

## Tools (from 340 .prproj and 435 .aep on the drive)
- **Premiere Pro** is the main editor. The most-used effects across 166 projects: Motion/Transform, Opacity, Text/Essential Graphics, Cross Dissolve, Constant Power (audio crossfade), Lumetri (matching only), Tint, Shape, Gaussian Blur (background blur, glass, censoring), Custom Fade, Mask, Drop Shadow, FilmImpact Impact Dissolve / Blur, Motion Blur, Mirror, Roughen Edges, Ultra Key, Warp Stabilizer, Directional Blur (whips), 4-Color Gradient (board backgrounds), Lens Distortion, Posterize Time, Mosaic (pixelated reveal), Track Matte Key, Mettle digital glitch. Audio: DeNoise, Parametric EQ, Hard Limiter, Vocal Enhancer, Single-band Compressor, Channel Volume.
- **After Effects** is used for hooks, map-mode real estate, kinetic typography, logo animations, seasonal templates and lower thirds. It lives in the client's "Ae Comps" folder and is dynamic-linked or rendered to .mov with alpha (qtrle/ProRes).
- **Essential Graphics / MOGRT library**: Fade Characters Separately/Together, Fade & Position Characters, Decode & Fade, Position & Rotate Characters (Bottom), Overshoot Scale, Ease Fade, 1-Line Fill Text Box, Generated Light Leak, Map – Digital, gadget interface icons, scribble elements, TikTok lower third, HUD titles, text-message and social UI packs, YouTube subscribe.
- **Captions** come from VEED auto-subtitles (`VEED-subtitles_<name>_ar-SA.srt`) or Premiere transcription, then are corrected by hand. Translated SRTs are kept alongside (`_english`, `_translated`, `tr`, `eng`, `فارسي`).
- **Adobe Podcast Enhance Speech v2** for voice (files tagged `-esv2-50p-bg-m-music-m`).
- **Topaz** for upscaling and stabilising (`_prob3`, `_stab`, `_chf3`, `_ahq12` suffixes = intermediates, never deliverables).
- **AI imagery and video** (Higgsfield and others) for scenario stills, B-roll and future-building renders.
- **Fonts** live in each client's `Font` folder. Logos live in `Logo`, brand books in `Brand`/`Branding`, and LUTs (rare, client-supplied) in `Lut`.

## Client folder standard
```
<Client>/
  Footage/            by shoot: "01 29-11-2025", "02 06-12-2025"
  Project/            .prproj (+ Auto-Save)
  Ae Comps/           .aep
  Library/            assets, music, sfx, templates, photos
  Music/  Logo/  Brand/  Font/  Photos/  Thumbnail/  Outro/  Script/  Subtitle(s)/
  Render(s)/
    Not Subtitled/    clean masters (no captions): keep for re-captioning and translation
    Not Stabilized/   pre-Topaz
    From the Editor/  freelance editor deliveries, to review and re-export
    Done | Ready | Subtitled/   final deliverables
  Invoice/  Proposal/
```

## Naming and versioning
- Deliverables are numbered by video: `01.mp4`, `<ClientName> 23.mp4`, `Video 300.mp4`. The number stays the same across revisions.
- Revisions: `01.1`, `01.2` … (or `01_1`, `01_2`). Several revisions per video are normal (one job went to .8).
- Suffixes describe variants: the language (`ENG`, `TR`, `Türkçe`, `عربي`, `فارسي`, `Ar`), `مع موسيقى` / `بدون موسيقى` / `No Music`, `مع كتابة`, `مع لوجو` / `No Logo`, `الرقم الجديد` (updated phone), `tl` / `usd`, `bio` / `comment` (CTA test), `Hook 03` (hook test), and the hook text itself in the filename.
- Use a separate subfolder for proxies and tests (`Test`, `Ai Before`). Never ship a proxy.

## Standard deliverable set per video
1. The main export, 1080x1920 H.264 at about 16–20 Mbps VBR (the drive's median is 16–18 Mbps), AAC 48 kHz stereo at 320 kbps.
2. The **Not Subtitled** master.
3. Where relevant: language versions, the no-music version (silent bed for in-app trending audio), with/without logo (white-label), CTA or hook A/B variants, and a 16:9 version for YouTube or Facebook.
4. For big productions: a BTS cut-down (4:5 + 9:16) for the agency page.

## Export spec (house)
| Field | Value |
|---|---|
| Resolution | 1080x1920 (4K 2160x3840 only if the source is 4K and requested); 1920x1080 for 16:9; 1080x1350 for 4:5 feed ads |
| Frame rate | Match the source: 30 (most common), 25, 60 or 50 for slow-mo / 60 fps sources, 24 for cinematic |
| Codec | H.264 High, yuv420p, +faststart |
| Bitrate | 16–20 Mbps (1080p), 40–60 Mbps (4K) |
| Audio | AAC 48 kHz stereo, 320 kbps |
| Loudness | −14 LUFS integrated (±1), true peak ≤ −1 dBTP |
| Alpha assets | QuickTime Animation (qtrle) or ProRes 4444 .mov |

## Known mistakes found on the drive (check for these every time)
- Proxy or low-resolution exports shipped: 608x1080, 608x1088, 720x1280, 480x860 (seen across several clinic and coach client jobs).
- Odd frame sizes: 1080x1934, 2160x3838, 1072x1920. Set the sequence to exactly 1080x1920.
- Footage exported rotated 90° inside a correct 1080x1920 frame (seen on a brand-film job). The rotation is baked into the picture, so qc.py can't see it. Always look at the contact sheet.
- Loudness too low (about 20% of renders are under −20 LUFS, some −25 to −34) or too hot (−7 to −9 LUFS with the true peak above 0 dBTP, so clipping).
- A silent render where speech was expected (only fine when it's the deliberate no-music export).
- Watermarked stock or template previews: always check the licence and the final frames.

Run `python scripts/qc.py <files>` to catch the technical ones automatically (size, fps, codec, bitrate, loudness, true peak, silence, rotation metadata). Then run `scripts/contact_sheet.py` and look at it to catch visual ones (rotated picture, captions over the face, missing end card, watermarks).
