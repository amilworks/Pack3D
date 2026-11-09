const DATA = {"repack":{"seeds":[13,29,41,53,67,83],"ax0":[0.8232041876661003,0.8233935994406542,0.8219183080748164,0.8238790235613092,0.8301391905794541,0.8255466957887013],"ax1":[0.8232724456635336,0.8233549147844315,0.8223302837069276,0.823957710136404,0.8301796226451794,0.8256099889365335],"pk0":[0.8253415346145629,0.8195828790465991,0.825005172441403,0.8185641605406999,0.8264244556427002,0.8223262195204751],"pk1":[0.7731130219375094,0.7535358890270193,0.7723392908771832,0.7799754473112029,0.7801123619700472,0.7906655114804761],"chg_ax":[0.0059668223063151045,0.008325576782226562,0.0075499216715494795,0.006144841512044271,0.0062719980875651045,0.00698089599609375],"chg_pk":[1.1211490631103516,1.2609418233235676,1.41387939453125,1.150795618693034,1.2623087565104167,1.1498578389485676],"gap_training":-0.001806097217432523},"named":{"ax0":0.8228386983938569,"ax1":0.8223233485636666,"pk0":0.8233098620341883,"pk1":0.744521283565296},"msd":{"heart_ax":[0.00324249267578125,0.0045299530029296875,0.0034809112548828125],"heart_pk":[0.08459091186523438,0.11553764343261719,0.10709762573242188],"heart_sep":[0.00362396240234375,0.002288818359375,0.003814697265625],"spleen_ax":[0.0045299530029296875,0.007987022399902344,0.002765655517578125],"spleen_pk":[0.3493309020996094,0.3667116165161133,0.23906230926513672],"spleen_sep":[0.0027894973754882812,0.0035047531127929688,0.003981590270996094]},"msd_named_spleen":0.0020692323644955954,"interv":[["zero",-0.009365088338912808],["swap",-0.015739486108038398],["perm",0.00014089652233654584]],"probes":{"tb":0.9996744791666666,"sc":0.5,"un":0.5,"full":1.0,"loc":0.5,"zero":0.5,"flip":0.0},"unet":{"seeds":[13,29,41,53,67,83],"pack":[0.8232041876661003,0.8233935994406542,0.8219183080748164,0.8238790235613092,0.8301391905794541,0.8255466957887013],"unet":[0.8172108811055677,0.8107680829062366,0.8122415966485246,0.8174004382804092,0.8179785210639239,0.8161599975739973],"best_mean":0.009386914588729348,"final_mean":0.00960221888176536,"ci":[0.0064846530910970665,0.012289176086361629],"p_best":0.03125,"p_final":0.0625,"params_pack":30081234,"params_unet":31867394,"structures":[{"name":"CETN2","d":-0.03665039502084255,"holm":false},{"name":"NUP153","d":-0.0037632609407107034,"holm":false},{"name":"ACTN1","d":0.001855120062828064,"holm":false},{"name":"HIST1H2BJ","d":0.003941800445318222,"holm":false},{"name":"MYH10","d":0.004043251276016235,"holm":false},{"name":"FBL","d":0.004296741137901942,"holm":false},{"name":"NPM1","d":0.0058793798089027405,"holm":false},{"name":"TUBA1B","d":0.005880969266096751,"holm":false},{"name":"TOMM20","d":0.009293404718240103,"holm":false},{"name":"LMNB1","d":0.011992927640676498,"holm":false},{"name":"DSP","d":0.016795318465230524,"holm":false},{"name":"LAMP1","d":0.02065400779247284,"holm":false},{"name":"ATP2A2","d":0.02457561468084653,"holm":true},{"name":"SEC61B","d":0.03210276861985525,"holm":true},{"name":"AAVS1","d":0.039906070878108345,"holm":false}]},"systems":[{"n":65536,"grid":"16x64x64","m":256,"dense":103.83390426635742,"window":13.86403226852417,"pack":16.144015312194824,"speedup":6.4317273155658885,"gb_dense":1.1911659240722656,"gb_window":2.042217254638672,"gb_pack":1.4471940994262695},{"n":131072,"grid":"32x64x64","m":512,"dense":406.1379852294922,"window":26.676688194274902,"pack":29.02284812927246,"speedup":13.99373291761332,"gb_dense":2.3195838928222656,"gb_window":4.021686553955078,"gb_pack":2.8237967491149902},{"n":262144,"grid":"32x128x64","m":1024,"dense":1630.2820434570312,"window":52.62824058532715,"pack":56.35273551940918,"speedup":28.929953948651253,"gb_dense":4.574466705322266,"gb_window":7.978672027587891,"gb_pack":5.57944393157959},{"n":524288,"grid":"64x128x64","m":2048,"dense":6709.878173828125,"window":104.47785568237305,"pack":113.14481353759766,"speedup":59.303453371271445,"gb_dense":9.084232330322266,"gb_window":15.893131256103516,"gb_pack":11.088296890258789},{"n":1048576,"grid":"64x128x128","m":4096,"dense":27245.685546875,"window":208.15438079833984,"pack":273.64959716796875,"speedup":99.5641354083607,"gb_dense":18.103763580322266,"gb_window":31.721561431884766,"gb_pack":22.111373901367188}]};
(() => {
'use strict';
const D = DATA;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
const RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
// say "tap" where nothing can hover
const HOVERLESS = window.matchMedia('(hover: none)').matches;
const MINUS = '−';
const tok = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const isDark = () => {
  const t = document.documentElement.getAttribute('data-theme');
  if (t === 'dark' || t === 'light') return t === 'dark';
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};
const sgn = (v, d) => (v < 0 ? MINUS : '+') + Math.abs(v).toFixed(d);
const fix = (v, d) => (v < 0 ? MINUS : '') + Math.abs(v).toFixed(d);
const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;
const intf = (v) => Math.round(v).toLocaleString('en-US');
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
// easeOut answers the reader, as --ease does; ease is for motion nobody asked for
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const easeOut = (t) => 1 - Math.pow(1 - t, 5);
// a --t-* token in seconds (written in s or ms), or d
const seconds = (n, d) => { const v = tok(n), x = parseFloat(v); return isFinite(x) ? (/ms$/.test(v) ? x / 1000 : x) : d; };
// a d3 move that answers the reader (made late: d3 loads after this file)
const answer = (sel) => sel.transition().duration(seconds('--t-3', 0.4) * 1000).ease(d3.easePolyOut.exponent(5));

// ====================================================================== color (OKLab)
function hex2rgb(h) {
  h = h.replace('#', '');
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
}
const toLin = (c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
const toGam = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055);
function rgb2lab(rgb) {
  const [r, g, b] = rgb.map(toLin);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
          1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
          0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s];
}
function lab2rgb(lab) {
  const [L, a, b] = lab;
  const l = Math.pow(L + 0.3963377774 * a + 0.2158037573 * b, 3);
  const m = Math.pow(L - 0.1055613458 * a - 0.0638541728 * b, 3);
  const s = Math.pow(L - 0.0894841775 * a - 1.291485548 * b, 3);
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
          -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
          -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s].map((c) => clamp(toGam(clamp(c, 0, 1)), 0, 1));
}
const lab = (hex) => rgb2lab(hex2rgb(hex));
const mixLab = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const css = (labv) => { const c = lab2rgb(labv); return `rgb(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)})`; };
function ramp(hexes) {
  const L = hexes.map(lab);
  return (t) => {
    t = clamp(t, 0, 1);
    const x = t * (L.length - 1), i = Math.min(L.length - 2, Math.floor(x));
    return mixLab(L[i], L[i + 1], x - i);
  };
}
const RAMPS = {
  geo: () => ramp(isDark() ? ['#0C3B32', '#0D6B58', '#18A385', '#62D7BC', '#C6F4E9'] : ['#E2F6F0', '#9DE2D0', '#3DC6A6', '#009078', '#00493A']),
  // memory order (--mem-0 to --mem-4): the opening and the end
  mem: () => ramp([0, 1, 2, 3, 4].map((i) => tok('--mem-' + i))),
};
// "r,g,b", for a canvas color with an alpha of its own
const rgbOf = (hex) => hex2rgb(hex).map((c) => Math.round(c * 255)).join(',');

// ====================================================================== storage orders
// slot[v] = memory slot of the token at voxel v = (z*N + y)*N + x
function makeLayouts(N, B, perm) {
  const n = N * N * N, bits = Math.log2(N), nb = N / B;
  const raster = new Int32Array(n), morton = new Int32Array(n), blocks = new Int32Array(n), repack = new Int32Array(n);
  const pos = new Int32Array(N);
  perm.forEach((g, i) => { pos[g] = i; });            // perm lists the z-groups in their new memory order
  for (let z = 0; z < N; z++) for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const v = (z * N + y) * N + x;
    raster[v] = v;
    let m = 0;
    for (let b = 0; b < bits; b++) m |= (((x >> b) & 1) << (3 * b)) | (((y >> b) & 1) << (3 * b + 1)) | (((z >> b) & 1) << (3 * b + 2));
    morton[v] = m;
    const bz = Math.floor(z / B), by = Math.floor(y / B), bx = Math.floor(x / B);
    blocks[v] = ((bz * nb + by) * nb + bx) * B * B * B + ((z % B) * B + (y % B)) * B + (x % B);
    repack[v] = pos[z] * N * N + y * N + x;
  }
  const out = { raster, morton, blocks, repack };
  for (const k in out) {                             // sanity: each order is a bijection
    const seen = new Uint8Array(n);
    out[k].forEach((s) => { seen[s] = 1; });
    if (seen.reduce((a, b) => a + b, 0) !== n) throw new Error('layout ' + k + ' is not a permutation');
  }
  return out;
}
const LAYOUT_NAMES = { raster: 'raster order', morton: 'Morton order', blocks: 'block-contiguous order', repack: 'repacked: whole layers moved' };

// ====================================================================== tooltip
// tipOff undoes whatever marked a tapped item once its tip goes
const tip = $('#tip');
let lastPointer = 'mouse', tapped = false, tipOff = null, tipT = 0, restT = 0, onTip = false;
// touch or pen, from the pointer that began the gesture: Safari reports a tap's click as pointerType 'mouse'
const byFinger = () => lastPointer !== 'mouse';
function showTip(html, ev, above) {
  clearTimeout(tipT); clearTimeout(restT);
  tip.innerHTML = html;
  tip.classList.add('on');
  tip.classList.remove('hover');
  tip.style.maxWidth = '';
  tip.style.left = '0px'; tip.style.top = '0px';           // measure at full width, not squeezed by an edge
  let r = tip.getBoundingClientRect();
  const vw = window.innerWidth, vh = window.innerHeight;
  let x = ev.clientX + 14, y = ev.clientY + 14;
  if (above) {
    const bar = $('.topbar'), ceil = (bar ? bar.getBoundingClientRect().bottom : 0) + 8;
    x = ev.clientX - r.width / 2; y = ev.clientY - r.height - 24;
    if (y < ceil) {
      // no room above: beside the finger, on the roomier side, narrowed to fit
      const right = ev.clientX < vw / 2, room = (right ? vw - ev.clientX : ev.clientX) - 28 - 8;
      if (room < r.width) { tip.style.maxWidth = Math.max(120, room) + 'px'; r = tip.getBoundingClientRect(); }
      x = right ? ev.clientX + 28 : ev.clientX - 28 - r.width;
      y = clamp(ev.clientY - r.height / 2, ceil, vh - r.height - 8);
    }
  } else {
    if (x + r.width > vw - 8) x = ev.clientX - r.width - 14;
    if (y + r.height > vh - 8) y = ev.clientY - r.height - 14;
  }
  tip.style.left = Math.max(8, Math.min(x, vw - r.width - 8)) + 'px';
  tip.style.top = Math.max(8, y) + 'px';
}
function hideTip() {
  clearTimeout(tipT); clearTimeout(restT);
  tip.classList.remove('on', 'hover');
  tapped = false; onTip = false;
  if (tipOff) { const f = tipOff; tipOff = null; f(); }
}
function tapTip(html, ev, off) { hideTip(); showTip(html, ev, true); tapped = true; tipOff = off || null; }
// WCAG 1.4.13: after 0.4s at rest the tip takes the pointer, so a mouse can move onto it
function hoverTip(html, ev) {
  showTip(html, ev);
  restT = setTimeout(() => { if (tip.classList.contains('on')) tip.classList.add('hover'); }, 400);
}
function leaveTip() { clearTimeout(tipT); tipT = setTimeout(hideTip, 300); }
tip.addEventListener('pointerenter', () => { if (tip.classList.contains('hover')) { clearTimeout(tipT); onTip = true; } });
tip.addEventListener('pointerleave', () => { if (onTip) { onTip = false; leaveTip(); } });
const closeTip = () => { hideTip(); tip.classList.remove('on-dark'); };
document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && tip.classList.contains('on')) closeTip(); });
document.addEventListener('pointerdown', (ev) => { lastPointer = ev.pointerType; if (tapped) hideTip(); }, { capture: true, passive: true });
// a scroll carries every mark away from its tip
window.addEventListener('scroll', () => { if (tip.classList.contains('on')) closeTip(); }, { passive: true });
document.addEventListener('touchstart', () => {}, { passive: true });   // iOS shows :active only with a touch listener

// ====================================================================== canvas helper
// null without a 2D context: the caller skips drawing
function canvasScale(cssW, cssH, budget = 4e6) {
  return Math.max(1, Math.min(window.devicePixelRatio || 1, 3, Math.sqrt(budget / Math.max(1, cssW * cssH))));
}
function fitCanvas(canvas, cssW, cssH, budget) {
  const s = canvasScale(cssW, cssH, budget);
  const w = Math.max(1, Math.round(cssW * s)), h = Math.max(1, Math.round(cssH * s));
  if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.setTransform(cssW ? w / cssW : 1, 0, 0, cssH ? h / cssH : 1, 0, 0);
  return ctx;
}

// ====================================================================== motion: one switch for every figure that moves on its own
const motion = (() => {
  let paused = RM;
  try { if (!RM && localStorage.getItem('pack3d-motion') === 'paused') paused = true; } catch (e) { /* storage blocked */ }
  const cbs = [];
  const label = () => $$('[data-motion]').forEach((b) => { b.textContent = paused ? 'Play motion' : 'Pause motion'; });
  const api = {
    get paused() { return paused; },
    set(p) {
      p = !!p;
      if (p === paused) return;
      paused = p;
      try { localStorage.setItem('pack3d-motion', p ? 'paused' : 'on'); } catch (e) { /* storage blocked */ }
      label();
      cbs.forEach((f) => f(p));
    },
    on(cb) { cbs.push(cb); },
  };
  document.addEventListener('click', (ev) => { if (ev.target.closest('[data-motion]')) api.set(!paused); });
  label();
  return api;
})();

// ====================================================================== the opening: paths through memory
function hilbert3(x, y, z, bits) {                      // Skilling's transpose, then its bits interleaved
  const X = [x, y, z], M = 1 << (bits - 1);
  for (let Q = M; Q > 1; Q >>= 1) {
    const P = Q - 1;
    for (let i = 0; i < 3; i++) {
      if (X[i] & Q) X[0] ^= P;
      else { const t = (X[0] ^ X[i]) & P; X[0] ^= t; X[i] ^= t; }
    }
  }
  for (let i = 1; i < 3; i++) X[i] ^= X[i - 1];
  let t = 0;
  for (let Q = M; Q > 1; Q >>= 1) if (X[2] & Q) t ^= Q - 1;
  for (let i = 0; i < 3; i++) X[i] ^= t;
  let h = 0;
  for (let b = bits - 1; b >= 0; b--) for (let i = 0; i < 3; i++) h = (h << 1) | ((X[i] >> b) & 1);
  return h;
}
function initPaths() {
  const hero = $('#hero'), canvas = $('#heroCanvas'), field = $('#heroField');
  if (!hero || !canvas || !field) return;
  const g = canvas.getContext('2d');
  if (!g) { hero.classList.add('no-canvas'); return; }
  const N = 8, NT = N * N * N;
  const L = makeLayouts(N, 4, [5, 2, 7, 0, 3, 6, 1, 4]);
  const hil = new Int32Array(NT);
  for (let v = 0; v < NT; v++) hil[v] = hilbert3(v % N, Math.floor(v / N) % N, Math.floor(v / (N * N)), 3);
  const SLOTS = { raster: L.raster, morton: L.morton, hilbert: hil, blocks: L.blocks, repack: L.repack };
  const ORDERS = ['raster', 'morton', 'hilbert', 'blocks', 'repack'];
  const NAME = { raster: 'Raster order', morton: 'Morton order', hilbert: 'Hilbert order', blocks: '4 × 4 × 4 blocks', repack: 'Repacked: whole layers moved' };
  const path = {};                                     // path[o][i]: the token at memory position i, centered
  for (const o of ORDERS) {
    const p = new Array(NT);
    SLOTS[o].forEach((s, v) => { p[s] = [v % N - 3.5, Math.floor(v / N) % N - 3.5, Math.floor(v / (N * N)) - 3.5]; });
    if (p.some((q) => !q)) throw new Error('order ' + o + ' is not a permutation');
    path[o] = p;
  }
  const rampF = RAMPS.mem();
  const COL = Array.from({ length: NT }, (_, i) => lab2rgb(rampF(i / (NT - 1))).map((c) => Math.round(c * 255)));
  // the head glows in the stage's mint; its core is a near-white mint that no token names
  const MINT = tok('--stage-mint'), MINT3 = hex2rgb(MINT).map((c) => Math.round(c * 255)), CORE = '#C9FFF1';
  // kept: building some 1,500 color strings a frame cost more than the drawing (alpha in steps of 1/64)
  const RGBA = new Array(NT * 65);
  const rgba = (i, a) => {
    const q = a <= 0 ? 0 : a >= 1 ? 64 : Math.round(a * 64), k = i * 65 + q;
    return RGBA[k] || (RGBA[k] = `rgba(${COL[i][0]},${COL[i][1]},${COL[i][2]},${q / 64})`);
  };
  const P = new Float32Array(NT * 3), S = new Float32Array(NT * 3);
  // settled: the path once a morph ends, so a still path is not interpolated every frame
  let from = path.raster, to = path.raster, settled = path.raster, cur = 'raster', t0 = 0, auto = !RM, switchedAt = performance.now(), curve = ease;
  for (let i = 0; i < NT; i++) P.set(path.raster[i], i * 3);
  const buttons = $$('#heroOrders [data-order]'), cap = $('#heroOrder');
  function setOrder(o, byHand) {
    if (byHand) auto = false;
    if (o === cur) return;
    const snap = []; for (let i = 0; i < NT; i++) snap.push([P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]);
    from = snap; to = path[o]; settled = null; cur = o; t0 = performance.now(); switchedAt = t0; curve = byHand ? easeOut : ease;
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.order === o)));
    cap.textContent = NAME[o];
    kick();
  }
  buttons.forEach((b) => b.addEventListener('click', () => setOrder(b.dataset.order, true)));
  // the cycle stops once the keyboard is in the tray, so the choice never changes under focus
  if (buttons.length) buttons[0].parentElement.addEventListener('focusin', () => { auto = false; });

  // a turn by hand pauses motion everywhere, so the view the reader chose stays put
  let yaw = 0.7, pitch = 0.36, drag = null;
  canvas.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 || !e.isPrimary) return;            // a right-click or a second finger turns nothing
    drag = { x: e.clientX, y: e.clientY, yaw, pitch, on: false };
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', (e) => {
    if (!drag || !e.isPrimary) return;
    if (e.pointerType === 'mouse' && !(e.buttons & 1)) { endDrag(); return; }   // the button came up where the page could not see it
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.on) {
      // a turn starts once the press moves, a finger's only sideways: one going up is a scroll (pointercancel), and a
      // scroll must not stop the opening
      if (e.pointerType === 'mouse' ? Math.hypot(dx, dy) < 4 : Math.abs(dx) < 10 || Math.abs(dx) < Math.abs(dy)) return;
      Object.assign(drag, { x: e.clientX, y: e.clientY, yaw, pitch, on: true });
      canvas.classList.add('grabbing');
      motion.set(true);
      return;
    }
    yaw = drag.yaw + dx * 0.008;
    pitch = clamp(drag.pitch + dy * 0.006, -1.2, 1.2);
    kick();
  });
  const endDrag = () => { drag = null; canvas.classList.remove('grabbing'); };
  canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);
  canvas.addEventListener('lostpointercapture', endDrag);
  const TURN = { ArrowLeft: [-0.2, 0], ArrowRight: [0.2, 0], ArrowUp: [0, -0.15], ArrowDown: [0, 0.15] };   // as a drag that way
  canvas.addEventListener('keydown', (e) => {
    const t = TURN[e.key];
    if (!t || e.altKey || e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    yaw += t[0]; pitch = clamp(pitch + t[1], -1.2, 1.2);
    motion.set(true);
    kick();
  });

  // whole pixels, so the bitmap lands 1:1 (a fractional size is resampled and goes soft); a budget for a 2x screen
  let W = 0, H = 0, CX = 0, CY = 0, SC = 1;
  const resize = () => {
    const st = canvas.style;
    st.width = st.height = '';
    const cr = canvas.getBoundingClientRect(), fr = field.getBoundingClientRect();
    W = Math.round(cr.width); H = Math.round(cr.height);
    Object.assign(st, { width: W + 'px', height: H + 'px' });          // CSS anchors it by its top right corner
    CX = fr.left + fr.width / 2 - (cr.right - W); CY = fr.top + fr.height / 2 - cr.top; SC = Math.min(fr.width, fr.height) / 12.6;
    const ctx = fitCanvas(canvas, W, H, Math.max(4e6, W * H * Math.min(window.devicePixelRatio || 1, 2) ** 2));
    hero.classList.toggle('no-canvas', !ctx);
    if (!ctx) return;
    draw();          // at once: a resized canvas is blank, and this frame's rAF has already run
    kick();
  };
  // paused or reduced: a still frame, the head parked past the end
  let visible = true, raf = 0, last = 0, head = motion.paused ? NT + 46 : 0;
  function kick() { if (!raf && visible) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0;
    const dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
    const run = !motion.paused;
    if (run && auto && now - switchedAt > 5200) setOrder(ORDERS[(ORDERS.indexOf(cur) + 1) % ORDERS.length]);
    const m = RM ? 1 : clamp((now - t0) / 1700, 0, 1);     // a frame may be stamped a moment before the press
    if (settled !== to) {
      const e = curve(m);
      for (let i = 0; i < NT; i++) for (let k = 0; k < 3; k++) P[i * 3 + k] = from[i][k] + (to[i][k] - from[i][k]) * e;
      if (m >= 1) settled = to;
    }
    if (run && !drag) yaw += 0.09 * dt;
    if (run) head = (head + dt * 70) % (NT + 120);
    draw();
    if (run || settled !== to) kick();      // kick() never queues a second frame: setOrder() above may already have queued one
  }
  function draw() {
    const cx = CX, cy = CY, sc = SC;
    const cyw = Math.cos(yaw), syw = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch), Dv = 26;
    for (let i = 0; i < NT; i++) {
      const x = P[i * 3], y = P[i * 3 + 2], z = P[i * 3 + 1];          // layers run up the screen
      const x1 = x * cyw + z * syw, z1 = -x * syw + z * cyw;
      const y2 = y * cp - z1 * sp, z2 = y * sp + z1 * cp, f = Dv / (Dv - z2);
      S[i * 3] = cx + x1 * sc * f; S[i * 3 + 1] = cy - y2 * sc * f; S[i * 3 + 2] = z2;
    }
    g.clearRect(0, 0, W, H);
    g.globalCompositeOperation = 'lighter'; g.lineCap = 'round'; g.lineJoin = 'round';
    const k = Math.max(0.7, Math.min(1.25, sc / 34));
    for (let pass = 0; pass < 2; pass++) {
      for (let i = 1; i < NT; i++) {
        const a = i * 3 - 3, b = i * 3, near = ((S[a + 2] + S[b + 2]) / 2 + 7) / 14;
        const hd = head - i, lit = hd >= 0 && hd < 46 ? 1 - hd / 46 : 0, c = COL[i];
        if (pass === 0) { g.lineWidth = 7 * k * (0.7 + 0.5 * near); g.strokeStyle = rgba(i, 0.045 + 0.05 * near + 0.12 * lit); }
        else {
          g.lineWidth = k * (1.5 * (0.75 + 0.5 * near) + 1.4 * lit);
          g.strokeStyle = lit > 0
            ? `rgba(${Math.round(c[0] + (MINT3[0] - c[0]) * lit)},${Math.round(c[1] + (MINT3[1] - c[1]) * lit)},${Math.round(c[2] + (MINT3[2] - c[2]) * lit)},${0.5 + 0.5 * lit})`
            : rgba(i, 0.32 + 0.5 * near);
        }
        g.beginPath(); g.moveTo(S[a], S[a + 1]); g.lineTo(S[b], S[b + 1]); g.stroke();
      }
    }
    for (let i = 0; i < NT; i++) {
      const near = (S[i * 3 + 2] + 7) / 14;
      g.fillStyle = rgba(i, 0.18 + 0.4 * near);
      g.beginPath(); g.arc(S[i * 3], S[i * 3 + 1], k * (1.3 + 1.2 * near), 0, Math.PI * 2); g.fill();
    }
    const hi = Math.floor(head);
    if (hi < NT) {
      g.shadowColor = MINT; g.shadowBlur = 18; g.fillStyle = CORE;
      g.beginPath(); g.arc(S[hi * 3], S[hi * 3 + 1], 3.6 * k, 0, Math.PI * 2); g.fill(); g.shadowBlur = 0;
    }
    g.globalCompositeOperation = 'source-over';
  }
  const heroRO = new ResizeObserver(resize); heroRO.observe(hero); heroRO.observe(field);
  canvas.addEventListener('contextrestored', resize);   // a restored context comes back blank, its transform reset
  onDpr(resize);
  resize();
  motion.on((paused) => { if (!paused) { last = 0; switchedAt = performance.now(); kick(); } });
  // stacked and sideways the CSS reorders the opening: move the parts in the page too, so Tab and a screen reader
  // meet them as seen
  const stacked = window.matchMedia('(max-width: 920px), (orientation: landscape) and (max-height: 500px), (max-width: 1100px) and (max-aspect-ratio: 4/5)');
  const phone = window.matchMedia('(max-width: 560px)');
  const byline = $('.hero-byline', hero), foot = $('.hero-foot', hero), capP = $('.hero-cap', hero), ctl = $('.hero-ctl', hero);
  // a moved element loses focus: give it back
  const move = (el, put) => {
    const f = el.contains(document.activeElement) ? document.activeElement : null;
    put();
    if (f && document.activeElement !== f) f.focus({ preventScroll: true });
  };
  const place = () => {
    if (byline && foot && (stacked.matches ? foot.nextElementSibling !== byline : byline.nextElementSibling !== foot)) {
      move(byline, () => (stacked.matches ? foot.after(byline) : foot.before(byline)));
    }
    if (capP && ctl && (phone.matches ? ctl.nextElementSibling !== capP : capP.nextElementSibling !== ctl)) {
      move(ctl, () => (phone.matches ? capP.before(ctl) : capP.after(ctl)));
    }
  };
  place();
  stacked.addEventListener('change', place);
  phone.addEventListener('change', place);
  // runs only while the field shows below the bar
  new IntersectionObserver((es) => {
    visible = es.some((x) => x.isIntersecting);
    if (visible) { last = 0; kick(); }
  }, { rootMargin: '-56px 0px 0px 0px' }).observe(field);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { last = 0; kick(); } });
}

