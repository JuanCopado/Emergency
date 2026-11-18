'use strict';
// Temporary fail-closed policy, not an upstream fix or a general RegExp sandbox.
const LIMITS = Object.freeze({ pattern: 1024, input: 8192, work: 100000000 });
function refuse(reason) {
  const error = new SyntaxError(`Temporary picomatch policy: ${reason}`);
  error.code = 'ERR_PICOMATCH_POLICY';
  throw error;
}
function validatePatternOptions(input, options = {}) {
  if (typeof input !== 'string' || input.length > LIMITS.pattern) refuse('pattern length/type');
  if (options.prepend || typeof options.expandRange === 'function') refuse('custom regex injection');
  // Raw regex syntax is outside the glob contract. Both parser entry paths use this copy.
  return { ...options, regex: false };
}
function repeatedBody(input, index) {
  let body = '', bracket = false;
  for (let i = index + 2; i < input.length; i++) {
    const c = input[i];
    if (c === '\\' || c === '"' || c === '(') refuse('unreviewed repeated extglob body');
    if (c === '[') { if (bracket) refuse('nested class'); bracket = true; }
    if (c === ']' && bracket) bracket = false;
    if (c === ')' && !bracket) return body;
    body += c;
  }
  refuse('unclosed repeated extglob');
}
function assertRepeated(input, index, options = {}) {
  const body = repeatedBody(input, index);
  if (/^\[[!^]?[A-Za-z0-9_. /:-]+\]$/.test(body)) return;
  const words = body.split('|');
  if (words.some(word => !/^[A-Za-z0-9_. /:-]+$/.test(word))) refuse('ambiguous repeated extglob');
  const folded = options.nocase || String(options.flags || '').includes('i') ? words.map(word => word.toLowerCase()) : words;
  for (let i = 0; i < folded.length; i++) {
    for (let j = 0; j < folded.length; j++) {
      if (i !== j && folded[j].startsWith(folded[i])) refuse('non-prefix-free repeated alternatives');
    }
  }
}
function addTokenCost(c, next, state) {
  if (c === '+' && next === '(') state.variable++;
  if (c === '?' && next === '(') state.choices *= 2;
  if (c === '|' || c === ',') state.choices += 1;
  if (c === '!' && next === '(') state.variable++;
}
function consumeToken(pattern, index, state) {
  const c = pattern[index];
  if (c === '\\') return index + 1;
  if (c === '"') { state.quoted = !state.quoted; return index; }
  if (state.quoted) return index;
  if (c === '[') { state.bracket = true; return index; }
  if (c === ']') { state.bracket = false; return index; }
  if (state.bracket) return index;
  if (c === '*') {
    state.variable++;
    while (pattern[index + 1] === '*') index++;
  } else addTokenCost(c, pattern[index + 1], state);
  return index;
}
function complexity(pattern) {
  const state = { variable: 0, choices: 1, bracket: false, quoted: false };
  for (let i = 0; i < pattern.length; i++) {
    i = consumeToken(pattern, i, state);
    if (state.choices > LIMITS.work) refuse('branch budget');
  }
  return { variable: state.variable, choices: state.choices };
}
function assertWork(pattern, input, cost) {
  if (typeof input !== 'string') refuse('non-string match input');
  if (input.length > LIMITS.input) refuse('match input length');
  let work = Math.max(1, pattern.length) * cost.choices;
  for (let i = 0; i < cost.variable; i++) {
    work *= input.length + 1;
    if (work > LIMITS.work) refuse('match work budget');
  }
}
function guardRegex(regex, pattern, options = {}) {
  validatePatternOptions(pattern, options);
  const cost = complexity(pattern);
  const nativeExec = RegExp.prototype.exec;
  // Standard test/exec and the matcher use this entry. Calling the native intrinsic
  // directly, recompiling .source or supplying forged parser states is trusted JS.
  Object.defineProperty(regex, 'exec', { configurable: false, writable: false, value(input) {
    assertWork(pattern, input, cost);
    return nativeExec.call(this, input);
  } });
  return regex;
}
module.exports = { LIMITS, validatePatternOptions, assertRepeated, complexity, assertWork, guardRegex };
