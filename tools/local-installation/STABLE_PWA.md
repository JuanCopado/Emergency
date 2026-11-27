# Individual PWA and stable local runtime

Status: CLINICALLY_PENDING / NO_GO_CLINICAL_RELEASE.

## Contract

`stable_launcher.make_stable_server(root, verify_release=verifier, backend_factory=factory)` requires an authenticated, read-only verifier. There is no unsigned fallback. The verifier returns `(release_directory, manifest, file_descriptors, selection)`. The factory receives `(release_directory, ui_port, full_source_sha)` and returns a private backend session implementing `request(path, object)` and `close()`. The caller owns `serve_forever`, `shutdown` and `server_close`.

The installation retains a randomly assigned loopback port in `stable-origin.json`. Updates and explicit rollbacks use this same origin. An OS lock permits one runtime per installation. Windows uses exclusive socket binding; an occupied port fails without choosing another port. Existing files, cookies, browser profiles and browser preferences are never removed.

The selected authenticated snapshot is fixed for the lifetime of a runtime. Installing or selecting another release does not mutate that running snapshot. To use a new selection, finish/export open encounters and explicitly stop and restart the runtime. Stopping the local runtime interrupts API requests; a stale browser tab is not a substitute for keeping its matching runtime running.

## Update and rollback behavior

Build with `EMERGENCY_INDIVIDUAL_BUILD=1`. This defines `VITE_INDIVIDUAL_INSTALLATION=1`, requires the same-origin API, excludes laboratory entry points, injects the individual-installation marker and changes PWA registration from automatic update to prompt mode. Other builds retain their existing automatic-update behavior.

An installed worker checks for updates on focus, reconnect and every 30 seconds. A waiting update displays a banner. Each tab requires its own explicit confirmation; the current clinical note must be empty. The same guard runs again when the worker takes control. An update activated by another tab never automatically reloads this tab. The operator must finish/export other open encounters before confirming. This acknowledgement does not inspect or adjudicate other clinical workflows or tabs.

The implementation uses the installed vite-plugin-pwa 1.3 `onNeedReload` callback, which overrides its default page reload when an updated worker controls a tab. It does not silently opt in to that default reload.

The existing settings provider retains language, theme and microgram display preference in its existing storage keys. Neither the update controller nor the installer copies, clears or serializes clinical notes or arbitrary browser storage. Keeping the origin retains those settings across update and rollback. A previous prototype served on a different random port has a different browser origin: settings must be selected again in the existing Settings screen; automatic cross-origin migration is not claimed. No case data should be copied through a preference migration.

Every individual-build clinical transport sends its full source SHA in `X-Emergency-Revision`. A stale tab receives HTTP 409 before the new backend reads its payload. No automatic resubmission or note deletion occurs. Older cached pages may require an explicitly accepted reload before using the newly selected backend. Rollback applies the same version guard and update-consent rules.

Individual builds also gate first navigation to an unseen screen against the current runtime identity. A known update or mismatching runtime blocks that new lazy import, restores the current URL and shows a recoverable message. Previously visited screens remain reachable, including an open note. A route error boundary inside the existing draft provider contains residual dynamic-import failures without destroying that provider. Before an update is observed, an unavailable runtime does not block first navigation to a cached offline frontend screen. This guard applies only to builds containing it; it does not retrofit older installed pages. Retaining the note does not restore stale API compatibility: to finish an API operation such as canonical export, explicitly restore its matching runtime version. No new persistence or export mechanism is introduced.

## Local API boundary and offline limits

The browser receives no private backend token. The UI listener checks loopback peer, exact Host and Origin, rejects ambiguous framing, bounds JSON input to 26,165,824 bytes and output to 33,554,432 bytes, and exposes no backend sources, wheels or runtime files. Static assets are checked against the authenticated snapshot on each server read. Request paths, headers and clinical payloads are not logged.

The blood-gas OCR runtime is not packaged in this increment. Its API returns HTTP 503 with `OCR_RUNTIME_NOT_PACKAGED`. This is distinct from frontend gasometry calculations. Remote image interpretation remains unavailable in the individual backend. Do not label these capabilities as working offline.

With the local runtime running and external connectivity unavailable, packaged deterministic APIs can operate locally. Browser network emulation that disables loopback also disables those APIs: only successfully precached frontend capabilities can then run. Offline availability of a screen or an OS-installed PWA must be demonstrated in a real browser and must not be inferred solely from service-worker unit tests.

## Verification scope

Focused tests cover stable origin across restart/update/rollback, runtime exclusion, occupied-port refusal, stale revision rejection, private-file refusal, hostile framing/origin, bounded backend output, missing OCR capability and cleanup after backend failure. Frontend tests cover update consent, delayed control, a newly dirty note, another tab activating the update, failure retention and actual draft-provider behavior. They use synthetic data.

Combined signed-release browser installation/update/rollback, multi-tab evidence and native Windows PWA installation are separate acceptance checks. Until observed, they remain unverified by these focused tests. A passing synthetic verifier double is not evidence of package signature verification.
