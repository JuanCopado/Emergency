"""Blood gas extraction with a locally provisioned OCR model."""
import io
from decimal import Decimal
import json
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps
from acid_base_hyperglycemia import calculate
from blood_gas_geometry import bind, in_region, overlaps, pdf_lines, tsv_lines, validate_regions

LIMIT = int(os.getenv("BG_MAX_BYTES", 8 * 1024 * 1024))
PAGES = int(os.getenv("BG_MAX_PAGES", 8))
PIXELS = int(os.getenv("BG_MAX_PIXELS", 8_000_000))
FIELDS = {
    "pH": {"": "ph"}, "pCO2": {"mmHg": "pco2_mm_hg", "kPa": "pco2_kpa"},
    "pO2": {"mmHg": "pao2_mm_hg", "kPa": "pao2_kpa"},
    "HCO3": {"mmol/L": "hco3_mmol_l"}, "Na": {"mmol/L": "sodium_mmol_l"},
    "Cl": {"mmol/L": "chloride_mmol_l"}, "K": {"mmol/L": "potassium_mmol_l"},
    "Glucose": {"mg/dL": "glucose_mg_dl", "mmol/L": "glucose_mmol_l"},
    "Albumin": {"g/dL": "albumin_g_dl", "g/L": "albumin_g_l"},
    "FiO2": dict.fromkeys(("%", "fraction", "fracción", "fraccion"), "fio2_fraction"),
    "BE": {"mmol/L": None}, "Lactate": {"mmol/L": None},
    "iCa": {"mmol/L": None}, "Hb": {"g/dL": None}, "Hct": {"%": None},
    "sO2": {"%": None},
}
ALIASES = {"bicarbonato":"HCO3","sodio":"Na","potasio":"K","cloro":"Cl",
           "glucosa":"Glucose","lactato":"Lactate","albúmina":"Albumin"}
NAMES = {k.casefold(): k for k in FIELDS} | ALIASES
NUMBER = r"[+-]?\d+(?:[.,]\d+)?"
HEADER = re.compile(r"^\s*(?:muestra|sample|gasometr[ií]a)(?:\s*[:#]\s*|\s+(?=\d))(\S.*)$", re.I)

# Specimen IDs (Sample: A, Muestra #2) remain structural boundaries.
# A text declaration after a colon can be both a boundary and a specimen type.
SHORT_LABEL = re.compile(r"Sample|Muestra", re.I)
IDENTIFIER = re.compile(r"(?:\d+|[A-Za-z]+[-_]\d+)")
METADATA_LABEL = re.compile(r"Sample type|Tipo de muestra|Date|Fecha|Time|Hora|Device|Dispositivo|Flags|Avisos", re.I)
SAMPLE_TYPES = {
    'arterial': 'arterial', 'arterial blood': 'arterial', 'sangre arterial': 'arterial',
    'venosa': 'venosa', 'venoso': 'venosa', 'venous': 'venosa',
    'venous blood': 'venosa', 'sangre venosa': 'venosa',
    'capilar': 'capilar', 'capillary': 'capilar', 'capillary blood': 'capilar',
    'sangre capilar': 'capilar',
}


def finite_decimal_number(literal):
    """Reject representation loss; explicit zero and clinical ranges stay unchanged."""
    exact = Decimal(literal.replace(",", "."))
    number = float(exact)
    if not math.isfinite(number):
        raise ValueError("Valor numérico no finito")
    if exact != 0 and number == 0:
        raise ValueError("Valor numérico no representable: el literal no es cero")
    return number


def sample_type(value):
    return SAMPLE_TYPES.get(' '.join(value.casefold().split()))


def heading(line, labels):
    label, separator, value = line.partition(":")
    label = label.strip()
    if separator and labels.fullmatch(label):
        return label, value.lstrip()
    return None


def type_heading(line):
    match = heading(line, SHORT_LABEL)
    if match:
        label, value = match
        value = value.rstrip()
        if not IDENTIFIER.fullmatch(value):
            return label, value
    return None


