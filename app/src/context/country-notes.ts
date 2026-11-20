import dossier from '../../../clinical/references/t02-country-notes.json';

// A country-wide conclusion needs a separate, explicitly accepted whole-topic review.
export type TopicReview = {
  country: string;
  topic: string;
  outcome: 'NO_MATERIAL_DIFFERENCE';
  decision: string;
  reviewedOn: string;
  source: string;
};

export function reviewedWithoutDifference(code: string, topics: string[], reviews: readonly TopicReview[]) {
  if (topics.length !== 1) return undefined;
  const matching = reviews.filter(review => review.country === code && review.topic === topics[0]);
  if (matching.length !== 1) return undefined;
  const review = matching[0];
  if (review?.outcome === 'NO_MATERIAL_DIFFERENCE' && review.decision.trim() &&
      review.reviewedOn && review.source.startsWith('https://')) return review;
  return undefined;
}

export const topicReviews: readonly TopicReview[] = dossier.whole_topic_reviews;
