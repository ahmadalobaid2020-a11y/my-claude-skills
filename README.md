# my-claude-skills

Personal Claude Code skills.

| Skill | What it does |
| --- | --- |
| `subtitles` | Subtitles for any video/audio (SRT/VTT), English translation, burn-in. Local faster-whisper + ffmpeg. |
| `video-shorts` | Cut vertical 9:16 shorts from a long video, blur or crop framing, burned captions and title. |
| `thumbnail` | YouTube thumbnails (1280x720) from HTML + Chromium, Arabic fonts, small-size preview check. |
| `real-sfx` | Real recorded sound effects (own files or CC0 from Freesound) placed at timestamps and mixed under the voice. |
| `audio-cleanup` | Denoise, de-ess, compress and normalise voice audio (YouTube -14 LUFS by default). |
| `youtube-seo` | Titles, description, tags and real-timestamp chapters from a transcript. |
| `social-post` | X/Instagram/TikTok/LinkedIn posts and threads from a video or text. |
| `yt-dlp` | Download video, audio, subtitles and info with yt-dlp. |
| `hypit` | Clone/produce videos with AI agents via SVML Installed from [hypit-ai/hypit](https://github.com/hypit-ai/hypit) the official way (`npx skills add hypit-ai/hypit -g`), not stored here. |

Install: `./install.sh` (copies skills to `~/.claude/skills`, installs faster-whisper).
Needs ffmpeg; `thumbnail` needs Node + Playwright Chromium; yt-dlp is installed separately;
`real-sfx` search/download needs a free `FREESOUND_API_KEY`;
`hypit` needs Node 22.15+ (`install.sh` runs the official skill install plus `npm install -g @hypit/hypit`) and a model service such as HypiHub for generation.
