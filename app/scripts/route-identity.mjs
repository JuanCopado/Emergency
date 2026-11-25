import { matchPath } from 'react-router-dom';

// Independent functional expectations, not inferred from whatever happened to render.
// Spanish is selected by the browser harness; dynamic records also need their own UI.
export const ROUTE_CONTRACTS = [
  ['/', '/', '^Apoyo clínico para urgencias y cuidados agudos$', { 'main form[role="search"]': 1 }],
  ['/drugs', '/drugs', '^Fármacos$', { '#drug-search': 1, '[data-testid^="drug-card-"]': 1 }],
  ['/drugs/:id', '/drugs/norepinephrine', '.+', { '#drug-title': 1, '[data-testid="open-calculator"]': 1 }],
  ['/calculator', '/calculator', '^Calculadora de perfusiones$', { '#calc-drug': 1, 'main form': 1 }],
  ['/acute-medications', '/acute-medications', '^Farmacología aguda$', { '[data-testid="acute-group"]': 1 }],
  ['/insulin-uci', '/insulin-uci', '^Insulinoterapia UCI$', { 'form[aria-label="Formulario de simulación"]': 1 }],
  ['/scores', '/scores', '^Scores clínicos$', { 'main form [data-field]': 1, 'main select': 1 }],
  ['/pediatrics', '/pediatrics', '^Pediatría ambulatoria$', { 'main select': 2 }],
  ['/procedures', '/procedures', '^Procedimientos$', { 'main input[type="search"]': 1, 'main a[href^="/procedures/"]': 1 }],
  ['/procedures/:id', '/procedures/PROC-VASC-007', '.+', { 'nav[aria-label="Secciones del procedimiento"]': 1, 'section[aria-label="STOP"]': 1 }],
  ['/clinical-note', '/clinical-note', '^Apoyo al diagnóstico$', { '[data-testid="clinical-note-workspace"]': 1, 'main input[aria-label="Edad"]': 1 }],
  ['/blood-gas', '/blood-gas', '^Revisión de gasometrías$', { 'main input[aria-label="Documento sintético"]': 1 }],
  ['/t06-lab', '/t06-lab', '^Laboratorio T06 en localhost$', { '.t06-lab #scenario': 1 }],
  ['/clinical', '/clinical', '^Patologías y módulos$', { 'main input[aria-label="Buscar patología o módulo"]': 1 }],
  ['/clinical/:id', '/clinical/sepsis-shock', '.+', { '#related-procedures': 1, 'main a[href^="/guides/"]': 1 }],
  ['/guides', '/guides', '^Pantalla completa · impresión · PDF$', { 'main a[href^="/guides/"]': 1, 'main select': 1 }],
  ['/guides/:id', '/guides/sepsis-shock', '.+', { '.clinical-guide-sheet': 1, 'main button': 2 }],
  ['/settings', '/settings', '^Ajustes$', { 'main input[name="lang"]': 4, 'main input[name="theme"]': 3 }],
  ['/about', '/about', '^Acerca de y aviso legal$', { '[data-testid="disclaimer"]': 1 }],
].map(([pattern, example, heading, controls]) => ({ pattern, example, heading, controls }));

const NOT_FOUND = /(?:no encontrad[oa]|not found|não encontrad[oa]|未找到|找不到|404)/i;
const pathname = path => new URL(path, 'https://route-audit.invalid').pathname;

export function contractFor(path) {
  const contract = ROUTE_CONTRACTS.find(c => matchPath({ path: c.pattern, end: true }, pathname(path)));
  if (!contract) throw new Error(`No valid route contract: ${path}`);
  return contract;
}

export function identityProblems(observed, expectedPath) {
  const contract = contractFor(expectedPath);
  const problems = [];
  if (!Number.isInteger(observed.httpStatus) || observed.httpStatus < 200 || observed.httpStatus >= 400) problems.push('HTTP_ERROR');
  if (observed.pathname !== pathname(expectedPath)) problems.push('WRONG_PATH');
  if (!observed.mainVisible) problems.push('MISSING_MAIN');
  if (NOT_FOUND.test(observed.heading || '')) problems.push('NOT_FOUND_PAGE');
  if (!new RegExp(contract.heading).test(observed.heading || '')) problems.push('WRONG_MODULE_HEADING');
  for (const [selector, minimum] of Object.entries(contract.controls)) {
    if (!Number.isInteger(observed.probes?.[selector]) || observed.probes[selector] < minimum) problems.push(`MISSING_MODULE_CONTROL:${selector}`);
  }
  if (observed.overlay) problems.push('FRAMEWORK_ERROR_OVERLAY');
  if (!Array.isArray(observed.errors) || observed.errors.length) problems.push('BROWSER_ERRORS');
  return problems;
}

export function registeredPaths(source) {
  // App.tsx currently has one pathless Layout and flat literal child routes.
  // Fail closed if a future route expression is not covered by this extractor.
  if (/<Route\b[^>]*\bpath=\{/.test(source)) throw new Error('Dynamic router paths require an explicit audit');
  return ['/', ...[...source.matchAll(/<Route\b[^>]*\bpath="([^"]+)"/g)].map(m => m[1]).filter(p => p !== '*').map(p => '/' + p.replace(/^\//, ''))];
}

export function matchesRegisteredRoute(path, patterns) {
  return patterns.some(pattern => pattern !== '*' && matchPath({ path: pattern, end: true }, pathname(path)));
}

export function assertRouteCoverage(patterns) {
  for (const pattern of patterns) {
    if (!ROUTE_CONTRACTS.some(c => c.pattern === pattern)) throw new Error(`Missing functional contract: ${pattern}`);
  }
  for (const contract of ROUTE_CONTRACTS) {
    if (!patterns.includes(contract.pattern)) throw new Error(`Contract has no registered route: ${contract.pattern}`);
  }
}
