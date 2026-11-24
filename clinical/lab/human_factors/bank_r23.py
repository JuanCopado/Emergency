"""Stimulus bank of the R23 protocol (30 stimuli = 2 sets x 15 pairs) · LABORATORY ONLY, no patient data, no clinical adjudication.

Composition follows R23_GEMINI_INFORME_INTEGRADO Part II table 6 (pairs 01-15; M3 = A,F; M1 = B,C,D; M2 = E1,E2). Only the stimuli that can
be produced as technically valid files WITHOUT inventing realistic medical imagery are generated (procedural placeholders, synthetic PDFs and
deliberately corrupt/incompatible containers for the Layer 7 triggers). Every other stimulus stays PENDING_STIMULUS_GENERATION with its
specification. Hashes are SHA-256 over the REAL BYTES of each file. The bank is NOT frozen and NOT validated.
"""
import hashlib
import io
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
STIMULI_DIR = HERE / "bank" / "stimuli"
MANIFEST_PATH = HERE / "bank" / "stimuli_manifest.json"
BANK_VERSION = "alt-b-bank-0.1"
PENDING = "PENDING_STIMULUS_GENERATION"
GENERATED = "GENERATED_TECHNICAL_PLACEHOLDER"
PAIR_CODES = {1: "A", 2: "A", 3: "A", 4: "B", 5: "B", 6: "C", 7: "D", 8: "F", 9: "F", 10: "F", 11: "F", 12: "F", 13: "F", 14: "E1", 15: "E2"}
MECHANISM = {"A": "M3", "B": "M1", "C": "M1", "D": "M1", "E1": "M2", "E2": "M2", "F": "M3"}
HAMMING_MIN = 16
T01, T03, T04 = "T7-01_UNDECLARED_MODALITY", "T7-03_CORRUPT_UNPROCESSABLE", "T7-04_FORMAT_CONTAINER_MISMATCH"

