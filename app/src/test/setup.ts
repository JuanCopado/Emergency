import '@testing-library/jest-dom/vitest';

// jsdom does not implement scrolling.
window.scrollTo = (() => {}) as typeof window.scrollTo;
