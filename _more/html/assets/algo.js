/* ===== 演算法互動教材 · 共用工具 (AG) =====
   純 vanilla JS，無依賴，可從 file:// 直接開啟。
   包含：DOM 輔助、步驟播放器 Player、長條圖 bars、成長曲線圖 lineChart。
*/
'use strict';
const AG = (() => {

  const $  = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

  function el(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    for (const k in attrs) {
      if (k === 'class') e.className = attrs[k];
      else if (k === 'style') e.style.cssText = attrs[k];
      else if (k === 'html') e.innerHTML = attrs[k];
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    }
    for (const c of kids) {
      if (c == null) continue;
      e.append(c.nodeType ? c : document.createTextNode(c));
    }
    return e;
  }

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  function randArr(n, max) {
    const a = [];
    for (let i = 0; i < n; i++) a.push(1 + Math.floor(Math.random() * max));
    return a;
  }

  function fmt(x) {
    if (!isFinite(x)) return '∞';
    if (x === 0) return '0';
    if (x < 0) return '-' + fmt(-x);
    if (x < 1000) return String(Math.round(x * 100) / 100);
    const e = Math.floor(Math.log10(x));
    if (e >= 15) return x.toExponential(2).replace('e+', 'e');
    if (x >= 1e9) return (x / 1e9).toFixed(2) + 'G';
    if (x >= 1e6) return (x / 1e6).toFixed(2) + 'M';
    if (x >= 1e4) return (x / 1e3).toFixed(1) + 'K';
    return String(Math.round(x));
  }

  /* ===== 播放器：預先算好 frames，支援播放/暫停/單步/拖曳/加速 ===== */
  class Player {
    constructor(cfg) {
      this.render = cfg.render;                // (frame, idx) => void
      this.row = cfg.row || null;              // 額外的 DOM 行可插入控制列
      this.baseSpeed = cfg.speed ?? 320;       // 1x 時每步毫秒
      this.speedSteps = [['0.5×', 2.1], ['1×', 1], ['2×', .52], ['4×', .26], ['10×', .1]];
      this.frames = [];
      this.sel = cfg.buttonify !== false;      // 控制器是否有「執行/重設」按鈕
      this.idx = 0;
      this.playing = false;
      this.timer = null;
      this.onEnd = cfg.onEnd || (() => {});
      this.onChange = cfg.onChange || (() => {});
      this._cols = cfg.colors || null;
      this.build();
    }
    build() {
      const box = AG.el('div', { class: 'playerbar' });
      this.bPlay = AG.el('button', { onClick: () => this.play(), title: '播放/暫停' }, '▶');
      this.bPrev = AG.el('button', { onClick: () => this.prev(), title: '上一步' }, '⟨');
      this.bNext = AG.el('button', { onClick: () => this.step(), title: '下一步' }, '⟩');
      this.bFirst = AG.el('button', { onClick: () => this.seek(0), title: '回到起點' }, '⏮');
      this.bLast = AG.el('button', { onClick: () => this.end(), title: '跳到最後' }, '⏭');
      this.slider = AG.el('input', { type: 'range', class: 'slider' });
      this.slider.addEventListener('input', () => this.seek(+this.slider.value));
      this.lbl = AG.el('span', { class: 'lbl' }, '—');
      this.spd = AG.el('select');
      for (const [txt, mult] of this.speedSteps) {
        const o = AG.el('option', { value: mult }, txt);
        this.spd.append(o);
      }
      this.spd.value = '1';
      this.boxEl = box;
      box.append(this.bFirst, this.bPrev, this.bPlay, this.bNext, this.bLast, this.slider, this.lbl, this.spd);
      if (this.row) box.append(this.row);
      return box;
    }
    setFrames(frames) {
      this.stop();
      this.frames = frames || [];
      this.idx = 0;
      const max = Math.max(0, this.frames.length - 1);
      this.slider.max = max;
      this.slider.value = 0;
      this.renderFrame();
      this.updateLbl();
    }
    get ok() { return this.frames.length > 0; }
    speedMs() { return this.baseSpeed * (+this.spd.value); }
    renderFrame() {
      const f = this.frames[this.idx];
      this.render(f, this.idx);
      if (this.onChange) this.onChange(f, this.idx);
    }
    updateLbl() {
      const max = this.frames.length - 1;
      this.lbl.textContent = this.frames.length ? `${this.idx} / ${max}` : '—';
    }
    seek(i) {
      if (!this.frames.length) return;
      this.stop();
      this.idx = Math.max(0, Math.min(this.frames.length - 1, i));
      this.slider.value = this.idx;
      this.renderFrame();
      this.updateLbl();
    }
    step()  { this.seek(this.idx + 1); }
    prev()  { this.seek(this.idx - 1); }
    end()   { this.seek(this.frames.length - 1); }
    play() {
      if (this.frames.length < 2) return;
      if (this.playing) { this.pause(); return; }
      if (this.idx >= this.frames.length - 1) this.seek(0);
      this.playing = true;
      this.bPlay.textContent = '⏸';
      this.bPlay.classList.add('playing');
      this.tick();
    }
    pause() {
      this.playing = false;
      clearTimeout(this.timer);
      this.bPlay.textContent = '▶';
      this.bPlay.classList.remove('playing');
    }
    stop() { this.pause(); }
    tick() {
      this.seek(this.idx + 1);
      if (this.idx >= this.frames.length - 1) { this.pause(); this.onEnd(); return; }
      this.timer = setTimeout(() => this.tick(), this.speedMs());
    }
  }

  /* ===== 長條圖：arr 為值陣列，可給高亮色圖 ===== */
  function bars(canvas, arr, opts = {}) {
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.clientWidth || 600;
    const H = canvas.clientHeight || 260;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const rawMax = Math.max(...arr, 1);
    const max = opts.logY ? Math.log10(Math.max(rawMax, 10)) : (opts.max || rawMax);
    const pad = 6, n = arr.length, bw = (W - 2 * pad) / n;
    const valH = v => {
      if (opts.logY) { const l = Math.log10(Math.max(v, 1)); return (l / max) * (H - 26); }
      return (v / max) * (H - 26);
    };
    for (let i = 0; i < n; i++) {
      const v = arr[i];
      const h = valH(v);
      let color = opts.colors && opts.colors[i] ? opts.colors[i] : 'rgba(11,92,173,.78)';
      ctx.fillStyle = color;
      ctx.fillRect(pad + i * bw + bw * .18, H - 12 - h, bw * .64, h);
      if (opts.labels) {
        ctx.fillStyle = '#5b6472';
        ctx.font = '11px ui-monospace,monospace';
        ctx.textAlign = 'center';
        ctx.fillText(opts.labels[i], pad + i * bw + bw / 2, H - 2);
      }
    }
    if (opts.value) {
      ctx.fillStyle = '#3b4655'; ctx.font = '11px ui-monospace,monospace';
      for (let i = 0; i < n; i++) {
        const v = arr[i]; const h = valH(v);
        ctx.textAlign = 'center';
        ctx.fillText(fmt(v), pad + i * bw + bw / 2, H - 18 - h);
      }
    }
    if (opts.baseline !== false) {
      ctx.strokeStyle = '#cbd5e1'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(pad, H - 12); ctx.lineTo(W - pad, H - 12); ctx.stroke();
    }
  }

  /* ===== 成長曲線圖：series=[{name,color,fn}], opts={maxN,logY} ===== */
  const PALETTE = ['#0b5cad', '#d97706', '#0d9488', '#db2777', '#7c3aed', '#dc2626', '#059669', '#ca8a04'];

  function lineChart(canvas, series, opts = {}) {
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.clientWidth || 640;
    const H = canvas.clientHeight || 300;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    const maxN = Math.max(2, opts.maxN || 20);
    const logY = !!opts.logY;
    const L = 52, R = 14, T = 12, B = 28;

    const vals = series.map(s => {
      const pts = [];
      for (let n = 0; n <= maxN; n++) {
        let v;
        try { v = s.fn(n); } catch (e) { v = NaN; }
        if (!isFinite(v)) v = NaN;
        if (logY && v > 0) v = Math.log10(Math.max(v, 1e-12));
        pts.push(v);
      }
      return pts;
    });

    let yLo = logY ? 0 : 0, yHi = 1;
    const flat = vals.flat().filter(isFinite);
    if (flat.length) {
      yHi = Math.max(...flat);
      if (!logY) yHi = yHi * 1.06;
      if (logY) { yLo = Math.min(0, Math.min(...flat)); yHi += 0.3; }
    }

    const mapX = n => L + (n / maxN) * (W - L - R);
    const mapY = v => H - B - ((v - yLo) / (yHi - yLo)) * (H - T - B);

    // 格線 + 軸標籤
    ctx.strokeStyle = '#eef1f6'; ctx.fillStyle = '#8b94a3';
    ctx.font = '10.5px ui-monospace,monospace'; ctx.lineWidth = 1;
    const ticks = 4;
    for (let i = 0; i <= ticks; i++) {
      const v = yLo + (i / ticks) * (yHi - yLo);
      const y = mapY(v);
      ctx.beginPath(); ctx.moveTo(L, y); ctx.lineTo(W - R, y); ctx.stroke();
      ctx.textAlign = 'right';
      const lbl = logY ? '10^' + (Math.round(v * 10) / 10) : fmt(Math.round(v));
      ctx.fillText(lbl, L - 5, y + 3);
    }
    for (let i = 0; i <= maxN; i += (maxN > 40 ? 10 : maxN > 20 ? 5 : 1)) {
      const x = mapX(i);
      ctx.beginPath(); ctx.moveTo(x, T); ctx.lineTo(x, H - B); ctx.stroke();
      ctx.textAlign = 'center'; ctx.fillText(String(i), x, H - B + 14);
    }
    ctx.fillStyle = '#8b94a3'; ctx.textAlign = 'left';
    ctx.fillText('n →', W - 30, H - B + 14);

    // 曲線
    series.forEach((s, si) => {
      const pts = vals[si];
      ctx.strokeStyle = s.color || PALETTE[si % PALETTE.length];
      ctx.lineWidth = 2;
      ctx.beginPath();
      let started = false;
      for (let n = 0; n <= maxN; n++) {
        const v = pts[n];
        if (!isFinite(v)) { started = false; continue; }
        const x = mapX(n), y = mapY(v);
        if (!started) { ctx.moveTo(x, y); started = true; }
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    });

    // 儲存資料供 hover 使用
    canvas._AG_data = { series, vals, maxN, mapX, mapY, logY, yLo, yHi, H };
  }

  function chartHover(canvas, outEl) {
    canvas.addEventListener('mousemove', e => {
      const d = canvas._AG_data;
      if (!d) return;
      const r = canvas.getBoundingClientRect();
      const x = e.clientX - r.left;
      const n = Math.round((x - 52) / (canvas.clientWidth - 52 - 14) * d.maxN);
      if (n < 0 || n > d.maxN) { outEl.textContent = ''; return; }
      const parts = d.series.map((s, i) => {
        const v = d.vals[i][n];
        const real = d.logY && isFinite(v) ? Math.pow(10, v) : v;
        return `<i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${s.color};margin-right:4px"></i>${s.name} = ${isFinite(real) ? fmt(real) : '∞'}`;
      });
      outEl.innerHTML = `<b>n=${n}</b>　` + parts.join('　');
    });
    canvas.addEventListener('mouseleave', () => { if (outEl) outEl.textContent = ''; });
  }

  return { $, $$, el, sleep, randArr, fmt, PALETTE, Player, bars, lineChart, chartHover };
})();