import { BRAND } from '../config/brand';

/** Original mark: rounded tile, cross, ECG trace. Colours come from BRAND. */
export function LogoMark({ size = 32, className = '' }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className={className} aria-hidden="true" focusable="false">
      <rect width="64" height="64" rx="14" fill={BRAND.themeColor} />
      <path d="M26 12h12v14h14v12H38v14H26V38H12V26h14z" fill={BRAND.accentColor} />
      <path d="M14 32h9l3-6 5 13 4-10 2 3h13" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
