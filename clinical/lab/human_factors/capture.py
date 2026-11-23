"""Stage 1 trial capture (laboratory instrument, NO study executed). Standard library only; no file or network access.

A TrialRecorder turns a closed sequence of UI events of ONE trial into one record accepted by human_factors_tools.validate_records.
Only closed event types, opaque codes and a monotonic clock enter; there is no free text, no identity and no image content.
Participant codes are derived from a study secret held by the study custodian (HMAC), so the code cannot be reversed by the tool.
"""
import hashlib
import hmac
import re

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import human_factors_tools as hf  # noqa: E402

EVENTS = ("select", "change", "confirm", "cancel", "answer")
CODE = hf.CODE


def opaque_participant(study_secret, ordinal, prefix="HF1"):
    """Opaque participant code from a secret and an enrolment ordinal (no name, e-mail or hospital enters)."""
    if not isinstance(study_secret, str) or len(study_secret) < 16:
        raise ValueError("study_secret must be a custodian-held string of at least 16 characters")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1:
        raise ValueError("ordinal must be a positive integer")
    if not re.fullmatch(r"[A-Za-z0-9]{1,8}", prefix):
        raise ValueError("prefix must be 1-8 letters or digits")
    mac = hmac.new(study_secret.encode("utf-8"), f"{prefix}:{ordinal}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{prefix}-{mac[:10]}"


class TrialRecorder:
    """One trial. Times are monotonic milliseconds supplied by the caller (never wall-clock time)."""

    def __init__(self, participant, role, scenario_id, condition, period, intended_modality, platform, order_in_period, start_ms):
        self.fixed = {"participant": participant, "role": role, "scenario_id": scenario_id, "condition": condition,
                      "period": period, "intended_modality": intended_modality, "platform": platform, "order_in_period": order_in_period}
        self.start_ms = self._ms(start_ms)
        self.last_ms = self.start_ms
        self.current = None
        self.initial = None
        self.changes = 0
        self.confirmed = False
        self.closed = False
        self.comprehension = None

    @staticmethod
    def _ms(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value != value:
            raise ValueError("time must be a finite non-negative number of milliseconds")
        return float(value)

    def event(self, kind, at_ms, modality=None, correct=None):
        if kind not in EVENTS:
            raise ValueError("unknown event type")
        if self.closed:
            raise ValueError("the trial is already closed")
        at = self._ms(at_ms)
        if at < self.last_ms:
            raise ValueError("events must be in non-decreasing time order")
        self.last_ms = at
        if kind in ("select", "change"):
            if modality not in hf.MODALITIES:
                raise ValueError("unknown modality")
            if kind == "select":
                if self.initial is not None:
                    raise ValueError("a trial has exactly one initial selection (use change afterwards)")
                self.initial = modality
            else:
                if self.initial is None:
                    raise ValueError("change before the initial selection")
                if modality == self.current:
                    raise ValueError("change to the same modality is not a change")
                self.changes += 1
            self.current = modality
        elif kind == "confirm":
            if self.current is None:
                raise ValueError("confirm before any selection")
            self.confirmed = True
            self.closed = True
            self.end_ms = at
        elif kind == "cancel":
            self.confirmed = False
            self.current = None
            self.closed = True
            self.end_ms = at
        else:  # answer (comprehension): allowed after the trial was closed
            raise ValueError("answer is recorded with answer_comprehension after the trial closes")

    def answer_comprehension(self, correct):
        if not self.closed:
            raise ValueError("the comprehension answer follows the trial")
        if correct is not None and not isinstance(correct, bool):
            raise ValueError("correct must be true, false or null")
        self.comprehension = correct

    def record(self):
        if not self.closed:
            raise ValueError("the trial is not closed")
        built = dict(self.fixed, initial_modality=self.initial, chosen_modality=self.current if self.confirmed else None,
                     confirmed=self.confirmed, changed_modality_count=self.changes,
                     seconds=round((self.end_ms - self.start_ms) / 1000.0, 3), comprehension_correct=self.comprehension)
        hf.validate_records([built])
        return built


def collect(records):
    """Whole-session validation with the same rules as the analysis tool (no record is accepted that the tool would reject)."""
    hf.validate_records(records)
    return {"records": records, "count": len(records), "dataset_sha256": hf.digest(records),
            "note": "Capture only; no participant has been recruited and no study has been run."}
