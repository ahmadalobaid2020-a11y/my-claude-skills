#!/usr/bin/env bash
# Copy every skill in skills/ into ~/.claude/skills and install their dependencies.
set -e
cd "$(dirname "$0")"
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
pip install -q --break-system-packages faster-whisper yt-dlp
if command -v npx >/dev/null; then
  npm install -g --silent skills           # skills CLI (vercel-labs/skills)
  skills add vercel-labs/skills -g -y      # find-skills skill
  skills add hypit-ai/hypit -g -y          # official Hypit skill install
  npm install -g --silent @hypit/hypit     # Hypit CLI
else
  echo "npx not found: skipping skills CLI and hypit"
fi
# Reel Studio skills, installed from their own repos (not stored here).
# Both call themselves "reel-studio", so the second one is renamed.
tmp=$(mktemp -d)
if git clone -q --depth 1 https://github.com/harper-carroll/reel-studio-skill "$tmp/a"; then
  rm -rf ~/.claude/skills/reel-studio
  cp -R "$tmp/a/reel-studio" ~/.claude/skills/reel-studio
else
  echo "could not fetch harper-carroll/reel-studio-skill: skipping"
fi
if git clone -q --depth 1 https://github.com/mohamedishagg/reel-studio "$tmp/b"; then
  rm -rf ~/.claude/skills/reel-studio-gen
  mkdir -p ~/.claude/skills/reel-studio-gen
  cp -R "$tmp/b/SKILL.md" "$tmp/b/scripts" "$tmp/b/LICENSE" ~/.claude/skills/reel-studio-gen/
  sed -i 's/^name: reel-studio$/name: reel-studio-gen/' ~/.claude/skills/reel-studio-gen/SKILL.md
  pip install -q --break-system-packages pillow
else
  echo "could not fetch mohamedishagg/reel-studio: skipping"
fi
rm -rf "$tmp"
echo "installed: $(ls skills | tr '\n' ' ')reel-studio reel-studio-gen"
