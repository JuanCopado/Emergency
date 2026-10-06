#!/usr/bin/env python3
"""Deterministic DOCX/PDF exporter for privacy-screened clinical notes."""

import html
import io
import json
import textwrap
import zipfile
from pathlib import Path
from datetime import datetime, timezone

from clinical_note_support import validate_for_export

LABELS = {
 "pt-PT":{
  "title":"Nota Clínica de Apoio ao Diagnóstico","encounter":"Contexto clínico",
  "history":"História clínica","pmh":"Antecedentes pessoais","meds":"Medicação habitual",
  "allergies":"Alergias","hpi":"História da doença atual","timeline":"Evolução / linha temporal",
  "exam":"Exame objetivo","tests":"Meios complementares de diagnóstico",
  "problems":"Problemas ativos","synthesis":"Síntese clínica","likely":"Diagnósticos prováveis",
  "differential":"Diagnóstico diferencial","must":"Diagnósticos a não perder",
  "more_tests":"Exames complementares sugeridos","treatment":"Tratamento sugerido",
  "disposition":"Destino / reavaliação","clarify":"Dados a esclarecer / contradições",
  "limitations":"Limitações","privacy":"Privacidade e validação"
 },
 "es-ES":{
  "title":"Nota clínica de apoyo al diagnóstico","encounter":"Contexto clínico",
  "history":"Historia clínica","pmh":"Antecedentes personales","meds":"Medicación habitual",
  "allergies":"Alergias","hpi":"Historia de la enfermedad actual","timeline":"Evolución / línea temporal",
  "exam":"Exploración","tests":"Pruebas complementarias","problems":"Problemas activos",
  "synthesis":"Síntesis clínica","likely":"Diagnósticos probables","differential":"Diagnóstico diferencial",
  "must":"Diagnósticos que no se deben omitir","more_tests":"Pruebas complementarias sugeridas",
  "treatment":"Tratamiento sugerido","disposition":"Destino / reevaluación",
  "clarify":"Datos a aclarar / contradicciones","limitations":"Limitaciones","privacy":"Privacidad y validación"
 }
}

def _labels(note):
    return LABELS.get(note.get("language"), LABELS["pt-PT"])

def _txt(value):
    if value is None: return ""
    if isinstance(value, (list, tuple)): return "; ".join(_txt(x) for x in value)
    if isinstance(value, dict): return ", ".join(f"{k}: {_txt(v)}" for k,v in value.items() if v not in (None,"",[],{}))
    return str(value)

def _candidate_lines(items):
    out=[]
    for i,x in enumerate(items or [],1):
        evf="; ".join(x.get("evidence_for",[]))
        eva="; ".join(x.get("evidence_against",[]))
        miss="; ".join(x.get("missing_discriminating_data",[]))
        line=f"{i}. {x.get('diagnosis','')} [{x.get('confidence','')}]"
        if evf: line += f" | a favor: {evf}"
        if eva: line += f" | contra: {eva}"
        if miss: line += f" | falta discriminar: {miss}"
        out.append(line)
    return out

def _suggestion_lines(items):
    out=[]
    for i,x in enumerate(items or [],1):
        line=f"{i}. {x.get('action','')} [{x.get('priority','')}]"
        if x.get("rationale"): line += f" - {x['rationale']}"
        out.append(line)
    return out

def _report_lines(reports, language):
    es = language == "es-ES"
    labels = {
        "provenance": "Procedencia" if es else "Proveniência",
        "official": "Informe oficial / dados extraídos" if not es else "Informe oficial / datos extraídos",
        "ai": "Interpretação IA" if not es else "Interpretación IA",
        "findings": "Achados" if not es else "Hallazgos",
        "impression": "Impressão" if not es else "Impresión",
        "limitations": "Limitações" if not es else "Limitaciones",
        "modules": "Módulos fonte" if not es else "Módulos fuente",
    }
    out = []
    for index, report in enumerate(reports or [], 1):
        kind = report.get("kind") or "MCDT"
        when = report.get("time_label")
        heading = f"{index}. {kind}" + (f" · {when}" if when else "")
        out.append(heading)
        provenance = report.get("provenance")
        source_ref = report.get("source_reference")
        if provenance:
            suffix = f" · {source_ref}" if source_ref else ""
            out.append(f"   {labels['provenance']}: {provenance}{suffix}")
        if report.get("official_report"):
            out.append(f"   {labels['official']}: {report['official_report']}")
        if report.get("findings"):
            out.append(f"   {labels['findings']}: {report['findings']}")
        if report.get("impression"):
            out.append(f"   {labels['impression']}: {report['impression']}")
        if report.get("ai_interpretation"):
            out.append(f"   {labels['ai']}: {report['ai_interpretation']}")
        if report.get("limitations"):
            out.append(f"   {labels['limitations']}: {'; '.join(report['limitations'])}")
        if report.get("routed_modules"):
            out.append(f"   {labels['modules']}: {'; '.join(report['routed_modules'])}")
    return out


