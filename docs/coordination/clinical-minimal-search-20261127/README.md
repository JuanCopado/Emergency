# Home search — focused accessibility increment

Base `3cc5139b149feef390e6ceaa7358e2425d92620a`, isolated branch
`codex/clinical-minimal-search-accessibility-20261127`.

The existing shared Home search form, in both its default and opt-in Clinical
Minimal presentation, now has an accessible name using the existing search label.
Its input is associated with a short hidden keyboard hint. An explicit clear
button has a translated accessible label, does not submit the form and returns
focus to the same input. Escape clears the current query without navigating.
The existing empty and nonempty submission destinations and URL encoding are
preserved.

Enter used to confirm an IME candidate is prevented from submitting. Composition
start/end state, the native isComposing flag and legacy229 input-method key code
are handled; Escape during composition is left to the IME instead of clearing
the application query. These controls do not assert universal platform/IME
compatibility beyond the tests observed.

Only two new UI strings were added in ES/PT/EN/ZH: search.hint and search.clear.
Existing headings, clinical text, navigation routes, draft warning and visual
theme/presentation are unchanged. No UX/UI2.0 redesign or CSS change is included.

## Verification observed

-15 Home unit tests PASS:3 previous +12 new.
-New cases cover four-language landmark/input/hint names, clear-button keyboard
  semantics and focus return, Escape without route loss, encoded fresh search,
  empty search, Chinese composition events, direct submit during composition,
  native isComposing and legacy229 Enter.
-`npm run typecheck`: PASS.
-Actual DOM focus and router transitions were checked through React Testing
  Library/user-event; composition guards used synthetic DOM events.
-No browser, physical Chinese IME, Narrator, PDF, printing, clinical validation or
  full WCAG conformance is claimed here. Work performs the new browser-control
  checks separately; earlier PR127 tests are not repeated.

The source package-lock SHA-256 matched the existing dependency tree:
`b8fe2dab440fa967d64b816bc1bc4ea299c007f0f89352eb9c2265a023b58535`.
A temporary junction was rejected by the existing ordinary-path security
prehook. It was removed without touching its target, and the existing installed
artifacts were copied into an ordinary local node_modules directory. No npm
install/ci was run; the unchanged pretest/pretypecheck safeguards then passed.
No warning, rule, threshold or Trivy policy was suppressed.

React composition and focus-ref syntax was checked through the existing
Context7 connection, official React documentation library
`/reactjs/react.dev`; no proprietary project source was sent in those queries.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
