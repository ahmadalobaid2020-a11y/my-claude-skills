---
name: yt-dlp
description: Download video, audio, subtitles or info from YouTube and ~1800 sites with yt-dlp. Use for a video or playlist URL, mp3 audio, a quality cap, a clip, or subtitles.
---

# yt-dlp

yt-dlp (source checkout in /opt/yt-dlp, `git pull` to update) and ffmpeg are on PATH.

Rules: download only what the user may (own, licensed, or personal use the site allows); no DRM or paywall bypass.
Save into the working directory; add `--no-playlist` for a single video unless the playlist is wanted.
Inspect first with `yt-dlp -F URL`. Report file path, size and duration; quote the real error on failure.

- Best mp4: `yt-dlp -f "bv*+ba/b" --merge-output-format mp4 URL`
- Max 1080p: `yt-dlp -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 URL`
- Audio mp3: `yt-dlp -x --audio-format mp3 --audio-quality 0 URL`
- Clip: `yt-dlp --download-sections "*00:01:30-00:02:45" --force-keyframes-at-cuts URL`
- Subtitles: `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "ar,en.*" --convert-subs srt URL`
- Thumbnail: `yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg URL`
- Playlist: `yt-dlp --yes-playlist -o "%(playlist_index)03d - %(title).80s.%(ext)s" URL`
- Info: `yt-dlp -j --no-download URL`

Errors: 403/429/"not a bot" usually means the cloud IP or network is blocked; say so and suggest running it locally.
A proxy "Tunnel connection failed: 403" means the environment's network policy blocks that host.
