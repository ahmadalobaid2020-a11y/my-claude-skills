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
| `handdraw-skill` | Hand-drawn / whiteboard explainer MP4s from a JSON animation DSL (SVG line art, text reveals), rendered with Remotion, optional free Edge TTS narration. Installed and built by `install.sh` from [ToBeWin/HandDraw-Skill](https://github.com/ToBeWin/HandDraw-Skill) (~310 MB with `node_modules`). Needs Node 20+ and ffmpeg. Remotion fetches its browser from `remotion.media` on first render (`install.sh` links the Playwright headless shell instead when one exists); narration needs `speech.platform.bing.com` and, behind the cloud proxy, `wss_proxy="$HTTPS_PROXY"` in front of the render command. Slower narration (a negative `rate` such as `-5%`) fails in the upstream CLI; use `+0%` or faster. |
| `huashu-art-motion` | Art-style animation drawn in code: 36 painting styles (cave art to pixel), explainer animation grammars, narrated-film pipeline, QA gates. Skill text is in Chinese. Installed by `install.sh` from [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) (~74 MB). Needs `uv`, ffmpeg and Playwright Chromium; render with `uv run --with playwright python scripts/engine/render.py ...`. In a cloud container pin Playwright to the pre-installed browser: `--with playwright==$(node -e "console.log(require('playwright/package.json').version)")`. |
| `solidworks-mcp` | Drive a running SOLIDWORKS from Claude: sketch and model parts, assemblies, drawings, import/export, simulation. Two MCP servers, **Windows only** (SOLIDWORKS is), installed there with `powershell -ExecutionPolicy Bypass -File scripts\install-solidworks-mcp.ps1`: `solidworks` from [soheil-mp/solidworks-mcp](https://github.com/soheil-mp/solidworks-mcp) (C#, 161 tools, needs the .NET 10 SDK, built from source) and `solidworks-py` from [HarrierPigeon/Solidworks-MCP-Server](https://github.com/HarrierPigeon/Solidworks-MCP-Server) (Python via `uv`, tools prefixed `solidworks_`). Both are registered with Claude Code at user scope (`-Desktop` adds Claude Desktop, `-Only DotNet` or `-Only Python` installs one). They share one SOLIDWORKS, so use one at a time, and save your work first. `install.sh` installs only the `solidworks-mcp` skill (how to use the first server's tools). |
| `papermorph` | Narrated, animated web books: lessons from textbook PDFs, paper-puppet picture books, documentaries, upright shorts, scroll stories and explorable maps, as static pages. Installed by `install.sh` from [DozenTwelve/Papermorph](https://github.com/DozenTwelve/Papermorph) (skill folder only, MIT). Needs `uv`, ffmpeg and Playwright Chromium + Firefox (`uv run --with playwright playwright install chromium firefox`); narration uses Edge TTS (online) or Kokoro; ElevenLabs/OpenRouter steps are optional and paid. |
| Anthropic skills | `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator`, `frontend-design`, `canvas-design`, `mcp-builder`, `webapp-testing` and the rest of [anthropics/skills](https://github.com/anthropics/skills). Cloned and copied by `install.sh`, not stored here. |

## Video editing skills (from a shared Drive folder)

18 skills copied into `skills/` from the public Google Drive folder "Claude editing skills" (owner hidden, files dated Oct 11). Installed by `install.sh` like the other local skills. Most need ffmpeg and Python 3; several need your own API keys (ElevenLabs, Gemini, Groq, fal) or the Higgsfield MCP, as each `SKILL.md` explains. The `majed-*` folders register under their own names without the prefix (`video-ad-editor`, `montage-video`, `motion-video`, `podcast-video`, `davinci-video`, `thumbnail-video`).

| Skill | What it does |
| --- | --- |
| `we-viral-editing` | The We Viral agency editing playbook, with its community reel engine. |
| `famous-reel-editor` | Talking head to a styled 9:16 reel with motion graphics and AI B-roll. |
| `albert-reel` | Green-glass motion-graphics reel, accent colour themeable. |
| `albert-reel-white` | White "popout" reel where the speaker's head breaks out of the frame. |
| `albert-reel-white-screen` | Split-screen tutorial reel (camera + screen recording). |
| `majed-video-ad-editor` | Talking head to reel or ad: silence cuts, word-timed Arabic captions. Its `00_setup.sh --update` replaces the skill with the latest GitHub release, and `--extras` downloads a DeepFilterNet binary; both only when run. |
| `majed-montage-video` | No-speech clips cut to the beat of a song. |
| `majed-motion-video` | 3D motion-graphics film from text only. |
| `majed-podcast-video` | Multi-camera podcasts and interviews cut into reels. |
| `majed-davinci-video` | Edits inside DaVinci Resolve Studio (needs Resolve on your own machine). |
| `majed-thumbnail-video` | Reel cover / first-frame design. |
| `famous-youtube-editor` | Long-form 16:9 edit with full-screen animations, picture-in-picture and B-roll. |
| `youtube-clean` | Calm long-form edit with Apple-style UI recreations. |
| `youtube-popup-graphic` | Premiere-style UI popup graphics. |
| `youtube-broll-maker` | AI B-roll of yourself from one photo (Higgsfield MCP). |
| `youtube-clipper` | Short clips from a YouTube video (Higgsfield clipper). |
| `capcut-smartcut` | Removes silences and repeated takes from CapCut projects (needs CapCut on your own machine). |
| `open-edit` | Runs edits through VEED's engine. |

Four of them ship the same 11.6 MB `assets/bg-music.m4a` with no licence stated; check its rights before publishing a video that uses it.

Install: `./install.sh` (copies skills to `~/.claude/skills`, adds the Anthropic skills, installs faster-whisper and yt-dlp).
Needs ffmpeg; `thumbnail` needs Node + Playwright Chromium;
`real-sfx` search/download needs a free `FREESOUND_API_KEY`;
`hypit` needs Node 22.15+ (`install.sh` runs the official skill install plus `npm install -g @hypit/hypit`) and a model service such as HypiHub for generation.