# pair -> (true_modality, route_modality, difficulty_level, [(spec set1, container1, mst1), (spec set2, container2, mst2)], expected trigger per set)
_P = {
 1: ("skin_wound", "skin_wound", "low_medium", ("Herida superficial abierta sin cierre visible; piel clara, luz neutra, JPEG RGB.", "jpeg", 2), ("Herida superficial abierta sin cierre visible; piel clara, luz neutra, JPEG RGB.", "jpeg", 3)),
 2: ("skin_wound", "skin_wound", "medium", ("Herida con suturas visibles y exudado leve; piel media, luz cálida, JPEG RGB.", "jpeg", 5), ("Herida con grapas visibles y cambio cromático perilesional leve; piel media, luz cálida, JPEG RGB.", "jpeg", 6)),
 3: ("skin_wound", "skin_wound", "high", ("Lesión/úlcera superficial con costra oscura; piel oscura, luz móvil con sombra leve, WebP RGB.", "webp", 8), ("Lesión/úlcera superficial con exudado y borde irregular; piel oscura, luz móvil con sombra leve, WebP RGB.", "webp", 9)),
 4: ("skin_wound", "ecg", "medium", ("Galería de 4 miniaturas contiguas (IMG_4102.jpg-4105.jpg): herida sintética sobre fondo claro junto a ECG.", "jpeg", 4), ("Galería de 4 miniaturas contiguas (IMG_5201.jpg-5204.jpg): herida sintética sobre gasa/fondo claro junto a ECG.", "jpeg", 7)),
 5: ("skin_wound", "ecg", "inspection_of_thumbnail_ignoring_filenames", ("Herida suturada sintética con nombre confusor (ecg_guardia_01.jpg, JPEG RGB).", "jpeg", 5), ("Laceración abierta sintética con nombre confusor (trazado_box3.jpg, JPEG RGB).", "jpeg", 4)),
 6: ("skin_wound", "xray", "high_tonal_similarity", ("Herida oscura/necrótica sintética (fondo oscuro) junto a miniaturas de Rx tórax.", "jpeg", 6), ("Lesión cutánea extensa sintética (fondo oscuro) junto a miniaturas de Rx extremidad.", "jpeg", 8)),
 7: ("skin_wound", "pocus", "high_visual_similarity", ("Herida/hematoma cutáneo sintético (luz tenue) junto a capturas ecográficas oscuras.", "jpeg", 5), ("Herida con apósito parcial sintética (luz tenue) junto a capturas ecográficas oscuras.", "jpeg", 3)),
 8: ("ecg", "ecg", "critical_control_zero_false_block", ("Foto móvil RGB sin DICOM (IMG_7011.jpg, inclinación 4°) de ECG sintético en papel milimetrado (sin elevación ST).", "jpeg", None), ("Foto móvil RGB sin DICOM (IMG_8022.jpg, inclinación 5°) de ECG sintético impreso (sin elevación ST).", "jpeg", None)),
 9: ("ecg", "ecg", "realism_of_screen_photo", ("Foto móvil RGB de monitor multiparamétrico simulado con tira de ECG: ritmo y reflejo leve, WebP RGB.", "webp", None), ("Foto móvil RGB de pantalla clínica simulada con ECG 12 derivaciones y reflejo leve, JPEG RGB.", "jpeg", None)),
 10: ("xray", "xray", "critical_control_zero_false_block", ("Foto móvil RGB de monitor simulado con Rx tórax PA sintética/abierta libre de PHI (IMG_7033.jpg, sin DICOM).", "jpeg", None), ("Foto móvil RGB de monitor simulado con Rx muñeca/tobillo sintética/abierta libre de PHI (IMG_8044.jpg, sin DICOM).", "jpeg", None)),
 11: ("xray", "xray", "realism_urgent_xray", ("Foto móvil RGB oblicua leve de Rx torácica/abdominal con borde de pantalla, WebP RGB.", "webp", None), ("Foto móvil RGB de Rx pelvis/tórax con leve patrón moiré de pantalla, JPEG RGB.", "jpeg", None)),
 12: ("pocus", "pocus", "critical_control_zero_false_block", ("Captura móvil RGB de ecógrafo simulado/fantoma (ventana FAST sin líquido libre evidente, sin PHI/DICOM).", "jpeg", None), ("Captura móvil RGB de ecógrafo simulado/fantoma (ventana subxifoidea/pulmonar sin derrame evidente, sin PHI/DICOM).", "jpeg", None)),
 13: ("document", "document", "pdf_and_photo_in_document_route", ("PDF sintético multipágina (2 págs.: informe ficticio con negaciones válidas en ES/PT AO90/EN) por ruta Documento (puente kind=null).", "pdf", None), ("Foto móvil RGB (JPEG) de hoja impresa sintética de analítica/informe con pliegue leve por ruta Documento (puente kind=null).", "jpeg", None)),
 14: (None, None, "trigger_expected", ("Envío de imagen válida sintética sin elegir modalidad (declared_modality=null, selection_origin='none').", "unspecified_image", None), ("Envío de documento válido sintético sin elegir modalidad (declared_modality=null, selection_origin='none').", "pdf", None)),
 15: (None, "skin_wound", "trigger_expected", ("Corrupción técnica (T7-03): JPEG truncado/cabecera rota (o 0 bytes / exceso PR66 > 512 segmentos) en ruta fotográfica.", "jpeg_corrupt", None), ("Incompatibilidad (T7-04): PDF textual sintético enviado a ruta exclusivamente fotográfica (modality_container_incompatible; el subcaso global_unsupported_format queda para el QA técnico).", "pdf", None)),
}
EXPECTED = {(14, 1): T01, (14, 2): T01, (15, 1): T03, (15, 2): T04}
GENERATED_FILES = {"S1-08": "S1-08.jpg", "S2-08": "S2-08.jpg", "S1-09": "S1-09.webp", "S2-09": "S2-09.jpg", "S1-13": "S1-13.pdf",
                   "S2-13": "S2-13.jpg", "S1-14": "S1-14.png", "S2-14": "S2-14.pdf", "S1-15": "S1-15.jpg", "S2-15": "S2-15.pdf"}
PROCEDURAL_SCHEMATIC = {"S1-08", "S2-08", "S1-09", "S2-09", "S2-13"}   # R25: schematic renders, NOT clinical imagery
SCHEMATIC_JUSTIFICATION = ("Stage 1 measures usage errors (modality selection, confirmation, false cancellation, comprehension of technical abstentions), not "
                           "diagnostic performance. For the legitimate-negative controls (scenario F) the stimulus only has to be recognizable as its true "
                           "modality and technically valid (RGB photo, no DICOM) so that the pipeline must NOT block it. A schematic is a candidate for that "
                           "narrow role only; it is NOT assumed valid until two independent reviewers rate realism >= 4/5 and the owner signs.")
