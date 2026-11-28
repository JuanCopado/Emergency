import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { registerSW } from 'virtual:pwa-register';
import './i18n';
import './index.css';
import App from './App';
import { SettingsProvider } from './state/settings';
import { configureLocalUpdater, localWorkerNeedsReload, markLocalUpdateAvailable } from './lib/localUpdate';

const localReview = document.querySelector('meta[name="blood-gas-local"], meta[name="emergency-local-review"]');
if (!localReview) {
  if (import.meta.env.VITE_INDIVIDUAL_INSTALLATION === '1') {
    const update = registerSW({
      immediate: true,
      onNeedRefresh: markLocalUpdateAvailable,
      onNeedReload: localWorkerNeedsReload,
      onRegisteredSW(_url, registration) {
        if (!registration) return;
        const check = () => { void registration.update().catch(() => { /* Offline retains this version. */ }); };
        window.addEventListener('online', check);
        window.addEventListener('focus', check);
        window.setInterval(check, 30_000);
      },
    });
    configureLocalUpdater(update);
  } else registerSW({ immediate: true });
}

createRoot(document.getElementById('root') as HTMLElement).render(
  <StrictMode>
    <BrowserRouter>
      <SettingsProvider>
        <App />
      </SettingsProvider>
    </BrowserRouter>
  </StrictMode>,
);