// ====================================================================== two readings: the title as a packed sequence
function initReadings() {
  const fig = $('#rdFig'), big = $('#rdBig'), memEl = $('#rdMem'), cv = $('#rdCanvas');
  if (!fig || !big || !memEl || !cv) return;
  const ROWS = ['GEOMETRY', 'MATTERS'], T = [];
  big.querySelectorAll('.rd-row').forEach((rowEl, r) => {
    rowEl.textContent = '';
    [...ROWS[r]].forEach((ch, c) => {
      const s = document.createElement('span');
      s.className = 'rd-L'; s.textContent = ch;
      rowEl.appendChild(s); T.push({ ch, r, c, el: s });
    });
  });
  const n = T.length;
  // the site's four orders, on the 2 x 8 field of the title
  const KEY = {
    raster: (t) => t.r * 8 + t.c,
    morton: (t) => (t.c & 1) | (t.r << 1) | ((t.c >> 1) << 2),
    blocks: (t) => (t.c >> 2) * 8 + t.r * 4 + (t.c & 3),           // two 2 x 4 blocks, raster inside each
    repack: (t) => (1 - t.r) * 8 + t.c,                             // the two rows trade places, each kept whole
  };
  const ORDERS = ['raster', 'morton', 'blocks', 'repack'];
  const NAME = { raster: 'raster order', morton: 'Morton order', blocks: 'blocks of 2 × 4', repack: 'a repacked order: the rows moved whole' };
  const slot = {};
  for (const o of ORDERS) {
    const s = T.map((t, k) => [KEY[o](t), k]).sort((a, b) => a[0] - b[0]);
    slot[o] = new Int32Array(n); s.forEach(([, k], i) => { slot[o][k] = i; });
  }
  const buttons = $$('#rdOrders [data-order]'), note = $('#rdNote'), seqEl = $('#rdSeq'), oname = $('#rdOrderName'), status = $('#rdStatus');
  const LABEL = {}; buttons.forEach((b) => { LABEL[b.dataset.order] = b.textContent.trim(); });
  const NOTE = note.innerHTML;                         // "point at" for a mouse, "tap" for a finger
  const KEYS = 'Use the arrow keys to read each letter’s two indices.', IDLE = 'No letter picked. ' + KEYS;
  const from = Float32Array.from(slot.raster);         // where each memory letter was drawn when the current change began
  // curve: easeOut for a pick, ease for the cycle
  let cur = 'raster', t0 = 0, auto = !RM, switchedAt = 0, hov = -1, visible = false, raf = 0, waitT = 0, curve = ease;
  const progress = (now) => (RM ? 1 : clamp((now - t0) / 1300, 0, 1));   // a frame may be stamped a moment before the press
  function setOrder(o, byHand) {
    if (byHand) auto = false;
    if (o === cur) return;
    // mid-change, start from where the letters are drawn
    const e = curve(progress(performance.now()));
    for (let k = 0; k < n; k++) from[k] += (slot[cur][k] - from[k]) * e;
    cur = o; t0 = performance.now(); switchedAt = t0; curve = byHand ? easeOut : ease;
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.order === o)));
    oname.textContent = NAME[o];
    const seq = new Array(n); T.forEach((t, k) => { seq[slot[o][k]] = t.ch; });
    seqEl.textContent = seq.join('');
    seqEl.classList.toggle('bad', o !== 'raster');
    // only an order the reader chose is spoken, spelled out; the cycle stays quiet
    if (byHand && status) status.textContent = `${LABEL[o]}. Packed RoPE now reads ${seq.join(' ')}.`;
    if (hov >= 0) say(hov);
    kick();
  }
  buttons.forEach((b) => b.addEventListener('click', () => setOrder(b.dataset.order, true)));
  // as in the opening: the cycle stops once the keyboard is in the tray
  if (buttons.length) buttons[0].parentElement.addEventListener('focusin', () => { auto = false; });
  // the title is a slider over its letters, for the keyboard and assistive tech
  const say = (k) => {
    const t = T[k], i = slot[cur][k];
    note.textContent = `“${t.ch}”\u00A0· coordinate (row\u00A0${t.r}, column\u00A0${t.c})\u00A0· memory position i\u00A0=\u00A0${i}`;
    big.setAttribute('aria-valuenow', String(k));
    big.setAttribute('aria-valuetext', `${t.ch}, letter ${k + 1} of ${n}: coordinate (row ${t.r}, column ${t.c}), memory position ${i}`);
  };
  const pick = (k) => {
    T.forEach((t, j) => t.el.classList.toggle('on', j === k));
    if (hov >= 0 && k < 0) switchedAt = performance.now();   // the cycle waits a full turn after the reader lets go
    hov = k;
    if (k >= 0) say(k);
    else { note.innerHTML = NOTE; big.setAttribute('aria-valuenow', '0'); big.setAttribute('aria-valuetext', IDLE); }
    kick();
  };
  T.forEach((t, k) => {
    t.el.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') pick(k); });
    t.el.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') pick(-1); });
    // a mouse picked the letter on its way in, so its click keeps it; a tap picks it or lets it go
    t.el.addEventListener('click', () => { auto = false; pick(byFinger() && hov === k ? -1 : k); });
  });
  // the memory row answers too: a slot stands for the letter stored in it
  const atSlot = (e) => {
    const r = memEl.getBoundingClientRect();
    if (e.clientY < r.top || e.clientY > r.bottom) return -1;
    const i = Math.floor((e.clientX - r.left - MX) / SW);
    return i >= 0 && i < n ? slot[cur].indexOf(i) : -1;
  };
  memEl.addEventListener('pointermove', (e) => { if (e.pointerType !== 'mouse') return; const k = atSlot(e); if (k !== hov) pick(k); });
  memEl.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && hov >= 0) pick(-1); });
  memEl.addEventListener('click', (e) => { const k = atSlot(e); if (k < 0) return; auto = false; pick(byFinger() && hov === k ? -1 : k); });
  document.addEventListener('pointerdown', (e) => { if (hov >= 0 && !big.contains(e.target) && !memEl.contains(e.target)) pick(-1); });
  big.removeAttribute('aria-hidden');
  big.tabIndex = 0;
  big.setAttribute('role', 'slider');
  big.setAttribute('aria-label', 'Letters of the title');
  big.setAttribute('aria-valuemin', '0');
  big.setAttribute('aria-valuemax', String(n - 1));
  big.setAttribute('aria-valuenow', '0');
  big.setAttribute('aria-valuetext', IDLE);
  big.addEventListener('keydown', (e) => {
    // Page Up and Page Down move a row, to the same column in the other word
    const d = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1, PageUp: 8, PageDown: -8 }[e.key];
    let k;
    if (d) k = hov < 0 ? (d > 0 ? 0 : n - 1) : clamp(hov + d, 0, n - 1);
    else if (e.key === 'Home') k = 0;
    else if (e.key === 'End') k = n - 1;
    else if (e.key === 'Escape') k = -1;
    else return;
    e.preventDefault();
    auto = false;
    pick(k);
  });
  // the keys are named on the title once it has the keyboard's focus
  const byKeys = () => { try { return big.matches(':focus-visible'); } catch (e) { return true; } };
  big.addEventListener('focus', () => { auto = false; if (hov < 0 && byKeys()) note.textContent = KEYS; });
  big.addEventListener('blur', () => { if (hov >= 0) pick(-1); else note.innerHTML = NOTE; });

  let W = 0, H = 0, ctx = null, SW = 40, MX = 0, MY = 0, col = null;
  function colors() { col = { ink: rgbOf(tok('--ink')), ink3: rgbOf(tok('--ink-3')), lav: rgbOf(tok('--lav')), mint: rgbOf(tok('--mint-ink')), mono: tok('--font-mono') }; }
  // WCAG 1.4.12: under a reader's own letter spacing, a word that would pass the sheet's edge shrinks just enough
  const sheet = $('#readings'), ends = [...big.querySelectorAll('.rd-row')].map((r) => r.lastElementChild).filter(Boolean);
  function fitTitle() {
    if (!sheet || !ends.length) return;
    big.style.fontSize = '';
    const edge = sheet.getBoundingClientRect().right - 4, over = Math.max(...ends.map((el) => el.getBoundingClientRect().right));
    if (over <= edge) return;
    const x0 = big.getBoundingClientRect().left, fs = parseFloat(getComputedStyle(big).fontSize);
    big.style.fontSize = (fs * (edge - x0) / (over - x0)).toFixed(2) + 'px';
  }
  function layout() {
    fitTitle();
    const fr = fig.getBoundingClientRect(), rr = big.querySelector('.rd-row').getBoundingClientRect(), mr = memEl.getBoundingClientRect();
    SW = Math.max(14, rr.width / n);
    MX = rr.left - fr.left; MY = mr.top - fr.top;
    memEl.style.height = Math.round(SW * 1.06 + (SW >= 26 ? 26 : 8)) + 'px';
    W = fig.clientWidth; H = fig.clientHeight;
    ctx = fitCanvas(cv, W, H);
    // paint at once: a resized canvas is blank until drawn
    if (ctx && paint(performance.now()) < 1) kick();
  }
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  // frames only while something moves; a timer waits between the cycle's steps
  function frame(now) {
    raf = 0;
    if (!ctx) return;
    const cycling = auto && !motion.paused && visible && hov < 0;
    if (cycling && now - switchedAt > 4200) setOrder(ORDERS[(ORDERS.indexOf(cur) + 1) % ORDERS.length]);
    const m = paint(now);
    clearTimeout(waitT);
    if (m < 1) kick();
    else if (cycling) waitT = setTimeout(kick, Math.max(0, 4200 - (now - switchedAt)));
  }
  function paint(now) {
    const m = progress(now), e = curve(m);
    const fr = fig.getBoundingClientRect();
    ctx.clearRect(0, 0, W, H);
    const sh = SW * 1.06, r = SW >= 30 ? 6 : SW * 0.2;    // a slot is a mark: --r-xs, or less on a slot too small for it
    ctx.textAlign = 'center';
    for (let i = 0; i < n; i++) {                      // the memory: fifteen slots in a row
      const x = MX + i * SW;
      ctx.fillStyle = `rgba(${col.ink},0.05)`;
      ctx.beginPath(); ctx.roundRect(x + SW * 0.06, MY, SW * 0.88, sh, r); ctx.fill();
      if (SW >= 26) { ctx.fillStyle = `rgba(${col.ink3},1)`; ctx.font = '400 12px ' + col.mono; ctx.fillText(String(i), x + SW / 2, MY + sh + 18); }
    }
    T.forEach((t, k) => {
      const lr = t.el.getBoundingClientRect();
      const sx = lr.left - fr.left + lr.width / 2, sy = lr.top - fr.top + lr.height * 0.84;
      const i = from[k] + (slot[cur][k] - from[k]) * e;
      const ex = MX + i * SW + SW / 2, ey = MY - 3;
      const on = hov === k, dim = hov >= 0 && !on;
      const gr = ctx.createLinearGradient(sx, sy, ex, ey);
      gr.addColorStop(0, on ? `rgba(${col.mint},0.9)` : `rgba(${col.ink},${dim ? 0.04 : 0.14})`);
      gr.addColorStop(1, on ? `rgba(${col.mint},1)` : `rgba(${col.lav},${dim ? 0.18 : 0.85})`);
      ctx.strokeStyle = gr; ctx.lineWidth = on ? 2.2 : 1.4;
      const dy = (ey - sy) * 0.55;
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.bezierCurveTo(sx, sy + dy, ex, ey - dy, ex, ey); ctx.stroke();
      ctx.fillStyle = on ? `rgba(${col.mint},1)` : `rgba(${col.ink},1)`;
      // the memory row's letter: half a slot, and never under 12px (a 12px capital fits the narrowest slot)
      ctx.font = `400 ${Math.max(12, Math.round(SW * 0.5))}px ${col.mono}`; ctx.textBaseline = 'middle';
      ctx.fillText(t.ch, ex, MY + sh * 0.53); ctx.textBaseline = 'alphabetic';
    });
    return m;
  }
  // one column: move the lede in the page too, where the CSS shows it
  const one = window.matchMedia('(max-width: 980px), (orientation: landscape) and (max-height: 500px)');
  const side = $('.rd-side'), panel = $('.rd-panel'), lede = $('.rd-side > .lede');
  const placeLede = () => {
    if (!side || !panel || !lede) return;
    if (one.matches ? panel.nextElementSibling !== lede : side.firstElementChild !== lede) {
      if (one.matches) panel.after(lede); else side.prepend(lede);
    }
  };
  placeLede();
  one.addEventListener('change', placeLede);
  colors();
  // a theme change repaints at once: printing switches to light and takes its picture before any frame runs
  onTheme(() => { colors(); if (ctx) paint(performance.now()); kick(); });
  new ResizeObserver(layout).observe(fig);
  cv.addEventListener('contextrestored', layout);
  onDpr(layout);
  document.fonts.ready.then(layout);
  // Play motion starts the cycle again, soon, from the order on show
  motion.on((paused) => {
    if (!paused && !RM) { auto = true; switchedAt = performance.now() - 3600; }
    clearTimeout(waitT); kick();
  });
  new IntersectionObserver((es) => {
    visible = es.some((x) => x.isIntersecting);
    if (visible) { if (!switchedAt) switchedAt = performance.now(); kick(); } else clearTimeout(waitT);
  }, { threshold: 0.4 }).observe(fig);
}

// ====================================================================== theme changes
// Each callback repaints at once, not on a later frame: a print takes its picture before the next frame.
const themeCbs = [];
function onTheme(cb) { themeCbs.push(cb); }
const themeChanged = () => themeCbs.forEach((f) => { try { f(); } catch (e) { console.error(e); } });
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeChanged);
const themeWatch = new MutationObserver(themeChanged);
themeWatch.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
// set the page's theme ('light', 'dark', or null for the system's), every figure repainted before this returns
function setTheme(t) {
  const h = document.documentElement;
  if (h.getAttribute('data-theme') === t) return;
  if (t === null) h.removeAttribute('data-theme'); else h.setAttribute('data-theme', t);
  themeWatch.takeRecords();
  themeChanged();
}

// ====================================================================== device pixel ratio changes
// a window dragged to a screen of another density keeps its CSS size, so no ResizeObserver fires
const dprCbs = [];
function onDpr(cb) { dprCbs.push(cb); }
(function watchDpr() {
  const mq = window.matchMedia(`(resolution: ${window.devicePixelRatio || 1}dppx)`);
  const f = () => { mq.removeEventListener('change', f); dprCbs.forEach((cb) => cb()); watchDpr(); };
  mq.addEventListener('change', f);
})();

// ====================================================================== the two-indices lab
function initLab() {
  const N = 8, n = 512, NN = 64;
  const L = makeLayouts(N, 2, [3, 6, 0, 5, 1, 7, 2, 4]);
  const inv = {};
  for (const k in L) { inv[k] = new Int32Array(n); L[k].forEach((s, v) => { inv[k][s] = v; }); }
  const vid = (z, y, x) => (z * N + y) * N + x;
  const co = (v) => [Math.floor(v / NN), Math.floor(v / N) % N, v % N];
  const st = { layout: 'raster', mode: 'pair', q: vid(3, 5, 2), t: 1, hover: -1 };
  let geo = RAMPS.geo();
  let colors = [];
  const bakeColors = () => { geo = RAMPS.geo(); colors = Array.from({ length: n }, (_, v) => css(geo(v / (n - 1)))); };
  bakeColors();

  const slicesC = $('#labSlices'), ribbonC = $('#labRibbon');
  let sl = {}, rb = {};
  function k() { const [z, y, x] = co(st.q); return z + 1 < N ? vid(z + 1, y, x) : -1; }
  function offsetsOf(q) {
    const s = L[st.layout][q];
    return [1, -1, 8, -8, 64, -64].map((d) => ({ d, v: s + d >= 0 && s + d < n ? inv[st.layout][s + d] : -1 }));
  }
  function trueNeighbors(q) {
    const [z, y, x] = co(q), out = [];
    [[0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0]].forEach(([a, b, c]) => {
      const zz = z + a, yy = y + b, xx = x + c;
      if (zz >= 0 && zz < N && yy >= 0 && yy < N && xx >= 0 && xx < N) out.push(vid(zz, yy, xx));
    });
    return out;
  }
  function localWindow(q) {
    const [z, y, x] = co(q), out = [];
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
      const zz = z + a, yy = y + b, xx = x + c;
      if (zz >= 0 && zz < N && yy >= 0 && yy < N && xx >= 0 && xx < N) out.push(vid(zz, yy, xx));
    }
    return out;
  }

  // ---- geometry of the two views (mirrored in the stylesheet). printW: a printed column's width while printing
  function layoutViews(printW) {
    const wrap = $('#labSlicesWrap');
    const W = printW || wrap.getBoundingClientRect().width;
    // eight slices in a row once their tokens are big enough to point at: 12px for a mouse, 14px for a finger
    const cols = W >= (HOVERLESS ? 1000 : 880) ? 8 : W >= 560 ? 4 : 2, rows = 8 / cols;
    const gap = W < 560 ? 12 : cols === 8 ? 14 : 18, lab = 18;
    const S = (W - gap * (cols - 1)) / cols;
    const Hs = rows * (S + lab) + (rows - 1) * gap;
    wrap.style.height = printW ? 'auto' : Hs + 'px';
    wrap.style.aspectRatio = printW ? `${W} / ${Hs}` : '';
    sl = { W, H: Hs, cols, gap, lab, S, cell: S / N, ctx: fitCanvas(slicesC, W, Hs) };
    const Wr = printW || ribbonC.getBoundingClientRect().width || W;
    const cw = Wr / 64, rgap = Math.max(2, cw * 0.35);
    const Hr = 8 * cw + 7 * rgap + 22;
    ribbonC.style.height = printW ? 'auto' : Hr + 'px';   // auto: the canvas keeps its own proportions
    rb = { W: Wr, H: Hr, cw, rgap, top: 22, ctx: fitCanvas(ribbonC, Wr, Hr) };
  }
  const sliceXY = (v) => { const [z, y, x] = co(v); const c = z % sl.cols, r = Math.floor(z / sl.cols); return [c * (sl.S + sl.gap) + x * sl.cell, r * (sl.S + sl.lab + sl.gap) + sl.lab + y * sl.cell]; };

  // ---- drawing
  function marks() {
    const q = st.q, kk = k(), M = new Map();
    const add = (v, m) => { if (v < 0) return; M.set(v, Object.assign(M.get(v) || {}, m)); };
    if (st.mode === 'local') localWindow(q).forEach((v) => add(v, { local: true }));
    if (st.mode === 'offsets') {
      trueNeighbors(q).forEach((v) => add(v, { nb: true }));
      offsetsOf(q).forEach((o) => add(o.v, { off: o.d }));
    }
    if (st.mode === 'pair' && kk >= 0) add(kk, { k: true });
    add(q, { q: true });
    return M;
  }
  // the rest fade further in the local window
  const faded = () => (st.mode === 'local' ? 0.3 : 0.55);
  function drawSlices() {
    const c = sl.ctx, M = marks();
    if (!c) return;
    c.clearRect(0, 0, sl.W, sl.H);
    c.font = '400 12px ' + tok('--font-mono');
    c.textBaseline = 'alphabetic';
    for (let z = 0; z < N; z++) {
      const col = z % sl.cols, row = Math.floor(z / sl.cols);
      const x0 = col * (sl.S + sl.gap), y0 = row * (sl.S + sl.lab + sl.gap);
      c.fillStyle = tok('--ink-3');
      c.fillText('z = ' + z, x0, y0 + 12);
    }
    const pad = Math.max(0.6, sl.cell * 0.06);
    for (let v = 0; v < n; v++) {
      const [x, y] = sliceXY(v), m = M.get(v);
      c.fillStyle = colors[v];
      c.globalAlpha = st.mode === 'pair' || m ? 1 : faded();
      c.fillRect(x + pad, y + pad, sl.cell - 2 * pad, sl.cell - 2 * pad);
    }
    c.globalAlpha = 1;
    M.forEach((m, v) => {
      const [x, y] = sliceXY(v), s = sl.cell;
      if (m.local && !m.q) { c.strokeStyle = tok('--ink'); c.lineWidth = 1.5; c.strokeRect(x + pad, y + pad, s - 2 * pad, s - 2 * pad); }
      if (m.q) { c.fillStyle = tok('--orange'); c.fillRect(x + pad, y + pad, s - 2 * pad, s - 2 * pad); }
      if (m.k) { c.fillStyle = tok('--green'); c.fillRect(x + pad, y + pad, s - 2 * pad, s - 2 * pad); }
      if (m.nb) { c.strokeStyle = tok('--ink'); c.lineWidth = 1.6; c.setLineDash([2.5, 2]); c.strokeRect(x + 1.5, y + 1.5, s - 3, s - 3); c.setLineDash([]); }
      if (m.off !== undefined) {
        c.fillStyle = tok('--coral'); c.beginPath(); c.arc(x + s / 2, y + s / 2, s * 0.3, 0, Math.PI * 2); c.fill();
      }
      if (m.q || m.k) { c.strokeStyle = tok('--ink'); c.lineWidth = 1.4; c.strokeRect(x + pad, y + pad, s - 2 * pad, s - 2 * pad); }
    });
    if (st.hover >= 0) { const [x, y] = sliceXY(st.hover); c.strokeStyle = tok('--ink'); c.lineWidth = 2; c.strokeRect(x + 0.5, y + 0.5, sl.cell - 1, sl.cell - 1); }
  }
  // a cell's (column, row) in the ribbon; mid-change, on a low arc from where it was drawn (fromCR)
  let fromCR = null;
  function placeCR(v, out) {
    const s = L[st.layout][v], c1 = s % 64, r1 = Math.floor(s / 64);
    if (!fromCR || st.t >= 1) { out[0] = c1; out[1] = r1; return out; }
    const e = easeOut(st.t);
    out[0] = fromCR[2 * v] + (c1 - fromCR[2 * v]) * e;
    out[1] = fromCR[2 * v + 1] + (r1 - fromCR[2 * v + 1]) * e - Math.sin(Math.PI * e) * 1.4 * rb.cw / (rb.cw + rb.rgap);
    return out;
  }
  function drawRibbon() {
    const c = rb.ctx, M = marks();
    if (!c) return;
    c.clearRect(0, 0, rb.W, rb.H);
    c.font = '400 12px ' + tok('--font-mono');
    c.fillStyle = tok('--ink-3');
    c.fillText('position 0', 0, 12);
    const endLab = 'position 511';
    c.fillText(endLab, rb.W - c.measureText(endLab).width, 12);
    const pad = Math.max(0.35, rb.cw * 0.08), cr = [0, 0];
    const pos = (v) => { placeCR(v, cr); return [cr[0] * rb.cw, rb.top + cr[1] * (rb.cw + rb.rgap)]; };
    for (let v = 0; v < n; v++) {
      const [x, y] = pos(v), m = M.get(v);
      c.globalAlpha = st.mode === 'pair' || m ? 1 : faded();
      c.fillStyle = colors[v];
      c.fillRect(x + pad, y + pad, rb.cw - 2 * pad, rb.cw - 2 * pad);
    }
    c.globalAlpha = 1;
    M.forEach((m, v) => {
      const [x, y] = pos(v), s = rb.cw;
      if (m.local && !m.q) { c.strokeStyle = tok('--ink'); c.lineWidth = 1.2; c.strokeRect(x + pad, y + pad, s - 2 * pad, s - 2 * pad); }
      if (m.q) { c.fillStyle = tok('--orange'); c.fillRect(x, y, s, s); c.strokeStyle = tok('--ink'); c.lineWidth = 1.2; c.strokeRect(x, y, s, s); }
      if (m.k) { c.fillStyle = tok('--green'); c.fillRect(x, y, s, s); c.strokeStyle = tok('--ink'); c.lineWidth = 1.2; c.strokeRect(x, y, s, s); }
      if (m.off !== undefined) { c.fillStyle = tok('--coral'); c.beginPath(); c.arc(x + s / 2, y + s / 2, Math.max(1.6, s * 0.32), 0, Math.PI * 2); c.fill(); }
      if (m.nb) { c.strokeStyle = tok('--ink'); c.lineWidth = 1.3; c.setLineDash([2, 1.6]); c.strokeRect(x + 0.6, y + 0.6, s - 1.2, s - 1.2); c.setLineDash([]); }
    });
    if (st.hover >= 0) { const [x, y] = pos(st.hover); c.strokeStyle = tok('--ink'); c.lineWidth = 2; c.strokeRect(x - 0.5, y - 0.5, rb.cw + 1, rb.cw + 1); }
  }
  function draw() { drawSlices(); drawRibbon(); readouts(); }

  // ---- readouts. A coordinate keeps together on one line
  const fmtC = (v) => '(' + co(v).join(', ') + ')';
  const RO = { q: $('#roQ'), dc: $('#roDc'), slots: $('#roSlots'), dseq: $('#roDseq'), box: $('#roExtraBox'), xlab: $('#roExtraLab'), x: $('#roExtra'), note: $('#labNote') };
  const put = (el, s) => { if (el.textContent !== s) el.textContent = s; };   // readouts() runs every frame of an order change
  // the same for words that hold a variable, set in italic: HTML from the constants here, never from data
  const putH = (el, html) => { if (el.textContent !== html.replace(/<[^>]+>/g, '')) el.innerHTML = html; };
  const NOTES = {
    pair: 'Colors follow each token’s place in the sample, so a token keeps its color in every view. Repacked keeps the raster order inside each <span class="nw"><i>z</i>-layer</span> and moves whole layers, the way the paper’s pure repack moves whole summary groups.',
    offsets: 'Coral dots: the tokens at Δseq = ±1, ±8 and ±64 from <i>q</i>, the offsets that mean “one step along <i>x</i>, <i>y</i> or <i>z</i>” under raster order. Dashed squares: <i>q</i>’s true face neighbors. Change the order and count how many still agree.',
    local: 'PACK3D’s local window: the 3 × 3 × 3 neighborhood of <i>q</i>, defined by coordinates. Change the order: the window stays the same tokens in the sample, wherever they sit in memory.',
  };
  // the readout only the neighbor and window modes have: [label, value]
  function extra() {
    const q = st.q;
    if (st.mode === 'offsets') {
      const tn = new Set(trueNeighbors(q)), offs = offsetsOf(q).filter((o) => o.v >= 0);
      return ['sequence neighbors that are true neighbors', offs.filter((o) => tn.has(o.v)).length + ' of ' + offs.length];
    }
    if (st.mode === 'local') return ['local window, every order', localWindow(q).length + ' tokens'];
    return null;
  }
  function readouts() {
    const q = st.q, kk = k(), lay = L[st.layout];
    put(RO.q, fmtC(q));
    if (kk >= 0) {
      put(RO.dc, '(1, 0, 0)');
      put(RO.slots, lay[q] + '\u00A0→\u00A0' + lay[kk]);
      const d = lay[kk] - lay[q];
      put(RO.dseq, (d < 0 ? MINUS : '+') + Math.abs(d));
    } else {
      putH(RO.dc, '<i>k</i> is off the top');
      put(RO.slots, String(lay[q]));
      put(RO.dseq, '—');
    }
    const x = extra();
    if (RO.box.hidden !== !x) RO.box.hidden = !x;
    if (x) { put(RO.xlab, x[0]); put(RO.x, x[1]); }
    putH(RO.note, NOTES[st.mode]);
  }
  // the readouts as one sentence for assistive tech, after each move or change
  const status = $('#labStatus');
  function tell() {
    if (!status) return;
    const q = st.q, kk = k(), lay = L[st.layout], [z, y, x] = co(q);
    let s = `Query at z ${z}, y ${y}, x ${x}: memory position ${lay[q]}.`;
    if (kk >= 0) { const d = Math.abs(lay[kk] - lay[q]); s += ` Its neighbor k is at memory position ${lay[kk]}, ${d} ${d === 1 ? 'position' : 'positions'} ${lay[kk] < lay[q] ? 'before' : 'after'} it.`; }
    else s += ' Its neighbor k is off the top.';
    const xr = extra();
    if (xr) s += ` ${xr[0][0].toUpperCase() + xr[0].slice(1)}: ${xr[1]}.`;
    status.textContent = s;
  }

  // ---- interaction
  let morph = 0;
  function setLayout(name) {
    if (name === st.layout) return;
    $$('#labLayouts [data-layout]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.layout === name)));
    // from where the cells are drawn, so a pick mid-change carries on
    const next = new Float32Array(2 * n), cr = [0, 0];
    for (let v = 0; v < n; v++) { placeCR(v, cr); next[2 * v] = cr[0]; next[2 * v + 1] = cr[1]; }
    fromCR = next; st.layout = name; st.t = RM ? 1 : 0;
    ribbonC.setAttribute('aria-label', `The memory order of the tokens: ${LAYOUT_NAMES[name]}`);
    const t0 = performance.now();
    cancelAnimationFrame(morph);                         // one morph at a time: a new pick replaces the one in flight
    const step = (now) => {
      st.t = RM ? 1 : clamp((now - t0) / 1100, 0, 1);
      if (st.t >= 1) fromCR = null;
      drawRibbon(); readouts();
      morph = st.t < 1 ? requestAnimationFrame(step) : 0;
    };
    drawSlices(); morph = requestAnimationFrame(step);
    tell();
  }
  function setMode(m) {
    if (m === st.mode) return;
    st.mode = m; $$('#labModes [data-mode]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === m)));
    draw(); tell();
  }
  $$('#labLayouts [data-layout]').forEach((b) => b.addEventListener('click', () => setLayout(b.dataset.layout)));
  $$('#labModes [data-mode]').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));
  function hitSlice(ev) {
    const r = slicesC.getBoundingClientRect(), px = ev.clientX - r.left, py = ev.clientY - r.top;
    const col = Math.floor(px / (sl.S + sl.gap)), row = Math.floor(py / (sl.S + sl.lab + sl.gap));
    const lx = px - col * (sl.S + sl.gap), ly = py - row * (sl.S + sl.lab + sl.gap) - sl.lab;
    if (col < 0 || col >= sl.cols || lx < 0 || lx >= sl.S || ly < 0 || ly >= sl.S) return -1;
    const z = row * sl.cols + col, x = Math.floor(lx / sl.cell), y = Math.floor(ly / sl.cell);
    return z < N ? vid(z, y, x) : -1;
  }
  function hitRibbon(ev) {
    const r = ribbonC.getBoundingClientRect(), px = ev.clientX - r.left, py = ev.clientY - r.top - rb.top;
    const row = Math.floor(py / (rb.cw + rb.rgap)), col = Math.floor(px / rb.cw);
    if (row < 0 || row > 7 || col < 0 || col > 63 || py - row * (rb.cw + rb.rgap) > rb.cw) return -1;
    return inv[st.layout][row * 64 + col];
  }
  const tipFor = (v) => `token at (<i>z</i>, <i>y</i>, <i>x</i>) = ${fmtC(v)}<br>memory position ${L[st.layout][v]} (${LAYOUT_NAMES[st.layout]})`;
  [[slicesC, hitSlice], [ribbonC, hitRibbon]].forEach(([el, hit]) => {
    el.addEventListener('pointermove', (ev) => { if (ev.pointerType === 'touch') return; const v = hit(ev); if (v !== st.hover) { st.hover = v; drawSlices(); drawRibbon(); } if (v >= 0) showTip(tipFor(v), ev); else hideTip(); });
    el.addEventListener('pointerleave', (ev) => { if (ev.pointerType === 'touch') return; st.hover = -1; hideTip(); drawSlices(); drawRibbon(); });
    // a tap also names the token: a finger cannot hover
    el.addEventListener('click', (ev) => { const v = hit(ev); if (v < 0) return; st.q = v; draw(); tell(); if (byFinger(ev)) tapTip(tipFor(v), ev); });
  });
  // arrows move the query in x and y, Page Up and Page Down in z; each move is said in #labStatus
  slicesC.tabIndex = 0;
  slicesC.setAttribute('role', 'application');
  slicesC.setAttribute('aria-roledescription', 'token field');
  slicesC.setAttribute('aria-describedby', 'labReadouts');
  slicesC.setAttribute('aria-label', `Eight z-slices of 512 tokens. ${HOVERLESS ? 'Tap' : 'Click'} a token, or use the arrow keys, Home and End, and Page Up or Page Down, to move the query.`);
  ribbonC.setAttribute('aria-label', `The memory order of the tokens: ${LAYOUT_NAMES[st.layout]}`);
  // Home and End: the row's ends (with Control, the slice's corners)
  slicesC.addEventListener('keydown', (ev) => {
    const [z, y, x] = co(st.q);
    if ((ev.key === 'Home' || ev.key === 'End') && !ev.altKey && !ev.metaKey) {
      ev.preventDefault();
      const e = ev.key === 'Home' ? 0 : N - 1;
      st.q = vid(z, ev.ctrlKey ? e : y, e);
      draw(); tell();
      return;
    }
    const d = { ArrowLeft: [0, 0, -1], ArrowRight: [0, 0, 1], ArrowUp: [0, -1, 0], ArrowDown: [0, 1, 0], PageUp: [1, 0, 0], PageDown: [-1, 0, 0] }[ev.key];
    if (!d) return;
    ev.preventDefault();
    st.q = vid(clamp(z + d[0], 0, N - 1), clamp(y + d[1], 0, N - 1), clamp(x + d[2], 0, N - 1));
    draw(); tell();
  });
  // lay out only when the width changes, not the height
  const slicesWrap = $('#labSlicesWrap');
  new ResizeObserver(() => { if (slicesWrap.getBoundingClientRect().width !== sl.W) { layoutViews(); draw(); } }).observe(slicesWrap);
  [slicesC, ribbonC].forEach((c) => c.addEventListener('contextrestored', () => { layoutViews(); draw(); }));
  onDpr(() => { layoutViews(); draw(); });
  onTheme(() => { bakeColors(); draw(); });
  // on paper: drawn for a printed column, in the print theme (set before this runs), and back after
  addEventListener('beforeprint', () => { layoutViews(PRINT_W); draw(); });
  addEventListener('afterprint', () => { layoutViews(); draw(); });
  layoutViews(); draw();
  // the labels are DM Mono: draw again once it is in, if it was not when the lab first drew
  if (!document.fonts.check('400 12px "DM Mono"')) document.fonts.load('400 12px "DM Mono"').then(() => draw(), () => {});
}

