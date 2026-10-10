#!/usr/bin/env python3
"""Generate or check the outpatient frontend catalog from the Python registry."""
import argparse
from pediatric_catalog import ROOT, build_catalog, serialize_catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = ROOT.parent / 'app/src/data/generatedPediatricOutpatient.json'
    content = serialize_catalog()
    if args.check:
        if not output.exists() or output.read_text(encoding='utf-8') != content:
            raise SystemExit('Pediatric catalog is stale; run npm run pediatrics:build')
    else:
        output.write_text(content, encoding='utf-8', newline='\n')
    print(build_catalog()['inventory'])


if __name__ == '__main__':
    main()
