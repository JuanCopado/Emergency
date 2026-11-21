import { describe, expect, it } from 'vitest';
import { mediaQualityMessages, reviewMessage, uploadError } from '../clinical-note/imageReview';

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

  it('distinguishes provider configuration and availability from request errors', () => {
    expect(uploadError(new Error('clinical vision provider is not configured'),'',literal))
      .toBe('O serviço de interpretação não está configurado. A imagem não foi enviada; reveja manualmente.');
    expect(uploadError(new Error('clinical vision provider unavailable'),'',literal))
      .toBe('O serviço de interpretação está indisponível. Tente mais tarde ou reveja manualmente.');
    expect(uploadError(new Error('invalid clinical request'),'',literal)).toBe('invalid clinical request');
  });

  it('translates each supported media quality flag once and ignores arbitrary values', () => {
    const flags = [
      'low_resolution', 'low_resolution', 'insufficient_resolution', 'no_visual_content_suspected',
      'synthetic-private-id', 'confidence_withheld', 'abstained: low_resolution',
      { code: 'low_resolution' }, 'constructor', null, 123,
    ];
    expect(mediaQualityMessages(flags, key => `UI: ${key}`)).toEqual([
      'UI: Resolução insuficiente.',
      'UI: Resolução limitada.',
      'UI: Não foi possível confirmar conteúdo visual utilizável.',
    ]);
  });

  it.each([undefined, null, 'low_resolution', { 0: 'low_resolution', length: 1 }])(
    'ignores a non-array quality field (%s)',
    flags => expect(mediaQualityMessages(flags, literal)).toEqual([]),
  );
});