// ====================================================================== rotary dials
function initRope() {
  const G = 9, W = 320, cell = W / G;
  const svg = d3.select('#ropeGrid');
  const OM = { z: 0.55, y: 0.47, x: 0.71 };          // toy frequencies (radians per token)
  const PSI = { z: 0.6, y: -0.4, x: 1.1 };           // toy content: the key's own angle against the query's
  const OMS = 0.29, PSIS = 0.5;                       // the sequence dial
  const rowsRepack = [4, 7, 1, 8, 2, 5, 0, 6, 3];     // whole rows moved in memory
  let st = { q: [4, 2], k: [2, 5], repacked: false };
  const slot = (p) => (st.repacked ? rowsRepack.indexOf(p[0]) : p[0]) * G + p[1];
  let picked = null;
  const g = svg.append('g').attr('aria-hidden', 'true');
  for (let i = 0; i < G; i++) for (let j = 0; j < G; j++) {
    g.append('rect').datum([i, j]).attr('x', j * cell + 1.5).attr('y', i * cell + 1.5).attr('width', cell - 3).attr('height', cell - 3)
      .attr('rx', 6).attr('class', 'cellr').style('fill', 'var(--track)');
  }
  g.on('click', (ev) => { const p = d3.select(ev.target).datum(); if (Array.isArray(p)) moveTo(picked || 'q', p); });
  const slotLab = svg.append('g').attr('aria-hidden', 'true');
  const tokens = svg.append('g');
  const mk = (key, fill, lab) => {
    const t = tokens.append('g').attr('class', 'tok').attr('tabindex', 0).attr('role', 'button')
      .attr('aria-roledescription', 'movable token').attr('aria-describedby', 'ropeKeys');
    // an undrawn margin: a fingertip is wider than the token, so it may grab a little outside it (sized by fitGrab)
    t.append('rect').attr('class', 'grab').style('fill', 'transparent');
    // the ring shows the picked token, and the focused one
    t.append('rect').attr('class', 'ring').attr('x', 0.5).attr('y', 0.5).attr('width', cell - 1).attr('height', cell - 1).attr('rx', 8);
    t.append('rect').attr('width', cell - 6).attr('height', cell - 6).attr('x', 3).attr('y', 3).attr('rx', 6).style('fill', fill).style('stroke', 'var(--ink)').style('stroke-width', 1.5);
    // the variable's letter, in italic, in the stage's dark ink: the token's fill is light in either theme
    t.append('text').attr('x', cell / 2).attr('y', cell / 2 + 5).attr('text-anchor', 'middle').style('font-style', 'italic').style('font-weight', 600).style('fill', 'var(--stage-bg)').style('font-size', '15px').text(lab);
    // d3.drag swallows the click that ends a drag, so this is a tap in place. With a token picked, a tap on this one's
    // margin, outside its cell, chooses that cell
    t.on('click', (ev) => {
      const [px, py] = d3.pointer(ev, svg.node()), p = [Math.floor(py / cell), Math.floor(px / cell)];
      const inGrid = p[0] >= 0 && p[0] < G && p[1] >= 0 && p[1] < G;
      if (picked && inGrid && (p[0] !== st[key][0] || p[1] !== st[key][1])) moveTo(picked, p);
      else pick(picked === key ? null : key);
    });
    t.on('keydown', (ev) => {
      const d = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] }[ev.key];
      if (!d) return;
      ev.preventDefault();
      const other = st[key === 'q' ? 'k' : 'q'];
      let [y, x] = st[key];
      do { y += d[0]; x += d[1]; } while (y === other[0] && x === other[1]);   // hop over the other token
      if (y >= 0 && y < G && x >= 0 && x < G) moveTo(key, [y, x]);
    });
    return t;
  };
  const tq = mk('q', 'var(--orange)', 'q'), tk = mk('k', 'var(--green)', 'k');
  // --u keeps the slot labels at their size. Under a finger the margin grows as the grid shrinks: 46px to hit, so
  // rounding never takes it under 44
  const coarse = window.matchMedia('(any-pointer: coarse)');
  let gridW = 0, grabM = -1;
  const fitGrab = () => {
    const m = coarse.matches && gridW ? Math.max(6, (46 * W / gridW - cell) / 2) : 6;
    if (Math.abs(m - grabM) < 0.01) return;
    grabM = m;
    tokens.selectAll('rect.grab').attr('x', -m).attr('y', -m).attr('width', cell + 2 * m).attr('height', cell + 2 * m);
  };
  fitGrab();
  new ResizeObserver(() => {
    const w = svg.node().getBoundingClientRect().width;
    if (!w) return;
    gridW = w; svg.style('--u', (W / w).toFixed(4)); fitGrab();
  }).observe(svg.node());
  coarse.addEventListener('change', fitGrab);
  function pick(key) { picked = key; tq.classed('picked', key === 'q'); tk.classed('picked', key === 'k'); }
  function moveTo(key, p) {
    const other = st[key === 'q' ? 'k' : 'q'];
    if ((p[0] === other[0] && p[1] === other[1]) || (p[0] === st[key][0] && p[1] === st[key][1])) return;
    st[key] = p; update();
  }
  // the dial cards are in the page already, so the rows keep their height before this runs
  function dial(card) {
    const s = d3.select(card).select('svg');
    s.append('circle').attr('cx', 60).attr('cy', 60).attr('r', 50).style('fill', 'var(--surface-2)').style('stroke', 'var(--rule)').style('stroke-width', 1.5);
    for (let i = 0; i < 24; i++) {
      const a = i / 24 * Math.PI * 2, r0 = i % 6 === 0 ? 42 : 46;
      s.append('line').attr('x1', 60 + r0 * Math.cos(a)).attr('y1', 60 + r0 * Math.sin(a)).attr('x2', 60 + 50 * Math.cos(a)).attr('y2', 60 + 50 * Math.sin(a)).style('stroke', 'var(--rule)').style('stroke-width', 1.2);
    }
    const arc = s.append('path').style('opacity', 0.35);
    // the hands differ in more than color: the key's ends in a ring, the query's in a dot, drawn over it
    const hk = s.append('line').attr('x1', 60).attr('y1', 60).style('stroke', 'var(--green-ink)').style('stroke-width', 4).style('stroke-linecap', 'round');
    const hq = s.append('line').attr('x1', 60).attr('y1', 60).style('stroke', 'var(--orange-mark)').style('stroke-width', 4).style('stroke-linecap', 'round');
    const ek = s.append('circle').attr('r', 5.5).style('fill', 'none').style('stroke', 'var(--green-ink)').style('stroke-width', 2.5);
    const eq = s.append('circle').attr('r', 4.5).style('fill', 'var(--orange-mark)');
    s.append('circle').attr('cx', 60).attr('cy', 60).attr('r', 4).style('fill', 'var(--ink)');
    // a: the query hand's angle, d: the key hand's turn from it, as drawn now (null until the first draw)
    return { arc, hq, hk, eq, ek, cap: d3.select(card).select('.cap'), capH: '', a: null, d: 0 };
  }
  const dialsC = $$('#ropeDialsCoord .dial-card').map(dial);
  const dialS = dial($('#ropeDialsSeq .dial-card'));
  const arcPath = (a0, a1) => {
    const r = 34, d = a1 - a0, large = Math.abs(d) % (2 * Math.PI) > Math.PI ? 1 : 0;
    const sweep = d >= 0 ? 1 : 0;
    const p0 = [60 + r * Math.cos(a0), 60 + r * Math.sin(a0)], p1 = [60 + r * Math.cos(a1), 60 + r * Math.sin(a1)];
    return `M60 60 L${p0[0]} ${p0[1]} A${r} ${r} 0 ${large} ${sweep} ${p1[0]} ${p1[1]} Z`;
  };
  const wrap = (a) => { a = ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI; return a; };
  function pose(dl, a, d) {
    const R = 42, b = a + d;
    dl.hq.attr('x2', 60 + R * Math.cos(a)).attr('y2', 60 + R * Math.sin(a));
    dl.eq.attr('cx', 60 + R * Math.cos(a)).attr('cy', 60 + R * Math.sin(a));
    dl.hk.attr('x2', 60 + (R - 5.5) * Math.cos(b)).attr('y2', 60 + (R - 5.5) * Math.sin(b));
    dl.ek.attr('cx', 60 + R * Math.cos(b)).attr('cy', 60 + R * Math.sin(b));
    dl.arc.attr('d', arcPath(a, b));
    dl.a = a; dl.d = d;
  }
  // the first draw is not a move; a drag is followed at once
  function setDial(dl, aq, ak, color, text) {
    const A = -Math.PI / 2 + wrap(aq), dA = wrap(ak - aq);
    dl.arc.interrupt().style('fill', color);            // a move in flight stops where it is drawn, and turns from there
    if (RM || !drawn || dragging || dl.a === null) pose(dl, A, dA);
    else {
      const a0 = dl.a, d0 = dl.d, a1 = a0 + wrap(A - a0);   // the query's hand turns the short way round
      answer(dl.arc).tween('pose', () => (t) => pose(dl, a0 + (a1 - a0) * t, d0 + (dA - d0) * t));
    }
    if (dl.capH !== text) { dl.capH = text; dl.cap.html(text); }   // the caption: HTML from the constants here
  }
  // read out once a move settles, not on the first draw
  const note = $('#ropeNote'), NOTE = note.textContent, live = $('#ropeLive');
  const say = (el, text) => { if (el.textContent !== text) el.textContent = text; };
  const sgnI = (d) => (d < 0 ? MINUS : d > 0 ? '+' : '') + Math.abs(d);
  let drawn = false, dragging = false, liveT = 0;
  const glide = (sel) => (RM || !drawn || dragging ? sel.interrupt() : answer(sel));
  function update() {
    const [qy, qx] = st.q, [ky, kx] = st.k;
    const cq = { z: 0, y: qy, x: qx }, ck = { z: 0, y: ky, x: kx };
    let logitC = 0;
    ['z', 'y', 'x'].forEach((a, i) => {
      const aq = OM[a] * cq[a], ak = OM[a] * ck[a];      // the hands: pure rotation by coordinate
      const d = ck[a] - cq[a];
      setDial(dialsC[i], aq, ak, 'var(--teal)', `<i>${a}</i> axis<br>Δ<i>${a}</i> = ${sgnI(d)}`);
      logitC += Math.cos(OM[a] * d + PSI[a]) / 3;          // mean over the three planes, so both meters share a scale
    });
    const sq = slot(st.q), sk = slot(st.k), ds = sk - sq;
    setDial(dialS, OMS * sq, OMS * sk, 'var(--coral)', `memory position<br>Δseq = ${ds < 0 ? MINUS : '+'}${Math.abs(ds)}`);
    const logitS = Math.cos(OMS * ds + PSIS);
    say($('#ropeValC'), fix(logitC, 2));
    say($('#ropeValS'), fix(logitS, 2));
    $('#ropeMeterC').style.width = ((logitC + 1) / 2 * 100) + '%';
    $('#ropeMeterS').style.width = ((logitS + 1) / 2 * 100) + '%';
    glide(tq).attr('transform', `translate(${qx * cell},${qy * cell})`);
    glide(tk).attr('transform', `translate(${kx * cell},${ky * cell})`);
    tq.attr('aria-label', `Query q, at y ${qy} and x ${qx}, memory position ${sq}`);
    tk.attr('aria-label', `Key k, at y ${ky} and x ${kx}, memory position ${sk}`);
    const labs = slotLab.selectAll('text').data(d3.range(G * G));
    labs.join('text').attr('class', 'slot').attr('x', (d) => (d % G) * cell + cell - 5).attr('y', (d) => Math.floor(d / G) * cell + cell - 5)
      .attr('text-anchor', 'end').text((d) => slot([Math.floor(d / G), d % G]));
    say($('#ropeRepack'), st.repacked ? 'Restore raster order' : 'Repack the rows');
    if (drawn) {
      clearTimeout(liveT);
      const text = `Δy ${sgnI(ky - qy)}, Δx ${sgnI(kx - qx)}, Δseq ${sgnI(ds)}. PACK3D logit ${fix(logitC, 2)}, packed RoPE logit ${fix(logitS, 2)}.`;
      liveT = setTimeout(() => say(live, text), 400);
    }
    drawn = true;
  }
  function dragger(sel, key) {
    sel.call(d3.drag().on('start', function () { dragging = true; d3.select(this).style('cursor', 'grabbing'); })
      .on('drag', (ev) => {
        // the drag event's own x and y: d3.pointer(ev) reads clientX from the source event, which a touch event lacks
        const p = [clamp(Math.floor(ev.y / cell), 0, G - 1), clamp(Math.floor(ev.x / cell), 0, G - 1)];
        const other = key === 'q' ? st.k : st.q;
        if (p[0] === other[0] && p[1] === other[1]) return;
        if (p[0] !== st[key][0] || p[1] !== st[key][1]) { st[key] = p; update(); }
      })
      .on('end', function () { dragging = false; d3.select(this).style('cursor', 'grab'); }));
  }
  dragger(tq, 'q'); dragger(tk, 'k');
  $('#ropeMove').addEventListener('click', () => {
    const dy = Math.max(st.q[0], st.k[0]) < G - 1 ? 1 : -Math.min(st.q[0], st.k[0]);
    const dx = Math.max(st.q[1], st.k[1]) < G - 1 ? 1 : -Math.min(st.q[1], st.k[1]);
    st.q = [st.q[0] + dy, st.q[1] + dx]; st.k = [st.k[0] + dy, st.k[1] + dx];
    say(note, 'Both tokens moved by the same step. Every hand turned, but the arcs between them did not, so PACK3D’s logit is unchanged. Packed RoPE keeps its logit only while the move happens to preserve the difference in memory position.');
    update();
  });
  $('#ropeRepack').addEventListener('click', () => {
    st.repacked = !st.repacked;
    say(note, st.repacked
      ? 'The memory order changed and the tokens did not move. PACK3D’s dials are untouched. Packed RoPE now sees a different Δseq for the same two tokens, and its logit changes.'
      : 'Back to raster order.');
    update();
  });
  $('#ropeReset').addEventListener('click', () => { st = { q: [4, 2], k: [2, 5], repacked: false }; pick(null); say(note, NOTE); update(); });
  update();
}

