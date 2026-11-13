#!/usr/bin/env bash
# Copy every skill in skills/ into ~/.claude/skills and install their dependencies.
set -e
cd "$(dirname "$0")"
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
# av 19 dropped an argument faster-whisper 1.2 still passes, so transcription fails with it.
pip install -q --break-system-packages faster-whisper "av<19" yt-dlp
if command -v npx >/dev/null; then
  npm install -g --silent skills           # skills CLI (vercel-labs/skills)
  skills add vercel-labs/skills -g -y      # find-skills skill
  skills add hypit-ai/hypit -g -y          # official Hypit skill install
  npm install -g --silent @hypit/hypit     # Hypit CLI
else
  echo "npx not found: skipping skills CLI and hypit"
fi
# majed-video (majedphotos/video-ad-editor): six Arabic video-editing skills, not stored here.
MV_SKILLS="video-ad-editor montage-video motion-video podcast-video review-video thumbnail-video"
MV_TMP="$(mktemp -d)"
if git clone -q --depth 1 https://github.com/majedphotos/video-ad-editor.git "$MV_TMP/src"; then
  for s in $MV_SKILLS; do rm -rf ~/.claude/skills/"$s"; cp -r "$MV_TMP/src/$s" ~/.claude/skills/; done
  pip install -q --break-system-packages opencv-python-headless scipy numpy pillow
  command -v npm >/dev/null && (cd ~/.claude/skills/video-ad-editor && npm i --silent puppeteer-core)
  echo "installed majed-video $(cat ~/.claude/skills/video-ad-editor/VERSION 2>/dev/null): $MV_SKILLS"
else
  echo "could not clone majedphotos/video-ad-editor: skipping majed-video"
fi
rm -rf "$MV_TMP"
echo "installed: $(ls skills | tr '\n' ' ')"