def ocr_once(image):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d, "pixels.png")
        image.convert("RGB").save(path)
        if os.getenv("BG_OCR_MODEL"):
            cmd = ["node", str(Path(__file__).with_name("blood_gas_ocr.cjs")), str(path)]
        else:
            raise ValueError("Configure el modelo OCR local verificado")
        result = subprocess.run(cmd,capture_output=True,timeout=20,check=True)
        return json.loads(result.stdout.decode("utf-8-sig"))

def ocr_lines(image):
    """Compare all right-angle orientations, retaining literal OCR observations."""
    candidates = []
    for angle in (0, 90, 180, 270):
        result = ocr_once(image if angle == 0 else image.rotate(angle, expand=True))
        lines = tsv_lines(result['tsv'], angle, image.width, image.height)
        fields = parse('\n'.join(line['text'] for line in lines), 1)
        score = sum((2 if f['normalized_unit'] is not None else 0.5) *
                    max(0, lines[f['line']-1]['confidence']) / 100 for f in fields)
        candidates.append((score, lines, fields, angle))
    _, lines, fields, angle = max(candidates, key=lambda item: item[0])
    for field in fields:
        for _, other_lines, others, _ in candidates:
            for other in others:
                if (other['name'] == field['name'] and
                    overlaps(lines[field['line']-1]['bbox'], other_lines[other['line']-1]['bbox']) and
                    (other['number'], other['unit']) != (field['number'], field['unit']) and
                    other_lines[other['line']-1]['confidence'] >= 80):
                    lines[field['line']-1]['confidence'] = 0
    return lines, angle


def ocr(image):
    return '\n'.join(line['text'] for line in ocr_lines(image)[0])

def parse(text, page):
    fields = []
    for row, raw in enumerate(text.splitlines(), 1):
        line = raw.translate(str.maketrans("₂₃","23"))
        origin = "unknown"
        marker = re.search(r"(?<=\s)\[(measured|calculated)\]$", line.rstrip(), re.I)
        if marker:
            origin = marker[1].lower()
            line = line[:marker.start()].rstrip()
        match = re.fullmatch(r"\s*([\w₂₃]+)\s*[:=]?\s+("+NUMBER+r")\s*([^\s]*)\s*",line)
        if not match:
            # Retain ambiguous multi-token FiO2 units for explicit transcription.
            match = re.fullmatch(r"\s*(FiO2)\s*[:=]?\s+("+NUMBER+r")\s*(.*?)\s*", line, re.I)
        if match and match[1].casefold() in NAMES:
            name = NAMES[match[1].casefold()]
            number = finite_decimal_number(match[2])
            fields.append(dict(name=name, raw=raw, number=match[2], unit=match[3],
                               numeric_value=number,
                               normalized_unit=match[3] if match[3] in FIELDS[name] else None,
                               legibility="unverified" if match[3] in FIELDS[name] else "unit_unreadable",
                               page=page,line=row,review="pending",origin=origin))
    return fields

def samples(text, page):
    """Split only explicit sample headers; ambiguous repeated analytes abstain."""
    groups = []
    label, lines, offset = None, [], 0
    has_fields = has_type = False
    for index, line in enumerate(text.splitlines()):
        header = HEADER.fullmatch(line)
        declaration = type_heading(line)
        full = heading(line, METADATA_LABEL)
        long_type = full is not None and full[0].casefold() in ('sample type', 'tipo de muestra')
        if declaration and label is not None and not has_fields:
            # Consecutive labels before any analyte describe the same candidate.
            lines.append(line)
            has_type = True
        elif header or declaration or (long_type and has_fields and has_type):
            if lines:
                groups.append((label, "\n".join(lines), offset))
            label = header[1] if header else None
            has_type = bool(declaration or long_type)
            lines, offset = ([line], index) if has_type else ([], index + 1)
            has_fields = False
        else:
            lines.append(line)
            has_fields = has_fields or bool(parse(line, page))
            has_type = has_type or long_type
    if lines:
        groups.append((label, "\n".join(lines), offset))
    results, unassigned = [], []
    for label, content, offset in groups:
        fields = parse(content, page)
        ambiguous = len({f["name"] for f in fields}) != len(fields)
        for field in fields:
            field["line"] += offset
        metadata = []
        for index, line in enumerate(content.splitlines(), 1):
            match = heading(line, METADATA_LABEL) or type_heading(line)
            if match:
                metadata_label, value = match
                item = dict(label=metadata_label, raw=line, value=value, page=page,
                            line=index+offset, review="pending", source_sample_label=label)
                if metadata_label.casefold() in ('sample type', 'tipo de muestra', 'sample', 'muestra'):
                    item.update(kind='sample_type', normalized_sample_type=sample_type(value))
                metadata.append(item)
        if not fields:
            unassigned.extend(dict(m, scope='unassigned') for m in metadata)
            continue
        results.append(dict(label=label, fields=[] if ambiguous else fields,metadata=metadata,
                            blocked=ambiguous,
                            warning="Analitos repetidos; se requiere separar las muestras" if ambiguous else ""))
    results = results or [dict(label=None, fields=[], metadata=[], blocked=True,
                               warning="Sin parámetros legibles o sin segmentación fiable")]
    for result in results:
        result['metadata'].extend(dict(m) for m in unassigned)
    return results

