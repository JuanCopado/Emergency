import '@testing-library/jest-dom/vitest';

// jsdom does not implement scrolling.
if (typeof window !== 'undefined') {
  window.scrollTo = (() => {}) as typeof window.scrollTo;
}