// ====================================================================== rotate-before-pool
function initPool() {
  const svg = d3.select('#poolSvg');
  const OMx = 0.95;
  // four toy key states; chosen so both summaries are long enough to read
  const states = [{ n: 'A', a: 3.4, r: 0.95 }, { n: 'B', a: 5.5, r: 0.85 }, { n: 'C', a: 2.7, r: 1.0 }, { n: 'D', a: 2.0, r: 0.85 }];
  let order = [0, 1, 2, 3], swapped = false;
  const xc = 1.5;
  const rot = (v, a) => [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a)];
  const vec = (s) => [s.r * Math.cos(s.a), s.r * Math.sin(s.a)];
  // what each plot pools: rotated at each member's own x, or all rotated at the block center
  const membersTB = () => order.map((si, u) => rot(vec(states[si]), OMx * u));
  const membersSC = () => order.map((si) => rot(vec(states[si]), OMx * xc));
  const avg = (ms) => ms.reduce((s, m) => [s[0] + m[0] / ms.length, s[1] + m[1] / ms.length], [0, 0]);
  const first = { tb: avg(membersTB()), sc: avg(membersSC()) };
  const plots = [
    { key: 'tb', title: 'rotate, then pool', mem: membersTB, color: 'var(--teal-mark)', tint: 'var(--tint-teal)' },
    { key: 'sc', title: 'pool, then rotate at center', mem: membersSC, color: 'var(--warm-mark)', tint: 'var(--warm)' },
  ];
  let stateLab, tokArrow, S = 78;
  function build() {
    svg.selectAll('*').remove();
    const W = chartW(svg.node(), 520);
    const narrow = W < 440, foot = narrow ? 58 : 40;
    // sideways the dials give way first: to a radius of 40 under Safari's bars, 54 elsewhere
    const R = Math.round(Math.min(clamp(W / 4 - 22, 54, 86), Math.max(40, (heightRange(svg.node())[1] - 118 - foot) / 2))), cy = 118 + R, H = cy + R + foot;
    S = R * 0.92;
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const cw = narrow ? 44 : 50, gap = narrow ? 8 : 8;
    const blk = svg.append('g').attr('transform', `translate(2,30)`);
    const along = blk.append('text').attr('x', 0).attr('y', -12).attr('class', 'muted-t').text('a block of four tokens along ');
    along.append('tspan').style('font-style', 'italic').text('x');
    const cells = blk.selectAll('g.cellb').data([0, 1, 2, 3]).join('g').attr('class', 'cellb').attr('transform', (d) => `translate(${d * (cw + gap)},0)`);
    cells.append('rect').attr('width', cw).attr('height', cw).attr('rx', 6).style('fill', 'var(--surface-2)').style('stroke', 'var(--lav)').style('stroke-width', 1.5);
    const xLab = cells.append('text').attr('x', cw / 2).attr('y', cw + 17).attr('text-anchor', 'middle').attr('class', 'muted-t').style('font-size', '12px');
    xLab.append('tspan').style('font-style', 'italic').text('x');
    xLab.append('tspan').text((d) => ' = ' + d);
    stateLab = cells.append('text').attr('x', 6).attr('y', 16).attr('class', 'lab-strong');
    const c0 = cw / 2 + 2;
    tokArrow = cells.append('line').attr('x1', c0).attr('y1', c0).attr('x2', c0).attr('y2', c0).style('stroke', 'var(--ink-2)').style('stroke-width', 2).style('stroke-linecap', 'round');
    cells.append('circle').attr('cx', c0).attr('cy', c0).attr('r', 2.4).style('fill', 'var(--ink-2)');
    tokArrow.datum((d) => d).each(function () { this.__c0 = c0; this.__len = cw * 0.3; });
    if (!narrow) svg.append('text').attr('x', W).attr('y', 18).attr('text-anchor', 'end').attr('class', 'muted-t').style('font-size', '12px').text('thin: members · thick: summary');
    else svg.append('text').attr('x', 0).attr('y', H - 6).attr('class', 'muted-t').style('font-size', '12px').text('thin: members · thick: summary');
    plots.forEach((p, i) => {
      const cx = i === 0 ? W * 0.25 : W * 0.75;
      const g = svg.append('g').attr('transform', `translate(${cx},${cy})`);
      g.append('circle').attr('r', R).style('fill', 'none').style('stroke', 'var(--grid)').style('stroke-width', 1.2);
      g.append('line').attr('x1', -R - 6).attr('x2', R + 6).style('stroke', 'var(--grid)');
      g.append('line').attr('y1', -R - 6).attr('y2', R + 6).style('stroke', 'var(--grid)');
      const title = g.append('text').attr('y', R + 24).attr('text-anchor', 'middle').attr('class', 'lab-ink').text(narrow && i === 1 ? 'pool, rotate at center' : p.title);
      // centred under its plot, but slid in where it would run past the figure's edge (4px spare for the font's arrival)
      const half = title.node().getComputedTextLength() / 2;
      title.attr('x', clamp(0, 4 + half - cx, W - 4 - half - cx));
      p.members = g.append('g').style('opacity', p.key === 'sc' ? 0.5 : 1);
      p.ghost = g.append('line').style('stroke', p.color).style('stroke-width', 3).style('stroke-dasharray', '3 4').style('opacity', 0).style('stroke-linecap', 'round');
      p.arrow = g.append('line').style('stroke', p.color).style('stroke-width', 5).style('stroke-linecap', 'round');
      p.head = g.append('circle').attr('r', 6).style('fill', p.color).style('stroke', 'var(--surface)').style('stroke-width', 1.5);
    });
  }
  function update(animate) {
    // a swap eases out; a first draw, or a redraw for a new width, is not a move
    const move = (sel) => (animate && !RM ? answer(sel) : sel.interrupt());
    stateLab.text((d) => states[order[d]].n);
    move(tokArrow)
      .attr('x2', function (d) { return this.__c0 + this.__len * Math.cos(-states[order[d]].a); })
      .attr('y2', function (d) { return this.__c0 + this.__len * Math.sin(-states[order[d]].a); });
    plots.forEach((p) => {
      const ms = p.mem(), v = avg(ms), f = first[p.key];
      p.ghost.attr('x1', 0).attr('y1', 0).attr('x2', f[0] * S).attr('y2', -f[1] * S).style('opacity', swapped ? 0.6 : 0);
      move(p.arrow).attr('x1', 0).attr('y1', 0).attr('x2', v[0] * S).attr('y2', -v[1] * S);
      move(p.head).attr('cx', v[0] * S).attr('cy', -v[1] * S);
      move(p.members.selectAll('line').data(ms).join('line').attr('x1', 0).attr('y1', 0)
        .style('stroke', p.tint).style('stroke-width', 2).style('stroke-linecap', 'round'))
        .attr('x2', (d) => d[0] * S).attr('y2', (d) => -d[1] * S);
    });
    const moved = (p) => { const v = avg(p.mem()), f = first[p.key]; return Math.hypot(v[0] - f[0], v[1] - f[1]); };
    // the readouts are a live region: write them only when a value changes, so a redraw is not announced
    [['#poolDtb', plots[0]], ['#poolDsc', plots[1]]].forEach(([id, p]) => { const el = $(id), v = moved(p).toFixed(3); if (el.textContent !== v) el.textContent = v; });
  }
  build();
  onResize(() => { build(); update(false); });
  $('#poolSwap').addEventListener('click', () => {
    order = swapped ? [0, 1, 2, 3] : [0, 2, 1, 3];
    swapped = !swapped;
    $('#poolSwap').textContent = swapped ? 'Swap them back' : 'Swap tokens 1 and 2';
    update(true);
  });
  update(false);
  // the placement probe, from the paper
  const P = D.probes;
  const rows = [['keys rotated before pooling', P.tb, 'var(--teal-mark)'], ['summary-center rotation', P.sc, 'var(--warm-mark)'], ['unrotated summaries', P.un, 'var(--warm-mark)']];
  const box = d3.select('#probeMini');
  box.append('p').attr('class', 'view-label mb-1').text('Placement probe accuracy, 6 seeds');
  rows.forEach(([name, v, col]) => {
    const r = box.append('div').attr('class', 'meter-row');
    r.append('span').attr('class', 'small muted').text(name);
    const m = r.append('div').attr('class', 'meter');
    m.append('i').style('width', (v * 100) + '%').style('background', col);
    m.append('b');
    r.append('span').attr('class', 'num').text(v.toFixed(4));
  });
  // the note beside the figure; HTML from this constant only
  box.append('p').attr('class', 'note mt-1').html('The line marks chance, 0.5. Only keys rotated before pooling beat it (<span class="nw">exact <i>p</i> = 0.031</span> for each contrast).');
}

// ====================================================================== Figure 1 tour
// The figure is only scaled and moved, never redrawn. Regions are in the figure's own units.
function initTour() {
  const FW = 3016.58, FH = 1080;
  // p: a part as the figure labels it; t: its title; d: HTML from these constants only. The overview's instruction is
  // added here, as a hint
  const stops = [
    { p: 'Overview', t: 'The whole operator', d: 'PACK3D separates memory layout from attention geometry. <span class="hint">Step through the panels, or choose any part of the figure to zoom in.</span>', r: [0, 0, FW, FH] },
    { p: 'Panel 1', t: 'A 3D token field', d: 'Queries, keys and values sit on a 3D token grid, so every token has a place in the sample.', r: [16, 16, 572, 580] },
    { p: 'Panel 2', t: 'Pack for memory (layout only)', d: 'The field may be packed in any memory order for efficient execution, such as a block-Morton or block-contiguous layout. Each token’s grid coordinate travels with it.', r: [16, 592, 572, 456] },
    { p: 'Panel 3', t: 'Physical 3D coordinates', d: 'Each token carries integer coordinates on the token grid, <i>c</i> = (<i>z</i>, <i>y</i>, <i>x</i>). These, not memory positions, are what PACK3D’s attention reads.', r: [608, 10, 504, 484] },
    { p: 'Panel 4', t: 'Axial RoPE', d: 'Axial RoPE rotates queries and keys by their coordinates, one subspace per axis, and leaves values unrotated, so query–key compatibility depends on the relative displacement, not on sequence position.', r: [606, 504, 506, 560] },
    { p: 'Panel 5.1', t: 'Rotate keys before compression', d: 'The compressed branch has its own key and value projections. It rotates each key by its own token coordinate before any pooling. Values are kept unrotated.', r: [1186, 158, 508, 768] },
    { p: 'Panel 5.2', t: 'Build summaries per 3D block', d: 'Tokens are partitioned into contiguous 3D blocks. Each block’s rotated keys are pooled into one summary key, and its unrotated values into one summary value.', r: [1738, 158, 614, 772] },
    { p: 'Panel 5', t: 'Main result', d: 'Because keys are rotated before pooling, each query-to-summary logit is a weighted sum of query–key terms evaluated at the displacements of the tokens that formed the summary (Proposition 1).', r: [1122, 938, 1264, 128] },
    { p: 'Panel A', t: 'Local neighborhood (exact)', d: 'Each query, the orange token, attends exactly to the tokens in its coordinate neighborhood.', r: [2428, 28, 584, 408] },
    { p: 'Panel B', t: 'Compressed summaries (global)', d: 'It also attends to summaries across the field, drawn here as one summary per 3D block.', r: [2428, 434, 584, 296] },
    { p: 'Panel C', t: 'Local + compressed', d: 'Together, the query combines exact local context with compressed global context.', r: [2428, 726, 584, 300] },
  ];
  const view = $('#tourView'), img = $('#tourImg'), spot = $('#tourSpot'), map = $('#tourMap'), say = $('#tour .tour-say');
  let cur = 0, geom = null;
  const pct = (v, of) => (v / of * 100) + '%';
  const name = (s) => `${s.p}: ${s.t}`;
  const put = (el, text) => { if (el.textContent !== text) el.textContent = text; };
  // the same for HTML, compared by its words, so the live region hears only a stop that changed
  const putH = (el, html) => { if (el.textContent !== html.replace(/<[^>]+>/g, '')) el.innerHTML = html; };
  const mapBtns = stops.map((s, i) => {
    if (i === 0) return null;
    const b = document.createElement('button');
    const [rx, , rw] = s.r;
    b.className = 'map-r'; b.type = 'button'; b.setAttribute('aria-label', name(s));
    Object.assign(b.style, { left: pct(rx, FW), width: pct(rw, FW) });   // top and height: fitTargets
    // the second click of a double-click would only zoom straight back out
    b.addEventListener('click', (ev) => { if (ev.detail < 2) go(cur === i ? 0 : i); });
    // a resting mouse names the part in the page's own tip
    b.addEventListener('pointermove', (ev) => { if (ev.pointerType === 'mouse') showTip(name(s), ev); });
    b.addEventListener('pointerleave', (ev) => { if (ev.pointerType === 'mouse') hideTip(); });
    map.appendChild(b);
    return b;
  });
  // a live region from the reader's first step on; the first writing is not read out
  function go(i, quiet) {
    cur = (i + stops.length) % stops.length;
    const s = stops[cur];
    if (!quiet && say) say.setAttribute('aria-live', 'polite');
    mapBtns.forEach((b, j) => b && b.setAttribute('aria-pressed', String(j === cur)));
    put($('#tourN'), `Step ${cur + 1} of ${stops.length}`);
    put($('#tourP'), s.p); put($('#tourT'), s.t); putH($('#tourD'), s.d);
    const inMap = map.contains(document.activeElement);
    view.classList.toggle('zoomed', cur !== 0);
    // on a phone the map leaves with the overview: a part that zoomed back out hands the keyboard on to Next
    if (inMap && cur === 0 && !map.getClientRects().length) $('#tourNext').focus({ preventScroll: true });
    if (cur !== 0) sharpen();
    place();
  }
  function place() {
    const r = view.getBoundingClientRect(), W = r.width, H = r.height;
    if (!W || !H) return;
    const [rx, ry, rw, rh] = stops[cur].r;
    const s = Math.min(W / rw, H / rh) * (cur === 0 ? 0.98 : 0.92), s0 = W / FW;
    const tx = W / 2 - (rx + rw / 2) * s, ty = H / 2 - (ry + rh / 2) * s;
    geom = { s, tx, ty };
    img.style.transform = `translate(${tx}px, ${ty}px) scale(${s / s0})`;
    // the spotlight: the camera as translate and scale (glides on the compositor), its place as transform (jumps)
    const pad = 6 / s;
    Object.assign(spot.style, {
      translate: `${tx}px ${ty}px`, scale: String(s / s0), transform: `translate(${(rx - pad) * s0}px, ${(ry - pad) * s0}px)`,
      width: (rw + 2 * pad) * s0 + 'px', height: (rh + 2 * pad) * s0 + 'px',
    });
    spot.style.setProperty('--z', (s / s0).toFixed(4));
    spot.classList.toggle('on', cur !== 0);
  }
  view.addEventListener('click', (ev) => {
    if (ev.detail > 1) return;                 // the second click of a double-click would undo the first
    if (cur !== 0 || !geom) { go(0); return; }
    const r = view.getBoundingClientRect();
    const fx = (ev.clientX - r.left - geom.tx) / geom.s, fy = (ev.clientY - r.top - geom.ty) / geom.s;
    const hit = stops.findIndex((s, i) => i > 0 && fx >= s.r[0] && fx <= s.r[0] + s.r[2] && fy >= s.r[1] && fy <= s.r[1] + s.r[3]);
    if (hit > 0) go(hit);
  });
  // a part under 24px grows about its middle; a part it would overlap gives way
  function fitTargets() {
    const mh = map.getBoundingClientRect().height, MIN = 24;
    if (!mh) return;
    const box = stops.map((s, i) => {
      if (!i) return null;
      const [rx, ry, rw, rh] = s.r;
      let y = ry / FH * mh, h = rh / FH * mh;
      const grown = h < MIN;
      if (grown) { y = clamp(y + h / 2 - MIN / 2, 0, mh - MIN); h = MIN; }
      return { x0: rx, x1: rx + rw, y, h, grown };
    });
    box.forEach((a, i) => a && a.grown && box.forEach((o, j) => {
      if (!o || j === i || o.x0 >= a.x1 || a.x0 >= o.x1 || o.y >= a.y + a.h || a.y >= o.y + o.h) return;
      if (o.y < a.y) o.h = a.y - 1 - o.y;
      else { const bottom = o.y + o.h; o.y = a.y + a.h + 1; o.h = bottom - o.y; }
    }));
    mapBtns.forEach((b, i) => b && Object.assign(b.style, { top: box[i].y + 'px', height: Math.max(0, box[i].h) + 'px' }));
  }
  new ResizeObserver(fitTargets).observe(map);
  // the vector's parse is one long task: it is fetched only once the reader rests on the figure or steps into it
  let vector = false, restT = 0;
  const rest = () => { clearTimeout(restT); restT = setTimeout(sharpen, 600); };   // a page in motion scrolls every frame
  const restIO = new IntersectionObserver((es) => {
    clearTimeout(restT);
    window.removeEventListener('scroll', rest);
    if (!es.some((e) => e.isIntersecting)) return;
    window.addEventListener('scroll', rest, { passive: true });
    rest();
  }, { threshold: 0.5 });
  restIO.observe(view);
  function sharpen() {
    if (vector) return;
    vector = true;
    clearTimeout(restT); restIO.disconnect(); window.removeEventListener('scroll', rest);
    const v = new Image();
    v.src = 'figure1.min.svg';
    // swap once it is ready, so the picture never blanks
    v.decode().then(() => { img.removeAttribute('srcset'); img.removeAttribute('sizes'); img.src = v.src; }, () => {});
  }
  $('#tourPrev').addEventListener('click', () => go(cur - 1));
  $('#tourNext').addEventListener('click', () => go(cur + 1));
  view.tabIndex = -1;
  new ResizeObserver(place).observe(view);
  go(0, true);
}

// ====================================================================== the contract
function initContract() {
  const boxes = $$('#tags input');
  const named = { pk: D.named.pk1 - D.named.pk0, ax: D.named.ax1 - D.named.ax0 };
  const R = D.repack, axd = mean(R.ax1) - mean(R.ax0), pkd = mean(R.pk1) - mean(R.pk0);
  const title = $('#verdictTitle'), text = $('#verdictText');
  // a live region: write only what changed, so the first draw says nothing
  const put = (el, t) => { if (el.textContent !== t) el.textContent = t; };
  const list = (a) => (a.length < 3 ? a.join(' and ') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]);
  function update() {
    const on = Object.fromEntries(boxes.map((b) => [b.dataset.tag, b.checked]));
    const all = boxes.every((b) => b.checked);
    const v = $('#verdict');
    v.classList.toggle('off', !all);
    if (all) {
      put(title, 'Inside Proposition 2: a pure repack');
      put(text, `For PACK3D the repack only permutes the computation: on Allen-15 it moves Dice by ${sgn(axd, 4)}. Packed RoPE, which rotates by sequence position, has no such guarantee: it moves by ${sgn(pkd, 3)}.`);
    } else if (!on.members && on.coord && on.edges) {
      put(title, 'Outside Proposition 2: a named-layout switch');
      put(text, `Coordinates and neighborhoods travel, but tokens are summarized in new groups, so the operator itself changes. On Allen-15 (3 seeds), PACK3D loses ${fix(-named.ax, 4)} Dice and packed RoPE loses ${fix(-named.pk, 4)}.`);
    } else {
      put(title, 'Outside Proposition 2');
      const miss = [!on.coord && 'coordinates', !on.edges && 'neighborhood edges', !on.members && 'summary memberships', !on.slot && 'within-block slots'].filter(Boolean);
      put(text, `Without ${list(miss)}, Proposition 2 no longer applies and guarantees nothing. The paper’s only test outside it is the named-layout switch, which changes memberships but keeps coordinates and neighborhoods.`);
    }
  }
  boxes.forEach((b) => b.addEventListener('change', update));
  update();
  // Safari, unlike Chrome, gives an overflowing scroller no tab stop: each display equation gets one while it
  // overflows, named by its place
  const eqs = $$('.math-display');
  const wide = new ResizeObserver((es) => es.forEach(({ target: el }) => {
    const over = el.scrollWidth > el.clientWidth + 1;
    if (over === (el.getAttribute('role') === 'region')) return;
    if (over) { el.tabIndex = 0; el.setAttribute('role', 'region'); el.setAttribute('aria-label', `Equation ${eqs.indexOf(el) + 1}`); }
    else { el.removeAttribute('tabindex'); el.removeAttribute('role'); el.removeAttribute('aria-label'); }
  }));
  eqs.forEach((el) => wide.observe(el));
}

// ====================================================================== charts: helpers
// CHART_MIN: a sheet's inside on a 320px phone; PRINT_W: a Letter or A4 column
const CHART_MIN = 256, PRINT_W = 650;
let printW = 0;
const chartW = (node, fallback) => printW || Math.max(CHART_MIN, node.getBoundingClientRect().width || fallback);
// the floor and ceiling the stylesheet reserves for a chart's height (a phone on its side lowers them)
function heightRange(node) {
  const cs = getComputedStyle(node), lo = parseFloat(cs.minHeight), hi = parseFloat(cs.maxHeight);
  return [isFinite(lo) ? lo : 0, isFinite(hi) ? hi : Infinity];
}
function chartSize(svgSel, aspect, minH, maxH = Infinity) {
  const W = chartW(svgSel.node(), 600);
  const H = Math.min(maxH, Math.max(minH || 0, W * aspect));
  svgSel.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
  return [W, H];
}
// a chart's numbers as a table; a wide one scrolls and takes the keyboard
function tableFrom(el, head, rows, caption) {
  const t = d3.select(el); t.selectAll('*').remove();
  if (caption) t.append('caption').attr('class', 'sr-only').text(caption);
  t.append('thead').append('tr').selectAll('th').data(head).join('th').attr('scope', 'col').text((d) => d);
  t.append('tbody').selectAll('tr').data(rows).join('tr').each(function (r) {
    r.forEach((d, i) => { const c = document.createElement(i ? 'td' : 'th'); if (!i) c.scope = 'row'; c.textContent = d; this.appendChild(c); });
  });
  scroller(t.node().closest('.table-wrap'), caption);
}
function scroller(box, label) {
  if (!box) return;
  box.__label = label || 'Table of numbers';
  if (!box.__fit) {
    box.__fit = () => {
      if (box.scrollWidth > box.clientWidth + 1) { box.tabIndex = 0; box.setAttribute('role', 'region'); box.setAttribute('aria-label', box.__label); }
      else if (box.hasAttribute('tabindex')) { box.removeAttribute('tabindex'); box.removeAttribute('role'); box.removeAttribute('aria-label'); }
    };
    if ('ResizeObserver' in window) new ResizeObserver(box.__fit).observe(box);
  }
  box.__fit();
}
// sel.call(explain, html): a mouse hovers the mark; a tap on the chart opens the nearest mark's tip
function explain(sel, html) {
  sel.classed('has-tip', true).property('__tip', html)
    .on('pointermove', (ev) => { if (ev.pointerType !== 'touch') hoverTip(html, ev); })
    .on('pointerleave', (ev) => { if (ev.pointerType !== 'touch') leaveTip(); });
  const svg = sel.node().ownerSVGElement;
  if (svg && !svg.__taps) { svg.__taps = true; svg.addEventListener('click', tapChart); }
}
const REACH = 26;                                         // CSS pixels from a mark's edge
function tapChart(ev) {
  if (!byFinger(ev)) return;
  let best = null, bd = REACH;
  ev.currentTarget.querySelectorAll('.has-tip').forEach((el) => {
    const d = reach(el, ev.clientX, ev.clientY);
    if (d < bd) { bd = d; best = el; }
  });
  if (!best) return;
  best.classList.add('is-tapped');
  tapTip(best.__tip, ev, () => best.classList.remove('is-tapped'));
}
// screen distance from a point to a mark: a circle by its radius, a line by its segment, the rest by box
function reach(el, x, y) {
  const m = el.getScreenCTM();
  if (!m) return Infinity;
  const at = (u, v) => [m.a * u + m.c * v + m.e, m.b * u + m.d * v + m.f], n = (k) => +el.getAttribute(k) || 0;
  if (el.tagName === 'circle') {
    const [cx, cy] = at(n('cx'), n('cy'));
    return Math.max(0, Math.hypot(x - cx, y - cy) - n('r') * Math.hypot(m.a, m.b));
  }
  if (el.tagName === 'line') {
    const [x1, y1] = at(n('x1'), n('y1')), [x2, y2] = at(n('x2'), n('y2')), dx = x2 - x1, dy = y2 - y1, L = dx * dx + dy * dy;
    const t = L ? clamp(((x - x1) * dx + (y - y1) * dy) / L, 0, 1) : 0;
    return Math.hypot(x - x1 - t * dx, y - y1 - t * dy);
  }
  const r = el.getBoundingClientRect();
  return Math.hypot(Math.max(r.left - x, 0, x - r.right), Math.max(r.top - y, 0, y - r.bottom));
}
const redrawers = [];
function onResize(fn) {
  // the first chart adds the print path, after the page has set its print theme (initControls runs first)
  if (!redrawers.length) {
    addEventListener('beforeprint', () => { printW = PRINT_W; redrawers.forEach((f) => f()); });
    addEventListener('afterprint', () => { printW = 0; redrawers.forEach((f) => f()); });
  }
  redrawers.push(fn);
}
// redraw when the layout's width changes, and only then: Safari's Page Zoom changes it and tells only the visual
// viewport, while a pinch changes Safari's innerWidth but not the layout, so the width is read from the document
let rzT = 0, rzW = document.documentElement.clientWidth;
const onWidth = () => {
  const w = document.documentElement.clientWidth;
  if (w === rzW) return;
  rzW = w;
  clearTimeout(rzT); rzT = setTimeout(() => redrawers.forEach((f) => f()), 120);
};
window.addEventListener('resize', onWidth);
if (window.visualViewport) window.visualViewport.addEventListener('resize', onWidth);

