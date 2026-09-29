/**
 * Single source of truth for product branding.
 * Change these values to rebrand the app (name, colours used by manifest, etc.).
 */
export const BRAND = {
  name: 'Emergency',
  shortName: 'Emergency',
  /** English tagline (UI tagline is translated via i18n key `brand.tagline`). */
  description: 'Emergency & ICU infusion reference and calculator (draft, pending clinical validation)',
  themeColor: '#0b1220',
  backgroundColor: '#0b1220',
  accentColor: '#e11d48',
  contentVersion: 'v1.35',
  appVersion: '0.1.0',
} as const;
