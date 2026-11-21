import { describe, expect, it } from 'vitest';
import { reviewMessage, uploadError } from '../clinical-note/imageReview';

const literal = (text: string) => text;

describe('image intake messages', () => {
  it('preserves unstructured observations and interprets only known flags', () => {
    expect(reviewMessage('constructor',literal)).toBe('constructor');
    expect(reviewMessage('Observation supplied for review.',literal)).toBe('Observation supplied for review.');
    expect(reviewMessage('provider_abstained',literal)).toBe('O serviço não forneceu uma interpretação.');
    expect(reviewMessage('abstained: insufficient_resolution, no_visual_content_suspected',literal))
      .toBe('Resolução insuficiente. · Não foi possível confirmar conteúdo visual utilizável.');
    expect(reviewMessage('abstained: sanitized_raster_too_large',literal))
      .toBe('A imagem processada excede o limite de envio.');
  });

  it('gives a stable translated message for a malformed provider response', () => {
    expect(uploadError(new Error('clinical vision provider returned an invalid response'),'',literal))
      .toBe('O serviço devolveu uma resposta inválida. A proposta não foi aceite.');
  });
});
