import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { BRAND } from './src/config/brand';

export default defineConfig({
  server: {
    proxy: {
      '/api/clinical-note': 'http://127.0.0.1:8765',
    },
  },
  plugins: [
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
  },
});
