import { it } from 'vitest';
import { registerTests } from '../src/test/build-dependency-guard-cases.mjs';

registerTests(it, { integration: true });
