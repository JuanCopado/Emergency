"""Coordinates refer to the rendered, EXIF-normalized original page, in pixels.

No image enhancement, inpainting, inferred digits or unit correction is used.
"""
import base64
import csv
import io
import math


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)] if boxes else None


def original_box(box, angle, width, height):
    def point(x, y):
        return {0: (x, y), 90: (width-y, x), 180: (width-x, height-y),
                270: (y, height-x)}[angle]
    points = [point(x, y) for x in (box[0], box[2]) for y in (box[1], box[3])]
    return [min(x for x, _ in points), min(y for _, y in points),
            max(x for x, _ in points), max(y for _, y in points)]


def tsv_lines(tsv, angle, width, height):
    groups = {}
    columns = 'level page_num block_num par_num line_num word_num left top width height conf text'.split()
    for row in csv.DictReader(io.StringIO(tsv), fieldnames=columns, delimiter='\t'):
        if row['level'] != '5' or not row.get('text', '').strip():
            continue
        key = tuple(row[k] for k in ('page_num', 'block_num', 'par_num', 'line_num'))
        x, y, w, h = [int(row[k]) for k in ('left', 'top', 'width', 'height')]
        groups.setdefault(key, []).append((row['text'], [x, y, x+w, y+h], float(row['conf'])))
    return [dict(text=' '.join(word[0] for word in words),
                 bbox=original_box(union([word[1] for word in words]), angle, width, height),
                 confidence=min(word[2] for word in words)) for words in groups.values()]


def pdf_lines(page, bitmap):
    """Read each PDF character by its native index; do not zip Unicode offsets."""
    conversion = bitmap.get_posconv(page)
    lines, chars, boxes = [], [], []
    def flush():
        if ''.join(chars).strip():
            lines.append(dict(text=''.join(chars), bbox=union(boxes), confidence=None))
        chars.clear()
        boxes.clear()
    text = page.get_textpage()
    try:
        if text.count_chars() > 20_000:
            raise ValueError('Demasiado texto por página')
        for index in range(text.count_chars()):
            char = text.get_text_range(index, 1)
            if '\r' in char or '\n' in char:
                flush()
                continue
            chars.append(char)
            if char.strip():
                left, bottom, right, top = text.get_charbox(index)
                points = [conversion.to_bitmap(x, y) for x in (left, right) for y in (bottom, top)]
                boxes.append([min(p[0] for p in points), min(p[1] for p in points),
                              max(p[0] for p in points), max(p[1] for p in points)])
        flush()
    finally:
        text.close()
    return lines


def validate_regions(regions, page_count=None):
    if not isinstance(regions, list) or not 1 <= len(regions) <= 16:
        raise ValueError('Seleccione entre 1 y 16 áreas')
    for index, region in enumerate(regions):
        page, box = region.get('page'), region.get('bbox')
        if type(page) is not int or page < 1 or (page_count and page > page_count):
            raise ValueError('Página de área inválida')
        if not isinstance(box, list) or len(box) != 4 or not all(
            type(v) in (int, float) and math.isfinite(v) for v in box
        ) or min(box) < 0 or box[2]-box[0] < 8 or box[3]-box[1] < 8:
            raise ValueError('Coordenadas de área inválidas')
        label = region.get('label', str(index+1))
        if not isinstance(label, str) or len(label) > 80:
            raise ValueError('Etiqueta de área inválida')
        for previous in regions[:index]:
            a = previous['bbox']
            if previous['page'] == page and min(a[2], box[2]) > max(a[0], box[0]) and min(a[3], box[3]) > max(a[1], box[1]):
                raise ValueError('Las áreas de distintas muestras no deben solaparse')


def in_region(line, region):
    box = line.get('bbox')
    # Require the entire native text line to belong to the selected sample.
    return box and box[0] >= region[0] and box[1] >= region[1] and box[2] <= region[2] and box[3] <= region[3]


def overlaps(a, b):
    if not a or not b:
        return False
    intersection = max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))
    smaller = min((a[2]-a[0])*(a[3]-a[1]), (b[2]-b[0])*(b[3]-b[1]))
    return smaller > 0 and intersection / smaller >= 0.3


def bind(fields, lines, image):
    total = 0
    for field in fields:
        line = lines[field['line']-1]
        field['bbox'] = line.get('bbox')
        field['confidence'] = line.get('confidence')
        field['coordinate_space'] = 'rendered_original_pixels_top_left'
        if not field['bbox']:
            field['legibility'] = 'location_unverified'
            field['crop'] = None
            continue
        box = field['bbox']
        crop_box = [max(0, math.floor(box[0])-4), max(0, math.floor(box[1])-4),
                    min(image.width, math.ceil(box[2])+4), min(image.height, math.ceil(box[3])+4)]
        field['crop_bbox'] = crop_box
        output = io.BytesIO()
        image.crop(crop_box).convert('RGB').save(output, format='PNG')
        total += len(output.getvalue())
        field['crop'] = base64.b64encode(output.getvalue()).decode()
        # An engineering abstention threshold, not a clinically validated confidence.
        if field['confidence'] is not None and field['confidence'] < 80:
            field['legibility'] = 'low_confidence'
            field['review'] = 'discrepancy'
            field['warning'] = 'OCR inseguro: transcriba desde el original o rechace el campo'
    return total
