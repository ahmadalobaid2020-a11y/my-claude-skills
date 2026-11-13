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
if command -v hermes >/dev/null; then
  # Hermes plugin: live WhatsApp voice calls (needs pairing afterwards, see README)
  hermes plugins install ashwanthbalakrishnan5/hermes-whatsapp-voice --enable
else
  echo "hermes not found: skipping hermes-whatsapp-voice"
fi
echo "installed: $(ls skills | tr '\n' ' ')"
