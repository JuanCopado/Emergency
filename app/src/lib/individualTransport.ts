/** Build identity is not a credential; it prevents mixing installed client and backend versions. */
export function localRevisionHeaders(
  mode = import.meta.env.VITE_INDIVIDUAL_INSTALLATION,
  revision = import.meta.env.VITE_BUILD_REVISION,
): Record<string, string> {
  if (mode !== '1') return {};
  return { 'X-Emergency-Revision': String(revision ?? '') };
}
