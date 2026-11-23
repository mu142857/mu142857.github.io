// The section text (About, Skills, Projects, …) is written once, in index.html's
// <template id="section-*"> blocks. v1.html — the first interactive site, kept beside the
// current one — borrows it from there: this fetches index.html and adopts every section
// template the page does not already have (v1.html keeps its own Settings template), then
// runs the same language and follower-count passes index.html runs.
import { applyTranslations } from './i18n.js';
import { applyBiliStats } from './bili-stats.js';

export async function adoptTemplates(from = 'index.html') {
  const res = await fetch(from, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`Could not load ${from} for the section templates`);
  const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
  let n = 0;
  for (const src of doc.querySelectorAll('template[id^="section-"]')) {
    if (document.getElementById(src.id)) continue;
    const tpl = document.createElement('template');
    tpl.id = src.id;
    tpl.innerHTML = src.innerHTML;
    document.body.appendChild(tpl);
    n++;
  }
  applyTranslations();
  applyBiliStats(); // patches the templates in place when data/bilibili.json arrives
  return n;
}
