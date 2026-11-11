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
| `reel-studio` | Talking-head or podcast clip to a 9:16 reel: Higgsfield AI B-roll, word-synced captions and split-screen in Remotion. Installed from [harper-carroll/reel-studio-skill](https://github.com/harper-carroll/reel-studio-skill), not stored here. |
| `reel-studio-gen` | Create clips from a prompt (Pollinations `gen` API) and edit a reel: captions, silence cuts, generated SFX, hook title, CTA card. Installed from [mohamedishagg/reel-studio](https://github.com/mohamedishagg/reel-studio) and renamed to avoid the name clash, not stored here. |

Install: `./install.sh` (copies skills to `~/.claude/skills`, installs faster-whisper and yt-dlp).
Needs ffmpeg; `thumbnail` needs Node + Playwright Chromium;
`real-sfx` search/download needs a free `FREESOUND_API_KEY`;
`hypit` needs Node 22.15+ (`install.sh` runs the official skill install plus `npm install -g @hypit/hypit`) and a model service such as HypiHub for generation;
`reel-studio` needs Node 18+ and the Higgsfield MCP (`https://mcp.higgsfield.ai/mcp`, active plan) for B-roll;
`reel-studio-gen` needs a Pollinations key (`python3 ~/.claude/skills/reel-studio-gen/scripts/gen.py --set-key`).
