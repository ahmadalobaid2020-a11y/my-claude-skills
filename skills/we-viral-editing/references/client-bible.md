# Client bible (template)

This file is where the agency records what's true for each client, so the next edit for them starts from confirmed facts instead of a guess. Keep one entry per client. Update it the moment a client confirms or corrects something — never invent a value, and never carry a value forward from a similar-sounding client.

## What each entry should hold

- **Niche** — the industry (clinic, restaurant, real estate, study-abroad, coach/creator, SaaS, brand/event, etc.) and any sub-type that changes the format (e.g. "dental clinic — offer ads" vs "dental clinic — educational").
- **Accent colour (hex)** — the one brand colour that drives key words, pills, highlight boxes, prices and the end card. Confirm it's a hex value, not "the blue in the logo" — pull it from the logo file or ask.
- **Caption system** — which of the house caption systems this client uses (brand pill / key-word colour / white label / glassmorphism / word-by-word build / karaoke bar / bilingual / floating words — see `house-style.md`), and any client-specific tweak (font weight, box shape, position).
- **Logo placement** — where the logo bug sits (top-left, top-right, top-centre) and whether there's also a bottom-centre credit watermark, plus its opacity.
- **Font(s)** — the confirmed brand font(s) for on-screen text, separately for Arabic and Latin script if both are used. Note the source of the confirmation (client said so on a date, or it's the only font in their brand file) — never guess from "what looks right."
- **End card contents** — exactly what appears on the closing card: logo, phone/WhatsApp, handle(s), website, App Store/Play badges, country flags, hold duration, and whether it fades to black or holds.
- **CTA** — the client's standard call to action wording and mechanism (comment keyword, WhatsApp pill, link in bio, "تواصل معنا", etc.), and whether they A/B test CTA variants.
- **Language versions** — which languages/dialects this client ships in, and any client-specific rule (e.g. "keep Gulf dialect, never correct to MSA").
- **SFX / music toggle** — on, off, or voice-only. Some talk-only clients want zero SFX/music; others expect the full house sound design. Never assume — check this field or ask.
- **Known pitfalls** — anything that has gone wrong before for this specific client and must not repeat (e.g. "exports have shipped at 720x1280 twice — always confirm 1080x1920 before delivery", "a renamed program/product name must not appear in captions anymore").
- **Accepted / rejected log** — a short running list of what this client has approved or turned down, with dates, so style choices aren't re-litigated every job (e.g. "2026-08-02: approved the orange glow price ring; rejected the red starburst version").

Phone numbers, handles and other contact details in this file are live client business information — keep them current, confirm before reusing, and never publish this file's real contents outside the agency.

---

## Example entry (fictional, for format only)

### Example Dental Clinic
- **Niche**: clinic — dental, mix of educational and offer-ad content.
- **Accent colour**: `#2E8B7A` (teal-green), confirmed from the clinic's logo file.
- **Caption system**: glassmorphism — white text in a frosted translucent rounded box, key word bolder, ExtraBold weight.
- **Logo placement**: top-left bug, persistent; no bottom watermark.
- **Font(s)**: Arabic — Cairo Bold for captions, Greta Arabic for hook titles (confirmed by the client 2026-06-10). Latin — Montserrat Bold.
- **End card**: white card, logo centred, phone + WhatsApp pill, three country flags (patients travel from), holds 2 s then fades to black.
- **CTA**: WhatsApp pill plus "للحجز والاستفسار تواصل معنا"; occasionally A/B tests a comment-keyword variant ("اكتب كلمة ابتسامة").
- **Language versions**: Arabic (Gulf dialect, keep as spoken) + English for international patients.
- **SFX/music toggle**: on — light UI pops on icon reveals, soft corporate bed under VO, no music on offer ads (keeps focus on the price).
- **Known pitfalls**: two exports shipped at 608x1080 in the past — always confirm 1080x1920 in the sequence settings before rendering. The clinic renamed its "Smile Package" to "Signature Smile" in 2026-05 — never use the old name.
- **Accepted / rejected log**:
  - 2026-05-14: approved the teal glassmorphism caption box; rejected an earlier orange-pill version as "too loud."
  - 2026-06-10: confirmed Greta Arabic as the hook font going forward.
  - 2026-07-01: rejected a comedy skit format — the clinic wants to stay strictly educational/offer-led.