SCHEMATIC_LIMITS = {
    "S2-09": "Synthetic model with derived limb leads and modeled R-wave progression; not clinically validated. The rendered screen and paired difficulty require independent realism review.",
    "S1-09": "Monitor strip is a flat render with a gradient reflection; no multiparametric monitor chrome.",
    "S1-08": "Clean synthetic paper render; no print noise, no stray marks.", "S2-08": "Clean synthetic paper render; no print noise, no stray marks.",
    "S2-13": "Synthetic text sheet with placeholder values (0,0); header and layout are generic.",
}
IMPEDIMENT = {
    "skin_wound": "Needs authorized synthetic or open-licence skin/wound photographs with controlled skin tone and lighting; a procedural drawing "
                  "would not be a scientifically adequate stimulus for appearance, skin tone or lighting variables.",
    "xray": "Needs an authorized synthetic or open-licence, PHI-free radiograph (and its screen photo); procedural drawing is not adequate.",
    "pocus": "Needs an authorized phantom or open-licence ultrasound capture; procedural speckle is not adequate for FAST/lung windows.",
}
QA_TECH = [  # technical QA cases OUTSIDE the 30 pilot stimuli (they exercise subcases the 30 do not reach)
    {"stimulus_id": "QA-01", "file": "QA-01.wav", "route_modality": "skin_wound", "expected_layer7_trigger": T04, "expected_subreason": "global_unsupported_format",
     "spec_text": "Audio WAV de silencio enviado a la ruta fotográfica: formato global no admitido (Texto 4)."},
    {"stimulus_id": "QA-02", "file": "QA-02.jpg", "route_modality": "skin_wound", "expected_layer7_trigger": T03, "expected_subreason": "container_parse_error",
     "spec_text": "Archivo de 0 bytes con extensión .jpg: contenedor ilegible (Texto 3)."},
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _procedural_png():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (240, 320), (235, 238, 240))
    draw = ImageDraw.Draw(img)
    for i in range(0, 240, 20):
        draw.line([(i, 0), (240 - i, 320)], fill=(150 + i % 90, 160, 200 - i % 80), width=3)
    draw.rectangle([20, 20, 220, 300], outline=(90, 90, 90), width=2)
    draw.text((30, 150), "SYNTHETIC PLACEHOLDER\nNOT A MEDICAL IMAGE", fill=(60, 60, 60))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def _procedural_jpeg_truncated():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (320, 240), (225, 228, 232))
    draw = ImageDraw.Draw(img)
    for i in range(0, 320, 16):
        draw.rectangle([i, (i * 7) % 200, i + 8, 240], fill=(120 + i % 100, 140, 160))
    draw.text((20, 100), "SYNTHETIC PLACEHOLDER (CORRUPTED ON PURPOSE)", fill=(40, 40, 40))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    data = buffer.getvalue()
    return data[: int(len(data) * 0.45)]          # valid SOI + headers, truncated entropy-coded data: decoding fails


def _font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                                  # Pillow < 10.1: fixed bitmap font
        return ImageFont.load_default()


PX_PER_MM, PAPER_SPEED_MM_S = 8, 25                   # grid: 1 mm = 8 px; 25 mm/s -> 1 px = 5 ms
ECG_RR_PX = {"S1-08": 190, "S2-08": 100, "S1-09": 190, "S2-09": 190}


def ecg_parameters(stimulus_id):
    """Rate derived from the generator constants (not measured from pixels): RR[px] * 5 ms."""
    rr_ms = ECG_RR_PX[stimulus_id] * 1000.0 / (PX_PER_MM * PAPER_SPEED_MM_S)
    return {"heart_rate_bpm": round(60000.0 / rr_ms), "paper_speed_mm_s": PAPER_SPEED_MM_S, "grid_px_per_mm": PX_PER_MM,
            "rhythm": "regular synthetic sinus-like", "st_elevation": False}


def _ecg_wave(width, amplitude=1.0, rr=190):
    """Synthetic sinus rhythm (P, QRS, T; isoelectric ST). Pure arithmetic, deterministic, no clinical data."""
    ys = []
    for x in range(width):
        t = (x % rr) / rr
        v = 0.12 * math.exp(-((t - 0.18) / 0.035) ** 2) - 0.10 * math.exp(-((t - 0.36) / 0.012) ** 2) \
            + 1.0 * math.exp(-((t - 0.385) / 0.011) ** 2) - 0.22 * math.exp(-((t - 0.41) / 0.014) ** 2) \
            + 0.30 * math.exp(-((t - 0.66) / 0.06) ** 2)
        ys.append(v * amplitude)
    return ys


