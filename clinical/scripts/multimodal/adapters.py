"""Technical input contracts only; no diagnostic model or temporal interpretation."""
import math

TASKS = {
    'ecg_still': ('ecg', 'image', ['Raster ECG only; signal, calibration and lead completeness need review.']),
    'pocus_still': ('pocus', 'image', ['A still cannot demonstrate sliding, compression or ventricular dynamics.']),
    'pocus_video_navigation': ('pocus', 'video', ['Navigation frames are not validated temporal inference.']),
    'radiograph_still': ('chest_xray', 'image', ['Views, laterality, devices and full field require human review.']),
    'msk_radiograph_still': ('musculoskeletal_xray', 'image', ['Required projections and occult injuries need review.']),
    'ct_mri_screenshot': ('ct_mri', 'image', ['A screenshot is not a complete DICOM study; no geometry/HU claim.']),
    'ct_mri_video_navigation': ('ct_mri', 'video', ['Rendered video is not a complete CT/MRI series or validated temporal inference.']),
}
CONTEXT = {'speed_mm_s': {25, 50}, 'gain_mm_mv': {5, 10, 20},
           'view': {'unknown', 'AP', 'PA', 'lateral', 'long_axis', 'short_axis'},
           'laterality': {'unknown', 'left', 'right', 'bilateral'}}


def context_valid(context):
    if not isinstance(context, dict):
        return False
    for key, value in context.items():
        if key not in CONTEXT or type(value) not in {str, int, float}:
            return False
        if isinstance(value, (int, float)) and not math.isfinite(value):
            return False
        if value not in CONTEXT[key]:
            return False
    return True


def build_input(case, reports):
    task = TASKS.get(case['task_id'])
    if not task or task[0] != case['modality'] or not context_valid(case.get('context', {})):
        raise ValueError('invalid_adapter_context')
    if not reports or any(r.get('errors') or r.get('kind') != task[1] for r in reports):
        raise ValueError('adapter_media_mismatch')
    return dict(case_id=case['id'], modality=task[0], task_id=case['task_id'],
        representation=task[1], context=case.get('context', {}),
        assets=[{k: r[k] for k in ('asset_id', 'sha256', 'format', 'width', 'height',
                                 'duration_seconds', 'fps', 'decoded_frames')} for r in reports],
        temporal_interpretation_validated=False, diagnostic_validation=False,
        limitations=[*task[2], 'Structural metadata inspection does not detect hidden payloads inside '
                     'PNG IDAT or JPEG scans; metadata absence is not a deidentification certificate.'],
        clinical_release_status='CLINICALLY_PENDING')
