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
};

export function reviewMessage(value: string, ui: (key: string) => string): string {
  const describe = (code: string) => Object.prototype.hasOwnProperty.call(labels,code) ? ui(labels[code]!) : code;
  if (value.startsWith('abstained: ')) {
    return value.slice('abstained: '.length).split(', ').map(describe).join(' · ');
  }
  return describe(value);
}

export function excludedContainer(prepared?: PreparedUpload) {
  return prepared?.media?.format === 'pdf' || prepared?.media?.format === 'dicom';
}

export function uploadError(error: unknown, fallback: string, ui: (key: string) => string) {
  if (!(error instanceof Error)) return ui(fallback);
  if (error.message.startsWith('invalid image upload:') || error.message === 'invalid or unsupported clinical image or filename') {
    return ui(error.message.endsWith('signature_mismatch')
      ? 'O conteúdo do ficheiro não corresponde ao formato declarado.'
      : 'O ficheiro foi recusado na verificação do nome, formato ou integridade.');
  }
  if (error.message.startsWith('clinical vision provider returned an invalid response')) {
    return ui('O serviço devolveu uma resposta inválida. A proposta não foi aceite.');
  }
  return error.message;
}
