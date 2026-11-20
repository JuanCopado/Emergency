"""One bounded UTF-8 JSON boundary for multimodal manifests and frozen receipts.

Kept within this prototype: importing the clinical HTTP/OCR server merely to
parse a manifest would introduce unrelated runtime dependencies and side effects.
"""
from decimal import Decimal
import json
import math
from pathlib import Path

MAX_JSON_BYTES = 8 * 1024 * 1024


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_json_key')
        result[key] = value
    return result


def _finite_float(literal):
    value = float(literal)
    if not math.isfinite(value) or (value == 0 and Decimal(literal) != 0):
        raise ValueError('unrepresentable_json_number')
    return value


def _reject_constant(_):
    raise ValueError('nonfinite_json_constant')


def loads_object(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_JSON_BYTES:
        raise ValueError('manifest_size_limit_exceeded')
    result = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                        parse_float=_finite_float, parse_constant=_reject_constant)
    if not isinstance(result, dict):
        raise ValueError('json_object_required')
    return result


def read_object(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    return loads_object(raw)