def note_to_sections(note):
    L = _labels(note)
    language = note.get("language")
    es = language == "es-ES"
    e = note["encounter"]
    h = note["history"]
    ex = note["exam"]
    a = note["assessment"]

    X = {
        "chief": "Motivo de consulta" if es else "Motivo de admissão / queixa principal",
        "baseline": "Situación basal" if es else "Estado basal",
        "surgery": "Antecedentes quirúrgicos" if es else "Antecedentes cirúrgicos",
        "reconciliation": "Conciliación / discrepancias de medicación" if es else "Conciliação / discrepâncias de medicação",
        "social": "Contexto social / fonte" if es else "Contexto social / fonte",
        "vitals": "Constantes seriadas" if es else "Sinais vitais seriados",
        "laboratory": "Analítica" if es else "Analítica",
        "blood_gas": "Gasometría" if es else "Gasometria",
        "ecg": "ECG",
        "xray": "Radiografía (Rx)" if es else "Radiografia (Rx)",
        "ct_mri": "TC / RM",
        "pocus": "Ecografía / POCUS" if es else "Ecografia / POCUS",
        "microbiology": "Microbiología" if es else "Microbiologia",
        "other_mcdt": "Otros MCDT" if es else "Outros MCDT",
        "image_other": "Otra imagen" if es else "Outra imagem",
        "validation": "Validación médica y privacidad" if es else "Validação médica e privacidade",
    }

    age = e.get("age", {})
    if age.get("years") is not None:
        age_text = f"{age['years']} años" if es else f"{age['years']} anos"
    elif age.get("months") is not None:
        age_text = f"{age['months']} meses"
    else:
        age_text = "no documentada" if es else "não documentada"

    context = [
        f"ID seudónimo del episodio: {e.get('encounter_id','')}" if es else f"ID pseudónimo do episódio: {e.get('encounter_id','')}",
        f"Edad: {age_text}" if es else f"Idade: {age_text}",
        f"Sexo: {e.get('sex','')}",
    ]
    context_fields = (
        ("origin", "Origen" if es else "Origem"),
        ("transfer_status", "Transferencia" if es else "Transferência"),
        ("functional_status", "Estado funcional" if es else "Estado funcional"),
        ("cognitive_status", "Estado cognitivo" if es else "Estado cognitivo"),
        ("living_context", "Contexto domiciliario" if es else "Contexto domiciliário"),
    )
    for key, label in context_fields:
        if e.get(key):
            context.append(f"{label}: {e[key]}")

    sections = [(L["title"], []), (L["encounter"], context)]

    if h.get("chief_complaint"):
        sections.append((X["chief"], [h["chief_complaint"]]))
    if h.get("baseline_status"):
        sections.append((X["baseline"], [h["baseline_status"]]))
    if h.get("past_medical_history"):
        sections.append((L["pmh"], [f"- {x}" for x in h["past_medical_history"]]))
    if h.get("past_surgical_history"):
        sections.append((X["surgery"], [f"- {x}" for x in h["past_surgical_history"]]))
    if h.get("chronic_medications"):
        sections.append((L["meds"], [
            f"- {m.get('name','')} {m.get('dose') or ''} {m.get('schedule') or ''}".strip()
            for m in h["chronic_medications"]
        ]))
    if h.get("medication_discrepancies"):
        sections.append((X["reconciliation"], [f"- {x}" for x in h["medication_discrepancies"]]))

    allergy_lines = [f"- {_txt(x)}" for x in h.get("allergies", [])]
    if not allergy_lines:
        allergy_lines = [
            "Alergias no documentadas; confirmar revisión." if es
            else "Alergias não documentadas; confirmar revisão."
        ]
    sections.append((L["allergies"], allergy_lines))

    if h.get("present_illness"):
        sections.append((L["hpi"], [h["present_illness"]]))
    social_lines = [x for x in [h.get("social_history"), h.get("source_reliability")] if x]
    if social_lines:
        sections.append((X["social"], social_lines))

    if note.get("timeline"):
        sections.append((L["timeline"], [
            f"- {x.get('time_label','')}: {x.get('event','')}"
            + (f" [{x.get('source')}]" if x.get("source") else "")
            for x in note["timeline"]
        ]))

    vital_lines = ["- " + _txt(v) for v in ex.get("vitals", [])]
    if vital_lines:
        sections.append((X["vitals"], vital_lines))

    exam_lines = []
    exam_labels = {
        "general": "General",
        "neurologic": "Neurológico",
        "respiratory": "Respiratorio" if es else "Respiratório",
        "cardiovascular": "Cardiovascular",
        "abdominal": "Abdomen" if es else "Abdómen",
        "skin_wounds": "Piel/heridas" if es else "Pele/feridas",
        "extremities": "Extremidades",
        "other": "Otros" if es else "Outros",
    }
    for key, label in exam_labels.items():
        if ex.get(key):
            exam_lines.append(f"{label}: {ex[key]}")
    if exam_lines:
        sections.append((L["exam"], exam_lines))

    tests = note["complementary_tests"]
    if tests.get("laboratory"):
        sections.append((X["laboratory"], _report_lines(tests["laboratory"], language)))
    if tests.get("blood_gas"):
        sections.append((X["blood_gas"], _report_lines(tests["blood_gas"], language)))
    if tests.get("ecg"):
        sections.append((X["ecg"], _report_lines(tests["ecg"], language)))

    imaging_groups = {"xray": [], "ct_mri": [], "pocus": [], "image_other": []}
    for report in tests.get("imaging", []):
        kind = str(report.get("kind") or "").lower()
        if kind in {"xray", "xray_chest", "chest_xray", "musculoskeletal_xray"}:
            imaging_groups["xray"].append(report)
        elif kind in {"ct", "ct_head", "ct_body", "mri"}:
            imaging_groups["ct_mri"].append(report)
        elif kind in {"pocus", "ultrasound"}:
            imaging_groups["pocus"].append(report)
        else:
            imaging_groups["image_other"].append(report)
    for key in ("xray", "ct_mri", "pocus", "image_other"):
        if imaging_groups[key]:
            sections.append((X[key], _report_lines(imaging_groups[key], language)))

    if tests.get("microbiology"):
        sections.append((X["microbiology"], _report_lines(tests["microbiology"], language)))
    if tests.get("other"):
        sections.append((X["other_mcdt"], _report_lines(tests["other"], language)))

    if a.get("active_problems"):
        sections.append((L["problems"], [f"- {x}" for x in a["active_problems"]]))
    if a.get("problem_representation"):
        sections.append((L["synthesis"], [a["problem_representation"]]))
    if a.get("likely_diagnoses"):
        sections.append((L["likely"], _candidate_lines(a["likely_diagnoses"])))
    if a.get("differential_diagnoses"):
        sections.append((L["differential"], _candidate_lines(a["differential_diagnoses"])))
    if a.get("must_not_miss"):
        sections.append((L["must"], _candidate_lines(a["must_not_miss"])))
    if a.get("suggested_tests"):
        sections.append((L["more_tests"], _suggestion_lines(a["suggested_tests"])))
    if a.get("treatment_suggestions"):
        sections.append((L["treatment"], _suggestion_lines(a["treatment_suggestions"])))

    disposition = _suggestion_lines(a.get("disposition")) + _suggestion_lines(a.get("reassessment"))
    if disposition:
        sections.append((L["disposition"], disposition))
    if a.get("contradictions_to_clarify"):
        sections.append((L["clarify"], [f"- {x}" for x in a["contradictions_to_clarify"]]))
    if a.get("limitations"):
        sections.append((L["limitations"], [f"- {x}" for x in a["limitations"]]))

    p = note["privacy"]
    cv = note.get("clinician_validation", {})
    validation_lines = [
        ("Modo de privacidad: " if es else "Modo de privacidade: ") + str(p.get("mode")),
        ("Revisión clínica: " if es else "Revisão clínica: ") + ("sí" if es and cv.get("reviewed") else "sim" if cv.get("reviewed") else "no" if es else "não"),
        ("Rol del revisor: " if es else "Função do revisor: ") + str(cv.get("reviewer_role") or ("no registrado" if es else "não registado")),
        ("Validado en: " if es else "Validado em: ") + str(cv.get("reviewed_at") or ("no registrado" if es else "não registado")),
        (
            "Los archivos clínicos originales no se incorporan al documento exportado por defecto."
            if es else
            "Os ficheiros clínicos originais não são incorporados no documento exportado por defeito."
        ),
    ]
    sections.append((X["validation"], validation_lines))

    return [(heading, [p for p in paragraphs if p]) for heading, paragraphs in sections if heading and (paragraphs or heading == L["title"])]


