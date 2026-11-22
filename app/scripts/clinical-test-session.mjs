// Synthetic browser harnesses use the same private proxy credential as the launcher.
import { randomBytes } from 'node:crypto';
import { clinicalApiProxy } from './clinical-api-boundary.mjs';

export function clinicalTestSession(uiPort) {
  if (!Number.isInteger(uiPort) || uiPort < 1024 || uiPort > 65535) throw new Error('Invalid clinical test UI port');
  const token = randomBytes(32).toString('hex');
  // Vite loads its Node configuration after this function. No VITE_* variable is used.
  process.env.EMERGENCY_LOCAL_API_TOKEN = token;
  return {
    environment: { ...process.env, EMERGENCY_LOCAL_API_TOKEN: token },
    python: `import os; from clinical_note_api import make_server; s=make_server(ui_port=${uiPort}, session_token=os.environ['EMERGENCY_LOCAL_API_TOKEN']); print(s.server_port,flush=True); s.serve_forever()`,
    proxy: port => clinicalApiProxy(`http://127.0.0.1:${port}`, token),
    headers: { Origin: `http://127.0.0.1:${uiPort}` },
  };
}
