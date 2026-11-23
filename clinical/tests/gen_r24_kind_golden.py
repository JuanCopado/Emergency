"""Regenerates tests/fixtures/r24_kind_oracle_golden.json from the EXACT base function.

The base is the pre-R8 `infer_attachment_kind` at commit 2116899bf43fd836173384af27d6e22a6480c51d
(`git archive` of that commit, run in a separate process; the current module's routing is never used).
Only needed to audit the golden file; the unit test never calls this script.
"""
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
BASE = "2116899bf43fd836173384af27d6e22a6480c51d"

NAMES = [
    None, "", "upload", "foto.png", "IMG_1234.jpg", "DSC0042.jpg", "informe.pdf", "INFORME.PDF", "serie.dcm", "SERIE.DCM",
    "ecg_01.png", "EKG.jpg", "electrocardiograma.pdf", "gasometria.png", "abg_result.png", "vbg.png",
    "microbiologia.pdf", "cultivo_orina.png", "hemocultivos.png", "laboratorio.pdf", "analitica.pdf", "bioquimica.png",
    "pocus_fast.jpg", "ecografia_abd.png", "ultrasound.png", "ct_craneo.dcm", "ct-torax.png", "tac_abdomen.png",
    "tc_cranio.png", "mri_rodilla.png", "rm_lumbar.png", "xray_torax.png", "x-ray.png", "radiografia.png", "pierna_rx.png",
    "rx_torax.png", "herida_pierna.png", "ferida.png", "lesion_01.png", "lesao.png", "lesão.png", "ulcera_pie.png",
    "úlcera.png", "dermatitis_contacto.png", "rash_abdomen.png", "celulitis.png", "absceso.png", "mordedura.png",
    "piel_tac.png", "lesion_rx_01.png", "ulcera_pie_rm_03.png", "ecg_herida.png", "herida.pdf", "herida.dcm",
    "dicom_file", "informe_dicom.png", "C:\\fotos\\herida.png", "/tmp/ecg.png", "a/b/c/foto.png", "  foto.png  ",
    "foto.", "x" * 256, "x" * 255, "a\x00b.png", "a\nb.png", ".pdf", ".dcm", "ECG", "Hemocult", "TC_craneo.png",
    "dermat.pdf", "wound.dcm", "skin", "abcdefg", "ctx.png", "tacos.png", "rm_.png",
]
MIMES = [None, "", "image/png", "image/jpeg", "application/pdf", "APPLICATION/PDF", "application/pdf; charset=binary",
         "application/dicom", "Application/DICOM", "x-dicom", "image/dicom+json", "text/plain"]
EXPLICIT = [None, "", " ", "skin_wound", "XRAY", " ecg ", "other_image", "pdf_document", "0"]


DRIVER = """
import json, sys
sys.path.insert(0, "clinical/scripts")
import clinical_note_api as api
import image_upload_guard as guard
out = []
for name, mime, explicit in json.load(sys.stdin):
    try:
        out.append(api.infer_attachment_kind(name, mime, explicit))
    except guard.MediaRejected as exc:
        out.append("REJECT:" + str(exc))
json.dump(out, sys.stdout)
"""


def run_base(triples):
    """Runs the EXACT base module (git archive of BASE) in a separate process; nothing is eval'ed here."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(["git", "archive", BASE, "clinical/scripts"], cwd=ROOT.parent, check=True,
                                 capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=archive, check=True)
        done = subprocess.run([sys.executable, "-I", "-c", DRIVER], cwd=tmp, check=True, capture_output=True,
                              input=json.dumps(triples).encode())
    return json.loads(done.stdout)


def main():
    triples = [list(t) for t in itertools.product(NAMES, MIMES, EXPLICIT)]
    results = run_base(triples)
    cases = [t + [r] for t, r in zip(triples, results)]
    body = json.dumps(cases, ensure_ascii=False, separators=(",", ":"))
    out = {"base_commit": BASE, "function": "clinical/scripts/clinical_note_api.py::infer_attachment_kind",
           "count": len(cases), "cases_sha256": hashlib.sha256(body.encode()).hexdigest(), "cases": cases}
    (ROOT / "tests/fixtures/r24_kind_oracle_golden.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(len(cases), out["cases_sha256"])


if __name__ == "__main__":
    main()
