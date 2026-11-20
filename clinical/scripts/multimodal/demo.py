"""Reproducible artificial media and catalog; no clinical dataset or model."""
import hashlib
import json
from pathlib import Path
import subprocess

from .bank import admitted_inputs, validate_bank
from .intake import extract_navigation_frames, resolve_media_tool
from .evaluation import evaluate


def create_demo(destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('demo_destination_must_be_new')
    try:
        ffmpeg = resolve_media_tool('ffmpeg')
        resolve_media_tool('ffprobe')
    except ValueError:
        raise ValueError('demo_requires_ffmpeg_and_ffprobe') from None
    try:
        return _create_demo(destination, ffmpeg)
    except (OSError, subprocess.SubprocessError):
        # Do not expose decoder commands, private paths or captured diagnostics.
        raise ValueError('demo_media_generation_failed') from None


def _create_demo(destination, ffmpeg):
    from PIL import Image
    destination.mkdir(parents=True)
    media = destination / 'media'
    media.mkdir()
    cases = []
    specs = [('ecg', 'ecg_still', 'development', '.png'),
             ('pocus', 'pocus_still', 'teaching', '.png'),
             ('chest_xray', 'radiograph_still', 'development', '.jpg'),
             ('ct_mri', 'ct_mri_screenshot', 'teaching', '.png')]
    for index, (modality, task, split, suffix) in enumerate(specs, 1):
        path = media / f'asset-{index:03d}{suffix}'
        # Colored geometric arrays, not anatomy or simulated diagnostic findings.
        image = Image.new('RGB', (64, 48), (index * 40, 30, 100))
        image.save(path)
        cases.append(_case(index, modality, task, split, path, destination))
    video = media / 'asset-005.mp4'
    subprocess.run([ffmpeg, '-v', 'error', '-nostdin', '-f', 'lavfi',
        '-i', 'testsrc=size=64x48:rate=5', '-t', '1', '-c:v', 'mpeg4', '-an', str(video)],
        check=True, capture_output=True, timeout=30,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    cases.append(_case(5, 'pocus', 'pocus_video_navigation', 'development', video, destination))
    bank = dict(schema_version='1.0', purpose='Synthetic software demonstration only', cases=cases)
    (destination / 'bank.private.json').write_text(json.dumps(bank, indent=2), encoding='utf-8')
    reports = {split: admitted_inputs(bank, destination, split) for split in ('teaching', 'development', 'blind_test')}
    frames = extract_navigation_frames(destination, cases[-1]['assets'][0], destination / 'navigation', count=3)
    result = dict(bank_gate=validate_bank(bank), admitted_counts={k: len(v) for k, v in reports.items()},
        inputs=reports, navigation=frames, diagnostic_cases_evaluated=0,
        evaluation=evaluate(bank, {'dataset_class': 'workflow_only', 'cases': []}, destination),
        training_performed=False, external_inference_performed=False,
        clinical_release_status='CLINICALLY_PENDING')
    (destination / 'technical-report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def _case(index, modality, task, split, path, root):
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    return dict(id=f'case-{index:03d}', patient_group_id=f'synthetic-patient-{index:03d}',
        study_group_id=f'synthetic-study-{index:03d}', source_group_id=f'synthetic-source-{index:03d}',
        modality=modality, task_id=task, split=split, data_kind='synthetic',
        source_known=True, annotated=False, context={},
        assets=[dict(id=f'asset-{index:03d}', path=path.relative_to(root).as_posix(),
                     sha256=digest, size_bytes=len(payload), derivative=False)],
        rights=dict(authorized=True, authorization_ref='synthetic-generation',
                    allowed_uses=['teaching', 'development']),
        privacy=dict(metadata_reviewed=True, pixels_reviewed=True, full_video_reviewed=True,
                     reviewer_id='synthetic-generator', reviewed_sha256=[digest]))
