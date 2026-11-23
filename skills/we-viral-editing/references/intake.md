# Intake: logo, brand colours, font (ask BEFORE editing)

Before any cutting, captioning or graphics work, ask these three questions **in the language the person is writing in** (match their language and dialect: Egyptian/Gulf/Levantine Arabic, Turkish, English, Farsi…). If they mix languages, use the one their latest message is mostly in. Send all three in one message, numbered, so they can answer at once and attach files.

## The questions

**English**
> Before I start editing, three quick questions:
> 1. Do you want me to use a logo in the video? If yes, please upload it.
> 2. Do you have brand colours? If yes, please send them.
> 3. Do you have a specific font you want me to use? If yes, please send it.

**العربية**
> قبل ما أبدأ المونتاج، عندي ٣ أسئلة سريعة:
> ١. هل تحب أستخدم لوجو في الفيديو؟ إذا نعم، ارفعه لي من فضلك.
> ٢. هل عندك ألوان خاصة بالبراند؟ إذا نعم، ابعتها لي.
> ٣. هل في خط (فونت) معيّن تحب أستخدمه؟ إذا نعم، ابعته لي.

**Türkçe**
> Montaja başlamadan önce üç kısa soru:
> 1. Videoda logo kullanmamı ister misiniz? Evet ise lütfen yükleyin.
> 2. Marka renkleriniz var mı? Varsa lütfen gönderin.
> 3. Kullanmamı istediğiniz belirli bir font var mı? Varsa lütfen gönderin.

Any other language: translate the same three questions faithfully; keep them short and numbered.

## Rules
- **Always ask**, even for known clients. For a client already in `client-bible.md`, show what's on file inside the question so they can just confirm: e.g. "2. Brand colours — I have this client's orange-tan on file. Use it, or send new ones?"
- If the person already answered any of the three earlier in the conversation, don't re-ask that one — confirm it in one line instead.
- For a batch of videos, ask once for the whole batch.
- Accept any form of answer; never demand hex codes: a hex/RGB value, a screenshot, a website or Instagram link (pull colours/logo from it), a brand PDF, or plain words ("dark green and gold"). Convert to exact values yourself and state them back.
- "No" / "skip" / no answer to a question → use the house defaults below and say so in one line. Don't block the edit waiting.
- Do the edit only after the answers (or explicit skips) are in. If they send footage and say "just start", ask anyway in the same reply but start the speech cut (which doesn't depend on branding) while waiting.

## Processing the answers

### Logo
- Prefer SVG or a transparent PNG (≥ 1000 px wide). If they send a JPG with a background, remove the background (Adobe `image_remove_background` or rembg) and show the result.
- Check it renders visibly on the background it will sit on: make a light and a dark variant if needed (recolour fills, never add a duplicate `fill` attribute; bake explicit fills — `currentColor` renders black).
- Placement (house): small persistent bug top-left/top-right/top-centre inside the safe zone (y ≥ 250) at ~120–180 px wide, or a 40–60% opacity credit watermark bottom-centre; always big on the end card. Use the same size and position in every video of the set.
- Never distort, recolour into a new palette, or add effects to a client logo beyond a soft shadow for legibility.

### Brand colours
- Take 1 primary accent (+ optional secondary). The accent drives caption key words, pills, highlight boxes, prices and the end card (house rule 4). Everything else stays white/black/neutral.
- Check contrast: white text on the accent pill must be readable (aim ≥ 4.5:1; if not, use dark text on the accent or darken the pill 10–15%).
- Semantic colours stay: money-green for prices/savings, red for wrong/old price — unless the brand accent is itself green/red, then use the accent for positive and a neutral grey strike for negative.

### Font
- Accept a font file (.ttf/.otf/.woff2), a name, or a screenshot (identify it; say how sure you are).
- Arabic/Farsi work: **verify the font actually contains Arabic glyphs** (render a test word like "خصم ٥٠٪") — never infer from the name. Check Latin and digits too if the captions mix scripts.
- Define roles: caption/heading font (heavy weight: Bold/Black) + body font, each with a fallback installed on the render machine. Pair Arabic + Latin fonts of similar weight and x-height.
- Install/embed it in the render (HyperFrames/HTML: `@font-face` with the local file; ffmpeg/PIL: point at the file path). Render one sample frame and check shaping (connected letters, correct order, digits).
- If they have no font: use the house defaults.

## House defaults (when they skip)
- Colours: white + black shadow, one accent from the niche (clinic teal, restaurant warm orange/red, real estate gold on navy, SaaS blue, coach yellow).
- Fonts: Arabic — Cairo / Lama Sans / Thmanyah Sans (Black/ExtraBold for captions); Latin — Montserrat Black or Nunito Sans Black; Turkish retail — Bebas/Anton condensed caps.
- Logo: none on-screen; end card uses the name as text.

## Confirm and save
1. Make one preview frame (caption with key word + end card) with the brand applied and ask "Match?" Cheap now, expensive after the full render.
2. Once confirmed, save the values to the client's entry in `client-bible.md` (show what you're saving). Never silently overwrite stored values, and never restyle videos already delivered.