def _ecg_strip(size, paper=(252, 232, 232), grid=(236, 150, 150), trace=(20, 20, 20), label="SYNTHETIC ECG - NOT PATIENT DATA", rr=190):
    from PIL import Image, ImageDraw
    width, height = size
    img = Image.new("RGB", size, paper)
    draw = ImageDraw.Draw(img)
    for x in range(0, width, 8):
        draw.line([(x, 0), (x, height)], fill=grid, width=2 if x % 40 == 0 else 1)
    for y in range(0, height, 8):
        draw.line([(0, y), (width, y)], fill=grid, width=2 if y % 40 == 0 else 1)
    wave = _ecg_wave(width, amplitude=0.8, rr=rr)
    pts = [(x, height * 0.62 - value * height * 0.42) for x, value in enumerate(wave)]
    draw.line(pts, fill=trace, width=2)
    draw.text((6, height - 14), label, fill=(70, 70, 70))
    return img


def _encode(img, fmt, **kw):
    buffer = io.BytesIO()
    img.save(buffer, format=fmt, **kw)          # no exif/icc/text passed: nothing identifying is written
    return buffer.getvalue()


def _tilted(img, degrees, background=(40, 40, 44)):
    return img.rotate(degrees, resample=3, expand=True, fillcolor=background)


def _ecg_paper_photo(degrees, rr):
    return _encode(_tilted(_ecg_strip((640, 280), rr=rr), degrees), "JPEG", quality=88)


def _ecg_monitor_webp():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (640, 360), (14, 16, 18))
    strip = _ecg_strip((600, 150), paper=(8, 14, 10), grid=(22, 54, 30), trace=(90, 255, 120), label="SYNTHETIC MONITOR - NOT PATIENT DATA")
    img.paste(strip, (20, 100))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 629, 349], outline=(70, 74, 78), width=4)
    glare = Image.new("RGB", (640, 360), (255, 255, 255))
    mask = Image.linear_gradient("L").resize((640, 360)).point(lambda v: 28 if v < 90 else 0)
    img.paste(glare, (0, 0), mask)               # mild reflection
    return _encode(img, "WEBP", quality=85, lossless=False)


ECG_LEAD_LAYOUT = (("I", "aVR", "V1", "V4"), ("II", "aVL", "V2", "V5"), ("III", "aVF", "V3", "V6"))
# Approximate morphology in mV. Columns are P, Q, R, S and T amplitudes.
_ECG_LEAD_AMPLITUDES = {
    "I": (0.10, -0.07, 0.75, -0.14, 0.23),
    "II": (0.15, -0.09, 1.05, -0.21, 0.32),
    "V1": (0.04, 0.00, 0.19, -0.80, -0.06),
    "V2": (0.07, 0.00, 0.35, -0.89, 0.14),
    "V3": (0.10, 0.00, 0.59, -0.62, 0.24),
    "V4": (0.12, -0.04, 1.05, -0.34, 0.34),
    "V5": (0.12, -0.06, 1.17, -0.24, 0.37),
    "V6": (0.10, -0.06, 0.95, -0.14, 0.30),
}


def ecg_12_lead_sample(seconds):
    """Synchronized sample for a synthetic usability fixture, in mV."""
    t = seconds % (ECG_RR_PX["S2-09"] / (PX_PER_MM * PAPER_SPEED_MM_S))
    shapes = tuple(math.exp(-((t - center) / width) ** 2) for center, width in
                   ((0.15, 0.029), (0.295, 0.010), (0.320, 0.014), (0.350, 0.013), (0.555, 0.061)))
    values = {lead: sum(amplitude * shape for amplitude, shape in zip(amplitudes, shapes))
              for lead, amplitudes in _ECG_LEAD_AMPLITUDES.items()}
    lead_i, lead_ii = values["I"], values["II"]
    values.update(III=lead_ii - lead_i, aVR=-(lead_i + lead_ii) / 2,
                  aVL=lead_i - lead_ii / 2, aVF=lead_ii - lead_i / 2)
    return values


