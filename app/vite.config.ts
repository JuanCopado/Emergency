import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { BRAND } from './src/config/brand';
import { auditBuild, productionDependencyGuard } from './scripts/build-dependency-guard.mjs';

export default defineConfig(({ mode }) => ({
  build: { sourcemap: auditBuild ? 'hidden' : false },
  server: {
    // Unit fidelity checks read the canonical Markdown without exposing it in dev mode.
    ...(mode === 'test' ? { fs: { allow: [
      '.',
      '../clinical/modules',
    ] } } : {}),
    proxy: {
      '/api/clinical-note': 'http://127.0.0.1:8765',
      '/api/pediatric-outpatient': 'http://127.0.0.1:8765',
      '/api/clinical-scores': 'http://127.0.0.1:8765',
      '/api/acute-medications': 'http://127.0.0.1:8765',
    },
  },
  plugins: [
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
    VitePWA({
      registerType: 'autoUpdate',
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
        sourcemap: auditBuild,
        globPatterns: ['**/*.{js,css,html,svg,png,json,woff2}'],
        navigateFallback: '/index.html',
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
      include: ['src/**/*.{ts,tsx}', 'scripts/**/*.{mjs,cjs}', 'vite.config.ts'],
      exclude: ['src/test/**', '**/*.test.*', 'scripts/check-*.mjs', 'scripts/**/*.node-test.mjs'],
    },
  },
}));
