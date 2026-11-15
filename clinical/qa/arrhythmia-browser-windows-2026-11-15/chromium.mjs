import { existsSync } from 'node:fs';

/** Locate a preinstalled Chromium (no download). Override with CHROMIUM_PATH. */
export function chromiumPath() {
  const candidates = [
    process.env.CHROMIUM_PATH,
    '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/opt/pw-browsers/chromium/chrome-linux/chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome',
  ].filter(Boolean);
  const found = candidates.find((p) => existsSync(p));
  if (!found) throw new Error('Chromium not found; set CHROMIUM_PATH');
  return found;
}
