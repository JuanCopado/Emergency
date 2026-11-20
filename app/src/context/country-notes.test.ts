import { describe, expect, it } from 'vitest';
import { reviewedWithoutDifference, type TopicReview } from './country-notes';

describe('explicit whole-topic documentary review', () => {
  const review: TopicReview = { country: 'PT', topic: 'Fixture', decision: 'synthetic',
    outcome: 'NO_MATERIAL_DIFFERENCE', reviewedOn: '2026-11-20', source: 'https://example.invalid/review' };
  it('requires one matching country, topic and sourced decision', () => {
    expect(reviewedWithoutDifference('PT', ['Fixture'], [review])).toEqual(review);
    expect(reviewedWithoutDifference('ES', ['Fixture'], [review])).toBeUndefined();
    expect(reviewedWithoutDifference('PT', ['Other'], [review])).toBeUndefined();
    expect(reviewedWithoutDifference('PT', [], [review])).toBeUndefined();
    expect(reviewedWithoutDifference('PT', ['Fixture'], [review, review])).toBeUndefined();
    expect(reviewedWithoutDifference('PT', ['Fixture'], [{ ...review, decision: '' }])).toBeUndefined();
    expect(reviewedWithoutDifference('PT', ['Fixture'], [{ ...review, source: '' }])).toBeUndefined();
  });
});