// ====================================================================== the repack slope chart
function initSlope() {
  const R = D.repack, svg = d3.select('#slope');
  const ax0 = mean(R.ax0), ax1 = mean(R.ax1), pk0 = mean(R.pk0), pk1 = mean(R.pk1);
  $('#bnAx').textContent = sgn(ax1 - ax0, 4);
  $('#bnPk').textContent = sgn(pk1 - pk0, 3);
  $('#bnAxD').textContent = `Dice ${ax0.toFixed(4)} → ${ax1.toFixed(4)}`;
  $('#bnPkD').textContent = `Dice ${pk0.toFixed(4)} → ${pk1.toFixed(4)}`;
  tableFrom('#slopeTable', ['seed', 'PACK3D before', 'PACK3D after', 'Packed RoPE before', 'Packed RoPE after'],
    R.seeds.map((s, i) => [s, R.ax0[i].toFixed(4), R.ax1[i].toFixed(4), R.pk0[i].toFixed(4), R.pk1[i].toFixed(4)])
      .concat([['mean', ax0.toFixed(4), ax1.toFixed(4), pk0.toFixed(4), pk1.toFixed(4)]]),
    'Macro Dice per seed, on the training layout (before) and after the pure repack');
  const series = [
    { s0: R.pk0, s1: R.pk1, tint: 'var(--tint-coral)', col: 'var(--coral-mark)', name: 'Packed RoPE' },
    { s0: R.ax0, s1: R.ax1, tint: 'var(--tint-teal)', col: 'var(--teal-mark)', name: 'PACK3D' },
  ];
  let progress = 1, x, y, marks = [];
  // drawn once per width and theme; a replay frame only moves the lines' far ends (update)
  function draw() {
    if (printW) { run++; progress = 1; }                   // paper shows the repack done, never a frame of the replay
    svg.selectAll('*').remove();
    const [W, H] = chartSize(svg, 0.72, ...heightRange(svg.node()));
    const m = { l: 46, r: 104, t: 18, b: 38 };                // the right margin holds the series labels
    x = d3.scalePoint().domain(['before', 'after']).range([m.l + 30, W - m.r]);
    y = d3.scaleLinear().domain([0.75, 0.83]).range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').selectAll('line').data([0.76, 0.78, 0.8, 0.82]).join('line')
      .attr('x1', m.l).attr('x2', W - m.r + 12).attr('y1', y).attr('y2', y);
    svg.append('g').selectAll('text').data([0.76, 0.78, 0.8, 0.82]).join('text').attr('class', 'muted-t num')
      .attr('x', m.l - 8).attr('y', (d) => y(d) + 4).attr('text-anchor', 'end').text((d) => d.toFixed(2));
    svg.append('text').attr('x', m.l - 8).attr('y', m.t - 4).attr('text-anchor', 'end').attr('class', 'muted-t').text('Dice');
    const names = [['before', 'training layout'], ['after', 'pure repack']].map(([k, lab]) => {
      svg.append('line').attr('x1', x(k)).attr('x2', x(k)).attr('y1', m.t).attr('y2', H - m.b).style('stroke', 'var(--rule)').style('stroke-dasharray', '3 4');
      return svg.append('text').attr('x', x(k)).attr('y', H - 12).attr('text-anchor', 'middle').attr('class', 'lab-ink').text(lab);
    });
    // on a narrow chart the two names would run into each other, so each takes two lines
    if (names.reduce((s, t) => s + t.node().getComputedTextLength(), 0) / 2 + 10 > x('after') - x('before')) {
      names.forEach((t) => {
        const w = t.text().split(' ');
        t.text(null);
        t.append('tspan').attr('x', t.attr('x')).attr('y', H - 21).text(w[0]);
        t.append('tspan').attr('x', t.attr('x')).attr('y', H - 6).text(w.slice(1).join(' '));
      });
    }
    // seeds under every mean: both series start near 0.82, so one's seed hit lines would cover the other's mean dot
    const start = (l, a) => l.attr('x1', x('before')).attr('y1', y(a));
    const seedG = series.map(() => svg.append('g')), meanG = series.map(() => svg.append('g'));
    marks = series.map((S, si) => {
      const gS = seedG[si];
      const lines = S.s0.map((a, i) => {
        const b = S.s1[i];
        const seed = start(gS.append('line'), a).style('stroke', S.tint).style('stroke-width', 1.4);
        const hit = start(gS.append('line'), a).style('stroke', 'transparent').style('stroke-width', 10)
          .call(explain, `<b>${S.name}</b>, seed ${R.seeds[i]}<br>${a.toFixed(4)} → ${b.toFixed(4)} (${sgn(b - a, 4)})`);
        return [a, b, seed, hit];
      });
      const a = mean(S.s0), b = mean(S.s1), tipM = `<b>${S.name}</b>, mean of six seeds<br>${a.toFixed(4)} → ${b.toFixed(4)} (${sgn(b - a, 4)})`;
      const gM = meanG[si];
      const avg = start(gM.append('line'), a).style('stroke', S.col).style('stroke-width', 4).style('stroke-linecap', 'round').call(explain, tipM);
      gM.append('circle').attr('cx', x('before')).attr('cy', y(a)).attr('r', 6.5).style('fill', S.col).style('stroke', 'var(--surface)').style('stroke-width', 2).call(explain, tipM);
      const end = gM.append('circle').attr('r', 6.5).style('fill', S.col).style('stroke', 'var(--surface)').style('stroke-width', 2).call(explain, tipM);
      const name = gM.append('text').attr('x', x('after') + 12).attr('y', y(b) + 4).attr('class', 'lab-strong').text(S.name);
      return { lines, a, b, avg, end, name };
    });
    update();
  }
  function update() {
    const fx = x('before') + (x('after') - x('before')) * progress, fy = (a, b) => y(a + (b - a) * progress);
    marks.forEach((k) => {
      k.lines.forEach(([a, b, seed, hit]) => { seed.attr('x2', fx).attr('y2', fy(a, b)); hit.attr('x2', fx).attr('y2', fy(a, b)); });
      k.avg.attr('x2', fx).attr('y2', fy(k.a, k.b));
      k.end.attr('cx', fx).attr('cy', fy(k.a, k.b));
      // the names come in once the lines are within 1% of home
      k.name.style('visibility', progress >= 0.99 ? null : 'hidden');
    });
  }
  let run = 0;
  // the button's replay eases out; the chart's own eases in and out
  function replay(byHand) {
    if (RM) { progress = 1; update(); return; }
    const t0 = performance.now(), id = ++run, curve = byHand ? easeOut : ease;
    const step = (now) => { if (id !== run) return; progress = curve(clamp((now - t0) / 1600, 0, 1)); update(); if (progress < 1) requestAnimationFrame(step); };
    progress = 0; update(); requestAnimationFrame(step);
  }
  $('#replay').addEventListener('click', () => replay(true));
  if (RM) $('#replay').hidden = true;                      // nothing to replay: the chart is shown done, as the end hides Build it again
  onResize(draw); onTheme(draw);
  draw();
  // once, the first time the chart's top passes 60% of the screen, unless motion is paused
  if (!RM && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); if (!motion.paused) replay(false); } }, { rootMargin: '0px 0px -40% 0px' });
    io.observe(svg.node());
  }
}

// ====================================================================== how many predictions moved: the repack on a cell
// After the repack every changed prediction lights up, at the paper's rates, on the cell's boundaries (the paper
// does not map where they fall). WebGL draws one soft point per voxel, added like light. Its canvas is made new
// when the figure is built, never taken from the markup: Mobile Safari can refuse WebGL to a canvas that has sat in
// the page for a while, and gives one to a new canvas at once. A lost context is rebuilt; where WebGL cannot run,
// Canvas 2D draws the same points, still. Keep all four paths (docs: Moments).
function initRepackStage() {
  const stage = $('#repackStage'), cellsEl = stage && $('.sw-cells', stage);
  let canvas = $('#swCanvas');
  if (!stage || !cellsEl || !canvas) return;
  const R = D.repack, G = 64, NV = G * G * G;
  const rateAx = mean(R.chg_ax), ratePk = mean(R.chg_pk);
  const nAx = Math.round(rateAx / 100 * NV), nPk = Math.round(ratePk / 100 * NV);
  $('#swRA').textContent = `${rateAx.toFixed(4)}%`;
  $('#swRB').textContent = `${ratePk.toFixed(2)}%`;
  canvas.setAttribute('aria-label', `Two copies of one cell, ${intf(NV)} positions each, under the same repack. About ${nAx} predictions change under PACK3D, each circled, and about ${intf(nPk)} under packed RoPE. ${HOVERLESS ? 'Swipe sideways' : 'Drag'}, or use the arrow keys, to turn them.`);
  const go = $('#swGo'), stateEl = $('#swState'), stateT = $('#swStateT'), stateX = $('#swStateX'), cA = $('#swNA'), cB = $('#swNB');
  const cells = [$('#swA'), $('#swB')];
  let strips = [$('#swStripA'), $('#swStripB')];
  cA.dataset.max = intf(nAx); cB.dataset.max = intf(nPk);   // each count is as wide as its final value (the CSS reads it)
  // a token that is not a hex color keeps these
  const spark = (c, alt) => { const v = hex2rgb(c); return v.every((x) => x >= 0) ? v : alt; };
  const SPARK = { ax: spark(tok('--stage-mint'), [0.37, 0.88, 0.76]), pk: spark(getComputedStyle(stage).getPropertyValue('--coral').trim(), [1.0, 0.45, 0.47]) };

  // a new canvas in place of an old one, focus kept, and the old store let go at once (iOS counts a detached canvas
  // against its memory until it is collected)
  function swap(old) {
    const c = old.cloneNode(false), had = document.activeElement === old;
    old.replaceWith(c);
    old.width = old.height = 0;
    if (had) c.focus({ preventScroll: true });
    return c;
  }

  // ---------------------------------------------------------------- a cell, as a segmented volume (made once)
  // It runs in a worker, from its own source, so it uses nothing from outside itself. Square roots, not
  // Math.hypot, whose rounding differs between engines: the same seed gives the same cell and sparks everywhere.
  function makeScene(G, nAx, nPk) {
    const NV = G * G * G;
    let seed = 7;
    const rnd = () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    const wob = (x, y, z) => 0.5 * Math.sin(3.1 * x + 1.7) * Math.sin(2.6 * y + 0.4) * Math.sin(2.9 * z + 2.1) + 0.3 * Math.sin(5.3 * x + 1.1 * y + 2.0) * Math.cos(4.1 * z - 0.7 * y);
    const cls = new Uint8Array(NV);                   // 0 outside, 1 cytoplasm, 2 nucleus, 3 organelle
    const at = (x, y, z) => (z * G + y) * G + x, P = (v) => (v - G / 2 + 0.5) / (G / 2);
    const len = (a, b, c) => Math.sqrt(a * a + b * b + c * c);
    // the cell and its nucleus, two wobbly ellipsoids; the wobble moves their surfaces by less than 0.0561
    // and 0.0401, so it is worked out only near them
    for (let z = 0; z < G; z++) for (let y = 0; y < G; y++) for (let x = 0; x < G; x++) {
      const px = P(x), py = P(y), pz = P(z), d = len(px / 0.93, py / 0.74, pz / 0.66);
      if (d >= 1.0561 || (d >= 0.9439 && d + 0.07 * wob(px, py, pz) >= 1)) continue;
      const e = len((px - 0.16) / 0.42, (py + 0.04) / 0.35, (pz - 0.02) / 0.36);
      cls[at(x, y, z)] = e < 0.9599 || (e < 1.0401 && e + 0.05 * wob(py, pz, px) < 1) ? 2 : 1;
    }
    for (let m = 0; m < 40; m++) {                    // mitochondria: short walks through the cytoplasm
      let x = 0, y = 0, z = 0, tries = 0;
      do { x = 4 + Math.floor(rnd() * (G - 8)); y = 4 + Math.floor(rnd() * (G - 8)); z = 4 + Math.floor(rnd() * (G - 8)); } while (cls[at(x, y, z)] !== 1 && ++tries < 300);
      let dx = rnd() - 0.5, dy = rnd() - 0.5, dz = (rnd() - 0.5) * 0.6;
      for (let s = 0; s < 14; s++) {
        const i = at(Math.round(x), Math.round(y), Math.round(z));
        if (cls[i] !== 1) break;
        cls[i] = 3;
        dx += (rnd() - 0.5) * 0.5; dy += (rnd() - 0.5) * 0.5;
        const l = len(dx, dy, dz) || 1; x += dx / l; y += dy / l; z += (dz / l) * 0.8;
      }
    }
    // the classes counted along each row of G positions in memory, for the memory strips: a strip's pixels then mix
    // 4,096 rows on the main thread instead of reading all 262,144 positions
    const rows = new Uint8Array(NV / G * 4);
    for (let r = 0, i = 0; r < NV / G; r++) for (let x = 0; x < G; x++, i++) rows[r * 4 + cls[i]]++;
    // the six neighbours on the flat index (x ± 1, y ± G, z ± G²); past a face of the volume is outside
    const GG = G * G, M = G - 1;
    const differs = (i, x, y, z, c) => (x < M ? cls[i + 1] !== c : c !== 0) || (x > 0 ? cls[i - 1] !== c : c !== 0)
      || (y < M ? cls[i + G] !== c : c !== 0) || (y > 0 ? cls[i - G] !== c : c !== 0)
      || (z < M ? cls[i + GG] !== c : c !== 0) || (z > 0 ? cls[i - GG] !== c : c !== 0);
    const touches = (i, x, y, z, c) => (x < M && cls[i + 1] === c) || (x > 0 && cls[i - 1] === c)
      || (y < M && cls[i + G] === c) || (y > 0 && cls[i - G] === c)
      || (z < M && cls[i + GG] === c) || (z > 0 && cls[i - GG] === c);
    const memb = [], env = [], edge = [], pos = [], col = [], size = [], kind = [];
    const C = { cyto: [0.42, 0.30, 0.86], memb: [0.66, 0.54, 1.0], nuc: [0.08, 0.62, 0.52], env: [0.30, 0.92, 0.76], mito: [1.0, 0.86, 0.78] };
    const KINDS = [[C.memb, 0.36], [C.cyto, 0.03], [C.env, 0.26], [C.nuc, 0.085], [C.mito, 0.4]];
    const put = (x, y, z, kd, s) => {
      const j = () => (rnd() - 0.5) * 0.9 / (G / 2);
      const [rgb, k] = KINDS[kd];
      pos.push(P(x) + j(), P(y) + j(), P(z) + j()); col.push(rgb[0] * k, rgb[1] * k, rgb[2] * k); size.push(s); kind.push(kd);
    };
    for (let z = 0, i = 0; z < G; z++) for (let y = 0; y < G; y++) for (let x = 0; x < G; x++, i++) {
      const c = cls[i];
      if (c === 0) { if (differs(i, x, y, z, 0)) edge.push([x, y, z]); continue; }
      if (c === 1) {
        if (differs(i, x, y, z, 1) && !touches(i, x, y, z, 2) && !touches(i, x, y, z, 3)) { memb.push([x, y, z]); if (rnd() < 0.55) put(x, y, z, 0, 1.5); }
        else if (rnd() < 0.08) put(x, y, z, 1, 3.4);
      } else if (c === 2) {
        if (differs(i, x, y, z, 2)) { env.push([x, y, z]); if (rnd() < 0.6) put(x, y, z, 2, 1.6); }
        else if (rnd() < 0.2) put(x, y, z, 3, 2.6);
      } else put(x, y, z, 4, 1.4);
    }
    // the predictions the repack changes, at the paper's rates over all 262,144 positions
    const pick = (list, k) => { const a = list.slice(), out = []; for (let i = 0; i < k && a.length; i++) out.push(a.splice(Math.floor(rnd() * a.length), 1)[0]); return out; };
    const sparksPk = pick(memb.concat(env, edge), nPk), sparksAx = pick(env, nAx);
    const sparkSet = (list) => {
      const p = new Float32Array(list.length * 3), t = new Float32Array(list.length);
      list.forEach(([x, y, z], i) => { p.set([P(x), P(y), P(z)], i * 3); t[i] = rnd() * 0.75; });
      return { n: list.length, pos: p, t };
    };
    return {
      rows, NP: size.length, pos: new Float32Array(pos), col: new Float32Array(col), size: new Float32Array(size), kind: new Uint8Array(kind),
      kinds: KINDS.map(([rgb, k]) => rgb.map((v) => v * k)), pk: sparkSet(sparksPk), ax: sparkSet(sparksAx),
    };
  }

  // ---------------------------------------------------------------- the camera (shared by both renderers)
  const persp = (f, a, nn, fa) => { const t = 1 / Math.tan(f / 2); return [t / a, 0, 0, 0, 0, t, 0, 0, 0, 0, (fa + nn) / (nn - fa), -1, 0, 0, 2 * fa * nn / (nn - fa), 0]; };
  const mul = (a, b) => { const o = new Array(16).fill(0); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o; };
  const viewM = (yaw, pitch, d) => {
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    return [cy, sp * sy, -cp * sy, 0, 0, cp, sp, 0, sy, -sp * cy, cp * cy, 0, 0, 0, -d, 1];
  };
  // one cell's viewport, in device pixels from the canvas's top left, and its camera
  function camera(v, dpr, yaw, pitch) {
    const w = v.w * dpr, h = v.h * dpr, dist = 3.45 / Math.min(1, w / h);
    return { x: v.x * dpr, y: v.y * dpr, w, h, dist, mvp: mul(persp(0.62, w / h, 0.1, 40), viewM(yaw, pitch, dist)), vox: (2 / G) * (h / 2) / Math.tan(0.31) };
  }

  // ---------------------------------------------------------------- WebGL
  const VS = `attribute vec3 a_pos; attribute vec3 a_col; attribute float a_size; attribute float a_t;
uniform mat4 u_mvp; uniform float u_vox, u_k, u_time, u_mode, u_dist, u_maxpt; uniform vec3 u_spark;
varying vec3 v_col; varying float v_ring;
void main() {
  vec4 p = u_mvp * vec4(a_pos, 1.0);
  gl_Position = p;
  float fog = clamp((p.w - u_dist + 0.95) / 1.9, 0.0, 1.0);
  float size;
  if (u_mode < 0.5) { v_col = a_col * mix(1.2, 0.5, fog); v_ring = 0.0; size = a_size * u_vox / p.w; }
  else {
    float d = (u_k - a_t) * 7.0;                       // d * d, not pow(d, 2.0): pow is undefined for d < 0
    float k = clamp((u_k - a_t) * 3.0, 0.0, 1.0);
    float flare = 1.0 + 1.6 * exp(-d * d) * step(a_t, u_k);
    float tw = 0.85 + 0.15 * sin(u_time * 5.0 + a_t * 40.0);
    v_col = u_spark * k * tw * flare * mix(1.0, 0.6, fog);
    v_ring = u_mode > 1.5 ? 1.0 : 0.0;
    size = (u_mode > 1.5 ? 5.2 : (1.5 + 1.1 * (flare - 1.0))) * u_vox / p.w * k;
  }
  gl_PointSize = min(size, u_maxpt);
}`;
  const FS = `precision mediump float; varying vec3 v_col; varying float v_ring;
void main() {
  float r = length(gl_PointCoord - 0.5) * 2.0;
  float a = v_ring > 0.5 ? smoothstep(0.74, 0.82, r) * (1.0 - smoothstep(0.88, 0.98, r)) * 0.95 : exp(-r * r * 4.0) * step(r, 1.0);
  vec3 c = v_col * a;
  gl_FragColor = vec4(c, max(c.r, max(c.g, c.b)));   // valid premultiplied light over the stage
}`;
  const GL_ATTRS = { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false, preserveDrawingBuffer: false, powerPreference: 'low-power' };
  // a WebGL renderer on canvas cv, or null. setup() can run again on the same context after a restore.
  function glRenderer(cv, S) {
    let gl = null;
    try { gl = cv.getContext('webgl', GL_ATTRS) || cv.getContext('experimental-webgl', GL_ATTRS); } catch (e) { gl = null; }
    if (!gl || gl.isContextLost()) return null;
    let X = null;
    function setup() {
      const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS) && !gl.isContextLost()) throw new Error(gl.getShaderInfoLog(o)); return o; };
      const prog = gl.createProgram();
      gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS) && !gl.isContextLost()) throw new Error(gl.getProgramInfoLog(prog));
      gl.useProgram(prog);
      const U = {}; ['u_mvp', 'u_vox', 'u_k', 'u_time', 'u_mode', 'u_dist', 'u_spark', 'u_maxpt'].forEach((n) => { U[n] = gl.getUniformLocation(prog, n); });
      const buf = (arr, n, name) => { const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, arr, gl.STATIC_DRAW); return { b, n, l: gl.getAttribLocation(prog, name) }; };
      const set = (p, t, n) => [buf(p, 3, 'a_pos'), buf(new Float32Array(n * 3), 3, 'a_col'), buf(new Float32Array(n).fill(1), 1, 'a_size'), buf(t, 1, 'a_t')];
      X = {
        U, cell: [buf(S.pos, 3, 'a_pos'), buf(S.col, 3, 'a_col'), buf(S.size, 1, 'a_size'), buf(new Float32Array(S.NP), 1, 'a_t')],
        pk: set(S.pk.pos, S.pk.t, S.pk.n), ax: set(S.ax.pos, S.ax.t, S.ax.n),
        maxpt: (gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE) || [1, 64])[1],
      };
      gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE); gl.clearColor(0, 0, 0, 0);
    }
    try { setup(); } catch (e) { console.warn('repack stage: WebGL setup failed', e); return null; }
    const bind = (bs) => bs.forEach((x) => { if (x.l < 0) return; gl.bindBuffer(gl.ARRAY_BUFFER, x.b); gl.enableVertexAttribArray(x.l); gl.vertexAttribPointer(x.l, x.n, gl.FLOAT, false, 0, 0); });
    return {
      lost: () => gl.isContextLost(),
      dispose() { const x = gl.getExtension('WEBGL_lose_context'); if (x && !gl.isContextLost()) x.loseContext(); },   // free the GPU now, not at GC
      restore() { try { setup(); return true; } catch (e) { console.warn('repack stage: WebGL restore failed', e); return false; } },
      draw(f) {
        const { U } = X;
        gl.viewport(0, 0, cv.width, cv.height); gl.clear(gl.COLOR_BUFFER_BIT);
        f.views.forEach((v, side) => {
          const c = camera(v, f.dpr, f.yaw, f.pitch);
          if (c.w < 2 || c.h < 2) return;
          gl.viewport(c.x, cv.height - c.y - c.h, c.w, c.h);
          gl.uniformMatrix4fv(U.u_mvp, false, c.mvp);
          gl.uniform1f(U.u_dist, c.dist); gl.uniform1f(U.u_vox, c.vox); gl.uniform1f(U.u_maxpt, X.maxpt);
          gl.uniform1f(U.u_time, (f.now / 1000) % 1256.6370614359173);   // a whole number of twinkles, so the wrap is seamless
          gl.uniform1f(U.u_mode, 0); bind(X.cell); gl.drawArrays(gl.POINTS, 0, S.NP);
          gl.uniform1f(U.u_k, f.kSpark);
          if (side === 1) { gl.uniform3f(U.u_spark, ...SPARK.pk); gl.uniform1f(U.u_mode, 1); bind(X.pk); gl.drawArrays(gl.POINTS, 0, S.pk.n); }
          else {
            gl.uniform3f(U.u_spark, ...SPARK.ax); gl.uniform1f(U.u_mode, 1); bind(X.ax); gl.drawArrays(gl.POINTS, 0, S.ax.n);
            gl.uniform1f(U.u_mode, 2); gl.drawArrays(gl.POINTS, 0, S.ax.n);   // circled: one in 14,000 is too small to see
          }
        });
      },
    };
  }

  // ---------------------------------------------------------------- Canvas 2D: the same points, for a reader without WebGL
  // drawn only when something changes, so the figure at rest costs nothing
  function ctx2dRenderer(cv, S) {
    const g = cv.getContext('2d');
    if (!g) return null;
    const SPR = 32;
    const bake = (rgb, ring) => {                         // the fragment shader, at 32 x 32, premultiplied by hand
      const c = document.createElement('canvas'); c.width = c.height = SPR;
      const x = c.getContext('2d'), img = x.createImageData(SPR, SPR);
      for (let j = 0; j < SPR; j++) for (let i = 0; i < SPR; i++) {
        const r = Math.hypot((i + 0.5) / SPR - 0.5, (j + 0.5) / SPR - 0.5) * 2;
        const ss = (a, b, v) => { const t = clamp((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
        const a = ring ? ss(0.74, 0.82, r) * (1 - ss(0.88, 0.98, r)) * 0.95 : (r <= 1 ? Math.exp(-r * r * 4) : 0);
        const p = rgb.map((v) => Math.min(1, v * a)), al = Math.max(...p);
        if (al > 0) img.data.set([p[0] / al * 255, p[1] / al * 255, p[2] / al * 255, al * 255], (j * SPR + i) * 4);
      }
      x.putImageData(img, 0, 0); return c;
    };
    const cellSpr = S.kinds.map((rgb) => bake(rgb.map((v) => v * 1.2)));
    const pkSpr = bake(SPARK.pk), axSpr = bake(SPARK.ax), ringSpr = bake(SPARK.ax, true);
    const project = (m, x, y, z) => { const w = m[3] * x + m[7] * y + m[11] * z + m[15]; return [(m[0] * x + m[4] * y + m[8] * z + m[12]) / w, (m[1] * x + m[5] * y + m[9] * z + m[13]) / w, w]; };
    function dots(c, pos, n, each) {
      for (let i = 0; i < n; i++) {
        const [nx, ny, w] = project(c.mvp, pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]);
        if (w <= 0) continue;
        each(i, c.x + (nx * 0.5 + 0.5) * c.w, c.y + (0.5 - ny * 0.5) * c.h, w, clamp((w - c.dist + 0.95) / 1.9, 0, 1));
      }
    }
    // a layer kept until the camera or the layout changes; a drag draws every third point, the release all of them
    const layer = document.createElement('canvas'), lg = layer.getContext('2d');
    let key = '';
    cv.addEventListener('contextrestored', () => { key = ''; kick(); });   // a 2D context given back blank
    function cellsInto(f, stride) {
      if (layer.width !== cv.width || layer.height !== cv.height) { layer.width = cv.width; layer.height = cv.height; }
      lg.setTransform(1, 0, 0, 1, 0, 0); lg.globalCompositeOperation = 'source-over'; lg.globalAlpha = 1;
      lg.clearRect(0, 0, layer.width, layer.height);
      lg.globalCompositeOperation = 'lighter';
      f.views.forEach((v) => {
        const c = camera(v, f.dpr, f.yaw, f.pitch);
        if (c.w < 2 || c.h < 2) return;
        lg.save(); lg.beginPath(); lg.rect(c.x, c.y, c.w, c.h); lg.clip();
        for (let i = 0; i < S.NP; i += stride) {
          const [nx, ny, w] = project(c.mvp, S.pos[i * 3], S.pos[i * 3 + 1], S.pos[i * 3 + 2]);
          if (w <= 0) continue;
          const x = c.x + (nx * 0.5 + 0.5) * c.w, y = c.y + (0.5 - ny * 0.5) * c.h, fog = clamp((w - c.dist + 0.95) / 1.9, 0, 1);
          const s = Math.max(1, S.size[i] * c.vox / w);
          lg.globalAlpha = Math.min(1, (1.2 + (0.5 - 1.2) * fog) / 1.2 * (stride > 1 ? 1.8 : 1));
          lg.drawImage(cellSpr[S.kind[i]], x - s / 2, y - s / 2, s, s);
        }
        lg.restore();
      });
      lg.globalCompositeOperation = 'source-over'; lg.globalAlpha = 1;
    }
    return {
      still: true, lost: () => false, restore: () => true, dispose() { layer.width = layer.height = 0; },
      draw(f) {
        const stride = f.drag ? 3 : 1;
        const k = [f.yaw, f.pitch, f.dpr, cv.width, cv.height, stride, f.lv].join();
        if (k !== key) { key = k; cellsInto(f, stride); }
        g.setTransform(1, 0, 0, 1, 0, 0);
        g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
        g.clearRect(0, 0, cv.width, cv.height);
        g.drawImage(layer, 0, 0);
        if (f.kSpark <= 0) return;
        g.globalCompositeOperation = 'lighter';
        f.views.forEach((v, side) => {
          const c = camera(v, f.dpr, f.yaw, f.pitch);
          if (c.w < 2 || c.h < 2) return;
          const set = side ? S.pk : S.ax, spr = side ? pkSpr : axSpr;
          dots(c, set.pos, set.n, (i, x, y, w, fog) => {
            const kk = clamp((f.kSpark - set.t[i]) * 3, 0, 1);
            if (kk <= 0) return;
            const s = Math.max(1, 1.5 * c.vox / w * kk);
            g.globalAlpha = Math.min(1, kk * (1 + (0.6 - 1) * fog));
            g.drawImage(spr, x - s / 2, y - s / 2, s, s);
            if (!side) { const r = 5.2 * c.vox / w * kk; g.drawImage(ringSpr, x - r / 2, y - r / 2, r, r); }
          });
        });
        g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
      },
    };
  }

  // ---------------------------------------------------------------- the story: the training layout, the repack, the changes
  // Each phase eases from where the figure stands, so a press midway turns it there; a press eases out, faster.
  const D_ = { repack: 1700, restore: 1100, fade: 500 }, BY_HAND = { repack: 1000, restore: 700 };
  const STATE = {
    before: 'Training layout: raster order',
    repack: 'Repacking: the same 262,144 tokens, moved in memory in 16 groups',
    after: 'Repacked. The same cell, the same two models, a new memory order',
    restore: 'Back to the training layout',
  };
  const HEARD = `. ${intf(nAx)} predictions changed under PACK3D, ${intf(nPk)} under packed RoPE.`;   // read out after "Repacked"; on screen the counts say it
  let phase = 'before', t0 = 0, from = { s: 0, k: 0, c: 0 }, cur = from, played = false, curve = ease, span = D_.repack;
  let S = null, rd = null, raf = 0, last = 0, shown = [0, 0], stripsAt = -1;
  let yaw = 0.6, pitch = 0.42, drag = null, dpr = 1, views = [], lv = 0, onScreen = false, wellInView = false, autoT = 0;
  const write = (el, t) => { if (el && el.textContent !== t) el.textContent = t; };
  // the markup holds the two longest states unseen; written from STATE, so they cannot drift
  $$('.sw-hold', stateEl).forEach((el, i) => write(el, [STATE.repack, STATE.after][i]));
  function setPhase(p, now = performance.now(), byHand = false) {
    from = cur;                                         // where the figure stands now
    phase = RM && p === 'repack' ? 'after' : RM && p === 'restore' ? 'before' : p;
    t0 = now;
    if (phase === 'repack' || phase === 'restore') { curve = byHand ? easeOut : ease; span = (byHand ? BY_HAND : D_)[phase]; }
    stateEl.classList.toggle('hot', phase === 'after');
    write(stateT, STATE[phase]);
    write(stateX, phase === 'after' ? HEARD : '');
    write(go, phase === 'after' || phase === 'repack' ? 'Restore the training layout' : 'Repack the memory');
    kick();
  }
  // where the figure stands at a time: s how far the memory is repacked, k the sparks, c the counts
  function standAt(now) {
    const e = Math.max(0, now - t0), fade = Math.max(0, 1 - e / D_.fade);
    if (phase === 'repack') return { s: from.s + (1 - from.s) * curve(Math.min(1, e / span)), k: from.k * fade, c: from.c * fade };
    if (phase === 'after') return { s: 1, k: RM ? 1.4 : Math.min(1.4, e / 900), c: RM ? 1 : Math.min(1, e / 1100) };
    if (phase === 'restore') return { s: from.s * (1 - curve(Math.min(1, e / span))), k: from.k * fade, c: from.c * fade };
    return { s: 0, k: 0, c: 0 };
  }
  // the status line speaks only for the reader: playing by itself turns its voice off, a press turns it on
  const voice = (on) => stateEl.setAttribute('aria-live', on ? 'polite' : 'off');
  go.addEventListener('click', () => { played = true; voice(true); setPhase(phase === 'after' || phase === 'repack' ? 'restore' : 'repack', performance.now(), true); });

  function kick() { if (!raf && !(rd && rd.lost())) raf = requestAnimationFrame(frame); }   // no renderer at all: the counts and strips still run
  function frame(now) {
    raf = 0;
    if (rd && rd.lost()) return;
    const dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
    if (phase === 'repack' && now - t0 > span) setPhase('after', now);
    else if (phase === 'restore' && now - t0 > span) setPhase('before', now);
    cur = standAt(now);
    const still = !rd || rd.still || motion.paused;    // paused, reduced or drawn in 2D: the cells turn only by hand
    if (!still && !drag) yaw += dt * 0.12;
    paint(now);
    const moving = phase === 'repack' || phase === 'restore' || (phase === 'after' && now - t0 < 1500);
    if (onScreen && (!still || moving || drag)) kick();
  }
  // counts written only when they change, strips only once the repack has moved; it reads no layout
  function paint(now) {
    const nA = Math.round(cur.c * nAx), nB = Math.round(cur.c * nPk);
    if (nA !== shown[0]) { shown[0] = nA; cA.textContent = intf(nA); }
    if (nB !== shown[1]) { shown[1] = nB; cB.textContent = intf(nB); }
    if (rd) rd.draw({ views, dpr, yaw, pitch, kSpark: cur.k, now, drag: !!drag, lv });
    if (cur.s !== stripsAt) drawStrips(cur.s);
  }

  // ---------------------------------------------------------------- the memory strips: all positions in raster order
  const SEG = 16, perm = [9, 3, 14, 0, 11, 6, 1, 13, 4, 15, 7, 2, 12, 5, 10, 8];
  const SCOL = [[22, 28, 27], [96, 78, 150], [26, 150, 124], [235, 228, 240]];
  let stripSrc = null, sg = [];
  function stripImage(w) {                              // each pixel the mean color of the positions it covers
    if (stripSrc) stripSrc.width = 0;
    const can = document.createElement('canvas'); can.width = w; can.height = 1;
    const c2 = can.getContext('2d'); if (!c2) return null;
    // from the worker's counts per row of 64 positions; a row split by a pixel's edge counts by the part it covers
    const img = c2.createImageData(w, 1), n = new Float64Array(4), rows = S.rows, nr = rows.length / 4;
    for (let px = 0; px < w; px++) {
      const a = px / w * nr, b = (px + 1) / w * nr;
      n.fill(0);
      for (let r = Math.floor(a); r < b; r++) { const f = Math.min(b, r + 1) - Math.max(a, r); for (let c = 0; c < 4; c++) n[c] += rows[r * 4 + c] * f; }
      const k = n[0] + n[1] + n[2] + n[3] || 1;
      for (let ch = 0; ch < 3; ch++) img.data[px * 4 + ch] = (n[0] * SCOL[0][ch] + n[1] * SCOL[1][ch] + n[2] * SCOL[2][ch] + n[3] * SCOL[3][ch]) / k;
      img.data[px * 4 + 3] = 255;
    }
    c2.putImageData(img, 0, 0); return can;
  }
  function drawStrips(s) {
    stripsAt = s;
    if (!stripSrc) return;
    strips.forEach((cv, i) => {
      const g2 = sg[i]; if (!g2) return;
      const w = cv.width, h = cv.height, sw = w / SEG;
      g2.clearRect(0, 0, w, h); g2.imageSmoothingEnabled = false;
      for (let k = 0; k < SEG; k++) g2.drawImage(stripSrc, k * stripSrc.width / SEG, 0, stripSrc.width / SEG, 1, (k + (perm.indexOf(k) - k) * s) * sw, 0, sw + 0.5, h);
    });
  }

  // measured when sizes change, never in a frame; drawn at once, since a resized canvas is blank
  function layout() {
    const cr = cellsEl.getBoundingClientRect(), W = cr.width, H = cr.height;
    dpr = Math.min(2, window.devicePixelRatio || 1, Math.sqrt(3e6 / Math.max(1, W * H)));   // at most 3 Mpx
    const bw = Math.round(W * dpr), bh = Math.round(H * dpr);
    if (canvas.width !== bw || canvas.height !== bh) { canvas.width = bw; canvas.height = bh; }
    views = cells.map((el) => { const r = el.getBoundingClientRect(); return { x: r.left - cr.left, y: r.top - cr.top, w: r.width, h: r.height }; });
    lv++;
    const sd = Math.min(2, window.devicePixelRatio || 1);
    strips.forEach((s) => { const w = Math.round(s.clientWidth * sd), h = Math.round(s.clientHeight * sd); if (s.width !== w || s.height !== h) { s.width = w; s.height = h; } });
    const sw = Math.max(64, strips[0].width);
    if (S && (!stripSrc || stripSrc.width !== sw)) stripSrc = stripImage(sw);   // only when the width changes
    stripsAt = -1;
    if (!(rd && rd.lost())) paint(performance.now());
    kick();
  }

  // ---------------------------------------------------------------- the renderer: WebGL, else Canvas 2D, else words
  let fails = 0, born = 0, lostT = 0;
  function useGL() {                                    // always on a new canvas
    if (fails >= 3) return false;                       // three contexts refused, or lost young: Canvas 2D from here on
    const old = rd;
    canvas = swap(canvas);
    if (old) old.dispose();                             // after the swap, so its 'lost' event is ignored
    rd = glRenderer(canvas, S);
    if (!rd) { fails++; return false; }
    born = performance.now(); watch(canvas); stage.classList.remove('no-canvas');
    return true;
  }
  function use2D() {
    const old = rd;
    canvas = swap(canvas);
    if (old) old.dispose();
    rd = ctx2dRenderer(canvas, S);
    stage.classList.toggle('no-canvas', !rd);           // no canvas at all: the words in the cells' place; the counts, strips and button still run
    return !!rd;
  }
  function start() {                                    // WebGL now, again a frame later, then Canvas 2D
    if (useGL()) return;                                // the observer's first call lays it out
    requestAnimationFrame(() => { if (!useGL()) use2D(); layout(); });
  }
  function watch(cv) {
    cv.addEventListener('webglcontextlost', (e) => {
      e.preventDefault();                               // ask the browser to give it back
      if (cv !== canvas) return;                        // a canvas already replaced
      cancelAnimationFrame(raf); raf = 0;
      fails = performance.now() - born < 5000 ? fails + 1 : 0;
      if (!document.hidden) recoverSoon();
    });
    cv.addEventListener('webglcontextrestored', () => {
      if (cv !== canvas) return;
      clearTimeout(lostT);
      born = performance.now();
      if (rd.restore()) layout(); else replace();
    });
  }
  // a context lost and not given back (iOS often never gives one back): a new canvas and a new context
  function replace() {
    clearTimeout(lostT);
    if (!useGL()) use2D();
    layout();
  }
  // a loss in view may be given back in a moment (a GPU process restarting); one found on return seldom is
  function recoverSoon(ms = 1500) { clearTimeout(lostT); lostT = setTimeout(() => { if (rd && rd.lost()) replace(); }, ms); }
  const onReturn = () => { if (!document.hidden && rd && rd.lost()) recoverSoon(300); };

  function build() {
    // the strips' contexts, made once; a strip that is refused one is given a new canvas, then put away
    sg = strips.map((s, i) => s.getContext('2d') || (strips[i] = swap(s)).getContext('2d'));
    strips.forEach((s, i) => { if (!sg[i]) s.parentElement.hidden = true; });
    strips.forEach((s) => s.addEventListener('contextrestored', () => { stripsAt = -1; kick(); }));
    start();
    // one layout per frame, starting a frame later, so it stays out of the task that took the volume in
    const ro = new ResizeObserver(() => layout());
    requestAnimationFrame(() => requestAnimationFrame(() => [cellsEl, ...cells, ...strips.map((s) => s.parentElement)].forEach((el) => ro.observe(el))));
    onDpr(layout);
    document.addEventListener('visibilitychange', onReturn);
    window.addEventListener('pageshow', onReturn);
    autoplay();
  }

  // ---------------------------------------------------------------- the volume: made in a worker, once, when the reader gets near
  function makeSoon() {
    let w = null, url = '', over = false, late = 0;
    const done = (s) => {
      if (over) return;
      over = true; clearTimeout(late);
      if (w) w.terminate();
      if (url) URL.revokeObjectURL(url);
      if (s) { S = s; build(); } else setTimeout(() => { S = makeScene(G, nAx, nPk); build(); }, 0);   // no worker: here, once
    };
    try {
      const src = `'use strict';const makeScene=${makeScene};self.onmessage=(e)=>{const s=makeScene(...e.data);self.postMessage(s,[s.rows,s.pos,s.col,s.size,s.kind,s.pk.pos,s.pk.t,s.ax.pos,s.ax.t].map((a)=>a.buffer));};`;
      url = URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
      w = new Worker(url);
      w.onmessage = (e) => done(e.data);
      w.onerror = w.onmessageerror = (e) => { e.preventDefault(); done(null); };
      late = setTimeout(() => done(null), 8000);        // a worker that never answers
      w.postMessage([G, nAx, nPk]);
    } catch (e) { done(null); }
  }
  new IntersectionObserver((es, io) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); makeSoon(); } }, { rootMargin: '1500px 0px' }).observe(stage);

  // ---------------------------------------------------------------- turning the cells by hand
  // on the cells' box, so a new canvas needs no listeners of its own
  const turned = () => { played = true; motion.set(true); };
  cellsEl.addEventListener('pointerdown', (e) => {
    if (e.target !== canvas || e.button !== 0) return;   // a right click opens the menu; it does not turn
    if (drag) { dropDrag(); return; }                    // a second finger: a pinch, which zooms the page
    drag = { x: e.clientX, y: e.clientY, yaw, pitch, id: e.pointerId, moved: false, finger: e.pointerType !== 'mouse' };
    try { canvas.setPointerCapture(e.pointerId); } catch (err) { /* the pointer is already gone */ }
    canvas.classList.add('grabbing');
  });
  cellsEl.addEventListener('pointermove', (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    if (e.pointerType === 'mouse' && !(e.buttons & 1)) { endDrag(); return; }   // the button came up where we could not hear it
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y, ax = Math.abs(dx), ay = Math.abs(dy);
    if (!drag.moved && (drag.finger ? ax < 8 || ax < ay : ax < 4 && ay < 4)) return;   // a finger turns only sideways
    drag.moved = true;
    yaw = drag.yaw + dx * 0.008; pitch = clamp(drag.pitch + dy * 0.006, -0.4, 1.3); kick();
  });
  const endDrag = () => { if (!drag) return; if (drag.moved) turned(); drag = null; canvas.classList.remove('grabbing'); kick(); };
  const dropDrag = () => { if (!drag) return; ({ yaw, pitch } = drag); drag = null; canvas.classList.remove('grabbing'); kick(); };
  cellsEl.addEventListener('pointerup', endDrag);
  cellsEl.addEventListener('lostpointercapture', endDrag);
  cellsEl.addEventListener('pointercancel', dropDrag);
  cellsEl.addEventListener('keydown', (e) => {
    const d = e.target === canvas && !e.altKey && !e.ctrlKey && !e.metaKey && { ArrowLeft: [-0.2, 0], ArrowRight: [0.2, 0], ArrowUp: [0, -0.1], ArrowDown: [0, 0.1] }[e.key];
    if (!d) return;
    e.preventDefault();
    turned();
    yaw += d[0]; pitch = clamp(pitch + d[1], -0.4, 1.3); kick();
  });

  // ---------------------------------------------------------------- playing by itself
  function autoplay() {
    if (played || autoT || motion.paused || !wellInView || !S) return;
    autoT = setTimeout(() => { autoT = 0; if (!played && phase === 'before' && !motion.paused && wellInView) { played = true; voice(false); setPhase('repack'); } }, 700);
  }
  new IntersectionObserver((es) => {
    const e = es[es.length - 1];
    onScreen = e.isIntersecting; wellInView = onScreen && e.intersectionRatio > 0.45;
    if (onScreen) { last = 0; kick(); autoplay(); }
  }, { threshold: [0, 0.45, 0.7] }).observe(stage);
  motion.on((paused) => { last = 0; kick(); if (!paused) autoplay(); });
  // focus in the window stops its autoplay, so the button's name never changes under focus
  stage.addEventListener('focusin', () => { if (!played) { played = true; clearTimeout(autoT); autoT = 0; } });

  setPhase(RM ? 'after' : 'before');                    // reduced motion: a still of the result, which still answers the button
  if (RM) played = true;
  stateEl.setAttribute('role', 'status');               // from here on a change of state is read out; the first, above, is not
}

