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
