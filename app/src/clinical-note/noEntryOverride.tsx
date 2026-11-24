import type { ComponentType } from 'react';

/** Props shared by every modality entry (the product ModalityEntry and any build-time override). */
export type ModalityEntryProps = {
  busy: boolean;
  language: string;
  ui: (key: string, values?: Record<string, string | number>) => string;
  onConfirm: (file: File, kind: string | null) => void;
};

/** Default target of the '@r51-entry-override' alias: no override. Renders nothing and is never mounted (see ClinicalNote.tsx). */
const NoEntryOverride: ComponentType<ModalityEntryProps> = () => null;
export default NoEntryOverride;
