#!/usr/bin/env python3
"""Provision only the known public OCR model; verify bytes before installation."""
import argparse
import hashlib
import os
from pathlib import Path
import tempfile
from urllib.request import urlopen

URL = 'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/eng.traineddata'
SHA256 = '7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2'
SIZE = 4_113_088


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] /
                        'tools/blood-gas-ocr/models/eng.traineddata')
    args = parser.parse_args()
    target = args.output.absolute()
    if target.name != 'eng.traineddata':
        parser.error('The OCR runtime requires the filename eng.traineddata')
    if target.exists():
        if target.is_symlink() or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != SHA256:
            parser.error('Refusing to replace an existing unverified path')
        print(f'Verified OCR model: {target}')
        return
    # This public artifact download contains no application or clinical data.
    with urlopen(URL, timeout=30) as response:
        data = response.read(SIZE + 1)
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('OCR model size or SHA-256 does not match the reviewed artifact')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    try:
        # Atomic exclusive installation preserves any concurrent/unknown file.
        os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'Installed verified OCR model: {target}')


if __name__ == '__main__':
    main()