// ====================================================================== named switch
function initNamed() {
  const svg = d3.select('#named'), n = D.named;
  const rows = [['PACK3D', n.ax1 - n.ax0, 'var(--teal-mark)', n.ax0, n.ax1], ['Packed RoPE', n.pk1 - n.pk0, 'var(--coral-mark)', n.pk0, n.pk1]];
  function draw() {
    svg.selectAll('*').remove();
    const [W] = chartSize(svg, 0, 120);
    const H = 120, m = { l: 110, r: 70 };
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const x = d3.scaleLinear().domain([-0.09, 0]).range([m.l, W - m.r]);
    (W < 280 ? [-0.08, 0] : W < 480 ? [-0.08, -0.04, 0] : [-0.08, -0.06, -0.04, -0.02, 0]).forEach((t) => {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', 10).attr('y2', H - 24).style('stroke', t === 0 ? 'var(--ink)' : 'var(--grid)').style('stroke-width', t === 0 ? 1.5 : 1);
      svg.append('text').attr('x', x(t)).attr('y', H - 8).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(t === 0 ? '0' : fix(t, 2));
    });
    rows.forEach(([name, v, col, a, b], i) => {
      const yy = 22 + i * 38;
      svg.append('text').attr('x', m.l - 12).attr('y', yy + 13).attr('text-anchor', 'end').attr('class', 'lab-ink').text(name);
      const bw = Math.max(1.5, x(0) - x(v));
      svg.append('rect').attr('x', x(0) - bw).attr('y', yy).attr('width', bw).attr('height', 18).attr('rx', 3).style('fill', col)
        .call(explain, `<b>${name}</b>, named switch<br>${a.toFixed(4)} → ${b.toFixed(4)}`);
      svg.append('text').attr('x', x(0) + 8).attr('y', yy + 13).attr('class', 'lab-strong num').text(fix(v, 4));
    });
  }
  onResize(draw); draw();
}

// ====================================================================== MSD
function initMSD() {
  const svg = d3.select('#msdChart'), M = D.msd, R = D.repack;
  const groups = [
    ['Allen-15 microscopy · 6 seeds', [['PACK3D', R.chg_ax, 'var(--teal-mark)'], ['Packed RoPE', R.chg_pk, 'var(--coral-mark)']]],
    ['MSD Heart (MRI) · 3 seeds', [['PACK3D', M.heart_ax, 'var(--teal-mark)'], ['Separable PE', M.heart_sep, 'var(--lav)'], ['Packed RoPE', M.heart_pk, 'var(--coral-mark)']]],
    ['MSD Spleen (CT) · 3 seeds', [['PACK3D', M.spleen_ax, 'var(--teal-mark)'], ['Separable PE', M.spleen_sep, 'var(--lav)'], ['Packed RoPE', M.spleen_pk, 'var(--coral-mark)']]],
  ];
  const pct = (v) => (v < 0.01 ? v.toFixed(4) : v.toFixed(3));
  const task = ['Allen-15', 'MSD Heart', 'MSD Spleen'];
  tableFrom('#msdTable', ['task, encoding', 'mean', 'seed 1', 'seed 2', 'seed 3', 'seed 4', 'seed 5', 'seed 6'],
    groups.flatMap(([, rows], g) => rows.map(([name, vals]) => [`${task[g]}, ${name}`, pct(mean(vals))].concat([0, 1, 2, 3, 4, 5].map((i) => (i < vals.length ? pct(vals[i]) : ''))))),
    'Predictions changed by the pure repack, in % of positions: the mean and each seed');
  function draw() {
    svg.selectAll('*').remove();
    const W = chartW(svg.node(), 700);
    const narrow = W < 560;
    // rows 26px apart under heads of 30; sideways they close up, no closer than 19 and 24
    const maxH = heightRange(svg.node())[1], rows = groups.reduce((s, g) => s + g[1].length, 0);
    const headH = clamp(30 * (maxH - 64) / (groups.length * 30 + rows * 26), 24, 30), rowH = clamp((maxH - 64 - groups.length * headH) / rows, 19, 26);
    const H = 30 + groups.reduce((s, g) => s + headH + g[1].length * rowH, 0) + 34;
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const m = { l: narrow ? 104 : 150, r: 16 };
    const x = d3.scaleLog().domain([0.0008, 2.5]).range([m.l, W - m.r]);
    const top = 16, bot = H - 30;
    [0.001, 0.01, 0.1, 1].forEach((t) => {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top).attr('y2', bot).style('stroke', 'var(--grid)');
      if (W >= 330 || t === 0.01 || t === 1) svg.append('text').attr('x', x(t)).attr('y', bot + 18).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(t + '%');
    });
    let yy = top + 8;
    groups.forEach(([title, rows]) => {
      svg.append('text').attr('x', 0).attr('y', yy + 14).attr('class', 'lab-strong').text(title);
      yy += headH;
      rows.forEach(([name, vals, col]) => {
        svg.append('text').attr('x', 8).attr('y', yy + 4).attr('class', 'lab-ink').text(name);
        // seeds that would sit on top of each other step up or down a little, so each reads as its own dot
        const placed = [];
        vals.forEach((v, i) => {
          const cx = x(v), dy = [0, -4, 4, -8, 8].find((o) => placed.every(([px, py]) => Math.hypot(px - cx, py - o) >= 7)) ?? 0;
          placed.push([cx, dy]);
          svg.append('circle').attr('cx', cx).attr('cy', yy + dy).attr('r', 4.5).style('fill', col).style('stroke', 'var(--surface)').style('stroke-width', 1)
            .call(explain, `<b>${name}</b> · ${title.split(' · ')[0]}<br>seed ${i + 1}: ${pct(v)}% of positions changed`);
        });
        const mv = mean(vals);
        svg.append('line').attr('x1', x(mv)).attr('x2', x(mv)).attr('y1', yy - 10).attr('y2', yy + 10).style('stroke', 'var(--ink)').style('stroke-width', 2);
        yy += rowH;
      });
    });
  }
  onResize(draw); draw();
}

// ====================================================================== interventions and probes
function initBranch() {
  const IV = { zero: 'zero the compressed output', swap: 'use another sample’s summaries', perm: 'permute summary keys and values together' };
  const svgI = d3.select('#interv');
  tableFrom('#intervTable', ['intervention', 'Dice change'], D.interv.map(([k, v]) => [IV[k], sgn(v, 4)]), 'Dice change under each intervention at inference, mean of 3 seeds');
  function drawI() {
    svgI.selectAll('*').remove();
    const W = chartW(svgI.node(), 500);
    const narrow = W < 460, H = narrow ? 210 : 150;
    svgI.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const valW = 64, z0 = W - valW;
    const x = d3.scaleLinear().domain([-0.018, 0]).range([narrow ? 8 : W * 0.46, z0]);
    const zero = (y1, y2) => svgI.append('line').attr('x1', z0).attr('x2', z0).attr('y1', y1).attr('y2', y2).style('stroke', 'var(--ink)').style('stroke-width', 1.5);
    D.interv.forEach(([k, v], i) => {
      const yy = narrow ? 20 + i * 64 : 26 + i * 42;
      const t = svgI.append('text').attr('x', 0).attr('y', narrow ? yy : yy + 13).attr('class', 'lab-ink').text(IV[k]);
      // narrow: the label sits over its bar; one too long for the width takes a second line, above
      if (narrow && t.node().getComputedTextLength() > W) {
        const w = IV[k].split(' '), h = Math.ceil(w.length / 2);
        t.text(null);
        t.append('tspan').attr('x', 0).attr('dy', -16).text(w.slice(0, h).join(' '));
        t.append('tspan').attr('x', 0).attr('dy', 16).text(w.slice(h).join(' '));
      }
      const by = narrow ? yy + 10 : yy;
      const bw = Math.max(1.5, Math.abs(x(v) - x(0)));
      svgI.append('rect').attr('x', v < 0 ? z0 - bw : z0).attr('y', by).attr('width', bw).attr('height', 18).attr('rx', 3).style('fill', 'var(--teal-mark)')
        .call(explain, `<b>${IV[k]}</b><br>Dice change ${sgn(v, 4)}, mean of 3 seeds`);
      svgI.append('text').attr('x', z0 + 8).attr('y', by + 13).attr('class', 'lab-strong num').text(sgn(v, 4));
      // narrow: zero is marked on each bar, so the line does not run through the labels above them
      if (narrow) zero(by - 4, by + 22);
    });
    if (!narrow) zero(14, H - 8);
  }
  const svgP = d3.select('#probes'), P = D.probes;
  const rows = [
    ['Placement probe', null], ['keys rotated before pooling', P.tb, 'var(--teal-mark)'], ['summary-center rotation', P.sc, 'var(--warm-mark)'], ['unrotated summaries', P.un, 'var(--warm-mark)'],
    ['Long-range probe', null], ['local + global', P.full, 'var(--teal-mark)'], ['local only, radius 0–2', P.loc, 'var(--warm-mark)'],
    ['local + global, evidence zeroed', P.zero, 'var(--warm-mark)'], ['local + global, evidence flipped', P.flip, 'var(--warm-mark)'],
  ];
  let probe = '';
  tableFrom('#probesTable', ['variant', 'probe', 'accuracy'],
    rows.flatMap(([name, v]) => { if (v === null) { probe = name.replace(' probe', ''); return []; } return [[name, probe, v.toFixed(4)]]; }),
    'Probe accuracy for each variant, mean of 6 seeds; chance is 0.5');
  // each bar a meter: a track, a fill with the meter's corners, a tick at chance
  function drawP() {
    svgP.selectAll('*').remove();
    const W = chartW(svgP.node(), 500);
    const narrow = W < 460;
    const rowH = narrow ? 40 : 26, H = rows.reduce((s, r) => s + (r[1] === null ? 26 : rowH), 10) + 16;
    svgP.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const valW = 58, x0 = narrow ? 8 : W * 0.5, x1 = W - valW, bh = 12, rx = parseFloat(tok('--r-xs')) || 6;
    const x = d3.scaleLinear().domain([0, 1]).range([x0, x1]);
    let yy = 8, lastBar = 0;
    rows.forEach(([name, v, col]) => {
      if (v === null) { svgP.append('text').attr('x', 0).attr('y', yy + 15).attr('class', 'lab-strong').text(name); yy += 26; return; }
      svgP.append('text').attr('x', 6).attr('y', narrow ? yy + 12 : yy + 13).attr('class', 'lab-ink').text(name);
      const by = narrow ? yy + 19 : yy + 3;
      svgP.append('rect').attr('x', x0).attr('y', by).attr('width', x1 - x0).attr('height', bh).attr('rx', rx).style('fill', 'var(--track)');
      if (v > 0) svgP.append('rect').attr('x', x0).attr('y', by).attr('width', x(v) - x0).attr('height', bh).attr('rx', rx).style('fill', col)
        .call(explain, `<b>${name}</b><br>accuracy ${v.toFixed(4)}, mean of 6 seeds`);
      svgP.append('text').attr('x', x1 + 8).attr('y', by + 10).attr('class', 'lab-strong num').text(v.toFixed(4));
      // the tick at chance lies over the bar; the bar under it keeps the pointer
      svgP.append('line').attr('x1', x(0.5)).attr('x2', x(0.5)).attr('y1', by - 3).attr('y2', by + bh + 3).style('stroke', 'var(--ink)').style('stroke-width', 1.5).style('pointer-events', 'none');
      lastBar = by + bh;
      yy += rowH;
    });
    svgP.append('text').attr('x', x(0.5)).attr('y', lastBar + 20).attr('text-anchor', 'middle').attr('class', 'muted-t').style('font-size', '12px').text('chance');
  }
  onResize(drawI); onResize(drawP); drawI(); drawP();
}

