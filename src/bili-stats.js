// Live bilibili follower count for the progress bar on both pages.
//
// Browsers can't read bilibili directly (no CORS, proxies get 403), so a scheduled GitHub
// Action (.github/workflows/bilibili-stats.yml) fetches the public count server-side and
// commits it to data/bilibili.json. This module reads that file and rewrites every
// `.progress-head` number + `.progress-fill` width it finds — in the live DOM (classic page)
// and inside every <template> (the interactive site clones sections on open).
//
// The numbers written in the HTML stay as the fallback: if the JSON is missing or stale the
// page simply shows them. The goal is parsed from the "/ 100,000" part of the HTML, so it is
// changed there, not here.

const DATA_URL = 'data/bilibili.json';

export async function applyBiliStats(root = document) {
  let follower;
  try {
    const res = await fetch(DATA_URL, { cache: 'no-cache' });
    if (!res.ok) return;
    ({ follower } = await res.json());
  } catch {
    return; // offline, file:// preview, or a broken JSON — keep the static numbers
  }
  if (!(Number.isFinite(follower) && follower > 0)) return;

  const roots = [root, ...Array.from(root.querySelectorAll('template'), (t) => t.content)];
  for (const r of roots) {
    for (const head of r.querySelectorAll('.progress-head')) {
      const span = head.querySelector('span:last-child');
      const m = span && /\/\s*([\d,]+)/.exec(span.textContent);
      if (!m) continue;
      const goal = Number(m[1].replace(/,/g, ''));
      span.textContent = `${follower.toLocaleString('en-US')} / ${goal.toLocaleString('en-US')}`;
      const fill = head.nextElementSibling?.querySelector('.progress-fill');
      if (fill) fill.style.width = `${Math.min(100, (follower / goal) * 100).toFixed(1)}%`;
    }
  }
}
