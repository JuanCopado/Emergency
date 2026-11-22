// The session credential stays in Vite's Node process. Never expose it with VITE_*.
const peers = new Set(['127.0.0.1', '::1', '::ffff:127.0.0.1']);
const prefixes = ['/api/clinical-note', '/api/pediatric-outpatient', '/api/clinical-scores', '/api/acute-medications'];
const tokenHeader = 'x-emergency-local-token';

function headerValues(request, name) {
  const values = [];
  for (let i = 0; i < request.rawHeaders.length; i += 2) {
    if (request.rawHeaders[i].toLowerCase() === name) values.push(request.rawHeaders[i + 1]);
  }
  return values;
}

export function clinicalApiBoundary(sessionToken = process.env.EMERGENCY_LOCAL_API_TOKEN) {
  const configured = typeof sessionToken === 'string' && /^[a-f0-9]{64}$/.test(sessionToken);
  function install(server) {
    server.middlewares.use((request, response, next) => {
      const path = (request.url ?? '').split('?')[0];
      // Match Vite's string-prefix proxy selection, including unknown suffixes.
      if (!prefixes.some(prefix => path.startsWith(prefix))) return next();
      const port = server.httpServer?.address()?.port;
      const hosts = new Set([`127.0.0.1:${port}`, `localhost:${port}`]);
      const origins = new Set([...hosts].map(host => `http://${host}`));
      const host = headerValues(request, 'host');
      const origin = headerValues(request, 'origin');
      const site = headerValues(request, 'sec-fetch-site');
      const reading = request.method === 'GET' || request.method === 'HEAD';
      const trusted = port && peers.has(request.socket.remoteAddress) && host.length === 1 && hosts.has(host[0]) &&
        origin.length <= 1 && (origin.length ? origins.has(origin[0]) : reading) &&
        site.length <= 1 && (!site.length || ['same-origin', 'same-site', 'none'].includes(site[0].trim().toLowerCase()));
      if (!trusted || !configured) {
        response.writeHead(trusted ? 503 : 403, {
          'Content-Type': 'application/json', 'Cache-Control': 'no-store',
          'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
        });
        response.end(JSON.stringify({ error: trusted ? 'Local API session is not configured.' : 'Local request origin is not permitted.' }));
        return;
      }
      // Ignore credentials submitted by a browser; only the verified proxy supplies its secret.
      delete request.headers[tokenHeader];
      next();
    });
  }
  return { name: 'clinical-api-boundary', configureServer: install, configurePreviewServer: install };
}

export function clinicalApiProxy(target = 'http://127.0.0.1:8765', sessionToken = process.env.EMERGENCY_LOCAL_API_TOKEN) {
  const url = new URL(target);
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || url.pathname !== '/' || url.search || url.hash || url.username || url.password) {
    throw new Error('Clinical API proxy target must be a direct IPv4 loopback origin.');
  }
  return {
    target: url.origin,
    changeOrigin: true,
    configure(proxy) {
      proxy.on('proxyReq', proxyRequest => {
        proxyRequest.removeHeader(tokenHeader);
        if (typeof sessionToken === 'string' && /^[a-f0-9]{64}$/.test(sessionToken)) {
          proxyRequest.setHeader(tokenHeader, sessionToken);
        }
      });
    },
  };
}