def _ecg_12_lead_jpeg():
    from PIL import Image, ImageDraw

    width, height = 1120, 572
    img = Image.new("RGB", (width, height), (24, 26, 30))
    draw = ImageDraw.Draw(img)
    draw.text((20, 9), "SYNTHETIC 12-LEAD ECG - NOT PATIENT DATA", font=_font(29), fill=(246, 246, 240))
    draw.text((20, 537), "25 mm/s   10 mm/mV   |   LAB SIMULATION", font=_font(24), fill=(246, 246, 240))
    step, top, cell_width, row_height = PX_PER_MM, 52, 264, 156
    sample_count = 224
    samples = [ecg_12_lead_sample(x / (step * PAPER_SPEED_MM_S)) for x in range(sample_count)]
    for row, leads in enumerate(ECG_LEAD_LAYOUT):
        for column, lead in enumerate(leads):
            left, y = 20 + column * (cell_width + 8), top + row * 160
            draw.rectangle((left, y, left + cell_width, y + row_height), fill=(248, 244, 240))
            for x in range(0, cell_width + 1, step):
                draw.line((left + x, y, left + x, y + row_height), fill=(220, 187, 185) if x % 40 == 0 else (236, 214, 212))
            for dy in range(0, row_height + 1, step):
                draw.line((left, y + dy, left + cell_width, y + dy), fill=(220, 187, 185) if dy % 40 == 0 else (236, 214, 212))
            draw.text((left + 6, y + 5), lead, font=_font(23), fill=(20, 22, 24))
            pixels = [values[lead] * step * 10 for values in samples]
            baseline = y + (row_height + max(pixels) + min(pixels)) / 2
            points = [(left + 20 + x, baseline - value) for x, value in enumerate(pixels)]
            draw.line(points, fill=(18, 24, 29), width=3)

    # Mild simulated screen reflection, confined to an upper corner.
    reflection = Image.new("L", img.size)
    ImageDraw.Draw(reflection).polygon([(940, 52), (1092, 52), (1092, 164)], fill=12)
    img.paste((255, 255, 255), (0, 0, width, height), reflection)
    return _encode(img, "JPEG", quality=90)


def _printed_sheet_photo():
    from PIL import Image, ImageDraw
    sheet = Image.new("RGB", (720, 960), (248, 247, 242))
    draw = ImageDraw.Draw(sheet)
    big, small = _font(30), _font(24)
    lines = ["INFORME SINTETICO DE ANALITICA - NO CLINICO", "", "Parametro        Resultado    Referencia",
             "Parametro A      0,0          0,0 - 0,0", "Parametro B      0,0          0,0 - 0,0", "Parametro C      0,0          0,0 - 0,0", "",
             "ES: Documento ficticio. Ningun dato real.", "PT: Documento ficticio. Nenhum dado real.", "EN: Fictitious document. No real data."]
    for i, text in enumerate(lines):
        draw.text((36, 48 + i * 44), text, fill=(30, 30, 30), font=big if i == 0 else small)
    draw.line([(0, 500), (720, 516)], fill=(215, 213, 205), width=4)     # mild fold
    return _encode(_tilted(sheet, -7, background=(176, 140, 98)), "JPEG", quality=88)   # light desk, opposite tilt


def _pdf(pages):
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(595, 842), invariant=1, pageCompression=0)
    pdf.setTitle("")
    pdf.setAuthor("")
    pdf.setSubject("")
    pdf.setCreator("")
    for lines in pages:
        y = 780
        for line in lines:
            pdf.drawString(50, y, line)
            y -= 18
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _wav_silence():
    import wave
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 800)
    return buffer.getvalue()


def generate_bytes():
    """Deterministic content of every generated file. PDFs are byte-reproducible (invariant mode); PNG/JPEG bytes depend on the Pillow build,
    so the SHA-256 that counts is the one of the COMMITTED file (verify_bank), not of a regeneration."""
    doc2 = [["INFORME SINTETICO DE PRUEBA - NO CLINICO (pagina 1/2)", "ES: Sin fiebre. No se observa derrame. Sin dolor referido.",
             "PT: Sem febre. Nao se observa derrame. Sem dor referida.", "EN: No fever. No effusion seen. No pain reported."],
            ["INFORME SINTETICO DE PRUEBA - NO CLINICO (pagina 2/2)", "ES: Documento ficticio; ningun dato real; no usar clinicamente.",
             "PT: Documento ficticio; nenhum dado real; nao usar clinicamente.", "EN: Fictitious document; no real data; not for clinical use."]]
    return {"S1-08.jpg": _ecg_paper_photo(4, ECG_RR_PX["S1-08"]), "S2-08.jpg": _ecg_paper_photo(-5, ECG_RR_PX["S2-08"]), "S1-09.webp": _ecg_monitor_webp(),
            "S2-09.jpg": _ecg_12_lead_jpeg(), "S2-13.jpg": _printed_sheet_photo(),
            "S1-13.pdf": _pdf(doc2), "S1-14.png": _procedural_png(),
            "S2-14.pdf": _pdf([["DOCUMENTO SINTETICO DE PRUEBA - NO CLINICO", "Envio valido sin seleccion de modalidad (escenario E1)."]]),
            "S1-15.jpg": _procedural_jpeg_truncated(),
            "S2-15.pdf": _pdf([["PDF TEXTUAL SINTETICO - NO CLINICO", "Enviado a una ruta exclusivamente fotografica (escenario E2)."]]),
            "QA-01.wav": _wav_silence(), "QA-02.jpg": b""}


