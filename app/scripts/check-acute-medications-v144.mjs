// Compatibility entry point: one driver, original FLOW_FILTER and evidence names.
process.env.ACUTE_SCOPE = 'all';
process.env.ACUTE_LEGACY_OUTPUT = '1';
await import('./check-reviewed-acute-contracts.mjs');
