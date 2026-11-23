# Long-form → shorts, scene detection, auto-reframe

Load when a client hands over a long recording (podcast, webinar, course, interview, event) and wants reels, or when reframing 16:9 footage to 9:16. Distilled from GitHub: Anil-matcha/AI-Youtube-Shorts-Generator, mutonby/openshorts, KazKozDev/auto-vertical-reframe, Breakthrough/PySceneDetect, WyattBlue/auto-editor, ClipsAI.

## 1. Find the clips
- Transcribe the whole source (Scribe), then chunk: sources > 30 min → 20-min windows with 60 s overlap. Dedupe candidates that overlap > 50%, keeping the higher score.
- Target **3–15 candidates of 15–60 s** per source (reels sweet spot 20–45 s).
- Score each candidate **0–100** against: hook strength of the first sentence · emotional peak · strong opinion/contrarian claim · revelation or number · conflict/tension · quotable line · story payoff · practical value · stands alone without context.
- Numeric version of that rubric (open-clip-studio, tune per client): hook type +12…18 · payoff quality +6…12 · complete thought +10 · good pacing/WPM +6 · each pause-for-emphasis +2 · speaker turns +1…5 · sentiment swing ±2 per charged word · banter/small talk −20 · generic intro ("hi guys, today…") −20. Target window 30–45 s, expanded to the nearest full sentence.
- Each candidate ships as: `start–end · score · hook line (first spoken sentence or a rewritten on-screen hook) · one-line "why it works"`. Show the ranked list to the user before cutting; let them pick.
- A clip must open on its strongest sentence (move it to the front if needed — a cold-open) and end on a complete thought. Trim run-up context ruthlessly; the hook device from SKILL.md still applies.
- Fast first pass alternative: `youtube-clipper` (Higgsfield personal_clipper) returns ranked clips from a YouTube URL.

## 2. Scene detection (split raw footage into shots)
PySceneDetect defaults, good starting points (`pip install scenedetect[opencv]`):
- **AdaptiveDetector** (default; best with pans/handheld): adaptive_threshold 3.0, window 2, min_scene_len 15 frames.
- ContentDetector (static cameras): threshold 27.0. ThresholdDetector (fades): 12. HashDetector: 0.395. HistogramDetector: 0.05.
- min_scene_len 15 frames is also the QC floor: a "shot" shorter than that is probably a flash frame.
- Uses: pre-split multicam/event footage before handing sections to agents; check "expected N cuts, found M"; give every shot its own reframe decision.

## 3. Auto-reframe 16:9 → 9:16 (target algorithm)
1. Detect shots (AdaptiveDetector). **Each shot gets a fresh framing decision** — never one smoothed track drifting across a cut.
2. Detect and track subjects (face detector + pose/landmarks; YOLO-seg + ByteTrack when available). Rank who to follow by face size, speaking (active-speaker/diarisation for interviews), pose and saliency.
3. Framing modes per shot: **single** (crop around the ranked subject, eyes at ~⅓ from the top) · **two-person** (both subjects close together → wider crop holding both, or stacked split-screen top/bottom when they're far apart) · **fallback** (low detection confidence, subject turned away, bad light) → full 16:9 frame letterboxed over a blurred, zoomed copy of itself — never a dead-centre crop that cuts a head.
   Stacked two-speaker layout: two 1080×960 panels with a thin brand-colour divider, each panel face-tracked; switch to a single panel on long monologues.
   Per-content presets: talking head = narrow zoom range, very slow moves; action/sports/pets/cars = wider zoom range, faster allowed step.
4. Camera path: lock on the subject, damp motion per axis, cap per-frame step and min/max zoom; hold still when the subject barely moves (a static crop reads more professional than constant micro-panning).
5. Re-place captions and graphics for 9:16 safe zones afterwards; never crop a finished edit with burned-in text.
- Reference implementations to read (not required to run): KazKozDev/auto-vertical-reframe (YOLOv11-seg + ByteTrack + MediaPipe + path optimiser), mutonby/openshorts (MediaPipe + YOLOv8 with blurred-background fallback), ClipsAI (Pyannote speaker-driven crops for podcasts).

## 4. Auto-cut helpers
- `auto-editor` (`pip install auto-editor`, public domain) — fast first-pass silence cut on long unscripted footage, exports Premiere/Resolve/FCP XML. Its `audio:threshold=0.04` is a linear ratio, **not** our −40 dB — calibrate per source. `--edit "(or audio:0.03 motion:0.06)"` keeps a section when *either* the audio or the picture is active, so silent-but-moving moments (demos, gestures) survive. `motion:0.02` alone cuts dead static footage (locked-off product shots with room tone). Always follow with the house last-take and word-safety pass from `cutting.md` — auto-editor doesn't know about takes.
- Jumpcutter-style **speed-up instead of delete** (silent parts at 4–8×) is an alternative for "tightened, not chopped" lecture content — not house style; only on request.
