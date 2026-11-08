---
name: subtitles
description: Make subtitles for a video or audio file - Arabic, English or any language - as SRT/VTT, translate them to English, or burn them onto the video. Runs locally with faster-whisper and ffmpeg. Use for "ترجمة للفيديو", "subtitles", "captions", "transcript", "SRT".
---

# subtitles

Script: `python3 ~/.claude/skills/subtitles/scripts/subtitles.py INPUT [options]`
Needs `faster-whisper` (`pip install --break-system-packages faster-whisper`) and ffmpeg.

| Option | Use |
| --- | --- |
| `--lang ar` | Spoken language; default `auto` detects it |
| `--translate` | English subtitles from any spoken language |
| `--model small` | `tiny`/`base` fast drafts; `medium`/`large-v3` best for Arabic and dialects |
| `--max-chars 42` | Line length; two lines per cue |
| `--burn` | Also writes `NAME.LANG.subtitled.mp4` with the subtitles rendered in |
| `--font`, `--size` | Burn-in style; the default DejaVu Sans renders Arabic |
| `--out DIR` | Output folder; default is next to the input |

Outputs: `NAME.LANG.srt` and `NAME.LANG.vtt`.

## Workflow

1. Confirm the file and what the user wants: a file, burned-in, or a translation.
2. Use `--model medium` (or `large-v3`) for Arabic unless the user wants speed; first run downloads the model from huggingface.co.
3. Run the script, then open the SRT and check a few cues: names, numbers and dialect words. Fix obvious errors in the SRT by hand, then burn if asked: rerunning re-transcribes, so for a corrected SRT burn it directly with
   `ffmpeg -i IN -vf "subtitles=FILE.srt:force_style='FontName=DejaVu Sans,FontSize=22,Outline=2'" -c:a copy OUT.mp4`.
4. For another target language (not English), translate the SRT text yourself cue by cue, keeping every index and timestamp unchanged.
5. Report the output paths and cue count. Treat the transcript as a draft, not verified text.