def generate_files(directory=STIMULI_DIR):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in generate_bytes().items():
        (directory / name).write_bytes(data)
    return sorted(generate_bytes())


def dhash64(data):
    """64-bit difference hash of an IMAGE (None for non-images). The 9x8 reduction is a plain integer block average over the decoded
    grayscale pixels (no library resampling), so the hash is identical across Pillow versions."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data)).convert("L")
        width, height = img.size
        raw = img.tobytes()
    except Exception:
        return None
    cols, rows = 9, 8
    cells = []
    for r in range(rows):
        y0, y1 = r * height // rows, max((r + 1) * height // rows, r * height // rows + 1)
        for c in range(cols):
            x0, x1 = c * width // cols, max((c + 1) * width // cols, c * width // cols + 1)
            total = count = 0
            for y in range(y0, min(y1, height)):
                row = raw[y * width + x0: y * width + min(x1, width)]
                total += sum(row)
                count += len(row)
            cells.append(total // count if count else 0)
    bits = 0
    for r in range(rows):
        for c in range(cols - 1):
            bits = (bits << 1) | (cells[r * cols + c] > cells[r * cols + c + 1])
    return f"{bits:016x}"


def hamming(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def interset_check(manifest):
    """Pairs (set 1 x set 2) with BOTH perceptual hashes closer than the protocol minimum, plus byte-identical files."""
    s1 = [s for s in manifest["stimuli"] if s["set_id"] == 1 and s["phash_64"]]
    s2 = [s for s in manifest["stimuli"] if s["set_id"] == 2 and s["phash_64"]]
    close = [(a["stimulus_id"], b["stimulus_id"], hamming(a["phash_64"], b["phash_64"])) for a in s1 for b in s2 if hamming(a["phash_64"], b["phash_64"]) < HAMMING_MIN]
    shas = [s["sha256"] for s in manifest["stimuli"] if s["sha256"]]
    return {"perceptually_too_close": close, "duplicate_sha256": len(shas) != len(set(shas)), "image_hashes_compared": f"{len(s1)} x {len(s2)}"}


def audit_metadata(data):
    """Automated scan only (NOT a PHI review): reports identifying container metadata found in the bytes."""
    findings = []
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 4 <= len(data) and data[i] == 0xFF:
            marker = data[i + 1]
            if marker in (0xDA, 0xD9):
                break
            length = int.from_bytes(data[i + 2:i + 4], "big")
            if marker == 0xE1:
                findings.append("exif_or_xmp_app1")
            elif marker == 0xE2:
                findings.append("icc_profile_app2")
            elif marker == 0xFE:
                findings.append("jpeg_comment")
            i += 2 + length
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        for chunk in (b"tEXt", b"iTXt", b"zTXt", b"eXIf", b"iCCP", b"tIME"):
            if chunk in data:
                findings.append("png_" + chunk.decode())
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        for chunk in (b"EXIF", b"XMP ", b"ICCP"):
            if chunk in data:
                findings.append("webp_" + chunk.decode().strip())
    elif data[:5] == b"%PDF-":
        for key in (b"/Author", b"/Producer", b"/Creator", b"/Title"):
            index = data.find(key)
            if index == -1:
                continue
            value = data[index + len(key):].lstrip()
            # Preserve the existing fixture hashes and their exact, generic toolchain attribution.
            if key == b"/Producer" and value.startswith(rb"(ReportLab PDF Library - \(opensource\))"):
                continue
            if not value.startswith((b"()", b"( )")):
                findings.append("pdf_" + key.decode().lstrip("/").lower())
    return findings


def _contain_scale(data):
    """Scale applied when the image is shown with object-fit: contain in a 360x640 viewport (1.0 = no reduction); None for non-images."""
    if data is None or data[:5] == b"%PDF-":
        return None
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        return round(min(360 / img.width, 640 / img.height, 1.0), 3)
    except Exception:
        return None


def _file_facts(data):
    """Format and dimensions (images) + automated metadata findings; all None for a stimulus without file."""
    empty = {"image_format": None, "width": None, "height": None, "metadata_findings": None}
    if data is None:
        return empty
    if data[:5] == b"%PDF-":
        return {**empty, "image_format": "PDF", "metadata_findings": audit_metadata(data)}
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        return {"image_format": img.format, "width": img.width, "height": img.height, "metadata_findings": audit_metadata(data)}
    except Exception:
        return {**empty, "image_format": "UNPARSEABLE_ON_PURPOSE", "metadata_findings": audit_metadata(data)}


def build_manifest(directory=STIMULI_DIR):
    directory = Path(directory)
    stimuli = []
    for pair in range(1, 16):
        true_modality, route, difficulty, spec1, spec2 = _P[pair]
        code = PAIR_CODES[pair]
        for set_id, (spec, container, mst) in ((1, spec1), (2, spec2)):
            sid = f"S{set_id}-{pair:02d}"
            file_name = GENERATED_FILES.get(sid)
            data = (directory / file_name).read_bytes() if file_name else None
            generated = data is not None
            stimuli.append({
                "stimulus_id": sid, "set_id": set_id, "pair_id": pair, "mechanism_id": MECHANISM[code], "scenario_code": code,
                "true_modality": true_modality, "route_modality": route, "expected_layer7_trigger": EXPECTED.get((pair, set_id)),
                "language_stratum": "multilingual_es_pt_en" if sid == "S1-13" else "language_neutral", "mst_band": mst,
                "difficulty_level": difficulty, "container_spec": container, "spec_text": spec,
                "file": f"stimuli/{file_name}" if generated else None, "bytes": len(data) if generated else None,
                "sha256": sha256_bytes(data) if generated else None, "phash_64": dhash64(data) if generated else None,
                "origin_type": ("synthetic_procedural_schematic" if sid in PROCEDURAL_SCHEMATIC else "synthetic_procedural") if generated else None,
                **_file_facts(data),
                "mobile_360x640_contain_scale": _contain_scale(data),
                "ecg_generator_parameters": ecg_parameters(sid) if sid in ECG_RR_PX else None,
                "visual_review_status": "PENDING_VISUAL_REVIEW" if generated else "NOT_APPLICABLE_NOT_GENERATED",
                "clinical_adjudication_status": "PENDING_CLINICAL_ADJUDICATION",
                "lifecycle_status": "GENERATED_NOT_ADJUDICATED" if generated else PENDING,
                "review_controls": {
                    "realism_review_360x640": {"required": "clinical realism >= 4/5 from EACH of 2 independent reviewers, unambiguous true modality, agreed pair difficulty",
                                               "reviewer_1": "PENDING", "reviewer_2": "PENDING", "third_adjudicator_if_disagreement": "PENDING"},
                    "visual_derivative_inspection": "PENDING", "freeze_seal_eligible": False,
                    "validity_note": "NOT_ASSUMED_VALID_REQUIRES_REALISM_REVIEW" if sid in PROCEDURAL_SCHEMATIC else None,
                    "validity_justification": SCHEMATIC_JUSTIFICATION if sid in PROCEDURAL_SCHEMATIC else None,
                    "known_limitations": SCHEMATIC_LIMITS.get(sid)},
                "generation_impediment": None if generated else IMPEDIMENT.get(true_modality if sid != "S2-13" else "document"),
                "license_ref": "CC0-1.0 (content generated by project code; no third-party material)" if generated else None,
                "phi_audit_passed": None, "phi_audit_status": "AUTOMATED_SCAN_ONLY_HUMAN_REVIEW_PENDING" if generated else "NOT_APPLICABLE_NOT_GENERATED",
                "clinical_adjudicator_signoff": "PENDING", "generation_status": GENERATED if generated else PENDING})
    qa = []
    for item in QA_TECH:
        data = (directory / item["file"]).read_bytes()
        qa.append({**item, "bytes": len(data), "sha256": sha256_bytes(data) if data else sha256_bytes(b""), "origin_type": "synthetic_procedural",
                   "license_ref": "CC0-1.0 (content generated by project code; no third-party material)", "file": f"stimuli/{item['file']}"})
    return {"manifest_version": BANK_VERSION, "bank_status": "NOT_FROZEN_NOT_VALIDATED",
            "composition_source": "R23_GEMINI_INFORME_INTEGRADO_FINAL Part II table 6 (set 1 / set 2, pairs 01-15)",
            "stimuli": stimuli, "qa_technical": qa}


def verify_bank(manifest, directory=STIMULI_DIR):
    """Verify the bank's physical files and measure duplicate and metadata checks from their bytes."""
    problems = []
    directory = Path(directory)
    stimuli = manifest["stimuli"]
    ids = [s["stimulus_id"] for s in stimuli]
    if len(ids) != 30 or len(set(ids)) != 30:
        problems.append("the bank must list exactly 30 distinct stimuli")
    for set_id in (1, 2):
        if sorted(s["pair_id"] for s in stimuli if s["set_id"] == set_id) != list(range(1, 16)):
            problems.append(f"set {set_id} must contain pairs 01-15")
    measured = []
    for entry in stimuli + manifest["qa_technical"]:
        sid = entry["stimulus_id"]
        findings = set(entry.get("metadata_findings") or [])
        if entry.get("file"):
            path = directory.parent / entry["file"]
            if not path.is_file():
                problems.append(f"{sid}: file missing")
                continue
            data = path.read_bytes()
            sha = sha256_bytes(data)
            if sha != entry["sha256"] or len(data) != entry["bytes"]:
                problems.append(f"{sid}: bytes do not match the manifest")
            findings.update(audit_metadata(data))
            if "set_id" in entry:
                perceptual = dhash64(data)
                if perceptual != entry["phash_64"]:
                    problems.append(f"{sid}: perceptual hash does not match the manifest")
                measured.append({**entry, "sha256": sha, "phash_64": perceptual})
        elif entry.get("generation_status") == GENERATED:
            problems.append(f"{sid}: marked generated but has no file")
        if findings:
            problems.append(f"{sid}: identifying metadata found {sorted(findings)}")
    summary = interset_check({"stimuli": measured})
    if summary["perceptually_too_close"]:
        problems.append(f"set1 x set2 perceptually too close: {summary['perceptually_too_close']}")
    if summary["duplicate_sha256"]:
        problems.append("duplicate SHA-256 among generated stimuli")
    return problems


