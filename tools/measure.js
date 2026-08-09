/* Geometry check for the README plates.
 *
 * The plates are emitted by python that positions every glyph by arithmetic on
 * an assumed character width. That assumption is wrong often enough that the
 * first hero draft ran its own name through the divider and out the far side of
 * the column next to it, and nothing in the generator could have noticed.
 *
 * So: render each SVG in a real browser, read the actual bounding box of every
 * text and rect, and fail on the two things arithmetic cannot see -- a mark
 * outside the plate, and two pieces of text overlapping each other.
 *
 *   node tools/measure.js hero hero-dark lab run stats
 *
 * Serve the repo root on 127.0.0.1:8020 first; the browser needs a real origin
 * for the SVG to lay out the way GitHub will lay it out.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const PORT = process.env.PLATE_PORT || 8020;

(async () => {
  const names = process.argv.slice(2);
  if (!names.length) { console.error('usage: node tools/measure.js <plate>...'); process.exit(2); }

  const b = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--force-device-scale-factor=1'] });

  let bad = 0;
  for (const name of names) {
    const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
    await p.goto(`http://127.0.0.1:${PORT}/assets/${name}.svg`, { waitUntil: 'load' });
    // Let the reveal animations settle; a box read mid-transform is not the box.
    await p.waitForTimeout(1800);

    const r = await p.evaluate(() => {
      const svg = document.querySelector('svg');
      const vb = svg.viewBox.baseVal;
      const texts = [...svg.querySelectorAll('text')].map(t => {
        // getBBox is in the element's own user space. Anything inside a
        // translated <g> -- which is how the run plate places both of its
        // panels -- reports a box relative to that group, so two panels sitting
        // side by side both claimed to start at x=0 and every label read as
        // overlapping its opposite number. getCTM maps it up to the root
        // viewport, which is the space the plate is actually laid out in.
        const bb = t.getBBox();
        const m = t.getCTM();
        const xs = [], ys = [];
        for (const [px, py] of [[bb.x, bb.y], [bb.x + bb.width, bb.y],
                                [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]]) {
          xs.push(m.a * px + m.c * py + m.e);
          ys.push(m.b * px + m.d * py + m.f);
        }
        const cs = getComputedStyle(t);
        return { s: (t.textContent || '').trim().slice(0, 34),
                 x: Math.min(...xs), y: Math.min(...ys),
                 w: Math.max(...xs) - Math.min(...xs),
                 h: Math.max(...ys) - Math.min(...ys),
                 size: parseFloat(cs.fontSize), anchor: cs.textAnchor };
      }).filter(t => t.s && t.w > 0);
      return { vw: vb.width, vh: vb.height, texts };
    });

    const issues = [];
    // The plate inset: marks live inside the rounded surface, not on its edge.
    const PAD = 8;
    for (const t of r.texts) {
      if (t.x < PAD || t.x + t.w > r.vw - PAD || t.y < 0 || t.y + t.h > r.vh) {
        issues.push(`outside plate: "${t.s}" at x=${t.x.toFixed(0)}..${(t.x + t.w).toFixed(0)}` +
                    ` y=${t.y.toFixed(0)}..${(t.y + t.h).toFixed(0)} (plate ${r.vw}x${r.vh})`);
      }
    }
    // Overlap, with a small tolerance: glyph boxes include leading, and two
    // lines of a heading legitimately share a pixel or two of it.
    const TOL = 3;
    for (let i = 0; i < r.texts.length; i++) {
      for (let j = i + 1; j < r.texts.length; j++) {
        const a = r.texts[i], c = r.texts[j];
        const ox = Math.min(a.x + a.w, c.x + c.w) - Math.max(a.x, c.x);
        const oy = Math.min(a.y + a.h, c.y + c.h) - Math.max(a.y, c.y);
        // Two lines of one wrapped heading share leading on purpose -- display
        // type wants leading tighter than its glyph box. Same left edge and
        // same size means these are lines of a block, not a collision.
        const sameBlock = Math.abs(a.x - c.x) < 2 && Math.abs(a.size - c.size) < 0.5;
        if (sameBlock && oy < Math.min(a.h, c.h) * 0.35) continue;
        if (ox > TOL && oy > TOL) {
          issues.push(`overlap ${ox.toFixed(0)}x${oy.toFixed(0)}px: "${a.s}" / "${c.s}"`);
        }
      }
    }

    console.log(`${name.padEnd(12)} ${r.vw}x${r.vh}  ${r.texts.length} text marks  ` +
                (issues.length ? `${issues.length} PROBLEM(S)` : 'clean'));
    for (const i of issues) console.log('   ' + i);
    bad += issues.length;
    await p.close();
  }

  await b.close();
  process.exit(bad ? 1 : 0);
})();