def _xml_escape(s): return html.escape(str(s), quote=False)

def export_docx(note, out_path):
    gate=validate_for_export(note)
    if gate["blocked"]: raise ValueError("export blocked: "+" | ".join(x["message"] for x in gate["findings"] if x["severity"]=="STOP"))
    sections=note_to_sections(note)
    paras=[]
    for idx,(heading,lines) in enumerate(sections):
        if idx==0:
            paras.append(("Title",heading))
        else:
            paras.append(("Heading1",heading))
            for line in lines: paras.append(("Normal",line))
    def pxml(style,text):
        return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t xml:space="preserve">{_xml_escape(text)}</w:t></w:r></w:p>'
    body="".join(pxml(st,tx) for st,tx in paras)
    document=f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>'''
    styles='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:sz w:val="20"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style></w:styles>'''
    content_types='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'''
    rels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'''
    wrels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    now=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core=f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><cp:title>Clinical Note</cp:title><cp:creator>Emergency Clinical Note Module</cp:creator><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created></cp:coreProperties>'''
    app='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Emergency Clinical Note Module</Application></Properties>'''
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",content_types); z.writestr("_rels/.rels",rels)
        z.writestr("word/document.xml",document); z.writestr("word/styles.xml",styles); z.writestr("word/_rels/document.xml.rels",wrels)
        z.writestr("docProps/core.xml",core); z.writestr("docProps/app.xml",app)
    return str(out)