// ====================================================================== U-Net
function initUnet() {
  const U = D.unet, svg = d3.select('#dumbbell');
  tableFrom('#dumbbellTable', ['seed', 'U-Net', 'PACK3D', 'difference'],
    U.seeds.map((s, i) => [s, U.unet[i].toFixed(4), U.pack[i].toFixed(4), sgn(U.pack[i] - U.unet[i], 4)])
      .concat([['mean', mean(U.unet).toFixed(4), mean(U.pack).toFixed(4), sgn(mean(U.pack) - mean(U.unet), 4)]]),
    'Best-checkpoint macro Dice per seed for the U-Net and PACK3D');
  tableFrom('#structsTable', ['structure', 'PACK3D − U-Net', 'survives Holm'],
    U.structures.map((r) => [r.name, sgn(r.d, 4), r.holm ? 'yes' : 'no']),
    'Mean Dice difference per structure at the best checkpoint, PACK3D minus U-Net');
  // the U-Net is a ring and PACK3D a filled dot, so the two read apart without their colors
  const ring = (c) => c.attr('r', 5.5).style('fill', 'var(--surface)').style('stroke', 'var(--warm-mark)').style('stroke-width', 2.5);
  const dot = (c, col) => c.attr('r', 6.5).style('fill', col).style('stroke', 'var(--surface)').style('stroke-width', 1.5);
  function draw() {
    svg.selectAll('*').remove();
    const W = chartW(svg.node(), 500), H = 270;
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const m = { l: 62, r: 14, t: 10, b: 30 };
    const x = d3.scaleLinear().domain([0.808, 0.832]).range([m.l, W - m.r]);
    const y = d3.scaleBand().domain(U.seeds).range([m.t, H - m.b]).padding(0.4);
    [0.81, 0.82, 0.83].forEach((t) => {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', m.t).attr('y2', H - m.b).style('stroke', 'var(--grid)');
      svg.append('text').attr('x', x(t)).attr('y', H - 8).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(t.toFixed(2));
    });
    U.seeds.forEach((s, i) => {
      const yy = y(s) + y.bandwidth() / 2;
      svg.append('text').attr('x', 0).attr('y', yy + 4).attr('class', 'muted-t num').text('seed ' + s);
      svg.append('line').attr('x1', x(U.unet[i])).attr('x2', x(U.pack[i])).attr('y1', yy).attr('y2', yy).style('stroke', 'var(--rule)').style('stroke-width', 3);
      const tipH = `<b>seed ${s}</b><br>PACK3D ${U.pack[i].toFixed(4)} · U-Net ${U.unet[i].toFixed(4)}<br>difference ${sgn(U.pack[i] - U.unet[i], 4)}`;
      ring(svg.append('circle').attr('cx', x(U.unet[i])).attr('cy', yy)).call(explain, tipH);
      dot(svg.append('circle').attr('cx', x(U.pack[i])).attr('cy', yy), 'var(--teal-mark)').call(explain, tipH);
    });
  }
  const svgS = d3.select('#structs');
  function drawS() {
    svgS.selectAll('*').remove();
    const W = chartW(svgS.node(), 500), H = 140;
    svgS.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const m = { l: 18, r: 18 };
    const x = d3.scaleLinear().domain([-0.045, 0.045]).range([m.l, W - m.r]);
    const base = 80;
    [-0.04, -0.02, 0, 0.02, 0.04].forEach((t) => {
      svgS.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', t === 0 ? base - 14 : base - 4).attr('y2', base + 6).style('stroke', t === 0 ? 'var(--ink)' : 'var(--grid)').style('stroke-width', t === 0 ? 1.5 : 1);
      svgS.append('text').attr('x', x(t)).attr('y', base + 22).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(t === 0 ? '0' : sgn(t, 2));
    });
    svgS.append('text').attr('x', x(0) - 8).attr('y', base + 44).attr('text-anchor', 'end').attr('class', 'muted-t').style('font-size', '12px').text('← U-Net ahead');
    svgS.append('text').attr('x', x(0) + 8).attr('y', base + 44).attr('class', 'muted-t').style('font-size', '12px').text('PACK3D ahead →');
    svgS.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', base).attr('y2', base).style('stroke', 'var(--grid)');
    const placed = [];
    U.structures.forEach((r) => {
      const cx = x(r.d);
      // a small beeswarm: take the first offset that clears every dot already placed
      const dy = [0, -12, 12, -24, 24].find((o) => placed.every(([px, py]) => Math.hypot(px - cx, py - o) >= 12)) ?? 0;
      placed.push([cx, dy]);
      // a structure the U-Net leads on takes the U-Net's ring
      const c = svgS.append('circle').attr('cx', cx).attr('cy', base + dy);
      (r.d > 0 ? c.attr('r', 5.5).style('fill', 'var(--teal-mark)').style('stroke', 'var(--surface)').style('stroke-width', 1.5) : c.attr('r', 4.5).style('fill', 'var(--surface)').style('stroke', 'var(--warm-mark)').style('stroke-width', 2.2))
        .call(explain, `<b>${r.name}</b>${r.holm ? ' *' : ''}<br>mean difference ${sgn(r.d, 4)}${r.holm ? '<br>survives Holm correction' : ''}`);
    });
    // the four structures the caption names, labels leaning away from their neighbors
    U.structures.forEach((r, i) => {
      const anchor = { CETN2: ['middle', 0], NUP153: ['end', 4], ATP2A2: ['end', 4], SEC61B: ['start', -4] }[r.name];
      if (!anchor) return;
      const [cx] = placed[i];
      const t = svgS.append('text').attr('x', cx + anchor[1]).attr('text-anchor', anchor[0]).attr('class', 'lab-ink').style('font-size', '12px').text(r.name + (r.holm ? '*' : ''));
      const w = t.node().getComputedTextLength(), x0 = cx + anchor[1] - (anchor[0] === 'end' ? w : anchor[0] === 'middle' ? w / 2 : 0);
      const top = Math.min(base, ...placed.filter(([px]) => px > x0 - 6 && px < x0 + w + 6).map(([, py]) => base + py - 6));
      const lift = Math.max(r.name === 'SEC61B' ? 38 : 22, base - top + 6);
      t.attr('y', base - lift);
      if (r.name === 'SEC61B') svgS.append('line').attr('x1', cx).attr('x2', cx).attr('y1', base - lift + 3).attr('y2', base - 8).style('stroke', 'var(--ink-3)');
    });
  }
  onResize(draw); onResize(drawS); draw(); drawS();
}

// ====================================================================== systems
function initSystems() {
  const S = D.systems, svg = d3.select('#sysChart');
  const lab = { 65536: '65k', 131072: '131k', 262144: '262k', 524288: '524k', 1048576: '1M' };
  let sel = S.length - 1;
  // in the page from the start, so the tray holds its place
  const chips = d3.select('#sysChips');
  if (chips.selectAll('button').size() !== S.length) { chips.selectAll('*').remove(); S.forEach((r) => chips.append('button').attr('class', 'chip').attr('type', 'button').text(lab[r.n])); }
  chips.selectAll('button').on('click', (ev) => { sel = chips.selectAll('button').nodes().indexOf(ev.currentTarget); update(true); });
  // two baselines in the baseline color, told apart by a dash; PACK3D drawn heavier
  const kinds = [['dense', 'Dense SDPA', 'var(--warm-mark)', null, 2], ['window', 'Window', 'var(--warm-mark)', '4 3', 2], ['pack', 'PACK3D', 'var(--teal-mark)', null, 3]];
  // the paper's table prints dense latency to 0.1 ms with thousands separators, the others to 0.01 ms
  const ms = (k, v) => v.toLocaleString('en-US', { minimumFractionDigits: k === 'dense' ? 1 : 2, maximumFractionDigits: k === 'dense' ? 1 : 2 });
  function draw() {
    svg.selectAll('*').remove();
    const W = chartW(svg.node(), 560), [lo, hi] = heightRange(svg.node()), H = Math.min(hi, Math.max(lo, W * 0.72));
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const m = { l: 54, r: 92, t: 14, b: 40 };
    const x = d3.scaleLog().domain([S[0].n / 1.3, S[S.length - 1].n * 1.3]).range([m.l, W - m.r]);
    const y = d3.scaleLog().domain([8, 50000]).range([H - m.b, m.t]);
    [10, 100, 1000, 10000].forEach((t) => {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--grid)');
      svg.append('text').attr('x', m.l - 8).attr('y', y(t) + 4).attr('text-anchor', 'end').attr('class', 'muted-t num').text(t.toLocaleString('en-US'));
    });
    svg.append('text').attr('x', m.l - 8).attr('y', m.t - 2).attr('text-anchor', 'end').attr('class', 'muted-t').text('ms');
    S.forEach((r, i) => { if (W < 420 && i % 2) return; svg.append('text').attr('x', x(r.n)).attr('y', H - 18).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(lab[r.n]); });
    svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 2).attr('text-anchor', 'middle').attr('class', 'muted-t').style('font-size', '12px').text('tokens (log scale)');
    const r = S[sel];
    svg.append('line').attr('x1', x(r.n)).attr('x2', x(r.n)).attr('y1', m.t).attr('y2', H - m.b).style('stroke', 'var(--ink)').style('stroke-dasharray', '2 3');
    kinds.forEach(([k, name, col, dash, sw]) => {
      svg.append('path').datum(S).attr('d', d3.line().x((d) => x(d.n)).y((d) => y(d[k]))).style('fill', 'none').style('stroke', col).style('stroke-width', sw).style('stroke-dasharray', dash);
      S.forEach((d) => svg.append('circle').attr('cx', x(d.n)).attr('cy', y(d[k])).attr('r', d === r ? 6 : 3.5).style('fill', col).style('stroke', 'var(--surface)').style('stroke-width', 1.5)
        .call(explain, `<b>${name}</b> · ${lab[d.n]} tokens<br>${ms(k, d[k])} ms forward + backward`));
      const last = S[S.length - 1];
      const dy = k === 'pack' ? -7 : k === 'window' ? 12 : 4;
      svg.append('text').attr('x', x(last.n) + 12).attr('y', y(last[k]) + dy).attr('class', 'lab-ink').text(name);
    });
  }
  // in the page from the start, so it holds its place
  function panel(say) {
    const r = S[sel], prem = r.pack / r.window - 1;
    $('#sysSpeed').textContent = `${r.speedup.toFixed(2)}×`;
    $('#sysPrem').textContent = `+${(prem * 100).toFixed(0)}%`;
    tableFrom('#sysTable', [lab[r.n] + ' tokens', 'latency, ms', 'peak, GiB'], [
      ['Dense SDPA', ms('dense', r.dense), r.gb_dense.toFixed(2)],
      ['Window attention', ms('window', r.window), r.gb_window.toFixed(2)],
      ['PACK3D', ms('pack', r.pack), r.gb_pack.toFixed(2)],
    ], `Layer latency and peak memory at ${lab[r.n]} tokens`);
    $('#sysNote').textContent = `${r.m.toLocaleString('en-US')} summaries per KV head at this size. Dense SDPA has the smallest peak allocation; PACK3D’s is below window attention’s.`;
    // a screen reader hears what a choice changed; the first render says nothing
    const st = $('#sysStatus'), msg = `${lab[r.n]} tokens: PACK3D is ${r.speedup.toFixed(2)}× faster than dense SDPA and ${(prem * 100).toFixed(0)}% slower than window attention.`;
    if (say && st.textContent !== msg) st.textContent = msg;
  }
  function update(say) { chips.selectAll('button').attr('aria-pressed', (d, i) => String(i === sel)); draw(); panel(say); }
  onResize(draw); update(false);
}

// ====================================================================== the end: a word built in memory order
// c = (z, y, x): z up, y into the word, x along it; i: the memory position under the chosen order
function initEnd() {
  // a code block wider than its column joins the tab order with a name (Safari does not do that by itself)
  [['#recipe pre.code', 'A repack test, in pseudocode'], ['#bibtex', 'BibTeX']].forEach(([sel, name]) => {
    const el = $(sel);
    if (!el) return;
    const upd = () => {
      const over = el.scrollWidth > el.clientWidth + 1, x = el.scrollLeft;
      if (over !== el.hasAttribute('tabindex')) {
        if (over) { el.tabIndex = 0; el.setAttribute('role', 'region'); el.setAttribute('aria-label', name); }
        else ['tabindex', 'role', 'aria-label'].forEach((a) => el.removeAttribute(a));
      }
      el.classList.toggle('more-l', over && x > 1);
      el.classList.toggle('more-r', over && x + el.clientWidth < el.scrollWidth - 1);
    };
    el.addEventListener('scroll', upd, { passive: true });
    new ResizeObserver(upd).observe(el);
    if (document.fonts) document.fonts.addEventListener('loadingdone', upd);   // the mono font changes the width
    upd();
  });

  const foot = $('#end'), wrap = $('#endWrap'), canvas = $('#endCanvas'), rib = $('#endRibbon');
  if (!foot || !canvas || !rib) return;
  foot.classList.add('js');
  const GLYPH = {        // 5 x 7 faces; every '#' is a row of cubes running back through the word
    P: ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
    A: ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    C: ['.####', '#....', '#....', '#....', '#....', '#....', '.####'],
    K: ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'],
    3: ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
    D: ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
  };
  const GW = 5, GH = 7, Y = 3, WIN = 7, TRAIL = 18, DROP = 1.2;
  // the repack moves whole z-layers: these list the layers in their new memory order
  const PERMS = { 7: [4, 1, 6, 0, 3, 5, 2], 16: [11, 3, 14, 6, 0, 9, 13, 2, 7, 15, 4, 10, 1, 12, 5, 8] };
  // a lower camera than Figure 1's, turned toward the front, so the word reads left to right
  const AZ = 18 * Math.PI / 180, CA = Math.cos(AZ), SA = Math.sin(AZ), EL = 0.3, ZS = 1;
  const DV = [SA, CA, EL / ZS];            // toward the viewer; painting far to near sorts on this
  // the opening's ramp; the stage keeps its colors in both themes, so they are read once
  const rampF = RAMPS.mem();
  const BLACK = lab('#000000'), WHITE = lab('#FFFFFF'), EDGE = tok('--stage-bg'), MINT = tok('--stage-mint');
  const UNWRITTEN = `rgba(${rgbOf(tok('--stage-ink'))},0.08)`;
  // on touch screens there is no pointer to hover and usually no arrow keys: say "tap"
  if (HOVERLESS) $('#endRead').textContent = 'Tap a cube, or slide a finger across the word, to read its two indices.';
  const HINT = $('#endRead').textContent;
  let T = [], n = 0, X = 0, Z = 0, two = null, cur = 'raster';
  let mem = null, order = null, shades = null, ribCol = null, farFirst = null, mirFirst = null;
  let ctx = null, rctx = null, W = 0, H = 0, RW = 0, RH = 0, k = 1, ox = 0, oy = 0, fade = null, lastW = -1;
  let P = RM ? 1 : 0, target = RM ? 1 : 0, trailA = RM ? 0 : 1, raf = 0, last = 0, hovTok = -1, selI = -1, lastCount = -2;
  let buildS = 3.2;                                     // seconds a build takes: the show, as the word arrives

  function makeWord() {
    const rows = two ? ['PACK', '3D'] : ['PACK3D'];
    const widths = rows.map((r) => r.length * (GW + 1) - 1);
    X = Math.max(...widths); Z = rows.length * GH + (rows.length - 1) * 2;
    T = [];
    rows.forEach((r, ri) => {
      const x0 = Math.floor((X - widths[ri]) / 2), zTop = Z - 1 - ri * (GH + 2);
      [...r].forEach((ch, ci) => GLYPH[ch].forEach((line, gy) => {
        for (let gx = 0; gx < GW; gx++) {
          if (line[gx] !== '#') continue;
          for (let y = 0; y < Y; y++) T.push({ x: x0 + ci * (GW + 1) + gx, y, z: zTop - gy });
        }
      }));
    });
    n = T.length;
    const depth = (t, z) => t.x * DV[0] + t.y * DV[1] + z * DV[2];
    const idx = T.map((t, j) => j);
    farFirst = idx.slice().sort((a, b) => depth(T[a], T[a].z) - depth(T[b], T[b].z));
    mirFirst = idx.slice().sort((a, b) => depth(T[a], -T[a].z - 1) - depth(T[b], -T[b].z - 1));
    ribCol = idx.map((i) => css(rampF(i / (n - 1))));
  }
  function keyOf(name, t, pos) {
    const { x, y, z } = t;
    if (name === 'raster') return (z * Y + y) * X + x;
    if (name === 'morton') {
      let m = 0;
      for (let b = 0; b < 6; b++) m |= (((x >> b) & 1) << (3 * b)) | (((y >> b) & 1) << (3 * b + 1)) | (((z >> b) & 1) << (3 * b + 2));
      return m;
    }
    if (name === 'blocks') {                // 4 x 4 x 4 blocks, block by block, raster inside each
      const nbx = Math.ceil(X / 4), nby = Math.ceil(Y / 4);
      return (((z >> 2) * nby + (y >> 2)) * nbx + (x >> 2)) * 64 + ((z & 3) * 4 + (y & 3)) * 4 + (x & 3);
    }
    return (pos[z] * Y + y) * X + x;        // repacked: raster inside each layer, layers moved whole
  }
  function setOrder(name) {
    const pos = new Int32Array(Z);
    (PERMS[Z] || Array.from({ length: Z }, (_, i) => i)).forEach((g, i) => { pos[g] = i; });
    const keyed = T.map((t, j) => [keyOf(name, t, pos), j]).sort((a, b) => a[0] - b[0]);
    for (let i = 1; i < n; i++) if (keyed[i][0] === keyed[i - 1][0]) throw new Error('order ' + name + ' is not a permutation');
    order = keyed.map((p) => p[1]);                       // order[i]: the token at memory position i
    mem = new Int32Array(n);
    order.forEach((j, i) => { mem[j] = i; });             // mem[j]: the memory position of token j
    shades = T.map((t, j) => {                            // top, front, side: the front carries the color,
      const b = rampF(mem[j] / (n - 1));                  // lit from above, shaded on the side
      return [mixLab(b, WHITE, 0.28), b, mixLab(b, BLACK, 0.38)].map(css);
    });
  }

  const sx = (x, y) => ox + k * (x * CA - y * SA);
  const sy = (x, y, z) => oy + k * (EL * (x * SA + y * CA) - ZS * z);
  const pt = (x, y, z) => [sx(x, y), sy(x, y, z)];
  function quads(t, z) {                                   // the three faces a viewer can see
    const { x, y } = t;
    return [
      [pt(x, y, z + 1), pt(x + 1, y, z + 1), pt(x + 1, y + 1, z + 1), pt(x, y + 1, z + 1)],
      [pt(x, y + 1, z + 1), pt(x + 1, y + 1, z + 1), pt(x + 1, y + 1, z), pt(x, y + 1, z)],
      [pt(x + 1, y, z + 1), pt(x + 1, y + 1, z + 1), pt(x + 1, y + 1, z), pt(x + 1, y, z)],
    ];
  }
  const ctr = (j) => { const t = T[j]; return pt(t.x + 0.5, t.y + 0.5, t.z + 0.5); };
  const land = (i, NP) => clamp((NP - i) / WIN, 0, 1);    // 0: not yet sent, 1: landed
  const NPnow = () => P * (n + WIN);

  function layout() {
    const w = wrap.clientWidth;
    if (!w) return false;
    lastW = W = w;
    const wantTwo = w < 600;
    if (wantTwo !== two) { two = wantTwo; hovTok = selI = -1; makeWord(); setOrder(cur); canvas.setAttribute('aria-valuemax', String(n - 1)); }
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const t of T) for (let a = 0; a < 2; a++) for (let b = 0; b < 2; b++) {
      const u = (t.x + a) * CA - (t.y + b) * SA, v = EL * ((t.x + a) * SA + (t.y + b) * CA);
      x0 = Math.min(x0, u); x1 = Math.max(x1, u);
      y0 = Math.min(y0, v - ZS * (t.z + 1 + DROP)); y1 = Math.max(y1, v - ZS * t.z);
    }
    const reflect = ZS * GH * 0.45;                        // the reflection fades out within this depth
    y1 += reflect;
    const bw = x1 - x0, bh = y1 - y0;
    // at most 520px and 58% of the screen, and short enough to share the screen under the bar with its memory and orders
    // (292px tall sideways under Safari's bars)
    const bar = $('.topbar'), ctl = $('.end-controls', foot);
    const below = ctl ? ctl.getBoundingClientRect().bottom - wrap.getBoundingClientRect().bottom : 0;
    const fits = window.innerHeight - (bar ? bar.offsetHeight : 0) - below - 12;
    const cap = Math.max(140, Math.min(520, window.innerHeight * 0.58, fits));
    k = Math.min((w * 0.97) / bw, cap / bh);
    H = Math.ceil(bh * k);
    wrap.style.aspectRatio = 'auto';
    wrap.style.height = H + 'px';
    ox = (w - bw * k) / 2 - x0 * k; oy = -y0 * k;
    ctx = fitCanvas(canvas, W, H);
    if (!ctx) { foot.classList.remove('js'); return false; }   // no 2D context: the end keeps its words, without the figure
    // the floor fade runs at right angles to the floor's front edge
    const f = pt(X / 2, Y, 0), ul = Math.hypot(EL * SA, CA), L = reflect * k;
    fade = ctx.createLinearGradient(f[0], f[1], f[0] - (EL * SA / ul) * L, f[1] + (CA / ul) * L);
    fade.addColorStop(0, 'rgba(0,0,0,0.3)');
    fade.addColorStop(0.5, 'rgba(0,0,0,0.82)');
    fade.addColorStop(1, 'rgba(0,0,0,1)');
    RW = rib.clientWidth; RH = rib.clientHeight;
    rctx = fitCanvas(rib, RW, RH);
    return true;
  }

  function cube(j, z, alpha) {
    const q = quads(T[j], z), s = shades[j];
    ctx.globalAlpha = alpha;
    for (let f = 0; f < 3; f++) {
      const p = q[f];
      ctx.beginPath();
      ctx.moveTo(p[0][0], p[0][1]); ctx.lineTo(p[1][0], p[1][1]); ctx.lineTo(p[2][0], p[2][1]); ctx.lineTo(p[3][0], p[3][1]);
      ctx.closePath();
      ctx.fillStyle = s[f]; ctx.fill(); ctx.stroke();
    }
  }
  function render() {
    if (!ctx) return;
    const NP = NPnow();
    ctx.clearRect(0, 0, W, H);
    ctx.lineJoin = 'round'; ctx.lineWidth = Math.max(0.6, k * 0.06); ctx.strokeStyle = EDGE;
    // the reflection, drawn first
    for (const j of mirFirst) {
      const a = land(mem[j], NP);
      if (a > 0) cube(j, -T[j].z - 1 - (1 - ease(a)) * DROP, 0.24 * Math.min(1, a * 1.6));
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = fade; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'source-over';
    // the word
    for (const j of farFirst) {
      const a = land(mem[j], NP);
      if (a > 0) cube(j, T[j].z + (1 - ease(a)) * DROP, Math.min(1, a * 1.6));
    }
    ctx.globalAlpha = 1;
    if (trailA > 0 && P > 0) trail(NP);
    const fi = focusI();
    if (fi >= 0 && land(fi, NP) >= 1) focus(fi);
    ribbon(NP);
    count(NP);
  }
  // the memory head and the last positions it wrote
  function trail(NP) {
    const head = Math.min(n - 1, Math.floor(NP));
    if (head < 0) return;
    const from = Math.max(0, head - TRAIL);
    ctx.save();
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = MINT; ctx.lineWidth = Math.max(1.3, k * 0.075);
    let prev = ctr(order[from]);
    for (let i = from + 1; i <= head; i++) {
      const p = ctr(order[i]);
      ctx.globalAlpha = trailA * (0.12 + 0.88 * (i - from) / (head - from));
      ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(p[0], p[1]); ctx.stroke();
      prev = p;
    }
    ctx.globalAlpha = trailA; ctx.fillStyle = MINT; ctx.shadowColor = MINT; ctx.shadowBlur = 16;
    ctx.beginPath(); ctx.arc(prev[0], prev[1], Math.max(2.6, k * 0.14), 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
  const focusI = () => (hovTok >= 0 ? mem[hovTok] : selI);
  // a picked token: its cube outlined, and memory i - 3 .. i + 3
  function focus(i) {
    const lo = Math.max(0, i - 3), hi = Math.min(n - 1, i + 3);
    ctx.save();
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.strokeStyle = MINT; ctx.lineWidth = Math.max(1.6, k * 0.08);
    ctx.beginPath();
    for (let m = lo; m <= hi; m++) { const p = ctr(order[m]); if (m === lo) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]); }
    ctx.stroke();
    ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 2;
    quads(T[order[i]], T[order[i]].z).forEach((p) => {
      ctx.beginPath(); p.forEach((v, m) => (m ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1]))); ctx.closePath(); ctx.stroke();
    });
    for (let m = lo; m <= hi; m++) {
      const p = ctr(order[m]);
      ctx.fillStyle = m === i ? '#FFFFFF' : MINT;
      ctx.beginPath(); ctx.arc(p[0], p[1], m === i ? Math.max(3, k * 0.15) : Math.max(2.2, k * 0.1), 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }
  function ribbon(NP) {
    if (!rctx) return;
    rctx.clearRect(0, 0, RW, RH);
    const cw = RW / n;
    for (let i = 0; i < n; i++) {
      rctx.fillStyle = land(i, NP) > 0 ? ribCol[i] : UNWRITTEN;
      rctx.fillRect(i * cw, 0, cw + 0.6, RH);
    }
    if (P > 0 && P < 1) { rctx.fillStyle = MINT; rctx.fillRect(clamp(Math.min(n, NP) * cw - 1, 0, RW - 2), 0, 2, RH); }
    const fi = focusI();
    if (fi >= 0) { rctx.fillStyle = '#FFFFFF'; rctx.fillRect(clamp((fi + 0.5) * cw - 1.5, 0, RW - 3), 0, 3, RH); }
  }
  function count(NP) {
    const c = Math.min(n, Math.floor(NP));
    if (c === lastCount) return;
    lastCount = c;
    $('#endCount').textContent = c >= n ? `${n} tokens` : `${Math.max(0, c)} / ${n}`;
  }
  const fmt = (v) => (v < 0 ? MINUS + -v : String(v));
  // an expression keeps together: no-break spaces around = and after the commas of a coordinate
  const eq = (a, b) => `${a} = ${b}`, at = (z, y, x) => `(${z}, ${y}, ${x})`;
  function describe(i) {
    if (i < 0) return HINT;
    const t = T[order[i]];
    let s = `${eq('i', i)} holds the token at ${eq('c', at(t.z, t.y, t.x))}.`;
    if (i + 1 < n) { const u = T[order[i + 1]]; s += ` Next in memory, ${eq('i', i + 1)}, is ${eq('Δc', at(fmt(u.z - t.z), fmt(u.y - t.y), fmt(u.x - t.x)))} away.`; }
    else s += ' It is the last position in memory.';
    return s;
  }
  // a slider over memory positions, for assistive tech
  function readout(i, live) {
    $('#endRead').textContent = describe(i);
    if (!live) return;
    canvas.setAttribute('aria-valuenow', String(Math.max(0, i)));
    canvas.setAttribute('aria-valuetext', i >= 0 ? describe(i) : 'No token picked. Use the arrow keys to walk the memory.');
  }

  function tick(now) {
    raf = 0;
    const dt = last ? Math.min(0.05, (now - last) / 1000) : 0;
    last = now;
    let busy = false;
    if (P !== target) {
      P = target > P ? Math.min(target, P + dt / buildS) : Math.max(target, P - dt / 0.9);
      busy = true;
    } else if (P >= 1 && trailA > 0) {
      trailA = Math.max(0, trailA - dt / 0.8);
      busy = true;
    }
    render();
    if (busy) raf = requestAnimationFrame(tick); else last = 0;
  }
  const kick = () => { if (!raf) { last = 0; raf = requestAnimationFrame(tick); } };
  // a new order answers in about a second, so orders can be compared
  function build(quick) {
    if (!ctx) return;
    if (RM) { render(); return; }
    buildS = quick ? 1.1 : 3.2;
    P = 0; target = 1; trailA = 1; lastCount = -2; kick();
  }
  // the word as it stands built, at once: how it arrives while motion is paused
  function whole() {
    if (!ctx) return;
    P = target = 1; trailA = 0; lastCount = -2; render();
  }

  $$('#endChips [data-layout]').forEach((b) => b.addEventListener('click', () => {
    cur = b.dataset.layout;
    $$('#endChips [data-layout]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    if (!T.length) return;                                 // not laid out yet: the first build uses cur
    setOrder(cur);
    if (selI >= 0) readout(selI, true);
    build(true);
  }));
  const again = $('#endAgain');
  if (RM) again.hidden = true; else again.addEventListener('click', () => build());

  const unTip = () => { hideTip(); tip.classList.remove('on-dark'); };
  const tipFor = (j, ev) => { const t = T[j]; showTip(`<b>${eq('<i>i</i>', mem[j])}</b> · ${eq('<i>c</i>', at(t.z, t.y, t.x))}`, ev); tip.classList.add('on-dark'); };
  function hit(px, py) {
    const NP = NPnow();
    const inQuad = (p) => {
      let s = 0;
      for (let m = 0; m < 4; m++) {
        const a = p[m], b = p[(m + 1) % 4], c = (b[0] - a[0]) * (py - a[1]) - (b[1] - a[1]) * (px - a[0]);
        if (c === 0) continue;
        if (!s) s = Math.sign(c); else if (Math.sign(c) !== s) return false;
      }
      return true;
    };
    for (let r = farFirst.length - 1; r >= 0; r--) {
      const j = farFirst[r];
      if (land(mem[j], NP) < 1) continue;
      if (quads(T[j], T[j].z).some(inQuad)) return j;
    }
    return -1;
  }
  const local = (el, ev) => { const r = el.getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top, r.width]; };
  function point(j, ev) {
    if (j !== hovTok) { hovTok = j; render(); readout(focusI()); }
    if (j >= 0) tipFor(j, ev); else unTip();
  }
  // the ribbon answers in a band taller than it is drawn (CSS), which belongs to its parent
  const ribHit = rib.parentElement;
  canvas.addEventListener('pointermove', (ev) => { if (ctx && ev.pointerType === 'mouse') { const [x, y] = local(canvas, ev); point(hit(x, y), ev); } });
  ribHit.addEventListener('pointermove', (ev) => {
    if (!ctx || ev.pointerType !== 'mouse') return;
    const [x, , w] = local(rib, ev), i = clamp(Math.floor((x / w) * n), 0, n - 1);
    point(land(i, NPnow()) >= 1 ? order[i] : -1, ev);
  });
  const leave = () => { if (hovTok >= 0) { hovTok = -1; render(); readout(selI); } unTip(); };
  canvas.addEventListener('pointerleave', leave);
  ribHit.addEventListener('pointerleave', leave);
  const pick = (i) => { selI = i; readout(i, true); render(); };
  const onWord = (ev) => { const [x, y] = local(canvas, ev), j = hit(x, y); return j >= 0 ? mem[j] : -1; };
  const onRibbon = (ev) => { const [x, , w] = local(rib, ev), i = clamp(Math.floor((x / w) * n), 0, n - 1); return land(i, NPnow()) >= 1 ? i : -1; };
  // a tap picks on click, not pointerdown, so a scroll that starts on the word picks nothing
  canvas.addEventListener('click', (ev) => { if (ctx) pick(onWord(ev)); });
  ribHit.addEventListener('click', (ev) => { if (ctx) pick(onRibbon(ev)); });
  // a sideways slide walks the word or the memory; vertical drags and pinches stay the page's
  canvas.addEventListener('pointermove', (ev) => { if (ctx && ev.pointerType === 'touch') { const i = onWord(ev); if (i >= 0 && i !== selI) pick(i); } });
  ribHit.addEventListener('pointermove', (ev) => { if (ctx && ev.pointerType === 'touch') { const i = onRibbon(ev); if (i >= 0 && i !== selI) pick(i); } });
  // Page Up and Page Down step ten; the pick stays when focus leaves
  canvas.addEventListener('keydown', (ev) => {
    if (!ctx) return;
    const d = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1, PageUp: 10, PageDown: -10 }[ev.key];
    let i;
    if (d) i = selI < 0 ? (d > 0 ? 0 : n - 1) : clamp(selI + d, 0, n - 1);
    else if (ev.key === 'Home') i = 0;
    else if (ev.key === 'End') i = n - 1;
    else if (ev.key === 'Escape') i = -1;
    else return;
    ev.preventDefault();
    if (P < 1) { P = target = 1; trailA = 0; }             // finish the build so every token can be visited
    pick(i);
  });

  // paused, the line is whole as soon as any of it shows
  if (!RM) {
    const line = $('#endClosing');
    let w = 0;
    [...line.childNodes].forEach((node) => {
      if (node.nodeType === 1) { node.classList.add('w'); node.style.setProperty('--i', w++); return; }
      if (node.nodeType !== 3) return;
      const frag = document.createDocumentFragment();
      node.textContent.split(/([ \t\n]+)/).forEach((part) => {
        if (!part) return;
        if (/^[ \t\n]+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
        const s = document.createElement('span');
        s.className = 'w'; s.style.setProperty('--i', w++); s.textContent = part;
        frag.appendChild(s);
      });
      node.replaceWith(frag);
    });
    foot.classList.add('anim');
    const io = new IntersectionObserver((es) => {
      const e = es[es.length - 1];
      if (motion.paused && e.isIntersecting) foot.classList.remove('anim');   // its words as they stand, no transition
      else if (!motion.paused && e.intersectionRatio >= 0.3) foot.classList.add('in');
      else return;
      io.disconnect();
    }, { threshold: [0, 0.3] });
    io.observe(line);
  }
  // lay out near the end, build in view, reset a screen away; paused, the word arrives whole
  const near = new IntersectionObserver((es) => {
    if (!ctx && es.some((e) => e.isIntersecting) && layout()) render();
  }, { rootMargin: '900px 0px' });
  near.observe(foot);
  // and in any case once the page is idle, so a reader who jumps to the end finds the stage ready
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 2500));
  idle(() => { if (!ctx && layout()) render(); }, { timeout: 5000 });
  if (!RM) {
    const seen = new IntersectionObserver((es) => es.forEach((e) => {
      if (!ctx && !layout()) return;
      if (target >= 1) return;
      if (motion.paused) { if (e.isIntersecting) whole(); } else if (e.intersectionRatio >= 0.4) build();
    }), { threshold: [0, 0.4] });
    seen.observe(wrap);
    window.addEventListener('scroll', () => {
      if (!ctx || target === 0) return;
      const r = wrap.getBoundingClientRect(), vh = window.innerHeight;
      if (r.bottom > -vh && r.top < 2 * vh) return;
      P = target = 0; trailA = 1; hovTok = selI = -1;
      readout(-1, true); render();
    }, { passive: true });
  }
  // the ribbon is watched too: its width moves with the count beside it once the mono font arrives
  const ro = new ResizeObserver(() => { if (ctx && (wrap.clientWidth !== lastW || rib.clientWidth !== RW)) { layout(); render(); } });
  ro.observe(wrap); ro.observe(rib);
  const relayout = () => { if (ctx) { layout(); render(); } };
  [canvas, rib].forEach((c) => c.addEventListener('contextrestored', relayout));
  onDpr(relayout);
}