def compare_specimen_layers(segments, native, visual, page):
    """Reconcile specimen declarations by position, including raster-only headers."""
    visual_groups = samples('\n'.join(line['text'] for line in visual), page)
    native_types = [(i, m) for i, segment in enumerate(segments) for m in segment['metadata']
                    if m.get('kind') == 'sample_type']
    block_owners = [set() for _ in segments]
    recorded = set()
    for group_index, group in enumerate(visual_groups):
        types = [m for m in group['metadata'] if m.get('kind') == 'sample_type']
        if not types:
            continue
        owners = [i for i, s in enumerate(segments) if any(
            a['name'] == b['name'] and overlaps(native[a['line']-1]['bbox'], visual[b['line']-1]['bbox'])
            for a in s['fields'] for b in group['fields'])]
        for i in owners:
            block_owners[i].add(group_index)
        for m in types:
            bbox = visual[m['line']-1]['bbox']
            matches = [(i, n) for i, n in native_types if overlaps(n.get('bbox'), bbox)]
            # The same unassigned header can occur in several segments.
            key = (m['line'], m['raw'])
            if key in recorded:
                continue
            recorded.add(key)
            def agrees(n):
                normalized = n.get('normalized_sample_type')
                return (n['value'].strip().casefold() == m['value'].strip().casefold()
                        or (normalized is not None and normalized == m.get('normalized_sample_type')))
            unassigned = m.get('scope') == 'unassigned'
            matching_segments = {i for i, _ in matches}
            targets = set(range(len(segments))) if unassigned else (
                matching_segments or set(owners) or set(range(len(segments))))
            conflict = bool(matches) and not all(agrees(n) for _, n in matches)
            if conflict:
                for _, n in matches:
                    n['type_discrepancy'] = True
            else:
                for _, n in matches:
                    n.update(visual_raw=m['raw'], visual_bbox=bbox)
                    if unassigned:
                        n['scope'] = 'unassigned'
                targets -= matching_segments
            for i in targets:
                item = dict(m, bbox=bbox, source_layer='visual_ocr', type_discrepancy=conflict)
                if unassigned or len(targets) != 1 or (not matches and not owners):
                    item['scope'] = 'unassigned'
                segments[i]['metadata'].append(item)
    for segment, owners in zip(segments, block_owners):
        if len(owners) > 1:
            segment.update(blocked=True, warning='Las capas del PDF delimitan muestras diferentes. Separe las áreas.')


