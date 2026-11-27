"""OOXML metadata regression: XML well-formedness alone did not catch this defect."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from clinical_note_exporter import export_sections_docx  # noqa: E402

DC = "http://purl.org/dc/elements/1.1/"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
TERMS = "http://purl.org/dc/terms/"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


class DocxCoreProperties(unittest.TestCase):
    def test_core_properties_expose_standard_dublin_core_semantics(self):
        title = '诊断支持病历 & Clinical <QA> "synthetic"'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "metadata.docx"
            export_sections_docx([(title, [])], target)
            with zipfile.ZipFile(target) as archive:
                core = ET.fromstring(archive.read("docProps/core.xml"))
            # ECMA-376 core-properties uses Dublin Core for title and creator;
            # cp:title/cp:creator are well-formed XML but are not those properties.
            self.assertEqual(core.tag, "{" + CP + "}coreProperties")
            self.assertEqual(core.find("{" + DC + "}title").text, title)
            self.assertEqual(core.find("{" + DC + "}creator").text, "Emergency")
            self.assertIsNone(core.find("{" + CP + "}title"))
            self.assertIsNotNone(core.find("{" + TERMS + "}created"))

    def test_body_paragraphs_and_unicode_survive_metadata_export(self):
        sections = [("临床记录", []), ("Privacy / Segurança", ["SYNTHETIC NON-PRESCRIBING QA", "α & β <sample> 7.4 mg"])]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "body.docx"
            export_sections_docx(sections, target)
            with zipfile.ZipFile(target) as archive:
                self.assertIsNone(archive.testzip())
                document = ET.fromstring(archive.read("word/document.xml"))
            text = [node.text for node in document.iter("{" + W + "}t")]
            self.assertEqual(text, ["临床记录", "Privacy / Segurança", "SYNTHETIC NON-PRESCRIBING QA", "α & β <sample> 7.4 mg"])

    @unittest.skipUnless(sys.platform == "win32" and shutil.which("powershell.exe"), "WindowsBase native OPC parser requires Windows PowerShell")
    def test_windows_native_opc_reader_reads_title_and_creator(self):
        title = "诊断支持病历 & Synthetic QA"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "native.docx"
            export_sections_docx([(title, [])], target)
            script = Path(directory) / "read-properties.ps1"
            script.write_text('''param([string]$DocumentPath)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName WindowsBase
$package = [System.IO.Packaging.Package]::Open($DocumentPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read)
try {
    $properties = $package.PackageProperties
    @{title=$properties.Title;creator=$properties.Creator} | ConvertTo-Json -Compress
} finally { $package.Close() }
''', encoding="ascii")
            result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-File", str(script), "-DocumentPath", str(target)],
                                    capture_output=True, text=True, encoding="utf-8", check=True)
            properties = json.loads(result.stdout.lstrip("\ufeff"))
            self.assertEqual(properties["title"], title)
            self.assertEqual(properties["creator"], "Emergency")


if __name__ == "__main__":
    unittest.main()
