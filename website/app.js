const DATA = {"repack":{"seeds":[13,29,41,53,67,83],"ax0":[0.8232041876661003,0.8233935994406542,0.8219183080748164,0.8238790235613092,0.8301391905794541,0.8255466957887013],"ax1":[0.8232724456635336,0.8233549147844315,0.8223302837069276,0.823957710136404,0.8301796226451794,0.8256099889365335],"pk0":[0.8253415346145629,0.8195828790465991,0.825005172441403,0.8185641605406999,0.8264244556427002,0.8223262195204751],"pk1":[0.7731130219375094,0.7535358890270193,0.7723392908771832,0.7799754473112029,0.7801123619700472,0.7906655114804761],"chg_ax":[0.0059668223063151045,0.008325576782226562,0.0075499216715494795,0.006144841512044271,0.0062719980875651045,0.00698089599609375],"chg_pk":[1.1211490631103516,1.2609418233235676,1.41387939453125,1.150795618693034,1.2623087565104167,1.1498578389485676],"gap_training":-0.001806097217432523},"named":{"ax0":0.8228386983938569,"ax1":0.8223233485636666,"pk0":0.8233098620341883,"pk1":0.744521283565296},"msd":{"heart_ax":[0.00324249267578125,0.0045299530029296875,0.0034809112548828125],"heart_pk":[0.08459091186523438,0.11553764343261719,0.10709762573242188],"heart_sep":[0.00362396240234375,0.002288818359375,0.003814697265625],"spleen_ax":[0.0045299530029296875,0.007987022399902344,0.002765655517578125],"spleen_pk":[0.3493309020996094,0.3667116165161133,0.23906230926513672],"spleen_sep":[0.0027894973754882812,0.0035047531127929688,0.003981590270996094]},"msd_named_spleen":0.0020692323644955954,"interv":[["zero",-0.009365088338912808],["swap",-0.015739486108038398],["perm",0.00014089652233654584]],"probes":{"tb":0.9996744791666666,"sc":0.5,"un":0.5,"full":1.0,"loc":0.5,"zero":0.5,"flip":0.0},"unet":{"seeds":[13,29,41,53,67,83],"pack":[0.8232041876661003,0.8233935994406542,0.8219183080748164,0.8238790235613092,0.8301391905794541,0.8255466957887013],"unet":[0.8172108811055677,0.8107680829062366,0.8122415966485246,0.8174004382804092,0.8179785210639239,0.8161599975739973],"best_mean":0.009386914588729348,"final_mean":0.00960221888176536,"ci":[0.0064846530910970665,0.012289176086361629],"p_best":0.03125,"p_final":0.0625,"params_pack":30081234,"params_unet":31867394,"structures":[{"name":"CETN2","d":-0.03665039502084255,"holm":false},{"name":"NUP153","d":-0.0037632609407107034,"holm":false},{"name":"ACTN1","d":0.001855120062828064,"holm":false},{"name":"HIST1H2BJ","d":0.003941800445318222,"holm":false},{"name":"MYH10","d":0.004043251276016235,"holm":false},{"name":"FBL","d":0.004296741137901942,"holm":false},{"name":"NPM1","d":0.0058793798089027405,"holm":false},{"name":"TUBA1B","d":0.005880969266096751,"holm":false},{"name":"TOMM20","d":0.009293404718240103,"holm":false},{"name":"LMNB1","d":0.011992927640676498,"holm":false},{"name":"DSP","d":0.016795318465230524,"holm":false},{"name":"LAMP1","d":0.02065400779247284,"holm":false},{"name":"ATP2A2","d":0.02457561468084653,"holm":true},{"name":"SEC61B","d":0.03210276861985525,"holm":true},{"name":"AAVS1","d":0.039906070878108345,"holm":false}]},"systems":[{"n":65536,"grid":"16x64x64","m":256,"dense":103.83390426635742,"window":13.86403226852417,"pack":16.144015312194824,"speedup":6.4317273155658885,"gb_dense":1.1911659240722656,"gb_window":2.042217254638672,"gb_pack":1.4471940994262695},{"n":131072,"grid":"32x64x64","m":512,"dense":406.1379852294922,"window":26.676688194274902,"pack":29.02284812927246,"speedup":13.99373291761332,"gb_dense":2.3195838928222656,"gb_window":4.021686553955078,"gb_pack":2.8237967491149902},{"n":262144,"grid":"32x128x64","m":1024,"dense":1630.2820434570312,"window":52.62824058532715,"pack":56.35273551940918,"speedup":28.929953948651253,"gb_dense":4.574466705322266,"gb_window":7.978672027587891,"gb_pack":5.57944393157959},{"n":524288,"grid":"64x128x64","m":2048,"dense":6709.878173828125,"window":104.47785568237305,"pack":113.14481353759766,"speedup":59.303453371271445,"gb_dense":9.084232330322266,"gb_window":15.893131256103516,"gb_pack":11.088296890258789},{"n":1048576,"grid":"64x128x128","m":4096,"dense":27245.685546875,"window":208.15438079833984,"pack":273.64959716796875,"speedup":99.5641354083607,"gb_dense":18.103763580322266,"gb_window":31.721561431884766,"gb_pack":22.111373901367188}]};
(() => {
'use strict';
const D = DATA;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
const RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
// phones and tablets: nothing can hover, so the page says "tap" and every hover has a tap to match
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
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

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
  slot: () => ramp(isDark() ? ['#2C2163', '#5639AC', '#8B6AD4', '#BFAAEE', '#F1ECFB'] : ['#F0EBFA', '#C9B7F0', '#9478D8', '#5E43A6', '#271B50']),
  geo: () => ramp(isDark() ? ['#0C3B32', '#0D6B58', '#18A385', '#62D7BC', '#C6F4E9'] : ['#E2F6F0', '#9DE2D0', '#3DC6A6', '#009078', '#00493A']),
};
// Figure 1's faces: the top is the color, the sides are lighter (or darker, in the dark theme)
function faceShades(base) {
  if (isDark()) return [base, mixLab(base, lab('#000000'), 0.22), mixLab(base, lab('#000000'), 0.42)];
  return [base, mixLab(base, lab('#FFFFFF'), 0.42), mixLab(base, lab('#FFFFFF'), 0.70)];
}

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
const LAYOUT_NAMES = { raster: 'raster order', morton: 'Morton order', blocks: 'block-contiguous order', repack: 'repacked: whole z-groups moved' };

// ====================================================================== tooltip
// A mouse or pen reads a mark by hovering it. A finger cannot hover, so a tap opens the tip instead:
// it sits above the finger, where the finger does not cover it, and stays up until the next touch or
// scroll. `tipOff` undoes whatever marked the tapped item (an outline) once the tip goes away.
const tip = $('#tip');
let lastPointer = 'mouse', tapped = false, tipOff = null;
const byFinger = (ev) => (ev.pointerType || lastPointer) !== 'mouse';   // touch or pen
function showTip(html, ev, above) {
  tip.innerHTML = html;
  tip.classList.add('on');
  tip.style.left = '0px'; tip.style.top = '0px';           // measure at full width, not squeezed by an edge
  const r = tip.getBoundingClientRect(), vw = window.innerWidth, vh = window.innerHeight;
  let x = ev.clientX + 14, y = ev.clientY + 14;
  if (above) {
    x = ev.clientX - r.width / 2; y = ev.clientY - r.height - 24;
    if (y < 8) y = ev.clientY + 30;
  } else {
    if (x + r.width > vw - 8) x = ev.clientX - r.width - 14;
    if (y + r.height > vh - 8) y = ev.clientY - r.height - 14;
  }
  tip.style.left = Math.max(8, Math.min(x, vw - r.width - 8)) + 'px';
  tip.style.top = Math.max(8, y) + 'px';
}
function hideTip() {
  tip.classList.remove('on');
  tapped = false;
  if (tipOff) { const f = tipOff; tipOff = null; f(); }
}
function tapTip(html, ev, off) { hideTip(); showTip(html, ev, true); tapped = true; tipOff = off || null; }
document.addEventListener('pointerdown', (ev) => { lastPointer = ev.pointerType; if (tapped) hideTip(); }, { capture: true, passive: true });
window.addEventListener('scroll', () => { if (tapped) hideTip(); }, { passive: true });
document.addEventListener('touchstart', () => {}, { passive: true });   // iOS shows :active only with a touch listener

// ====================================================================== canvas helper
function fitCanvas(canvas, cssW, cssH) {
  const dpr = Math.min(2.5, window.devicePixelRatio || 1);
  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

// ====================================================================== the opening: paths through memory
// To store a 3D field you draw one path through it. The opening draws that path through an 8 x 8 x 8 field
// of tokens, one line from each memory position to the next, and morphs it from one storage order to the
// next while the volume turns: raster, Morton, Hilbert, 4 x 4 x 4 blocks, and a repack that moves whole
// layers. The tokens never move; only the path does. A mint head runs along memory, as at the end.
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
  const NAME = { raster: 'Raster order', morton: 'Morton order', hilbert: 'Hilbert order', blocks: '4 × 4 × 4 blocks', repack: 'Repacked: whole layers moved' };
  const path = {};                                     // path[o][i]: the token at memory position i, centered
  for (const o of ORDERS) {
    const p = new Array(NT);
    SLOTS[o].forEach((s, v) => { p[s] = [v % N - 3.5, Math.floor(v / N) % N - 3.5, Math.floor(v / (N * N)) - 3.5]; });
    if (p.some((q) => !q)) throw new Error('order ' + o + ' is not a permutation');
    path[o] = p;
  }
  const rampF = ramp(['#4B3AB0', '#7356D6', '#9A7DE6', '#C9B6F4', '#F7F3FE']);
  const COL = Array.from({ length: NT }, (_, i) => lab2rgb(rampF(i / (NT - 1))).map((c) => Math.round(c * 255)));
  const P = new Float32Array(NT * 3), S = new Float32Array(NT * 3);
  let from = path.raster, to = path.raster, cur = 'raster', t0 = 0, auto = !RM, switchedAt = performance.now();
  for (let i = 0; i < NT; i++) P.set(path.raster[i], i * 3);
  const buttons = $$('#heroOrders [data-order]'), cap = $('#heroOrder');
  function setOrder(o, byHand) {
    if (byHand) auto = false;
    if (o === cur) return;
    const snap = []; for (let i = 0; i < NT; i++) snap.push([P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]);
    from = snap; to = path[o]; cur = o; t0 = performance.now(); switchedAt = t0;
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.order === o)));
    cap.textContent = NAME[o];
    kick();
  }
  buttons.forEach((b) => b.addEventListener('click', () => setOrder(b.dataset.order, true)));

  // the camera: a slow turn, and a drag (sideways on a phone, so the page still scrolls)
  let yaw = 0.7, pitch = 0.36, drag = null;
  canvas.addEventListener('pointerdown', (e) => { drag = [e.clientX, e.clientY, yaw, pitch]; canvas.setPointerCapture(e.pointerId); canvas.classList.add('grabbing'); auto = false; });
  canvas.addEventListener('pointermove', (e) => {
    if (!drag) return;
    yaw = drag[2] + (e.clientX - drag[0]) * 0.008;
    pitch = clamp(drag[3] + (e.clientY - drag[1]) * 0.006, -1.2, 1.2);
    kick();
  });
  const endDrag = () => { drag = null; canvas.classList.remove('grabbing'); };
  canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);

  let W = 0, H = 0;
  const resize = () => { W = hero.clientWidth; H = hero.clientHeight; fitCanvas(canvas, W, H); kick(); };
  let visible = true, raf = 0, last = 0, head = 0;
  function kick() { if (!raf && visible) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0;
    const dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
    if (auto && visible && now - switchedAt > 5200) setOrder(ORDERS[(ORDERS.indexOf(cur) + 1) % ORDERS.length]);
    const m = RM ? 1 : Math.min(1, (now - t0) / 1700), e = ease(m);
    for (let i = 0; i < NT; i++) for (let k = 0; k < 3; k++) P[i * 3 + k] = from[i][k] + (to[i][k] - from[i][k]) * e;
    if (!RM && !drag) yaw += 0.09 * dt;
    if (!RM) head = (head + dt * 70) % (NT + 120);
    draw();
    if (!RM && visible) raf = requestAnimationFrame(frame);
    else if (m < 1) raf = requestAnimationFrame(frame);
  }
  function draw() {
    const hr = hero.getBoundingClientRect(), r = field.getBoundingClientRect();
    const cx = r.left - hr.left + r.width / 2, cy = r.top - hr.top + r.height / 2, sc = Math.min(r.width, r.height) / 12.6;
    const cyw = Math.cos(yaw), syw = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch), Dv = 26;
    for (let i = 0; i < NT; i++) {
      const x = P[i * 3], y = P[i * 3 + 2], z = P[i * 3 + 1];          // layers run up the screen
      const x1 = x * cyw + z * syw, z1 = -x * syw + z * cyw;
      const y2 = y * cp - z1 * sp, z2 = y * sp + z1 * cp, f = Dv / (Dv - z2);
      S[i * 3] = cx + x1 * sc * f; S[i * 3 + 1] = cy - y2 * sc * f; S[i * 3 + 2] = z2;
    }
    g.clearRect(0, 0, W, H);
    g.globalCompositeOperation = 'lighter'; g.lineCap = 'round'; g.lineJoin = 'round';
    const k = Math.max(0.7, Math.min(1.25, sc / 34));              // line weights follow the sculpture's size
    for (let pass = 0; pass < 2; pass++) {
      for (let i = 1; i < NT; i++) {
        const a = i * 3 - 3, b = i * 3, near = ((S[a + 2] + S[b + 2]) / 2 + 7) / 14;
        const hd = head - i, lit = !RM && hd >= 0 && hd < 46 ? 1 - hd / 46 : 0, c = COL[i];
        if (pass === 0) { g.lineWidth = 7 * k * (0.7 + 0.5 * near); g.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${0.045 + 0.05 * near + 0.12 * lit})`; }
        else {
          g.lineWidth = k * (1.5 * (0.75 + 0.5 * near) + 1.4 * lit);
          g.strokeStyle = lit > 0
            ? `rgba(${Math.round(c[0] + (95 - c[0]) * lit)},${Math.round(c[1] + (224 - c[1]) * lit)},${Math.round(c[2] + (195 - c[2]) * lit)},${0.5 + 0.5 * lit})`
            : `rgba(${c[0]},${c[1]},${c[2]},${0.32 + 0.5 * near})`;
        }
        g.beginPath(); g.moveTo(S[a], S[a + 1]); g.lineTo(S[b], S[b + 1]); g.stroke();
      }
    }
    for (let i = 0; i < NT; i++) {
      const near = (S[i * 3 + 2] + 7) / 14, c = COL[i];
      g.fillStyle = `rgba(${c[0]},${c[1]},${c[2]},${0.18 + 0.4 * near})`;
      g.beginPath(); g.arc(S[i * 3], S[i * 3 + 1], k * (1.3 + 1.2 * near), 0, Math.PI * 2); g.fill();
    }
    const hi = Math.floor(head);
    if (!RM && hi < NT) {
      g.shadowColor = '#5FE0C3'; g.shadowBlur = 18; g.fillStyle = '#C9FFF1';
      g.beginPath(); g.arc(S[hi * 3], S[hi * 3 + 1], 3.6 * k, 0, Math.PI * 2); g.fill(); g.shadowBlur = 0;
    }
    g.globalCompositeOperation = 'source-over';
  }
  new ResizeObserver(resize).observe(hero);
  resize();
  // the path runs only while the opening is in view
  new IntersectionObserver((es) => {
    visible = es.some((x) => x.isIntersecting);
    if (visible) { last = 0; kick(); }
  }).observe(hero);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { last = 0; kick(); } });
}

// ====================================================================== two readings: the title as a packed sequence
// The paper's sheet opens on its idea, drawn with the title. Every letter is a token with two indices: its
// place on the page, a coordinate (row, column), and its place in memory under the storage order. A thread
// ties each letter to its memory slot. Change the order and the memory line, and the threads, rearrange;
// the words stay where they are. PACK3D reads the words; a model that indexes memory reads the line.
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
  const NAME = { raster: 'raster order', morton: 'Morton order', blocks: 'blocks of 2 × 4', repack: 'a repacked order: the rows moved whole' };
  const slot = {};
  for (const o of ORDERS) {
    const s = T.map((t, k) => [KEY[o](t), k]).sort((a, b) => a[0] - b[0]);
    slot[o] = new Int32Array(n); s.forEach(([, k], i) => { slot[o][k] = i; });
  }
  const buttons = $$('#rdOrders [data-order]'), note = $('#rdNote'), seqEl = $('#rdSeq'), oname = $('#rdOrderName');
  const NOTE = note.innerHTML;                         // "point at" for a mouse, "tap" for a finger
  let cur = 'raster', prev = 'raster', t0 = 0, auto = !RM, switchedAt = 0, hov = -1, visible = false, raf = 0;
  function setOrder(o, byHand) {
    if (byHand) auto = false;
    if (o === cur) return;
    prev = cur; cur = o; t0 = performance.now(); switchedAt = t0;
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.order === o)));
    oname.textContent = NAME[o];
    const seq = new Array(n); T.forEach((t, k) => { seq[slot[o][k]] = t.ch; });
    seqEl.textContent = seq.join('');
    seqEl.classList.toggle('bad', o !== 'raster');
    if (hov >= 0) say(hov);
    kick();
  }
  buttons.forEach((b) => b.addEventListener('click', () => setOrder(b.dataset.order, true)));
  const say = (k) => { const t = T[k]; note.textContent = `“${t.ch}”  ·  coordinate (row ${t.r}, column ${t.c})  ·  memory position i = ${slot[cur][k]}`; };
  const pick = (k) => { T.forEach((t, j) => t.el.classList.toggle('on', j === k)); hov = k; if (k >= 0) say(k); else note.innerHTML = NOTE; kick(); };
  T.forEach((t, k) => {
    t.el.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') pick(k); });
    t.el.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') pick(-1); });
    t.el.addEventListener('click', () => { auto = false; pick(hov === k ? -1 : k); });
  });
  document.addEventListener('pointerdown', (e) => { if (hov >= 0 && !big.contains(e.target)) pick(-1); });

  let W = 0, H = 0, ctx = null, SW = 40, MX = 0, MY = 0, col = null;
  const rgb = (hex) => hex2rgb(hex).map((c) => Math.round(c * 255)).join(',');
  function colors() { col = { ink: rgb(tok('--ink')), ink3: rgb(tok('--ink-3')), lav: rgb(tok('--lav')), mint: rgb(tok('--mint-ink')) }; }
  function layout() {
    const fr = fig.getBoundingClientRect(), rr = big.querySelector('.rd-row').getBoundingClientRect(), mr = memEl.getBoundingClientRect();
    SW = Math.max(14, rr.width / n);
    MX = rr.left - fr.left; MY = mr.top - fr.top;
    memEl.style.height = Math.round(SW * 1.06 + (SW >= 26 ? 26 : 8)) + 'px';
    W = fig.clientWidth; H = fig.clientHeight;
    ctx = fitCanvas(cv, W, H);
    kick();
  }
  function kick() { if (!raf) raf = requestAnimationFrame(draw); }
  function draw(now) {
    raf = 0;
    if (!ctx) return;
    if (auto && visible && now - switchedAt > 4200) setOrder(ORDERS[(ORDERS.indexOf(cur) + 1) % ORDERS.length]);
    const m = RM ? 1 : Math.min(1, (now - t0) / 1300), e = ease(m);
    const fr = fig.getBoundingClientRect();
    ctx.clearRect(0, 0, W, H);
    const sh = SW * 1.06, r = Math.min(9, SW * 0.2);
    ctx.textAlign = 'center';
    for (let i = 0; i < n; i++) {                      // the memory: fifteen slots in a row
      const x = MX + i * SW;
      ctx.fillStyle = `rgba(${col.ink},0.05)`;
      ctx.beginPath(); ctx.roundRect(x + SW * 0.06, MY, SW * 0.88, sh, r); ctx.fill();
      if (SW >= 26) { ctx.fillStyle = `rgba(${col.ink3},1)`; ctx.font = '400 11px "DM Mono", ui-monospace, monospace'; ctx.fillText(String(i), x + SW / 2, MY + sh + 18); }
    }
    T.forEach((t, k) => {
      const lr = t.el.getBoundingClientRect();
      const sx = lr.left - fr.left + lr.width / 2, sy = lr.top - fr.top + lr.height * 0.84;
      const i = slot[prev][k] + (slot[cur][k] - slot[prev][k]) * e;
      const ex = MX + i * SW + SW / 2, ey = MY - 3;
      const on = hov === k, dim = hov >= 0 && !on;
      const gr = ctx.createLinearGradient(sx, sy, ex, ey);
      gr.addColorStop(0, on ? `rgba(${col.mint},0.9)` : `rgba(${col.ink},${dim ? 0.04 : 0.14})`);
      gr.addColorStop(1, on ? `rgba(${col.mint},1)` : `rgba(${col.lav},${dim ? 0.18 : 0.85})`);
      ctx.strokeStyle = gr; ctx.lineWidth = on ? 2.2 : 1.4;
      const dy = (ey - sy) * 0.55;
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.bezierCurveTo(sx, sy + dy, ex, ey - dy, ex, ey); ctx.stroke();
      ctx.fillStyle = on ? `rgba(${col.mint},1)` : `rgba(${col.ink},1)`;
      ctx.font = `500 ${Math.round(SW * 0.5)}px "DM Mono", ui-monospace, monospace`; ctx.textBaseline = 'middle';
      ctx.fillText(t.ch, ex, MY + sh * 0.53); ctx.textBaseline = 'alphabetic';
    });
    if (m < 1 || (auto && visible)) kick();
  }
  colors();
  onTheme(() => { colors(); kick(); });
  new ResizeObserver(layout).observe(fig);
  document.fonts.ready.then(layout);
  // the orders change on their own while the figure is in view, until the reader picks one
  new IntersectionObserver((es) => {
    visible = es.some((x) => x.isIntersecting);
    if (visible) { if (!switchedAt) switchedAt = performance.now(); kick(); }
  }, { threshold: 0.4 }).observe(fig);
}

// ====================================================================== theme changes
const themeCbs = [];
function onTheme(cb) { themeCbs.push(cb); }
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => themeCbs.forEach((f) => f()));
new MutationObserver(() => themeCbs.forEach((f) => f())).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

// ====================================================================== the two-indices lab
function initLab() {
  const N = 8, n = 512, NN = 64;
  const L = makeLayouts(N, 2, [3, 6, 0, 5, 1, 7, 2, 4]);
  const inv = {};
  for (const k in L) { inv[k] = new Int32Array(n); L[k].forEach((s, v) => { inv[k][s] = v; }); }
  const vid = (z, y, x) => (z * N + y) * N + x;
  const co = (v) => [Math.floor(v / NN), Math.floor(v / N) % N, v % N];
  const st = { layout: 'raster', mode: 'pair', q: vid(3, 5, 2), prev: null, t: 1, hover: -1 };
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

  // ---- geometry of the two views
  function layoutViews() {
    const wrap = $('#labSlicesWrap');
    const W = wrap.getBoundingClientRect().width;
    const cols = W >= 1000 ? 8 : W >= 560 ? 4 : 2, rows = 8 / cols;
    const gap = W < 560 ? 12 : W >= 1000 ? 14 : 18, lab = 18;
    const S = (W - gap * (cols - 1)) / cols;
    const Hs = rows * (S + lab) + (rows - 1) * gap;
    wrap.style.height = Hs + 'px';
    sl = { W, H: Hs, cols, gap, lab, S, cell: S / N, ctx: fitCanvas(slicesC, W, Hs) };
    const Wr = ribbonC.getBoundingClientRect().width || W;
    const cw = Wr / 64, rgap = Math.max(2, cw * 0.35);
    const Hr = 8 * cw + 7 * rgap + 22;
    ribbonC.style.height = Hr + 'px';
    rb = { W: Wr, H: Hr, cw, rgap, top: 22, ctx: fitCanvas(ribbonC, Wr, Hr) };
  }
  const sliceXY = (v) => { const [z, y, x] = co(v); const c = z % sl.cols, r = Math.floor(z / sl.cols); return [c * (sl.S + sl.gap) + x * sl.cell, r * (sl.S + sl.lab + sl.gap) + sl.lab + y * sl.cell]; };
  const slotXY = (s) => [(s % 64) * rb.cw, rb.top + Math.floor(s / 64) * (rb.cw + rb.rgap)];

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
  function drawSlices() {
    const c = sl.ctx, M = marks();
    c.clearRect(0, 0, sl.W, sl.H);
    c.font = '500 11px ' + tok('--font-mono');
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
      c.globalAlpha = st.mode === 'pair' || !m ? (st.mode === 'pair' ? 1 : 0.55) : 1;
      if (m && m.local) c.fillStyle = tok('--green');
      c.fillRect(x + pad, y + pad, sl.cell - 2 * pad, sl.cell - 2 * pad);
    }
    c.globalAlpha = 1;
    M.forEach((m, v) => {
      const [x, y] = sliceXY(v), s = sl.cell;
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
  function drawRibbon() {
    const c = rb.ctx, M = marks(), lay = L[st.layout], prev = st.prev ? L[st.prev] : null, e = ease(st.t);
    c.clearRect(0, 0, rb.W, rb.H);
    c.font = '500 11px ' + tok('--font-mono');
    c.fillStyle = tok('--ink-3');
    c.fillText('position 0', 0, 12);
    const endLab = 'position 511';
    c.fillText(endLab, rb.W - c.measureText(endLab).width, 12);
    const pad = Math.max(0.35, rb.cw * 0.08);
    const pos = (v) => {
      const [x1, y1] = slotXY(lay[v]);
      if (!prev || st.t >= 1) return [x1, y1];
      const [x0, y0] = slotXY(prev[v]);
      return [x0 + (x1 - x0) * e, y0 + (y1 - y0) * e - Math.sin(Math.PI * e) * rb.cw * 1.4];
    };
    for (let v = 0; v < n; v++) {
      const [x, y] = pos(v), m = M.get(v);
      c.globalAlpha = st.mode === 'pair' || m ? 1 : 0.55;
      c.fillStyle = m && m.local ? tok('--green') : colors[v];
      c.fillRect(x + pad, y + pad, rb.cw - 2 * pad, rb.cw - 2 * pad);
    }
    c.globalAlpha = 1;
    M.forEach((m, v) => {
      const [x, y] = pos(v), s = rb.cw;
      if (m.q) { c.fillStyle = tok('--orange'); c.fillRect(x, y, s, s); c.strokeStyle = tok('--ink'); c.lineWidth = 1.2; c.strokeRect(x, y, s, s); }
      if (m.k) { c.fillStyle = tok('--green'); c.fillRect(x, y, s, s); c.strokeStyle = tok('--ink'); c.lineWidth = 1.2; c.strokeRect(x, y, s, s); }
      if (m.off !== undefined) { c.fillStyle = tok('--coral'); c.beginPath(); c.arc(x + s / 2, y + s / 2, Math.max(1.6, s * 0.32), 0, Math.PI * 2); c.fill(); }
      if (m.nb) { c.strokeStyle = tok('--ink'); c.lineWidth = 1.3; c.setLineDash([2, 1.6]); c.strokeRect(x + 0.6, y + 0.6, s - 1.2, s - 1.2); c.setLineDash([]); }
    });
    if (st.hover >= 0) { const [x, y] = pos(st.hover); c.strokeStyle = tok('--ink'); c.lineWidth = 2; c.strokeRect(x - 0.5, y - 0.5, rb.cw + 1, rb.cw + 1); }
  }
  function draw() { drawSlices(); drawRibbon(); readouts(); }

  // ---- readouts
  const fmtC = (v) => '(' + co(v).join(', ') + ')';
  function readouts() {
    const q = st.q, kk = k(), lay = L[st.layout];
    $('#roQ').textContent = fmtC(q);
    const box = $('#roExtraBox');
    if (kk >= 0) {
      $('#roDc').textContent = '(1, 0, 0)';
      $('#roSlots').textContent = lay[q] + ' → ' + lay[kk];
      const d = lay[kk] - lay[q];
      $('#roDseq').textContent = (d < 0 ? MINUS : '+') + Math.abs(d);
    } else {
      $('#roDc').textContent = 'k is off the top';
      $('#roSlots').textContent = String(lay[q]);
      $('#roDseq').textContent = '—';
    }
    if (st.mode === 'offsets') {
      const tn = new Set(trueNeighbors(q));
      const offs = offsetsOf(q).filter((o) => o.v >= 0);
      const hit = offs.filter((o) => tn.has(o.v)).length;
      box.hidden = false;
      $('#roExtraLab').textContent = 'sequence neighbors that are true neighbors';
      $('#roExtra').textContent = hit + ' of ' + offs.length;
    } else if (st.mode === 'local') {
      box.hidden = false;
      $('#roExtraLab').textContent = 'local window, every order';
      $('#roExtra').textContent = localWindow(q).length + ' tokens';
    } else box.hidden = true;
    const notes = {
      pair: 'Colors follow each token’s place in the sample, so a token keeps its color in every view. The pure repack keeps the raster order inside each z-layer and moves whole layers, the way the paper’s repack moves whole summary groups.',
      offsets: 'Coral dots: the tokens at Δseq = ±1, ±8 and ±64 from q, the offsets that mean “one step along x, y or z” under raster order. Dashed squares: q’s true face neighbors. Change the order and count how many still agree.',
      local: 'PACK3D’s local window: the 3 × 3 × 3 neighborhood of q, defined by coordinates. Change the order: the window stays the same tokens in the sample, wherever they sit in memory.',
    };
    $('#labNote').textContent = notes[st.mode];
  }

  // ---- interaction
  function setLayout(name) {
    if (name === st.layout) return;
    $$('#labLayouts [data-layout]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.layout === name)));
    st.prev = st.layout; st.layout = name; st.t = RM ? 1 : 0;
    const t0 = performance.now();
    const step = (now) => { st.t = RM ? 1 : clamp((now - t0) / 1100, 0, 1); drawRibbon(); readouts(); if (st.t < 1) requestAnimationFrame(step); else { st.prev = null; draw(); } };
    drawSlices(); requestAnimationFrame(step);
  }
  function setMode(m) { st.mode = m; $$('#labModes [data-mode]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === m))); draw(); }
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
  const tipFor = (v) => `token at (z, y, x) = ${fmtC(v)}<br>memory position ${L[st.layout][v]} (${LAYOUT_NAMES[st.layout]})`;
  [[slicesC, hitSlice], [ribbonC, hitRibbon]].forEach(([el, hit]) => {
    el.addEventListener('pointermove', (ev) => { if (ev.pointerType === 'touch') return; const v = hit(ev); if (v !== st.hover) { st.hover = v; drawSlices(); drawRibbon(); } if (v >= 0) showTip(tipFor(v), ev); else hideTip(); });
    el.addEventListener('pointerleave', (ev) => { if (ev.pointerType === 'touch') return; st.hover = -1; hideTip(); drawSlices(); drawRibbon(); });
    // a click or a tap makes the token the query; a finger cannot hover, so a tap also names the token
    el.addEventListener('click', (ev) => { const v = hit(ev); if (v < 0) return; st.q = v; draw(); if (byFinger(ev)) tapTip(tipFor(v), ev); });
  });
  // keyboard: arrows move the query along x and y, Page Up and Page Down along z
  slicesC.tabIndex = 0;
  slicesC.setAttribute('aria-label', `The token field as eight z-slices. ${HOVERLESS ? 'Tap' : 'Click'} a token, or use the arrow keys and Page Up or Page Down, to move the query.`);
  slicesC.addEventListener('keydown', (ev) => {
    const d = { ArrowLeft: [0, 0, -1], ArrowRight: [0, 0, 1], ArrowUp: [0, -1, 0], ArrowDown: [0, 1, 0], PageUp: [1, 0, 0], PageDown: [-1, 0, 0] }[ev.key];
    if (!d) return;
    ev.preventDefault();
    const [z, y, x] = co(st.q);
    st.q = vid(clamp(z + d[0], 0, N - 1), clamp(y + d[1], 0, N - 1), clamp(x + d[2], 0, N - 1));
    draw();
  });
  new ResizeObserver(() => { layoutViews(); draw(); }).observe($('#lab'));
  onTheme(() => { bakeColors(); draw(); });
  layoutViews(); draw();
}

// ====================================================================== rotary dials
function initRope() {
  const G = 9, W = 320, cell = W / G;
  const svg = d3.select('#ropeGrid');
  const OM = { z: 0.55, y: 0.47, x: 0.71 };          // toy frequencies (radians per token)
  const PSI = { z: 0.6, y: -0.4, x: 1.1 };           // toy content: the key's own angle against the query's
  const OMS = 0.29, PSIS = 0.5;                       // the sequence dial
  const rowsRaster = d3.range(G);
  const rowsRepack = [4, 7, 1, 8, 2, 5, 0, 6, 3];     // whole rows moved in memory
  let st = { q: [4, 2], k: [2, 5], repacked: false };
  const slot = (p) => (st.repacked ? rowsRepack.indexOf(p[0]) : p[0]) * G + p[1];
  const g = svg.append('g');
  for (let i = 0; i < G; i++) for (let j = 0; j < G; j++) {
    g.append('rect').attr('x', j * cell + 1.5).attr('y', i * cell + 1.5).attr('width', cell - 3).attr('height', cell - 3)
      .attr('rx', 4).attr('class', 'cellr').style('fill', 'var(--track)');
  }
  svg.append('text').attr('x', W).attr('y', W + 16).attr('text-anchor', 'end').attr('class', 'muted-t').style('font-size', '10px').text('x →');
  svg.attr('viewBox', `0 0 ${W} ${W + 20}`);
  svg.append('text').attr('x', 0).attr('y', W + 16).attr('class', 'muted-t').style('font-size', '10px').text('one z-slice · y ↓');
  const slotLab = svg.append('g');
  const tokens = svg.append('g');
  const mk = (cls, fill, lab) => {
    const t = tokens.append('g').attr('class', cls).style('cursor', 'grab');
    // an undrawn margin: a fingertip is wider than the token, so it may grab a little outside it
    t.append('rect').attr('x', -6).attr('y', -6).attr('width', cell + 12).attr('height', cell + 12).style('fill', 'transparent');
    t.append('rect').attr('width', cell - 6).attr('height', cell - 6).attr('x', 3).attr('y', 3).attr('rx', 6).style('fill', fill).style('stroke', 'var(--ink)').style('stroke-width', 1.5);
    t.append('text').attr('x', cell / 2).attr('y', cell / 2 + 5).attr('text-anchor', 'middle').style('font-style', 'italic').style('font-weight', 700).style('fill', '#111').style('font-size', '15px').text(lab);
    return t;
  };
  const tq = mk('tq', 'var(--orange)', 'q'), tk = mk('tk', 'var(--green)', 'k');
  function dial(container, label) {
    const card = d3.select(container).append('div').attr('class', 'dial-card');
    const s = card.append('svg').attr('viewBox', '0 0 120 120');
    s.append('circle').attr('cx', 60).attr('cy', 60).attr('r', 50).style('fill', 'var(--surface-2)').style('stroke', 'var(--rule)').style('stroke-width', 1.5);
    for (let i = 0; i < 24; i++) {
      const a = i / 24 * Math.PI * 2, r0 = i % 6 === 0 ? 42 : 46;
      s.append('line').attr('x1', 60 + r0 * Math.cos(a)).attr('y1', 60 + r0 * Math.sin(a)).attr('x2', 60 + 50 * Math.cos(a)).attr('y2', 60 + 50 * Math.sin(a)).style('stroke', 'var(--rule)').style('stroke-width', 1.2);
    }
    const arc = s.append('path').style('opacity', 0.35);
    const hq = s.append('line').attr('x1', 60).attr('y1', 60).style('stroke', 'var(--orange)').style('stroke-width', 4).style('stroke-linecap', 'round');
    const hk = s.append('line').attr('x1', 60).attr('y1', 60).style('stroke', 'var(--green-ink)').style('stroke-width', 4).style('stroke-linecap', 'round');
    s.append('circle').attr('cx', 60).attr('cy', 60).attr('r', 4).style('fill', 'var(--ink)');
    const cap = card.append('div').attr('class', 'cap');
    return { arc, hq, hk, cap, label };
  }
  const dialsC = ['z', 'y', 'x'].map((a) => dial('#ropeDialsCoord', a));
  const dialS = dial('#ropeDialsSeq', 'seq');
  d3.select('#ropeDialsSeq').append('div');
  d3.select('#ropeDialsSeq').append('div');
  const arcPath = (a0, a1) => {
    const r = 34, d = a1 - a0, large = Math.abs(d) % (2 * Math.PI) > Math.PI ? 1 : 0;
    const sweep = d >= 0 ? 1 : 0;
    const p0 = [60 + r * Math.cos(a0), 60 + r * Math.sin(a0)], p1 = [60 + r * Math.cos(a1), 60 + r * Math.sin(a1)];
    return `M60 60 L${p0[0]} ${p0[1]} A${r} ${r} 0 ${large} ${sweep} ${p1[0]} ${p1[1]} Z`;
  };
  const wrap = (a) => { a = ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI; return a; };
  // each hand shows the turn a token gets from its own index; the shaded arc is the difference
  function setDial(dl, aq, ak, color, text) {
    const R = 44, base = -Math.PI / 2;
    const A = base + wrap(aq), B = A + wrap(ak - aq);
    dl.hq.transition().duration(RM ? 0 : 450).attr('x2', 60 + R * Math.cos(A)).attr('y2', 60 + R * Math.sin(A));
    dl.hk.transition().duration(RM ? 0 : 450).attr('x2', 60 + R * Math.cos(B)).attr('y2', 60 + R * Math.sin(B));
    dl.arc.attr('d', arcPath(A, B)).style('fill', color);
    dl.cap.html(text);
  }
  function update() {
    const [qy, qx] = st.q, [ky, kx] = st.k;
    const cq = { z: 0, y: qy, x: qx }, ck = { z: 0, y: ky, x: kx };
    let logitC = 0;
    ['z', 'y', 'x'].forEach((a, i) => {
      const aq = OM[a] * cq[a], ak = OM[a] * ck[a];      // the hands: pure rotation by coordinate
      const d = ck[a] - cq[a];
      setDial(dialsC[i], aq, ak, 'var(--teal)', `${a} axis<br>Δ${a} = ${d < 0 ? MINUS : d > 0 ? '+' : ''}${Math.abs(d)}`);
      logitC += Math.cos(OM[a] * d + PSI[a]) / 3;          // mean over the three planes, so both meters share a scale
    });
    const sq = slot(st.q), sk = slot(st.k), ds = sk - sq;
    setDial(dialS, OMS * sq, OMS * sk, 'var(--coral)', `memory position<br>Δseq = ${ds < 0 ? MINUS : '+'}${Math.abs(ds)}`);
    const logitS = Math.cos(OMS * ds + PSIS);
    $('#ropeValC').textContent = fix(logitC, 2);
    $('#ropeValS').textContent = fix(logitS, 2);
    $('#ropeMeterC').style.width = ((logitC + 1) / 2 * 100) + '%';
    $('#ropeMeterS').style.width = ((logitS + 1) / 2 * 100) + '%';
    tq.transition().duration(RM ? 0 : 250).attr('transform', `translate(${qx * cell},${qy * cell})`);
    tk.transition().duration(RM ? 0 : 250).attr('transform', `translate(${kx * cell},${ky * cell})`);
    const labs = slotLab.selectAll('text').data(d3.range(G * G));
    labs.join('text').attr('x', (d) => (d % G) * cell + cell - 5).attr('y', (d) => Math.floor(d / G) * cell + cell - 5)
      .attr('text-anchor', 'end').style('font-size', '8.5px').style('fill', 'var(--ink-3)').style('font-family', 'var(--font-mono)')
      .text((d) => slot([Math.floor(d / G), d % G]));
    $('#ropeRepack').textContent = st.repacked ? 'Restore raster order' : 'Repack the memory';
  }
  function dragger(sel, key) {
    sel.call(d3.drag().on('start', function () { d3.select(this).style('cursor', 'grabbing'); })
      .on('drag', (ev) => {
        // the drag event's own x and y, in the grid's units; d3.pointer(ev) would read clientX from
        // the source event, which a touch event does not have, so a finger could not move a token
        const p = [clamp(Math.floor(ev.y / cell), 0, G - 1), clamp(Math.floor(ev.x / cell), 0, G - 1)];
        const other = key === 'q' ? st.k : st.q;
        if (p[0] === other[0] && p[1] === other[1]) return;
        if (p[0] !== st[key][0] || p[1] !== st[key][1]) { st[key] = p; update(); }
      })
      .on('end', function () { d3.select(this).style('cursor', 'grab'); }));
  }
  dragger(tq, 'q'); dragger(tk, 'k');
  $('#ropeMove').addEventListener('click', () => {
    const dy = Math.max(st.q[0], st.k[0]) < G - 1 ? 1 : -Math.min(st.q[0], st.k[0]);
    const dx = Math.max(st.q[1], st.k[1]) < G - 1 ? 1 : -Math.min(st.q[1], st.k[1]);
    st.q = [st.q[0] + dy, st.q[1] + dx]; st.k = [st.k[0] + dy, st.k[1] + dx];
    $('#ropeNote').textContent = 'Both tokens moved by the same step. Every hand turned, but the arcs between them did not, so PACK3D’s logit is unchanged. Packed RoPE keeps its logit only while the move happens to preserve the difference in memory position.';
    update();
  });
  $('#ropeRepack').addEventListener('click', () => {
    st.repacked = !st.repacked;
    $('#ropeNote').textContent = st.repacked
      ? 'The memory order changed and the tokens did not move. PACK3D’s dials are untouched. Packed RoPE now sees a different Δseq for the same two tokens, and its logit changes.'
      : 'Back to raster order.';
    update();
  });
  $('#ropeReset').addEventListener('click', () => { st = { q: [4, 2], k: [2, 5], repacked: false }; $('#ropeNote').textContent = 'The orange hand is the query’s turn and the green hand the key’s. The shaded arc between them is the only positional information the logit receives.'; update(); });
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
    { key: 'tb', title: 'rotate, then pool', mem: membersTB, color: 'var(--teal)', tint: 'var(--tint-teal)' },
    { key: 'sc', title: 'pool, then rotate at center', mem: membersSC, color: 'var(--warm)', tint: 'var(--warm)' },
  ];
  let stateLab, tokArrow, S = 78;
  // drawn in real pixels, so the text stays at its set size on every screen
  function build() {
    svg.selectAll('*').remove();
    const W = Math.max(300, svg.node().getBoundingClientRect().width || 520);
    const narrow = W < 440;
    const R = clamp(Math.round(W / 4 - 22), 54, 86), cy = 118 + R, H = cy + R + (narrow ? 58 : 40);
    S = R * 0.92;
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const cw = narrow ? 44 : 50, gap = narrow ? 8 : 8;
    const blk = svg.append('g').attr('transform', `translate(2,30)`);
    blk.append('text').attr('x', 0).attr('y', -12).attr('class', 'muted-t').text('a block of four tokens along x');
    const cells = blk.selectAll('g.cellb').data([0, 1, 2, 3]).join('g').attr('class', 'cellb').attr('transform', (d) => `translate(${d * (cw + gap)},0)`);
    cells.append('rect').attr('width', cw).attr('height', cw).attr('rx', 7).style('fill', 'var(--surface-2)').style('stroke', 'var(--lav)').style('stroke-width', 1.5);
    cells.append('text').attr('x', cw / 2).attr('y', cw + 17).attr('text-anchor', 'middle').attr('class', 'muted-t').style('font-size', '12px').text((d) => 'x = ' + d);
    stateLab = cells.append('text').attr('x', 6).attr('y', 16).attr('class', 'lab-strong').style('font-size', '13px');
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
      g.append('text').attr('y', R + 24).attr('text-anchor', 'middle').attr('class', 'lab-ink').text(narrow && i === 1 ? 'pool, rotate at center' : p.title);
      p.members = g.append('g').style('opacity', p.key === 'sc' ? 0.5 : 1);
      p.ghost = g.append('line').style('stroke', p.color).style('stroke-width', 3).style('stroke-dasharray', '3 4').style('opacity', 0).style('stroke-linecap', 'round');
      p.arrow = g.append('line').style('stroke', p.color).style('stroke-width', 5).style('stroke-linecap', 'round');
      p.head = g.append('circle').attr('r', 6).style('fill', p.color).style('stroke', 'var(--surface)').style('stroke-width', 1.5);
    });
  }
  function update(animate) {
    const dur = (ms) => (animate && !RM ? ms : 0);
    stateLab.text((d) => states[order[d]].n);
    tokArrow.transition().duration(dur(500))
      .attr('x2', function (d) { return this.__c0 + this.__len * Math.cos(-states[order[d]].a); })
      .attr('y2', function (d) { return this.__c0 + this.__len * Math.sin(-states[order[d]].a); });
    plots.forEach((p) => {
      const ms = p.mem(), v = avg(ms), f = first[p.key];
      p.ghost.attr('x1', 0).attr('y1', 0).attr('x2', f[0] * S).attr('y2', -f[1] * S).style('opacity', swapped ? 0.6 : 0);
      p.arrow.transition().duration(dur(600)).attr('x1', 0).attr('y1', 0).attr('x2', v[0] * S).attr('y2', -v[1] * S);
      p.head.transition().duration(dur(600)).attr('cx', v[0] * S).attr('cy', -v[1] * S);
      p.members.selectAll('line').data(ms).join('line').attr('x1', 0).attr('y1', 0)
        .style('stroke', p.tint).style('stroke-width', 2).style('stroke-linecap', 'round')
        .transition().duration(dur(600)).attr('x2', (d) => d[0] * S).attr('y2', (d) => -d[1] * S);
    });
    const moved = (p) => { const v = avg(p.mem()), f = first[p.key]; return Math.hypot(v[0] - f[0], v[1] - f[1]); };
    $('#poolDtb').textContent = moved(plots[0]).toFixed(3);
    $('#poolDsc').textContent = moved(plots[1]).toFixed(3);
  }
  build();
  onResize(() => { build(); update(false); });
  $('#poolSwap').addEventListener('click', () => {
    order = swapped ? [0, 1, 2, 3] : [0, 2, 1, 3];
    swapped = !swapped;
    $('#poolSwap').textContent = swapped ? 'Swap them back' : 'Swap the states of tokens 1 and 2';
    update(true);
  });
  update(false);
  // the placement probe, from the paper
  const P = D.probes;
  const rows = [['keys rotated before pooling', P.tb, 'var(--teal)'], ['summary-center rotation', P.sc, 'var(--warm)'], ['unrotated summaries', P.un, 'var(--warm)']];
  const box = d3.select('#probeMini');
  box.append('p').attr('class', 'view-label').style('margin-bottom', '6px').text('Placement probe accuracy, 6 seeds');
  rows.forEach(([name, v, col]) => {
    const r = box.append('div').style('display', 'grid').style('grid-template-columns', 'minmax(0,1.3fr) minmax(0,1fr) auto').style('gap', '10px').style('align-items', 'center').style('margin', '4px 0');
    r.append('span').attr('class', 'small').text(name);
    const m = r.append('div').attr('class', 'meter');
    m.append('i').style('width', (v * 100) + '%').style('background', col);
    m.append('b').style('position', 'absolute').style('left', '50%').style('top', '-3px').style('bottom', '-3px').style('width', '1.5px').style('background', 'var(--ink)');
    r.append('span').attr('class', 'mono num').text(v.toFixed(4));
  });
  box.append('p').attr('class', 'small muted').style('margin-top', '6px').text('The line marks chance, 0.5. Only token-before rotation beats it (exact p = 0.031 for each contrast).');
}

// ====================================================================== Figure 1 tour
// The figure is only scaled and moved, never redrawn. Regions are in the figure's own units.
function initTour() {
  const FW = 3016.58, FH = 1080;
  const stops = [
    { t: 'The whole operator', d: `PACK3D separates memory layout from attention geometry. Step through the panels, or ${HOVERLESS ? 'tap' : 'click'} any part of the figure to zoom in.`, r: [0, 0, FW, FH] },
    { t: '1 · A 3D token field', d: 'Queries, keys and values sit on a 3D token grid, so every token has a place in the sample.', r: [16, 16, 572, 580] },
    { t: '2 · Pack for memory (layout only)', d: 'The field may be packed in any memory order for efficient execution, such as a block-Morton or block-contiguous layout. Each token’s grid coordinate travels with it.', r: [16, 592, 572, 456] },
    { t: '3 · Physical 3D coordinates', d: 'Each token carries integer coordinates on the token grid, c = (z, y, x). These, not memory positions, are what PACK3D’s attention reads.', r: [608, 10, 504, 484] },
    { t: '4 · Axial RoPE', d: 'Axial RoPE rotates queries and keys by their coordinates, one subspace per axis, and leaves values unrotated, so query–key compatibility depends on the relative displacement, not on sequence position.', r: [606, 504, 506, 560] },
    { t: '5.1 · Rotate keys before compression', d: 'The compressed branch has its own key and value projections. It rotates each key by its own token coordinate before any pooling. Values are kept unrotated.', r: [1186, 158, 508, 768] },
    { t: '5.2 · Build summaries per 3D block', d: 'Tokens are partitioned into contiguous 3D blocks. Each block’s rotated keys are pooled into one summary key, and its unrotated values into one summary value.', r: [1738, 158, 614, 772] },
    { t: 'Main result', d: 'Because keys are rotated before pooling, each query-to-summary logit is a weighted sum of query–key terms evaluated at the displacements of the tokens that formed the summary (Proposition 1).', r: [1122, 938, 1264, 128] },
    { t: 'A · Local neighborhood (exact)', d: 'Each query, the orange token, attends exactly to the tokens in its coordinate neighborhood.', r: [2428, 28, 584, 408] },
    { t: 'B · Compressed summaries (global)', d: 'It also attends to summaries across the field, drawn here as one summary per 3D block.', r: [2428, 434, 584, 296] },
    { t: 'C · Local + compressed', d: 'Together, the query combines exact local context with compressed global context.', r: [2428, 726, 584, 300] },
  ];
  const view = $('#tourView'), img = $('#tourImg'), spot = $('#tourSpot'), map = $('#tourMap');
  let cur = 0, geom = null;
  const pct = (v, of) => (v / of * 100) + '%';
  const mapBtns = stops.map((s, i) => {
    if (i === 0) return null;
    const b = document.createElement('button');
    const [rx, ry, rw, rh] = s.r;
    b.className = 'map-r'; b.type = 'button'; b.title = s.t; b.setAttribute('aria-label', 'Zoom to ' + s.t);
    Object.assign(b.style, { left: pct(rx, FW), top: pct(ry, FH), width: pct(rw, FW), height: pct(rh, FH) });
    b.addEventListener('click', () => go(cur === i ? 0 : i));
    map.appendChild(b);
    return b;
  });
  function go(i) {
    cur = (i + stops.length) % stops.length;
    mapBtns.forEach((b, j) => b && b.setAttribute('aria-pressed', String(j === cur)));
    $('#tourN').textContent = `${cur + 1} of ${stops.length}`;
    $('#tourT').textContent = stops[cur].t;
    $('#tourD').textContent = stops[cur].d;
    view.classList.toggle('zoomed', cur !== 0);
    place();
  }
  // fit the stop's region into the view, centered, with a margin
  function place() {
    const r = view.getBoundingClientRect(), W = r.width, H = r.height;
    if (!W || !H) return;
    const [rx, ry, rw, rh] = stops[cur].r;
    const s = Math.min(W / rw, H / rh) * (cur === 0 ? 0.98 : 0.92), s0 = W / FW;
    const tx = W / 2 - (rx + rw / 2) * s, ty = H / 2 - (ry + rh / 2) * s;
    geom = { s, tx, ty };
    img.style.transform = `translate(${tx}px, ${ty}px) scale(${s / s0})`;
    const pad = 6;
    Object.assign(spot.style, { left: (tx + rx * s - pad) + 'px', top: (ty + ry * s - pad) + 'px', width: (rw * s + 2 * pad) + 'px', height: (rh * s + 2 * pad) + 'px' });
    spot.classList.toggle('on', cur !== 0);
  }
  // click the overview to zoom into the part under the pointer; click a zoomed view to step back out
  view.addEventListener('click', (ev) => {
    if (cur !== 0 || !geom) { go(0); return; }
    const r = view.getBoundingClientRect();
    const fx = (ev.clientX - r.left - geom.tx) / geom.s, fy = (ev.clientY - r.top - geom.ty) / geom.s;
    const hit = stops.findIndex((s, i) => i > 0 && fx >= s.r[0] && fx <= s.r[0] + s.r[2] && fy >= s.r[1] && fy <= s.r[1] + s.r[3]);
    if (hit > 0) go(hit);
  });
  function fitTargets() {
    const mh = map.getBoundingClientRect().height;
    mapBtns.forEach((b, i) => {
      if (!b) return;
      const [, ry, , rh] = stops[i].r, h = rh / FH * mh;
      if (h < 24) Object.assign(b.style, { top: `calc(${pct(ry, FH)} - ${(24 - h) / 2}px)`, height: '24px' });
      else Object.assign(b.style, { top: pct(ry, FH), height: pct(rh, FH) });
    });
  }
  new ResizeObserver(fitTargets).observe(map);
  $('#tourPrev').addEventListener('click', () => go(cur - 1));
  $('#tourNext').addEventListener('click', () => go(cur + 1));
  view.tabIndex = -1;
  new ResizeObserver(place).observe(view);
  go(0);
}

// ====================================================================== the contract
function initContract() {
  const boxes = $$('#tags input');
  const named = { pk: D.named.pk1 - D.named.pk0, ax: D.named.ax1 - D.named.ax0 };
  const R = D.repack, axd = mean(R.ax1) - mean(R.ax0), pkd = mean(R.pk1) - mean(R.pk0);
  function update() {
    const on = Object.fromEntries(boxes.map((b) => [b.dataset.tag, b.checked]));
    const all = boxes.every((b) => b.checked);
    const v = $('#verdict');
    v.classList.toggle('off', !all);
    if (all) {
      $('#verdictTitle').textContent = 'Inside Proposition 2: a pure repack';
      $('#verdictText').innerHTML = `For PACK3D the repack only permutes the computation: on Allen-15 it moves Dice by ${sgn(axd, 4)}. Packed RoPE, which rotates by sequence position, has no such guarantee: it moves by ${sgn(pkd, 3)}.`;
    } else if (!on.members && on.coord && on.edges) {
      $('#verdictTitle').textContent = 'Outside Proposition 2: a named-layout switch';
      $('#verdictText').innerHTML = `Coordinates and neighborhoods travel, but tokens are summarized in new groups, so the operator itself changes. On Allen-15 (3 seeds), PACK3D loses ${fix(-named.ax, 4)} Dice and packed RoPE loses ${fix(-named.pk, 4)}.`;
    } else {
      $('#verdictTitle').textContent = 'Outside Proposition 2';
      const miss = [!on.coord && 'coordinates', !on.edges && 'neighborhood edges', !on.members && 'summary memberships', !on.slot && 'within-block slots'].filter(Boolean);
      $('#verdictText').innerHTML = `Without ${miss.join(' and ')}, Proposition 2 no longer applies and guarantees nothing. The paper’s only test outside it is the named-layout switch, which changes memberships but keeps coordinates and neighborhoods.`;
    }
  }
  boxes.forEach((b) => b.addEventListener('change', update));
  update();
}

// ====================================================================== charts: helpers
function chartSize(svgSel, aspect, minH) {
  const node = svgSel.node(), W = Math.max(280, node.getBoundingClientRect().width || 600);
  const H = Math.max(minH || 0, W * aspect);
  svgSel.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
  return [W, H];
}
function tableFrom(el, head, rows) {
  const t = d3.select(el); t.selectAll('*').remove();
  t.append('thead').append('tr').selectAll('th').data(head).join('th').text((d) => d);
  t.append('tbody').selectAll('tr').data(rows).join('tr').selectAll('td').data((r) => r).join('td').text((d) => d);
}
// A mark that explains itself, used as sel.call(explain, html). A mouse or pen hovers the mark. A
// fingertip is wider than most marks, so a tap anywhere on the chart opens the tip of the nearest mark
// within reach and outlines that mark while its tip is up.
function explain(sel, html) {
  sel.classed('has-tip', true).property('__tip', html)
    .on('pointermove', (ev) => { if (ev.pointerType !== 'touch') showTip(html, ev); })
    .on('pointerleave', (ev) => { if (ev.pointerType !== 'touch') hideTip(); });
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
function onResize(fn) { redrawers.push(fn); }
let rzT = 0;
window.addEventListener('resize', () => { clearTimeout(rzT); rzT = setTimeout(() => redrawers.forEach((f) => f()), 120); });

// ====================================================================== the repack slope chart
function initSlope() {
  const R = D.repack, svg = d3.select('#slope');
  const ax0 = mean(R.ax0), ax1 = mean(R.ax1), pk0 = mean(R.pk0), pk1 = mean(R.pk1);
  $('#bnAx').textContent = sgn(ax1 - ax0, 4);
  $('#bnPk').textContent = sgn(pk1 - pk0, 3);
  $('#bnAxD').textContent = `Dice ${ax0.toFixed(4)} → ${ax1.toFixed(4)}`;
  $('#bnPkD').textContent = `Dice ${pk0.toFixed(4)} → ${pk1.toFixed(4)}`;
  tableFrom('#slopeTable', ['seed', 'PACK3D before', 'PACK3D after', 'Packed RoPE before', 'Packed RoPE after'],
    R.seeds.map((s, i) => [s, R.ax0[i].toFixed(4), R.ax1[i].toFixed(4), R.pk0[i].toFixed(4), R.pk1[i].toFixed(4)])
      .concat([['mean', ax0.toFixed(4), ax1.toFixed(4), pk0.toFixed(4), pk1.toFixed(4)]]));
  let progress = 1;
  function draw() {
    svg.selectAll('*').remove();
    const [W, H] = chartSize(svg, 0.72, 300);
    const m = { l: 46, r: 104, t: 18, b: 38 };                // the right margin holds the series labels
    const x = d3.scalePoint().domain(['before', 'after']).range([m.l + 30, W - m.r]);
    const y = d3.scaleLinear().domain([0.75, 0.83]).range([H - m.b, m.t]);
    svg.append('g').attr('class', 'grid').selectAll('line').data([0.76, 0.78, 0.8, 0.82]).join('line')
      .attr('x1', m.l).attr('x2', W - m.r + 12).attr('y1', y).attr('y2', y);
    svg.append('g').selectAll('text').data([0.76, 0.78, 0.8, 0.82]).join('text').attr('class', 'muted-t num')
      .attr('x', m.l - 8).attr('y', (d) => y(d) + 4).attr('text-anchor', 'end').text((d) => d.toFixed(2));
    svg.append('text').attr('x', m.l - 8).attr('y', m.t - 4).attr('text-anchor', 'end').attr('class', 'muted-t').text('Dice');
    [['before', 'training layout'], ['after', 'pure repack']].forEach(([k, lab]) => {
      svg.append('line').attr('x1', x(k)).attr('x2', x(k)).attr('y1', m.t).attr('y2', H - m.b).style('stroke', 'var(--rule)').style('stroke-dasharray', '3 4');
      svg.append('text').attr('x', x(k)).attr('y', H - 12).attr('text-anchor', 'middle').attr('class', 'lab-ink').text(lab);
    });
    const seg = (a, b) => [x('before'), y(a), x('before') + (x('after') - x('before')) * progress, y(a + (b - a) * progress)];
    const series = [
      { k: 'pk', s0: R.pk0, s1: R.pk1, tint: 'var(--tint-coral)', col: 'var(--coral)', name: 'Packed RoPE' },
      { k: 'ax', s0: R.ax0, s1: R.ax1, tint: 'var(--tint-teal)', col: 'var(--teal)', name: 'PACK3D' },
    ];
    series.forEach((S) => {
      const gS = svg.append('g');
      S.s0.forEach((a, i) => {
        const b = S.s1[i], p = seg(a, b);
        gS.append('line').attr('x1', p[0]).attr('y1', p[1]).attr('x2', p[2]).attr('y2', p[3]).style('stroke', S.tint).style('stroke-width', 1.4);
        gS.append('line').attr('x1', p[0]).attr('y1', p[1]).attr('x2', p[2]).attr('y2', p[3]).style('stroke', 'transparent').style('stroke-width', 10)
          .call(explain, `<b>${S.name}</b>, seed ${R.seeds[i]}<br>${a.toFixed(4)} → ${b.toFixed(4)} (${sgn(b - a, 4)})`);
      });
      const a = mean(S.s0), b = mean(S.s1), p = seg(a, b);
      gS.append('line').attr('x1', p[0]).attr('y1', p[1]).attr('x2', p[2]).attr('y2', p[3]).style('stroke', S.col).style('stroke-width', 4).style('stroke-linecap', 'round');
      [[p[0], p[1]], [p[2], p[3]]].forEach(([cx, cy]) => gS.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 6.5).style('fill', S.col).style('stroke', 'var(--surface)').style('stroke-width', 2));
      if (progress >= 1) {
        gS.append('text').attr('x', p[2] + 12).attr('y', p[3] + 4).attr('class', 'lab-strong').text(S.name);
      }
    });
  }
  function replay() {
    if (RM) { progress = 1; draw(); return; }
    const t0 = performance.now();
    const step = (now) => { progress = ease(clamp((now - t0) / 1600, 0, 1)); draw(); if (progress < 1) requestAnimationFrame(step); };
    progress = 0; draw(); requestAnimationFrame(step);
  }
  $('#replay').addEventListener('click', replay);
  onResize(draw); onTheme(draw);
  draw();
  // the first time the result scrolls into view, play the repack once
  if (!RM && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); replay(); } }, { threshold: 0.55 });
    io.observe($('#repackBench'));
  }
}

// ====================================================================== how many predictions moved: the repack on a cell
// One crop's worth of positions, 64 x 64 x 64, drawn as a cell for illustration, under each model. The memory
// is repacked in sixteen groups, and then every prediction the repack changed lights up: about 18 for PACK3D
// (teal, each circled so it can be seen) and about 3,215 for packed RoPE (coral), the paper's mean rates
// times 262,144 positions. The paper does not map where in a crop the changes fall, so they are placed along
// the cell's boundaries, where a segmentation is least sure. WebGL: one soft point per voxel drawn, added
// together like light, in two viewports of one canvas. The volume is built only when the reader gets near.
function initRepackStage() {
  const stage = $('#repackStage'), canvas = $('#swCanvas');
  if (!stage || !canvas) return;
  const R = D.repack, G = 64, NV = G * G * G;
  const rateAx = mean(R.chg_ax), ratePk = mean(R.chg_pk);
  const nAx = Math.round(rateAx / 100 * NV), nPk = Math.round(ratePk / 100 * NV);
  $('#swRA').textContent = `${rateAx.toFixed(4)}%`;
  $('#swRB').textContent = `${ratePk.toFixed(2)}%`;
  canvas.setAttribute('aria-label', `Two copies of one cell, ${intf(NV)} positions each, under the same repack. About ${nAx} predictions change under PACK3D, each circled, and about ${intf(nPk)} under packed RoPE.`);
  const go = $('#swGo'), stateEl = $('#swState'), stateT = $('#swStateT'), cA = $('#swNA'), cB = $('#swNB');
  const strips = [$('#swStripA'), $('#swStripB')];
  let built = false;
  new IntersectionObserver((es) => { if (!built && es.some((e) => e.isIntersecting)) { built = true; build(); } }, { rootMargin: '700px 0px' }).observe(stage);

  function build() {
    const gl = canvas.getContext('webgl', { antialias: false, alpha: true, premultipliedAlpha: true });
    if (!gl) { stage.classList.add('no-gl'); return; }
    // ---------------------------------------------------------------- a cell, as a segmented volume
    let seed = 7;
    const rnd = () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    const wob = (x, y, z) => 0.5 * Math.sin(3.1 * x + 1.7) * Math.sin(2.6 * y + 0.4) * Math.sin(2.9 * z + 2.1) + 0.3 * Math.sin(5.3 * x + 1.1 * y + 2.0) * Math.cos(4.1 * z - 0.7 * y);
    const cls = new Uint8Array(NV);                   // 0 outside, 1 cytoplasm, 2 nucleus, 3 organelle
    const at = (x, y, z) => (z * G + y) * G + x, P = (v) => (v - G / 2 + 0.5) / (G / 2);
    for (let z = 0; z < G; z++) for (let y = 0; y < G; y++) for (let x = 0; x < G; x++) {
      const px = P(x), py = P(y), pz = P(z);
      if (Math.hypot(px / 0.93, py / 0.74, pz / 0.66) + 0.07 * wob(px, py, pz) >= 1) continue;
      cls[at(x, y, z)] = Math.hypot((px - 0.16) / 0.42, (py + 0.04) / 0.35, (pz - 0.02) / 0.36) + 0.05 * wob(py, pz, px) < 1 ? 2 : 1;
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
        const l = Math.hypot(dx, dy, dz) || 1; x += dx / l; y += dy / l; z += (dz / l) * 0.8;
      }
    }
    const NB = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
    const differs = (x, y, z, c) => NB.some(([a, b, d]) => {
      const X = x + a, Y = y + b, Z = z + d;
      if (X < 0 || Y < 0 || Z < 0 || X >= G || Y >= G || Z >= G) return c !== 0;
      return cls[at(X, Y, Z)] !== c;
    });
    const touches = (x, y, z, c) => NB.some(([a, b, d]) => {
      const X = x + a, Y = y + b, Z = z + d;
      return X >= 0 && Y >= 0 && Z >= 0 && X < G && Y < G && Z < G && cls[at(X, Y, Z)] === c;
    });
    const memb = [], env = [], edge = [], pos = [], col = [], size = [];
    const C = { cyto: [0.42, 0.30, 0.86], memb: [0.66, 0.54, 1.0], nuc: [0.08, 0.62, 0.52], env: [0.30, 0.92, 0.76], mito: [1.0, 0.86, 0.78] };
    const put = (x, y, z, rgb, k, s) => {
      const j = () => (rnd() - 0.5) * 0.9 / (G / 2);
      pos.push(P(x) + j(), P(y) + j(), P(z) + j()); col.push(rgb[0] * k, rgb[1] * k, rgb[2] * k); size.push(s);
    };
    for (let z = 0; z < G; z++) for (let y = 0; y < G; y++) for (let x = 0; x < G; x++) {
      const c = cls[at(x, y, z)];
      if (c === 0) { if (differs(x, y, z, 0)) edge.push([x, y, z]); continue; }
      if (c === 1) {
        if (differs(x, y, z, 1) && !touches(x, y, z, 2) && !touches(x, y, z, 3)) { memb.push([x, y, z]); if (rnd() < 0.55) put(x, y, z, C.memb, 0.36, 1.5); }
        else if (rnd() < 0.08) put(x, y, z, C.cyto, 0.03, 3.4);
      } else if (c === 2) {
        if (differs(x, y, z, 2)) { env.push([x, y, z]); if (rnd() < 0.6) put(x, y, z, C.env, 0.26, 1.6); }
        else if (rnd() < 0.2) put(x, y, z, C.nuc, 0.085, 2.6);
      } else put(x, y, z, C.mito, 0.4, 1.4);
    }
    // the predictions the repack changes, at the paper's rates over all 262,144 positions
    const pick = (list, k) => { const a = list.slice(), out = []; for (let i = 0; i < k && a.length; i++) out.push(a.splice(Math.floor(rnd() * a.length), 1)[0]); return out; };
    const sparksPk = pick(memb.concat(env, edge), nPk), sparksAx = pick(env, nAx);

    // ---------------------------------------------------------------- WebGL
    const VS = `attribute vec3 a_pos; attribute vec3 a_col; attribute float a_size; attribute float a_t;
uniform mat4 u_mvp; uniform float u_vox, u_k, u_time, u_mode, u_dist; uniform vec3 u_spark;
varying vec3 v_col; varying float v_ring;
void main() {
  vec4 p = u_mvp * vec4(a_pos, 1.0);
  gl_Position = p;
  float fog = clamp((p.w - u_dist + 0.95) / 1.9, 0.0, 1.0);
  if (u_mode < 0.5) { v_col = a_col * mix(1.2, 0.5, fog); v_ring = 0.0; gl_PointSize = a_size * u_vox / p.w; }
  else {
    float k = clamp((u_k - a_t) * 3.0, 0.0, 1.0);
    float flare = 1.0 + 1.6 * exp(-pow((u_k - a_t) * 7.0, 2.0)) * step(a_t, u_k);
    float tw = 0.85 + 0.15 * sin(u_time * 5.0 + a_t * 40.0);
    v_col = u_spark * k * tw * flare * mix(1.0, 0.6, fog);
    v_ring = u_mode > 1.5 ? 1.0 : 0.0;
    gl_PointSize = (u_mode > 1.5 ? 5.2 : (1.5 + 1.1 * (flare - 1.0))) * u_vox / p.w * k;
  }
}`;
    const FS = `precision mediump float; varying vec3 v_col; varying float v_ring;
void main() {
  float r = length(gl_PointCoord - 0.5) * 2.0;
  float a = v_ring > 0.5 ? smoothstep(0.74, 0.82, r) * (1.0 - smoothstep(0.88, 0.98, r)) * 0.95 : exp(-r * r * 4.0) * step(r, 1.0);
  vec3 c = v_col * a;
  gl_FragColor = vec4(c, max(c.r, max(c.g, c.b)));   // valid premultiplied light over the stage
}`;
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog); gl.useProgram(prog);
    const U = {}; ['u_mvp', 'u_vox', 'u_k', 'u_time', 'u_mode', 'u_dist', 'u_spark'].forEach((n) => { U[n] = gl.getUniformLocation(prog, n); });
    const buf = (arr, n, name) => { const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(arr), gl.STATIC_DRAW); return { b, n, l: gl.getAttribLocation(prog, name) }; };
    const bind = (...bs) => bs.forEach((x) => { gl.bindBuffer(gl.ARRAY_BUFFER, x.b); gl.enableVertexAttribArray(x.l); gl.vertexAttribPointer(x.l, x.n, gl.FLOAT, false, 0, 0); });
    const NP = size.length;
    const cell = [buf(pos, 3, 'a_pos'), buf(col, 3, 'a_col'), buf(size, 1, 'a_size'), buf(new Float32Array(NP), 1, 'a_t')];
    const sparkSet = (list) => {
      const p = [], t = [];
      list.forEach(([x, y, z]) => { p.push(P(x), P(y), P(z)); t.push(rnd() * 0.75); });
      return { n: list.length, b: [buf(p, 3, 'a_pos'), buf(new Float32Array(list.length * 3), 3, 'a_col'), buf(new Float32Array(list.length).fill(1), 1, 'a_size'), buf(t, 1, 'a_t')] };
    };
    const SPK = sparkSet(sparksPk), SAX = sparkSet(sparksAx);
    gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE); gl.clearColor(0, 0, 0, 0);
    const persp = (f, a, nn, fa) => { const t = 1 / Math.tan(f / 2); return [t / a, 0, 0, 0, 0, t, 0, 0, 0, 0, (fa + nn) / (nn - fa), -1, 0, 0, 2 * fa * nn / (nn - fa), 0]; };
    const mul = (a, b) => { const o = new Array(16).fill(0); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o; };
    const view = (yaw, pitch, d) => {
      const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
      return [cy, sp * sy, -cp * sy, 0, 0, cp, sp, 0, sy, -sp * cy, cp * cy, 0, 0, 0, -d, 1];
    };

    // ---------------------------------------------------------------- the memory strips: all positions in raster order
    const SEG = 16, perm = [9, 3, 14, 0, 11, 6, 1, 13, 4, 15, 7, 2, 12, 5, 10, 8];
    const SCOL = [[22, 28, 27], [96, 78, 150], [26, 150, 124], [235, 228, 240]];
    let stripSrc = null;
    function stripImage(w) {
      const can = document.createElement('canvas'); can.width = w; can.height = 1;
      const c2 = can.getContext('2d'), img = c2.createImageData(w, 1);
      for (let px = 0; px < w; px++) {
        const a = Math.floor(px / w * NV), b = Math.floor((px + 1) / w * NV); let r = 0, gg = 0, bl = 0;
        for (let i = a; i < b; i++) { const c = SCOL[cls[i]]; r += c[0]; gg += c[1]; bl += c[2]; }
        const k = Math.max(1, b - a); img.data.set([r / k, gg / k, bl / k, 255], px * 4);
      }
      c2.putImageData(img, 0, 0); return can;
    }

    // ---------------------------------------------------------------- the story: the training layout, the repack, the changes
    let phase = 'before', t0 = performance.now(), visible = false, played = false, raf = 0, last = 0;
    const D_ = { repack: 1700, restore: 1100 };
    const STATE = {
      before: 'Training layout: raster order',
      repack: 'Repacking: the same 262,144 tokens, moved in memory in 16 groups',
      after: 'Repacked. The same cell, the same two models, a new memory order',
      restore: 'Back to the training layout',
    };
    function setPhase(p) {
      phase = RM && p === 'repack' ? 'after' : RM && p === 'restore' ? 'before' : p;
      t0 = performance.now();
      stateEl.classList.toggle('hot', phase === 'after');
      stateT.textContent = STATE[phase];
      go.textContent = phase === 'after' || phase === 'repack' ? 'Restore the training layout' : 'Repack the memory';
      kick();
    }
    go.addEventListener('click', () => { played = true; setPhase(phase === 'after' || phase === 'repack' ? 'restore' : 'repack'); });

    let yaw = 0.6, pitch = 0.42, drag = null, W = 0, H = 0, dpr = 1;
    canvas.addEventListener('pointerdown', (e) => { drag = [e.clientX, e.clientY, yaw, pitch]; canvas.setPointerCapture(e.pointerId); canvas.classList.add('grabbing'); });
    canvas.addEventListener('pointermove', (e) => {
      if (!drag) return;
      yaw = drag[2] + (e.clientX - drag[0]) * 0.008; pitch = clamp(drag[3] + (e.clientY - drag[1]) * 0.006, -0.4, 1.3); kick();
    });
    const endDrag = () => { drag = null; canvas.classList.remove('grabbing'); };
    canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);
    function resize() {
      dpr = Math.min(2, window.devicePixelRatio || 1); W = stage.clientWidth; H = stage.clientHeight;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      strips.forEach((s) => { s.width = Math.round(s.clientWidth * dpr); s.height = Math.round(s.clientHeight * dpr); });
      stripSrc = stripImage(Math.max(64, strips[0].width));
      kick();
    }
    function kick() { if (!raf) raf = requestAnimationFrame(frame); }
    function frame(now) {
      raf = 0;
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
      const el = now - t0;
      if (phase === 'repack' && el > D_.repack) setPhase('after');
      else if (phase === 'restore' && el > D_.restore) setPhase('before');
      const e2 = now - t0;
      const shuffle = phase === 'repack' ? ease(Math.min(1, e2 / D_.repack)) : phase === 'after' ? 1 : phase === 'restore' ? 1 - ease(Math.min(1, e2 / D_.restore)) : 0;
      const kSpark = phase === 'after' ? (RM ? 1.4 : Math.min(1.4, e2 / 900)) : phase === 'restore' ? Math.max(0, 1 - e2 / 500) * 1.4 : 0;
      const c = phase === 'after' ? (RM ? 1 : Math.min(1, e2 / 1100)) : phase === 'restore' ? Math.max(0, 1 - e2 / 500) : 0;
      cA.textContent = intf(c * nAx); cB.textContent = intf(c * nPk);
      if (!RM && !drag) yaw += dt * 0.12;
      // the cells
      gl.viewport(0, 0, canvas.width, canvas.height); gl.clear(gl.COLOR_BUFFER_BIT);
      const cr = canvas.getBoundingClientRect();
      ['#swA', '#swB'].forEach((id, side) => {
        const r = $(id).getBoundingClientRect();
        const x = (r.left - cr.left) * dpr, y = (cr.bottom - r.bottom) * dpr, w = r.width * dpr, h = r.height * dpr;
        if (w < 2 || h < 2) return;
        gl.viewport(x, y, w, h);
        const dist = 3.45 / Math.min(1, w / h);
        gl.uniformMatrix4fv(U.u_mvp, false, mul(persp(0.62, w / h, 0.1, 40), view(yaw, pitch, dist)));
        gl.uniform1f(U.u_dist, dist);
        gl.uniform1f(U.u_vox, (2 / G) * (h / 2) / Math.tan(0.31));
        gl.uniform1f(U.u_time, now / 1000);
        gl.uniform1f(U.u_mode, 0); bind(...cell); gl.drawArrays(gl.POINTS, 0, NP);
        gl.uniform1f(U.u_k, kSpark);
        if (side === 1) { gl.uniform3f(U.u_spark, 1.0, 0.45, 0.47); gl.uniform1f(U.u_mode, 1); bind(...SPK.b); gl.drawArrays(gl.POINTS, 0, SPK.n); }
        else {
          gl.uniform3f(U.u_spark, 0.37, 0.88, 0.76); gl.uniform1f(U.u_mode, 1); bind(...SAX.b); gl.drawArrays(gl.POINTS, 0, SAX.n);
          gl.uniform1f(U.u_mode, 2); gl.drawArrays(gl.POINTS, 0, SAX.n);   // circled: one in 14,000 is too small to see
        }
      });
      // the strips: the same repack under both models, sixteen groups sliding to their new places
      strips.forEach((s) => {
        const g2 = s.getContext('2d'), w = s.width, h = s.height, sw = w / SEG;
        g2.clearRect(0, 0, w, h); g2.imageSmoothingEnabled = false;
        for (let k = 0; k < SEG; k++) g2.drawImage(stripSrc, k * stripSrc.width / SEG, 0, stripSrc.width / SEG, 1, (k + (perm.indexOf(k) - k) * shuffle) * sw, 0, sw + 0.5, h);
      });
      const moving = phase === 'repack' || phase === 'restore' || (phase === 'after' && e2 < 1500);
      if (visible && (!RM || moving || drag)) kick();
    }
    new ResizeObserver(resize).observe(stage);
    resize();
    // the repack plays by itself the first time the cells are well in view
    new IntersectionObserver((es) => {
      visible = es.some((x) => x.isIntersecting && x.intersectionRatio > 0.45);
      if (visible) { last = 0; kick(); if (!played) { played = true; setTimeout(() => { if (phase === 'before') setPhase('repack'); }, 700); } }
    }, { threshold: [0, 0.45, 0.7] }).observe(stage);
    canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); stage.classList.add('no-gl'); });
    setPhase(RM ? 'after' : 'before');
    if (RM) played = true;
  }
}

// ====================================================================== named switch
function initNamed() {
  const svg = d3.select('#named'), n = D.named;
  const rows = [['PACK3D', n.ax1 - n.ax0, 'var(--teal)', n.ax0, n.ax1], ['Packed RoPE', n.pk1 - n.pk0, 'var(--coral)', n.pk0, n.pk1]];
  function draw() {
    svg.selectAll('*').remove();
    const [W] = chartSize(svg, 0, 120);
    const H = 120, m = { l: 110, r: 70 };
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const x = d3.scaleLinear().domain([-0.09, 0]).range([m.l, W - m.r]);
    (W < 480 ? [-0.08, -0.04, 0] : [-0.08, -0.06, -0.04, -0.02, 0]).forEach((t) => {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', 10).attr('y2', H - 24).style('stroke', t === 0 ? 'var(--ink)' : 'var(--grid)').style('stroke-width', t === 0 ? 1.5 : 1);
      svg.append('text').attr('x', x(t)).attr('y', H - 8).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(t === 0 ? '0' : fix(t, 2));
    });
    rows.forEach(([name, v, col, a, b], i) => {
      const yy = 22 + i * 38;
      svg.append('text').attr('x', m.l - 12).attr('y', yy + 13).attr('text-anchor', 'end').attr('class', 'lab-ink').text(name);
      const bw = Math.max(1.5, x(0) - x(v));
      svg.append('rect').attr('x', x(0) - bw).attr('y', yy).attr('width', bw).attr('height', 18).attr('rx', 3).style('fill', col)
        .call(explain, `<b>${name}</b>, named switch<br>${a.toFixed(4)} → ${b.toFixed(4)}`);
      svg.append('text').attr('x', x(0) + 8).attr('y', yy + 13).attr('class', 'lab-strong num').text(fix(v, 4));
    });
  }
  onResize(draw); draw();
}

// ====================================================================== MSD
function initMSD() {
  const svg = d3.select('#msdChart'), M = D.msd, R = D.repack;
  const groups = [
    ['Allen-15 microscopy · 6 seeds', [['PACK3D', R.chg_ax, 'var(--teal)'], ['Packed RoPE', R.chg_pk, 'var(--coral)']]],
    ['MSD Heart (MRI) · 3 seeds', [['PACK3D', M.heart_ax, 'var(--teal)'], ['Separable PE', M.heart_sep, 'var(--lav)'], ['Packed RoPE', M.heart_pk, 'var(--coral)']]],
    ['MSD Spleen (CT) · 3 seeds', [['PACK3D', M.spleen_ax, 'var(--teal)'], ['Separable PE', M.spleen_sep, 'var(--lav)'], ['Packed RoPE', M.spleen_pk, 'var(--coral)']]],
  ];
  function draw() {
    svg.selectAll('*').remove();
    const W = Math.max(300, svg.node().getBoundingClientRect().width || 700);
    const narrow = W < 560;
    const rowH = 26, headH = 30;
    const H = 30 + groups.reduce((s, g) => s + headH + g[1].length * rowH, 0) + 34;
    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const m = { l: narrow ? 104 : 150, r: 16 };
    const x = d3.scaleLog().domain([0.0008, 2.5]).range([m.l, W - m.r]);
    const top = 16, bot = H - 30;
    [0.001, 0.01, 0.1, 1].forEach((t) => {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top).attr('y2', bot).style('stroke', 'var(--grid)');
      svg.append('text').attr('x', x(t)).attr('y', bot + 18).attr('text-anchor', 'middle').attr('class', 'muted-t num').text(t + '%');
    });
    let yy = top + 8;
    groups.forEach(([title, rows]) => {
      svg.append('text').attr('x', 0).attr('y', yy + 14).attr('class', 'lab-strong').style('font-size', narrow ? '12.5px' : '13.5px').text(title);
      yy += headH;
      rows.forEach(([name, vals, col]) => {
        svg.append('text').attr('x', 8).attr('y', yy + 4).attr('class', 'lab-ink').style('font-size', '13px').text(name);
        vals.forEach((v, i) => {
          svg.append('circle').attr('cx', x(v)).attr('cy', yy).attr('r', 5.5).style('fill', col).style('stroke', 'var(--surface)').style('stroke-width', 1.5)
            .call(explain, `<b>${name}</b> · ${title.split(' · ')[0]}<br>seed ${i + 1}: ${v < 0.01 ? v.toFixed(4) : v.toFixed(3)}% of positions changed`);
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
  function drawI() {
    svgI.selectAll('*').remove();
    const W = Math.max(280, svgI.node().getBoundingClientRect().width || 500);
    const narrow = W < 460, H = narrow ? 210 : 150;
    svgI.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const valW = 64, z0 = W - valW;
    const x = d3.scaleLinear().domain([-0.018, 0]).range([narrow ? 8 : W * 0.46, z0]);
    D.interv.forEach(([k, v], i) => {
      const yy = narrow ? 20 + i * 64 : 26 + i * 42;
      svgI.append('text').attr('x', 0).attr('y', narrow ? yy : yy + 13).attr('class', 'lab-ink').style('font-size', '13px').text(IV[k]);
      const by = narrow ? yy + 10 : yy;
      const bw = Math.max(1.5, Math.abs(x(v) - x(0)));
      svgI.append('rect').attr('x', v < 0 ? z0 - bw : z0).attr('y', by).attr('width', bw).attr('height', 18).attr('rx', 3).style('fill', 'var(--tint-teal)').style('stroke', 'var(--teal)').style('stroke-width', 1)
        .call(explain, `<b>${IV[k]}</b><br>Dice change ${sgn(v, 4)}, mean of 3 seeds`);
      svgI.append('text').attr('x', z0 + 8).attr('y', by + 13).attr('class', 'lab-strong num').text(sgn(v, 4));
    });
    svgI.append('line').attr('x1', z0).attr('x2', z0).attr('y1', 14).attr('y2', H - 8).style('stroke', 'var(--ink)').style('stroke-width', 1.5);
  }
  const svgP = d3.select('#probes'), P = D.probes;
  const rows = [
    ['Placement probe', null], ['keys rotated before pooling', P.tb, 'var(--teal)'], ['summary-center rotation', P.sc, 'var(--warm)'], ['unrotated summaries', P.un, 'var(--warm)'],
    ['Long-range probe', null], ['local + global', P.full, 'var(--teal)'], ['local only, radius 0–2', P.loc, 'var(--warm)'],
    ['local + global, evidence zeroed', P.zero, 'var(--warm)'], ['local + global, evidence flipped', P.flip, 'var(--warm)'],
  ];
  function drawP() {
    svgP.selectAll('*').remove();
    const W = Math.max(280, svgP.node().getBoundingClientRect().width || 500);
    const narrow = W < 460;
    const rowH = narrow ? 40 : 26, H = rows.reduce((s, r) => s + (r[1] === null ? 26 : rowH), 10) + 16;
    svgP.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const valW = 58, x0 = narrow ? 8 : W * 0.5, x1 = W - valW;
    const x = d3.scaleLinear().domain([0, 1]).range([x0, x1]);
    let yy = 8, firstBar = null, lastBar = 0;
    const barYs = [];
    rows.forEach(([name, v, col]) => {
      if (v === null) { svgP.append('text').attr('x', 0).attr('y', yy + 15).attr('class', 'muted-t').style('font-weight', 650).text(name); yy += 26; return; }
      svgP.append('text').attr('x', 6).attr('y', narrow ? yy + 12 : yy + 13).attr('class', 'lab-ink').style('font-size', '13px').text(name);
      const by = narrow ? yy + 18 : yy + 2;
      svgP.append('rect').attr('x', x0).attr('y', by).attr('width', x1 - x0).attr('height', 14).attr('rx', 3).style('fill', 'var(--track)');
      if (v > 0) svgP.append('rect').attr('x', x0).attr('y', by).attr('width', x(v) - x0).attr('height', 14).attr('rx', 3).style('fill', col)
        .call(explain, `<b>${name}</b><br>accuracy ${v.toFixed(4)}, mean of 6 seeds`);
      svgP.append('text').attr('x', x1 + 8).attr('y', by + 11).attr('class', 'lab-strong num').text(v.toFixed(4));
      if (firstBar === null) firstBar = by; lastBar = by + 14; barYs.push(by);
      yy += rowH;
    });
    if (narrow) barYs.forEach((by) => svgP.append('line').attr('x1', x(0.5)).attr('x2', x(0.5)).attr('y1', by - 3).attr('y2', by + 17).style('stroke', 'var(--ink)').style('stroke-width', 1.5));
    else svgP.append('line').attr('x1', x(0.5)).attr('x2', x(0.5)).attr('y1', firstBar - 6).attr('y2', lastBar + 6).style('stroke', 'var(--ink)').style('stroke-dasharray', '2 3').style('stroke-width', 1.2);
    svgP.append('text').attr('x', x(0.5)).attr('y', lastBar + 18).attr('text-anchor', 'middle').attr('class', 'muted-t').style('font-size', '12px').text('chance');
  }
  onResize(drawI); onResize(drawP); drawI(); drawP();
}

// ====================================================================== U-Net
function initUnet() {
  const U = D.unet, svg = d3.select('#dumbbell');
  function draw() {
    svg.selectAll('*').remove();
    const W = Math.max(280, svg.node().getBoundingClientRect().width || 500), H = 270;
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
      [[U.unet[i], 'var(--warm)'], [U.pack[i], 'var(--teal)']].forEach(([v, c]) => svg.append('circle').attr('cx', x(v)).attr('cy', yy).attr('r', 6.5).style('fill', c).style('stroke', 'var(--surface)').style('stroke-width', 1.5)
        .call(explain, tipH));
    });
  }
  const svgS = d3.select('#structs');
  function drawS() {
    svgS.selectAll('*').remove();
    const W = Math.max(280, svgS.node().getBoundingClientRect().width || 500), H = 140;
    svgS.attr('viewBox', `0 0 ${W} ${H}`).attr('height', H);
    const m = { l: 18, r: 18 };
    const x = d3.scaleLinear().domain([-0.045, 0.045]).range([m.l, W - m.r]);
    const base = 80;
    [-0.04, -0.02, 0, 0.02, 0.04].forEach((t) => {
      svgS.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', t === 0 ? base - 14 : base - 4).attr('y2', base + 6).style('stroke', t === 0 ? 'var(--ink)' : 'var(--ink-3)').style('stroke-width', t === 0 ? 1.5 : 1);
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
      svgS.append('circle').attr('cx', cx).attr('cy', base + dy).attr('r', 5.5).style('fill', r.d > 0 ? 'var(--teal)' : 'var(--warm)').style('stroke', 'var(--surface)').style('stroke-width', 1.5)
        .call(explain, `<b>${r.name}</b>${r.holm ? ' *' : ''}<br>mean difference ${sgn(r.d, 4)}${r.holm ? '<br>survives Holm correction' : ''}`);
      if (['CETN2', 'NUP153', 'ATP2A2', 'SEC61B'].includes(r.name)) {
        // labels lean away from their neighbors: NUP153 and ATP2A2 to the left, SEC61B to the right
        const lift = r.name === 'SEC61B' ? 38 : 22;
        const anchor = { CETN2: ['middle', 0], NUP153: ['end', 4], ATP2A2: ['end', 4], SEC61B: ['start', -4] }[r.name];
        svgS.append('text').attr('x', cx + anchor[1]).attr('y', base - lift).attr('text-anchor', anchor[0]).attr('class', 'lab-ink').style('font-size', '12px').text(r.name + (r.holm ? '*' : ''));
        if (r.name === 'SEC61B') svgS.append('line').attr('x1', cx).attr('x2', cx).attr('y1', base - lift + 3).attr('y2', base - 8).style('stroke', 'var(--ink-3)');
      }
    });
  }
  onResize(draw); onResize(drawS); draw(); drawS();
}

// ====================================================================== systems
function initSystems() {
  const S = D.systems, svg = d3.select('#sysChart');
  const lab = { 65536: '65k', 131072: '131k', 262144: '262k', 524288: '524k', 1048576: '1M' };
  let sel = S.length - 1;
  const chips = d3.select('#sysChips');
  S.forEach((r, i) => chips.append('button').attr('class', 'chip').attr('aria-pressed', String(i === sel)).text(lab[r.n]).on('click', () => { sel = i; update(); }));
  const kinds = [['dense', 'Dense SDPA', 'var(--warm)'], ['window', 'Window', 'var(--neutral-2)'], ['pack', 'PACK3D', 'var(--teal)']];
  // the paper's table prints dense latency to 0.1 ms with thousands separators, the others to 0.01 ms
  const ms = (k, v) => v.toLocaleString('en-US', { minimumFractionDigits: k === 'dense' ? 1 : 2, maximumFractionDigits: k === 'dense' ? 1 : 2 });
  function draw() {
    svg.selectAll('*').remove();
    const W = Math.max(280, svg.node().getBoundingClientRect().width || 560), H = Math.min(380, Math.max(280, W * 0.72));
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
    kinds.forEach(([k, name, col]) => {
      svg.append('path').datum(S).attr('d', d3.line().x((d) => x(d.n)).y((d) => y(d[k]))).style('fill', 'none').style('stroke', col).style('stroke-width', 2.6);
      S.forEach((d) => svg.append('circle').attr('cx', x(d.n)).attr('cy', y(d[k])).attr('r', d === r ? 6 : 3.5).style('fill', col).style('stroke', 'var(--surface)').style('stroke-width', 1.5)
        .call(explain, `<b>${name}</b> · ${lab[d.n]} tokens<br>${ms(k, d[k])} ms forward + backward`));
      const last = S[S.length - 1];
      const dy = k === 'pack' ? -7 : k === 'window' ? 12 : 4;
      svg.append('text').attr('x', x(last.n) + 12).attr('y', y(last[k]) + dy).attr('class', 'lab-ink').style('font-size', '13px').text(name);
    });
  }
  function panel() {
    const r = S[sel], p = d3.select('#sysPanel'); p.selectAll('*').remove();
    const prem = r.pack / r.window - 1;
    p.append('div').attr('class', 'bignums').html(
      `<div class="bignum"><span class="who">vs dense SDPA</span><span class="v num">${r.speedup.toFixed(2)}×</span><span class="d">faster, forward + backward</span></div>` +
      `<div class="bignum"><span class="who">vs window attention</span><span class="v num">+${(prem * 100).toFixed(0)}%</span><span class="d">latency premium, for a global pathway</span></div>`);
    const tbl = p.append('div').attr('class', 'table-wrap').append('table').attr('class', 'data');
    tableFrom(tbl.node(), [lab[r.n] + ' tokens', 'latency, ms', 'peak, GiB'], [
      ['Dense SDPA', ms('dense', r.dense), r.gb_dense.toFixed(2)],
      ['Window attention', ms('window', r.window), r.gb_window.toFixed(2)],
      ['PACK3D', ms('pack', r.pack), r.gb_pack.toFixed(2)],
    ]);
    p.append('p').attr('class', 'small muted').text(`${r.m.toLocaleString('en-US')} summaries per KV head at this size. Dense SDPA has the smallest peak allocation; PACK3D’s is below window attention’s.`);
  }
  function update() { chips.selectAll('button').attr('aria-pressed', (d, i) => String(i === sel)); draw(); panel(); }
  onResize(draw); update();
}

// ====================================================================== the end: a word built in memory order
// The page closes on its own idea. The word PACK3D is a small packed field: one cube per token, each with a
// coordinate c = (z, y, x) (z up, y into the word, x along it) and a memory position i under the chosen
// storage order. Tokens arrive in memory order, so every order traces its own path through the volume, and
// every path builds the same word. The memory ribbon below fills left to right while the word fills in
// the order's pattern. Point at a cube, or walk the memory with the arrow keys, to read both indices.
function initEnd() {
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
  const rampF = ramp(['#3B2D8F', '#6047BC', '#8D6DD8', '#C0ACF0', '#F5F1FD']);
  const BLACK = lab('#000000'), WHITE = lab('#FFFFFF'), EDGE = '#060A09', MINT = '#5FE0C3';
  // on touch screens there is no pointer to hover and usually no arrow keys: say "tap"
  if (HOVERLESS) $('#endRead').textContent = 'Tap a cube, or slide a finger across the word, to read its two indices.';
  const HINT = $('#endRead').textContent;
  let T = [], n = 0, X = 0, Z = 0, two = null, cur = 'raster';
  let mem = null, order = null, shades = null, ribCol = null, farFirst = null, mirFirst = null;
  let ctx = null, rctx = null, W = 0, H = 0, RW = 0, RH = 0, k = 1, ox = 0, oy = 0, fade = null, lastW = -1;
  let P = RM ? 1 : 0, target = RM ? 1 : 0, trailA = RM ? 0 : 1, raf = 0, last = 0, hovTok = -1, selI = -1, lastCount = -2;

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
    const cap = two ? Infinity : Math.max(300, Math.min(520, window.innerHeight * 0.58));
    k = Math.min((w * 0.97) / bw, cap / bh);
    H = Math.ceil(bh * k);
    wrap.style.aspectRatio = 'auto';
    wrap.style.height = H + 'px';
    ox = (w - bw * k) / 2 - x0 * k; oy = -y0 * k;
    ctx = fitCanvas(canvas, W, H);
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
    // the reflection in the stage floor: the mirrored word, drawn first and faded into the floor
    for (const j of mirFirst) {
      const a = land(mem[j], NP);
      if (a > 0) cube(j, -T[j].z - 1 - (1 - ease(a)) * DROP, 0.24 * Math.min(1, a * 1.6));
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = fade; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'source-over';
    // the word: each token drops into place as its memory position comes up
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
  // the memory head and the last few positions it wrote, as a path through the volume
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
  // a picked token: its cube outlined, and the memory path through its neighbors i - 3 .. i + 3
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
      rctx.fillStyle = land(i, NP) > 0 ? ribCol[i] : 'rgba(238, 243, 241, 0.08)';
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
  function describe(i) {
    if (i < 0) return HINT;
    const t = T[order[i]];
    let s = `i = ${i} holds the token at c = (${t.z}, ${t.y}, ${t.x}).`;
    if (i + 1 < n) { const u = T[order[i + 1]]; s += ` Next in memory, i = ${i + 1}, is Δc = (${fmt(u.z - t.z)}, ${fmt(u.y - t.y)}, ${fmt(u.x - t.x)}) away.`; }
    else s += ' It is the last position in memory.';
    return s;
  }
  // the word is also a slider over memory positions, so assistive tech hears each step
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
      P = target > P ? Math.min(target, P + dt / 3.2) : Math.max(target, P - dt / 0.9);
      busy = true;
    } else if (P >= 1 && trailA > 0) {
      trailA = Math.max(0, trailA - dt / 0.8);
      busy = true;
    }
    render();
    if (busy) raf = requestAnimationFrame(tick); else last = 0;
  }
  const kick = () => { if (!raf) { last = 0; raf = requestAnimationFrame(tick); } };
  function build() {
    if (!ctx) return;
    if (RM) { render(); return; }
    P = 0; target = 1; trailA = 1; lastCount = -2; kick();
  }

  $$('#endChips [data-layout]').forEach((b) => b.addEventListener('click', () => {
    cur = b.dataset.layout;
    $$('#endChips [data-layout]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    if (!T.length) return;                                 // not laid out yet: the first build uses cur
    setOrder(cur);
    if (selI >= 0) readout(selI, true);
    build();
  }));
  const again = $('#endAgain');
  if (RM) again.hidden = true; else again.addEventListener('click', build);

  // pointing: the mouse shows a tip; a finger or pen taps a cube to pick it, or a finger slides across
  const unTip = () => { hideTip(); tip.classList.remove('on-dark'); };
  const tipFor = (j, ev) => { const t = T[j]; showTip(`<b>i = ${mem[j]}</b> · c = (${t.z}, ${t.y}, ${t.x})`, ev); tip.classList.add('on-dark'); };
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
  canvas.addEventListener('pointermove', (ev) => { if (ctx && ev.pointerType === 'mouse') { const [x, y] = local(canvas, ev); point(hit(x, y), ev); } });
  rib.addEventListener('pointermove', (ev) => {
    if (!ctx || ev.pointerType !== 'mouse') return;
    const [x, , w] = local(rib, ev), i = clamp(Math.floor((x / w) * n), 0, n - 1);
    point(land(i, NPnow()) >= 1 ? order[i] : -1, ev);
  });
  const leave = () => { if (hovTok >= 0) { hovTok = -1; render(); readout(selI); } unTip(); };
  canvas.addEventListener('pointerleave', leave);
  rib.addEventListener('pointerleave', leave);
  const pick = (i) => { selI = i; readout(i, true); render(); };
  const onWord = (ev) => { const [x, y] = local(canvas, ev), j = hit(x, y); return j >= 0 ? mem[j] : -1; };
  const onRibbon = (ev) => { const [x, , w] = local(rib, ev), i = clamp(Math.floor((x / w) * n), 0, n - 1); return land(i, NPnow()) >= 1 ? i : -1; };
  // a tap picks on click, not on pointerdown, so a scroll that starts on the word picks nothing
  canvas.addEventListener('click', (ev) => { if (ctx && byFinger(ev)) pick(onWord(ev)); });
  rib.addEventListener('click', (ev) => { if (ctx && byFinger(ev)) pick(onRibbon(ev)); });
  // a finger sliding sideways walks the word or the memory; both leave vertical drags to the page (pan-y)
  canvas.addEventListener('pointermove', (ev) => { if (ctx && ev.pointerType === 'touch') { const i = onWord(ev); if (i >= 0 && i !== selI) pick(i); } });
  rib.addEventListener('pointermove', (ev) => { if (ctx && ev.pointerType === 'touch') { const i = onRibbon(ev); if (i >= 0 && i !== selI) pick(i); } });
  // the keyboard walks the memory: arrows step one position, Home and End jump to either end
  canvas.addEventListener('keydown', (ev) => {
    if (!ctx) return;
    const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[ev.key];
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
  canvas.addEventListener('blur', () => { if (selI >= 0) pick(-1); });

  // the closing line, a word at a time (motion only, once)
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
      if (es.some((e) => e.isIntersecting)) { foot.classList.add('in'); io.disconnect(); }
    }, { threshold: 0.3 });
    io.observe(line);
  }
  // lay out once the end is near; build when the word comes into view, and reset once the reader has
  // moved more than a screen away, so the next arrival builds it again
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
      if (e.intersectionRatio >= 0.4 && target < 1) build();
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
  new ResizeObserver(() => { if (ctx && wrap.clientWidth !== lastW) { layout(); render(); } }).observe(wrap);
}

// ====================================================================== nav, copy
function initNav() {
  const bar = $('#progress'), topbar = $('.topbar'), main = $('main'), sheet = $('.standfirst');
  // the breadcrumb: PACK3D / the chapter you are reading, which opens the contents
  const toc = $('#toc'), btn = $('#tocBtn'), menu = $('#tocMenu'), label = $('#tocLabel');
  const links = $$('a', menu);
  const spots = links.filter((a) => a.hash).map((a) => ({ a, s: $(a.hash), name: a.dataset.short || $('.t', a).textContent }))
    .filter((p) => p.s);
  let cur = -2, openedAt = 0;
  const setCur = (i) => {
    if (i === cur) return;
    const first = cur === -2;
    label.style.setProperty('--dy', (i > cur ? 0.45 : -0.45) + 'em');
    cur = i;
    spots.forEach((p, j) => (j === i ? p.a.setAttribute('aria-current', 'location') : p.a.removeAttribute('aria-current')));
    label.textContent = i < 0 ? 'Contents' : spots[i].name;
    btn.setAttribute('aria-label', i < 0 ? 'Contents' : `Contents, now reading ${spots[i].name}`);
    label.classList.remove('swap');
    if (!first) { void label.offsetWidth; label.classList.add('swap'); }
  };
  const isOpen = () => toc.classList.contains('open');
  const shown = () => links.filter((a) => a.offsetParent);
  // pinned: opened by a click, a tap or the keyboard, so it stays until a choice, a click elsewhere or Escape.
  // Opened by a resting mouse, it closes again when the mouse leaves.
  let pinned = false, hoverT = 0;
  const later = (f, ms) => { clearTimeout(hoverT); hoverT = setTimeout(f, ms); };
  const open = (focus, pin = true) => {
    clearTimeout(hoverT);
    pinned = pinned || pin;
    if (!isOpen()) { toc.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); openedAt = window.scrollY; }
    if (focus) (spots[cur] ? spots[cur].a : shown()[0]).focus({ preventScroll: true });
  };
  const close = (refocus) => {
    clearTimeout(hoverT);
    pinned = false;
    if (!isOpen()) return;
    toc.classList.remove('open'); btn.setAttribute('aria-expanded', 'false');
    if (refocus) btn.focus({ preventScroll: true });
  };
  // a click on a menu the mouse already opened keeps it open, rather than shutting it as the reader arrives
  btn.addEventListener('click', () => (isOpen() && pinned ? close(false) : open(false)));
  // a mouse resting on the chapter opens the contents: a short pause first, so passing over the bar opens
  // nothing, and a short grace after leaving, so the way down to the menu keeps it open
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
  menu.addEventListener('click', (e) => { if (e.target.closest('a')) close(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isOpen()) close(toc.contains(document.activeElement)); });
  document.addEventListener('pointerdown', (e) => { if (!toc.contains(e.target)) close(false); });
  // tabbing out closes it; a click that leaves focus nowhere (Safari does not focus links) does not
  toc.addEventListener('focusout', (e) => { if (e.relatedTarget && !toc.contains(e.relatedTarget)) close(false); });

  const onScroll = () => {
    const h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    const mb = main.getBoundingClientRect().bottom;
    const onStage = !!sheet && sheet.getBoundingClientRect().top > topbar.offsetHeight;   // the opening is under the bar
    topbar.classList.toggle('on-end', mb < topbar.offsetHeight);
    topbar.classList.toggle('on-stage', onStage);
    topbar.classList.toggle('at-start', window.scrollY < 4);
    h.classList.toggle('at-end', mb < window.innerHeight);         // overscroll past the end shows the stage
    h.classList.toggle('at-top', onStage);                         // and so does overscroll above the opening
    h.classList.toggle('stage-top', onStage || mb < topbar.offsetHeight);
    bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
    let i = -1;
    spots.forEach((p, j) => { if (p.s.getBoundingClientRect().top < window.innerHeight * 0.35) i = j; });
    setCur(i);
    if (isOpen() && Math.abs(window.scrollY - openedAt) > 120) close(false);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  $('#copyBib').addEventListener('click', async () => {
    const txt = $('#bibtex').textContent;
    try { await navigator.clipboard.writeText(txt); $('#copyNote').textContent = 'Copied.'; }
    catch (e) {
      const r = document.createRange(); r.selectNodeContents($('#bibtex'));
      const s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      $('#copyNote').textContent = 'Selected. Press Ctrl+C or Cmd+C to copy.';
    }
  });
}

// ====================================================================== boot
const parts = [initNav, initPaths, initReadings, initLab, initRope, initPool, initTour, initContract, initSlope, initRepackStage, initNamed, initMSD, initBranch, initUnet, initSystems, initEnd];
// each part starts in its own task, the bar and the opening first, so the page can paint between them and no single task runs long
const boot = () => {
  let i = 0;
  const next = () => {
    const f = parts[i++];
    if (!f) return;
    try { f(); } catch (e) { console.error(f.name, e); }
    setTimeout(next, 0);
  };
  next();
};
// d3 is loaded deferred on the self-hosted page: wait for it there, start at once where it is already in
if (typeof d3 === 'undefined' && document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
else boot();
})();
