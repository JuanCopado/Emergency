# Clinical Minimal — first opt-in token slice

This isolated candidate starts from `5494b0037dcfe2c2565187985b862ffa8ea1d83b`, tree `78e27cb900f7dd901eb5aeb48026276dc48b942c`. That tree is the integrated PR120 receiver `2058e97179ae793914dcd016e4fd033395dbc3e2`; the local repository could not fetch the receiver commit because DNS resolution failed. No protected branch was changed.

The owner-approved reference is [PROTOTIPO_EMERGENCY.html](https://drive.google.com/file/d/1Ipk9t-qpN-8eMMz5fmYWJ0y5wfZh9dRp/view), local source SHA-256 `5903371cc1fd6d8143fdfa28c02661d77afa6638b0a6d5ee231b2ae5dc336e61`. Approval is recorded in owner decisions commit `9018e14bb058c6ebb6f8bf1224924997ba3109a7`. The later physician/agent cover variant is not used as a replacement specification.

Open `/?design=clinical-minimal` to inspect the first React implementation slice. The normal home page remains the default. The exact opt-in changes only the home page's color tokens, typography, radii, focus ring and removal of decorative halos. The existing theme control selects the approved light/dark palettes. Existing home content, links, search form, four languages, clinical warnings and data remain shared with the existing page.

This is the design foundation increment, not completion of the prototype's full layout or adoption of its illustrative modules. It adds no AI capability, clinical workflow, route, source, formula, drug, dose, state promotion, external request or image asset. CSS is scoped below the home container; the application shell, other pages, PDF/Word and print rules are unchanged.

Observed QA on this working tree: `npm run lint` PASS; build with the existing `EMERGENCY_SECURITY_AUDIT=1` flag PASS; existing UI and route-identity suites 40/40 PASS. The five generated JSON files produced by build were semantically identical to the base and restored in this isolated worktree; no catalog delta is included. The final additional browser-check script passed focused ESLint after declaring its browser evaluation globals.

Native Chrome `158.0.8127.37` presentation checks passed 16 states (four languages, light/dark, widths 360/1366): all 30 home links and all text identical to the default, exact background palette, localized document language, no horizontal overflow, 3px keyboard focus, and real search navigation with preview styles removed after leaving home. See [BROWSER_QA.json](BROWSER_QA.json). Chrome could not access loopback HTTP (`ERR_NETWORK_ACCESS_DENIED`), so this successful check fulfilled built artifact requests through Playwright on a synthetic origin; it does not verify the HTTP server, backend or deployment. Early harness attempts exposed a root-path rejection and a React render-timing assertion; these were fixed in the harness without changing app code. Screenshots were inspected against the approved reference for this token slice only, not certified as the complete prototype.

Reproduce with a built `app/dist`: set `MINIMAL_QA_DIST=1` and `MINIMAL_QA_OUTPUT` to an evidence directory, then run `node scripts/check-clinical-minimal.mjs` in `app`. The script requires native Chrome or an explicit `CHROME_PATH`; it neither downloads a browser nor disables security controls.

A technical review is required before any later proposal to make this appearance default. The optional query is not a security boundary or authorization to release clinically. Export implementations and clinical contracts were untouched; no new full export regression or clinical validation is claimed for this visual slice.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