def composition_audit(manifest):
    """Protocol composition per set (R25 Gemini criterion 2): M3=9 (3 A + 6 F), M1=4 (2 B + C + D), M2=2 (E1 + E2); sets disjoint by id."""
    expected = {"M3": 9, "M1": 4, "M2": 2}
    codes = {"A": 3, "B": 2, "C": 1, "D": 1, "E1": 1, "E2": 1, "F": 6}
    problems = []
    for set_id in (1, 2):
        rows = [s for s in manifest["stimuli"] if s["set_id"] == set_id]
        got = {m: sum(r["mechanism_id"] == m for r in rows) for m in expected}
        if got != expected:
            problems.append(f"set {set_id}: mechanisms {got} != {expected}")
        got_codes = {c: sum(r["scenario_code"] == c for r in rows) for c in codes}
        if got_codes != codes:
            problems.append(f"set {set_id}: scenario codes {got_codes} != {codes}")
    ids = [s["stimulus_id"] for s in manifest["stimuli"]]
    if len(set(ids)) != len(ids):
        problems.append("stimulus ids are not disjoint across sets")
    return problems


def status_counts(manifest):
    pending = sum(s["generation_status"] == PENDING for s in manifest["stimuli"])
    return {"total": len(manifest["stimuli"]), "generated_technical": len(manifest["stimuli"]) - pending, "pending_stimulus_generation": pending,
            "lifecycle": {k: sum(s["lifecycle_status"] == k for s in manifest["stimuli"]) for k in ("GENERATED_NOT_ADJUDICATED", PENDING, "FROZEN")},
            "adjudicated": sum(s["clinical_adjudicator_signoff"] not in ("PENDING", None) for s in manifest["stimuli"]),
            "bank_status": manifest["bank_status"]}


if __name__ == "__main__":
    generate_files()
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(status_counts(manifest)), verify_bank(manifest))
