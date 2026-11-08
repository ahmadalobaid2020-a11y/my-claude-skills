---
name: social-post
description: Write social media posts from a video, transcript, article or idea - X/Twitter posts and threads, Instagram and TikTok captions, LinkedIn, YouTube community posts - in Arabic (Gulf or MSA) or English, with hooks and hashtags. Use for "اكتب منشور", "كابشن", "تغريدة", "ثريد", "social post", "caption".
---

# social-post

## Inputs

- Source: a transcript (from the `subtitles` skill), a script, an article or the user's notes. For a video file, transcribe it first:
  `python3 ~/.claude/skills/subtitles/scripts/subtitles.py VIDEO --model small`
- Platforms, language and tone. Default to the user's language; for Arabic ask Gulf dialect or MSA if unclear.
- The goal: views, comments, link clicks, followers. And any link, handle or call to action to include.

## Platform rules

| Platform | Shape |
| --- | --- |
| X / Twitter | ≤280 chars per post. Hook in line 1. Thread: 4–8 posts, each standing alone, numbered `1/`; last one = summary + CTA. 1–2 hashtags max |
| Instagram | First 125 chars must hook (cut by "more"). Short paragraphs, line breaks, 1 CTA. 3–8 relevant hashtags at the end |
| TikTok | 1–2 punchy lines + 3–5 hashtags; on-screen text matters more than the caption |
| LinkedIn | Hook line, white space, a lesson or story, no hashtag walls (≤3) |
| YouTube community | Question or poll to start conversation, ≤2 lines |

## Writing rules

- Lead with the most surprising, useful or emotional point from the source, not "In this video…".
- One idea per post; concrete numbers and specifics beat adjectives.
- Write like a person: no clichés ("in today's fast-paced world", "game-changer"), no emoji spam (0–2).
- Hashtags: specific and in the post's language, mixing one broad and a few niche ones; never invent trends.
- Never invent facts, quotes or numbers that are not in the source; mark anything that needs checking.

## Output

For each platform give 2–3 options in a code block each, so they copy cleanly, with the character count for X.
Offer to schedule or publish only through a connected tool the user already has, and confirm the exact text and account before posting anything.