// ====================================================================== controls: trays and scrollers
// The figures write aria-pressed; it becomes aria-checked here (a tray is a radio group), and focus stays put.
function initControls() {
  // this runs before any figure starts, so a figure that redraws for print hears the light theme
  let printing = false, themeBefore = null;
  window.addEventListener('beforeprint', () => {
    if (printing) return;
    printing = true; themeBefore = document.documentElement.getAttribute('data-theme');
    setTheme('light');
  });
  window.addEventListener('afterprint', () => {
    if (!printing) return;
    printing = false; setTheme(themeBefore);
  });
  const STEP = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
  const sync = (tray) => {
    const opts = $$('.chip', tray);
    opts.forEach((b) => {
      const p = b.getAttribute('aria-pressed');
      if (p !== null) { b.setAttribute('aria-checked', p); b.removeAttribute('aria-pressed'); }
      if (b.getAttribute('role') !== 'radio') b.setAttribute('role', 'radio');
    });
    const on = opts.find((b) => b.getAttribute('aria-checked') === 'true') || opts[0];
    opts.forEach((b) => { const t = b === on ? 0 : -1; if (b.tabIndex !== t) b.tabIndex = t; });
  };
  const SCROLLERS = '.math-display, .table-wrap', seen = new WeakSet();
  let scanT = 0;
  const cue = (el) => {
    const more = el.scrollWidth - el.clientWidth;
    el.classList.toggle('more-l', more > 1 && el.scrollLeft > 1);
    el.classList.toggle('more-r', more > 1 && el.scrollLeft < more - 1);
  };
  const ro = new ResizeObserver((es) => es.forEach((x) => (x.target.isConnected ? cue(x.target) : ro.unobserve(x.target))));
  const scan = () => $$(SCROLLERS).forEach((el) => {
    if (seen.has(el)) return;
    seen.add(el);
    el.addEventListener('scroll', () => cue(el), { passive: true });
    ro.observe(el);
  });
  $$('.chips').forEach((tray) => {
    tray.setAttribute('role', 'radiogroup');
    sync(tray);
    // a figure's aria-pressed, or a new option, is taken over here; a choice can rebuild a table, so new scrollers are
    // looked for a moment later
    new MutationObserver((rs) => {
      if (!rs.some((r) => r.type === 'childList' || r.target.hasAttribute('aria-pressed'))) return;
      sync(tray);
      clearTimeout(scanT); scanT = setTimeout(scan, 150);
    }).observe(tray, { subtree: true, childList: true, attributes: true, attributeFilter: ['aria-pressed'] });
    tray.addEventListener('keydown', (e) => {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      const opts = $$('.chip', tray), i = opts.indexOf(e.target);
      if (i < 0) return;
      const j = e.key in STEP ? (i + STEP[e.key] + opts.length) % opts.length : e.key === 'Home' ? 0 : e.key === 'End' ? opts.length - 1 : -1;
      if (j < 0) return;
      e.preventDefault();
      opts[j].focus();
      if (opts[j].getAttribute('aria-checked') !== 'true') opts[j].click();
    });
  });
  scan();
}

// ====================================================================== nav, copy
function initNav() {
  const bar = $('#progress'), topbar = $('.topbar'), main = $('main'), sheet = $('.standfirst');
  const wins = $$('.stage-window');
  // the browser's own bar follows ours: the markup gives the stage's color, data-page the page's
  const metas = $$('meta[name="theme-color"]');
  metas.forEach((m) => { m.dataset.stage = m.content; });
  const toc = $('#toc'), btn = $('#tocBtn'), menu = $('#tocMenu'), label = $('#tocLabel');
  const links = $$('a', menu);
  const spots = links.filter((a) => a.hash).map((a) => ({ a, s: $(a.hash), name: $('.t', a).textContent, short: a.dataset.short || '' }))
    .filter((p) => p.s);
  let cur = -2, openedAt = 0;
  // which full names fit is measured once per bar width (and after the fonts or the text size change), from the text's
  // fractional width: WebKit rounds scrollWidth
  let fits = null;
  const range = document.createRange();
  const measure = () => {
    if (!label.getClientRects().length) return;          // the bar is not laid out (on paper): measured once it is
    fits = spots.map((p) => {
      if (!p.short) return true;
      label.textContent = p.name; range.selectNodeContents(label);
      return range.getBoundingClientRect().width <= label.getBoundingClientRect().width + 0.01;
    });
  };
  const fit = () => {
    if (!fits) measure();
    const p = spots[cur], name = !p ? 'Contents' : !fits || fits[cur] ? p.name : p.short;
    if (label.textContent !== name) label.textContent = name;
  };
  const setCur = (i) => {
    if (i === cur) return;
    const first = cur === -2;
    label.style.setProperty('--dy', (i > cur ? 0.45 : -0.45) + 'em');
    cur = i;
    spots.forEach((p, j) => (j === i ? p.a.setAttribute('aria-current', 'location') : p.a.removeAttribute('aria-current')));
    btn.setAttribute('aria-label', i < 0 ? 'Contents' : `Contents, now reading ${spots[i].name}`);
    label.classList.remove('swap');
    fit();
    if (!first) { void label.offsetWidth; label.classList.add('swap'); }   // the name's arrival plays again
  };
  const isOpen = () => toc.classList.contains('open');
  const shown = () => links.filter((a) => a.offsetParent);
  // pinned by a click, a tap or the keyboard until a choice, a click elsewhere or Escape; a resting mouse's closes as
  // it leaves
  let pinned = false, hoverT = 0;
  const later = (f, ms) => { clearTimeout(hoverT); hoverT = setTimeout(f, ms); };
  // a closed menu is inert: its rows leave the Tab order at once, while the sheet is still fading out
  menu.inert = true;
  const open = (focus, pin = true) => {
    clearTimeout(hoverT);
    pinned = pinned || pin;
    if (!isOpen()) {
      toc.classList.add('open'); menu.inert = false; btn.setAttribute('aria-expanded', 'true'); openedAt = window.scrollY;
      // open at the top with the current chapter in view: a scroll left from an earlier visit would hide the first chapters
      const a = spots[cur] && spots[cur].a;
      menu.scrollTop = 0;
      if (a && a.offsetTop + a.offsetHeight + 6 > menu.clientHeight) menu.scrollTop = a.offsetTop + a.offsetHeight + 6 - menu.clientHeight;
    }
    if (focus) (spots[cur] ? spots[cur].a : shown()[0]).focus({ preventScroll: true });
  };
  const close = (refocus) => {
    clearTimeout(hoverT);
    pinned = false;
    if (!isOpen()) return;
    if (refocus) btn.focus({ preventScroll: true });
    toc.classList.remove('open'); menu.inert = true; btn.setAttribute('aria-expanded', 'false');
  };
  // a click on a menu the mouse already opened keeps it open, rather than shutting it as the reader arrives
  btn.addEventListener('click', () => (isOpen() && pinned ? close(false) : open(false)));
  // a resting mouse opens the contents after a short pause and closes them after a short grace
  toc.addEventListener('pointerenter', (e) => {
    if (e.pointerType !== 'mouse') return;
    if (isOpen()) clearTimeout(hoverT); else later(() => open(false, false), 110);
  });
  toc.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && !pinned) later(() => close(false), 260); });
  btn.addEventListener('keydown', (e) => { if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); open(true); } });
  menu.addEventListener('keydown', (e) => {
    const list = shown(), k = list.indexOf(document.activeElement);
    const go = (j) => { e.preventDefault(); list[(j + list.length) % list.length].focus(); };
    if (e.key === 'ArrowDown') go(k + 1);
    else if (e.key === 'ArrowUp') go(k < 0 ? -1 : k - 1);
    else if (e.key === 'Home') go(0);
    else if (e.key === 'End') go(-1);
    else if (/^[0-9]$/.test(e.key) && !e.metaKey && !e.ctrlKey && !e.altKey) {
      // the numbers the menu shows are shortcuts while it is open: 1 to 9, and 0 for chapter 10
      const a = links.find((x) => x.dataset.n === (e.key === '0' ? '10' : e.key));
      if (a) { e.preventDefault(); a.click(); }
    }
  });
  // a choice moves focus to the heading it lands on, so the keyboard carries on from there
  menu.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a) return;
    const t = a.hash && document.getElementById(decodeURIComponent(a.hash.slice(1)));
    const head = t && (t.matches('h1, h2, h3') ? t : $('h1, h2, h3', t));
    close(false);
    if (head) {
      if (!head.hasAttribute('tabindex')) head.tabIndex = -1;
      requestAnimationFrame(() => head.focus({ preventScroll: true }));
    }
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isOpen()) close(toc.contains(document.activeElement)); });
  document.addEventListener('pointerdown', (e) => { if (!toc.contains(e.target)) close(false); });
  // tabbing out closes it; a click that leaves focus nowhere (Safari does not focus links) does not
  toc.addEventListener('focusout', (e) => { if (e.relatedTarget && !toc.contains(e.relatedTarget)) close(false); });

  // One update a frame, every measure read before anything is written, so a scroll forces no layout. The edge comes
  // from the bar's style, not its sticky box: Safari can report that from before a jump for a frame.
  let raf = 0, scope = '', edge = 0, resized = true, barW = 0;
  const update = () => {
    raf = 0;
    const h = document.documentElement, y = window.scrollY, vw = h.clientWidth, vh = window.innerHeight, max = h.scrollHeight - h.clientHeight;
    if (resized) edge = (parseFloat(getComputedStyle(topbar).top) || 0) + topbar.offsetHeight;
    const mb = main.getBoundingClientRect().bottom;
    const onStage = !!sheet && sheet.getBoundingClientRect().top > edge;   // the opening is under the bar
    const overWin = wins.some((w) => { const r = w.getBoundingClientRect(); return r.top < edge && r.bottom > edge; });
    let i = -1;
    spots.forEach((p, j) => { if (p.s.getBoundingClientRect().top < vh * 0.35) i = j; });
    const s = onStage || overWin ? 'stage' : mb < edge ? 'end' : 'page';
    if (s !== scope) {
      // an open menu closes rather than change color under the reader
      if (scope && isOpen()) close(menu.contains(document.activeElement));
      scope = s;
      topbar.classList.toggle('on-stage', s === 'stage');
      topbar.classList.toggle('on-end', s === 'end');
      h.classList.toggle('stage-top', s !== 'page');   // the strip above the bar follows it
      metas.forEach((m) => { if (m.dataset.page) m.content = s === 'page' ? m.dataset.page : m.dataset.stage; });
    }
    topbar.classList.toggle('at-start', y < 4);
    h.classList.toggle('at-end', mb < vh);             // overscroll past the end shows the stage
    h.classList.toggle('at-top', onStage);             // and so does overscroll above the opening
    bar.style.transform = `scaleX(${max > 0 ? Math.min(1, y / max) : 0})`;
    // a new width (a rotation, Safari's Page Zoom, which fires no resize of its own) measures the names again
    if (vw !== barW) { barW = vw; fits = null; }
    resized = false;
    setCur(i);
    if (!fits) fit();
    if (isOpen() && Math.abs(y - openedAt) > 120) close(menu.contains(document.activeElement));
  };
  const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', () => { resized = true; onScroll(); }, { passive: true });
  // Safari's Page Zoom resizes only the visual viewport; a pinch or a toolbar leaves the layout's width as it was
  if (window.visualViewport) window.visualViewport.addEventListener('resize', () => { if (document.documentElement.clientWidth !== barW) { resized = true; onScroll(); } }, { passive: true });
  if (document.fonts) document.fonts.ready.then(() => { fits = null; resized = true; onScroll(); });   // names measured in Inter
  // larger text at the same width: the slash, which only the text's size resizes, hears it
  const sep = $('.crumb-sep');
  let sepH = 0;
  if (sep && 'ResizeObserver' in window) new ResizeObserver((es) => { const h = es[0].contentRect.height; if (!h) return; if (sepH && h !== sepH) { fits = null; onScroll(); } sepH = h; }).observe(sep);
  update();

  // a fresh note on every press, so a screen reader hears it again
  const note = $('#copyNote');
  let noteT = 0;
  const say = (t, ms) => {
    clearTimeout(noteT);
    note.textContent = '';
    requestAnimationFrame(() => {
      note.textContent = t;
      if (!RM && note.animate) note.animate([{ opacity: 0, transform: 'translateY(0.45em)' }, { opacity: 1, transform: 'none' }], { duration: seconds('--t-3', 0.4) * 1000, easing: tok('--ease') || 'ease-out' });
      noteT = setTimeout(() => { note.textContent = ''; }, ms);
    });
  };
  $('#copyBib').addEventListener('click', async () => {
    const txt = $('#bibtex').textContent;
    try { await navigator.clipboard.writeText(txt); say('Copied.', 4000); }
    catch (e) {
      const r = document.createRange(); r.selectNodeContents($('#bibtex'));
      const s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      say(HOVERLESS ? 'Selected. Touch and hold it to copy.' : 'Selected. Press Ctrl+C or Cmd+C to copy.', 9000);
    }
  });
}

// ====================================================================== boot
const parts = [initNav, initControls, initPaths, initReadings, initLab, initRope, initPool, initTour, initContract, initSlope, initRepackStage, initNamed, initMSD, initBranch, initUnet, initSystems, initEnd];
// each part starts in its own task, the bar and the opening first, so the page can paint between them and no single task runs long
const boot = () => {
  let i = 0;
  const next = () => {
    const f = parts[i++];
    if (!f) { holdPlace(); loadItalic(); return; }
    try { f(); } catch (e) { console.error(f.name, e); }
    setTimeout(next, 0);
  };
  next();
};
// a #link lands where its place was before the figures above it drew; once every part has run, land it again and
// hold it while late layouts settle, unless the reader has moved (the script at the top of the page)
function holdPlace() {
  let el = null;
  try { const id = decodeURIComponent(location.hash.slice(1)); el = id && document.getElementById(id); } catch (e) { /* a malformed hash */ }
  const nav = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
  if (!el || (nav && nav.type !== 'navigate')) return;
  let moved = false;
  const types = ['wheel', 'touchstart', 'keydown', 'pointerdown'], opt = { capture: true, passive: true };
  const stop = () => { moved = true; ro.disconnect(); types.forEach((t) => removeEventListener(t, stop, opt)); };
  const land = () => { if (!moved && !window.__readerMoved) el.scrollIntoView({ block: 'start' }); };
  const ro = new ResizeObserver(land);
  types.forEach((t) => addEventListener(t, stop, opt));
  land();
  ro.observe(document.body);
  if (document.fonts) document.fonts.ready.then(land);
  setTimeout(stop, 4000);
}
// the italic is first used screens down, so it loads once the page is up (the noscript style declares it)
function loadItalic() {
  if (!window.FontFace || !document.fonts) return;
  const upright = [...document.fonts].find((f) => /Inter/.test(f.family) && f.style === 'normal');
  const go = () => {
    const f = new FontFace('Inter', 'url(fonts/inter-latin-standard-italic.woff2) format("woff2")',
      { style: 'italic', weight: '100 900', display: 'swap', unicodeRange: upright ? upright.unicodeRange : 'U+0000-00FF' });
    document.fonts.add(f);
    f.load().catch(() => {});
  };
  if (window.requestIdleCallback) requestIdleCallback(go, { timeout: 1500 }); else setTimeout(go, 300);
}
// d3 is loaded deferred on the self-hosted page: wait for it there, start at once where it is already in
if (typeof d3 === 'undefined' && document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
else boot();
})();
