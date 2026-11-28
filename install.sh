#!/usr/bin/env bash
# Copy every skill in skills/ into ~/.claude/skills and install their dependencies.
set -e
cd "$(dirname "$0")"
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
pip install -q --break-system-packages faster-whisper yt-dlp
# Anthropic's official skills (anthropics/skills): docx, pdf, pptx, xlsx, skill-creator, ...
tmp=$(mktemp -d)
if git clone -q --depth 1 https://github.com/anthropics/skills.git "$tmp/anthropic-skills"; then
  cp -r "$tmp"/anthropic-skills/skills/* ~/.claude/skills/
  pip install -q --break-system-packages \
    -r "$tmp/anthropic-skills/skills/slack-gif-creator/requirements.txt" \
    -r "$tmp/anthropic-skills/skills/mcp-builder/scripts/requirements.txt" || true
else
  echo "could not clone anthropics/skills: skipping"
fi
# SallyRS/video-director, installed as video-director-sally (designly's video-director keeps the plain name)
if git clone -q --depth 1 https://github.com/SallyRS/video-director.git "$tmp/sally-vd"; then
  rm -rf ~/.claude/skills/video-director-sally
  cp -r "$tmp/sally-vd/skills/video-director" ~/.claude/skills/video-director-sally
  sed -i '0,/^name: video-director$/s//name: video-director-sally/' ~/.claude/skills/video-director-sally/SKILL.md
else
  echo "could not clone SallyRS/video-director: skipping"
fi
# earshot (Leonxlnx/earshot): lets the agent listen to audio. CPU-only PyTorch, ~1.1 GB of models.
if command -v uv >/dev/null; then
  uv tool install -q "earshot[mcp,llm] @ git+https://github.com/Leonxlnx/earshot" \
    --index https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match \
    || echo "earshot install failed: skipping"
  if command -v earshot >/dev/null || [ -x ~/.local/bin/earshot ]; then
    PATH="$HOME/.local/bin:$PATH"
    HF_HUB_DISABLE_XET=1 earshot doctor --fetch >/dev/null 2>&1 || echo "earshot model download failed: run 'HF_HUB_DISABLE_XET=1 earshot doctor --fetch'"
    if git clone -q --depth 1 https://github.com/Leonxlnx/earshot.git "$tmp/earshot"; then
      rm -rf ~/.claude/skills/earshot
      cp -r "$tmp/earshot/skills/earshot" ~/.claude/skills/earshot
    fi
    if command -v claude >/dev/null && ! claude mcp get earshot >/dev/null 2>&1; then
      claude mcp add earshot --scope user -e EARSHOT_THREADS=3 -e HF_HUB_DISABLE_XET=1 \
        -- "$HOME/.local/bin/earshot" mcp || echo "earshot MCP registration failed: skipping"
    fi
  fi
else
  echo "uv not found: skipping earshot"
fi
# VoiceStudio (debpalash/VoiceStudio): local TTS, voice cloning, dubbing and transcription.
# Headless CPU backend in ~/VoiceStudio; start it with scripts/voicestudio-start.sh. Models download on request.
if command -v uv >/dev/null && { command -v bun >/dev/null || [ -x ~/.bun/bin/bun ]; }; then
  PATH="$HOME/.bun/bin:$PATH"
  if [ ! -d ~/VoiceStudio/.git ]; then
    git clone -q --depth 1 https://github.com/debpalash/VoiceStudio.git ~/VoiceStudio || echo "could not clone VoiceStudio"
  fi
  if [ -d ~/VoiceStudio ]; then
    (cd ~/VoiceStudio && OMNIVOICE_TORCH_VARIANT=cpu OMNIVOICE_DEVICE=cpu UV_HTTP_TIMEOUT=300 bun run setup:api >/dev/null) \
      || echo "VoiceStudio backend setup failed: skipping"
    if command -v skills >/dev/null; then
      skills add debpalash/VoiceStudio --skill voicestudio -g -y || echo "voicestudio skill install failed"
    fi
    if command -v claude >/dev/null && ! claude mcp get voicestudio >/dev/null 2>&1; then
      claude mcp add --transport http voicestudio http://127.0.0.1:3900/mcp --scope user || echo "voicestudio MCP registration failed"
    fi
  fi
else
  echo "uv or bun not found: skipping VoiceStudio"
fi
# bang-motion (bangtutorial/bang-motion): cinematic HTML + GSAP motion graphics (openers, promos, explainers).
# puppeteer is for its snap.mjs / export-frames.mjs; an existing Playwright Chromium is reused instead of a download.
if git clone -q --depth 1 https://github.com/bangtutorial/bang-motion.git "$tmp/bang-motion"; then
  rm -rf ~/.claude/skills/bang-motion && mkdir -p ~/.claude/skills/bang-motion
  (cd "$tmp/bang-motion" && cp -r SKILL.md LICENSE references assets scripts ~/.claude/skills/bang-motion/)
  if command -v npm >/dev/null; then
    (cd ~/.claude/skills/bang-motion && { [ ! -x /opt/pw-browsers/chromium ] || export PUPPETEER_SKIP_DOWNLOAD=1; } \
      && npm install --silent --no-save puppeteer) || echo "bang-motion: puppeteer install failed (frame capture and MP4 export unavailable)"
  fi
else
  echo "could not clone bangtutorial/bang-motion: skipping"
fi
# HandDraw-Skill (ToBeWin/HandDraw-Skill): hand-drawn / whiteboard explainer MP4s from a JSON DSL, rendered with Remotion.
# Built in place (~310 MB with node_modules); .venv holds edge-tts for optional narration.
if command -v npm >/dev/null && git clone -q --depth 1 https://github.com/ToBeWin/HandDraw-Skill.git "$tmp/handdraw"; then
  rm -rf "$tmp/handdraw/.git" ~/.claude/skills/handdraw-skill
  cp -r "$tmp/handdraw" ~/.claude/skills/handdraw-skill
  (
    cd ~/.claude/skills/handdraw-skill && npm install --silent && npm run build >/dev/null
    if command -v uv >/dev/null; then uv venv -q .venv && uv pip install -q --python .venv/bin/python -r packages/audio/requirements.txt
    else python3 -m venv .venv && .venv/bin/pip install -q -r packages/audio/requirements.txt; fi
    # Remotion downloads Chrome Headless Shell from remotion.media on first render. Where a Playwright
    # headless shell is already installed (Claude Code cloud containers), use that one instead.
    pw=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64 2>/dev/null | tail -1)
    if [ -n "$pw" ]; then
      d=node_modules/.remotion/chrome-headless-shell
      mkdir -p $d/linux64 && ln -sfn "$pw" $d/linux64/chrome-headless-shell-linux64
      sed -n "s/^exports.TESTED_VERSION = '\(.*\)';/\1/p" node_modules/@remotion/renderer/dist/browser/get-chrome-download-url.js > $d/VERSION
    fi
  ) || echo "handdraw-skill setup failed: run 'npm install && npm run build' in ~/.claude/skills/handdraw-skill"
else
  echo "npm missing or could not clone ToBeWin/HandDraw-Skill: skipping"
fi
# huashu-art-motion (alchaincyf/huashu-art-motion): art-style animation in code (36 painting styles, explainer grammars).
# Renders with uv + Playwright Chromium + ffmpeg; skill text is in Chinese. Installed whole (~74 MB), minus git metadata.
if git clone -q --depth 1 https://github.com/alchaincyf/huashu-art-motion.git "$tmp/huashu-art-motion"; then
  rm -rf "$tmp/huashu-art-motion/.git" "$tmp/huashu-art-motion/.github" ~/.claude/skills/huashu-art-motion
  cp -r "$tmp/huashu-art-motion" ~/.claude/skills/huashu-art-motion
  # A Chromium already provided through PLAYWRIGHT_BROWSERS_PATH is reused (pin playwright to its version when rendering).
  if command -v uv >/dev/null && ! ls "${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"/chromium-* >/dev/null 2>&1; then
    uv run -q --with playwright playwright install chromium || echo "huashu-art-motion: Chromium install failed: run 'uv run --with playwright playwright install chromium'"
  fi
else
  echo "could not clone alchaincyf/huashu-art-motion: skipping"
fi
# solidworks-mcp skill (soheil-mp/solidworks-mcp): how to drive SOLIDWORKS through that MCP server.
# The servers themselves are Windows-only: install them there with scripts/install-solidworks-mcp.ps1.
if git clone -q --depth 1 https://github.com/soheil-mp/solidworks-mcp.git "$tmp/solidworks-mcp"; then
  rm -rf ~/.claude/skills/solidworks-mcp
  cp -r "$tmp/solidworks-mcp/skills/solidworks-mcp" ~/.claude/skills/solidworks-mcp
else
  echo "could not clone soheil-mp/solidworks-mcp: skipping"
fi
# Papermorph (DozenTwelve/Papermorph): narrated, animated web books, picture books, documentaries and shorts.
# Only the skill folder (SKILL.md, references, scripts, templates) is installed, not the repo's site/ books.
# Needs uv, ffmpeg and Playwright Chromium + Firefox at use time.
if git clone -q --depth 1 https://github.com/DozenTwelve/Papermorph.git "$tmp/papermorph"; then
  rm -rf ~/.claude/skills/papermorph
  cp -r "$tmp/papermorph/.claude/skills/papermorph" ~/.claude/skills/papermorph
else
  echo "could not clone DozenTwelve/Papermorph: skipping"
fi
# YouTube agent (Jakeschincariol/youtube-agent-skill): eleven yt-* skills (script, package, edit, retention, shorts, ...).
# Plain Python 3, no dependencies, no API key. The skills read the voice profile at ~/.claude/youtube/voice.md;
# this repo's youtube/voice.md is the copy that lasts, so fill that one in.
if git clone -q --depth 1 https://github.com/Jakeschincariol/youtube-agent-skill.git "$tmp/youtube-agent"; then
  for d in "$tmp"/youtube-agent/skills/yt-*; do
    rm -rf ~/.claude/skills/"$(basename "$d")"
    cp -r "$d" ~/.claude/skills/
  done
  mkdir -p ~/.claude/youtube
  if [ -f youtube/voice.md ]; then cp youtube/voice.md ~/.claude/youtube/voice.md
  else cp -n "$tmp/youtube-agent/templates/voice.md" ~/.claude/youtube/voice.md; fi
else
  echo "could not clone Jakeschincariol/youtube-agent-skill: skipping"
fi
# CLI-Anything (HKUDS/CLI-Anything): turns software into agent-native CLIs.
# cli-hub browses and installs ready-made CLIs (catalog at hkuds.github.io, redirecting to clianything.cc); the cli-hub-meta-skill teaches
# the agent to use it; the Claude Code plugin adds /cli-anything to generate a CLI for new software.
pip install -q --break-system-packages cli-anything-hub || echo "cli-anything-hub install failed: skipping"
if git clone -q --depth 1 https://github.com/HKUDS/CLI-Anything.git "$tmp/cli-anything"; then
  rm -rf ~/.claude/skills/cli-hub-meta-skill
  cp -r "$tmp/cli-anything/cli-hub-meta-skill" ~/.claude/skills/cli-hub-meta-skill
else
  echo "could not clone HKUDS/CLI-Anything: skipping"
fi
if command -v claude >/dev/null; then
  { claude plugin marketplace add HKUDS/CLI-Anything && claude plugin install cli-anything; } >/dev/null 2>&1 \
    || echo "cli-anything plugin install failed: run '/plugin marketplace add HKUDS/CLI-Anything' then '/plugin install cli-anything'"
fi
rm -rf "$tmp"
if command -v npx >/dev/null; then
  npm install -g --silent skills           # skills CLI (vercel-labs/skills)
  skills add vercel-labs/skills -g -y      # find-skills skill
  skills add hypit-ai/hypit -g -y          # official Hypit skill install
  # AutoAE motion-graphics templates (needs Node 24+ at use time; sign in with `npx @autoae/cli auth login`)
  NODE_USE_ENV_PROXY=1 skills add https://autoae.online -g -y || echo "AutoAE skill install failed: skipping"
  # video-director only, from imMamdouhaboammar/designly (AI video directing and multi-model prompting)
  skills add imMamdouhaboammar/designly --skill video-director -g -y || echo "video-director install failed: skipping"
  npm install -g --silent @hypit/hypit     # Hypit CLI
else
  echo "npx not found: skipping skills CLI and hypit"
fi
echo "installed: $(ls skills | tr '\n' ' ')"
