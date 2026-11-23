# Cutting: transcription, take selection, cut points

Load this for any speech edit (talking head, VSL, course, podcast clip). Distilled from albert-reel, famous-reel-editor, youtube-clean, open-edit, capcut-smartcut, community-reels-engine and the agency's own client jobs (a talk-only creator client, a luxury course client).

## 1. Transcribe
- **Default: ElevenLabs Scribe** (word-level, ~20 ms boundaries — cut-point math depends on it). Fallbacks, same output shape: Groq whisper-large-v3 (fast, looser timing) → local Whisper (offline, loosest). Never mix engines between the raw and the final-cut transcript.
- Long Arabic/Turkish files: full-file Whisper can silently skip chunks. Transcribe ~20–30 s silence-bounded chunks, or label from the full transcript and re-run only under-covered spans. Per-tiny-island Whisper is ~50× slower — don't.
- Normalise known Latin names that a model transliterates into Arabic script (tool, product, clinic names) in a post-process.
- Transcriber scripts often cache by output filename. After ANY re-cut to the same filename, delete the cached JSON first. Symptom of staleness: word times beyond the file's duration, or a "cached:" log line.
- Retiming beats re-buying: map existing per-word timings onto the EDL (`retime`) instead of re-transcribing, **except** for the final verification pass below.

## 2. Pick takes — last take wins
- Raws are multi-take with spoken director's notes ("put a clip of…", "ok so…", "again"). Read the transcript word by word and build a keep-EDL by hand.
- **Always keep the LAST complete take** of a repeated line, whole and uncut; cut only *between* takes at real silence. (House rule — it overrides "pick the best-sounding one".)
- A take counts as complete only if it reaches the sentence end with no restart, trail-off, laugh, "sorry" or self-correction. If the last take aborts, use the last complete one. On a mid-sentence restart, start the range at the restart that leads into the last complete ending.
- Also catch **paraphrased** retakes that share no exact words — do a semantic pass, not just string matching.
- Spoken triplets (the same sentence 3×) keep one; a genuine rule-of-three list keeps all three.
- Doubled connectors across kept takes ("Well… Well…", "يعني… يعني…") are a separate dupe class: scan consecutive sentence openers after the cut.
- Redundant trailing clauses that only restate the previous action are legitimate cuts.

## 3. Cut points (measure the signal, not the transcript)
- Silence detect: **−40 dB, min gap 0.35 s, pad 0.12 s** (pad the last word 0.45 s). Noisy room and −40 finds nothing → try **−35 dB**. Never −30/−32 (eats soft word releases). For Arabic content speech in echoey rooms, RMS > −42 dB ≈ speech; crew chatter sits −30…−38 — tune per source.
- Land the cut in the RMS trough after the previous word, ~30 ms before the next onset (5–10 ms scan). Body joins keep 60–120 ms of air; hook/opening joins 10–40 ms.
- Extend each kept range's end +0.2–0.4 s to catch the word release and breath, then trim the gap.
- No gap > 0.25–0.30 s inside a section (≤ 0.45 s only for a deliberate pre-reveal beat). After the final cut, print per-word gaps and micro-cut every one > 0.30 s — splice pads re-create gaps the first pass never saw.
- **No micro-fragments**: any kept clip < 0.8 s between two cuts reads as a double jump-cut. Merge it into a neighbour or drop the word.
- Room tone defeats the silence gate (locked-off product/B-roll shots, AC noise)? Use a motion detector instead, or combine: keep a span when audio **or** picture is active (auto-editor `--edit "(or audio:0.03 motion:0.06)"`, see `clipping-reframe.md`).
- Inhale vs fricative onset: low zero-crossing rate = inhale (cut it), high = "s/sh/f" (keep it).
- Quiet word tails under the threshold are performance, not dead air — never clip a complete word to win rhythm.
- Hide jump cuts: alternate 100% ↔ 110–115% punch-in at jump cuts (4K source makes this lossless). If a static stretch runs > 8 s, punch at a sentence boundary.

## 4. Verify the cut (before any graphics work)
1. **Re-transcribe the assembled cut** (fresh, cache deleted). Transcribers auto-complete clipped words ("out" prints "output"), so check each word's `end` against the file duration and look for hyphen fragments ("dol-").
2. **Hidden retakes**: a speaker who restarts without pausing becomes one long word-blob. Slice-transcribe ±2 s around any suspicious blob alone; narrow and repeat; a blob can hide more than one take. Re-slice the spliced region in the FINAL cut to prove it's gone.
3. **Triple check**: (A) coverage — every script line appears once or is knowingly dropped; (B) duplicates — slide a 5-word window for repeated n-grams and compare each section's end with the next section's start (retakes often repeat the transition line); (C) read-through as a viewer — dangling conjunctions, lost pronoun referents, numbers that contradict each other.
4. Replay short clips around every join and the last word. Only then start captions and graphics.

## 5. Assemble without drift
- Join with the **concat filter** (`[0:v][0:a][1:v][1:a]…concat=n=N:v=1:a=1`), one encode. Never `concat -c copy` of AAC segments — priming drift appears after ~40 s.
- If you must copy-concat, first normalise every segment (yuv420p, same colour range, same timescale). Mixed full/tv range resets the decoder mid-file (~2 s drift seen on a real client job). Check frame count with `showinfo`/`nb_read_frames`.
- Keep intermediate audio uncompressed (WAV/PCM) through cuts; encode AAC once at export. Add 4 ms fades at hard joins to kill clicks.
- Never put `afade` after an output-side `-ss` (mutes the segment) — seek on the input side.
- Sync-critical builds (camera + separate mic): one continuous encode on a constant frame clock; don't mux with `-shortest`. Refuse to render if picture/audio already differ by > 1.5 frames.
- Two sources (camera video + recorder audio): estimate offset from matched word-time deltas (median of inliers), confirm with cross-correlation (mono 8 kHz, 5 ms steps, 30 s windows near start/middle/end; peak < 0.15 = silence, move the window). Use a per-section offset on long recordings — device clocks drift ms/min.
- Every re-cut is atomic: rebuild everything derived from the cut (transcript, captions, card anchors, screen windows, cutouts, SFX cue times). One stale artifact misaligns the whole render.

## 6. When the edit lives in CapCut
The `capcut-smartcut` skill drives CapCut draft JSON directly (`smart-cut`, `cut-ranges`, subtitle fix/split/merge). Its heuristic cut must be followed by a manual transcript re-read loop — it misses partial restarts and intra-caption repeats. Last-take rule still applies.
