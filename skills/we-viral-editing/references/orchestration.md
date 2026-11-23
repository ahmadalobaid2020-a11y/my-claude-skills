# Long edits, sub-agents, notes and approval gates

Load for anything longer than ~3 min (VSL, course module, YouTube long-form), a batch of reels, or a revision round with client notes.

## Stage gates (hard state machine)
1. **Clean cut** (speech only) → show it → client/user approves. Record what was approved (file hash or version name).
2. **Elements** (captions, graphics, B-roll, music) are built on the approved clean timeline only.
3. Any change to the clean cut after approval invalidates stage 2 → rebuild derived artifacts and re-approve.
4. Stitch/finalise only after every section is explicitly accepted. Never auto-assemble on completion.

## Mediator + section agents (long-form)
- **Mediator** owns everything that must stay globally consistent: the single voice cut, sync build, per-section packaging, verification, notes routing, stitching.
- **Section agents** each own one section, work only inside their own folder, never touch shared libs or other sections. Sections render in parallel.
- Each agent gets a written brief file (template), not an ad-hoc chat message: inputs, folder boundary, what to read first (this skill's SKILL.md + `motion-design.md` + the client entry), shared do/don'ts, and a required terse report: mode timeline, % per mode, what each visual shows and why, files produced.
- Hold the first/last frames of each section on a neutral resting state and add short audio fades so any two sections butt-join cleanly. Let music tails overlap ~1.5 s via an audio-only crossfade.
- The render machine is shared: expect lower fps with many agents; background long renders instead of letting a shell call time out.
- Never message/resume an agent that's still mid-workflow (it spawns a second concurrent instance that edits the same files). Put shared answers in a common brief file; wait for it to finish.

## Notes loop
1. Batch the client's notes. Route each note to the agent/section it concerns, not a broadcast. Global notes ("music quieter everywhere") go into the shared brief file.
2. Tell the user who is working on what.
3. Re-verify each note yourself at the exact timestamp named (frames + audio).
4. Report per note: done / not done / done differently (why).
5. Scoped edits ("fix only X"): diff before/after against an allow-list of what may change; name every out-of-scope difference.
6. Keep an **accepted / rejected log** per client (in the project folder) and feed it into the next round's brief so rejected directions are never re-proposed.

## Batches of short reels
- Ask the intake questions once for the whole batch (see `intake.md`).
- One sub-agent per reel is fine for 4+ reels; each gets the same brief file plus its own clip. The coordinator runs QC on every output.

## Reference decoding
To learn from a reference reel, analyse technique only: hook structure, caption grammar, cut rhythm, framing, 3 concrete motion events with timestamps, audio role. Map each borrowed move to "existing template" vs "new custom work". Never copy branded assets, exact wording, or clone a voice. (`community-decode` skill does this.)

## Beginner / client-facing mode
One question at a time, infer everything already answered, do technical work silently, surface only the next decision the person must make.
