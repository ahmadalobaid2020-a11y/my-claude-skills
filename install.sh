#!/usr/bin/env bash
# Copy every skill in skills/ into ~/.claude/skills and install their dependencies.
set -e
cd "$(dirname "$0")"
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
pip install -q --break-system-packages faster-whisper
if command -v npx >/dev/null; then
  npx -y skills add hypit-ai/hypit -g -y   # official Hypit skill install
  npm install -g --silent @hypit/hypit     # Hypit CLI
else
  echo "npx not found: skipping hypit"
fi
echo "installed: $(ls skills | tr '\n' ' ')"