def _pdf_escape(s):
    raw=str(s).encode("cp1252","replace").decode("latin1")
    return raw.replace("\\","\\\\").replace("(","\\(").replace(")","\\)")

def export_pdf(note, out_path):
    gate=validate_for_export(note)
    if gate["blocked"]: raise ValueError("export blocked: "+" | ".join(x["message"] for x in gate["findings"] if x["severity"]=="STOP"))
    sections=note_to_sections(note)
    lines=[]
    for idx,(heading,paragraphs) in enumerate(sections):
        lines.append(("title" if idx==0 else "heading",heading))
        for p in paragraphs:
            for line in textwrap.wrap(str(p), width=95, replace_whitespace=False) or [""]:
                lines.append(("normal",line))
    pages=[]; current=[]; y=790
    for kind,text in lines:
        step=22 if kind=="title" else 18 if kind=="heading" else 14
        if y-step<45:
            pages.append(current); current=[]; y=790
        current.append((kind,text,y)); y-=step
    if current: pages.append(current)
    objects=[]
    def add(obj):
        objects.append(obj); return len(objects)
    font=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    bold=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    page_ids=[]; content_ids=[]
    for page in pages:
        commands=["BT"]
        for kind,text,ypos in page:
            if kind=="title": commands += ["/F2 16 Tf", f"50 {ypos} Td", f"({_pdf_escape(text)}) Tj", f"-50 -{ypos} Td"]
            elif kind=="heading": commands += ["/F2 12 Tf", f"50 {ypos} Td", f"({_pdf_escape(text)}) Tj", f"-50 -{ypos} Td"]
            else: commands += ["/F1 10 Tf", f"55 {ypos} Td", f"({_pdf_escape(text)}) Tj", f"-55 -{ypos} Td"]
        commands.append("ET")
        stream="\n".join(commands).encode("latin1","replace")
        cid=add(f"<< /Length {len(stream)} >>\nstream\n".encode()+stream+b"\nendstream")
        content_ids.append(cid); page_ids.append(None)
    pages_id=len(objects)+1
    for i,cid in enumerate(content_ids):
        pid=add(f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font} 0 R /F2 {bold} 0 R >> >> /Contents {cid} 0 R >>".encode())
        page_ids[i]=pid
    kids=" ".join(f"{pid} 0 R" for pid in page_ids)
    objects.insert(pages_id-1,f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode())
    # inserting shifts page ids at/after pages_id by +1
    page_ids=[pid+1 if pid>=pages_id else pid for pid in page_ids]
    kids=" ".join(f"{pid} 0 R" for pid in page_ids)
    objects[pages_id-1]=f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    catalog=add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    buf=io.BytesIO(); buf.write(b"%PDF-1.4\n")
    offsets=[0]
    for i,obj in enumerate(objects,1):
        offsets.append(buf.tell()); buf.write(f"{i} 0 obj\n".encode()); buf.write(obj); buf.write(b"\nendobj\n")
    xref=buf.tell(); buf.write(f"xref\n0 {len(objects)+1}\n".encode()); buf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]: buf.write(f"{off:010d} 00000 n \n".encode())
    buf.write(f"trailer\n<< /Size {len(objects)+1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    out.write_bytes(buf.getvalue()); return str(out)

def export_json(note,out_path):
    gate=validate_for_export(note)
    if gate["blocked"]: raise ValueError("export blocked")
    Path(out_path).write_text(json.dumps(note,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return str(out_path)
