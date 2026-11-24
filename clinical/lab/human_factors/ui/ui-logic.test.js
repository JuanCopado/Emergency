"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const HFLab = require("./ui-logic.js");
const fixtures = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures.json"), "utf8"));
const clockFrom = (values) => { let i = 0; return () => values[Math.min(i++, values.length - 1)]; };

test("arm B E1: undeclared modality blocks the send with the approved text and offers no force send", () => {
  const s = HFLab.createSession({ fixtures, arm: "B", trialId: "S1-14", lang: "es", clock: clockFrom([0, 10, 20, 30, 40, 50, 60, 70, 80, 90]) });
  assert.equal(s.state().modality, null);
  const r = s.attemptSend();
  assert.equal(r.blocked, true);
  assert.equal(r.trigger_id, "T7-01_UNDECLARED_MODALITY");
  assert.match(r.text, /No se ha seleccionado una modalidad admitida/);
  assert.equal(s.state().canSend, false);
  assert.throws(() => s.attemptSend(), /no force send/);
  assert.equal(s.export().forced_send_available, false);
});

test("recovery by choosing a compatible modality, then the simulated send completes", () => {
  const s = HFLab.createSession({ fixtures, arm: "B", trialId: "S1-14", lang: "en", clock: clockFrom([0, 5, 10, 15, 100, 200, 300, 400, 500, 600]) });
  s.attemptSend();
  s.selectModality("skin_wound");
  assert.equal(s.state().canSend, true);
  assert.equal(s.attemptSend().blocked, false);
  const out = s.finish();
  const types = out.events.map((e) => e.type);
  assert.deepEqual(types.slice(0, 2), ["trial_start", "preview_shown"]);
  assert.ok(types.includes("layer7_message_shown") && types.includes("recovery_action") && types.includes("send_simulated"));
  assert.equal(out.events.find((e) => e.type === "recovery_action").action, "change_modality");
  assert.equal(out.events.at(-1).recovery_outcome, "recovered");
});

test("E2 corrupt and incompatible files: replacing the file is the only way out, never forcing", () => {
  for (const [id, trigger, message] of [["S1-15", "T7-03_CORRUPT_UNPROCESSABLE", "MSG_T7_C"], ["S2-15", "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_B"], ["QA-01", "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_D"]]) {
    const s = HFLab.createSession({ fixtures, arm: "B", trialId: id, lang: "pt" });
    const r = s.attemptSend();
    assert.equal(r.trigger_id, trigger, id);
    assert.equal(s.message().message_id, message, id);
    assert.throws(() => s.attemptSend(), /no force send/);
    s.replaceFile();
    assert.equal(s.attemptSend().blocked, false, id);
  }
});

test("E1: replacing the file does NOT lift T7-01 while the modality is still undeclared", () => {
  const s = HFLab.createSession({ fixtures, arm: "B", trialId: "S1-14", lang: "es" });
  s.attemptSend();
  s.replaceFile();
  const again = s.attemptSend();
  assert.equal(again.blocked, true);
  assert.equal(again.trigger_id, "T7-01_UNDECLARED_MODALITY");
  s.selectModality("ecg");
  assert.equal(s.attemptSend().blocked, false);
});

test("arm A (legacy mock): no Layer 7, no selector, the send is simulated directly", () => {
  const s = HFLab.createSession({ fixtures, arm: "A", trialId: "S1-15", lang: "es" });
  assert.throws(() => s.selectModality("ecg"), /arm A has no modality selector/);
  assert.equal(s.attemptSend().blocked, false);
  const out = s.finish();
  assert.equal(out.layer7_execution_mode, "NOT_APPLICABLE_ARM_A");
  assert.ok(!out.events.some((e) => e.type === "layer7_message_shown"));
  assert.ok(!out.events.some((e) => e.type === "preview_shown"));
});

test("events: closed types, monotonic relative milliseconds, no calendar time, no free text", () => {
  const s = HFLab.createSession({ fixtures, arm: "B", trialId: "S2-15", lang: "es", clock: clockFrom([50, 40, 30, 20, 10, 5, 100, 90, 80]) });   // a clock that goes backwards
  s.attemptSend(); s.replaceFile(); s.attemptSend();
  const out = s.finish();
  let last = -1;
  for (const e of out.events) {
    assert.ok(HFLab.EVENT_TYPES.includes(e.type));
    assert.ok(Number.isInteger(e.t_ms) && e.t_ms >= last);
    last = e.t_ms;
  }
  const text = JSON.stringify(out);
  assert.ok(!/\d{4}-\d{2}-\d{2}/.test(text));
  assert.ok(!/Date|timestamp/i.test(text));
});

test("fixtures: every abstention comes from the harness with send_allowed=false and all three languages", () => {
  for (const trial of fixtures.trials) {
    for (const d of Object.values(trial.by_modality)) {
      if (d.trigger_id) {
        assert.equal(d.send_allowed, false);
        assert.deepEqual(Object.keys(d.texts).sort(), ["en", "es", "pt"]);
      }
    }
  }
});

test("invalid inputs are rejected", () => {
  assert.throws(() => HFLab.createSession({ fixtures, arm: "C", trialId: "S1-14" }), /arm must be A or B/);
  assert.throws(() => HFLab.createSession({ fixtures, arm: "B", trialId: "S1-14", lang: "zh" }), /language/);
  assert.throws(() => HFLab.createSession({ fixtures, arm: "B", trialId: "nope" }), /unknown trial/);
  const s = HFLab.createSession({ fixtures, arm: "B", trialId: "S1-14" });
  assert.throws(() => s.selectModality("dermatology"), /unknown modality/);
  assert.throws(() => s.replaceFile(), /needs a blocked state/);
});
