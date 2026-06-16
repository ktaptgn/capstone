// C5.1 demo server — serves the dashboard and the PM app from the SAME ORIGIN
// so their real-time PM-order sync (BroadcastChannel + localStorage) works.
//
// Zero dependencies. Requires only Node.js (v16+).
//
//   Dashboard : http://localhost:4173/
//   PM app    : http://localhost:4173/pm
//
// Run:  node server.mjs       (or just double-click start.bat on Windows)

import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { exec } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT ? Number(process.env.PORT) : 4173;

const DASHBOARD_HTML = join(__dirname, 'operator_dashboard.html');
const PM_HTML = join(__dirname, 'pm_worker_app.html');

async function sendFile(res, path) {
  try {
    const html = await readFile(path);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(`Not found: ${path}`);
  }
}

const server = createServer((req, res) => {
  const url = (req.url || '/').split('?')[0];
  if (url === '/pm' || url === '/pm/' || url.startsWith('/pm/')) {
    sendFile(res, PM_HTML);
  } else {
    sendFile(res, DASHBOARD_HTML);
  }
});

server.listen(PORT, () => {
  const base = `http://localhost:${PORT}`;
  console.log('C5.1 demo server running.');
  console.log(`  Dashboard : ${base}/`);
  console.log(`  PM app    : ${base}/pm`);
  console.log('\nOpen both URLs in two tabs/windows of the SAME browser.');
  console.log('Press Ctrl+C to stop.');

  // Best-effort: open both tabs automatically on the host OS.
  if (process.env.NO_OPEN !== '1') {
    const open =
      process.platform === 'win32' ? 'start ""' :
      process.platform === 'darwin' ? 'open' : 'xdg-open';
    exec(`${open} ${base}/`);
    setTimeout(() => exec(`${open} ${base}/pm`), 600);
  }
});
