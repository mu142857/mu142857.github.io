// Headless-Chrome screenshot of next.html (adapted from 好结局/游戏/tools/截图.mjs).
// The desktop app's preview pane never fires requestAnimationFrame, so the page cannot be
// looked at there; a headless Chrome draws normally. Also prints page errors and the frame
// rate.
//
//   node tools/shot.mjs <out.png> [query] [--size=1280x720] [--wait=1500] [--dpr=1]
//                       [--js=<code run in the page>] [--buf=<480x270 buffer.png>]
//                       [--page=next.html] [--port=5173] [--after=<ms to wait after --js>]
//   node tools/shot.mjs /tmp/a.png 'x=1200&mix=0.7' --buf=/tmp/a_buf.png
//
// --js runs inside an async function; whatever it returns is printed. --buf saves the
// 480x270 buffer before upscaling (G.png()), for pixel-exact comparison with the art.
// It talks to a server on localhost (the `dev` preview server on 5173, or any static server
// started from the repo root: `python3 -m http.server 5180` then --port=5180).
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';

const args = process.argv.slice(2);
const flag = (k, d) => { const f = args.find((a) => a.startsWith(`--${k}=`)); return f ? f.slice(k.length + 3) : d; };
const [out, query = ''] = args.filter((a) => !a.startsWith('--'));
const [W, H] = flag('size', '1280x720').split('x').map(Number);
const waitMs = +flag('wait', '1500');
const afterMs = +flag('after', '300');
const js = flag('js', '');
const dpr = +flag('dpr', '1');
const bufOut = flag('buf', '');
const origin = `http://localhost:${flag('port', '5173')}`;
let pagePath = `/${flag('page', 'next.html')}`;
// `npx serve` (the dev preview server) answers next.html with a redirect to /next and DROPS
// the query string on the way, so follow that redirect here and put the query back.
try {
  const r = await fetch(origin + pagePath, { redirect: 'manual' });
  const loc = r.headers.get('location');
  if (r.status >= 300 && r.status < 400 && loc) pagePath = new URL(loc, origin).pathname;
} catch (e) { console.log(`no server on ${origin} — start one from the repo root`); process.exit(2); }
const url = origin + pagePath + (query ? '?' + query : '');

const port = 9400 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(process.env.TMPDIR || tmpdir(), 'site-shot-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--no-first-run', '--no-default-browser-check',
  '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--hide-scrollbars',
  `--window-size=${W},${H}`, 'about:blank'], { stdio: 'ignore' });
// Delete this run's temporary Chrome profile on the way out (about 150 MB each; left behind
// they pile up fast). Covers a normal finish, a timeout's process.exit, Ctrl-C and a kill.
const cleanTmp = () => {
  try { chrome.kill('SIGKILL'); } catch (e) { /* already gone */ }
  try { rmSync(prof, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 }); } catch (e) { /* best effort */ }
};
process.on('exit', cleanTmp);
for (const s of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(s, () => process.exit(130));
setTimeout(() => { console.log('timed out'); process.exit(2); }, 60000).unref();

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
let id = 0;
const pending = new Map();
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const save = (p, b64) => { const f = resolve(process.cwd(), p); mkdirSync(dirname(f), { recursive: true }); writeFileSync(f, Buffer.from(b64, 'base64')); return f; };
const evaluate = (expression, awaitPromise = false) => send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });

try {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    await sleep(200);
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page'); } catch (e) { /* not up yet */ }
  }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => { ws.onopen = r; });
  const errors = [];
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && pending.has(d.id)) { pending.get(d.id)(d.result); pending.delete(d.id); }
    if (d.method === 'Runtime.exceptionThrown') errors.push(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text);
    if (d.method === 'Runtime.consoleAPICalled' && (d.params.type === 'error' || d.params.type === 'warning')) {
      errors.push(`[console.${d.params.type}] ` + d.params.args.map((a) => a.value || a.description).join(' '));
    }
  };
  await send('Runtime.enable');
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: dpr, mobile: false });
  await send('Page.navigate', { url });
  // Wait for the page to say it is up (window.READY), then the requested settle time.
  for (let i = 0; i < 60; i++) {
    await sleep(150);
    if ((await evaluate('!!window.READY')).result.value) break;
  }
  await sleep(waitMs);
  if (!(await evaluate('!!window.READY')).result.value) {
    errors.push('page did not come up (window.READY is not true): '
      + (await evaluate('(document.getElementById("boot-error") || {}).textContent || ""')).result.value);
  }
  if (js) {
    const r = await evaluate(`(async () => { ${js} })()`, true);
    if (!r) errors.push('--js lost its page (did it navigate or reload?)');
    else if (r.exceptionDetails) errors.push(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    else if (r.result && r.result.value !== undefined) console.log(typeof r.result.value === 'string' ? r.result.value : JSON.stringify(r.result.value, null, 1));
    await sleep(afterMs);
  }
  if (out) { const shot = await send('Page.captureScreenshot', { format: 'png' }); console.log('shot', save(out, shot.data)); }
  if (bufOut) { const b = await evaluate('G.png()'); console.log('buffer', save(bufOut, b.result.value.split(',')[1])); }
  // Timing last: it steps the world, so it must not run before the picture is taken.
  const fps = await evaluate('new Promise(r => { let n = 0; const t0 = performance.now(); (function f() { n++; if (performance.now() - t0 < 1000) requestAnimationFrame(f); else r(Math.round(n / ((performance.now() - t0) / 1000))); })(); })', true);
  const cost = await evaluate('(() => { if (!window.G) return -1; const t0 = performance.now(); for (let i = 0; i < 60; i++) { G.clock.step(1 / 60); G.clock.draw(); } return +((performance.now() - t0) / 60).toFixed(2); })()');
  console.log('FPS', fps.result.value, ' one frame (logic + draw)', cost.result.value, 'ms');
  if (errors.length) { console.log('page errors:\n' + errors.join('\n')); process.exitCode = 1; }
} finally {
  try { ws && ws.close(); } catch (e) { /* closed */ }
  chrome.kill();
}
