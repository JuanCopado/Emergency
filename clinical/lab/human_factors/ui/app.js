/* DOM glue for the lab page. No decision logic here: see ui-logic.js (lookup into fixtures from the Python harness). */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var fixtures, session = null;
  var TITLES = { es: "No se puede enviar este archivo", pt: "Não é possível enviar este ficheiro", en: "This file cannot be sent" };

  function render() {
    var st = session.state(), msg = session.message();
    $("alert").hidden = !msg;
    if (msg) { $("alert-title").textContent = TITLES[$("lang").value]; $("alert-text").textContent = msg.text; $("alert").dataset.trigger = msg.trigger_id; $("alert").dataset.message = msg.message_id; }
    $("recovery").hidden = !msg;
    $("send").disabled = !st.canSend;
    $("sentbox").hidden = !st.sent;
    $("events").textContent = JSON.stringify(session.export(), null, 1);
    $("log-section").hidden = false;
    Array.prototype.forEach.call(document.querySelectorAll("input[name=modality]"), function (r) { r.checked = (r.value === (st.modality === null ? "none" : st.modality)); });
  }
  function start() {
    var arm = $("arm").value;
    session = HFLab.createSession({ fixtures: fixtures, arm: arm, trialId: $("trial").value, lang: $("lang").value, clock: function () { return performance.now(); } });
    var t = fixtures.trials.filter(function (x) { return x.stimulus_id === $("trial").value; })[0];
    $("file").textContent = "Archivo sintético " + t.stimulus_id + " (" + t.container.extension + ") · el contenido no se muestra";
    $("selector").hidden = arm !== "B";
    $("lab").dataset.arm = arm;
    $("lab").dataset.layer7ExecutionMode = arm === "B" ? "SIMULATED_LAB_HARNESS_ONLY" : "NOT_APPLICABLE_ARM_A";
    $("stage").hidden = false;
    render();
  }
  function init(data) {
    fixtures = data;
    data.trials.forEach(function (t) { var o = document.createElement("option"); o.value = t.stimulus_id; o.textContent = t.stimulus_id + " · " + t.scenario_code; $("trial").appendChild(o); });
    data.options.forEach(function (name) {
      var l = document.createElement("label"), r = document.createElement("input");
      r.type = "radio"; r.name = "modality"; r.value = name;
      r.addEventListener("change", function () { if (session) { session.selectModality(name); render(); } });
      l.appendChild(r); l.appendChild(document.createTextNode(" " + (name === "none" ? "(sin seleccionar)" : name)));
      $("options").appendChild(l);
    });
    $("start").addEventListener("click", start);
    $("send").addEventListener("click", function () { var r = session.attemptSend(); render(); if (r.blocked) $("alert").focus(); });
    $("rec-modality").addEventListener("click", function () { var first = document.querySelector("input[name=modality]"); if (first) first.focus(); });
    $("rec-file").addEventListener("click", function () { session.replaceFile(); render(); });
    $("end").addEventListener("click", function () { session.finish(); render(); });
    $("export").addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(session.export(), null, 1)], { type: "application/json" }), a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = "hf_lab_events.json"; a.click();
    });
    window.__HF_EXPORT__ = function () { return session ? session.export() : null; };
    document.documentElement.dataset.ready = "1";
  }
  init(window.__HF_FIXTURES__);
})();
