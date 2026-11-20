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
rm -rf "$tmp"
if command -v npx >/dev/null; then
  npm install -g --silent skills           # skills CLI (vercel-labs/skills)
  skills add vercel-labs/skills -g -y      # find-skills skill
  skills add hypit-ai/hypit -g -y          # official Hypit skill install
  # AutoAE motion-graphics templates (needs Node 24+ at use time; sign in with `npx @autoae/cli auth login`)
  NODE_USE_ENV_PROXY=1 skills add https://autoae.online -g -y || echo "AutoAE skill install failed: skipping"
  npm install -g --silent @hypit/hypit     # Hypit CLI
else
  echo "npx not found: skipping skills CLI and hypit"
fi
echo "installed: $(ls skills | tr '\n' ' ')"