def extract(data, regions=None):
    if not data or len(data) > LIMIT:
        raise ValueError("Tamaño no admitido")
    if regions is not None:
        validate_regions(regions)
    pages, total_pixels, preview_bytes, source_pages = [], 0, 0, 0

    def append(image, native_lines=None):
        nonlocal total_pixels, preview_bytes, source_pages
        import base64
        source_pages += 1
        page_number = source_pages
        image = image.convert('RGB')
        total_pixels += image.width * image.height
        if total_pixels > int(os.getenv('BG_TOTAL_PIXELS', 16_000_000)) or image.width * image.height > PIXELS:
            raise ValueError('Resolución acumulada excesiva')
        preview = io.BytesIO()
        image.save(preview, format='PNG')
        areas = [r for r in regions if r['page'] == page_number] if regions else [
            dict(page=page_number, bbox=[0, 0, image.width, image.height], label=None)]
        for area in areas:
            box = area['bbox']
            if box[2] > image.width or box[3] > image.height:
                raise ValueError('Área fuera del original')
            # Integer crop origin is shared by native and OCR coordinates.
            import math
            box = [math.floor(box[0]), math.floor(box[1]), math.ceil(box[2]), math.ceil(box[3])]
            visual, angle = ocr_lines(image.crop(box))
            for line in visual:
                b = line['bbox']
                line['bbox'] = [b[0]+box[0], b[1]+box[1], b[2]+box[0], b[3]+box[1]]
            native = [line for line in (native_lines or []) if in_region(line, box)]
            native_text = '\n'.join(line['text'] for line in native)
            use_native = bool(parse(native_text, page_number))
            lines = native if use_native else visual
            source = '\n'.join(line['text'] for line in lines)
            segments = samples(source, page_number)
            observed = parse('\n'.join(line['text'] for line in visual), page_number)
            observed_extra = []
            for segment in segments:
                for item in segment['metadata']:
                    item['bbox'] = lines[item['line']-1].get('bbox')
                    item['source_layer'] = 'pdf_text' if use_native else 'visual_ocr'
            if use_native:
                compare_specimen_layers(segments, native, visual, page_number)
            for segment in segments:
                preview_bytes += len(preview.getvalue())
                preview_bytes += bind(segment['fields'], lines, image)
                for field in segment['fields']:
                    if use_native:
                        matches = [v for v in observed if v['name'] == field['name'] and
                                   overlaps(field['bbox'], visual[v['line']-1]['bbox'])]
                        good = [v for v in matches if v['number'].replace(',', '.') == field['number'].replace(',', '.') and
                                v['unit'] == field['unit'] and visual[v['line']-1]['confidence'] >= 80]
                        field['visual_check'] = 'matched' if len(matches) == len(good) == 1 else 'discrepancy'
                        field['visual_observations'] = [dict(raw=v['raw'], bbox=visual[v['line']-1]['bbox']) for v in matches]
                        if field['visual_check'] != 'matched':
                            field['review'] = 'discrepancy'
                            field['warning'] = 'Texto y representación visual sin coincidencia fiable: cotejo médico obligatorio'
                    else:
                        field['visual_check'] = 'ocr_only'
                pages.append(dict(fields=segment['fields'], text=source,
                                  preview=base64.b64encode(preview.getvalue()).decode(),
                                  width=image.width, height=image.height,
                                  source_page=page_number, region=box, manual_region=regions is not None,
                                  sample_label=area.get('label') or segment['label'], blocked=segment['blocked'],
                                  metadata=segment['metadata'], warning=segment['warning'],
                                  method='text' if use_native else 'ocr', orientation=angle,
                                  visual_extras=observed_extra))
            if use_native:
                native_fields = parse(native_text, page_number)
                for item in observed:
                    if not any(item['name'] == f['name'] and overlaps(visual[item['line']-1]['bbox'], native[f['line']-1]['bbox']) for f in native_fields):
                        observed_extra.append(dict(raw=item['raw'], bbox=visual[item['line']-1]['bbox']))
                if observed_extra:
                    for result in pages[-len(segments):]:
                        result['warning'] += ' Hay parámetros exclusivamente visuales; revise cada recorte.'
                        if len(segments) == 1:
                            extra_fields = [v for v in observed if any(v['raw'] == e['raw'] and
                                            visual[v['line']-1]['bbox'] == e['bbox'] for e in observed_extra)]
                            preview_bytes += bind(extra_fields, visual, image)
                            for field in extra_fields:
                                field['review'] = 'discrepancy'
                                field['visual_check'] = 'visual_only'
                                field['warning'] = 'Parámetro ausente de la capa de texto: cotejo obligatorio'
                            result['fields'].extend(extra_fields)
                            if len({f['name'] for f in result['fields']}) != len(result['fields']):
                                result['blocked'] = True
                        else:
                            result['blocked'] = True
            if len(pages) > 16 or preview_bytes > 20 * 1024 * 1024:
                raise ValueError('Presupuesto de muestras o vistas previas excedido')

    if data.startswith(b'%PDF-'):
        import pypdfium2 as pdfium
        from pypdf import PdfReader
        if PdfReader(io.BytesIO(data)).is_encrypted:
            raise ValueError('PDF cifrado')
        with pdfium.PdfDocument(data) as doc:
            if not 0 < len(doc) <= PAGES:
                raise ValueError('Número de páginas no admitido')
            if regions is not None:
                validate_regions(regions, len(doc))
            for page in doc:
                w, h = page.get_size()
                if min(w, h) <= 0 or (2*w+1)*(2*h+1) > PIXELS:
                    raise ValueError('Página excesiva')
                bitmap = page.render(scale=2)
                try:
                    append(bitmap.to_pil(), pdf_lines(page, bitmap))
                finally:
                    bitmap.close()
    else:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ('PNG', 'JPEG', 'TIFF', 'WEBP') or getattr(image, 'n_frames', 1) != 1:
                raise ValueError('Formato o imagen multiframe no admitido')
            if image.width * image.height > PIXELS:
                raise ValueError('Resolución excesiva')
            if regions is not None:
                validate_regions(regions, 1)
            append(ImageOps.exif_transpose(image))
    return pages

