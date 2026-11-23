/**
 * R13 · R5-1 safety policy layers 1-6 (DEC-CLIN-R8-06A), INACTIVE prototype.
 *
 * Off unless a development build sets VITE_R51_PROTOTYPE=1; a production build ignores the variable.
 * No network and no clinical rule lives here: it only declares which modality entry points exist,
 * the explicit category each one sends, and that the dermatological reassurance filter belongs to
 * skin_wound alone (the server already behaves like that). Human confirmation never verifies the
 * content of an image.
 */
import approvedResource from './r51-limitations.approved.json';

export type PrototypeModalityId = 'skin_wound' | 'ecg' | 'xray' | 'pocus' | 'document';

export interface ModalityContract {
  readonly id: PrototypeModalityId;
  /**
   * The explicit category sent to the server; never inferred from a filename or from pixels.
   * null = send none and let the server infer exactly as it does today. Documents use null so that
   * choosing «Documento» never moves a file to a different clinical circuit than it takes today.
   */
  readonly kind: string | null;
  readonly labelKey: string;
  /** Fixed, non-generated scope text. The wording per modality is pending medical approval. */
  readonly limitationKey: string;
  readonly accept: string;
  /** True only where the server applies the dermatological reassurance filter. */
  readonly dermatologicFilter: boolean;
}

export const PROVISIONAL_LIMITATION =
  'Modalidade {{modality}}: o ficheiro é enviado ao módulo desta modalidade. O conteúdo não é verificado automaticamente. Texto provisório; redação médica pendente.';

/**
 * Fixed limitation text per modality (R16). The texts are deterministic resources approved by the medical
 * owner (DEC-CLIN-R14-01, only for the inactive prototype and human-factors tests); they are never
 * generated and never edited here. An entry replaces the provisional text only when it is APPROVED
 * AND carries the decision id, an approval date and the three language texts; anything else falls
 * back to the provisional text (fail-closed). zh has no approved wording: it shows the English text.
 */
export type LimitationStatus = 'PROVISIONAL' | 'APPROVED';
export type ApprovedLanguage = 'es' | 'pt' | 'en';

export interface LimitationEntry {
  readonly status: LimitationStatus;
  readonly approvedTexts?: Readonly<Record<ApprovedLanguage, string>>;
  readonly approval?: { readonly decision: string; readonly date: string };
}

export type LimitationTable = Readonly<Record<PrototypeModalityId, LimitationEntry>>;

const approvedTexts = (id: PrototypeModalityId): LimitationEntry => ({
  status: 'APPROVED',
  approvedTexts: approvedResource.texts[id],
  approval: { decision: approvedResource.decision, date: approvedResource.approved_on },
});

export const LIMITATION_TEXTS: LimitationTable = {
  skin_wound: /* @__PURE__ */ approvedTexts('skin_wound'),
  ecg: /* @__PURE__ */ approvedTexts('ecg'),
  xray: /* @__PURE__ */ approvedTexts('xray'),
  pocus: /* @__PURE__ */ approvedTexts('pocus'),
  document: /* @__PURE__ */ approvedTexts('document'),
};

function isApproved(entry: LimitationEntry | undefined): entry is LimitationEntry & { approvedTexts: Readonly<Record<ApprovedLanguage, string>> } {
  const t = entry?.approvedTexts;
  return entry?.status === 'APPROVED' && !!t && !!t.es && !!t.pt && !!t.en
    && !!entry.approval?.decision && /^\d{4}-\d{2}-\d{2}$/.test(entry.approval.date);
}

/** The approved text for the language, or null while the modality is still provisional. */
export function approvedLimitationText(id: PrototypeModalityId, language: string, table: LimitationTable = LIMITATION_TEXTS): string | null {
  const entry = table[id];
  if (!isApproved(entry)) return null;
  const lang: ApprovedLanguage = language === 'es' || language === 'pt' ? language : 'en';
  return entry.approvedTexts[lang];
}

export function limitationStatusFor(id: PrototypeModalityId, table: LimitationTable = LIMITATION_TEXTS): LimitationStatus {
  return isApproved(table[id]) ? 'APPROVED' : 'PROVISIONAL';
}

const IMAGES = '.png,.jpg,.jpeg,.webp';

export const MODALITIES: readonly ModalityContract[] = [
  { id: 'skin_wound', kind: 'skin_wound', labelKey: 'Pele/ferida', limitationKey: PROVISIONAL_LIMITATION, accept: IMAGES, dermatologicFilter: true },
  { id: 'ecg', kind: 'ecg', labelKey: 'ECG', limitationKey: PROVISIONAL_LIMITATION, accept: `${IMAGES},.pdf`, dermatologicFilter: false },
  { id: 'xray', kind: 'xray', labelKey: 'Rx', limitationKey: PROVISIONAL_LIMITATION, accept: `${IMAGES},.pdf,.dcm`, dermatologicFilter: false },
  { id: 'pocus', kind: 'pocus', labelKey: 'Ecografia/POCUS', limitationKey: PROVISIONAL_LIMITATION, accept: `${IMAGES},.pdf,.dcm`, dermatologicFilter: false },
  { id: 'document', kind: null, labelKey: 'Documento (PDF ou texto)', limitationKey: PROVISIONAL_LIMITATION, accept: '.pdf,.txt,.csv,.json,.xml', dermatologicFilter: false },
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
