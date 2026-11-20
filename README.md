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

| `autoae` | Find and customise animated video templates (intros, outros, titles, lower thirds, logo reveals) with [AutoAE](https://autoae.online). Installed by `install.sh` with `npx skills add https://autoae.online`. Needs Node 24+ and an AutoAE sign-in (`npx @autoae/cli auth login`). |
| `video-director` | Dramaturgy-first AI video directing: 14-field shot cards, pacing, and prompts for Seedance, Kling, Veo and MiniMax. Installed by `install.sh` from [imMamdouhaboammar/designly](https://github.com/imMamdouhaboammar/designly) (this skill only). |
| Anthropic skills | `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator`, `frontend-design`, `canvas-design`, `mcp-builder`, `webapp-testing` and the rest of [anthropics/skills](https://github.com/anthropics/skills). Cloned and copied by `install.sh`, not stored here. |

Install: `./install.sh` (copies skills to `~/.claude/skills`, adds the Anthropic skills, installs faster-whisper and yt-dlp).
Needs ffmpeg; `thumbnail` needs Node + Playwright Chromium;
`real-sfx` search/download needs a free `FREESOUND_API_KEY`;
`hypit` needs Node 22.15+ (`install.sh` runs the official skill install plus `npm install -g @hypit/hypit`) and a model service such as HypiHub for generation.