def interpret(rows, sample):
    if sample not in ("arterial","venosa","capilar","desconocida"):
        raise ValueError("Muestra inválida")
    inputs, seen = {}, set()
    fio2_trace = None
    for row in rows:
        if row["review"]=="rejected":
            continue
        name, unit = row["name"], row["unit"]
        if row["review"]!="confirmed" or name in seen or unit not in FIELDS[name]:
            raise ValueError("Verifique cada campo, la unidad y una única muestra")
        seen.add(name)
        if not re.fullmatch(NUMBER,row["number"]):
            raise ValueError("Número ambiguo")
        number = finite_decimal_number(row["number"])
        key=FIELDS[name][unit]
        if name == "FiO2":
            number = number / 100 if unit == "%" else number
            # Physician-owner decision, 2026-11-19: clinical intake interval.
            # The canonical mathematical engine retains its existing contract.
            literal = Decimal(row["number"].replace(",", "."))
            minimum, maximum = (Decimal("21"), Decimal("100")) if unit == "%" else (Decimal("0.21"), Decimal("1"))
            if not minimum <= literal <= maximum:
                raise ValueError("FiO2 fuera de rango: confirme 21–100 % o fracción 0,21–1")
            fio2_trace = dict(reviewed_number=row["number"], reviewed_unit=unit,
                              normalized_fraction=number, used_fraction=number if sample == "arterial" else None)
        if key and (sample=="arterial" or name not in ("pCO2","pO2","FiO2")):
            inputs[key]=number
    if not seen:
        raise ValueError("Sin datos confirmados")
    result = calculate(inputs)
    result["confirmed_sample_type"] = sample
    if fio2_trace is not None:
        result["fio2_trace"] = fio2_trace
    result["confirmed_values"] = [
        dict(name=row["name"],number=finite_decimal_number(row["number"]),unit=row["unit"])
        for row in rows if row["review"] == "confirmed"
    ]
    result["limitations"] = [
        "Confirmación médica de cifras y unidades requerida en cada revisión.",
        "Los valores complementarios se muestran sin alertas automáticas de umbral.",
        "No se infiere FiO2 del dispositivo ni el tipo de muestra del idioma.",
    ]
    for unrelated in ("dka_criteria", "hhs_criteria", "insulin_infusion_reference"):
        result.pop(unrelated, None)
    if sample != "arterial":
        for key in tuple(result):
            if "compensation" in key or "expected_pco2" in key:
                del result[key]
    return result
