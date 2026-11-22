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
| `video-director-sally` | Direct and build a short motion-graphics video end to end: design options, a reviewable storyboard, motion spec, HyperFrames build and sound. Installed by `install.sh` from [SallyRS/video-director](https://github.com/SallyRS/video-director), renamed so it can sit beside designly's `video-director`. Needs Python 3, ffmpeg and `npx hyperframes`. |
| `earshot` | Lets the agent listen: pick and trim sound effects, check a soundtrack's sync and loudness, tell real recordings from synthesized ones. Installed by `install.sh` from [Leonxlnx/earshot](https://github.com/Leonxlnx/earshot) with `uv` (CPU-only PyTorch), downloads ~1.1 GB of models and registers the `earshot` MCP server. |
| `voicestudio` | Local text-to-speech, voice cloning and design, dubbing and transcription with [VoiceStudio](https://github.com/debpalash/VoiceStudio). `install.sh` builds its headless CPU backend in `~/VoiceStudio` (~2.3 GB), installs the skill and registers the `voicestudio` MCP server. Start the backend each session with `scripts/voicestudio-start.sh`; voice models (e.g. OmniVoice, 2.4 GB) download only when you approve. |
| `bang-motion` | Cinematic motion graphics in the browser (openers, promos, kinetic typography, explainers) as one `index.html` with HTML + CSS + GSAP, optional MP4 export. Installed by `install.sh` from [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) with puppeteer for frame checks. In a cloud container run its scripts with `PUPPETEER_EXECUTABLE_PATH=<repo>/scripts/chrome-nosandbox.sh`; pages load GSAP and fonts from `cdn.jsdelivr.net`, `cdnjs.cloudflare.com` and Google Fonts, so those hosts must be reachable. |
| `handdraw-skill` | Hand-drawn / whiteboard explainer MP4s from a JSON animation DSL (SVG line art, text reveals), rendered with Remotion, optional free Edge TTS narration. Installed and built by `install.sh` from [ToBeWin/HandDraw-Skill](https://github.com/ToBeWin/HandDraw-Skill) (~310 MB with `node_modules`). Needs Node 20+ and ffmpeg. Remotion fetches its browser from `remotion.media` on first render (`install.sh` links the Playwright headless shell instead when one exists); narration needs `speech.platform.bing.com`. |
| Anthropic skills | `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator`, `frontend-design`, `canvas-design`, `mcp-builder`, `webapp-testing` and the rest of [anthropics/skills](https://github.com/anthropics/skills). Cloned and copied by `install.sh`, not stored here. |

Install: `./install.sh` (copies skills to `~/.claude/skills`, adds the Anthropic skills, installs faster-whisper and yt-dlp).
Needs ffmpeg; `thumbnail` needs Node + Playwright Chromium;
`real-sfx` search/download needs a free `FREESOUND_API_KEY`;
`hypit` needs Node 22.15+ (`install.sh` runs the official skill install plus `npm install -g @hypit/hypit`) and a model service such as HypiHub for generation.
