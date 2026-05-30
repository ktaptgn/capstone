// Zero-dependency static server that serves BOTH single-file UI builds
// from the SAME ORIGIN, so the dashboard <-> PM app real-time sync
// (BroadcastChannel + localStorage) works across browser tabs.
//
// Usage:
//   1) build both apps:
//        (cd operator_dashboard && npm run build)
//        (cd pm_worker_app && npm run build)
//   2) node serve_demo.mjs
//   3) open in two tabs of the SAME browser:
//        Dashboard : http://localhost:4173/
//        PM app    : http://localhost:4173/pm
//
// Decisions (요청/승인/보류/거절) made in one tab appear instantly in the other.

import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT ? Number(process.env.PORT) : 4173;

const DASHBOARD_HTML = join(__dirname, 'operator_dashboard', 'dist', 'index.html');
const PM_HTML = join(__dirname, 'pm_worker_app', 'dist', 'index.html');

async function sendFile(res, path) {
  try {
    const html = await readFile(path);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(
      'Build not found. Run "npm run build" in operator_dashboard and pm_worker_app first.\n' +
        `Missing: ${path}`,
    );
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
  console.log(`C5.1 demo server running on http://localhost:${PORT}`);
  console.log(`  Dashboard : http://localhost:${PORT}/`);
  console.log(`  PM app    : http://localhost:${PORT}/pm`);
});
