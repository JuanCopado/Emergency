"""Stimulus bank of the R23 protocol (30 stimuli = 2 sets x 15 pairs) · LABORATORY ONLY, no patient data, no clinical adjudication.

Composition follows R23_GEMINI_INFORME_INTEGRADO Part II table 6 (pairs 01-15; M3 = A,F; M1 = B,C,D; M2 = E1,E2). Only the stimuli that can
be produced as technically valid files WITHOUT inventing realistic medical imagery are generated (procedural placeholders, synthetic PDFs and
deliberately corrupt/incompatible containers for the Layer 7 triggers). Every other stimulus stays PENDING_STIMULUS_GENERATION with its
specification. Hashes are SHA-256 over the REAL BYTES of each file. The bank is NOT frozen and NOT validated.
"""
import hashlib
import io
import json
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
GENERATED_FILES = {"S1-13": "S1-13.pdf", "S1-14": "S1-14.png", "S2-14": "S2-14.pdf", "S1-15": "S1-15.jpg", "S2-15": "S2-15.pdf"}
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
    return {"S1-13.pdf": _pdf(doc2), "S1-14.png": _procedural_png(),
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
    """64-bit difference hash of an IMAGE (None for non-images)."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data)).convert("L").resize((9, 8))
    except Exception:
        return None
    pixels = list(img.tobytes())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
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
                "origin_type": "synthetic_procedural" if generated else None,
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
    """Recompute SHA-256 over the real bytes of every listed file. Returns a list of problems (empty = consistent)."""
    problems = []
    directory = Path(directory)
    ids = [s["stimulus_id"] for s in manifest["stimuli"]]
    if len(ids) != 30 or len(set(ids)) != 30:
        problems.append("the bank must list exactly 30 distinct stimuli")
    for set_id in (1, 2):
        if sorted(s["pair_id"] for s in manifest["stimuli"] if s["set_id"] == set_id) != list(range(1, 16)):
            problems.append(f"set {set_id} must contain pairs 01-15")
    for s in list(manifest["stimuli"]) + list(manifest["qa_technical"]):
        if s.get("file"):
            path = directory.parent / s["file"]
            if not path.exists():
                problems.append(f"{s['stimulus_id']}: file missing")
                continue
            data = path.read_bytes()
            if sha256_bytes(data) != s["sha256"] or len(data) != s["bytes"]:
                problems.append(f"{s['stimulus_id']}: bytes do not match the manifest")
        elif s.get("generation_status") == GENERATED:
            problems.append(f"{s['stimulus_id']}: marked generated but has no file")
    summary = interset_check(manifest)
    if summary["perceptually_too_close"]:
        problems.append(f"set1 x set2 perceptually too close: {summary['perceptually_too_close']}")
    if summary["duplicate_sha256"]:
        problems.append("duplicate SHA-256 among generated stimuli")
    return problems


def status_counts(manifest):
    pending = sum(s["generation_status"] == PENDING for s in manifest["stimuli"])
    return {"total": len(manifest["stimuli"]), "generated_technical": len(manifest["stimuli"]) - pending, "pending_stimulus_generation": pending,
            "adjudicated": sum(s["clinical_adjudicator_signoff"] not in ("PENDING", None) for s in manifest["stimuli"]),
            "bank_status": manifest["bank_status"]}


if __name__ == "__main__":
    generate_files()
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(status_counts(manifest)), verify_bank(manifest))
