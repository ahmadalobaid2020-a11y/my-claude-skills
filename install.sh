#!/usr/bin/env bash
# Copy every skill in skills/ into ~/.claude/skills and install their dependencies.
set -e
cd "$(dirname "$0")"
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
pip install -q --break-system-packages faster-whisper
command -v npm >/dev/null && npm install -g --silent @hypit/hypit || echo "npm not found: skipping @hypit/hypit CLI"
echo "installed: $(ls skills | tr '\n' ' ')"
