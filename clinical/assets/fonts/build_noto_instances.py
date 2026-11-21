"""Reproduce the two embedded CJK fonts from the pinned upstream variable font.

Preparation-only dependency: fonttools==4.68.0. Not imported by the application.
Usage: python build_noto_instances.py PATH_TO_NotoSansSC-VF.ttf OUTPUT_DIRECTORY
"""
import hashlib
from pathlib import Path
import sys

import fontTools
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SOURCE_SHA256 = 'd68bafcb48a2707749396aa12bbbd833cb70401f3a9a689fd2902c7e0d295964'


def main():
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    if fontTools.__version__ != '4.68.0':
        raise ValueError('Font preparation requires fonttools==4.68.0')
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('Upstream font SHA-256 mismatch')
    output.mkdir(parents=True, exist_ok=True)
    for style, weight in (('Regular', 400), ('Bold', 700)):
        font = TTFont(source, recalcTimestamp=False)
        instance = instantiateVariableFont(font, {'wght': weight}, inplace=True)
        instance.recalcTimestamp = False
        names = {
            1: 'Emergency CJK', 2: style, 3: 'Emergency CJK 2.004 ' + style,
            4: 'Emergency CJK ' + style, 6: 'EmergencyCJK-' + style,
            16: 'Emergency CJK', 17: style, 18: 'Emergency CJK ' + style,
            25: 'EmergencyCJK',
        }
        for record in instance['name'].names:
            if record.nameID in names:
                instance['name'].setName(names[record.nameID], record.nameID,
                                         record.platformID, record.platEncID, record.langID)
        target = output / ('EmergencyCJK-' + style + '.ttf')
        instance.save(target)
        print(target.name, target.stat().st_size, hashlib.sha256(target.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
