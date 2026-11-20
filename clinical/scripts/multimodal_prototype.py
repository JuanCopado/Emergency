#!/usr/bin/env python3
"""Local media engineering CLI. No network, clinical inference or training."""
import argparse
import json
from pathlib import Path

from multimodal.bank import validate_bank, admitted_inputs, blinded_inputs
from multimodal.demo import create_demo
from multimodal.evaluation import evaluate
from multimodal.json_io import read_object


def _read(path):
    return read_object(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    demo = commands.add_parser('demo')
    demo.add_argument('destination', type=Path)
    for command in ('validate-bank', 'admit', 'export-blind', 'evaluate'):
        sub = commands.add_parser(command)
        sub.add_argument('bank', type=Path)
        if command == 'admit':
            sub.add_argument('--split', choices=['teaching', 'development', 'blind_test'], required=True)
        if command == 'evaluate':
            sub.add_argument('dataset', type=Path)
            sub.add_argument('--freeze-sha256', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            result = create_demo(args.destination)
        else:
            bank = _read(args.bank)
            if args.command == 'validate-bank':
                result = validate_bank(bank)
            elif args.command == 'admit':
                result = dict(errors=[], inputs=admitted_inputs(bank, args.bank.parent, args.split))
            elif args.command == 'export-blind':
                result = dict(errors=[], inputs=blinded_inputs(bank, args.bank.parent))
            else:
                result = evaluate(bank, _read(args.dataset), args.bank.parent, freeze_sha256=args.freeze_sha256)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return bool(result.get('errors'))
    except Exception as exc:
        # Never echo arbitrary manifest values, original paths or decoder text.
        allowed_demo_errors = {'demo_destination_must_be_new', 'demo_requires_ffmpeg_and_ffprobe',
                               'demo_media_generation_failed'}
        code = str(exc) if args.command == 'demo' and type(exc) is ValueError and str(exc) in allowed_demo_errors else 'operation_blocked'
        print(json.dumps(dict(errors=[code], clinical_release_status='CLINICALLY_PENDING')))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
