// Presenter mode for a lesson: the chapter as an e-book the speaker drives. Each beat is a page; every narration mark is
// a step on it. Nothing moves until the presenter clicks or presses a key, and the narration stays silent unless asked
// for. Loaded after boot() when the page sets window.PRESENT or its address has "present" in the query or hash.
//   → Space PageDown, or a click on the picture   next step, then the next page
//   ← PageUp                                      one step back
//   Home / End                                    first / last page
// On a question page the arrows and digits belong to the question, so only PageDown / PageUp and the buttons turn it.
(() => {
  'use strict';
  const AR = /^ar/.test(navigator.language || '');
  const L = AR
    ? { prev: 'السابق', next: 'التالي', pages: 'الصفحات', voice: 'تشغيل الصفحة بالصوت', stop: 'إيقاف الصوت', full: 'ملء الشاشة', hint: 'اضغط على الصورة أو السهم ← → للتنقل' }
    : { prev: 'Back', next: 'Next', pages: 'Pages', voice: 'Play this page with narration', stop: 'Stop narration', full: 'Full screen', hint: 'Click the picture or press ← → to move' };
  const $id = id => document.getElementById(id);
  const frameEl = $id('frame'), stage = $id('stage');
  // the step times of beat i on its own clock: the opening picture, a little after each mark, the last frame
  function steps(i) {
    const b = BEATS[i], tm = TIMINGS[b.id] || { dur: b.dur || 1, marks: {} }, pre = b.pre || 0;
    const end = pre + tm.dur + .5;
    if (b.ask) return [Math.min(1, end)];
    const ms = Object.values(tm.marks).map(t => t + pre).sort((a, c) => a - c);
    const out = [Math.min(1.2, ms.length ? Math.max(.5, ms[0] - .08) : end)];
    ms.forEach((t, k) => out.push(k < ms.length - 1 ? Math.min(t + 1.3, ms[k + 1] - .08) : end));
    if (!ms.length) out.push(end);
    return out.filter((t, k) => !k || t - out[k - 1] > .3 || k === out.length - 1).map((t, k, a) => k === a.length - 1 ? end : t);
  }
  let page = 0, step = 0, anim = 0, voiced = false;
  const stopAnim = () => { if (anim) cancelAnimationFrame(anim); anim = 0; };
  const drawAt = t => { P.t = t; evalTo(t); };
  // run the beat clock from where it is to t, in under a second
  function runTo(t) {
    stopAnim();
    const from = P.t, wall = Math.min(.9, Math.max(.25, (t - from) / 4)), t0 = performance.now();   // quick: the presenter is talking
    const f = now => {
      const q = Math.min(1, (now - t0) / (wall * 1000));
      drawAt(from + (t - from) * q);
      anim = q < 1 ? requestAnimationFrame(f) : 0;
    };
    anim = requestAnimationFrame(f);
  }
  function open(i, s, animate) {            // page i at its step s
    stopAnim(); voiced = false;
    page = Math.max(0, Math.min(BEATS.length - 1, i));
    const st = steps(page);
    step = Math.max(0, Math.min(st.length - 1, s));
    seek(page, false);
    if (animate) runTo(st[step]); else drawAt(st[step]);
    paint();
  }
  function next() {
    if (voiced) return open(page, steps(page).length - 1, false);
    const st = steps(page);
    if (anim) { stopAnim(); drawAt(st[step]); return; }           // a click during a move finishes it
    if (step < st.length - 1) { step++; runTo(st[step]); paint(); }
    else if (page < BEATS.length - 1) open(page + 1, 0, true);
  }
  function prev() {
    if (voiced || anim) return open(page, step, false);
    if (step > 0) open(page, step - 1, false);
    else if (page > 0) open(page - 1, steps(page - 1).length - 1, false);
  }
  function voice() {                         // hand this page to the engine's own playback, with its narration
    if (voiced) return open(page, step, false);
    stopAnim(); seek(page, true); setPlaying(true); voiced = true; paint();
  }

  /* ---------- the presenter's bar, in place of the player's ---------- */
  const css = document.createElement('style');
  css.textContent = `
#bar, .paused-mark { display: none !important; }
#pbar { position: absolute; left: 0; top: var(--sh, 900px); width: var(--sw, 1600px); height: 60px; display: flex; align-items: center; gap: 12px;
  padding: 0 20px; background: var(--board); border-top: 1px solid var(--bar-edge); font: 600 20px/1 var(--ui); color: var(--chalk); }
#pbar button { height: 42px; min-width: 46px; padding: 0 14px; border-radius: 21px; border: 1.5px solid var(--edge); background: var(--panel); color: var(--chalk); font: inherit; }
#pbar button:hover { background: var(--hover); }
#pbar button.go { background: var(--task); border-color: var(--task); color: #fff; }
#pbar button[disabled] { opacity: .35; cursor: default; }
#pbar .where { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; }
#pbar .where b { color: var(--task); }
#pbar .dots { display: inline-flex; gap: 5px; margin-inline-start: 12px; vertical-align: middle; }
#pbar .dots i { width: 9px; height: 9px; border-radius: 50%; background: var(--faint); }
#pbar .dots i.on { background: var(--task); }
#ptoc { position: absolute; left: 20px; bottom: 70px; width: 460px; max-height: 760px; overflow: auto; padding: 10px; border-radius: 14px;
  background: var(--panel); border: 1.5px solid var(--edge); box-shadow: 0 16px 50px rgba(60, 50, 30, .25); font: 500 22px/1.2 var(--ui); z-index: 30; }
#ptoc[hidden] { display: none; }
#ptoc button { display: flex; gap: 12px; width: 100%; padding: 10px 12px; border: 0; border-radius: 9px; background: none; color: var(--chalk); font: inherit; text-align: start; }
#ptoc button:hover, #ptoc button.on { background: var(--hover); }
#ptoc button span { color: var(--dim); min-width: 28px; }
#ptoc button.q em { font-style: normal; color: var(--quiz); margin-inline-start: auto; font-size: 18px; }
#phint { position: absolute; left: 0; right: 0; top: calc(var(--sh, 900px) - 54px); text-align: center; font: 500 20px/1 var(--ui); color: var(--dim); pointer-events: none; transition: opacity .4s; }`;
  document.head.append(css);
  const el = (tag, props = {}, kids = []) => { const e = Object.assign(document.createElement(tag), props); e.append(...kids); return e; };
  const bPages = el('button', { textContent: '☰', title: L.pages }), bPrev = el('button', { textContent: '◀', title: L.prev });
  const bNext = el('button', { className: 'go', textContent: '▶', title: L.next }), where = el('div', { className: 'where' });
  const bVoice = el('button', { textContent: '🔊', title: L.voice }), bFull = el('button', { textContent: '⛶', title: L.full });
  [bPages, bPrev, bNext, bVoice, bFull].forEach(b => b.setAttribute('aria-label', b.title));
  const pbar = el('div', { id: 'pbar' }, [bPages, bPrev, where, bVoice, bFull, bNext]);
  const toc = el('div', { id: 'ptoc', hidden: true }), hint = el('div', { id: 'phint', textContent: L.hint });
  BEATS.forEach((b, i) => {
    const r = el('button', { className: b.ask ? 'q' : '' }, [el('span', { textContent: String(i + 1) }), b.title, ...(b.ask && i < BEATS.length - 1 ? [el('em', { textContent: '?' })] : [])]);
    r.onclick = () => { toc.hidden = true; open(i, 0, false); };
    toc.append(r);
  });
  frameEl.append(pbar, toc, hint);
  function paint() {
    const st = steps(page), dots = el('span', { className: 'dots' });
    if (st.length > 1) st.forEach((_, k) => dots.append(el('i', { className: k <= step ? 'on' : '' })));
    where.replaceChildren(el('b', { textContent: `${page + 1} / ${BEATS.length}` }), `  ${BEATS[page].title}`, dots);
    bPrev.disabled = !page && !step;
    bNext.disabled = page === BEATS.length - 1 && step === st.length - 1;
    bVoice.textContent = voiced ? '⏸' : '🔊'; bVoice.title = voiced ? L.stop : L.voice;
    [...toc.children].forEach((r, i) => r.classList.toggle('on', i === page));
    if (page || step) hint.style.opacity = 0;
  }
  bPrev.onclick = prev; bNext.onclick = next; bVoice.onclick = voice;
  bPages.onclick = () => { toc.hidden = !toc.hidden; };
  bFull.onclick = () => { (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen())?.catch?.(() => {}); };
  stage.addEventListener('click', () => { toc.hidden = true; if (!BEATS[page].ask) next(); });
  // ahead of the engine's own keys, which would play, pause and step whole beats
  window.addEventListener('keydown', e => {
    if (e.altKey || e.metaKey || e.ctrlKey || e.target.matches?.('input, textarea')) return;
    const ask = !!BEATS[page].ask, k = e.key;
    const act = k === 'PageDown' ? next : k === 'PageUp' ? prev
      : k === 'Home' ? () => open(0, 0, false) : k === 'End' ? () => open(BEATS.length - 1, 0, false)
      : ask ? null : k === 'ArrowRight' || k === ' ' ? next : k === 'ArrowLeft' ? prev : null;
    if (k === 'Escape' && !toc.hidden) { toc.hidden = true; return; }
    if (!act || (k === ' ' && e.target.closest?.('button'))) return;
    e.preventDefault(); e.stopImmediatePropagation(); act();
  }, true);
  // the engine moved on by itself (narrated playback reached the next page, or a question was continued): follow it
  setInterval(() => {
    if (P.i !== page && !anim) { page = P.i; step = voiced ? steps(page).length - 1 : 0; if (!voiced) { setPlaying(false); open(page, 0, true); } else paint(); }
  }, 200);
  hideCover(); setPlaying(false);
  open(0, 0, false);
})();
