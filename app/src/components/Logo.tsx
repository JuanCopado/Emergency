import { BRAND } from '../config/brand';

/** Original mark: rounded tile, three note lines (E) and an alert dot. Colours come from BRAND. */
export function LogoMark({ size = 32, className = '' }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className={className} aria-hidden="true" focusable="false">
      <rect width="64" height="64" rx="16" fill={BRAND.themeColor} />
      <rect x="16" y="14" width="30" height="8" rx="4" fill="#fff" />
      <rect x="16" y="28" width="22" height="8" rx="4" fill="#fff" />
      <rect x="16" y="42" width="30" height="8" rx="4" fill="#fff" />
      <circle cx="50" cy="32" r="5" fill={BRAND.accentColor} />
    </svg>
  );
}
