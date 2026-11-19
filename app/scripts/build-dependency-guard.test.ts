// @vitest-environment node
import { it } from 'vitest';
import { registerTests } from '../src/test/build-dependency-guard-cases.mjs';

registerTests((name, run) => it(name, run), { integration: true });
