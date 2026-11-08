---
name: audio-cleanup
description: Clean voice recordings and video audio - remove rumble, hiss and background noise, soften harsh "s" sounds, even out the level and normalise loudness for YouTube, podcasts or broadcast. Use for "نظف الصوت", "ضوضاء", "الصوت واطي", "audio cleanup", "normalize", "denoise".
---

# audio-cleanup

Script: `bash ~/.claude/skills/audio-cleanup/scripts/cleanup.sh INPUT [OUTPUT] [options]`

Chain: high-pass 80 Hz → FFT denoise → de-esser → gentle compressor → exact gain to target → limiter at −1.5 dBFS.
Video files keep their picture untouched (stream copy); only the audio is re-encoded.

| Option | Use |
| --- | --- |
| `--target -14` | LUFS. `-14` YouTube/TikTok/Instagram (default), `-16` podcasts, `-23` broadcast |
| `--denoise 12` | Noise reduction in dB. 6–10 light, 12 default, 18–25 noisy room (more = more artefacts) |
| `--no-denoise` | Level/loudness only, for already clean audio or music |
| OUTPUT | Default `NAME.clean.EXT`; `.wav`, `.mp3`, `.m4a` or a video extension |

The script prints loudness before and after; expect the result within about 1 LU of the target.

## Workflow

1. Run with defaults. For music-only tracks use `--no-denoise`: the denoiser is tuned for speech.
2. Listen-check by measurement, since you cannot hear it: compare before/after loudness, and on request extract 10 s of each (`ffmpeg -ss 30 -t 10 -i FILE out.wav`) for the user to compare. If the user says it sounds "underwater" or robotic, lower `--denoise`.
3. This fixes level and steady noise (fans, hum, hiss). It cannot remove echo, music under speech, or overlapping voices; say so instead of over-processing.
