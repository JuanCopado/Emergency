import { defineConfig } from 'vitest/config';
import type { ViteDevServer } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { BRAND } from './src/config/brand';
import { auditBuild, productionDependencyGuard } from './scripts/build-dependency-guard.mjs';
import { clinicalApiBoundary, clinicalApiProxy } from './scripts/clinical-api-boundary.mjs';
import { readBuildIdentity } from './scripts/build-identity.mjs';
import { fileURLToPath } from 'node:url';

// Build-time target of the '@r51-entry-override' import in ClinicalNote.tsx: a null stub unless a non-production experiment opts in.
const entryOverride = process.env.VITE_LAB_LAYER7 === '1'
  ? fileURLToPath(new URL('./lab-entry/LabModalityEntry.tsx', import.meta.url))
  : fileURLToPath(new URL('./src/clinical-note/noEntryOverride.tsx', import.meta.url));

const sourceIdentity = readBuildIdentity(fileURLToPath(new URL('..', import.meta.url)));
const individualInstallation = process.env.EMERGENCY_INDIVIDUAL_BUILD === '1';
if (individualInstallation && process.env.VITE_CLINICAL_NOTE_API_BASE) {
  throw new Error('Individual installation requires its same-origin local API');
}
if (individualInstallation && (process.env.VITE_LAB_LAYER7 === '1' || process.env.EMERGENCY_LOCAL_REVIEW === '1')) {
  throw new Error('Individual installation cannot include laboratory entry points');
}

const loopbackHost = '127.0.0.1';
const localPeers = new Set([loopbackHost, `::ffff:${loopbackHost}`, '::1']);
const localReview = process.env.EMERGENCY_LOCAL_REVIEW === '1';
const reviewPort = Number(process.env.EMERGENCY_LOCAL_REVIEW_PORT ?? '5173');
if (localReview && (!Number.isInteger(reviewPort) || reviewPort < 1024 || reviewPort > 65535)) {
  throw new Error('Invalid local review port');
}

export default defineConfig(({ mode }) => ({
  resolve: { alias: { '@r51-entry-override': entryOverride } },
  define: {
    'import.meta.env.VITE_BUILD_REVISION': JSON.stringify(sourceIdentity.revision),
    'import.meta.env.VITE_BUILD_DIRTY': JSON.stringify(String(sourceIdentity.dirty)),
    'import.meta.env.VITE_INDIVIDUAL_INSTALLATION': JSON.stringify(individualInstallation ? '1' : '0'),
  },
  build: { sourcemap: auditBuild ? 'hidden' : false },
  server: {
    ...(localReview ? {
      host: loopbackHost,
      port: reviewPort,
      strictPort: true,
      headers: {
        'Cache-Control': 'no-store',
        'Referrer-Policy': 'no-referrer',
        'X-Content-Type-Options': 'nosniff',
        // Vite uses inline refresh/style scripts and its own loopback websocket.
        // This bounds requests from the application; it is not OS isolation.
        'Content-Security-Policy': `default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self' ws://127.0.0.1:${reviewPort}; manifest-src 'self'; worker-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'`,
      },
    } : {}),
    // Unit fidelity checks read the canonical Markdown without exposing it in dev mode.
    ...(mode === 'test' ? { fs: { allow: [
      '.',
      '../clinical/modules',
    ] } } : {}),
    proxy: {
      '/api/clinical-note': clinicalApiProxy(),
      '/api/pediatric-outpatient': clinicalApiProxy(),
      '/api/clinical-scores': clinicalApiProxy(),
      '/api/acute-medications': clinicalApiProxy(),
      ...(localReview ? { '/api/blood-gas': {
        target: 'http://127.0.0.1:8767',
        changeOrigin: true,
      },
      '/api/t06-lab': {
        target: 'http://127.0.0.1:8766',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/t06-lab/, '/api'),
      } } : {}),
    },
  },
  plugins: [
    {
      name: 'individual-installation-marker',
      transformIndexHtml: () => individualInstallation ? [{
        tag: 'meta', attrs: { name: 'emergency-individual-installation', content: 'enabled' }, injectTo: 'head' as const,
      }] : [],
    },
    clinicalApiBoundary(),
    productionDependencyGuard(),
    react(),
    {
      name: 'brand-html',
      transformIndexHtml: (html) =>
        html
          .replace(/%BRAND_NAME%/g, BRAND.name)
          .replace(/%BRAND_DESCRIPTION%/g, BRAND.description)
          .replace(/%THEME_COLOR%/g, BRAND.themeColor),
    },
    ...(localReview ? [{
      name: 'local-review-session',
      configureServer(server: ViteDevServer) {
        server.middlewares.use((request, response, next) => {
          if (request.headers.host !== `${loopbackHost}:${reviewPort}` ||
              !localPeers.has(request.socket.remoteAddress ?? '')) {
            response.writeHead(403, { 'Content-Type': 'text/plain', 'Cache-Control': 'no-store' });
            response.end('Local review requires its exact loopback origin.');
            return;
          }
          next();
        });
      },
      transformIndexHtml: () => [{
        tag: 'meta', attrs: { name: 'emergency-local-review', content: 'synthetic-only' }, injectTo: 'head' as const,
      }, {
        tag: 'meta', attrs: { name: 'emergency-local-platform', content: process.platform }, injectTo: 'head' as const,
      }],
    }] : []),
    VitePWA({
      registerType: individualInstallation ? 'prompt' : 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: BRAND.name,
        short_name: BRAND.shortName,
        description: BRAND.description,
        lang: 'es',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        orientation: 'any',
        theme_color: BRAND.themeColor,
        background_color: BRAND.backgroundColor,
        categories: ['medical', 'health', 'utilities'],
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'maskable-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
          { src: 'favicon.svg', sizes: 'any', type: 'image/svg+xml' },
        ],
      },
      workbox: {
        // Initial installation controls its matching page. Later versions wait for per-tab user consent.
        clientsClaim: true,
        skipWaiting: !individualInstallation,
        sourcemap: auditBuild,
        globPatterns: ['**/*.{js,css,html,svg,png,json,woff2}'],
        navigateFallback: '/index.html',
        // A navigation to an API path must fail or reach the server; it must never be answered with the app shell.
        navigateFallbackDenylist: [individualInstallation ? /^\/api(?:\/|$)/ : /^\/api\//, ...(individualInstallation ? [/^\/__local_release__(?:$|\?)/] : [])],
      },
    }),
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', ['lcov', { projectRoot: '..' }], 'json-summary'],
      include: ['src/**/*.{ts,tsx}', 'lab-entry/**/*.{ts,tsx}', 'scripts/**/*.{mjs,cjs}', 'vite.config.ts'],
      exclude: ['src/test/**', '**/*.test.*', 'scripts/check-*.mjs', 'scripts/**/*.node-test.mjs'],
    },
  },
}));
