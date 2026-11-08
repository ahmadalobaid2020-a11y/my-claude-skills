---
name: youtube-seo
description: Write YouTube titles, descriptions, tags, hashtags and timestamped chapters from a video's transcript, in Arabic or English. Use for "عنوان للفيديو", "وصف يوتيوب", "فصول", "تاقات", "YouTube SEO", "chapters", "title ideas".
---

# youtube-seo

## 1. Get the transcript

- Video file: `python3 ~/.claude/skills/subtitles/scripts/subtitles.py VIDEO --model small` (`medium` for Arabic), then read the SRT.
- Or use a transcript/script the user gives. Ask for the channel's niche, audience and the main search phrase if not obvious.

## 2. Chapters

- Read the SRT timestamps and split by topic changes. First chapter must be `00:00`; at least 3 chapters, each ≥10 s; 4–10 chapters for most videos.
- Format one per line: `00:00 المقدمة`, `02:15 ...` (use `H:MM:SS` past one hour). Titles 2–6 words, descriptive, not clickbait.
- Use real timestamps from the transcript, never invented ones.

## 3. Titles (give 5 options)

- ≤60 characters so they are not cut; main keyword in the first half.
- Mix angles: how-to, number/list, curiosity, result/benefit, question.
- Must match what the video actually delivers; the thumbnail text (see the `thumbnail` skill) should complement the title, not repeat it.

## 4. Description

- Lines 1–2 (shown above "more"): what the viewer gets + main keyword, naturally.
- Then a 3–5 sentence summary, the chapters block, links/CTA the user gave, and 3 hashtags at the end (`#...`; the first three show above the title).
- No keyword stuffing; write for people.

## 5. Tags

- 10–15 tags, ≤500 characters total: exact main phrase, variations, Arabic and English spellings if the audience uses both, channel name.

## Output

Deliver each part in its own code block for copy-paste: titles, description (with chapters inside), tags as one comma-separated line.
Do not claim search volumes or rankings; there is no keyword-volume data here unless a tool provides it.
