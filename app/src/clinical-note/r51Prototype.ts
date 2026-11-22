/**
 * R13 · R5-1 safety policy layers 1-6 (DEC-CLIN-R8-06A), INACTIVE prototype.
 *
 * Off unless a development build sets VITE_R51_PROTOTYPE=1; a production build ignores the variable.
 * No network and no clinical rule lives here: it only declares which modality entry points exist,
 * the explicit category each one sends, and that the dermatological reassurance filter belongs to
 * skin_wound alone (the server already behaves like that). Human confirmation never verifies the
 * content of an image.
 */
export type PrototypeModalityId = 'skin_wound' | 'ecg' | 'xray' | 'pocus' | 'document';

export interface ModalityContract {
  readonly id: PrototypeModalityId;
  /** The explicit category sent to the server; never inferred from a filename or from pixels. */
  readonly kind: string;
  readonly labelKey: string;
  /** Fixed, non-generated scope text. The wording per modality is pending medical approval. */
  readonly limitationKey: string;
  readonly accept: string;
  /** True only where the server applies the dermatological reassurance filter. */
  readonly dermatologicFilter: boolean;
}

export const PROVISIONAL_LIMITATION =
  'Modalidade {{modality}}: o ficheiro é enviado ao módulo desta modalidade. O conteúdo não é verificado automaticamente. Texto provisório; redação médica pendente.';

const IMAGES = '.png,.jpg,.jpeg,.webp';

export const MODALITIES: readonly ModalityContract[] = [
  { id: 'skin_wound', kind: 'skin_wound', labelKey: 'Pele/ferida', limitationKey: PROVISIONAL_LIMITATION, accept: IMAGES, dermatologicFilter: true },
  { id: 'ecg', kind: 'ecg', labelKey: 'ECG', limitationKey: PROVISIONAL_LIMITATION, accept: `${IMAGES},.pdf`, dermatologicFilter: false },
  { id: 'xray', kind: 'xray', labelKey: 'Rx', limitationKey: PROVISIONAL_LIMITATION, accept: `${IMAGES},.pdf,.dcm`, dermatologicFilter: false },
  { id: 'pocus', kind: 'pocus', labelKey: 'Ecografia/POCUS', limitationKey: PROVISIONAL_LIMITATION, accept: `${IMAGES},.pdf,.dcm`, dermatologicFilter: false },
  { id: 'document', kind: 'pdf_document', labelKey: 'Documento (PDF ou texto)', limitationKey: PROVISIONAL_LIMITATION, accept: '.pdf,.txt,.csv,.json,.xml', dermatologicFilter: false },
];

/** Fail-closed: only an explicit '1' in a non-production build turns the prototype on. */
export function r51PrototypeEnabled(): boolean {
  return import.meta.env.VITE_R51_PROTOTYPE === '1' && !import.meta.env.PROD;
}

export function modalityContract(id: PrototypeModalityId): ModalityContract {
  const found = MODALITIES.find(m => m.id === id);
  if (!found) throw new Error(`unknown modality ${id}`);
  return found;
}

export function appliesDermatologicFilter(kind: string): boolean {
  return MODALITIES.some(m => m.kind === kind && m.dermatologicFilter);
}
