import type { PreparedUpload } from './types';

const labels: Record<string, string> = {
  confidence_withheld: 'Confiança omitida porque o desempenho diagnóstico não foi validado.',
  abstained_before_provider: 'Envio ao serviço interrompido antes da interpretação.',
  provider_abstained: 'O serviço não forneceu uma interpretação.',
  sanitized_raster_too_large: 'A imagem processada excede o limite de envio.',
  reassurance_language: 'A proposta continha linguagem de exclusão não sustentada.',
  insufficient_resolution: 'Resolução insuficiente.',
  low_resolution: 'Resolução limitada.',
  no_visual_content_suspected: 'Não foi possível confirmar conteúdo visual utilizável.',
  unsupported_external_format: 'Formato excluído da interpretação externa.',
  gps_metadata_present: 'O ficheiro original contém metadados de localização. Não são enviados ao serviço.',
  trailing_data_after_image: 'O ficheiro original contém dados adicionais após a imagem. Não são enviados ao serviço.',
  metadata_present: 'O ficheiro original contém metadados. São removidos antes do envio ao serviço.',
  explicit: 'escolhida por si.',
  inferred_from_filename: 'inferida do nome do ficheiro; não verifica a modalidade real da imagem.',
  inferred_from_container: 'inferida do tipo de contentor; não verifica a modalidade real do conteúdo.',
  default_unclassified: 'nenhuma categoria enviada nem pista no nome do ficheiro; tratada como «Outro». A modalidade real não foi verificada.',
};

export function reviewMessage(value: string, ui: (key: string) => string): string {
  const describe = (code: string) => Object.prototype.hasOwnProperty.call(labels,code) ? ui(labels[code]!) : code;
  if (value.startsWith('abstained: ')) {
    return value.slice('abstained: '.length).split(', ').map(describe).join(' · ');
  }
  return describe(value);
}

export function mediaQualityMessages(flags: unknown, ui: (key: string) => string): string[] {
  if (!Array.isArray(flags)) return [];
  return ['insufficient_resolution', 'low_resolution', 'no_visual_content_suspected']
    .filter(code => flags.includes(code))
    .map(code => reviewMessage(code, ui));
}

// Categorical notices only: codes are allow-listed and no metadata value is ever rendered.
export function mediaPrivacyMessages(issues: unknown, metadataPresent: unknown, ui: (key: string) => string): string[] {
  const codes = Array.isArray(issues)
    ? ['gps_metadata_present', 'trailing_data_after_image'].filter(code => issues.includes(code))
    : [];
  if (codes.length === 0 && metadataPresent === true) codes.push('metadata_present');
  return codes.map(code => reviewMessage(code, ui));
}

// Transparency only: reports where the effective category came from; it never verifies the modality.
export function kindSourceMessage(source: unknown, ui: (key: string) => string): string | null {
  const known = ['explicit', 'inferred_from_filename', 'inferred_from_container', 'default_unclassified'];
  return typeof source === 'string' && known.includes(source) ? reviewMessage(source, ui) : null;
}

export function excludedContainer(prepared?: PreparedUpload) {
  return prepared?.media?.format === 'pdf' || prepared?.media?.format === 'dicom';
}

export const CONNECTION_MESSAGES = {
  network: 'Sem ligação ao serviço clínico. Verifique a rede e tente novamente; o que introduziu mantém-se nesta página.',
  timeout: 'O serviço clínico não respondeu a tempo. Nada foi aceite nem guardado; tente novamente.',
  providerNote: 'O pedido pode ter chegado ao serviço antes da falha; reveja manualmente e repita só se for necessário.',
} as const;

/** A connection failure is never a clinical result. Returns null for any other error. */
export function connectionErrorMessage(error: unknown, ui: (key: string) => string, providerCall = false): string | null {
  if (!(error instanceof Error) || error.name !== 'ClinicalApiConnectionError') return null;
  const failure = (error as Error & { failure?: unknown }).failure === 'timeout' ? 'timeout' : 'network';
  const base = ui(CONNECTION_MESSAGES[failure]);
  return providerCall ? `${base} ${ui(CONNECTION_MESSAGES.providerNote)}` : base;
}

export function uploadError(error: unknown, fallback: string, ui: (key: string) => string, providerCall = false) {
  const connection = connectionErrorMessage(error, ui, providerCall);
  if (connection) return connection;
  if (!(error instanceof Error)) return ui(fallback);
  if (error.message === 'clinical text upload exceeds character limit') {
    return ui('O texto do ficheiro excede 120 000 caracteres. Nada foi importado; divida-o em documentos menores e reveja cada parte.');
  }
  if (error.message.startsWith('invalid image upload:') || error.message === 'invalid or unsupported clinical image or filename') {
    return ui(error.message.endsWith('signature_mismatch')
      ? 'O conteúdo do ficheiro não corresponde ao formato declarado.'
      : 'O ficheiro foi recusado na verificação do nome, formato ou integridade.');
  }
  if (error.message.startsWith('clinical vision provider returned an invalid response')) {
    return ui('O serviço devolveu uma resposta inválida. A proposta não foi aceite.');
  }
  if (error.message === 'clinical vision provider is not configured') {
    return ui('O serviço de interpretação não está configurado. A imagem não foi enviada; reveja manualmente.');
  }
  if (error.message === 'clinical vision provider unavailable') {
    return ui('O serviço de interpretação está indisponível. Tente mais tarde ou reveja manualmente.');
  }
  return error.message;
}
