# my-claude-skills

Personal Claude Code skills.

| Skill | What it does |
| --- | --- |
| `subtitles` | Subtitles for any video/audio (SRT/VTT), English translation, burn-in. Local faster-whisper + ffmpeg. |
| `video-shorts` | Cut vertical 9:16 shorts from a long video, blur or crop framing, burned captions and title. |
| `thumbnail` | YouTube thumbnails (1280x720) from HTML + Chromium, Arabic fonts, small-size preview check. |
| `real-sfx` | Real recorded sound effects (own files or CC0 from Freesound) placed at timestamps and mixed under the voice. |
| `openverse` | Openly licensed sounds and images from Openverse (CC0/CC), licence and credits kept per file. No API key. |
| `audio-cleanup` | Denoise, de-ess, compress and normalise voice audio (YouTube -14 LUFS by default). |
| `youtube-seo` | Titles, description, tags and real-timestamp chapters from a transcript. |
| `social-post` | X/Instagram/TikTok/LinkedIn posts and threads from a video or text. |
| `yt-dlp` | Download video, audio, subtitles and info with yt-dlp. |
| `hypit` | Clone/produce videos with AI agents via SVML. Installed from [hypit-ai/hypit](https://github.com/hypit-ai/hypit) the official way (`npx skills add hypit-ai/hypit -g`), not stored here. |
| `hermes-whatsapp-voice` | Not a Claude skill: a [Hermes](https://github.com/NousResearch/hermes-agent) plugin for live voice calls with the Hermes bot over WhatsApp (Gemini Live). Installed from [ashwanthbalakrishnan5/hermes-whatsapp-voice](https://github.com/ashwanthbalakrishnan5/hermes-whatsapp-voice) with `hermes plugins install`, not stored here. |

Install: `./install.sh` (copies skills to `~/.claude/skills`, installs faster-whisper and yt-dlp).
Needs ffmpeg; `thumbnail` needs Node + Playwright Chromium;
`real-sfx` search/download needs a free `FREESOUND_API_KEY`;
`hypit` needs Node 22.15+ (`install.sh` runs the official skill install plus `npm install -g @hypit/hypit`) and a model service such as HypiHub for generation.
`hermes-whatsapp-voice` is installed only when `hermes` (>= 0.21.5) is on the machine, and still needs manual setup:
`hermes config set plugins.entries.hermes-whatsapp-voice.settings.owner_number +<your number>`,
`hermes whatsapp-voice pair` (scan the QR from the bot's phone), then `hermes whatsapp-voice serve`.
Needs a separate WhatsApp number for the bot and a Gemini API key in Hermes. Unofficial WhatsApp protocol: use a number you can afford to lose.
