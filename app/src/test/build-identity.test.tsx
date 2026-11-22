import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { BuildIdentity } from '../components/BuildIdentity';
import i18n from '../i18n';

afterEach(() => { cleanup(); vi.unstubAllEnvs(); });

it.each([
  ['abcdef1234567890', 'false', 'abcdef123456', false],
  ['abcdef1234567890', 'true', 'abcdef123456', true],
  ['', 'false', 'Identity unavailable', false],
] as const)('shows source identity %s with dirty=%s without guessing missing metadata', async (revision, dirty, text, localChanges) => {
  vi.stubEnv('VITE_BUILD_REVISION', revision);
  vi.stubEnv('VITE_BUILD_DIRTY', dirty);
  await i18n.changeLanguage('en');
  render(<BuildIdentity />);
  expect(screen.getByTestId('build-identity')).toHaveTextContent(text);
  expect(screen.getByTestId('build-identity').textContent?.includes('uncommitted local changes')).toBe(localChanges);
});
