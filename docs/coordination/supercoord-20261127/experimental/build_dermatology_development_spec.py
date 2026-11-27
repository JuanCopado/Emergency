"""Build metadata-only development specifications; never reassign canonical slots."""
import argparse
import hashlib
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=output.parents[2])
    project = parser.parse_args().project_root.resolve()
    cases_path = project / "ChatGPT_Trabajo/WORK_CIERRE_COORDINADO_20261126/DERMATOLOGIA/DERMATOLOGIA_CASOS_HEREDADO.json"
    overlay_path = project / "supercoord-dermatology-20261127/DERMATOLOGY_ADMISSIBILITY_OVERLAY.json"
    addendum_path = project / "supercoord-dermatology-20261127/primary-license-worktree/docs/coordination/derm-primary-license-20261127/PRIMARY_LICENSE_ADDENDUM.json"
    admission_path = project / "ChatGPT_Trabajo/WORK_CIERRE_FINAL_20261127/IMAGEN_R88/COORDINACION/ADMISION_OPERATIVA_30.json"
    cases, overlay, addendum, admission = map(load, (cases_path, overlay_path, addendum_path, admission_path))
    overlay_assets = {a["asset_id"]: a for a in overlay["assets"]}
    source_assets = {a["record_id"]: (c, a) for c in cases["cases"] for a in c["assets"]}
    candidates, excluded = [], []
    for a in overlay["assets"]:
        matching = next((p for p in addendum["proposals"] if p["asset_id"] == a["asset_id"]), None)
        f = matching["fields_to_add_or_refine_only_after_review"] if matching else {}
        eligible = (
            a["source"] == "SCIN"
            and a["owner_review"]["scope_category"] == "CONSULTATION_DEVELOPMENT_CONDITIONAL_ON_PRIVACY"
            and f.get("privacy.source_consent_provenance") == "SOURCE_DATASET_CONSENT_DOCUMENTED"
            and f.get("privacy.source_deidentification_provenance") == "SOURCE_DATASET_CURATION_DOCUMENTED"
            and f.get("privacy.known_asset_specific_direct_identifier_obstacle_from_available_records") is False
            and f.get("admissibility.local_consultation_development_proposal") == "ELIGIBLE_WITH_EXISTING_OWNER_SCOPE_AND_SOURCE_SAFEGUARDS"
        )
        if eligible:
            case, asset = source_assets[a["asset_id"]]
            candidates.append((asset["label"], case["case_id"], a["asset_id"]))
        else:
            excluded.append({"asset_id": a["asset_id"], "reason": "Not eligible under the narrow source-consent/deidentification and owner-scope metadata filter; no pixel reuse authorized"})
    # Distinct source labels only, using a reproducible tie-breaker for two eczema cases.
    selected = {}
    reserve = []
    for label, case_id, asset_id in sorted(candidates, key=lambda c: (c[0].casefold(), c[1])):
        key = label.casefold()
        if key not in selected:
            selected[key] = (label, case_id, asset_id)
        else:
            reserve.append({"case_id": case_id, "asset_id": asset_id, "reason": "Duplicate source label; development reserve only"})
    assert len(candidates) == 8 and len(selected) == 7 and len(reserve) == 1
    historical = {r["stimulus_id"]: r for r in admission["rows"]}
    rows = []
    for n, (label, case_id, asset_id) in enumerate(selected.values(), 1):
        case, asset = source_assets[asset_id]
        oa = overlay_assets[asset_id]
        for side, viewport in ((1, {"width": 1440, "height": 900}), (2, {"width": 390, "height": 844})):
            old_id = f"S{side}-{n:02d}"
            assert historical[old_id]["status"] == "REQUISITO_HISTORICO_PENDIENTE_ADAPTACION"
            rows.append({
                "development_spec_id": f"DEV-DERM-{n:02d}-{side}",
                "historical_requirement_pointer_only": old_id,
                "canonical_slot_reassigned": False,
                "canonical_mechanism_inherited": False,
                "case_id": case_id, "metadata_candidate_asset_id": asset_id,
                "metadata_candidate_sha256": asset["sha256"],
                "source_label_not_independent_diagnosis": label,
                "owner_decision_id": case["decision_id"],
                "owner_decision_response": oa["owner_review"]["response"],
                "purpose": "LOCAL_DEVELOPMENT_ENGINEERING_DISPLAY_SPEC_ONLY",
                "comparison_pair": f"DEV-DERM-{n:02d}",
                "same_source_case_in_both_variants": True,
                "independent_validation_eligible": False,
                "display_specification": {"viewport_css_pixels": viewport,
                    "image_fit": "contain", "crop": False, "anatomy_edit": False,
                    "source_attribution_and_license_visible": True,
                    "show_source_differential_limitations": True,
                    "rendered_screen_is_not_physical_mobile_capture": True},
                "diagnostic_evidence_as_recorded": asset["diagnostic_evidence"],
                "limitations_as_recorded": asset["limitations"],
                "license_as_recorded": asset["license"],
                "attribution_as_recorded": asset["attribution"],
                "local_copyright_consent_basis": "PRIMARY_LICENSE_ADDENDUM SCIN-LICENSE/README/PUBLISHER-PRIVACY; source-level consent and curation, no unconditional consent certificate",
                "pixel_use_current_state": "NOT_PERFORMED_METADATA_SPEC_ONLY",
                "image_derivative_generated": False,
                "asset_selected_for_physical_experimental_admission": False,
                "specific_future_consumer_privacy_assessment": "REQUIRED_BEFORE_NEW_PIXEL_USE_OR_TRANSFER",
                "status": "PREPARED_DEVELOPMENT_SPEC_NOT_RENDERED_NOT_ADMITTED",
            })
    assert len(rows) == 14 and len({r["development_spec_id"] for r in rows}) == 14
    assert len({r["historical_requirement_pointer_only"] for r in rows}) == 14
    result = {
        "task_id": "E-DERM-DEVELOPMENT-SPEC-14-20261127",
        "author": "Codex technical preparation; not Antigravity or independent clinical review",
        "status": "PREPARED_METADATA_SPECIFICATIONS_ONLY",
        "scope": "Explicit development-only adaptation map; separate namespace, historical bank unchanged",
        "source_hashes": [{"path_relative_to_project": str(p.relative_to(project)).replace("\\", "/"), "sha256": hash_file(p)} for p in (cases_path, overlay_path, addendum_path, admission_path)],
        "selection_rule": "SCIN only; recorded consultation/development owner scope; source dataset consent and curation documented by primary addendum; no known direct-identifier obstacle in available records; seven distinct labels sorted case-insensitive, duplicate label tie-break by case_id ascending",
        "counts": {"source_assets": 24, "source_cases": 23, "metadata_eligible_candidates": len(candidates),
            "distinct_selected_cases": len(selected), "development_display_specs": len(rows),
            "reserve_duplicate_label_cases": len(reserve), "excluded_from_selection": len(excluded),
            "images_generated": 0, "image_bytes_read_or_copied": 0, "canonical_slot_changes": 0,
            "new_canonical_images": 0, "independent_adjudications": 0},
        "development_pairs_share_sources_and_are_not_independent": True,
        "unknown_or_unresolved_pixel_reuse_privacy_is_not_cleared_by_this_specification": True,
        "rows": rows, "reserve": reserve, "excluded_assets": excluded,
        "remaining_physical_blocks": [
            {"id": "S2-11", "block": "Real physical recapture required to address moire; no digital simulation"},
            {"id": "S2-12", "block": "Exact experimental condition, clean panel and applicable permission unresolved"}],
        "bank_counts_unchanged": {"canonical": 10, "pending": 20, "adjudications": 0},
        "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE",
        "no_external_transmissions": True,
    }
    target = output / "DERMATOLOGY_DEVELOPMENT_ADAPTATION_14.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"], "sha256": hash_file(target)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
